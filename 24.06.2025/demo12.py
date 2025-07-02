import cv2
import numpy as np
from collections import deque, Counter
import serial
import time

# 🔌 ESP32 seri portu (örneğin COM3 veya /dev/ttyUSB0)
ser = serial.Serial("COM3", 115200)
time.sleep(2)

# PID parametreleri
Kp = 0.4
Ki = 0.0
Kd = 0.15
previous_error = 0
integral = 0

# Yön geçmişini tutar, sarsıntıyı azaltmak için
direction_history = deque(maxlen=5)

# Kamera açılır
cap = cv2.VideoCapture(0)

# Keşif modunda olup olmadığımızı izlemek için
exploration_mode = False
exploration_counter = 0

def direction_to_joystick(direction):
    if direction == "DUZ ILERLE":
        return (1500, 1700, 1500, 1700)
    elif direction == "SOL KAY":
        return (1300, 1700, 1500, 1700)
    elif direction == "SAG KAY":
        return (1700, 1700, 1500, 1700)
    elif direction == "SOL DON":
        return (1300, 1500, 1300, 1500)
    elif direction == "SAG DON":
        return (1700, 1500, 1700, 1500)
    elif direction == "DON (CIZGI ARANIYOR)":
        return (1700, 1300, 1300, 1700)
    else:
        return (1500, 1500, 1500, 1500)

def send_joystick_values(x1, y1, x2, y2):
    message = f"X1:{x1},Y1:{y1},X2:{x2},Y2:{y2}\n"
    ser.write(message.encode('utf-8'))

def read_motor_values():
    while ser.in_waiting:
        line = ser.readline().decode('utf-8').strip()
        print("[ESP32]:", line)

# Konturdan yön açısını PCA ile hesapla (derece cinsinden)
def get_orientation(contour):
    sz = len(contour)
    data_pts = np.empty((sz, 2), dtype=np.float64)
    for i in range(sz):
        data_pts[i, 0] = contour[i, 0, 0]
        data_pts[i, 1] = contour[i, 0, 1]
    mean, eigenvectors, _ = cv2.PCACompute2(data_pts, mean=np.empty((0)))
    angle = np.arctan2(eigenvectors[0, 1], eigenvectors[0, 0])
    return np.degrees(angle)

# Karar sabitleyici: kısa süreli dalgalanmayı engeller
def get_stable_direction(current_direction):
    direction_history.append(current_direction)
    return Counter(direction_history).most_common(1)[0][0]

