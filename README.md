![ROV Elite Banner](./banner.png)

# 🌊 ROV TACTICAL COMMAND CENTER: ALPHA PROTOCOL

```text
[SYSTEM INITIALIZATION]
> Kernel Loading... OK
> Edge AI Models Synchronized... OK
> UART Link Established (Pi <-> Deneyap)... OK
> ROV Status: OPERATIONAL - READY FOR DEPLOYMENT
--------------------------------------------------
ID: ALPHA-01-ROV
CLASS: DEEP-SEA INTELLIGENCE PLATFORM
STATUS: TIER 1 - MISSION READY
```

---

## 🛰️ Sistem Mimarisi (Digital Command Panel)

Aşağıdaki HUD (Heads-Up Display) şeması, platformun otonom karar verme ve sensör füzyon mimarisini temsil eder.

```mermaid
graph TD
    %% Base Nodes
    A["📷 PiCamera2 (Raw Data)"]
    B{"🧠 Edge AI (TensorFlow Lite)"}
    C["🎯 Görev Mantığı (Priority 1)"]
    D["🛣️ Navigasyon Katmanı"]
    E["📡 Karar Mekanizması"]
    F["⚡ UART Communication"]
    G["🕹️ Deneyap Kart (Motor Driver)"]
    H["🔌 Sensör Füzyonu (IMU/Mesafe)"]
    I["🔱 ROV Motor Cluster (8x)"]

    %% Connections
    A --> B
    B -- "Nesne Tespiti" --> C
    B -- "Çizgi Analizi" --> D
    C --> E
    D --> E
    E --> F
    F --> G
    H --> G
    G --> I

    %% Elite Styling
    style A fill:#001a33,stroke:#00ccff,stroke-width:3px,color:#fff
    style B fill:#330000,stroke:#ff3300,stroke-width:4px,color:#fff
    style G fill:#003300,stroke:#00ff00,stroke-width:3px,color:#fff
    style E fill:#333300,stroke:#ffff00,stroke-width:3px,color:#fff
    style I fill:#1a1a1a,stroke:#cccccc,stroke-width:2px,color:#fff
    
    linkStyle 0,1,2,3,4,5,6,7,8 stroke:#00ccff,stroke-width:2px;
```

---

## 🗺️ Operasyonel Doktrinler (Eğitim Serisi)

Bu platform, sadece bir robot değil, sualtında otonom varlık göstermeniz için bir **Mühendislik Kılavuzu**dur.

### 🛠️ [MODÜL 00: STRATEJİK HAZIRLIK](./00_Kurulum_ve_Hazirlik)
> *Sistem temelleri ve izolasyon protokolleri.*

### 🔌 [MODÜL 01: SENSÖR & AKTÜATÖR KATMANI](./01_Temel_Donanim_Kontrol)
> *Gerçek zamanlı düşük gecikmeli donanım kontrolü.*

### 👁️ [MODÜL 02: VİZYONER ZEKA](./02_Goruntu_Isleme_ve_AI)
> *Edge AI ve OpenCV ile sualtı algı sistemleri.*

### 🎯 [MODÜL 03: OTONOM GÖREV SETLERİ](./03_Gorev_Algoritmalari)
> *Arama-tarama ve otonom hedef imha algoritmaları.*

### ⚓ [MODÜL 04: TOTAL ENTEGRASYON](./04_Final_Entegrasyon)
> *Alpha sürüm: Tam otonom final kodları.*

---

## 🛡️ Teknik Spesifikasyonlar

![Tech Badges](https://img.shields.io/badge/Tech-TensorFlow_Lite-orange?style=for-the-badge&logo=tensorflow)
![Tech Badges](https://img.shields.io/badge/Tech-OpenCV-green?style=for-the-badge&logo=opencv)
![Tech Badges](https://img.shields.io/badge/Tech-Raspberry_Pi-red?style=for-the-badge&logo=raspberry-pi)
![Tech Badges](https://img.shields.io/badge/Tech-ESP32_Deneyap-blue?style=for-the-badge)

| Özellik | Detay | Protokol |
| :--- | :--- | :--- |
| **Gecikme** | < 50ms (AI Inference) | TF-Lite |
| **Kontrol** | PID Loop (4-Axis) | Real-time |
| **Enerji** | Fail-Safe Protection | Active |
| **Görüş** | Night-Vision Logic | OpenCV |

---

> [!CAUTION]
> **OPR-STATUS:** Bu repo "Extreme" seviyede teknik içerik barındırır. Dokümantasyonu sırasıyla takip etmemek sistem instabilitesine yol açabilir.

---

[Elite Arşivi](./_ARCHIVE) | [Sistem Logları](./04_Final_Entegrasyon) | [Geliştirici: Bahattin Yunus]
