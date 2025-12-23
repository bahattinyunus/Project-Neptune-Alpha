import cv2
import numpy as np
import tensorflow as tf

# Kategoriler ve model yükleme
categories = ['circle', 'hexagon', 'parallelogram', 'pentagon', 'rectangle', 'rhombus', 'square', 'triangle']
model = tf.keras.models.load_model("shape_model_final1.h5")

# Kamera başlatma
cap = cv2.VideoCapture(0)

# CLAHE ayarı
clahe = cv2.createCLAHE(clipLimit=2.0, tileGridSize=(8, 8))

while True:
    ret, frame = cap.read()
    if not ret:
        break

    #########################
    # --- ŞEKİL TAHMİNİ ---
    #########################
    roi = cv2.resize(frame, (64, 64))
    img_array = roi.astype('float32') / 255.0
    img_array = np.expand_dims(img_array, axis=0)

    prediction = model.predict(img_array, verbose=0)
    predicted_class = categories[np.argmax(prediction)]

    cv2.putText(frame, f"Tahmin: {predicted_class}", (10, 30),
                cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)

    #########################
    # --- ÇİZGİ TAKİBİ ---
    #########################
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

    if contours:
        largest_contour = max(contours, key=cv2.contourArea)
        M = cv2.moments(largest_contour)
        if M["m00"] != 0:
            cx = int(M["m10"] / M["m00"])
            cy = int(M["m01"] / M["m00"])

            cv2.circle(frame, (cx, cy), 5, (0, 255, 0), -1)

            frame_center = frame.shape[1] // 2
            if cx < frame_center - 50:
                direction = "Sol"
            elif cx > frame_center + 50:
                direction = "Sag"
            else:
                direction = "Duz İlerle"

            cv2.putText(frame, f"Yon: {direction}", (50, 70),
                        cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)

    #########################
    # --- GÖRÜNTÜLER ---
    #########################
    cv2.imshow("Kombine Sistem", frame)
    cv2.imshow("Threshold", mask)

    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

cap.release()
cv2.destroyAllWindows()
