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

    while True:
        ret, frame = cap.read()
        if not ret:
            break

        frame = cv2.flip(frame, 1)
        height, width, _ = frame.shape

        # Görüntüyü 3x3 grid’e böl
        grid_h = height // 3
        grid_w = width // 3

        weights = [[0]*3 for _ in range(3)]  # Ağırlık matrisi (her karedeki siyah yoğunluğu)

        # HSV maskeleme ayarları
        hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)
        mask = cv2.inRange(hsv, (0, 0, 0), (180, 255, 80))

        for i in range(3):  # satırlar
            for j in range(3):  # sütunlar
                y1 = i * grid_h
                y2 = (i + 1) * grid_h
                x1 = j * grid_w
                x2 = (j + 1) * grid_w

                cell = mask[y1:y2, x1:x2]
                black_pixel_count = cv2.countNonZero(cell)
                weights[i][j] = black_pixel_count

                # Her hücreyi çiz ve yoğunluğu yaz
                cv2.rectangle(frame, (x1, y1), (x2, y2), (255, 0, 0), 1)
                cv2.putText(frame, str(black_pixel_count), (x1 + 5, y1 + 20), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 255), 1)

        # Karar mantığı: alt orta hücre en çoksa düz, sol ya da sağsa yön ver
        bottom_row = weights[2]
        middle_row = weights[1]

        left = bottom_row[0] + middle_row[0]
        center = bottom_row[1] + middle_row[1]
        right = bottom_row[2] + middle_row[2]

        if max(left, center, right) < 500:
            direction = "CIZGI YOK"
        elif center >= max(left, right):
            direction = "DUZ ILERLE"
        elif left > right:
            direction = "SOL"
        else:
            direction = "SAG"

        stable_direction = get_stable_direction(direction)
        cv2.putText(frame, f"Yon: {stable_direction}", (30, 30),
                    cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)

        # Gösterimler
        cv2.imshow("Underwater Line Following", frame)
        cv2.imshow("Line Mask", mask)

        if cv2.waitKey(1) & 0xFF == ord('q'):
            break


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