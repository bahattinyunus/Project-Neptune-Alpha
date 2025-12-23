# 🔌 Modül 01: Temel Donanım Kontrol

Bu modül, ROV'un fiziksel bileşenlerini (motorlar, sensörler) nasıl kontrol edeceğinizi açıklar.

## İçerik ve Kodlar

Bu modülde yer alan temel kodlar şunlardır:

### 🎮 Manuel Kontrol
- `Manuel_Yazilim_esp32_8motor_joystick_kontrol.ino`: 8 motorlu ROV sisteminin joystick ile kontrolü için ESP32 kodu.
- `deneyap_modlar_manuel-joystick-kontrol-robotu-esp32.ino`: Deneyap kartı için alternatif manuel sürüş modları.

### 📏 Sensör Okuma
- `Haberlesme_Deneyap_Kodu_ultrasonik-mesafe-sensoru-okuma`: Ultrasonik sensörden veri alan Deneyap kodu.
- `Haberlesme_Python_Kodu_ultrasonik-mesafe-sensoru-okuma`: Sensör verilerini Python tarafında işleyen kod.

---

## 🛠️ Devre Şeması ve Bağlantılar

*Not: Detaylı bağlantı şemaları yakında eklenecektir.*

1. **Motorlar:** PWM pinleri üzerinden sürücülere bağlanır.
2. **Sensörler:** I2C veya Digital pinler üzerinden Deneyap Kart'a bağlanır.

---

[⬅️ Ana Sayfaya Dön](file:///c:/github%20repolar%C4%B1m/rov/README.md)
