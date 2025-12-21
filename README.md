<p align="center">
  <img src="https://img.shields.io/badge/Fedora-43+-blue?style=for-the-badge&logo=fedora&logoColor=white" alt="Fedora"/>
  <img src="https://img.shields.io/badge/Python-3.12+-green?style=for-the-badge&logo=python&logoColor=white" alt="Python"/>
  <img src="https://img.shields.io/badge/License-MIT-yellow?style=for-the-badge" alt="License"/>
  <img src="https://img.shields.io/badge/AI-Powered-purple?style=for-the-badge&logo=openai&logoColor=white" alt="AI"/>
</p>

<h1 align="center">🚀 Fedora Optimizer 2025</h1>

<p align="center">
  <strong>AI-Powered System Optimization for Fedora Linux</strong><br>
  <em>Deep Analysis • Smart Recommendations • One-Click Rollback</em>
</p>

<p align="center">
  <a href="#features">Features</a> •
  <a href="#installation">Installation</a> •
  <a href="#usage">Usage</a> •
  <a href="#cli-interface">CLI Interface</a> •
  <a href="#architecture">Architecture</a>
</p>

---

## ✨ Features

### 🧠 AI-Driven Optimization
Every optimization follows our **SCAN → ANALYZE → EXPLAIN → CONFIRM → APPLY** workflow:

```
┌─────────────────────────────────────────────────────────────────┐
│  🧠 AI OPTİMİZASYON ÖNERİLERİ                                   │
├─────────────────────────────────────────────────────────────────┤
│  🧠 Bellek                                                      │
│  ┌──────────────────┬────────┬──────────┬───────────────┐       │
│  │ Parametre        │ Mevcut │ Önerilen │ Öncelik       │       │
│  ├──────────────────┼────────┼──────────┼───────────────┤       │
│  │ vm.swappiness    │ 60     │ 5        │ 🟡 Önerilen   │       │
│  │ vm.dirty_ratio   │ 20     │ 5        │ 🟡 Önerilen   │       │
│  └──────────────────┴────────┴──────────┴───────────────┘       │
│    → NVMe SSD tespit edildi. Düşük swappiness disk yerine       │
│      RAM kullanımını önceliklendirir.                           │
│                                                                 │
│  Bu değişiklikleri uygulamak istiyor musunuz? [E/H]:            │
└─────────────────────────────────────────────────────────────────┘
```

### 🔍 Deep System Analysis
- **CPU Detection**: Intel (Hybrid/Legacy), AMD (Zen/Pre-Zen), ARM, VM
- **Disk Detection**: NVMe, SATA SSD, HDD, eMMC
- **Kernel Features**: sched_ext, BORE, BBRv3, PREEMPT_RT, io_uring
- **Form Factor**: Laptop, Desktop, Server auto-detection

### ↩️ Transaction-Based Rollback
```
┌─────────────────────────────────────────┐
│  ↩️ GERİ AL MERKEZİ                     │
├─────────────────────────────────────────┤
│  1. SON İŞLEMİ GERİ AL                  │
│     └─ Quick Optimize (5 dk önce)       │
│                                         │
│  2. İŞLEM GEÇMİŞİ                       │
│     └─ Tüm işlemleri gör                │
│                                         │
│  3. VARSAYILANLARA DÖN                  │
│     └─ Tüm optimizasyonları sıfırla     │
└─────────────────────────────────────────┘
```

---

## 📦 Installation

```bash
# Clone repository
git clone https://github.com/bingoweb/FedoraOptimizer.git
cd FedoraOptimizer

# Install dependencies
./setup.sh

# Run with root privileges
sudo ./run.sh
```

### Requirements
- Fedora 40+ (tested on Fedora 43)
- Python 3.12+
- Root privileges


## ⚠️ Compatibility & Limitations

### Supported Systems
- **OS**: Fedora Workstation 40, 41, 42, 43 (Rawhide)
- **Desktop Environments**: GNOME 45+, KDE Plasma 6+
- **Architecture**: x86_64, aarch64 (ARM)

### Known Limitations
- **Immutable Variants (Silverblue/Kinoite)**: Fully supported, but some persistence methods differ due to read-only root.
- **Virtual Machines**: Deep hardware optimization is limited (CPUs often passed as "Common KVM processor").
- **NVIDIA Proprietary**: Some advanced power management features may be overridden by the driver.
- **Root Requirement**: This tool modifies system configurations and requires `sudo`.

---

## 🎯 Usage

### Main Menu
```
┌──────────────────────────────────────────────────────────────────────┐
│  FEDORA OPTİMİZER 2025 AI                                            │
├──────────────────────────────────────────────────────────────────────┤
│                                                                      │
│  ┌─ OPTİMİZASYON MENÜSÜ ─┐  ┌─ SİSTEM BİLGİSİ ───────────────────┐  │
│  │                       │  │                                     │  │
│  │  1  🔍 DERİN TARAMA   │  │  CPU: Intel i5-1235U (4P+8E)       │  │
│  │  2  ⚡ HIZLI OPTİMİZE │  │  RAM: 16.0 GB DDR4                 │  │
│  │  3  🚀 TAM AUTO       │  │  GPU: Intel Iris Xe                │  │
│  │  4  🎮 OYUN MODU      │  │  DISK: NVMe SSD                    │  │
│  │  5  💾 I/O SCHEDULER  │  │  KERNEL: 6.12.5                    │  │
│  │  6  🌐 AĞ OPTİMİZE    │  │                                     │  │
│  │  7  🔧 KERNEL AYAR    │  │  ✓ BBR aktif                       │  │
│  │  8  ↩️ GERİ AL        │  │  ✓ ZRAM aktif                      │  │
│  │  0  ❌ ÇIKIŞ          │  │  ✓ TRIM aktif                      │  │
│  │                       │  │                                     │  │
│  └───────────────────────┘  └─────────────────────────────────────┘  │
│                                                                      │
│  KOMUT: 1-9 Seçenekler - 0 Çıkış                                    │
└──────────────────────────────────────────────────────────────────────┘
```

