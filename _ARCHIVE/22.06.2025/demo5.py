import cv2
import numpy as np
import tensorflow as tf
import threading
import time
from collections import deque, Counter


# Kategoriler ve model yükleme
categories = ['circle', 'hexagon', 'parallelogram', 'pentagon', 'rectangle', 'rhombus', 'square', 'triangle']
model = tf.keras.models.load_model("shape_model_final1.h5")

# Kamera nesnesi
cap = cv2.VideoCapture(0)

# PID parametreleri
Kp = 0.4
Ki = 0.0
Kd = 0.15
previous_error = 0
integral = 0

# Karar sabitleme (moving mode)
direction_history = deque(maxlen=5)
last_applied_direction = "DUZ ILERLE"
last_direction_time = time.time()

# Karar üretme fonksiyonu
def get_stable_direction(current_direction):
    direction_history.append(current_direction)
    direction_mode = Counter(direction_history).most_common(1)[0][0]
    return direction_mode

def line_following():
    global previous_error, integral
    clahe = cv2.createCLAHE(clipLimit=2.0, tileGridSize=(8, 8))
    cap = cv2.VideoCapture(0)

    while True:
        ret, frame = cap.read()
        if not ret:
            break

        frame = cv2.flip(frame, 1)
        height, width, _ = frame.shape

        roi_top = height - 150
        roi_bottom = height
        roi_left = width // 2 - 100
        roi_right = width // 2 + 100
        roi_center_x = (roi_right - roi_left) // 2
        roi_center_y = (roi_bottom - roi_top) // 2

        # --- ROI'yi çıkar ---
        roi = frame[roi_top:roi_bottom, roi_left:roi_right]
        hsv_roi = cv2.cvtColor(roi, cv2.COLOR_BGR2HSV)
        mask_roi = cv2.inRange(hsv_roi, np.array([0, 0, 0]), np.array([180, 255, 80]))
        blur_roi = cv2.GaussianBlur(mask_roi, (5, 5), 0)
        edges_roi = cv2.Canny(blur_roi, 50, 150)
        kernel = np.ones((5, 5), np.uint8)
        edges_roi = cv2.morphologyEx(edges_roi, cv2.MORPH_CLOSE, kernel)

        contours_roi, _ = cv2.findContours(edges_roi, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)

        direction = "DUZ ILERLE"
        delta_x = 0
        stable_direction = "DUZ ILERLE"

        if contours_roi:
            largest_contour = max(contours_roi, key=cv2.contourArea)
            M = cv2.moments(largest_contour)

            if M["m00"] != 0:
                # ROI içi merkez
                cx = int(M["m10"] / M["m00"])
                cy = int(M["m01"] / M["m00"])
                delta_x = cx - roi_center_x

                # PID hesaplama
                error = delta_x
                integral += error
                derivative = error - previous_error
                output = Kp * error + Ki * integral + Kd * derivative
                previous_error = error

                # Yön belirleme
                if abs(delta_x) < 30:
                    direction = "DUZ ILERLE"
                elif delta_x < -30:
                    direction = "SOL"
                elif delta_x > 30:
                    direction = "SAG"

                stable_direction = get_stable_direction(direction)

                # Nokta işaretle (global frame'e çevrilmiş)
                cv2.circle(frame, (roi_left + cx, roi_top + cy), 5, (0, 255, 0), -1)
                cv2.putText(frame, f"deltaX: {delta_x}", (50, 50),
                            cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 255), 2)
                cv2.putText(frame, f"Yon: {stable_direction}", (50, 90),
                            cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)
            else:
                cv2.putText(frame, "ROI'de merkez hesaplanamadi", (50, 50),
                            cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 255), 2)
        else:
            # ROI'de çizgi yoksa: tüm karede çizgi arayarak geri yön belirleme
            hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)
            mask = cv2.inRange(hsv, np.array([0, 0, 0]), np.array([180, 255, 80]))
            blur = cv2.GaussianBlur(mask, (5, 5), 0)
            edges = cv2.Canny(blur, 50, 150)
            edges = cv2.morphologyEx(edges, cv2.MORPH_CLOSE, kernel)
            contours_full, _ = cv2.findContours(edges, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)

            if contours_full:
                largest = max(contours_full, key=cv2.contourArea)
                M = cv2.moments(largest)
                if M["m00"] != 0:
                    cx = int(M["m10"] / M["m00"])
                    if cx < roi_left:
                        stable_direction = "SAG (Geri ROI'ye)"
                    elif cx > roi_right:
                        stable_direction = "SOL (Geri ROI'ye)"
                    else:
                        stable_direction = "DUZ ROI'ye"
                    cv2.circle(frame, (cx, roi_bottom - 75), 5, (0, 255, 255), -1)
            else:
                stable_direction = "CIZGI YOK"

            cv2.putText(frame, f"Yon: {stable_direction}", (50, 90),
                        cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 255), 2)

        # ROI dikdörtgeni
        cv2.rectangle(frame, (roi_left, roi_top), (roi_right, roi_bottom), (255, 0, 0), 2)
        cv2.imshow("Underwater Line Following", frame)
        cv2.imshow("ROI Mask", mask_roi)

        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

    cap.release()
    cv2.destroyAllWindows()


    cap.release()
    cv2.destroyAllWindows()

        
def shape_detection():
    while True:
        ret, frame = cap.read()
        if not ret:
            break

        roi = cv2.resize(frame, (64, 64))
        img_array = roi.astype('float32') / 255.0
        img_array = np.expand_dims(img_array, axis=0)

        prediction = model.predict(img_array)
        predicted_class = categories[np.argmax(prediction)]

        if predicted_class:
            frame_copy = frame.copy()
            cv2.putText(frame_copy, f"Tahmin: {predicted_class}", (10, 30),
                        cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)

            cv2.imshow("Canli Tahmin", frame_copy)

        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

# Thread'leri başlat
thread1 = threading.Thread(target=shape_detection)
thread2 = threading.Thread(target=line_following)

thread1.start()
thread2.start()

thread1.join()
thread2.join()

cap.release()
cv2.destroyAllWindows()