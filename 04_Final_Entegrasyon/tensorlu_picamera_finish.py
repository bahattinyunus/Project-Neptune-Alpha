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
    "SERIAL_PORT": "/dev/ttyUSB0",
    "BAUD_RATE": 115200,
    "CAMERA_SIZE": (640, 480),
    "AI_MODEL": "best_shape_model.keras",
    "CATEGORIES": ['circle', 'hexagon', 'parallelogram', 'pentagon', 'rectangle', 'rhombus', 'square', 'triangle'],
    "PID": {"Kp": 0.4, "Ki": 0.0, "Kd": 0.15},
    "ROI_HEIGHT": 150,
    "ROI_WIDTH_OFFSET": 100,
    "CENTER_VAL": 1500
}

# Global Status
current_frame = None
frame_lock = threading.Lock()
is_running = True
predicted_class = "None"

# ==========================================
# COMMUNICATION LAYER
# ==========================================
try:
    ser = serial.Serial(CONFIG["SERIAL_PORT"], CONFIG["BAUD_RATE"], timeout=0.1)
    time.sleep(2)
    print(f"📡 [PC] Serial connected on {CONFIG['SERIAL_PORT']}")
except Exception as e:
    print(f"❌ [PC] Serial error: {e}")
    sys.exit(1)

def send_joystick_values(x1, y1, x2, y2):
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

def is_vertical_line(angle_deg, tan_threshold=1.5):
    return abs(np.tan(np.radians(angle_deg))) > tan_threshold

def is_horizontal_line(angle_deg, tan_threshold=0.7):
    return abs(np.tan(np.radians(angle_deg))) < tan_threshold

def scaled_joystick_value(direction, orientation_angle=None, cx_offset=None, area=None):
    x1, x2, y1, y2 = 1500, 1500, 1500, 1500
    if direction == "SAG DON" and orientation_angle is not None:
        delta = abs(orientation_angle - 90)
        x1 = scale(delta, 0, 45, 1500, 1700)
    elif direction == "SOL DON" and orientation_angle is not None:
        delta = abs(orientation_angle + 90)
        x1 = scale(delta, 0, 45, 1500, 1300)
    elif direction == "SAG KAY" and cx_offset is not None:
        x2 = scale(cx_offset, 0, 100, 1500, 1700)
    elif direction == "SOL KAY" and cx_offset is not None:
        x2 = scale(-cx_offset, 0, 100, 1500, 1300)
    elif direction == "DUZ ILERLE":
        if area is not None:
            if area < 2000: y1 = 1600
            elif area <= 7000: y1 = scale(area, 2000, 7000, 1600, 1450)
            elif area <= 11000: y1 = scale(area, 7000, 11000, 1450, 1300)
            else: y1 = 1300
        else: y1 = 1600
    elif direction == "DON (CIZGI ARANIYOR)":
        x1 = 1650
    return x1, y1, x2, y2

# ==========================================
# THREAD 01: AI INFERENCE (SHAPE)
# ==========================================
def ai_inference_thread():
    global current_frame, is_running, predicted_class
    print("🧠 [AI] Loading TF Lite Model...")
    model = tf.keras.models.load_model(CONFIG["AI_MODEL"], compile=False)
    
    while is_running:
        with frame_lock:
            if current_frame is None: continue
            working_frame = current_frame.copy()

        roi = cv2.resize(working_frame, (64, 64))
        img_array = roi.astype('float32') / 255.0
        img_array = np.expand_dims(img_array, axis=0)

        prediction = model.predict(img_array, verbose=0)
        predicted_class = CONFIG["CATEGORIES"][np.argmax(prediction)]
        time.sleep(0.1)

# ==========================================
# MASTER LOOP: CAMERA + LINE FOLLOWING
# ==========================================
def main_loop():
    global current_frame, is_running, predicted_class
    
    picam2 = Picamera2()
    config = picam2.create_preview_configuration(main={"size": CONFIG["CAMERA_SIZE"]})
    picam2.configure(config)
    picam2.start()
    print("📷 [CAM] Initialized and Streaming")

    direction_history = deque(maxlen=5)
    kernel = np.ones((5, 5), np.uint8)
    previous_error = 0
    integral = 0
    exploration_mode = False
    exploration_counter = 0

    try:
        while is_running:
            frame = picam2.capture_array()
            frame = cv2.flip(frame, 1)
            
            with frame_lock:
                current_frame = frame.copy()

            height, width = frame.shape[:2]
            roi_top, roi_bottom = height - CONFIG["ROI_HEIGHT"], height
            roi_left, roi_right = width // 2 - CONFIG["ROI_WIDTH_OFFSET"], width // 2 + CONFIG["ROI_WIDTH_OFFSET"]
            roi_center_x = (roi_right - roi_left) // 2
            roi_center_global_x = (roi_left + roi_right) // 2
            roi = frame[roi_top:roi_bottom, roi_left:roi_right]

            # Image processing
            hsv_roi = cv2.cvtColor(cv2.GaussianBlur(roi, (7, 7), 0), cv2.COLOR_BGR2HSV)
            mask_roi = cv2.morphologyEx(cv2.inRange(hsv_roi, np.array([0, 0, 0]), np.array([180, 255, 90])), cv2.MORPH_CLOSE, kernel)
            contours_roi, _ = cv2.findContours(mask_roi, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)
            filtered_roi = [c for c in contours_roi if cv2.contourArea(c) > 500]

            direction = "CIZGI YOK"
            orientation_angle = None
            cx_offset = None
            area = None

            if filtered_roi:
                largest = max(filtered_roi, key=cv2.contourArea)
                area = cv2.contourArea(largest)
                M = cv2.moments(largest)
                if M["m00"] != 0:
                    cx_roi = int(M["m10"] / M["m00"])
                    orientation_angle = get_orientation(largest)
                    error = cx_roi - roi_center_x
                    integral += error
                    derivative = error - previous_error
                    previous_error = error
                    cx_offset = error
                    exploration_mode = False
                    exploration_counter = 0

                    if is_vertical_line(orientation_angle):
                        direction = "DUZ ILERLE" if abs(error) < 30 else ("SOL KAY" if error < 0 else "SAG KAY")
                    elif is_horizontal_line(orientation_angle):
                        direction = "SOL DON" if error < 0 else "SAG DON"
                    else:
                        direction = "SOL DON" if orientation_angle < 0 else "SAG DON"
            else:
                exploration_counter += 1
                if exploration_counter > 10: exploration_mode = True

            if exploration_mode: direction = "DON (CIZGI ARANIYOR)"

            direction_history.append(direction)
            stable_direction = Counter(direction_history).most_common(1)[0][0]
            
            x1, y1, x2, y2 = scaled_joystick_value(stable_direction, orientation_angle, cx_offset, area)
            send_joystick_values(x1, y1, x2, y2)

            # UI
            cv2.putText(frame, f"Yon: {stable_direction}", (30, 50), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)
            cv2.putText(frame, f"AI: {predicted_class}", (30, 90), cv2.FONT_HERSHEY_SIMPLEX, 0.8, (255, 255, 0), 2)
            cv2.imshow("ROV MASTER CONTROL PANEL", frame)
            
            if cv2.waitKey(1) & 0xFF == ord('q'):
                is_running = False
                break
    finally:
        picam2.stop()
        cv2.destroyAllWindows()
        ser.close()

if __name__ == "__main__":
    threading.Thread(target=ai_inference_thread, daemon=True).start()
    main_loop()
