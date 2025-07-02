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

HABERLEŞME:
  Deneyap Karttan Pythona veri aktarma, Deneyap kartın seri portu üzerinden yapılır. 
  Örnek çalışmada mesafe sensöründen (ilerde sonar olacak inşallah) gelen veri seri porta yazdırılır. 
  Pythonda deneyap kart, port ve haberleşme hızı bilgileriyle birlikte tamınlanır: deneyap=serial.Serial("COM3",9600) 
  veri=deneyap.readline() ve print(veri) kodlarıyla deneyapın seri portundaki veriler okunup pythona aktarılmış olur.
  Eğer pythondan deneyapa veri göndermek istersek de arduino.write((deger + '\n').encode()) kodunu kullanıyoruz.
  Eğer gelen verinin boş olup olmadığını kontrol etmek istersek if (new_data.length() > 0) sorgulaması yapıyoruz.

PYTHONDAN DENEYAPA VERİ GÖNDERİMİ ÖRNEK KOD - DENEYAP TARAFI:
(Python terminalinden uyandır yazınca D12'ye bağlı led yanar, dinlendir dediğimizde söner)

String received_data = "";  // Gelen veriyi tutmak için değişken
#define yesil D12
void setup() {
  Serial.begin(9600);  // Seri haberleşmeyi başlat
  Serial.println("Hazir");
  pinMode(yesil,  OUTPUT);
  digitalWrite(yesil,  LOW);
}

void loop() {
  // Seri porttan gelen veriyi kontrol et
  if (Serial.available() > 0) {
    // Gelen veriyi oku ve '\n' karakterine kadar bekle    
    String new_data = Serial.readStringUntil('\n')
    if (new_data == "uyandır") {
      digitalWrite(yesil,  HIGH);
    }
    if (new_data == "dinlendir") {
      digitalWrite(yesil,  LOW);
    }
  }
}


PYTHONDAN DENEYAPA VERİ GÖNDERİMİ ÖRNEK KOD - PYTHON TARAFI:

import serial
import time
arduino = serial.Serial('COM3', 9600)  # Port numarasını sistemine göre ayarla
time.sleep(2)  # Bağlantı kurulmasını bekle
while True:
    deger=input("Ledin istikbali nedir? ")
    arduino.write((deger + '\n').encode())  # Arduino'ya veri gonder
    print(f"Veri gönderildi: {deger}")  # Konsola yaz

