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

# Karar sabitleme için geçmiş yönler (moving mode)
direction_history = deque(maxlen=5)

# Kamera nesnesi
cap = cv2.VideoCapture(0)

def get_stable_direction(current_direction):
    direction_history.append(current_direction)
    direction_mode = Counter(direction_history).most_common(1)[0][0]
    return direction_mode

def line_following():
    global previous_error, integral

    # Morfolojik işlem için kernel
    kernel = np.ones((5, 5), np.uint8)

    while True:
        ret, frame = cap.read()
        if not ret:
            break

        frame = cv2.flip(frame, 1)
        height, width, _ = frame.shape

        # ROI tanımı (alt ortada)
        roi_top = height - 150
        roi_bottom = height
        roi_left = width // 2 - 100
        roi_right = width // 2 + 100
        roi_center_x = (roi_right - roi_left) // 2

        roi = frame[roi_top:roi_bottom, roi_left:roi_right]

        # Parazit azaltmak için Gaussian blur uyguluyoruz
        blurred = cv2.GaussianBlur(roi, (7,7), 0)

        # HSV dönüşümü ve siyah renk maskesi
        hsv_roi = cv2.cvtColor(blurred, cv2.COLOR_BGR2HSV)

        # Siyah renk aralığı, ortam ışığına göre ayarlanabilir
        lower_black = np.array([0, 0, 0])
        upper_black = np.array([180, 255, 90])
        mask_roi = cv2.inRange(hsv_roi, lower_black, upper_black)

        # Morfolojik işlem: kapanış (gürültüyü azaltır)
        mask_roi = cv2.morphologyEx(mask_roi, cv2.MORPH_CLOSE, kernel, iterations=1)

        # Kontur bulma
        contours_roi, _ = cv2.findContours(mask_roi, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)

        direction = "CIZGI YOK"
        found_in_roi = False

        # Minimum kontur alanı eşik değeri
        min_area_threshold = 500

        # Yeterince büyük kontur var mı kontrolü
        filtered_contours = [cnt for cnt in contours_roi if cv2.contourArea(cnt) > min_area_threshold]

        if filtered_contours:
            # En büyük kontur seçilir
            largest = max(filtered_contours, key=cv2.contourArea)
            M = cv2.moments(largest)
            if M["m00"] != 0:
                cx_roi = int(M["m10"] / M["m00"])
                cy_roi = int(M["m01"] / M["m00"])
                cx_global = cx_roi + roi_left
                cy_global = cy_roi + roi_top
                found_in_roi = True

                # Referans noktası sabitlemek için hata hesaplama
                error = cx_roi - roi_center_x
                integral += error
                derivative = error - previous_error
                output = Kp * error + Ki * integral + Kd * derivative
                previous_error = error

                # Hata büyüklüğüne göre hareket komutu
                small_threshold = 30
                medium_threshold = 60

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

                # Algılanan konturu ve merkezi çiz
                cv2.drawContours(roi, [largest], -1, (0, 255, 0), 2)
                cv2.circle(frame, (cx_global, cy_global), 7, (0, 255, 0), -1)
        else:
            # ROI'de çizgi yoksa tüm frame'de arama (daha genel)
            hsv_all = cv2.cvtColor(cv2.GaussianBlur(frame, (7,7), 0), cv2.COLOR_BGR2HSV)
            mask_all = cv2.inRange(hsv_all, lower_black, upper_black)
            mask_all = cv2.morphologyEx(mask_all, cv2.MORPH_CLOSE, kernel, iterations=1)
            contours_all, _ = cv2.findContours(mask_all, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)
            filtered_contours_all = [cnt for cnt in contours_all if cv2.contourArea(cnt) > min_area_threshold]

            if filtered_contours_all:
                largest = max(filtered_contours_all, key=cv2.contourArea)
                M = cv2.moments(largest)
                if M["m00"] != 0:
                    cx_global = int(M["m10"] / M["m00"])
                    cy_global = int(M["m01"] / M["m00"])
                    # ROI'ye geri yönlendirme kararları
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
        cv2.putText(frame, f"Yon: {stable_direction}", (30, 50), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)
        cv2.putText(frame, f"x: {cx_global if 'cx_global' in locals() else 'N/A'}, y: {cy_global if 'cy_global' in locals() else 'N/A'}", (30, 90), cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 255, 255), 2)

        # ROI çizimi
        cv2.rectangle(frame, (roi_left, roi_top), (roi_right, roi_bottom), (255, 0, 0), 2)

        cv2.imshow("Underwater Line Following", frame)
        cv2.imshow("ROI Mask", mask_roi)

        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

    cap.release()
    cv2.destroyAllWindows()

if __name__ == "__main__":
    line_following()