def line_following():
    global previous_error, integral, exploration_mode, exploration_counter

    kernel = np.ones((5, 5), np.uint8)

    while True:
        ret, frame = cap.read()
        if not ret:
            break

        # Aynalama (opsiyonel, görüntü el komutları için)
        frame = cv2.flip(frame, 1)
        height, width, _ = frame.shape

        # ROI bölgesi
        roi_top = height - 150
        roi_bottom = height
        roi_left = width // 2 - 100
        roi_right = width // 2 + 100
        roi_center_x = (roi_right - roi_left) // 2
        roi_center_global_x = (roi_left + roi_right) // 2

        roi = frame[roi_top:roi_bottom, roi_left:roi_right]

        # ROI için maske işlemleri
        blurred_roi = cv2.GaussianBlur(roi, (7, 7), 0)
        hsv_roi = cv2.cvtColor(blurred_roi, cv2.COLOR_BGR2HSV)
        lower_black = np.array([0, 0, 0])
        upper_black = np.array([180, 255, 90])
        mask_roi = cv2.inRange(hsv_roi, lower_black, upper_black)
        mask_roi = cv2.morphologyEx(mask_roi, cv2.MORPH_CLOSE, kernel, iterations=1)
        contours_roi, _ = cv2.findContours(mask_roi, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)
        min_area = 500
        filtered_roi = [cnt for cnt in contours_roi if cv2.contourArea(cnt) > min_area]

        # Tüm frame için maske işlemleri
        blurred_frame = cv2.GaussianBlur(frame, (7, 7), 0)
        hsv_frame = cv2.cvtColor(blurred_frame, cv2.COLOR_BGR2HSV)
        mask_full = cv2.inRange(hsv_frame, lower_black, upper_black)
        mask_full = cv2.morphologyEx(mask_full, cv2.MORPH_CLOSE, kernel, iterations=1)
        contours_full, _ = cv2.findContours(mask_full, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)
        filtered_full = [cnt for cnt in contours_full if cv2.contourArea(cnt) > min_area]

        direction = "CIZGI YOK"
        found_line = False
        orientation_angle = None

        # 1. ROI içindeki çizgi varsa takip
        if filtered_roi:
            largest = max(filtered_roi, key=cv2.contourArea)
            M = cv2.moments(largest)
            if M["m00"] != 0:
                cx_roi = int(M["m10"] / M["m00"])
                cy_roi = int(M["m01"] / M["m00"])
                cx_global = cx_roi + roi_left
                cy_global = cy_roi + roi_top

                orientation_angle = get_orientation(largest)
                angle_deviation = abs(abs(orientation_angle) - 90)
                angle_tolerance = 15

                error = cx_roi - roi_center_x
                integral += error
                derivative = error - previous_error
                output = Kp * error + Ki * integral + Kd * derivative
                previous_error = error

                found_line = True
                exploration_mode = False
                exploration_counter = 0

                # Açının işaretine göre dönme kararı
                if angle_deviation < angle_tolerance:
                    if abs(error) < 30:
                        direction = "DUZ ILERLE"
                    else:
                        direction = "SOL KAY" if error < 0 else "SAG KAY"
                else:
                    # Burada açının işaretine göre doğru karar veriliyor
                    if orientation_angle < -5:
                        direction = "SOL DON"
                    elif orientation_angle > 5:
                        direction = "SAG DON"
                    else:
                        direction = "DUZ ILERLE"

                # Görsel işaretleme
                cv2.drawContours(roi, [largest], -1, (0, 255, 0), 2)
                cv2.circle(frame, (cx_global, cy_global), 6, (0, 255, 0), -1)

        # 2. ROI dışında çizgi varsa, ROI'ye yaklaştır
        elif filtered_full:
            largest_full = max(filtered_full, key=cv2.contourArea)
            M_full = cv2.moments(largest_full)
            if M_full["m00"] != 0:
                cx_full = int(M_full["m10"] / M_full["m00"])
                cy_full = int(M_full["m01"] / M_full["m00"])

                error_outside = cx_full - roi_center_global_x

                found_line = True
                exploration_mode = False
                exploration_counter = 0

                if abs(error_outside) < 30:
                    direction = "DUZ ILERLE (ROI'YE YAKIN)"
                else:
                    direction = "SOL KAY (ROI'YE DON)" if error_outside < 0 else "SAG KAY (ROI'YE DON)"

                # Görsel işaretleme (turuncu)
                cv2.drawContours(frame, [largest_full], -1, (0, 165, 255), 2)
                cv2.circle(frame, (cx_full, cy_full), 8, (0, 165, 255), -1)

        # 3. Çizgi yoksa keşif modu
        else:
            found_line = False
            exploration_counter += 1
            if exploration_counter > 10:
                exploration_mode = True

        if exploration_mode:
            direction = "DON (CIZGI ARANIYOR)"

        # Kararları yumuşat
        stable_direction = get_stable_direction(direction)

        # Ekrana yazdır
        cv2.putText(frame, f"Yon: {stable_direction}", (30, 50), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)
        if orientation_angle is not None:
            cv2.putText(frame, f"Aci: {int(orientation_angle)} deg", (30, 90), cv2.FONT_HERSHEY_SIMPLEX, 0.8, (255, 255, 0), 2)
        if found_line:
            if 'cx_global' in locals() and 'cy_global' in locals() and stable_direction != "DON (CIZGI ARANIYOR)":
                cv2.putText(frame, f"x: {cx_global}, y: {cy_global}", (30, 130), cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 255, 255), 2)
            elif 'cx_full' in locals() and 'cy_full' in locals():
                cv2.putText(frame, f"x: {cx_full}, y: {cy_full}", (30, 130), cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 255, 255), 2)

        # ROI bölgesi çizgisi
        cv2.rectangle(frame, (roi_left, roi_top), (roi_right, roi_bottom), (255, 0, 0), 2)

        # Pencereler
        cv2.imshow("Underwater Line Following", frame)
        cv2.imshow("ROI Mask", mask_roi)

        # Çıkış tuşu
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

        joystick_vals = direction_to_joystick(stable_direction)
        send_joystick_values(*joystick_vals)
        read_motor_values()

    cap.release()
    cv2.destroyAllWindows()

if __name__ == "__main__":
    line_following()
