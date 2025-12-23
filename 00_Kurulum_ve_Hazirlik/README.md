# 🛠️ Modül 00: Kurulum ve Hazırlık

Bu modül, ROV projesinin yazılımsal temelini atmak için gerekli olan tüm kurulum adımlarını içerir.

## 1. Sistem Güncelleme ve Temel Araçlar

Raspberry Pi terminaline aşağıdaki komutu yazarak sisteminizi güncelleyin:

```bash
sudo apt update && sudo apt upgrade -y
```

## 2. Arduino IDE ve Deneyap Kart Kurulumu

Deneyap Kartı motor sürücü olarak kullanabilmek için Arduino IDE kurulumu gereklidir.

```bash
sudo apt install arduino -y
```

### Deneyap Kart Tanımını Ekleme:
1. Arduino IDE > `File > Preferences` menüsüne gidin.
2. **Additional Board Manager URLs** alanına şunu ekleyin:
   `https://raw.githubusercontent.com/deneyapkart/deneyapkart-arduino-core/master/package_deneyapkart_index.json`
3. `Tools > Board > Boards Manager` menüsünden **Deneyap** aratın ve yükleyin.

## 3. Python Sanal Ortam (venv) Yapılandırması

Görüntü işleme ve TensorFlow kütüphanelerinin sistem geneline zarar vermemesi için sanal ortam kullanılması önerilir.

```bash
# Proje dizinine gidin
mkdir -p ~/rov-project && cd ~/rov-project

# Sanal ortam oluşturun
python3 -m venv rov-venv

# Aktif edin
source rov-venv/bin/activate

# Gerekli paketleri kurun
pip install --upgrade pip setuptools wheel
pip install opencv-python numpy pyserial tensorflow
```

---

> [!IMPORTANT]
> Projenin devamında kameranın aktif olması için `sudo raspi-config` menüsünden **Interface Options > Legacy Camera** seçeneğinin etkin olduğundan emin olun (kullandığınız Pi modeline göre değişebilir).

---

[⬅️ Ana Sayfaya Dön](file:///c:/github%20repolar%C4%B1m/rov/README.md)
