# 🧠 EDGE AI OPTİMİZASYON DOKTRİNİ

> [!TIP]
> Raspberry Pi üzerinde yüksek FPS ile otonom sürüş yapabilmek için 'Inference Time' (Tahmin Süresi) hayati önem taşır.

## 🚀 Optimizasyon Teknikleri

### 1. Model Quantization (Nicemleme)
`float32` yerine `int8` veya `float16` modeller kullanarak CPU yükünü %50'ye kadar azaltın.
- **Araç:** `TFLite Converter`
- **Etki:** Daha düşük RAM kullanımı ve daha hızlı tahmin.

### 2. Multi-Threading (İş Parçacığı Yönetimi)
Görüntü alma (Picamera2) ve Tahmin etme (TF Lite) işlemleri farklı çekirdeklerde çalıştırılmalıdır.
- **Mevcut Yapı:** `tensorlu_picamera_finish.py` içerisindeki threading yapısı.

### 3. ROI (Region of Interest) Kırpma
Tüm kareyi 640x480 olarak modele göndermek yerine, sadece alt kısımdaki (çizgi/nesne olan) 64x64 bölgeyi modele göndermek hızı artırır.

## ⚙️ Performans Metrikleri (Target)
| Cihaz | Model Tipi | Hedef FPS |
| :--- | :--- | :--- |
| **RPi 4 (4GB)** | TF-Lite Float32 | 10-15 FPS |
| **RPi 4 (4GB)** | TF-Lite Int8 | 25-30 FPS |

---
*Yazılımda verimlilik, donanımda güçten daha değerlidir.*
