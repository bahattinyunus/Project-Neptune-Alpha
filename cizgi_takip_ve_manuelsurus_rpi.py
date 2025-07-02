import cv2
import numpy as np
import RPi.GPIO as GPIO
import time

# GPIO pin tanımları (ESC sinyalleri)
ESC_SAG = 17
ESC_SOL = 18

GPIO.setmode(GPIO.BCM)
GPIO.setup(ESC_SAG, GPIO.OUT)
GPIO.setup(ESC_SOL, GPIO.OUT)

pwm_sag = GPIO.PWM(ESC_SAG, 50)  # 50Hz PWM (standart ESC frekansı)
pwm_sol = GPIO.PWM(ESC_SOL, 50)

pwm_sag.start(0)
pwm_sol.start(0)

def set_pwm_us(pwm, us):
    duty = us / 20000 * 100  # 20ms periyotta yüzdeye çevirme
    pwm.ChangeDutyCycle(duty)

# ESC başlangıç için kalibrasyon (gerekirse)
print("ESC'ler kalibre ediliyor...")
set_pwm_us(pwm_sag, 1500)
set_pwm_us(pwm_sol, 1500)
time.sleep(2)

cap = cv2.VideoCapture(0)
clahe = cv2.createCLAHE(clipLimit=2.0, tileGridSize=(8, 8))

try:
    while True:
        ret, frame = cap.read()
        if not ret:
            break

        hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)
        lower_black = np.array([0, 0, 0])
        upper_black = np.array([180, 255, 50])
        mask = cv2.inRange(hsv, lower_black, upper_black)

        result = cv2.bitwise_and(frame, frame, mask=mask)
        result = cv2.GaussianBlur(result, (5, 5), 0)
        edges = cv2.Canny(result, 50, 150)

        kernel = np.ones((5, 5), np.uint8)
        edges = cv2.morphologyEx(edges, cv2.MORPH_CLOSE, kernel)

        contours, _ = cv2.findContours(edges, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)

        direction = "BEKLE"
        frame_center = frame.shape[1] // 2

        if contours:
            largest_contour = max(contours, key=cv2.contourArea)
            M = cv2.moments(largest_contour)
            if M["m00"] != 0:
                cx = int(M["m10"] / M["m00"])
                cy = int(M["m01"] / M["m00"])
                cv2.circle(frame, (cx, cy), 5, (0, 255, 0), -1)

                if cx < frame_center - 50:
                    direction = "SOL"
                    set_pwm_us(pwm_sag, 1600)
                    set_pwm_us(pwm_sol, 1400)
                elif cx > frame_center + 50:
                    direction = "SAG"
                    set_pwm_us(pwm_sag, 1400)
                    set_pwm_us(pwm_sol, 1600)
                else:
                    direction = "DUZ"
                    set_pwm_us(pwm_sag, 1600)
                    set_pwm_us(pwm_sol, 1600)

        cv2.putText(frame, f"Yon: {direction}", (50, 50),
                    cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)

        cv2.imshow("Camera", frame)
        cv2.imshow("Mask", mask)

        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

finally:
    print("ESC durduruluyor...")
    set_pwm_us(pwm_sag, 1500)
    set_pwm_us(pwm_sol, 1500)
    time.sleep(1)
    pwm_sag.stop()
    pwm_sol.stop()
    GPIO.cleanup()
    cap.release()
    cv2.destroyAllWindows()
