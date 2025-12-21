# 🚀 Fedora Optimizer - 2025 AI-Powered

![Version](https://img.shields.io/badge/version-2.0-blue)
![Fedora](https://img.shields.io/badge/Fedora-43-blue)
![Python](https://img.shields.io/badge/Python-3.12+-green)
![License](https://img.shields.io/badge/license-MIT-green)

> 🧠 En gelişmiş Fedora sistem optimizasyon aracı - Tek iş, mükemmel yapılmış

## ✨ Özellikler

| Özellik | Açıklama |
|---------|----------|
| 🔍 **Derin Tarama** | Sistem DNA analizi, kernel, bellek, I/O profilleme |
| 🧠 **AI Optimizasyon** | Donanım ve kullanım profiline göre akıllı öneriler |
| 🎮 **Oyun Modu** | GameMode, CPU governor, compositor kontrolü |
| 💾 **I/O Scheduler** | NVMe/SSD/HDD için dinamik scheduler seçimi |
| 🌐 **Ağ Optimizasyonu** | TCP BBR, Fast Open, buffer tuning |
| 🔧 **Kernel Tuning** | 30+ sysctl parametresi |
| ↩️ **Rollback** | Tek tıkla geri alma |

## 📦 Kurulum

```bash
git clone https://github.com/bingoweb/FedoraOptimizer.git
cd fedoraclean
chmod +x setup.sh run.sh
./setup.sh
sudo ./run.sh
```

## 🖥️ Ekran Görüntüsü

```
┌─────────────────────────────────────────────────────────────┐
│ FEDORA OPTİMİZER /// 2025 AI                       19:20:00 │
├──────────────────────┬──────────────────────────────────────┤
│  OPTİMİZASYON MENÜSÜ │  SİSTEM BİLGİSİ         KAYNAK       │
│                      │  ─────────────          ──────       │
│  1  🔍 DERİN TARAMA  │  CPU: Intel i5-1235U    ⚡ CPU: 12%  │
│  2  ⚡ HIZLI OPTİMİZE│  RAM: 16GB DDR4         🧠 RAM: 45%  │
│  3  🚀 TAM OPTİMİZE  │  GPU: Intel Iris Xe     💿 DSK: 60%  │
│  4  🎮 OYUN MODU     │  DISK: NVMe SSD                      │
│  5  💾 I/O SCHEDULER │                                      │
│  6  🌐 AĞ OPTİMİZE   │  EN AKTİF İŞLEMLER      AĞ DURUMU   │
│  7  🔧 KERNEL AYAR   │  ─────────────────      ──────────   │
│  8  ↩️ GERİ AL       │  firefox     2.1%       ↓ 1.2 MB/s  │
│                      │  code        1.5%       ↑ 0.1 MB/s  │
│  0  ❌ ÇIKIŞ         │  konsole     0.8%                    │
└──────────────────────┴──────────────────────────────────────┘
```

## 📊 Desteklenen Optimizasyonlar

### Kernel Parametreleri (sysctl)
| Kategori | Parametreler |
|----------|-------------|
| **Bellek** | vm.swappiness, vm.dirty_ratio, vm.vfs_cache_pressure |
| **Ağ** | tcp_congestion_control=bbr, tcp_fastopen, buffer sizes |
| **I/O** | dirty_expire_centisecs, dirty_writeback_centisecs |
| **Latency** | sched_autogroup, compaction_proactiveness |

### I/O Scheduler Seçimi
| Cihaz Tipi | Gaming | Desktop | Server |
|------------|--------|---------|--------|
| NVMe | `none` | `mq-deadline` | `none` |
| SSD | `mq-deadline` | `bfq` | `mq-deadline` |
| HDD | `bfq` | `bfq` | `bfq` |

## 🛠️ Gereksinimler

- Fedora 40+ (43 önerilir)
- Python 3.12+
- Root yetkisi
- `nvme-cli` (NVMe sağlık kontrolü için)

## 📁 Proje Yapısı

```
fedoraclean/
├── run.sh              # Ana giriş noktası
├── setup.sh            # Sanal ortam kurulumu
├── requirements.txt    # Python bağımlılıkları
├── docs/
│   └── AI_MEMORY.md    # Geliştirici notları
└── src/
    ├── modules/
    │   ├── optimizer.py   # Ana optimizasyon motoru
    │   ├── gaming.py      # Oyun modu
    │   ├── utils.py       # Yardımcı fonksiyonlar
    │   └── logger.py      # Loglama
    └── ui/
        ├── tui_app.py     # Terminal arayüzü
        ├── dashboard.py   # Sistem widget'ları
        └── input_helper.py
```

## 📝 Son Güncellemeler

<!-- AUTO-UPDATED -->
- **2025-12-21** - Proje optimizasyon-odaklı olarak yeniden yapılandırıldı
- **2025-12-21** - 30+ kernel parametresi, I/O scheduler, gaming mode eklendi
- **2025-12-21** - Derin donanım profilleme (NVMe SMART, CPU hibrit çekirdek)

## 🤝 Katkıda Bulunma

1. Fork edin
2. Feature branch oluşturun (`git checkout -b feature/AmazingFeature`)
3. Commit edin (`git commit -m '✨ Add: AmazingFeature'`)
4. Push edin (`git push origin feature/AmazingFeature`)
5. Pull Request açın

## 📜 Lisans

MIT License - Detaylar için [LICENSE](LICENSE) dosyasına bakın.

## 👤 Geliştirici

**Taylan Soylu**
- GitHub: [@bingoweb](https://github.com/bingoweb)
- Email: taylansoylu@gmail.com

---

⭐ Bu projeyi beğendiyseniz yıldız vermeyi unutmayın!
