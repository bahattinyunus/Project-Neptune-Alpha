import cv2
import numpy as np
from collections import deque, Counter
import serial
import time

# ESP32 Seri Bağlantı
ser = serial.Serial("COM8", 115200)
time.sleep(2)

# PID Parametreleri
Kp, Ki, Kd = 0.4, 0.0, 0.15
previous_error = 0
integral = 0

# Yön geçmişi (karar sabitleme için)
direction_history = deque(maxlen=5)

# Kamera başlat
cap = cv2.VideoCapture(0)

# Keşif modu
exploration_mode = False
exploration_counter = 0

# 🎮 Yalnızca bir ekseni değiştiren joystick fonksiyonu
def scaled_joystick_value(direction, orientation_angle=None, cx_offset=None):
    # Başlangıçta tüm eksenler 1500
    x1, x2, y1, y2 = 1500, 1500, 1500, 1500

    def scale(val, val_min, val_max, out_min, out_max):
        val = np.clip(val, val_min, val_max)
        scaled = np.interp(val, [val_min, val_max], [out_min, out_max])
        return int(scaled)

    if direction == "SAG DON" and orientation_angle is not None:
        delta = abs(orientation_angle - 90)
        x1 = scale(delta, 0, 45, 1500, 1700)  # yumuşak-sağdan sert-sağa
    elif direction == "SOL DON" and orientation_angle is not None:
        delta = abs(orientation_angle + 90)
        x1 = scale(delta, 0, 45, 1500, 1300)
    elif direction == "SAG KAY" and cx_offset is not None:
        x2 = scale(cx_offset, 0, 100, 1500, 1700)
    elif direction == "SOL KAY" and cx_offset is not None:
        x2 = scale(-cx_offset, 0, 100, 1500, 1300)
    elif direction == "DUZ ILERLE":
        y2 = 1600  # sabit değer, istenirse scale yapılabilir
    elif direction == "DON (CIZGI ARANIYOR)":
        x1 = 1650  # sabit dönme hareketi

    return x1, y1, x2, y2


# ESP32’ye joystick verilerini gönder
def send_joystick_values(x1, y1, x2, y2):
    message = f"X1:{x1},Y1:{y1},X2:{x2},Y2:{y2}\n"
    ser.write(message.encode('utf-8'))

# ESP32’den motor verilerini oku
def read_motor_values():
    while ser.in_waiting:
        line = ser.readline().decode('utf-8').strip()
        print("[ESP32]:", line)

# Konturdan yön açısı hesapla
def get_orientation(contour):
    sz = len(contour)
    data_pts = np.empty((sz, 2), dtype=np.float64)
    for i in range(sz):
        data_pts[i] = contour[i, 0]
    mean, eigenvectors, _ = cv2.PCACompute2(data_pts, mean=np.empty((0)))
    angle = np.arctan2(eigenvectors[0, 1], eigenvectors[0, 0])
    return np.degrees(angle)

# Kararı sabitle
def get_stable_direction(current_direction):
    direction_history.append(current_direction)
    return Counter(direction_history).most_common(1)[0][0]

