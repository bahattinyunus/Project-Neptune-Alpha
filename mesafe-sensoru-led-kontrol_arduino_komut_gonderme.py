import serial
import time
import threading

# Arduino'ya bağlan
arduino = serial.Serial('/dev/ttyUSB0', 9600)
time.sleep(2)  # Arduino'nun resetlenmesini bekle

def seri_veri_okuma():
    while True:
        try:
            veri = arduino.readline().decode('utf-8').strip()
            if veri:
                print(f"[Arduino] {veri}")
        except:
            print("Veri okuma hatası!")
            break

# Seri veriyi ayrı bir iş parçacığında okuyalım
okuma_thread = threading.Thread(target=seri_veri_okuma)
okuma_thread.daemon = True
okuma_thread.start()

# Kullanıcıdan komut alalım
while True:
    komut = input("Komut gönder (uyandir / dinlendir / cik): ").strip().lower()
    if komut in ["uyandir", "dinlendir"]:
        arduino.write((komut + '\n').encode())
        print(f"[Python] Gönderildi: {komut}")
    elif komut == "cik":
        print("Program sonlandırılıyor.")
        break
    else:
        print("Geçersiz komut.")
