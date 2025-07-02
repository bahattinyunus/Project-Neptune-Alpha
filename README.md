# Raspberry Pi Üzerinde TensorFlow Sanal Ortam Kullanımı 🚀🐍

Selam!  
Bu dosya, Raspberry Pi’nda TensorFlow projeni nasıl *güvenli* ve *derli toplu* bir şekilde çalıştırabileceğini anlatıyor. Özetle, Python paketlerini sistemden bağımsız, kafanı karıştırmadan yönetmek için “sanala ortam” kurup açıp kapatmayı öğreneceksin.

---

## Neden Sanal Ortam? 🤔

E hadi, şu soruyu mutlaka sordun:  
**“Abi neden direkt `pip install tensorflow` demiyorum da sanal ortamla uğraşıyorum?”**  
Cevap:  
Sistem Python’unu direkt bozmak **çok tehlikeli** olabilir. Paket sürümleri çatışabilir, projeler birbirine bulaşabilir, Linux güncellemeleri ile çatışmalar yaşanabilir vs vs.  
Sanal ortam tam da bu karmaşayı önlemek için var.  
Her proje kendi kafasına göre bağımlılıklarını tutar, sistemdeki başka projelere zarar vermez.  
“Projenin kopyası gibi” düşünebilirsin.

---

## Başlamadan Önce ⚠️

- Python 3.11 Raspberry Pi’nda yüklü olmalı (ve sen zaten bunu kontrol ettin, süper!)  
- Terminal (SSH veya doğrudan Pi ekranı) kullanabiliyor olmalısın  
- VS Code kurulu ve çalışır durumda olmalı

---

## 1. Proje Klasörüne Git veya Oluştur

Terminalde şöyle yap:

```bash
mkdir -p ~/rov-project
cd ~/rov-project

SANAL ORTAM OLUŞTUR
python3 -m venv rov-venv


SANAL ORTAMI AKTİF ET
source rov-venv/bin/activate


pip install --upgrade pip setuptools wheel
pip install tensorflow



SANAL ORTAMDAN ÇIK
deactivate




# Proje Adı: Kamera ve ESP32 Kontrollü Şekil Tanıma ve Çizgi Takip Robotu

## Gereksinimler

Bu projenin çalışması için aşağıdaki Python paketlerinin kurulması gerekmektedir:

- picamera2
- opencv-python
- numpy
- pyserial
- tensorflow

## Kurulum

1. Sanal ortam oluşturun (opsiyonel ama tavsiye edilir):

```bash
python3 -m venv venv
source venv/bin/activate     # Linux/Mac
venv\Scripts\activate        # Windows

2. gerekli paketler
pip install picamera2 opencv-python numpy pyserial tensorflow