# Ana fonksiyon: çizgi takibi
def line_following():
    global previous_error, integral, exploration_mode, exploration_counter

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
        roi_center_global_x = (roi_left + roi_right) // 2
        roi = frame[roi_top:roi_bottom, roi_left:roi_right]

        # Maskeleme
        blurred_roi = cv2.GaussianBlur(roi, (7, 7), 0)
        hsv_roi = cv2.cvtColor(blurred_roi, cv2.COLOR_BGR2HSV)
        lower_black = np.array([0, 0, 0])
        upper_black = np.array([180, 255, 90])
        mask_roi = cv2.inRange(hsv_roi, lower_black, upper_black)
        mask_roi = cv2.morphologyEx(mask_roi, cv2.MORPH_CLOSE, kernel)
        contours_roi, _ = cv2.findContours(mask_roi, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)
        filtered_roi = [cnt for cnt in contours_roi if cv2.contourArea(cnt) > 500]

        # Tüm ekran için maske
        blurred_full = cv2.GaussianBlur(frame, (7, 7), 0)
        hsv_full = cv2.cvtColor(blurred_full, cv2.COLOR_BGR2HSV)
        mask_full = cv2.inRange(hsv_full, lower_black, upper_black)
        mask_full = cv2.morphologyEx(mask_full, cv2.MORPH_CLOSE, kernel)
        contours_full, _ = cv2.findContours(mask_full, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)
        filtered_full = [cnt for cnt in contours_full if cv2.contourArea(cnt) > 500]

        direction = "CIZGI YOK"
        found_line = False
        orientation_angle = None

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

                if angle_deviation < angle_tolerance:
                    direction = "DUZ ILERLE" if abs(error) < 30 else ("SOL KAY" if error < 0 else "SAG KAY")
                else:
                    direction = "SOL DON" if orientation_angle < -5 else ("SAG DON" if orientation_angle > 5 else "DUZ ILERLE")

                cv2.drawContours(roi, [largest], -1, (0, 255, 0), 2)
                cv2.circle(frame, (cx_global, cy_global), 6, (0, 255, 0), -1)

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

                direction = "DUZ ILERLE" if abs(error_outside) < 30 else (
                    "SOL KAY" if error_outside < 0 else "SAG KAY")

                cv2.drawContours(frame, [largest_full], -1, (0, 165, 255), 2)
                cv2.circle(frame, (cx_full, cy_full), 8, (0, 165, 255), -1)

        else:
            exploration_counter += 1
            if exploration_counter > 10:
                exploration_mode = True

        if exploration_mode:
            direction = "DON (CIZGI ARANIYOR)"

        # Kararı sabitle
        stable_direction = get_stable_direction(direction)

                # Joystick verilerini al ve gönder
        if stable_direction in ["SAG DON", "SOL DON"]:
            x1, y1, x2, y2 = scaled_joystick_value(stable_direction, orientation_angle=orientation_angle)
        elif stable_direction in ["SAG KAY", "SOL KAY"]:
            cx_offset = cx_roi - roi_center_x if 'cx_roi' in locals() else cx_full - roi_center_global_x
            x1, y1, x2, y2 = scaled_joystick_value(stable_direction, cx_offset=cx_offset)
        else:
            x1, y1, x2, y2 = scaled_joystick_value(stable_direction)

        send_joystick_values(x1, y1, x2, y2)
        read_motor_values()


        # Görsel yazılar
        cv2.putText(frame, f"Yon: {stable_direction}", (30, 50), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)
        if orientation_angle is not None:
            cv2.putText(frame, f"Aci: {int(orientation_angle)} deg", (30, 90), cv2.FONT_HERSHEY_SIMPLEX, 0.8, (255, 255, 0), 2)
        if found_line:
            if 'cx_global' in locals():
                cv2.putText(frame, f"x: {cx_global}, y: {cy_global}", (30, 130), cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 255, 255), 2)
            elif 'cx_full' in locals():
                cv2.putText(frame, f"x: {cx_full}, y: {cy_full}", (30, 130), cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 255, 255), 2)

        # Joystick değerlerini göster
        cv2.putText(frame, f"X1:{x1} Y1:{y1}", (30, 170), cv2.FONT_HERSHEY_SIMPLEX, 0.8, (200, 200, 255), 2)
        cv2.putText(frame, f"X2:{x2} Y2:{y2}", (30, 210), cv2.FONT_HERSHEY_SIMPLEX, 0.8, (200, 200, 255), 2)

        # ROI çiz
        cv2.rectangle(frame, (roi_left, roi_top), (roi_right, roi_bottom), (255, 0, 0), 2)

        # Pencereler
        cv2.imshow("Underwater Line Following", frame)
        cv2.imshow("ROI Mask", mask_roi)

        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

    cap.release()
    cv2.destroyAllWindows()

if __name__ == "__main__":
    line_following()
