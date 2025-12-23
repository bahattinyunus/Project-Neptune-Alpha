import cv2
import numpy as np
import threading
import time
from collections import deque, Counter

# PID parametreleri
Kp = 0.4
Ki = 0.0
Kd = 0.15
previous_error = 0
integral = 0

# Yön sabitleme için geçmiş yönler
direction_history = deque(maxlen=5)

# Kamera
cap = cv2.VideoCapture(0)

# Konturdan yön açısını (derece cinsinden) bulan fonksiyon
def get_orientation(contour):
    sz = len(contour)
    data_pts = np.empty((sz, 2), dtype=np.float64)
    for i in range(sz):
        data_pts[i, 0] = contour[i, 0, 0]
        data_pts[i, 1] = contour[i, 0, 1]
    mean, eigenvectors, eigenvalues = cv2.PCACompute2(data_pts, mean=np.empty((0)))
    angle = np.arctan2(eigenvectors[0, 1], eigenvectors[0, 0])
    angle_deg = np.degrees(angle)
    return angle_deg

# Yönü sabitleyen mod fonksiyonu
def get_stable_direction(current_direction):
    direction_history.append(current_direction)
    return Counter(direction_history).most_common(1)[0][0]

# Ana çizgi takip fonksiyonu
def line_following():
    global previous_error, integral

    kernel = np.ones((5, 5), np.uint8)

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

        roi = frame[roi_top:roi_bottom, roi_left:roi_right]
        blurred = cv2.GaussianBlur(roi, (7, 7), 0)
        hsv_roi = cv2.cvtColor(blurred, cv2.COLOR_BGR2HSV)

        lower_black = np.array([0, 0, 0])
        upper_black = np.array([180, 255, 90])
        mask_roi = cv2.inRange(hsv_roi, lower_black, upper_black)
        mask_roi = cv2.morphologyEx(mask_roi, cv2.MORPH_CLOSE, kernel, iterations=1)

        contours_roi, _ = cv2.findContours(mask_roi, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)

        direction = "CIZGI YOK"
        found_in_roi = False
        min_area_threshold = 500

        filtered_contours = [cnt for cnt in contours_roi if cv2.contourArea(cnt) > min_area_threshold]

        if filtered_contours:
            largest = max(filtered_contours, key=cv2.contourArea)
            M = cv2.moments(largest)

            if M["m00"] != 0:
                cx_roi = int(M["m10"] / M["m00"])
                cy_roi = int(M["m01"] / M["m00"])
                cx_global = cx_roi + roi_left
                cy_global = cy_roi + roi_top
                found_in_roi = True

                # PID hesaplama
                error = cx_roi - roi_center_x
                integral += error
                derivative = error - previous_error
                output = Kp * error + Ki * integral + Kd * derivative
                previous_error = error

                # Kontur doğrultusunun ROI’ye göre farkı
                orientation_angle = get_orientation(largest)
                roi_reference_angle = 0  # Yatay eksen (ekran düzlemi)
                angle_difference = abs(orientation_angle - roi_reference_angle)

                # Normalize: 0-180 arası tut
                if angle_difference > 180:
                    angle_difference = 360 - angle_difference

                # Eşikler
                small_threshold = 30
                angle_threshold = 20  # 20° üzeri fark varsa yön değiştir

                # Yön kararı
                if abs(error) <= small_threshold:
                    direction = "DUZ ILERLE"
                else:
                    if angle_difference < angle_threshold:
                        direction = "SOL KAY" if error < 0 else "SAG KAY"
                    else:
                        direction = "SOL DON" if error < 0 else "SAG DON"

                # Görselleştirme
                cv2.drawContours(roi, [largest], -1, (0, 255, 0), 2)
                cv2.circle(frame, (cx_global, cy_global), 7, (0, 255, 0), -1)

        else:
            # ROI'de çizgi bulunamadıysa genel çerçevede ara
            hsv_all = cv2.cvtColor(cv2.GaussianBlur(frame, (7, 7), 0), cv2.COLOR_BGR2HSV)
            mask_all = cv2.inRange(hsv_all, lower_black, upper_black)
            mask_all = cv2.morphologyEx(mask_all, cv2.MORPH_CLOSE, kernel, iterations=1)
            contours_all, _ = cv2.findContours(mask_all, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)
            filtered_all = [cnt for cnt in contours_all if cv2.contourArea(cnt) > min_area_threshold]

            if filtered_all:
                largest = max(filtered_all, key=cv2.contourArea)
                M = cv2.moments(largest)
                if M["m00"] != 0:
                    cx_global = int(M["m10"] / M["m00"])
                    cy_global = int(M["m01"] / M["m00"])

                    if cx_global < roi_left - 10:
                        direction = "SAG (GERI ROI'YE)"
                    elif cx_global > roi_right + 10:
                        direction = "SOL (GERI ROI'YE)"
                    elif cy_global < roi_top - 10:
                        direction = "GERI ROI'YE"
                    else:
                        direction = "DUZ ROI'YE"

                    cv2.circle(frame, (cx_global, cy_global), 7, (0, 255, 255), -1)
                else:
                    direction = "CIZGI YOK"

        stable_direction = get_stable_direction(direction)

        # Görselleştirme yazıları
        cv2.putText(frame, f"Yon: {stable_direction}", (30, 50), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)
        if 'orientation_angle' in locals():
            cv2.putText(frame, f"Aci: {int(orientation_angle)} deg", (30, 90), cv2.FONT_HERSHEY_SIMPLEX, 0.8, (255, 255, 0), 2)
        cv2.putText(frame, f"x: {cx_global if 'cx_global' in locals() else 'N/A'}, y: {cy_global if 'cy_global' in locals() else 'N/A'}", (30, 130), cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 255, 255), 2)

        # ROI çerçevesi
        cv2.rectangle(frame, (roi_left, roi_top), (roi_right, roi_bottom), (255, 0, 0), 2)

        # Ekrana göster
        cv2.imshow("Underwater Line Following", frame)
        cv2.imshow("ROI Mask", mask_roi)

        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

    cap.release()
    cv2.destroyAllWindows()

# Program başlangıcı
if __name__ == "__main__":
    line_following()
