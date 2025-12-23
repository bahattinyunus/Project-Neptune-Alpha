# 🚀 ROV Projesi – Raspberry Pi  Kurulumu


## 🛠️ 1. Arduino IDE Kurulumu (Raspberry Pi)

```bash
sudo apt update && sudo apt upgrade -y
sudo apt install arduino -y
```
## 🗃️ 2. Deneyap Kart Tanımını Ekleme

Arduino IDE > `File > Preferences` menüsüne gidin.

**Additional Board Manager URLs** alanına aşağıdaki linki yapıştırın:

```
https://raw.githubusercontent.com/deneyapkart/deneyapkart-arduino-core/master/package_deneyapkart_index.json
```

---

## 🛋️ 3. Deneyap Kart'ı Kurma

1. Tools > Board > Boards Manager menüsüne girin
2. "Deneyap" aratın
3. "Deneyap Kart" paketini seçin ve **Install** butonuna tıklayın

> Kurulumdan sonra Tools > Board menüsünden kullandığınız kart modelini seçin:
>
> - Deneyap Kart v2
> - Deneyap Mini
> - Deneyap Geliştirme Kartı

---

## 🤜 7. ESP32 + Servo Kurulumu


### ESP32 Kart Kurulumu:

- Tools > Board > Boards Manager > "esp32" ara


### ESP32Servo Kütüphanesi:

- Sketch > Include Library > Manage Libraries...
- "ESP32Servo" arat ve yükle

Bu projenin çalışması için aşağıdaki Python paketlerinin kurulması gerekmektedir:

- picamera2
- opencv-python
- numpy
- pyserial
sudo apt install python3 python3-pip -y

sudo apt install libatlas-base-dev libjpeg-dev libtiff5-dev libjasper-dev libpng-dev -y
sudo apt install libavcodec-dev libavformat-dev libswscale-dev libv4l-dev -y
sudo apt install libxvidcore-dev libx264-dev -y
sudo apt install python3-dev python3-numpy -y
sudo apt install python3-numpy python3-serial python3-opencv

sudo apt install -y python3-picamera2


# - tensorflow
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
.
