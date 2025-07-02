import cv2
import numpy as np
import serial
import time

# ESP32'nin bağlı olduğu seri portu ve baudrate'i ayarla
ser = serial.Serial('COM3', 9600)  # COM3 yerine kendi portunu yaz
time.sleep(2)  # ESP32'nin hazır olması için kısa bekleme

cap = cv2.VideoCapture(0)
clahe = cv2.createCLAHE(clipLimit=2.0, tileGridSize=(8, 8))

while True:
    ret, frame = cap.read()
    if not ret:
        break

    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    gray = clahe.apply(gray)
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

    if contours:
        largest_contour = max(contours, key=cv2.contourArea)
        M = cv2.moments(largest_contour)

        if M["m00"] != 0:
            cx = int(M["m10"] / M["m00"])
            cy = int(M["m01"] / M["m00"])
            cv2.circle(frame, (cx, cy), 5, (0, 255, 0), -1)

            frame_center = frame.shape[1] // 2
            if cx < frame_center - 50:
                direction = "SOL"
                ser.write(b'L')
            elif cx > frame_center + 50:
                direction = "SAG"
                ser.write(b'R')
            else:
                direction = "DUZ"
                ser.write(b'F')

    cv2.putText(frame, f"Yon: {direction}", (50, 50),
                cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)

    cv2.imshow("Kamera", frame)
    cv2.imshow("Maske", mask)

    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

cap.release()
ser.close()
cv2.destroyAllWindows()
#Seri iletişim kodu goruntuye gore L F R harfi göndercek
#c++ ardunıo kodu komutlara gore araca yon verecek

#include <ESP32Servo.h>

#define maxdeger 1940
#define mindeger 1060

Servo onsagalt, onsolalt, onsolust, onsagust;
Servo arsagalt, arsagust, arsolalt, arsolust;

void setup() {
  Serial.begin(9600);
  Serial.println("OTOMATİK MOD: ÇİZGİ TAKİP");

  onsagust.attach(D1);
  onsolust.attach(D2); 
  arsolust.attach(D3);
  arsagust.attach(D4);
  onsagalt.attach(D5);
  onsolalt.attach(D6);
  arsolalt.attach(D7);
  arsagalt.attach(D8);
}

void loop() {
  if (Serial.available() > 0) {
    char komut = Serial.read();

    if (komut == 'F') {  // DÜZ GİT
      hareketVer(1600, 1600);
    } else if (komut == 'L') {  // SOLA DÖN
      hareketVer(1400, 1600);
    } else if (komut == 'R') {  // SAĞA DÖN
      hareketVer(1600, 1400);
    }
  }
}

void hareketVer(int sol, int sag) {
  onsagust.writeMicroseconds(sag);
  onsagalt.writeMicroseconds(sag);
  arsagust.writeMicroseconds(sag);
  arsagalt.writeMicroseconds(sag);

  onsolust.writeMicroseconds(sol);
  onsolalt.writeMicroseconds(sol);
  arsolust.writeMicroseconds(sol);
  arsolalt.writeMicroseconds(sol);
}
