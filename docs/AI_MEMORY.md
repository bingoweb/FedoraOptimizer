# Fedora Optimizer - AI Development Memory 🧠

**Last Updated:** 2025-12-21
**Project Status:** Active / Optimization-Focused v2.0
**Core Tech:** Python 3, `rich` (TUI), `psutil`, `subprocess`

## 🌟 Project Overview
A dedicated AI-Powered System Optimization Tool for Fedora Linux. This project focuses solely on optimization - no cleaner, no uninstaller, no security module. **One job, done exceptionally well.**

## 📂 Architecture

### Directory Structure (Streamlined)
```
fedoraclean/
├── run.sh              # Entry point (sudo ./run.sh)
├── setup.sh            # Virtual environment setup
├── requirements.txt    # Python dependencies
├── docs/
│   └── AI_MEMORY.md    # This file
└── src/
    ├── modules/
    │   ├── optimizer.py   # THE BRAIN - All optimization logic
    │   ├── gaming.py      # Gaming mode optimizations
    │   ├── utils.py       # Shared utilities & Theme
    │   └── logger.py      # Debug logging
    └── ui/
        ├── tui_app.py     # Main TUI application
        ├── dashboard.py   # System monitoring widgets
        └── input_helper.py # Keyboard input handling
```

## 🤖 Core Components

### 1. HardwareDetector (Deep Profiling)
- CPU Microarchitecture (Intel P/E cores, AMD Zen CCX)
- NVMe SMART health data
- Kernel features (cgroup_v2, io_uring, PSI, sched_ext)
- BIOS/DMI settings (Secure Boot, Virtualization)

### 2. SysctlOptimizer (30+ Parameters)
| Category | Parameters |
|----------|------------|
| Memory | vm.swappiness, vm.dirty_ratio, vm.vfs_cache_pressure |
| Network | tcp_congestion_control=bbr, tcp_fastopen=3 |
| I/O | dirty_expire_centisecs, dirty_writeback_centisecs |

### 3. IOSchedulerOptimizer
Dynamic scheduler selection based on device type and workload:
- NVMe: `none` or `mq-deadline`
- SSD: `bfq` or `mq-deadline`
- HDD: `bfq`

### 4. GamingOptimizer
- GameMode integration
- CPU governor control
- KDE compositor toggle
- BORE scheduler detection

### 5. OptimizationBackup
- Automatic snapshots before optimization
- One-click rollback

## 🎯 TUI Menu Structure
```
1. 🔍 DERİN TARAMA      - Sistem DNA analizi
2. ⚡ HIZLI OPTİMİZE    - Temel optimizasyonlar
3. 🚀 TAM OPTİMİZASYON  - Tüm AI özellikleri
4. 🎮 OYUN MODU        - Gaming optimizasyonu
5. 💾 I/O SCHEDULER    - Disk zamanlayıcı
6. 🌐 AĞ OPTİMİZE      - TCP/BBR ayarları
7. 🔧 KERNEL AYAR      - Sysctl parametreleri
8. ↩️ GERİ AL          - Rollback
0. ❌ ÇIKIŞ
```

## ⚠️ Critical Notes
- **Root Required:** App runs via `sudo ./run.sh`
- **Idempotency:** All methods check before applying
- **Backup First:** Full optimization creates automatic backup
