import time
import serial
from math import atan2, degrees, sqrt, cos, radians

# Seri port ayarı
ser = serial.Serial("COM8", 115200)
time.sleep(2)

# GPS'ten XY hesapla
def gps_to_xy(lat0, lon0, lat1, lon1):
    meters_per_deg_lat = 111320
    meters_per_deg_lon = 111320 * cos(radians(lat0))

    delta_lat = lat1 - lat0
    delta_lon = lon1 - lon0

    x = delta_lon * meters_per_deg_lon
    y = delta_lat * meters_per_deg_lat

    return x, y

# Hedef yön ve mesafe
def compute_distance_and_bearing(x, y):
    distance = sqrt(x**2 + y**2)
    angle = degrees(atan2(y, x))
    if angle < 0:
        angle += 360
    return distance, angle

# ESP32’ye joystick komutu gönder
def send_joystick(x1, y1, x2, y2):
    msg = f"X1:{x1},Y1:{y1},X2:{x2},Y2:{y2}\n"
    ser.write(msg.encode())

# 🔧 PID yön düzeltme (örnek amaçlı)
def calculate_pid(error, kp=2.0):
    return int(kp * error)

# Ana görev fonksiyonu
def execute_navigation(lat0, lon0, lat1, lon1, current_yaw):
    x, y = gps_to_xy(lat0, lon0, lat1, lon1)
    distance, target_yaw = compute_distance_and_bearing(x, y)

    print(f"→ Hedefe mesafe: {distance:.2f} m")
    print(f"→ Hedef yönü: {target_yaw:.2f}°, Şu anki yön: {current_yaw:.2f}°")

    # Fark açısını hesapla ve rotaya dön
    yaw_error = target_yaw - current_yaw
    if yaw_error > 180:
        yaw_error -= 360
    elif yaw_error < -180:
        yaw_error += 360

    pid_output = calculate_pid(yaw_error)

    # Yön düzelt: X1 döndürme komutu (örnek olarak)
    if abs(yaw_error) > 5:
        x1 = 1500 + pid_output
        print(f"↺ Yön düzeltme: {x1}")
        for _ in range(30):
            send_joystick(x1, 1500, 1500, 1500)
            time.sleep(0.1)
    else:
        print("Yön zaten doğru.")

    # İleri hareket süresi hesapla (örnek hız: 0.2 m/s)
    speed = 0.2
    duration = distance / speed
    print(f"İleri gidilecek süre: {duration:.1f} saniye")

    # Sabit ileri komut
    for _ in range(int(duration * 10)):
        send_joystick(1500, 1500, 1500, 1600)
        time.sleep(0.1)

    print("🎯 Görev tamamlandı.")

# 🔵 Örnek kullanım
if __name__ == "__main__":
    lat0, lon0 = 36.123456, 33.123456
    lat1, lon1 = 36.124000, 33.124100

    current_yaw = 10.0  # buraya IMU’dan gelen gerçek yönü entegre et
    execute_navigation(lat0, lon0, lat1, lon1, current_yaw)