### Optimization Options

| Key | Option | Description |
|-----|--------|-------------|
| 1 | 🔍 Deep Scan | Full system DNA analysis with scoring |
| 2 | ⚡ Quick Optimize | AI-driven quick optimization with proposals |
| 3 | 🚀 Full Auto | Complete automatic optimization |
| 4 | 🎮 Gaming Mode | GameMode, compositor disable, CPU governor |
| 5 | 💾 I/O Scheduler | NVMe/SSD/HDD optimal scheduler |
| 6 | 🌐 Network | TCP BBR, Fast Open, buffer tuning |
| 7 | 🔧 Kernel | sysctl parameter optimization |
| 8 | ↩️ Rollback | Undo changes with transaction history |

---

## 🖥️ CLI Interface

### System DNA Report
```
┌────────────────────────────────────────┐
│ 🧬 SİSTEM DNA RAPORU                   │
├────────────────────────────────────────┤
│ CPU: Intel i5-1235U (4P+8E Hibrit)     │
│  └─ Governor: powersave ✓              │
│  └─ Scaling: intel_pstate             │
│  └─ EPP: balance_performance          │
│                                        │
│ RAM: 16GB DDR4-3200                    │
│  └─ ZRAM: Aktif (8GB, lz4) ✓           │
│  └─ Swappiness: 5 ✓                    │
│                                        │
│ DISK: NVMe Samsung 980 PRO             │
│  └─ Scheduler: none ✓                  │
│  └─ TRIM: Aktif ✓                      │
│  └─ Sağlık: %2 aşınma, 42°C            │
│                                        │
│ NETWORK: TCP BBR ✓                     │
│  └─ Fast Open: Aktif ✓                 │
├────────────────────────────────────────┤
│ SKOR: 87/100 🟢                        │
└────────────────────────────────────────┘
```

### Gaming Mode
```
┌────────────────────────────────────────┐
│ 🎮 OYUN MODU                           │
├────────────────────────────────────────┤
│  1. Oyun Modunu Etkinleştir            │
│  2. CPU Performance Governor           │
│  3. Compositor Kapat (KDE)             │
│  4. Gaming Sysctl Parametreleri        │
│  5. Tüm Gaming Optimizasyonları        │
│  0. Geri                               │
└────────────────────────────────────────┘
```

---

## 🏗️ Architecture

```
fedoraclean/
├── src/
│   ├── modules/
│   │   ├── optimizer.py      # Core optimization engine
│   │   │   ├── HardwareDetector      # Universal hardware detection
│   │   │   ├── AIOptimizationEngine  # AI-driven proposals
│   │   │   ├── TransactionManager    # Rollback system
│   │   │   ├── SysctlOptimizer       # Kernel parameters
│   │   │   └── IOSchedulerOptimizer  # Disk scheduler
│   │   ├── gaming.py         # Gaming optimizations
│   │   ├── utils.py          # Utilities and helpers
│   │   └── logger.py         # Logging system
│   └── ui/
│       ├── tui_app.py        # Main TUI application
│       ├── dashboard.py      # Dashboard components
│       └── input_helper.py   # Keyboard input handling
├── docs/
│   └── AI_MEMORY.md          # AI context documentation
├── setup.sh                  # Dependency installer
├── run.sh                    # Application launcher
└── README.md                 # This file
```

---

## 📊 Supported Optimizations

### Kernel Parameters (45+)
| Category | Parameters | Examples |
|----------|------------|----------|
| Memory | 10+ | `vm.swappiness`, `vm.dirty_ratio`, `vm.vfs_cache_pressure` |
| Network | 15+ | `net.ipv4.tcp_congestion_control`, `net.core.rmem_max` |
| Scheduler | 8+ | `kernel.sched_autogroup_enabled`, `kernel.sched_latency_ns` |
| Security | 5+ | `kernel.unprivileged_bpf_disabled`, `kernel.dmesg_restrict` |

### I/O Schedulers
| Disk Type | Recommended | Alternative |
|-----------|-------------|-------------|
| NVMe | `none` | `mq-deadline` |
| SATA SSD | `mq-deadline` | `bfq` |
| HDD | `bfq` | `mq-deadline` |

### Gaming Optimizations
- 🎮 GameMode integration
- ⚡ CPU Performance governor
- 🖥️ Compositor disable (KDE/GNOME)
- 🔧 Gaming-specific sysctl parameters

---

## 🔄 Changelog

### v2.0.0 (December 2025)
- ✨ AI-Driven Optimization Workflow
- ↩️ Transaction-Based Rollback System
- 🔍 Universal Hardware Detection
- 🧠 Smart Proposal System with Explanations
- 🛡️ Safe Integer Comparison Guards
- 📊 Enhanced Scoring System

---

## 🤝 Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

---

## 📜 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

---

## 👨‍💻 Author

**Taylan Soylu**
- GitHub: [@bingoweb](https://github.com/bingoweb)

---

<p align="center">
  Made with ❤️ for the Fedora community
</p>
