import cv2
import numpy as np
import tensorflow as tf

# Kategoriler ve model yükleme
categories = ['circle', 'hexagon', 'parallelogram', 'pentagon', 'rectangle', 'rhombus', 'square', 'triangle']
model = tf.keras.models.load_model("shape_model_final1.h5")

# Kamera başlatma
cap = cv2.VideoCapture(0)

while True:
    ret, frame = cap.read()
    if not ret:
        break

    # Görüntüyü yeniden boyutlandırma ve normalleştirme
    roi = cv2.resize(frame, (64, 64))
    img_array = roi.astype('float32') / 255.0
    img_array = np.expand_dims(img_array, axis=0)

    # Tahmin yapma
    prediction = model.predict(img_array)
    predicted_class = categories[np.argmax(prediction)]

    # Şekli tanımlama ve çerçeve çizme
    if predicted_class:
        # Şekli çerçeveye al
        height, width, _ = frame.shape
        color = (0, 255, 0)  # Yeşil renk
        thickness = 2

        # Şekli çerçeve içine al
        frame = cv2.putText(frame, f"Tahmin: {predicted_class}", (10, 30), cv2.FONT_HERSHEY_SIMPLEX,
                            1, (0, 255, 0), 2, cv2.LINE_AA)

    # Görüntüyü ekranda gösterme
    cv2.imshow("Canli Tahmin", frame)

    # 'q' tuşuna basıldığında çıkış
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

cap.release()
cv2.destroyAllWindows()
