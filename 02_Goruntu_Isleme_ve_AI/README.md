# 👁️ Modül 02: Görüntü İşleme ve AI

Bu modül, Raspberry Pi kamerasını kullanarak ROV'un çevresini algılamasını sağlayan algoritmaları içerir. 

## 🧠 Temel Kavramlar

ROV sistemimizde iki ana görüntü işleme yöntemi kullanılmaktadır:
1. **OpenCV:** Geleneksel görüntü işleme (Renk takibi, Şekil algılama, Kenar belirleme).
2. **TensorFlow Lite:** Yapay zeka tabanlı nesne tespiti (Şekil sınıflandırma).

## 📂 İçerik ve Önemli Dosyalar

- `shape_model_final1.h5`: Eğitilmiş TensorFlow modeli (Şekilleri tanımak için).
- `cizgi_takip_ve_manuelsurus_rpi.py`: Hem manuel sürüş hem de otonom çizgi takibi sağlayan ana script.
- `tekthreadlikod_opencv_tensorflow_sekil_tanima_cizgi_takip.py`: Tek bir iş parçacığında çalışan entegre AI kodu.
- `Threadlikod_paralel_sekil_tanima_ve_cizgi_takip.py`: Performans optimizasyonu için paralel işleme kullanan kod (Önerilen).

---

## 🚀 Çalıştırma

Kodları çalıştırmadan önce `Modül 00` içerisindeki Python sanal ortamının aktif olduğundan ve gerekli kütüphanelerin (opencv, tensorflow, numpy) kurulu olduğundan emin olun.

```bash
# Örnek çalıştırma
python Threadlikod_paralel_sekil_tanima_ve_cizgi_takip.py
```

---

[⬅️ Ana Sayfaya Dön](file:///c:/github%20repolar%C4%B1m/rov/README.md)
