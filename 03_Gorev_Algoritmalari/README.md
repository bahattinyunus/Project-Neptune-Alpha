# 🎯 OTONOM GÖREV PROTOKOLLERİ

> [!WARNING]
> Bu modül, yüksek riskli operasyonel görevleri (Arama-Kurtarma, Tespit) icra eden algoritma setlerini barındırır.

## 🏆 Görev Akış Diyagramı

```mermaid
graph LR
    A["🏁 Görev Başlat"] --> B["🔎 Alan Tarama"]
    B --> C{"💎 Hedef Tespit?"}
    C -- "Hayır" --> B
    C -- "Evet" --> D["📍 Konum Sabitleme (PID)"]
    D --> E["📸 Veri Kaydı / Operasyon"]
    E --> F["⚓ Üsse Dönüş"]
```

---

[⬅️ Komuta Merkezine Dön](file:///c:/github%20repolar%C4%B1m/rov/README.md)
