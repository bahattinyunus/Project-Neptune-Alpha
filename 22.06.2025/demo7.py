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

import cv2
import numpy as np

def line_following():
    global previous_error, integral
    clahe = cv2.createCLAHE(clipLimit=2.0, tileGridSize=(8, 8))

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

        roi = frame[roi_top:roi_bottom, roi_left:roi_right]

        # ROI'de çizgi tespiti
        hsv_roi = cv2.cvtColor(roi, cv2.COLOR_BGR2HSV)
        mask_roi = cv2.inRange(hsv_roi, (0, 0, 0), (180, 255, 80))
        edges_roi = cv2.Canny(mask_roi, 50, 150)
        edges_roi = cv2.morphologyEx(edges_roi, cv2.MORPH_CLOSE, np.ones((5, 5), np.uint8))

        contours_roi, _ = cv2.findContours(edges_roi, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)

        direction = "DUZ ILERLE"
        found_in_roi = False

        if contours_roi:
            largest = max(contours_roi, key=cv2.contourArea)
            M = cv2.moments(largest)
            if M["m00"] != 0:
                cx_roi = int(M["m10"] / M["m00"])
                cy_roi = int(M["m01"] / M["m00"])
                cx_global = cx_roi + roi_left
                cy_global = cy_roi + roi_top
                found_in_roi = True
        else:
            # ROI'de bulunamazsa tüm framede arayacağız
            hsv_all = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)
            mask_all = cv2.inRange(hsv_all, (0, 0, 0), (180, 255, 80))
            edges_all = cv2.Canny(mask_all, 50, 150)
            edges_all = cv2.morphologyEx(edges_all, cv2.MORPH_CLOSE, np.ones((5, 5), np.uint8))

            contours_all, _ = cv2.findContours(edges_all, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)

            if contours_all:
                largest = max(contours_all, key=cv2.contourArea)
                M = cv2.moments(largest)
                if M["m00"] != 0:
                    cx_global = int(M["m10"] / M["m00"])
                    cy_global = int(M["m01"] / M["m00"])

        if 'cx_global' in locals():
            cv2.circle(frame, (cx_global, cy_global), 5, (0, 255, 0), -1)
            cv2.putText(frame, f"x: {cx_global}, y: {cy_global}", (50, 50),
                        cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 255), 2)

            if found_in_roi:
                error = cx_roi - roi_center_x
                integral += error
                derivative = error - previous_error
                output = Kp * error + Ki * integral + Kd * derivative
                previous_error = error

                # Eşikleri burada tanımlıyoruz
                small_threshold = 30  # hata küçükse düz
                medium_threshold = 60 # orta hata kayma
                # büyük hata dönme

                if abs(error) <= small_threshold:
                    direction = "DUZ ILERLE"
                elif abs(error) <= medium_threshold:
                    if error < 0:
                        direction = "SOL KAY"
                    else:
                        direction = "SAG KAY"
                else:
                    if error < 0:
                        direction = "SOL DON"
                    else:
                        direction = "SAG DON"
            else:
                # ROI'ye geri yönlendirme
                if cx_global < roi_left - 10:
                    direction = "SAG (Geri ROI'ye)"
                elif cx_global > roi_right + 10:
                    direction = "SOL (Geri ROI'ye)"
                elif cy_global < roi_top - 10:
                    direction = "GERI ROI'ye"
                else:
                    direction = "DUZ ROI'ye"

            stable_direction = get_stable_direction(direction)
            cv2.putText(frame, f"Yon: {stable_direction}", (50, 90),
                        cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)
        else:
            cv2.putText(frame, "Cizgi hicbir yerde bulunamadi", (50, 50),
                        cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 255), 2)

        cv2.rectangle(frame, (roi_left, roi_top), (roi_right, roi_bottom), (255, 0, 0), 2)

        cv2.imshow("Underwater Line Following", frame)
        cv2.imshow("ROI Mask", mask_roi)

        if cv2.waitKey(1) & 0xFF == ord('q'):
            break


    cap.release()
    cv2.destroyAllWindows()

if __name__ == "__main__":
    line_following()


    cap.release()
    cv2.destroyAllWindows()


    cap.release()
    cv2.destroyAllWindows()


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