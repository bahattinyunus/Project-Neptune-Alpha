from math import cos, radians, atan2, degrees, sqrt

def gps_to_xy(lat0, lon0, lat1, lon1):
    
    meters_per_deg_lat = 111320
    meters_per_deg_lon = 111320 * cos(radians(lat0))

    delta_lat = lat1 - lat0
    delta_lon = lon1 - lon0

    x = delta_lon * meters_per_deg_lon  # doğu-batı
    y = delta_lat * meters_per_deg_lat  # kuzey-güney

    return (0, 0), (x, y)

def compute_distance_and_bearing(x, y):
    
    distance = sqrt(x**2 + y**2)
    angle_rad = atan2(y, x)
    angle_deg = degrees(angle_rad)
    if angle_deg < 0:
        angle_deg += 360  # 0-360 aralığına al
    return distance, angle_deg

# Örnek GPS koordinatları
lat0, lon0 = 36.123456, 33.123456  # Başlangıç
lat1, lon1 = 36.124000, 33.124100  # Hedef

# Hesapla
start_xy, target_xy = gps_to_xy(lat0, lon0, lat1, lon1)
x_target, y_target = target_xy
distance, bearing = compute_distance_and_bearing(x_target, y_target)

# Ekrana yazdır
print(" Başlangıç GPS:", lat0, lon0)
print(" Hedef GPS:    ", lat1, lon1)
print(" Başlangıç XY: ", start_xy)
print(" Hedef XY:     ", target_xy)
print(f" Mesafe:       {distance:.2f} metre")
print(f" Yön açısı:     {bearing:.2f} derece")
