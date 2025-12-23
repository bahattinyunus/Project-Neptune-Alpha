# 🌊 ROV TACTICAL COMMAND CENTER

> [!IMPORTANT]
> **Sistem Durumu:** ALPHA TEMSİLİYETİ - TÜM SİSTEMLER OPERASYONEL
> **Sınıflandırma:** Üst Düzey Sualtı Robotik ve Yapay Zeka Entegrasyon Platformu

---

## 🛰️ Sistem Mimarisi (Digital Command Panel)

Aşağıdaki şema, Raspberry Pi ve Deneyap Kart arasındaki stratejik veri akışını ve otonom karar verme mekanizmasını temsil eder.

```mermaid
graph TD
    A["📷 PiCamera2 (Raw Data)"] --> B{"🧠 Edge AI (TensorFlow Lite)"}
    B -- "Şekil Tespit Edildi" --> C["🎯 Görev Mantığı (Priority 1)"]
    B -- "Çizgi Takibi" --> D["🛣️ Navigasyon Katmanı"]
    
    C --> E["📡 Karar Mekanizması"]
    D --> E
    
    E --> F["⚡ UART Communication"]
    F --> G["🕹️ Deneyap Kart (Motor Driver)"]
    
    H["🔌 Sensör Füzyonu (IMU/Mesafe)"] --> G
    G --> I["🔱 ROV Motor Cluster (8x)"]
    
    style A fill:#003366,stroke:#00ccff,stroke-width:2px,color:#fff
    style B fill:#660000,stroke:#ff3300,stroke-width:2px,color:#fff
    style G fill:#004d00,stroke:#00ff00,stroke-width:2px,color:#fff
    style E fill:#4d4d00,stroke:#ffff00,stroke-width:2px,color:#000
```

---

## 🗺️ Operasyonel Modüller

Bu platform, sualtı görevlerini en zorlu koşullarda dahi başarıyla icra etmek üzere modüler bir doktrin üzerine inşa edilmiştir.

### 🛠️ [MODÜL 00: STRATEJİK HAZIRLIK](file:///c:/github%20repolar%C4%B1m/rov/00_Kurulum_ve_Hazirlik)
*Sistem kurulumu, çevre değişkenleri ve venv izolasyon protokolleri.*

### 🔌 [MODÜL 01: AKTÜATÖR VE SENSÖR KATMANI](file:///c:/github%20repolar%C4%B1m/rov/01_Temel_Donanim_Kontrol)
*Düşük gecikmeli motor kontrolü ve gerçek zamanlı telemetri verileri.*

### 👁️ [MODÜL 02: VIZYONER ZEKA (EDGE AI)](file:///c:/github%20repolar%C4%B1m/rov/02_Goruntu_Isleme_ve_AI)
*OpenCV ve TensorFlow ile sualtında yüksek başarımlı nesne tespiti.*

### 🎯 [MODÜL 03: OTONOM GÖREV PROTOKOLLERİ](file:///c:/github%20repolar%C4%B1m/rov/03_Gorev_Algoritmalari)
*Karmaşık senaryolar için otonom sürüş ve hedef odaklı algoritmalar.*

### ⚓ [MODÜL 04: TOTAL ENTEGRASYON](file:///c:/github%20repolar%C4%B1m/rov/04_Final_Entegrasyon)
*Tüm sistemlerin tek bir 'Master Loop' altında toplandığı final sürümü.*

---

## 🛡️ Teknik Protokoller ve Standartlar

| Protokol | Standart | Durum |
| :--- | :--- | :--- |
| **Görüntü İşleme** | OpenCV 4.x / TF Lite | Optimize Edildi |
| **Haberleşme** | UART / I2C | High-Speed |
| **Kontrol** | PID Stabilization | Aktif |
| **Dayanıklılık** | MIL-STD-810G (Teorik) | Planlanıyor |

---

> [!CAUTION]
> **Uyan:** Sualtı operasyonlarında sızdırmazlık testi yapılmadan donanım enerjilendirilmemelidir. 'Fail-Safe' kod bloklarının çalıştığından emin olun.

---

[Elite Geliştirici Kılavuzu](file:///c:/github%20repolar%C4%B1m/rov/_ARCHIVE) | [Hata Bildirimi](#) | [Sürüm: v2.0-Elite]
