import cv2
import numpy as np
import tensorflow as tf
import threading

# Kategoriler ve model yükleme
categories = ['circle', 'hexagon', 'parallelogram', 'pentagon', 'rectangle', 'rhombus', 'square', 'triangle']
model = tf.keras.models.load_model("shape_model_final1.h5")

# Kamera nesnesi
cap = cv2.VideoCapture(0)

def line_following():
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
        roi_center_x = (roi_left + roi_right) // 2
        roi_center_y = (roi_top + roi_bottom) // 2

        # Görüntüyü gri yap ve CLAHE uygula
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        gray = clahe.apply(gray)

        # Tüm karede siyah çizgi maskesi
        hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)
        lower_black = np.array([0, 0, 0])
        upper_black = np.array([180, 255, 80])
        mask = cv2.inRange(hsv, lower_black, upper_black)

        result = cv2.bitwise_and(frame, frame, mask=mask)
        result = cv2.GaussianBlur(result, (5, 5), 0)

        edges = cv2.Canny(result, 50, 150)
        kernel = np.ones((5, 5), np.uint8)
        edges = cv2.morphologyEx(edges, cv2.MORPH_CLOSE, kernel)

        contours, _ = cv2.findContours(edges, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)

        if contours:
            largest_contour = max(contours, key=cv2.contourArea)
            M = cv2.moments(largest_contour)

            if M["m00"] != 0:
                cx = int(M["m10"] / M["m00"])
                cy = int(M["m01"] / M["m00"])

                cv2.circle(frame, (cx, cy), 5, (0, 255, 0), -1)
                delta_x = cx - roi_center_x
                delta_y = cy - roi_center_y

                frame_center = width // 2

                # ROI içinde mi?
                if roi_left <= cx <= roi_right and roi_top <= cy <= roi_bottom:
                    if cx < frame_center - 50:
                        direction = "SOL"
                    elif cx > frame_center + 50:
                        direction = "SAG"
                    else:
                        direction = "DUZ ILERLE"
                else:
                    # ROI dışında, merkeze geri yönlendirme
                    if cx < roi_center_x - 10:
                        direction = "SAG (Geri ROI'ye)"
                    elif cx > roi_center_x + 10:
                        direction = "SOL (Geri ROI'ye)"
                    else:
                        direction = "DUZ ROI'ye"

                cv2.putText(frame, f"deltaX: {delta_x}, deltaY: {delta_y}", (50, 50),
                            cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 255), 2)
                cv2.putText(frame, f"Yon: {direction}", (50, 90),
                            cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)

            else:
                cv2.putText(frame, "Merkez hesaplanamadi", (50, 50),
                            cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 255), 2)
        else:
            cv2.putText(frame, "Cizgi bulunamadi", (50, 50),
                        cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 255), 2)

        # Mavi ROI çerçevesini çiz
        cv2.rectangle(frame, (roi_left, roi_top), (roi_right, roi_bottom), (255, 0, 0), 2)

        cv2.imshow("Underwater Line Following", frame)
        cv2.imshow("Threshold", mask)

        if cv2.waitKey(1) & 0xFF == ord('q'):
            break


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