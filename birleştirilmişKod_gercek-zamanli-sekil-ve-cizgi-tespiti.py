import cv2
import numpy as np
import threading

# --- Kamera Ayarları ---
framewidth = 640
frameheight = 480
cap = cv2.VideoCapture(0)
cap.set(3, framewidth)
cap.set(4, frameheight)

# Ortak Frame Değişkeni
shared_frame = None
lock = threading.Lock()
stop_threads = False

# --- Şekil Tespiti Fonksiyonları ---
def empty(a):
    pass

cv2.namedWindow("Parameters")
cv2.resizeWindow("Parameters", 640, 240)
cv2.createTrackbar("Threshold1", "Parameters", 150, 255, empty)
cv2.createTrackbar("Threshold2", "Parameters", 150, 255, empty)
cv2.createTrackbar("Area", "Parameters", 5000, 30000, empty)

def getContours(img, imgContour):
    contours, _ = cv2.findContours(img, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_NONE)
    for cnt in contours:
        area = cv2.contourArea(cnt)
        areaMin = cv2.getTrackbarPos("Area", "Parameters")
        if area > areaMin:
            cv2.drawContours(imgContour, contours, -1, (255, 0, 255), 2)
            perimeter = cv2.arcLength(cnt, True)
            approx = cv2.approxPolyDP(cnt, 0.01 * perimeter, True)
            x, y, w, h = cv2.boundingRect(approx)
            cv2.rectangle(imgContour, (x, y), (x + w, y + h), (0, 255, 0), 2)
            
            shape = "Bilinmiyor"
            sides = len(approx)
            if sides == 3:
                shape = "Ucgen"
            elif sides == 4:
                aspectRatio = w / float(h)
                if 0.95 < aspectRatio < 1.05:
                    shape = "Kare"
                else:
                    shape = "Dikdortgen"
            elif sides == 5:
                shape = "Besgen"
            elif sides == 6:
                shape = "Altigen"
            elif sides > 6:
                shape = "Daire"
            
            cv2.putText(imgContour, f"{shape}", (x, y - 10), cv2.FONT_HERSHEY_COMPLEX, 0.7, (0, 255, 0), 2)
            cv2.putText(imgContour, f"Points: {sides}", (x + w + 20, y + 20), cv2.FONT_HERSHEY_COMPLEX, 0.7, (0, 255, 0), 2)
            cv2.putText(imgContour, f"Area: {int(area)}", (x + w + 20, y + 45), cv2.FONT_HERSHEY_COMPLEX, 0.7, (0, 255, 0), 2)

def shape_detection():
    while not stop_threads:
        lock.acquire()
        if shared_frame is not None:
            img = shared_frame.copy()
            lock.release()

            imgContour = img.copy()
            imgBlur = cv2.GaussianBlur(img, (7, 7), 1)
            imgGray = cv2.cvtColor(imgBlur, cv2.COLOR_BGR2GRAY)

            threshold1 = cv2.getTrackbarPos("Threshold1", "Parameters")
            threshold2 = cv2.getTrackbarPos("Threshold2", "Parameters")
            imgCanny = cv2.Canny(imgGray, threshold1, threshold2)
            kernel = np.ones((5, 5))
            imgDil = cv2.dilate(imgCanny, kernel, iterations=1)

            getContours(imgDil, imgContour)

            cv2.imshow("Shape Detection", imgContour)
            cv2.waitKey(1)
        else:
            lock.release()

# --- Çizgi Takibi Fonksiyonları ---
def line_following():
    clahe = cv2.createCLAHE(clipLimit=2.0, tileGridSize=(8, 8))
    while not stop_threads:
        lock.acquire()
        if shared_frame is not None:
            frame = shared_frame.copy()
            lock.release()

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
                        direction = "SOL"
                    elif cx > frame_center + 50:
                        direction = "SAG"
                    else:
                        direction = "DUZ"

                    cv2.putText(frame, f"Yon: {direction}", (50, 50),
                                cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)

            cv2.imshow("Line Following", frame)
            cv2.imshow("Threshold", mask)
            cv2.waitKey(1)
        else:
            lock.release()

# --- Kamera Okuma Thread'i ---
def capture_frames():
    global shared_frame, stop_threads
    while not stop_threads:
        success, frame = cap.read()
        if not success:
            continue
        lock.acquire()
        shared_frame = frame.copy()
        lock.release()

# --- Thread Başlatma ---
capture_thread = threading.Thread(target=capture_frames)
shape_thread = threading.Thread(target=shape_detection)
line_thread = threading.Thread(target=line_following)


capture_thread.start()
shape_thread.start()
line_thread.start()

try:
    while True:
        if cv2.waitKey(1) & 0xFF == 27:  # ESC tuşu
            stop_threads = True
            break
except KeyboardInterrupt:
    pass

# --- Temizlik ---
capture_thread.join()
shape_thread.join()
line_thread.join()

cap.release()
cv2.destroyAllWindows()
