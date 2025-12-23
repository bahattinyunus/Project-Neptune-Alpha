# 🌡️ TERMAL STRES TEST PROTOKOLÜ (STD-THERM-01)

> [!WARNING]
> Sualtı araçlarının kapalı gövdeleri (WTP - Watertight Pressure Enclosure), hava akışı olmadığı için ısı birikimine duyarlıdır.

## 📍 Test Amacı
Raspberry Pi 4 ve motor sürücülerinin, sualtında 60 dakikalık kesintisiz operasyon sırasında kritik sıcaklık eşiklerini (80°C) aşmadığından emin olmak.

## 🛠️ Test Prosedürü
1. **Sistem Hazırlığı:** ROV gövdesi kapatılmadan önce tüm sensörler ve AI modelleri başlatılır.
2. **Yükleme Fazı:**
   - Python scripti ile 1080p video kaydı başlatılır.
   - TensorFlow Lite modeli otonom tarama moduna alınır.
   - 8 motor, %50 güçte 10 saniye çalışıp 5 saniye duracak şekilde döngüye sokulur.
3. **İzleme:** Kontrol panelinden `vcgencmd measure_temp` komutu ile ısı takibi yapılır.

## 🛡️ Güvenlik Eşikleri
| Sıcaklık | Durum | Aksiyon |
| :--- | :--- | :--- |
| **< 60°C** | Normal | Operasyon devam eder. |
| **60°C - 75°C** | Uyarı | AI inference hızı %20 düşürülür. |
| **> 80°C** | Kritik | Sistem otomatik olarak 'Safe Idle' moduna geçer. |

---
*Bu protokol, donanım ömrünü maksimize etmek için tasarlanmıştır.*
