# Fedora Optimizer - AI Development Memory 🧠

**Current Version:** v0.2.5 (Hardware Intelligence Release)
**Last Updated:** 2025-12-21
**Repository:** `https://github.com/bingoweb/FedoraOptimizer`

---

## 🏗️ Architecture & Core Logic

The project has evolved into a monolithic but modular AI engine located in `src/modules/optimizer.py`.

### 1. `HardwareDetector` Class
The "Eyes" of the system. Responsibilities:
- **Universal Detection:** Identifies CPU (Hybrid/Zen), Disk (NVMe/SATA), Chassis (Laptop/Desktop).
- **Workload Detection:** Scans installed binaries (`steam`, `docker`, `nginx`) to determine usage profile.
- **2025 Tech:** Detects `sched_ext`, `BBRv3` capability, `PSI` pressure data.

### 2. `AIOptimizationEngine` Class
The "Brain" of the system. Implements the workflow:
`SCAN` → `ANALYZE` → `EXPLAIN` → `CONFIRM` → `APPLY`

- **Analysis Logic:**
  - **Profile Rules:** e.g., If `Gamer` profile -> Apply `vm.max_map_count`.
  - **Hardware Rules:** e.g., If `Laptop` -> Increase `dirty_writeback_centisecs`.
  - **Kernel Rules:** e.g., If `bbr` missing -> Enable it.

### 3. `OptimizationProposal` Data Class
Standardized format for every change request:
```python
@dataclass
class OptimizationProposal:
    param: str        # e.g., "vm.swappiness"
    current: str      # e.g., "60"
    proposed: str     # e.g., "10"
    reason: str       # AI reasoning displayed to user
    category: str     # cpu, memory, network, gaming...
    priority: str     # critical, recommended, optional
    command: str      # Optional (if not simple sysctl)
```

---

## 🌟 Implemented Features (Development Areas)

### Area 1: 2025 Kernel Technologies (v0.2.1)
- **BBRv3:** Smart detection of available congestion controls (`bbr`, `bbr2`, `bbr3`).
- **PSI (Pressure Stall Information):** Reads `/proc/pressure` to measure CPU/IO stress.
- **sched_ext:** Detects and reports Extensible Scheduler status (Kernel 6.12+).

### Area 2: Deep DNA Reporting (v0.2.3)
- **0-100 Scoring System:**
  - **CPU (25p):** Governor, Hybrid logic, PSI.
  - **RAM (25p):** ZRAM, Swappiness, THP.
  - **Disk (25p):** Scheduler, TRIM, Health.
  - **Net (15p):** BBR, TFO.
  - **Kernel (10p):** Modern features.
- **Visualization:** ASCII Progress Bars in TUI (`[██████░░░░]`).

### Area 3: Smart Profile Management (v0.2.4)
- **Detective Mode:** Auto-detects installed software.
- **Profiles:**
  - 🎮 **Gamer:** `steam`, `lutris` → Tune `max_map_count`, `cfs_period`.
  - 👨‍💻 **Developer:** `docker`, `vscode` → Tune `inotify_watches`.
  - 🏢 **Server:** `nginx` → Tune `somaxconn`.

### Area 4: Hardware-Aware AI Tuning (v0.2.5)
- **Form Factor Intelligence:**
  - **Laptop (`🔋`):** Optimizes for battery (`vm.dirty_writeback_centisecs=6000`).
  - **Desktop (`⚡`):** Optimizes for performance (`governor=performance`).
- **CPU Intelligence:**
  - **Intel Hybrid:** Enforces `sched_itmt` (Thread Director).
  - **AMD Zen:** Checks `amd_pstate` status.

### Area 5: Modular Refactoring (v0.3.0)
- **New Architecture:** Monolithic `optimizer.py` split into `src/modules/optimizer/` package.
- **Code Quality:** Pylint score **9.21/10**.
- **Components:** `hardware.py`, `engine.py`, `sysctl.py`, `models.py`, `facade.py`.

---

## 🔄 Deployment & CI/CD
- **Semantic Versioning:** `v0.x.x`
- **GitHub Actions:** Automatically generates detailed release notes from commit history (Body & Subject).
- **Rollback:** Transaction-based rollback system (`transactions.json`).

## 🗺️ Next Steps (Future)
- **I/O Scheduler AI:** Deeper analysis of NVMe vs SATA scheduler (kyber vs bfq vs none).
- **Dashboard Mode:** Real-time monitoring TUI.
- **Benchmark Integration:** Before/After performance metrics.

---

**Use this memory file to quickly understand the project state when resuming development.**
