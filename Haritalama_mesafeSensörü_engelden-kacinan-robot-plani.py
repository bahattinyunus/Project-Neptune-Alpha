import serial, time, math

# --- Seri porttan mesafe okuma ---
def read_distance(ser):
    line = ser.readline().decode('utf-8', errors='ignore').strip()
    if line.startswith("Mesafe:"):
        try:
            val = float(line.replace("Mesafe:", "").replace("cm","").strip())
            return val
        except:
            return None
    return None

# --- Motor komutları (Arduino'ya gönder) ---
def send_cmd(ser, cmd):
    ser.write(cmd.encode())

# --- Global plan ---
plan = [('F', 2.0), ('L', 30.0), ('F', 5.0)]
current_step = 0
distance_covered = 0.0

# Engel eşiği (cm)
OBSTACLE_THRESHOLD = 20.0

# Seri bağlantı
ser = serial.Serial('COM8', 9600, timeout=1)
time.sleep(2)

print("Başlıyor…")

# Local bug modunda mıyız?
in_bug_mode = False
bug_turn_direction = None  # 'L' veya 'R'

while current_step < len(plan):
    typ, val = plan[current_step]
    
    # 1) Engel kontrolü
    dist = read_distance(ser)
    if dist and dist < OBSTACLE_THRESHOLD:
        if not in_bug_mode:
            # Engel algılandı → bug moduna gir
            in_bug_mode = True
            # Engel kenarını takip etmek için ters yönde dön
            bug_turn_direction = 'R' if typ=='F' else None
            print("Engel! Bug-mod: kenar takip", bug_turn_direction)
        # Bug-mod: küçük dönüş + ileri
        send_cmd(ser, bug_turn_direction or 'R')
        time.sleep(0.5)
        send_cmd(ser, 'F')
        time.sleep(0.5)
        continue
    
    # 2) Eğer bug-modda isek ve engelden temizlendiysek → çık
    if in_bug_mode and dist and dist > OBSTACLE_THRESHOLD*2:
        in_bug_mode = False
        print("Engel aşıldı, global plana dönülüyor.")
    
    # 3) Global komutu uygula
    if typ == 'F':
        # mesafe adımı (örneğin 0.1 m)
        step = 0.1
        send_cmd(ser, 'F')
        time.sleep(step)  
        distance_covered += step
        # bu komutu tamamladıysak
        if distance_covered >= val:
            current_step += 1
            distance_covered = 0.0
            print(f"Adım tamam: {val} m ilerledik.")
    elif typ in ('L','R'):
        # dönüş komutu: her döngüde küçük açı adımı
        angle_step = 5.0  # derece
        send_cmd(ser, typ)
        time.sleep(0.2)
        val -= angle_step
        print(f"{typ} {angle_step}°: kalan {val:.1f}°")
        if val <= 0:
            current_step += 1

# Döngü bitince dur
send_cmd(ser, 'S')
print("Plan tamamlandı, hedefe ulaşıldı.")
ser.close()
