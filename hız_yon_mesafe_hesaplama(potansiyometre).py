import serial
import time
import math

# === GPS Koordinatları ===
lat0, lon0 = 40.123456, 29.123456  # Başlangıç koordinatları
lat1, lon1 = 40.123860, 29.124460  # Hedef koordinatları

# Dünya yarıçapı (WGS84)
R = 6378137

# === GPS'ten lokal yön ve mesafe hesaplama ===
def gps_to_local(lat0, lon0, lat1, lon1):
    lat0 = math.radians(lat0)
    lat1 = math.radians(lat1)
    lon0 = math.radians(lon0)
    lon1 = math.radians(lon1)

    dlat = lat1 - lat0
    dlon = lon1 - lon0

    dx = dlon * math.cos((lat0 + lat1) / 2) * R
    dy = dlat * R

    angle_rad = math.atan2(dy, dx)
    angle_deg = (math.degrees(angle_rad) + 360) % 360
    distance = math.sqrt(dx**2 + dy**2)

    return angle_deg, distance

# === Seri Port Ayarları ===
ser = serial.Serial('COM9', 9600, timeout=1)
time.sleep(2)
print("Bağlantı kuruldu. Veriler bekleniyor...")

# === Veri Parslama ===
def read_values():
    try:
        line = ser.readline().decode('utf-8', errors='ignore').strip()
        if line.startswith("HIZ:") and "YON:" in line:
            parts = line.split()
            hiz = int(parts[0].split(":")[1])
            yon_raw = int(parts[1].split(":")[1])
            # Yönü 0–1023'ten 0–360°'ye dönüştür
            yon = (yon_raw / 1023) * 360
            return hiz, yon
    except Exception as e:
        print(f"Veri okuma hatası: {e}")
    return None, None

# === Yön ve mesafe hesaplama ===
hedef_yon, hedef_mesafe = gps_to_local(lat0, lon0, lat1, lon1)
print(f"🎯 Hedef yönü: {hedef_yon:.2f}°, Toplam mesafe: {hedef_mesafe:.2f} m")

# === Yön eşleşmesini bekle ===
tolerans = 5  # ±5° tolerans
print("🔄 Hedef yöne dönülmesi bekleniyor...")
while True:
    hiz, yon = read_values()
    if yon is not None:
        fark = abs(yon - hedef_yon)
        fark = min(fark, 360 - fark)  # 360 derecelik dairesel fark
        print(f"Şu anki yön: {yon:.2f}° | Hedef: {hedef_yon:.2f}° | Fark: {fark:.2f}°")
        if fark <= tolerans:
            print("✅ Hedef yöne ulaşıldı. Hareket başlıyor...")
            break
    time.sleep(0.1)

# === Hareket Başlıyor ===
distance_covered = 0.0
step_time = 0.1  # saniye

while distance_covered < hedef_mesafe:
    hiz, yon = read_values()
    if hiz is None or yon is None:
        continue

    # Yön kontrolü (tolerans dışında ise dur)
    fark = abs(yon - hedef_yon)
    fark = min(fark, 360 - fark)
    if fark > tolerans:
        print("⛔ Yön sapması tespit edildi. Düzeltme bekleniyor...")
        continue

    # Hız birimi: potansiyometre değeri (örnek: 0–1023)
    hiz_m_s = hiz / 100.0  # Örnek dönüşüm: 400 -> 4.0 m/s
    adim_mesafe = hiz_m_s * step_time
    distance_covered += adim_mesafe

    print(f"Hız: {hiz_m_s:.2f} m/s | Kat edilen mesafe: {distance_covered:.2f}/{hedef_mesafe:.2f} m")
    time.sleep(step_time)

print(" -------- Hedefe ulaşıldı! ---------")
ser.close()
