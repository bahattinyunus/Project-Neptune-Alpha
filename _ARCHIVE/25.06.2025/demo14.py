import cv2
import numpy as np
from collections import deque, Counter
import serial
import time

# ESP32 seri bağlantı
ser = serial.Serial("COM8", 115200)
time.sleep(2)

# PID sabitleri
Kp, Ki, Kd = 0.4, 0.0, 0.15
previous_error = 0
integral = 0

# Yön karar geçmişi
direction_history = deque(maxlen=5)

# Kamera başlatılır
cap = cv2.VideoCapture(0)

# Keşif modu kontrolü
exploration_mode = False
exploration_counter = 0

# Açıya veya merkeze uzaklığa göre joystick değeri ölçekleyici

def scale(val, val_min, val_max, out_min, out_max):
    val = np.clip(val, val_min, val_max)
    return int(np.interp(val, [val_min, val_max], [out_min, out_max]))

def scaled_joystick_value(direction, orientation_angle=None, cx_offset=None):
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
        y2 = 1600
    elif direction == "DON (CIZGI ARANIYOR)":
        x1 = 1650

    return x1, y1, x2, y2

# ESP32'ye joystick verisi gönder

def send_joystick_values(x1, y1, x2, y2):
    msg = f"X1:{x1},Y1:{y1},X2:{x2},Y2:{y2}\n"
    ser.write(msg.encode())

# Motor değerlerini oku

def read_motor_values():
    while ser.in_waiting:
        print("[ESP32]:", ser.readline().decode().strip())

# PCA ile açı hesapla

def get_orientation(contour):
    sz = len(contour)
    data_pts = np.empty((sz, 2), dtype=np.float64)
    for i in range(sz):
        data_pts[i] = contour[i, 0]
    _, eigenvectors, _ = cv2.PCACompute2(data_pts, mean=np.empty((0)))
    angle = np.arctan2(eigenvectors[0, 1], eigenvectors[0, 0])
    return np.degrees(angle)

# Yatay/dikey ayrımı

def is_vertical_line(angle_deg, tan_threshold=1.5):
    return abs(np.tan(np.radians(angle_deg))) > tan_threshold

def is_horizontal_line(angle_deg, tan_threshold=0.7):
    return abs(np.tan(np.radians(angle_deg))) < tan_threshold

# Karar sabitleyici

def get_stable_direction(current):
    direction_history.append(current)
    return Counter(direction_history).most_common(1)[0][0]

# Ana döngü

def line_following():
    global previous_error, integral, exploration_mode, exploration_counter

    kernel = np.ones((5, 5), np.uint8)

    while True:
        ret, frame = cap.read()
        if not ret:
            break

        frame = cv2.flip(frame, 1)
        height, width = frame.shape[:2]

        roi_top = height - 150
        roi_bottom = height
        roi_left = width // 2 - 100
        roi_right = width // 2 + 100
        roi_center_x = (roi_right - roi_left) // 2
        roi_center_global_x = (roi_left + roi_right) // 2
        roi = frame[roi_top:roi_bottom, roi_left:roi_right]

        blurred_roi = cv2.GaussianBlur(roi, (7, 7), 0)
        hsv_roi = cv2.cvtColor(blurred_roi, cv2.COLOR_BGR2HSV)
        lower_black = np.array([0, 0, 0])
        upper_black = np.array([180, 255, 90])
        mask_roi = cv2.inRange(hsv_roi, lower_black, upper_black)
        mask_roi = cv2.morphologyEx(mask_roi, cv2.MORPH_CLOSE, kernel)
        contours_roi, _ = cv2.findContours(mask_roi, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)
        filtered_roi = [c for c in contours_roi if cv2.contourArea(c) > 500]

        blurred_full = cv2.GaussianBlur(frame, (7, 7), 0)
        hsv_full = cv2.cvtColor(blurred_full, cv2.COLOR_BGR2HSV)
        mask_full = cv2.inRange(hsv_full, lower_black, upper_black)
        mask_full = cv2.morphologyEx(mask_full, cv2.MORPH_CLOSE, kernel)
        contours_full, _ = cv2.findContours(mask_full, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)
        filtered_full = [c for c in contours_full if cv2.contourArea(c) > 500]

        direction = "CIZGI YOK"
        found_line = False
        orientation_angle = None
        cx_offset = None

        if filtered_roi:
            largest = max(filtered_roi, key=cv2.contourArea)
            M = cv2.moments(largest)
            if M["m00"] != 0:
                cx_roi = int(M["m10"] / M["m00"])
                cy_roi = int(M["m01"] / M["m00"])
                cx_global = cx_roi + roi_left
                cy_global = cy_roi + roi_top

                orientation_angle = get_orientation(largest)
                error = cx_roi - roi_center_x
                integral += error
                derivative = error - previous_error
                previous_error = error
                cx_offset = error

                found_line = True
                exploration_mode = False
                exploration_counter = 0

                if is_vertical_line(orientation_angle):
                    direction = "DUZ ILERLE" if abs(error) < 30 else ("SOL KAY" if error < 0 else "SAG KAY")
                elif is_horizontal_line(orientation_angle):
                    direction = "SOL DON" if error < 0 else "SAG DON"
                else:
                    direction = "SOL DON" if orientation_angle < 0 else "SAG DON"

                cv2.drawContours(roi, [largest], -1, (0, 255, 0), 2)
                cv2.circle(frame, (cx_global, cy_global), 6, (0, 255, 0), -1)

        elif filtered_full:
            largest = max(filtered_full, key=cv2.contourArea)
            M = cv2.moments(largest)
            if M["m00"] != 0:
                cx_full = int(M["m10"] / M["m00"])
                cy_full = int(M["m01"] / M["m00"])
                cx_offset = cx_full - roi_center_global_x

                found_line = True
                exploration_mode = False
                exploration_counter = 0

                direction = "DUZ ILERLE" if abs(cx_offset) < 30 else ("SOL KAY" if cx_offset < 0 else "SAG KAY")

                cv2.drawContours(frame, [largest], -1, (0, 165, 255), 2)
                cv2.circle(frame, (cx_full, cy_full), 8, (0, 165, 255), -1)

        else:
            exploration_counter += 1
            if exploration_counter > 10:
                exploration_mode = True

        if exploration_mode:
            direction = "DON (CIZGI ARANIYOR)"

        stable_direction = get_stable_direction(direction)

        x1, y1, x2, y2 = scaled_joystick_value(stable_direction, orientation_angle, cx_offset)
        send_joystick_values(x1, y1, x2, y2)
        read_motor_values()

        cv2.putText(frame, f"Yon: {stable_direction}", (30, 50), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)
        if orientation_angle is not None:
            cv2.putText(frame, f"Aci: {int(orientation_angle)}", (30, 90), cv2.FONT_HERSHEY_SIMPLEX, 0.8, (255, 255, 0), 2)
        cv2.putText(frame, f"X1:{x1} Y1:{y1} X2:{x2} Y2:{y2}", (30, 130), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 200, 200), 2)
        cv2.rectangle(frame, (roi_left, roi_top), (roi_right, roi_bottom), (255, 0, 0), 2)

        cv2.imshow("Line Following", frame)
        cv2.imshow("ROI Mask", mask_roi)

        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

    cap.release()
    cv2.destroyAllWindows()

if __name__ == "__main__":
    line_following()
