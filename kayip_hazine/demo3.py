import time
import serial
from math import atan2, degrees, sqrt, cos, radians

# Seri port bağlantısı
ser = serial.Serial("COM8", 115200)
time.sleep(2)

def gps_to_xy(lat0, lon0, lat1, lon1):
    meters_per_deg_lat = 111320
    meters_per_deg_lon = 111320 * cos(radians(lat0))
    delta_lat = lat1 - lat0
    delta_lon = lon1 - lon0
    x = delta_lon * meters_per_deg_lon
    y = delta_lat * meters_per_deg_lat
    return x, y

def compute_distance_and_bearing(x, y):
    distance = sqrt(x**2 + y**2)
    angle = degrees(atan2(y, x))
    if angle < 0:
        angle += 360
    return distance, angle

def send_joystick(x1, y1, x2, y2):
    msg = f"X1:{x1},Y1:{y1},X2:{x2},Y2:{y2}\n"
    ser.write(msg.encode())

def read_data():
    """
    ESP32'den gelen veriyi okur. Format: YAW:xx.x,DIST:xxx,M1:xxxx,M2:xxxx
    """
    if ser.in_waiting:
        line = ser.readline().decode().strip()
        try:
            parts = dict(part.split(":") for part in line.split(","))
            return {
                "yaw": float(parts["YAW"]),
                "dist": int(parts["DIST"]),
                "m1": int(parts["M1"]),
                "m2": int(parts["M2"])
            }
        except:
            return None
    return None

def calculate_pid(error, kp=1.5):
    return int(kp * error)

def execute_navigation(lat0, lon0, lat1, lon1):
    x, y = gps_to_xy(lat0, lon0, lat1, lon1)
    distance, target_yaw = compute_distance_and_bearing(x, y)

    print(f"📍 Mesafe: {distance:.2f} m")
    print(f"🧭 Hedef yönü: {target_yaw:.2f}°")

    speed = 0.2  # m/s
    duration = distance / speed
    print(f"⏳ Süre: {duration:.1f} s")

    start_time = time.time()
    while time.time() - start_time < duration:
        data = read_data()
        if data:
            yaw = data["yaw"]
            dist = data["dist"]

            # Yön hatası hesapla
            yaw_error = target_yaw - yaw
            if yaw_error > 180:
                yaw_error -= 360
            elif yaw_error < -180:
                yaw_error += 360

            pid_output = calculate_pid(yaw_error)
            x1 = 1500 + pid_output  # yön düzeltme
            y2 = 1600               # ileri hareket

            # Engel kontrolü
            if dist < 80:  # örneğin 80 cm'den yakın engel varsa
                print("🚨 Engel algılandı! Duruluyor.")
                send_joystick(1500, 1500, 1500, 1500)
                time.sleep(2)
                continue  # tekrar veri bekle

            # Joystick gönder
            send_joystick(x1, 1500, 1500, y2)

            print(f"🔁 Yön: {yaw:.2f}°, Hata: {yaw_error:.2f}, X1: {x1}, Mesafe: {dist} cm")

        time.sleep(0.1)

    print("🎯 Görev tamamlandı.")
    send_joystick(1500, 1500, 1500, 1500)  # dur

# Örnek kullanım
if __name__ == "__main__":
    lat0, lon0 = 36.123456, 33.123456
    lat1, lon1 = 36.124000, 33.124100
    execute_navigation(lat0, lon0, lat1, lon1)