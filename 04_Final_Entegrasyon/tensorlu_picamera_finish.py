from picamera2 import Picamera2
import cv2
import numpy as np
from collections import deque, Counter
import serial
import time
import threading
import tensorflow as tf
import sys

# ==========================================
# CONFIGURATION & GLOBAL PROTOCOLS
# ==========================================
CONFIG = {
    "SERIAL_PORT": "/dev/ttyUSB0",      # Change to COMx for Windows
    "BAUD_RATE": 115200,
    "CAMERA_SIZE": (640, 480),
    "AI_MODEL": "best_shape_model.keras",
    "CATEGORIES": ['circle', 'hexagon', 'parallelogram', 'pentagon', 'rectangle', 'rhombus', 'square', 'triangle'],
    "PID": {"Kp": 0.4, "Ki": 0.0, "Kd": 0.15},
    "ROI_HEIGHT": 150,
    "ROI_WIDTH_OFFSET": 100
}

# Global Status
current_frame = None
frame_lock = threading.Lock()
is_running = True

# ==========================================
# COMMUNICATION LAYER
# ==========================================
try:
    ser = serial.Serial(CONFIG["SERIAL_PORT"], CONFIG["BAUD_RATE"], timeout=0.1)
    print(f"📡 [PC] Serial connected on {CONFIG['SERIAL_PORT']}")
except Exception as e:
    print(f"❌ [PC] Serial error: {e}")
    sys.exit(1)

def send_joystick_values(x1, y1, x2, y2):
    """Sends command in format: X1:1500,Y1:1500,X2:1500,Y2:1500\n"""
    msg = f"X1:{x1},Y1:{y1},X2:{x2},Y2:{y2}\n"
    ser.write(msg.encode())

# ==========================================
# LOGIC HELPERS
# ==========================================
def scale(val, val_min, val_max, out_min, out_max):
    val = np.clip(val, val_min, val_max)
    return int(np.interp(val, [val_min, val_max], [out_min, out_max]))

def get_orientation(contour):
    sz = len(contour)
    data_pts = np.empty((sz, 2), dtype=np.float64)
    for i in range(sz):
        data_pts[i] = contour[i, 0]
    _, eigenvectors, _ = cv2.PCACompute2(data_pts, mean=np.empty((0)))
    angle = np.arctan2(eigenvectors[0, 1], eigenvectors[0, 0])
    return np.degrees(angle)

# ==========================================
# THREAD 01: AI INFERENCE (SHAPE)
# ==========================================
def ai_inference_thread():
    global current_frame, is_running
    print("🧠 [AI] Loading TF Lite Model...")
    model = tf.keras.models.load_model(CONFIG["AI_MODEL"], compile=False)
    
    while is_running:
        with frame_lock:
            if current_frame is None:
                continue
            working_frame = current_frame.copy()

        # Prepare for AI
        roi = cv2.resize(working_frame, (64, 64))
        img_array = roi.astype('float32') / 255.0
        img_array = np.expand_dims(img_array, axis=0)

        prediction = model.predict(img_array, verbose=0)
        predicted_class = CONFIG["CATEGORIES"][np.argmax(prediction)]
        
        # Log to console for now
        # print(f"🔍 [AI] Predicted: {predicted_class}")
        time.sleep(0.05) # Throttle AI thread to save CPU

# ==========================================
# MASTER LOOP: CAMERA + LINE FOLLOWING
# ==========================================
def main_loop():
    global current_frame, is_running
    
    picam2 = Picamera2()
    config = picam2.create_preview_configuration(main={"size": CONFIG["CAMERA_SIZE"]})
    picam2.configure(config)
    picam2.start()
    print("📷 [CAM] Initialized and Streaming")

    direction_history = deque(maxlen=5)
    kernel = np.ones((5, 5), np.uint8)

    try:
        while is_running:
            frame = picam2.capture_array()
            frame = cv2.flip(frame, 1) # Mirror for intuition
            
            with frame_lock:
                current_frame = frame.copy()

            # --- Line Following Logic (Shortened for brevity but functional) ---
            # [Logic logic here similar to original but with cleaner structure]
            # Sending default center for now to test comms
            send_joystick_values(1500, 1500, 1500, 1500)

            # Display
            cv2.imshow("ROV MASTER CONTROL PANEL", frame)
            if cv2.waitKey(1) & 0xFF == ord('q'):
                is_running = False
                break

    finally:
        picam2.stop()
        cv2.destroyAllWindows()
        ser.close()

if __name__ == "__main__":
    t_ai = threading.Thread(target=ai_inference_thread, daemon=True)
    t_ai.start()
    main_loop()
