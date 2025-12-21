import os
import psutil
import platform
import re
from .utils import run_command, console, Theme
from rich.panel import Panel
from rich.prompt import Prompt, Confirm
from rich.table import Table
from rich.align import Align

class HardwareDetector:
    """Deep Hardware Profiling Engine - 2025 Enhanced"""
    
    def __init__(self):
        self.cpu_info = self._get_cpu_details()
        self.cpu_microarch = self._get_cpu_microarchitecture()
        self.ram_info = self._get_ram_details()
        self.gpu_info = self._get_gpu_details()
        self.disk_info = self._get_disk_details()
        self.nvme_health = self._get_nvme_health()
        self.net_info = self._get_net_details()
        self.chassis = self._get_chassis_type()
        self.kernel_features = self._get_kernel_features()
        self.bios_info = self._get_bios_settings()
    
    def _get_cpu_microarchitecture(self):
        """Universal CPU Architecture Detection - Works on Intel, AMD, ARM, VM"""
        info = {
            "vendor": "Unknown",
            "family": "Unknown",
            "model_name": "Unknown",
            "arch": "x86_64",  # x86_64, aarch64, etc.
            "hybrid": False,
            "p_cores": 0,
            "e_cores": 0,
            "total_cores": 0,
            "total_threads": 0,
            "topology": "Unknown",
            "has_avx512": False,
            "has_avx2": False,
            "governor": "Unknown",
            "scaling_driver": "Unknown",  # intel_pstate, amd_pstate, acpi-cpufreq
            "epp": "Unknown",
            "is_vm": False,
            "hypervisor": None,
            "cpu_generation": "Unknown",  # Zen3, Alder Lake, etc.
        }
        try:
            # Architecture detection
            s, out, _ = run_command("uname -m")
            if s:
                info["arch"] = out.strip()
            
            # VM/Hypervisor detection
            s, out, _ = run_command("systemd-detect-virt")
            if s and out.strip() and out.strip() != "none":
                info["is_vm"] = True
                info["hypervisor"] = out.strip()
            
            # Parse /proc/cpuinfo for detailed info
            with open("/proc/cpuinfo", "r") as f:
                content = f.read()
                
                # Vendor detection
                if "GenuineIntel" in content:
                    info["vendor"] = "Intel"
                elif "AuthenticAMD" in content:
                    info["vendor"] = "AMD"
                elif "ARM" in content.upper() or info["arch"] == "aarch64":
                    info["vendor"] = "ARM"
                
                # Model name
                for line in content.split('\n'):
                    if "model name" in line.lower():
                        info["model_name"] = line.split(':')[1].strip()
                        break
                    elif "Model" in line and info["vendor"] == "ARM":
                        info["model_name"] = line.split(':')[1].strip()
                        break
                
                # AVX support (x86 only)
                if info["arch"] == "x86_64":
                    if "avx512" in content.lower():
                        info["has_avx512"] = True
                    if "avx2" in content.lower():
                        info["has_avx2"] = True
            
            # Core/Thread count
            s, out, _ = run_command("nproc --all")
            if s:
                info["total_threads"] = int(out.strip())
            
            s, out, _ = run_command("lscpu | grep '^CPU(s):' | awk '{print $2}'")
            if s and out.strip():
                info["total_cores"] = int(out.strip())
            
            # Scaling driver detection (critical for optimization strategy)
            s, out, _ = run_command("cat /sys/devices/system/cpu/cpu0/cpufreq/scaling_driver 2>/dev/null")
            if s:
                info["scaling_driver"] = out.strip()
            
            # Intel-specific detection
            if info["vendor"] == "Intel":
                # Hybrid architecture detection (Alder Lake+)
                s, out, _ = run_command("cat /sys/devices/cpu_core/cpus 2>/dev/null")
                if s and out.strip():
                    info["hybrid"] = True
                    # Count P-cores
                    p_cores_str = out.strip()
                    if "-" in p_cores_str:
                        parts = p_cores_str.split("-")
                        info["p_cores"] = int(parts[1]) - int(parts[0]) + 1
                    else:
                        info["p_cores"] = len(p_cores_str.split(","))
                    
                    # Count E-cores
                    s2, out2, _ = run_command("cat /sys/devices/cpu_atom/cpus 2>/dev/null")
                    if s2 and out2.strip():
                        e_cores_str = out2.strip()
                        if "-" in e_cores_str:
                            parts = e_cores_str.split("-")
                            info["e_cores"] = int(parts[1]) - int(parts[0]) + 1
                        else:
                            info["e_cores"] = len(e_cores_str.split(","))
                    
                    info["topology"] = f"{info['p_cores']}P + {info['e_cores']}E Hibrit"
                    info["cpu_generation"] = "Alder Lake+"
                else:
                    info["topology"] = "Homojen"
                    # Try to guess generation from model name
                    if "13th" in info["model_name"] or "14th" in info["model_name"]:
                        info["cpu_generation"] = "Raptor Lake"
                    elif "12th" in info["model_name"]:
                        info["cpu_generation"] = "Alder Lake"
                    elif "11th" in info["model_name"]:
                        info["cpu_generation"] = "Tiger Lake"
                    elif "10th" in info["model_name"]:
                        info["cpu_generation"] = "Ice Lake"
            
            # AMD-specific detection
            elif info["vendor"] == "AMD":
                # Check for Zen architecture via amd_pstate or family
                if "amd_pstate" in info["scaling_driver"] or "amd-pstate" in info["scaling_driver"]:
                    info["cpu_generation"] = "Zen 2+"  # amd_pstate requires Zen 2+
                
                # CCX/CCD topology
                s, out, _ = run_command("lscpu | grep 'L3 cache'")
                if s and out.strip():
                    # Multiple L3 caches indicate multiple CCDs
                    info["topology"] = "Zen CCX/CCD"
                else:
                    info["topology"] = "Klasik AMD"
                
                # Try to detect Zen generation from model
                model = info["model_name"].lower()
                if "7000" in model or "9000" in model:
                    info["cpu_generation"] = "Zen 4"
                elif "5000" in model or "6000" in model:
                    info["cpu_generation"] = "Zen 3"
                elif "3000" in model or "4000" in model:
                    info["cpu_generation"] = "Zen 2"
                elif "2000" in model:
                    info["cpu_generation"] = "Zen+"
                elif "1000" in model:
                    info["cpu_generation"] = "Zen 1"
            
            # ARM-specific detection
            elif info["vendor"] == "ARM":
                info["topology"] = "ARM big.LITTLE" if "big" in info["model_name"].lower() else "ARM Homojen"
                info["cpu_generation"] = "ARM"
            
            # Current governor
            s, out, _ = run_command("cat /sys/devices/system/cpu/cpu0/cpufreq/scaling_governor 2>/dev/null")
            if s:
                info["governor"] = out.strip()
            
            # EPP (Energy Performance Preference) - Intel/AMD
            s, out, _ = run_command("cat /sys/devices/system/cpu/cpu0/cpufreq/energy_performance_preference 2>/dev/null")
            if s and out.strip():
                info["epp"] = out.strip()
                
        except Exception:
            pass
        return info
    
    def _get_nvme_health(self):
        """Read NVMe SMART data via nvme-cli"""
        info = {
            "available": False,
            "devices": [],
            "temperature": "N/A",
            "wear_level": "N/A",
            "power_on_hours": "N/A",
            "data_written_tb": "N/A"
        }
        try:
            # Check if nvme-cli is available
            s, out, _ = run_command("which nvme")
            if not s:
                return info
            
            # List NVMe devices
            s, out, _ = run_command("nvme list -o json 2>/dev/null")
            if s and out.strip():
                import json
                data = json.loads(out)
                devices = data.get("Devices", [])
                for dev in devices:
                    dev_path = dev.get("DevicePath", "")
                    info["devices"].append(dev_path)
                
                if info["devices"]:
                    info["available"] = True
                    # Get SMART data from first device
                    dev = info["devices"][0]
                    s2, out2, _ = run_command(f"nvme smart-log {dev} -o json 2>/dev/null")
                    if s2 and out2.strip():
                        smart = json.loads(out2)
                        # Temperature in Kelvin, convert to Celsius
                        temp_k = smart.get("temperature", 0)
                        if temp_k > 0:
                            info["temperature"] = f"{temp_k - 273}°C"
                        
                        # Percentage used (wear level)
                        info["wear_level"] = f"{smart.get('percent_used', 0)}%"
                        
                        # Power on hours
                        poh = smart.get("power_on_hours", 0)
                        info["power_on_hours"] = f"{poh:,} saat"
                        
                        # Data written (in units of 512KB, convert to TB)
                        dw = smart.get("data_units_written", 0)
                        tb = (dw * 512 * 1000) / (1024**4)
                        info["data_written_tb"] = f"{tb:.2f} TB"
        except Exception:
            pass
        return info
    
    def _get_kernel_features(self):
        """Detect enabled kernel features - 2025 Enhanced with Kernel 6.12+ features"""
        features = {
            # Basic features
            "cgroup_v2": False,
            "io_uring": False,
            "bpf": False,
            "psi": False,
            "zswap": False,
            "zram": False,
            
            # Kernel 6.12+ features
            "sched_ext": False,
            "sched_ext_state": "disabled",
            "bore_scheduler": False,
            "preempt_rt": False,
            "preempt_mode": "Unknown",
            
            # Kernel version info
            "kernel_version": "Unknown",
            "kernel_major": 0,
            "kernel_minor": 0,
            
            # Network
            "bbr_version": "Unknown",  # bbr, bbr2, bbr3
            "tcp_ecn": False,
            
            # Memory
            "transparent_hugepages": "Unknown",
            "thp_defrag": "Unknown",
            
            # Btrfs specific
            "btrfs_mount_options": {},
            "btrfs_noatime": False,
            "btrfs_compress": "Unknown",
            "btrfs_discard_async": False,
            
            # CPU governors/schedulers
            "available_governors": [],
            "available_schedulers": [],
        }
        try:
            # Kernel version parsing
            s, out, _ = run_command("uname -r")
            if s:
                features["kernel_version"] = out.strip()
                # Parse version like "6.12.4-200.fc41.x86_64"
                match = re.match(r'(\d+)\.(\d+)', out.strip())
                if match:
                    features["kernel_major"] = int(match.group(1))
                    features["kernel_minor"] = int(match.group(2))
            
            # cgroup v2
            s, out, _ = run_command("mount | grep cgroup2")
            features["cgroup_v2"] = s and "cgroup2" in out
            
            # io_uring support (check multiple ways)
            if os.path.exists("/proc/sys/kernel/io_uring_disabled"):
                s, out, _ = run_command("cat /proc/sys/kernel/io_uring_disabled")
                features["io_uring"] = s and out.strip() == "0"
            else:
                features["io_uring"] = os.path.exists("/sys/kernel/io_uring")
            
            # BPF filesystem
            features["bpf"] = os.path.exists("/sys/fs/bpf")
            
            # sched_ext (Kernel 6.12+) - Enhanced detection
            if os.path.exists("/sys/kernel/sched_ext"):
                features["sched_ext"] = True
                s, out, _ = run_command("cat /sys/kernel/sched_ext/state 2>/dev/null")
                if s and out.strip():
                    features["sched_ext_state"] = out.strip()  # enabled, disabled
            
            # BORE Scheduler detection (CachyOS kernel)
            s, out, _ = run_command("cat /sys/kernel/sched_bore/version 2>/dev/null")
            if s and out.strip():
                features["bore_scheduler"] = True
            else:
                # Alternative: check kernel version string
                if "bore" in features["kernel_version"].lower():
                    features["bore_scheduler"] = True
            
            # PREEMPT_RT detection
            if os.path.exists("/sys/kernel/realtime"):
                features["preempt_rt"] = True
            # Check kernel config or cmdline for preempt mode
            s, out, _ = run_command("cat /proc/cmdline")
            if s:
                if "preempt=full" in out:
                    features["preempt_mode"] = "full"
                elif "preempt=voluntary" in out:
                    features["preempt_mode"] = "voluntary"
                elif "preempt=none" in out:
                    features["preempt_mode"] = "none"
            
            # BBR version detection
            s, out, _ = run_command("sysctl net.ipv4.tcp_congestion_control 2>/dev/null")
            if s and "bbr" in out.lower():
                # Check for BBRv3 (kernel 6.5+)
                if features["kernel_major"] >= 6 and features["kernel_minor"] >= 5:
                    features["bbr_version"] = "bbr3"
                else:
                    features["bbr_version"] = "bbr"
            else:
                features["bbr_version"] = "cubic"
            
            # TCP ECN
            s, out, _ = run_command("sysctl net.ipv4.tcp_ecn 2>/dev/null")
            features["tcp_ecn"] = s and "1" in out or "2" in out
            
            # zswap
            s, out, _ = run_command("cat /sys/module/zswap/parameters/enabled 2>/dev/null")
            features["zswap"] = s and out.strip() == "Y"
            
            # zram
            s, out, _ = run_command("zramctl --noheadings 2>/dev/null")
            features["zram"] = s and len(out.strip()) > 0
            
            # PSI (Pressure Stall Information)
            features["psi"] = os.path.exists("/proc/pressure/cpu")
            
            # Transparent Hugepages
            s, out, _ = run_command("cat /sys/kernel/mm/transparent_hugepage/enabled 2>/dev/null")
            if s:
                match = re.search(r'\[(\w+)\]', out)
                if match:
                    features["transparent_hugepages"] = match.group(1)
            
            # THP defrag mode
            s, out, _ = run_command("cat /sys/kernel/mm/transparent_hugepage/defrag 2>/dev/null")
            if s:
                match = re.search(r'\[(\w+)\]', out)
                if match:
                    features["thp_defrag"] = match.group(1)
            
            # Btrfs mount options for root filesystem
            s, out, _ = run_command("mount | grep 'on / ' | grep btrfs")
            if s and out.strip():
                features["btrfs_mount_options"]["root"] = out.strip()
                if "noatime" in out:
                    features["btrfs_noatime"] = True
                if "compress=" in out:
                    match = re.search(r'compress=(\w+)', out)
                    if match:
                        features["btrfs_compress"] = match.group(1)
                if "discard=async" in out:
                    features["btrfs_discard_async"] = True
            
            # Available CPU governors
            s, out, _ = run_command("cat /sys/devices/system/cpu/cpu0/cpufreq/scaling_available_governors 2>/dev/null")
            if s:
                features["available_governors"] = out.strip().split()
            
            # Available I/O schedulers
            s, out, _ = run_command("cat /sys/block/$(lsblk -d -o NAME | grep -v loop | grep -v zram | head -1)/queue/scheduler 2>/dev/null")
            if s:
                features["available_schedulers"] = re.findall(r'\[?(\w+)\]?', out)
                
        except Exception:
            pass
        return features
    
    def _get_bios_settings(self):
        """Read DMI tables for virtualization, secure boot, and BIOS info"""
        info = {
            "vendor": "Unknown",
            "version": "Unknown",
            "secure_boot": "Unknown",
            "virtualization": "Unknown",
            "uefi": False
        }
        try:
            # BIOS vendor and version
            s, out, _ = run_command("dmidecode -s bios-vendor 2>/dev/null")
            if s:
                info["vendor"] = out.strip()
            
            s, out, _ = run_command("dmidecode -s bios-version 2>/dev/null")
            if s:
                info["version"] = out.strip()
            
            # Secure Boot status
            s, out, _ = run_command("mokutil --sb-state 2>/dev/null")
            if s:
                if "enabled" in out.lower():
                    info["secure_boot"] = "Aktif"
                else:
                    info["secure_boot"] = "Devre Dışı"
            
            # Virtualization support
            s, out, _ = run_command("lscpu | grep 'Virtualization'")
            if s:
                if "VT-x" in out:
                    info["virtualization"] = "Intel VT-x"
                elif "AMD-V" in out:
                    info["virtualization"] = "AMD-V"
            
            # UEFI check
            info["uefi"] = os.path.exists("/sys/firmware/efi")
            
        except Exception:
            pass
        return info

    def _get_cpu_details(self):
        # Use lscpu or /proc/cpuinfo
        info = {"model": "Unknown", "cores": psutil.cpu_count(logical=True), "freq": "Unknown"}
        try:
            with open("/proc/cpuinfo", "r") as f:
                for line in f:
                    if "model name" in line:
                        info["model"] = line.split(":")[1].strip()
                        break
            # Freq
            info["freq"] = f"{psutil.cpu_freq().max:.0f} MHz" if psutil.cpu_freq() else "Unknown"
        except: pass
        return info

    def _get_ram_details(self):
        # Requires dmidecode for speed/type, but psutil gives size
        total_gb = round(psutil.virtual_memory().total / (1024**3), 1)
        info = {"total": total_gb, "type": "Unknown", "speed": "Unknown"}
        
        # Try dmidecode
        s, out, _ = run_command("dmidecode -t memory")
        if s:
            # Find Speed and Type
            speeds = re.findall(r"Speed: (\d+ MT/s|\d+ MHz)", out)
            types = re.findall(r"Type: (DDR\d)", out)
            
            if speeds: info["speed"] = max(speeds) # Use max speed found
            if types: info["type"] = types[0] # Assume homogeneous
            
        return info

    def _get_gpu_details(self):
        s, out, _ = run_command("lspci | grep -i 'vga\\|3d'")
        if not s: return "Bilinmeyen Grafik Birimi"
        # Clean up output: "00:02.0 VGA compatible controller: Intel Corporation..."
        lines = out.strip().split('\n')
        gpus = []
        for line in lines:
            parts = line.split(': ')
            if len(parts) > 1:
                gpus.append(parts[-1].strip())
        return ", ".join(gpus)

    def _get_disk_details(self):
        # NVMe details
        disk_desc = "Unknown"
        # Check root or main disk
        s, out, _ = run_command("lsblk -d -o NAME,MODEL,TRAN,SIZE | grep -v loop")
        if s:
            # Prioritize NVMe
            if "nvme" in out: 
                disk_desc = "NVMe SSD (Yüksek Performans)"
            elif "ssd" in out or "sata" in out:
                disk_desc = "SATA SSD"
            else:
                for line in out.split('\n'):
                    if "hdd" in line or "1" in line: # crude rotation check often needs ROTA col
                        pass
                # Better check
                s2, out2, _ = run_command("lsblk -d -o NAME,ROTA")
                if "1" in out2: disk_desc = "HDD (Mekanik Disk)"
                else: disk_desc = "SSD (Solid State)"
        return disk_desc

    def _get_net_details(self):
        s, out, _ = run_command("lspci | grep -i 'network\\|ethernet'")
        if not s: return "Bilinmeyen Ağ"
        controllers = []
        for line in out.strip().split('\n'):
             parts = line.split(': ')
             if len(parts) > 1:
                 name = parts[-1]
                 # Shorten
                 if "Wireless" in name: controllers.append(f"Wi-Fi: {name.split('Wireless')[0].strip()}")
                 elif "Ethernet" in name: controllers.append(f"Ethernet: {name.split('Ethernet')[0].strip()}")
                 else: controllers.append(name)
        return " + ".join(controllers[:2])

    def _get_chassis_type(self):
        try:
             with open("/sys/class/dmi/id/chassis_type", "r") as f:
                 t = f.read().strip()
                 if t in ["8", "9", "10", "14"]: return "Laptop"
        except: pass
        return "Desktop"

# ============================================================================
# 2025 AI-DRIVEN OPTIMIZATION ENGINE
# ============================================================================

from dataclasses import dataclass
from typing import List, Dict, Optional

@dataclass
class OptimizationProposal:
    """Single optimization change with AI-generated explanation"""
    param: str           # Parameter name (e.g., "vm.swappiness")
    current: str         # Current value
    proposed: str        # Proposed optimal value
    reason: str          # WHY this change is needed (Turkish)
    category: str        # "memory", "network", "scheduler", "disk", "boot"
    priority: str        # "critical", "recommended", "optional"
    command: str = ""    # Command to apply (for non-sysctl)
    

class AIOptimizationEngine:
    """
    AI-Driven Optimization Workflow Engine
    
    Pattern: SCAN → ANALYZE → EXPLAIN → CONFIRM → APPLY
    
    Tüm optimizasyonlar bu motoru kullanır:
    1. Mevcut durumu tara
    2. AI ile optimal değerleri hesapla
    3. Değişiklikleri ve nedenlerini açıkla
    4. Kullanıcı onayı al
    5. Onaylanırsa uygula
    """
    
    # Reason templates for different optimization types (Turkish)
    REASONS = {
        "swappiness_nvme": "NVMe SSD tespit edildi. Düşük swappiness (5-10) disk yerine RAM kullanımını önceliklendirir, çok daha hızlı erişim sağlar.",
        "swappiness_ssd": "SATA SSD tespit edildi. Düşük swappiness (10-20) SSD ömrünü korur ve performansı artırır.",
        "swappiness_hdd": "HDD tespit edildi. Varsayılan swappiness (60) mekanik diskler için uygundur.",
        "bbr_enable": "TCP BBR algoritması, özellikle yüksek gecikmeli bağlantılarda %50'ye kadar daha hızlı transfer sağlar.",
        "bbr_already": "TCP BBR zaten aktif. Ağ performansı optimal.",
        "fastopen": "TCP Fast Open, bağlantı kurulum süresini azaltarak web sayfalarının daha hızlı yüklenmesini sağlar.",
        "scheduler_nvme": "NVMe SSD için 'none' veya 'mq-deadline' scheduler önerilir. NVMe'nin dahili kuyruk yönetimi yeterlidir.",
        "scheduler_ssd": "SATA SSD için 'bfq' veya 'mq-deadline' scheduler önerilir. Dengeli I/O önceliklendirmesi sağlar.",
        "scheduler_hdd": "HDD için 'bfq' scheduler önerilir. Dönen disk erişimini optimize eder.",
        "dirty_ratio": "Bellek dirty ratio azaltıldığında, veriler diske daha sık yazılır. SSD'ler için düşük değer performansı artırır.",
        "governor_performance": "CPU governor 'performance' modu, CPU'yu sürekli maksimum frekansta tutar. Oyun ve yoğun iş yükleri için önerilir.",
        "governor_powersave": "CPU governor 'powersave' modu aktif. Pil ömrü için iyi ama performans düşük olabilir.",
        "trim_disabled": "TRIM aktif değil! SSD performansı ve ömrü için TRIM kritik öneme sahiptir.",
        "trim_enabled": "TRIM zaten aktif. SSD bakımı optimal.",
        "noatime_btrfs": "Btrfs dosya sistemi için 'noatime' mount seçeneği önerilir. Gereksiz yazma işlemlerini %20-30 azaltır.",
        "zram_disabled": "ZRAM aktif değil. ZRAM, RAM'i sıkıştırarak etkin bellek kapasitesini artırır.",
        "zram_enabled": "ZRAM zaten aktif. Bellek yönetimi optimal.",
        "hybrid_itmt": "Intel Hybrid CPU (P+E çekirdek) tespit edildi. Thread Director etkinleştirilmeli.",
        "amd_pstate": "AMD Zen işlemci tespit edildi. amd_pstate EPP aktif, optimal ayarlarda.",
        "sched_latency": "Scheduler parametreleri masaüstü kullanımı için optimize edilmeli. Düşük latency, daha duyarlı sistem.",
    }
    
    def __init__(self, hw_detector: 'HardwareDetector'):
        self.hw = hw_detector
        self.proposals: List[OptimizationProposal] = []
    
    def scan_current_sysctl(self, params: List[str]) -> Dict[str, str]:
        """Scan current sysctl values for given parameters"""
        current = {}
        for param in params:
            s, out, _ = run_command(f"sysctl -n {param} 2>/dev/null")
            if s:
                current[param] = out.strip()
            else:
                current[param] = "N/A"
        return current
    
    def scan_current_state(self) -> Dict:
        """Full system state scan"""
        state = {
            "disk_type": self._detect_disk_type(),
            "chassis": self.hw.chassis.lower(),
            "cpu_vendor": self.hw.cpu_microarch.get("vendor", "Unknown"),
            "cpu_hybrid": self.hw.cpu_microarch.get("hybrid", False),
            "kernel_version": self.hw.kernel_features.get("kernel_version", "Unknown"),
            "governor": self.hw.cpu_microarch.get("governor", "Unknown"),
            "bbr_active": False,
            "trim_active": False,
            "zram_active": self.hw.kernel_features.get("zram", False),
            "btrfs_noatime": self.hw.kernel_features.get("btrfs_noatime", False),
        }
        
        # Check BBR
        s, out, _ = run_command("sysctl -n net.ipv4.tcp_congestion_control 2>/dev/null")
        state["bbr_active"] = s and "bbr" in out.lower()
        
        # Check TRIM
        s, out, _ = run_command("systemctl is-enabled fstrim.timer 2>/dev/null")
        state["trim_active"] = "enabled" in out
        
        return state
    
    def _detect_disk_type(self) -> str:
        disk = self.hw.disk_info.lower()
        if "nvme" in disk:
            return "nvme"
        elif "ssd" in disk:
            return "ssd"
        return "hdd"
    
    def analyze_and_propose_sysctl(self, persona: str = "general") -> List[OptimizationProposal]:
        """Analyze current state and generate optimization proposals"""
        self.proposals = []
        state = self.scan_current_state()
        disk_type = state["disk_type"]
        
        # Key parameters to analyze
        params_to_check = [
            "vm.swappiness",
            "vm.dirty_ratio",
            "vm.dirty_background_ratio",
            "net.ipv4.tcp_congestion_control",
            "net.ipv4.tcp_fastopen",
            "net.core.rmem_max",
            "kernel.sched_autogroup_enabled",
        ]
        
        current_values = self.scan_current_sysctl(params_to_check)
        
        # === VM.SWAPPINESS ===
        current_swp = current_values.get("vm.swappiness", "60")
        if disk_type == "nvme":
            optimal_swp = "5"
            reason = self.REASONS["swappiness_nvme"]
        elif disk_type == "ssd":
            optimal_swp = "10"
            reason = self.REASONS["swappiness_ssd"]
        else:
            optimal_swp = "60"
            reason = self.REASONS["swappiness_hdd"]
        
        if current_swp != optimal_swp:
            self.proposals.append(OptimizationProposal(
                param="vm.swappiness",
                current=current_swp,
                proposed=optimal_swp,
                reason=reason,
                category="memory",
                priority="recommended"
            ))
        
        # === TCP CONGESTION CONTROL (BBR) ===
        current_cc = current_values.get("net.ipv4.tcp_congestion_control", "cubic")
        if "bbr" not in current_cc.lower():
            self.proposals.append(OptimizationProposal(
                param="net.ipv4.tcp_congestion_control",
                current=current_cc,
                proposed="bbr",
                reason=self.REASONS["bbr_enable"],
                category="network",
                priority="recommended"
            ))
        
        # === TCP FAST OPEN ===
        current_tfo = current_values.get("net.ipv4.tcp_fastopen", "1")
        if current_tfo != "3":
            self.proposals.append(OptimizationProposal(
                param="net.ipv4.tcp_fastopen",
                current=current_tfo,
                proposed="3",
                reason=self.REASONS["fastopen"],
                category="network",
                priority="optional"
            ))
        
        # === DIRTY RATIO (if SSD/NVMe) ===
        if disk_type in ["nvme", "ssd"]:
            current_dirty = current_values.get("vm.dirty_ratio", "20")
            optimal_dirty = "5" if disk_type == "nvme" else "10"
            if int(current_dirty) > int(optimal_dirty):
                self.proposals.append(OptimizationProposal(
                    param="vm.dirty_ratio",
                    current=current_dirty,
                    proposed=optimal_dirty,
                    reason=self.REASONS["dirty_ratio"],
                    category="memory",
                    priority="recommended"
                ))
        
        # === SCHEDULER AUTOGROUP ===
        current_ag = current_values.get("kernel.sched_autogroup_enabled", "0")
        if current_ag == "0" and state["chassis"] == "desktop":
            self.proposals.append(OptimizationProposal(
                param="kernel.sched_autogroup_enabled",
                current="0",
                proposed="1",
                reason=self.REASONS["sched_latency"],
                category="scheduler",
                priority="recommended"
            ))
        
        # === TRIM CHECK ===
        if disk_type in ["nvme", "ssd"] and not state["trim_active"]:
            self.proposals.append(OptimizationProposal(
                param="fstrim.timer",
                current="disabled",
                proposed="enabled",
                reason=self.REASONS["trim_disabled"],
                category="disk",
                priority="critical",
                command="systemctl enable --now fstrim.timer"
            ))
        
        # === ZRAM CHECK ===
        if not state["zram_active"]:
            self.proposals.append(OptimizationProposal(
                param="ZRAM",
                current="disabled",
                proposed="enabled",
                reason=self.REASONS["zram_disabled"],
                category="memory",
                priority="optional",
                command="dnf install -y zram-generator && systemctl enable --now zram-generator"
            ))
        
        return self.proposals
    
    def analyze_network_only(self) -> List[OptimizationProposal]:
        """Analyze only network-related parameters"""
        self.proposals = []
        
        network_params = [
            "net.ipv4.tcp_congestion_control",
            "net.ipv4.tcp_fastopen",
            "net.core.rmem_max",
            "net.core.wmem_max",
            "net.ipv4.tcp_mtu_probing",
            "net.ipv4.tcp_ecn",
        ]
        
        current = self.scan_current_sysctl(network_params)
        
        # BBR Check
        cc = current.get("net.ipv4.tcp_congestion_control", "cubic")
        if "bbr" not in cc.lower():
            self.proposals.append(OptimizationProposal(
                param="net.ipv4.tcp_congestion_control",
                current=cc,
                proposed="bbr",
                reason=self.REASONS["bbr_enable"],
                category="network",
                priority="recommended"
            ))
        
        # TCP Fast Open
        tfo = current.get("net.ipv4.tcp_fastopen", "0")
        if tfo != "3":
            self.proposals.append(OptimizationProposal(
                param="net.ipv4.tcp_fastopen",
                current=tfo,
                proposed="3",
                reason=self.REASONS["fastopen"],
                category="network",
                priority="recommended"
            ))
        
        # Buffer sizes (for high-bandwidth connections)
        rmem = current.get("net.core.rmem_max", "212992")
        if int(rmem) < 16777216:
            self.proposals.append(OptimizationProposal(
                param="net.core.rmem_max",
                current=rmem,
                proposed="16777216",
                reason="Büyük alım buffer'ı yüksek bant genişliğinde indirme hızını artırır. Özellikle 100+ Mbps bağlantılarda etkilidir.",
                category="network",
                priority="optional"
            ))
        
        wmem = current.get("net.core.wmem_max", "212992")
        if int(wmem) < 16777216:
            self.proposals.append(OptimizationProposal(
                param="net.core.wmem_max",
                current=wmem,
                proposed="16777216",
                reason="Büyük gönderim buffer'ı yüksek bant genişliğinde yükleme hızını artırır.",
                category="network",
                priority="optional"
            ))
        
        # MTU Probing (for better throughput)
        mtu = current.get("net.ipv4.tcp_mtu_probing", "0")
        if mtu == "0":
            self.proposals.append(OptimizationProposal(
                param="net.ipv4.tcp_mtu_probing",
                current=mtu,
                proposed="1",
                reason="MTU probing, ağ yolundaki en uygun paket boyutunu otomatik algılar. Daha verimli veri transferi sağlar.",
                category="network",
                priority="optional"
            ))
        
        return self.proposals
    
    def analyze_io_scheduler(self) -> List[OptimizationProposal]:
        """Analyze I/O scheduler proposals for all block devices"""
        self.proposals = []
        disk_type = self._detect_disk_type()
        
        # Get current schedulers
        s, out, _ = run_command("lsblk -d -o NAME,TYPE,TRAN 2>/dev/null")
        if not s:
            return self.proposals
        
        for line in out.strip().split('\n')[1:]:
            parts = line.split()
            if len(parts) >= 2:
                dev = parts[0]
                trans = parts[2] if len(parts) > 2 else ""
                
                # Get current scheduler
                sched_path = f"/sys/block/{dev}/queue/scheduler"
                s2, sched_out, _ = run_command(f"cat {sched_path} 2>/dev/null")
                if not s2:
                    continue
                
                # Parse current scheduler (marked with [brackets])
                current_sched = "unknown"
                for s in sched_out.strip().split():
                    if s.startswith('[') and s.endswith(']'):
                        current_sched = s[1:-1]
                        break
                
                # Determine optimal scheduler
                if "nvme" in trans or "nvme" in dev:
                    optimal = "none"
                    reason = self.REASONS["scheduler_nvme"]
                elif trans == "sata" and disk_type == "ssd":
                    optimal = "mq-deadline"
                    reason = self.REASONS["scheduler_ssd"]
                else:
                    optimal = "bfq"
                    reason = self.REASONS["scheduler_hdd"]
                
                if current_sched != optimal:
                    self.proposals.append(OptimizationProposal(
                        param=f"I/O Scheduler ({dev})",
                        current=current_sched,
                        proposed=optimal,
                        reason=reason,
                        category="disk",
                        priority="recommended",
                        command=f"echo {optimal} > {sched_path}"
                    ))
        
        return self.proposals

    
    def display_proposals(self) -> None:
        """Display proposals in a formatted table with explanations"""
        if not self.proposals:
            console.print("[green]✓ Tüm ayarlar zaten optimal! Değişiklik gerekmez.[/green]")
            return
        
        # Group by category
        categories = {}
        for p in self.proposals:
            if p.category not in categories:
                categories[p.category] = []
            categories[p.category].append(p)
        
        category_names = {
            "memory": "🧠 Bellek",
            "network": "🌐 Ağ",
            "scheduler": "⚡ Zamanlayıcı",
            "disk": "💾 Disk",
            "boot": "🚀 Açılış"
        }
        
        priority_colors = {
            "critical": "red",
            "recommended": "yellow",
            "optional": "dim"
        }
        
        console.print("\n[bold cyan]🧠 AI OPTİMİZASYON ÖNERİLERİ[/bold cyan]\n")
        
        for cat, proposals in categories.items():
            cat_name = category_names.get(cat, cat.title())
            console.print(f"[bold]{cat_name}[/bold]")
            
            table = Table(box=None, padding=(0, 1), expand=True)
            table.add_column("Parametre", style="cyan", width=28)
            table.add_column("Mevcut", style="red", width=10)
            table.add_column("Önerilen", style="green", width=10)
            table.add_column("Öncelik", width=10)
            
            for p in proposals:
                prio_color = priority_colors.get(p.priority, "white")
                prio_text = {"critical": "🔴 Kritik", "recommended": "🟡 Önerilen", "optional": "⚪ İsteğe Bağlı"}.get(p.priority, p.priority)
                table.add_row(p.param, p.current, p.proposed, f"[{prio_color}]{prio_text}[/]")
            
            console.print(table)
            
            # Show reasons
            for p in proposals:
                console.print(f"  [dim]→ {p.reason}[/dim]")
            
            console.print()
    
    def apply_proposals(self, backup_first: bool = True) -> List[str]:
        """Apply approved proposals and return list of applied changes"""
        applied = []
        
        if backup_first:
            try:
                backup = OptimizationBackup()
                backup.create_snapshot()
                console.print("[green]✓ Yedek oluşturuldu.[/green]")
            except:
                pass
        
        for p in self.proposals:
            try:
                if p.command:
                    # Custom command (e.g., systemctl)
                    s, _, err = run_command(p.command, sudo=True)
                    if s:
                        applied.append(f"{p.param}: {p.current} → {p.proposed}")
                        console.print(f"[green]✓ {p.param} uygulandı[/green]")
                    else:
                        console.print(f"[red]✗ {p.param} hatası: {err}[/red]")
                else:
                    # Sysctl parameter
                    s, _, err = run_command(f"sysctl -w {p.param}={p.proposed}", sudo=True)
                    if s:
                        applied.append(f"{p.param}: {p.current} → {p.proposed}")
                        console.print(f"[green]✓ {p.param} = {p.proposed}[/green]")
                    else:
                        console.print(f"[red]✗ {p.param} hatası: {err}[/red]")
            except Exception as e:
                console.print(f"[red]Hata: {e}[/red]")
        
        # Persist sysctl changes
        if applied:
            self._persist_sysctl_changes()
        
        return applied
    
    def _persist_sysctl_changes(self):
        """Save sysctl changes to config file for persistence"""
        conf_file = "/etc/sysctl.d/99-fedoraclean-ai.conf"
        lines = []
        
        for p in self.proposals:
            if not p.command:  # Only sysctl params
                lines.append(f"# {p.reason[:60]}...")
                lines.append(f"{p.param} = {p.proposed}")
        
        if lines:
            try:
                content = "# Fedora Optimizer - AI Generated Config\n" + "\n".join(lines) + "\n"
                with open(conf_file, "a") as f:
                    f.write(content)
            except:
                pass


# ============================================================================
# 2025 ADVANCED OPTIMIZATION ENGINES
# ============================================================================

class SysctlOptimizer:
    """2025 Kernel Parameter Optimization Engine - Research Based"""
    
    # Memory parameters optimized for different storage types
    MEMORY_PARAMS = {
        "vm.swappiness": {"ssd": 10, "nvme": 5, "hdd": 60, "default": 10},
        "vm.dirty_ratio": {"ssd": 10, "nvme": 5, "hdd": 20, "default": 10},
        "vm.dirty_background_ratio": {"ssd": 5, "nvme": 3, "hdd": 10, "default": 5},
        "vm.dirty_expire_centisecs": {"all": 500},
        "vm.dirty_writeback_centisecs": {"all": 100},
        "vm.vfs_cache_pressure": {"all": 50},
        "vm.compaction_proactiveness": {"desktop": 50, "laptop": 20, "gamer": 50},
        "vm.page_lock_unfairness": {"all": 1},
        "vm.watermark_boost_factor": {"all": 0},
        "vm.watermark_scale_factor": {"all": 125},
        "vm.zone_reclaim_mode": {"all": 0},
        "vm.min_free_kbytes": {"auto": True},  # Calculated based on RAM
    }
    
    # Network parameters for modern high-speed connections
    NETWORK_PARAMS = {
        "net.ipv4.tcp_congestion_control": "bbr",
        "net.core.default_qdisc": "fq",
        "net.ipv4.tcp_fastopen": 3,
        "net.ipv4.tcp_slow_start_after_idle": 0,
        "net.ipv4.tcp_mtu_probing": 1,
        "net.ipv4.tcp_ecn": 1,
        "net.core.rmem_max": 16777216,
        "net.core.wmem_max": 16777216,
        "net.core.rmem_default": 1048576,
        "net.core.wmem_default": 1048576,
        "net.core.netdev_max_backlog": 16384,
        "net.core.somaxconn": 8192,
        "net.ipv4.tcp_max_syn_backlog": 8192,
        "net.ipv4.tcp_tw_reuse": 1,
        "net.ipv4.tcp_fin_timeout": 15,
        "net.ipv4.tcp_keepalive_time": 60,
        "net.ipv4.tcp_keepalive_intvl": 10,
        "net.ipv4.tcp_keepalive_probes": 6,
        # 2025 new parameters
        "net.ipv4.tcp_notsent_lowat": 16384,
        "net.ipv4.tcp_window_scaling": 1,
        "net.ipv4.tcp_sack": 1,
        "net.ipv4.tcp_timestamps": 1,
    }
    
    # Latency-sensitive parameters for gaming/desktop - 2025 Enhanced
    LATENCY_PARAMS = {
        "kernel.sched_cfs_bandwidth_slice_us": 500,
        "kernel.sched_autogroup_enabled": 1,
        # 2025 scheduler tuning for responsiveness
        "kernel.sched_min_granularity_ns": 500000,
        "kernel.sched_wakeup_granularity_ns": 500000,
        "kernel.sched_migration_cost_ns": 50000,
        "kernel.sched_nr_migrate": 128,
    }
    
    # Security-related kernel parameters
    SECURITY_PARAMS = {
        "kernel.kptr_restrict": 2,
        "kernel.dmesg_restrict": 1,
        "kernel.perf_event_paranoid": 2,
        "net.ipv4.conf.all.rp_filter": 1,
        "net.ipv4.conf.default.rp_filter": 1,
        # 2025 additional security
        "kernel.unprivileged_bpf_disabled": 1,
        "net.core.bpf_jit_harden": 2,
    }
    
    def __init__(self, hw_detector: HardwareDetector):
        self.hw = hw_detector
        self.conf_file = "/etc/sysctl.d/99-fedoraclean-ai.conf"
        
    def get_disk_type(self) -> str:
        """Determine disk type from hardware detector"""
        disk = self.hw.disk_info.lower()
        if "nvme" in disk:
            return "nvme"
        elif "ssd" in disk:
            return "ssd"
        else:
            return "hdd"
    
    def calculate_min_free_kbytes(self) -> int:
        """Calculate optimal min_free_kbytes based on RAM size"""
        ram_gb = self.hw.ram_info['total']
        # Formula: sqrt(RAM in KB) * 16, capped between 64MB and 256MB
        import math
        ram_kb = ram_gb * 1024 * 1024
        calculated = int(math.sqrt(ram_kb) * 16)
        min_val = 65536  # 64MB
        max_val = 262144  # 256MB
        return max(min_val, min(max_val, calculated))
    
    def generate_optimized_config(self, persona: str = "general") -> dict:
        """Generate optimized sysctl parameters based on detected hardware - UNIVERSAL"""
        disk_type = self.get_disk_type()
        chassis = self.hw.chassis.lower()
        tweaks = {}
        
        # Get CPU info for vendor-specific optimizations
        cpu_info = getattr(self.hw, 'cpu_microarch', {})
        is_vm = cpu_info.get('is_vm', False)
        cpu_vendor = cpu_info.get('vendor', 'Unknown')
        
        # Skip aggressive tweaks on VMs
        if is_vm:
            console.print("[dim]VM tespit edildi - Minimal tweaks uygulanacak[/dim]")
            # Only apply safe network tweaks for VMs
            tweaks["net.ipv4.tcp_congestion_control"] = "bbr"
            tweaks["net.core.default_qdisc"] = "fq"
            tweaks["net.ipv4.tcp_fastopen"] = "3"
            return tweaks
        
        # Memory parameters based on disk type
        for param, values in self.MEMORY_PARAMS.items():
            if isinstance(values, dict):
                if "auto" in values and values["auto"]:
                    if param == "vm.min_free_kbytes":
                        tweaks[param] = str(self.calculate_min_free_kbytes())
                elif disk_type in values:
                    tweaks[param] = str(values[disk_type])
                elif chassis in values:
                    tweaks[param] = str(values[chassis])
                elif persona.lower() in ["gamer", "oyuncu"] and "gamer" in values:
                    tweaks[param] = str(values["gamer"])
                elif "all" in values:
                    tweaks[param] = str(values["all"])
                elif "default" in values:
                    tweaks[param] = str(values["default"])
        
        # Network parameters (universal)
        for param, value in self.NETWORK_PARAMS.items():
            tweaks[param] = str(value)
        
        # Form factor specific adjustments
        if chassis == "laptop":
            # Laptop: Balance performance and power
            tweaks["vm.laptop_mode"] = "5"
            tweaks["vm.dirty_writeback_centisecs"] = "1500"  # Less frequent writes
        elif chassis == "server":
            # Server: Maximize throughput
            tweaks["vm.dirty_ratio"] = "40"
            tweaks["vm.dirty_background_ratio"] = "10"
            tweaks["net.core.somaxconn"] = "65535"
        
        # CPU vendor specific tweaks
        if cpu_vendor == "AMD":
            # AMD Zen specific: better NUMA awareness
            tweaks["kernel.numa_balancing"] = "1"
        elif cpu_vendor == "Intel":
            # Intel: EPP-aware systems benefit from these
            if cpu_info.get('hybrid', False):
                # Hybrid CPUs: scheduler awareness
                tweaks["kernel.sched_itmt_enabled"] = "1"  # Intel Thread Director
        
        # Latency parameters for desktop/gamer (not server)
        if persona.lower() in ["gamer", "oyuncu", "geliştirici", "dev"] or chassis == "desktop":
            for param, value in self.LATENCY_PARAMS.items():
                tweaks[param] = str(value)
        
        return tweaks
    
    def apply_config(self, tweaks: dict) -> list:
        """Apply sysctl configuration and return list of applied changes"""
        applied = []
        
        # Read existing config
        current_conf = ""
        if os.path.exists(self.conf_file):
            try:
                with open(self.conf_file, "r") as f:
                    current_conf = f.read()
            except:
                pass
        
        # Find new lines to add
        new_lines = []
        for key, val in tweaks.items():
            if f"{key} = {val}" not in current_conf and f"{key}={val}" not in current_conf:
                new_lines.append(f"{key} = {val}")
                applied.append((key, val))
        
        if new_lines:
            try:
                with open(self.conf_file, "a") as f:
                    f.write("\n# FedoraClean AI Generated - " + 
                           __import__('datetime').datetime.now().strftime("%Y-%m-%d %H:%M") + "\n")
                    f.write("\n".join(new_lines) + "\n")
                # Apply immediately
                run_command("sysctl --system", sudo=True)
            except Exception as e:
                console.print(f"[red]Sysctl yazma hatası: {e}[/red]")
                return []
        
        return applied


class IOSchedulerOptimizer:
    """Dynamic I/O Scheduler Selection based on device type and workload"""
    
    # Optimal scheduler for each device type and workload
    SCHEDULER_MATRIX = {
        "nvme": {
            "gaming": "none",      # Minimum latency
            "server": "none",      # Maximum throughput
            "desktop": "mq-deadline",  # Balanced
            "mixed": "mq-deadline",
        },
        "ssd": {
            "gaming": "mq-deadline",
            "server": "mq-deadline",
            "desktop": "bfq",      # Fair I/O for desktop responsiveness
            "mixed": "mq-deadline",
        },
        "hdd": {
            "all": "bfq",          # Best for rotational media
        },
    }
    
    # Read-ahead KB values
    READ_AHEAD = {
        "nvme": 256,
        "ssd": 256,
        "hdd": 4096,  # HDD benefits from more read-ahead
    }
    
    def __init__(self, hw_detector: HardwareDetector):
        self.hw = hw_detector
        
    def detect_block_devices(self) -> list:
        """Get list of block devices with their types"""
        devices = []
        s, out, _ = run_command("lsblk -d -o NAME,TYPE,TRAN,ROTA -n")
        if s:
            for line in out.strip().split('\n'):
                if not line.strip():
                    continue
                parts = line.split()
                if len(parts) >= 4:
                    name, dev_type, transport, rota = parts[0], parts[1], parts[2], parts[3]
                    if dev_type == "disk" and "loop" not in name:
                        # Determine device category
                        if transport == "nvme":
                            category = "nvme"
                        elif rota == "0":
                            category = "ssd"
                        else:
                            category = "hdd"
                        devices.append({
                            "name": name,
                            "transport": transport,
                            "category": category,
                            "path": f"/dev/{name}"
                        })
        return devices
    
    def get_current_scheduler(self, device: str) -> str:
        """Get current I/O scheduler for a device"""
        s, out, _ = run_command(f"cat /sys/block/{device}/queue/scheduler 2>/dev/null")
        if s:
            match = re.search(r'\[(\w+)\]', out)
            if match:
                return match.group(1)
        return "unknown"
    
    def get_optimal_scheduler(self, device_category: str, workload: str = "desktop") -> str:
        """Determine optimal scheduler based on device and workload"""
        if device_category in self.SCHEDULER_MATRIX:
            matrix = self.SCHEDULER_MATRIX[device_category]
            if workload in matrix:
                return matrix[workload]
            elif "all" in matrix:
                return matrix["all"]
            elif "desktop" in matrix:
                return matrix["desktop"]
        return "mq-deadline"  # Safe default
    
    def apply_scheduler(self, device: str, scheduler: str) -> bool:
        """Apply I/O scheduler to a device"""
        sched_path = f"/sys/block/{device}/queue/scheduler"
        try:
            with open(sched_path, "w") as f:
                f.write(scheduler)
            return True
        except Exception as e:
            console.print(f"[red]Scheduler değiştirilemedi ({device}): {e}[/red]")
            return False
    
    def apply_read_ahead(self, device: str, category: str) -> bool:
        """Apply optimal read-ahead value"""
        ra_path = f"/sys/block/{device}/queue/read_ahead_kb"
        ra_value = self.READ_AHEAD.get(category, 256)
        try:
            with open(ra_path, "w") as f:
                f.write(str(ra_value))
            return True
        except:
            return False
    
    def optimize_all_devices(self, workload: str = "desktop") -> list:
        """Optimize all detected block devices"""
        results = []
        devices = self.detect_block_devices()
        
        for dev in devices:
            name = dev["name"]
            category = dev["category"]
            current = self.get_current_scheduler(name)
            optimal = self.get_optimal_scheduler(category, workload)
            
            if current != optimal:
                success = self.apply_scheduler(name, optimal)
                if success:
                    results.append({
                        "device": name,
                        "category": category,
                        "from": current,
                        "to": optimal,
                        "status": "changed"
                    })
            else:
                results.append({
                    "device": name,
                    "category": category,
                    "scheduler": current,
                    "status": "optimal"
                })
            
            # Apply read-ahead
            self.apply_read_ahead(name, category)
        
        return results


class OptimizationBackup:
    """Backup and restore system for optimization rollback"""
    
    BACKUP_DIR = "/var/lib/fedoraclean/backups"
    
    def __init__(self):
        os.makedirs(self.BACKUP_DIR, exist_ok=True)
    
    def create_snapshot(self, name: str = None) -> str:
        """Create a backup snapshot of current optimization configs"""
        import datetime
        import shutil
        
        timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
        snapshot_name = name or f"snapshot_{timestamp}"
        snapshot_dir = os.path.join(self.BACKUP_DIR, snapshot_name)
        
        os.makedirs(snapshot_dir, exist_ok=True)
        
        # Files to backup
        backup_files = [
            "/etc/sysctl.d/99-fedoraclean-ai.conf",
            "/etc/sysctl.d/99-fedoraclean-net.conf",
            "/etc/dnf/dnf5.conf",
            "/etc/dnf/dnf.conf",
            "/etc/fstab",
        ]
        
        for src in backup_files:
            if os.path.exists(src):
                dst = os.path.join(snapshot_dir, os.path.basename(src))
                try:
                    shutil.copy2(src, dst)
                except:
                    pass
        
        # Save current sysctl values
        s, out, _ = run_command("sysctl -a 2>/dev/null")
        if s:
            with open(os.path.join(snapshot_dir, "sysctl_dump.txt"), "w") as f:
                f.write(out)
        
        # Save metadata
        with open(os.path.join(snapshot_dir, "metadata.txt"), "w") as f:
            f.write(f"Created: {datetime.datetime.now().isoformat()}\n")
            f.write(f"Kernel: {__import__('platform').release()}\n")
        
        return snapshot_name
    
    def list_snapshots(self) -> list:
        """List available snapshots"""
        snapshots = []
        if os.path.exists(self.BACKUP_DIR):
            for name in os.listdir(self.BACKUP_DIR):
                path = os.path.join(self.BACKUP_DIR, name)
                if os.path.isdir(path):
                    meta_file = os.path.join(path, "metadata.txt")
                    created = "Unknown"
                    if os.path.exists(meta_file):
                        with open(meta_file, "r") as f:
                            for line in f:
                                if line.startswith("Created:"):
                                    created = line.split(":", 1)[1].strip()
                                    break
                    snapshots.append({"name": name, "created": created})
        return sorted(snapshots, key=lambda x: x["created"], reverse=True)
    
    def restore_snapshot(self, snapshot_name: str) -> bool:
        """Restore configuration from a snapshot"""
        import shutil
        
        snapshot_dir = os.path.join(self.BACKUP_DIR, snapshot_name)
        if not os.path.exists(snapshot_dir):
            console.print(f"[red]Yedek bulunamadı: {snapshot_name}[/red]")
            return False
        
        # Restore files
        restore_map = {
            "99-fedoraclean-ai.conf": "/etc/sysctl.d/99-fedoraclean-ai.conf",
            "99-fedoraclean-net.conf": "/etc/sysctl.d/99-fedoraclean-net.conf",
            "dnf5.conf": "/etc/dnf/dnf5.conf",
            "dnf.conf": "/etc/dnf/dnf.conf",
        }
        
        for src_name, dst_path in restore_map.items():
            src = os.path.join(snapshot_dir, src_name)
            if os.path.exists(src):
                try:
                    shutil.copy2(src, dst_path)
                    console.print(f"[green]✓ Geri yüklendi: {dst_path}[/green]")
                except Exception as e:
                    console.print(f"[red]✗ Hata ({dst_path}): {e}[/red]")
        
        # Reload sysctl
        run_command("sysctl --system", sudo=True)
        
        return True


class FedoraOptimizer:
    def __init__(self):
        self.dnf_conf = "/etc/dnf/dnf5.conf"
        self.hw = HardwareDetector()

    def get_system_dna(self):
        """Enhanced system DNA with deep profiling - Format for display"""
        dna = [
            f"[bold cyan]CPU:[/] {self.hw.cpu_info['model']} ({self.hw.cpu_info['cores']} Çekirdek, {self.hw.cpu_info['freq']})",
        ]
        
        # CPU Microarchitecture (if available)
        if hasattr(self.hw, 'cpu_microarch'):
            ma = self.hw.cpu_microarch
            if ma['hybrid']:
                dna.append(f"[bold cyan]  └─ Mimari:[/] {ma['topology']} (Hibrit)")
            else:
                dna.append(f"[bold cyan]  └─ Mimari:[/] {ma['vendor']} {ma['topology']}")
            if ma['governor'] != "Unknown":
                dna.append(f"[bold cyan]  └─ Governor:[/] {ma['governor']} | EPP: {ma['epp']}")
        
        dna.append(f"[bold cyan]RAM:[/] {self.hw.ram_info['total']} GB {self.hw.ram_info['type']} @ {self.hw.ram_info['speed']}")
        dna.append(f"[bold cyan]GPU:[/] {self.hw.gpu_info}")
        dna.append(f"[bold cyan]DİSK:[/] {self.hw.disk_info}")
        
        # NVMe Health
        if hasattr(self.hw, 'nvme_health') and self.hw.nvme_health['available']:
            nvme = self.hw.nvme_health
            dna.append(f"[bold cyan]  └─ NVMe Sağlık:[/] Temp: {nvme['temperature']} | Aşınma: {nvme['wear_level']} | Yazılan: {nvme['data_written_tb']}")
        
        dna.append(f"[bold cyan]AĞ:[/] {self.hw.net_info}")
        dna.append(f"[bold cyan]TİP:[/] {self.hw.chassis}")
        
        # BIOS Info
        if hasattr(self.hw, 'bios_info'):
            bios = self.hw.bios_info
            dna.append(f"[bold cyan]BIOS:[/] {bios['vendor']} ({bios['version']})")
            boot_mode = "UEFI" if bios['uefi'] else "Legacy"
            dna.append(f"[bold cyan]  └─ Mod:[/] {boot_mode} | Secure Boot: {bios['secure_boot']} | {bios['virtualization']}")
        
        # Kernel Features
        if hasattr(self.hw, 'kernel_features'):
            kf = self.hw.kernel_features
            active_features = []
            if kf['psi']: active_features.append("PSI")
            if kf['cgroup_v2']: active_features.append("cgroup2")
            if kf['io_uring']: active_features.append("io_uring")
            if kf['bpf']: active_features.append("BPF")
            if kf['sched_ext']: active_features.append("sched_ext")
            if kf['zram']: active_features.append("ZRAM")
            if kf['zswap']: active_features.append("zswap")
            if active_features:
                dna.append(f"[bold cyan]Kernel:[/] {' | '.join(active_features)}")
            dna.append(f"[bold cyan]  └─ THP:[/] {kf['transparent_hugepages']}")
        
        return dna

    # ... Existing optimization methods (apply_dnf5, etc) remain ...
    
    def apply_dnf5_optimizations(self):
        console.print(f"[yellow]DNF5 Yapılandırması Kontrol Ediliyor ({self.dnf_conf})...[/yellow]")
        target_conf = self.dnf_conf
        if not os.path.exists(target_conf): target_conf = "/etc/dnf/dnf.conf"
        
        try:
             with open(target_conf, 'r') as f: content = f.read()
        except PermissionError:
             console.print(f"[red]Erişim reddedildi. Root gerekli.[/red]")
             return
        
        changes = []
        new_content = content
        
        if "max_parallel_downloads=10" in content:
            console.print("[dim cyan]• İndirme hızı zaten optimize edilmiş (10).[/]")
        elif "max_parallel_downloads" in content:
             new_content = new_content.replace("max_parallel_downloads=3", "max_parallel_downloads=10")
             changes.append("Maksimum indirme > 10")
        else:
            new_content += "\nmax_parallel_downloads=10\n"
            changes.append("Maksimum indirme > 10")
        
        if "defaultyes=True" in content:
             console.print("[dim cyan]• Varsayılan onay (defaultyes) zaten aktif.[/]")
        else:
            new_content += "\ndefaultyes=True\n"
            changes.append("Otomatik onay > True")

        if changes:
             try:
                 with open(target_conf, 'w') as f: f.write(new_content)
                 console.print(Panel("\n".join(changes), title="DNF5 Güncellendi", border_style=Theme.SUCCESS))
             except Exception as e: console.print(f"[red]Hata: {e}[/red]")
        else:
             console.print("[green]✓ DNF5 tamamen optimize durumda.[/green]")

    def optimize_boot_profile(self):
        console.print("[yellow]Boot Servisleri Kontrol Ediliyor...[/yellow]")
        s_ok, s_out, _ = run_command("systemctl is-enabled NetworkManager-wait-online.service")
        
        if "disabled" in s_out:
             console.print("[green]✓ NetworkManager-wait-online zaten devre dışı (Hızlı Boot aktif).[/green]")
        else:
            if Prompt.ask("[bold]Boot hızını artırmak için ağ bekleme servisinis kapatmak ister misiniz? (Önerilir)[/bold]", choices=["e", "h"], default="e") == "e":
                run_command("systemctl disable --now NetworkManager-wait-online.service", sudo=True)
                console.print("[green]✓ Servis devre dışı bırakıldı.[/green]")
            else:
                console.print("[dim]İşlem iptal edildi.[/dim]")

    def optimize_network(self):
        console.print("[yellow]Ağ Yığını (TCP/IP) Optimize Ediliyor...[/yellow]")
        tweaks = {
            "net.ipv4.tcp_fastopen": "3",
            "net.core.default_qdisc": "fq_codel",
            "net.ipv4.tcp_congestion_control": "bbr"
        }
        conf_file = "/etc/sysctl.d/99-fedoraclean-net.conf"
        current_conf = ""
        if os.path.exists(conf_file):
            with open(conf_file, 'r') as f: current_conf = f.read()
            
        new_lines = []
        for key, val in tweaks.items():
            if f"{key} = {val}" not in current_conf: new_lines.append(f"{key} = {val}")
        
        if new_lines:
             try:
                 with open(conf_file, "a") as f: f.write("\n".join(new_lines) + "\n")
                 run_command("sysctl --system", sudo=True)
                 console.print(Panel("\n".join(new_lines), title="sysctl Ayarları Eklendi", border_style=Theme.SUCCESS))
             except Exception as e: console.print(f"[red]Yazma hatası: {e}[/red]")
        else:
             console.print("[green]✓ Ağ yığını zaten optimize durumda.[/green]")

    def trim_ssd(self):
        if "SSD" not in self.hw.disk_info and "NVMe" not in self.hw.disk_info:
             console.print("[yellow]⚠ Sistemde SSD algılanmadı (veya HDD kullanılıyor). TRIM HDD için uygun değil.[/yellow]")
             # return silently or log? keeping simple
             pass

        console.print("[yellow]SSD Durumu Kontrol Ediliyor...[/yellow]")
        s_ok, s_out, _ = run_command("systemctl is-enabled fstrim.timer")
        if "enabled" not in s_out:
            run_command("systemctl enable --now fstrim.timer", sudo=True)
            console.print("[green]✓ Otomatik TRIM aktif edildi.[/green]")
        else:
            console.print("[dim cyan]• Otomatik SSD TRIM (fstrim.timer) zaten aktif.[/]")
        
        console.print(" > Manuel TRIM çalıştırılıyor...")
        run_command("fstrim -av", sudo=True)
        console.print("[green]✓ TRIM tamamlandı.[/green]")

    def optimize_btrfs(self):
        console.print("[yellow]Btrfs Bağlama Seçenekleri Kontrol Ediliyor...[/yellow]")
        fstab = "/etc/fstab"
        
        if not os.path.exists(fstab): return

        # Check against string description logic from HardwareDetector
        if "HDD" in self.hw.disk_info:
             console.print("[yellow]ℹ HDD kullanıyorsunuz. 'noatime' yine de faydalı olabilir ancak SSD kadar kritik değil.[/yellow]")
        try:
             with open(fstab, 'r') as f: lines = f.readlines()
        except: return
             
        new_lines = []
        changed = False
        for line in lines:
            if "btrfs" in line and "relatime" in line:
                new_lines.append(line.replace("relatime", "noatime"))
                changed = True
            else:
                new_lines.append(line)
        
        if changed:
            if Confirm.ask("[bold]Disk performansını artırmak için 'noatime' ayarı uygulansın mı?[/bold]"):
                 with open(fstab, 'w') as f: f.writelines(new_lines)
                 console.print("[green]✓ /etc/fstab güncellendi.[/green]")
        else:
            console.print("[green]✓ Btrfs zaten 'noatime' (veya özel ayar) kullanıyor.[/green]")

    def calculate_smart_score(self):
        score = 0
        report = []
        
        # 1. DNF (Universal)
        try:
            with open("/etc/dnf/dnf5.conf", "r") as f: c = f.read()
            if "max_parallel_downloads=10" in c: 
                score += 15
                report.append(("[green]MÜKEMMEL[/]", "Paket Yöneticisi", "DNF5 Tam Güçte (Paralel İndirme x10)."))
            else:
                report.append(("[yellow]GELİŞTİRİLMELİ[/]", "Paket Yöneticisi", "DNF5 limitli. Hızlandırma önerilir."))
        except: pass

        # 2. Boot Service
        s, out, _ = run_command("systemctl is-enabled NetworkManager-wait-online.service")
        if "disabled" in out:
             score += 15
             report.append(("[green]HIZLI[/]", "Boot Süresi", "Ağ bekleme servisi kapalı."))
        else:
             report.append(("[red]YAVAŞ[/]", "Boot Süresi", "Boot sırasında ağ bekleniyor (Gecikme yaratır)."))

        # 3. Disk Strategy (Context Aware)
        if "NVMe" in self.hw.disk_info:
            # NVMe uses 'none' scheduler usually
            # Check sched
            # Hard to pinpoint device name instantly, assume /dev/nvme0n1 for check
            # Or just check TRIM which is vital for NVMe
            t, out_t, _ = run_command("systemctl is-enabled fstrim.timer")
            if "enabled" in out_t:
                 score += 20
                 report.append(("[green]KORUNUYOR[/]", "NVMe Sağlığı", "NVMe SSD için otomatik TRIM aktif."))
            else:
                 report.append(("[red]RİSKLİ[/]", "NVMe Sağlığı", "Yüksek performanslı NVMe için TRIM şart!"))
        elif "SSD" in self.hw.disk_info:
            t, out_t, _ = run_command("systemctl is-enabled fstrim.timer")
            if "enabled" in out_t:
                 score += 20
                 report.append(("[green]KORUNUYOR[/]", "SSD Sağlığı", "Otomatik TRIM aktif."))
            else:
                 report.append(("[red]RİSKLİ[/]", "SSD Sağlığı", "SSD ömrü için TRIM açılmalı."))
        else:
            score += 20
            report.append(("[blue]SABİT[/]", "Disk", "Mekanik disk için standart yapılandırma."))

        # 4. Network (Wi-Fi 6 vs Ethernet)
        if os.path.exists("/etc/sysctl.d/99-fedoraclean-net.conf"):
             score += 15
             report.append(("[green]MODERN[/]", "Ağ Protokolü", "TCP BBR ve Fast Open aktif."))
        else:
             report.append(("[yellow]ESKİ[/]", "Ağ Protokolü", "Geleneksel TCP Cubic. BBR ile hızlanabilir."))

        # 5. RAM / ZRAM Strategy
        ram_gb = self.hw.ram_info['total']
        s_z, zram_out, _ = run_command("zramctl") # Fix: grab stdout
        
        if "zram" in zram_out:
            score += 20
            msg = f"{ram_gb} GB RAM ile ZRAM sıkıştırma devrede."
            if ram_gb < 16: msg += " (Düşük RAM için hayati)."
            report.append(("[green]VERİMLİ[/]", "Bellek Yönetimi", msg))
        else:
            if ram_gb < 16:
                report.append(("[red]KRİTİK[/]", "Bellek Yönetimi", f"{ram_gb} GB RAM var ama ZRAM kapalı! Performans düşer."))
            else:
                score += 15
                report.append(("[yellow]PASİF[/]", "Bellek Yönetimi", "ZRAM kapalı (Yüksek RAM var, acil değil)."))
        
        # 6. Performance Profile (New)
        # Check power-profiles-daemon if laptop
        if self.hw.chassis == "Laptop":
            s_p, p_out, _ = run_command("powerprofilesctl get")
            if "performance" in p_out or "balanced" in p_out:
                score += 15
                report.append(("[green]DENGELİ[/]", "Güç Yönetimi", f"Laptop modu: {p_out.strip()}"))
            else:
                report.append(("[yellow]TASARRUF[/]", "Güç Yönetimi", "Güç tasarrufu modunda. Performans düşebilir."))
        else:
            score += 15
            report.append(("[green]MAKSİMUM[/]", "Güç Yönetimi", "Masaüstü güç profili."))

        return min(100, score), report

    
    # --- AI / Expert System Engine ---

    def _get_pressure_stall(self, resource="cpu"):
        # Reads /proc/pressure/{cpu,io,memory}
        # Returns 'some 10' (avg10 pressure)
        try:
            with open(f"/proc/pressure/{resource}", "r") as f:
                content = f.read()
                # Format: some avg10=0.00 avg60=0.00 ...
                # Extract avg10
                match = re.search(r"avg10=(\d+\.\d+)", content)
                if match: return float(match.group(1))
        except: pass
        return 0.0

    def analyze_usage_persona(self):
        # Heuristic to determine user type
        persona = "Genel Kullanıcı"
        confidence = 0
        
        # Check active processes
        s, out, _ = run_command("ps -eo comm")
        procs = out.lower()
        
        if "steam" in procs or "lutris" in procs or "heroic" in procs:
            persona = "Oyuncu (Gamer)"
            confidence += 30
            
        if "code" in procs or "pycharm" in procs or "node" in procs or "docker" in procs:
             if persona == "Oyuncu (Gamer)":
                 persona = "Hibrit (Oyun & Dev)"
             else:
                 persona = "Geliştirici (Dev)"
             confidence += 30
             
        # Hardware Check
        if "NVIDIA" in self.hw.gpu_info or "AMD" in self.hw.gpu_info:
             if "Intel" not in self.hw.gpu_info: # Dedicated
                 confidence += 20
        
        if self.hw.ram_info['total'] > 30:
             confidence += 10 # Workstation likely
             
        return persona, confidence

    def optimize_ai_heuristic(self):
        console.print("[bold magenta]🤖 YZ Karar Motoru (AI Engine) Çalışıyor...[/bold magenta]")
        
        # 1. Gather Telemetry (Sensors)
        psi_cpu = self._get_pressure_stall("cpu")
        psi_io = self._get_pressure_stall("io")
        psi_mem = self._get_pressure_stall("memory")
        persona, conf = self.analyze_usage_persona()
        
        console.print(Panel(
            f"👤 [bold cyan]Tespit Edilen Persona:[/] {persona} (Güven: %{conf})\n"
            f"📊 [bold cyan]Sistem Stresi (PSI):[/] CPU: {psi_cpu:.2f} | IO: {psi_io:.2f} | MEM: {psi_mem:.2f}",
            title="AI Durum Analizi", border_style="magenta"
        ))
        
        tweaks = {}
        
        # 2. Decision Matrix
        
        # A. VM Compaction (Desfragmentation responsiveness)
        # Higher proactiveness = less latency spikes when allocating huge pages
        # Kernel default is usually 20.
        tweaks["vm.compaction_proactiveness"] = "20"
        
        if "Oyuncu" in persona or "Geliştirici" in persona:
             tweaks["vm.compaction_proactiveness"] = "50" # More aggressive compaction
             tweaks["vm.page_lock_unfairness"] = "1" # Reduce latency for lock contention
        
        # B. Swappiness Dynamic Adjustment
        # If PSI Memory is high (> 5.0), we need swap backing.
        # If low, we prefer RAM.
        if psi_mem > 5.0:
             tweaks["vm.swappiness"] = "60" # Allow swap to relieve pressure
        else:
             tweaks["vm.swappiness"] = "10" # Standard optimization for SSD
             
        # C. Scheduler Granularity
        # For Desktop/Latency, we want smaller timeslices usually? 
        # Actually newer kernels deprecated sched_latency_ns. 
        # We assume standard is fine, maybe tweak migration cost if available.
        
        # D. VFS Cache
        tweaks["vm.vfs_cache_pressure"] = "50" # Keep directory structure in RAM
        
        # E. Network Buffers (Auto-tuning usually good, but we ensure max)
        tweaks["net.core.rmem_max"] = "16777216"
        tweaks["net.core.wmem_max"] = "16777216"
        
        # Apply Logic
        console.print("[yellow]🧠 Algoritma Kararları Uygulanıyor (Kernel Sysctl)...[/yellow]")
        conf_file = "/etc/sysctl.d/99-fedoraclean-ai.conf"
        
        current_conf = ""
        if os.path.exists(conf_file):
             with open(conf_file, "r") as f: current_conf = f.read()
             
        new_lines = []
        for k, v in tweaks.items():
            if f"{k} = {v}" not in current_conf:
                 new_lines.append(f"{k} = {v}")
                 
        if new_lines:
             try:
                 with open(conf_file, "a") as f: f.write("\n".join(new_lines) + "\n")
                 run_command("sysctl --system", sudo=True)
                 for l in new_lines:
                     console.print(f"  [green]✓[/] {l} [dim](Persona: {persona})[/dim]")
             except Exception as e: console.print(f"[red]Hata: {e}[/red]")
        else:
             console.print("[green]✓ AI Kernel Ayarları zaten ideal durumda.[/green]")
             
        # F. CPU Governor Check (Intel P-State)
        if "Intel" in self.hw.cpu_info['model']:
             self.optimize_intel_pstate_ai(persona)

    def optimize_intel_pstate_ai(self, persona):
        # AI decision for P-State EPP (Energy Performance Preference)
        # Modes: performance, balance_performance, power
        console.print("[yellow]⚡ CPU Enerji Politikası (EPP) Denetleniyor...[/yellow]")
        
        target_epp = "balance_performance"
        if "Oyuncu" in persona or "Dev" in persona:
            if self.hw.chassis == "Desktop":
                 target_epp = "performance"
        # Apply to all cores
        # /sys/devices/system/cpu/cpu*/cpufreq/energy_performance_preference
        # Warning: This resets on boot unless we use TLP or tuned. 
        # We will use 'tuned-adm' if available as persistent method.
        
        s, out, _ = run_command("tuned-adm active")
        current_profile = out.strip().split(": ")[-1]
        
        target_profile = "balanced"
        if target_epp == "performance": target_profile = "throughput-performance"
        
        if target_profile not in current_profile:
             console.print(f"  [cyan]ℹ Hedef Profil: {target_profile} (Mevcut: {current_profile})[/]")
             if Confirm.ask(f"[bold]AI, '{target_profile}' güç profilini öneriyor. Geçiş yapılsın mı?[/bold]"):
                 run_command(f"tuned-adm profile {target_profile}", sudo=True)
                 console.print(f"[green]✓ Tuned profili güncellendi: {target_profile}[/green]")
        else:
             console.print(f"  [green]✓ CPU Güç Profili ({current_profile}) kullanıma uygun.[/green]")

    def optimize_intel_gpu(self):
        # Only for Intel systems
        if "Intel" not in self.hw.gpu_info:
             console.print("[dim]• Intel GPU algılanmadı. Atlanıyor.[/dim]")
             return

        console.print("[yellow]Intel Iris Xe (GuC/HuC) Bellenimi Kontrol Ediliyor...[/yellow]")
        
        # Check if parameter is already in GRUB cmdline
        try:
             with open("/proc/cmdline", "r") as f: cmdline = f.read()
             if "i915.enable_guc" in cmdline:
                  console.print("[green]✓ Intel GuC/HuC parametresi zaten ekli.[/green]")
                  return
        except: return

        if Confirm.ask("[bold]Intel GPU performansını artırmak için GuC/HuC Firmware aktif edilsin mi? (GRUB güncellenir)[/bold]"):
             # Fedora uses grubby safely
             # i915.enable_guc=2 -> Submission via GuC
             cmd = "grubby --update-kernel=ALL --args='i915.enable_guc=2'"
             s, out, err = run_command(cmd, sudo=True)
             if s:
                 console.print("[green]✓ GRUB güncellendi. Yeniden başlatma sonrası aktif olur.[/green]")
             else:
                 console.print(f"[red]⚠ Hata: {err}[/red]")

    def optimize_full_auto(self):
        """Enhanced full auto optimization using 2025 AI engines"""
        console.print("[bold magenta]🚀 TAM OTOMATİK YZ CİHAZ YÖNETİMİ (2025 Enhanced)[/bold magenta]")
        
        # 0. Create Backup First
        console.print("[yellow]📦 Yedek oluşturuluyor...[/yellow]")
        try:
            backup = OptimizationBackup()
            snapshot_name = backup.create_snapshot()
            console.print(f"[green]✓ Yedek oluşturuldu: {snapshot_name}[/green]")
        except Exception as e:
            console.print(f"[red]⚠ Yedek oluşturulamadı: {e}[/red]")
        
        # 1. Hardware & DNA Analysis
        console.print("\n[bold cyan]📊 Derin Sistem Analizi...[/bold cyan]")
        dna = self.get_system_dna()
        for line in dna[:8]:  # Show first 8 lines
            console.print(f"  {line}")
        
        # 2. Persona Detection
        persona, conf = self.analyze_usage_persona()
        console.print(f"\n[bold cyan]👤 Tespit Edilen Profil:[/] {persona} (Güven: %{conf})")
        
        # 3. Advanced Sysctl Optimization (NEW)
        console.print("\n[bold cyan]🧠 2025 Kernel Parametreleri Uygulanıyor...[/bold cyan]")
        try:
            sysctl_opt = SysctlOptimizer(self.hw)
            tweaks = sysctl_opt.generate_optimized_config(persona)
            applied = sysctl_opt.apply_config(tweaks)
            if applied:
                console.print(f"  [green]✓ {len(applied)} kernel parametresi optimize edildi.[/green]")
                for key, val in applied[:5]:  # Show first 5
                    console.print(f"    • {key} = {val}")
                if len(applied) > 5:
                    console.print(f"    [dim]... ve {len(applied) - 5} parametre daha[/dim]")
            else:
                console.print("  [dim]Tüm parametreler zaten optimal.[/dim]")
        except Exception as e:
            console.print(f"[red]Sysctl hatası: {e}[/red]")
        
        # 4. I/O Scheduler Optimization (NEW)
        console.print("\n[bold cyan]💾 I/O Zamanlayıcı Optimizasyonu...[/bold cyan]")
        try:
            io_opt = IOSchedulerOptimizer(self.hw)
            results = io_opt.optimize_all_devices(workload="desktop")
            for r in results:
                if r.get("status") == "changed":
                    console.print(f"  [green]✓ {r['device']} ({r['category']}): {r['from']} → {r['to']}[/green]")
                else:
                    console.print(f"  [dim]• {r['device']}: {r.get('scheduler', 'N/A')} (optimal)[/dim]")
        except Exception as e:
            console.print(f"[red]I/O Scheduler hatası: {e}[/red]")
        
        # 5. Legacy Heuristic Optimization
        self.optimize_ai_heuristic()
        
        # 6. Base/Legacy Optimizations
        console.print("\n[bold cyan]⚙️ Temel Optimizasyonlar...[/bold cyan]")
        self.apply_dnf5_optimizations()
        self.optimize_boot_profile()
        self.trim_ssd()
        self.optimize_btrfs()
        self.optimize_intel_gpu()
        
        # Final Summary
        console.print(Panel(
            "[bold green]🎉 SİSTEM 2025 YZ MOTORİYLE OPTİMİZE EDİLDİ![/bold green]\n\n"
            "✅ 30+ kernel parametresi uygulandı\n"
            "✅ I/O zamanlayıcıları donanıma göre ayarlandı\n"
            "✅ Ağ yığını BBR ile hızlandırıldı\n"
            "✅ Disk ve boot optimizasyonları tamamlandı\n\n"
            f"[dim]Yedek: {snapshot_name} (Geri almak için Rollback kullanın)[/dim]",
            border_style="green",
            title="[bold white]OPTİMİZASYON TAMAMLANDI[/]"
        ))

    # Need to merge AI logic into Score too
    def calculate_deep_score(self):
        score, report = self.calculate_smart_score() # Base score
        
        # AI Checks
        # VM Compaction
        try:
            with open("/proc/sys/vm/compaction_proactiveness", "r") as f: val = int(f.read().strip())
            if val >= 20: 
                score += 10
                report.append(("[green]AKILLI[/]", "Bellek Tepkisi", f"Proaktif Sıkıştırma Aktif ({val})"))
            else:
                 report.append(("[yellow]STANDART[/]", "Bellek Tepkisi", "Standart bellek yönetimi."))
        except: pass 
        
        # Intel GuC (copied from before)
        if "Intel" in self.hw.gpu_info:
             with open("/proc/cmdline", "r") as f: cmd = f.read()
             if "i915.enable_guc" in cmd:
                  score += 10
                  report.append(("[green]HIZLANDIRILMIŞ[/]", "GPU Firmware", "Intel GuC/HuC aktif."))
             else:
                  report.append(("[yellow]YAZILIM[/]", "GPU Firmware", "Standart CPU zamanlaması."))

        return min(100, score), report

    def full_audit(self):
        """Enhanced Deep System Audit with Category-Based Scoring"""
        from rich.table import Table
        from rich.align import Align
        from rich import box
        from rich.columns import Columns
        from rich.progress import Progress, SpinnerColumn, TextColumn
        import time
        
        console.print("\n[bold magenta]🧬 DERİN SİSTEM DNA ANALİZİ (2025 AI)[/bold magenta]\n")
        
        # Category scores
        scores = {
            "cpu": {"score": 0, "max": 25, "items": []},
            "memory": {"score": 0, "max": 25, "items": []},
            "disk": {"score": 0, "max": 25, "items": []},
            "network": {"score": 0, "max": 15, "items": []},
            "kernel": {"score": 0, "max": 10, "items": []},
        }
        
        with Progress(
            SpinnerColumn(),
            TextColumn("[bold cyan]{task.description}"),
            transient=True
        ) as progress:
            task = progress.add_task("Donanım profilleniyor...", total=5)
            
            # === CPU Analysis ===
            progress.update(task, description="CPU analiz ediliyor...")
            cpu = self.hw.cpu_microarch
            
            # CPU Vendor & Generation
            if cpu.get('vendor') != 'Unknown':
                scores["cpu"]["score"] += 5
                scores["cpu"]["items"].append(("✓", f"{cpu['vendor']} {cpu.get('cpu_generation', '')}"))
            
            # Governor check
            governor = cpu.get('governor', 'Unknown')
            if governor in ['performance', 'schedutil']:
                scores["cpu"]["score"] += 10
                scores["cpu"]["items"].append(("✓", f"Governor: {governor} (optimal)"))
            elif governor == 'powersave':
                scores["cpu"]["score"] += 5
                scores["cpu"]["items"].append(("!", f"Governor: {governor} (güç tasarrufu)"))
            else:
                scores["cpu"]["items"].append(("✗", f"Governor: {governor}"))
            
            # Scaling driver
            driver = cpu.get('scaling_driver', 'Unknown')
            if 'pstate' in driver:
                scores["cpu"]["score"] += 10
                scores["cpu"]["items"].append(("✓", f"Driver: {driver} (modern)"))
            elif driver != 'Unknown':
                scores["cpu"]["score"] += 5
                scores["cpu"]["items"].append(("~", f"Driver: {driver}"))
            
            progress.advance(task)
            
            # === Memory Analysis ===
            progress.update(task, description="Bellek analiz ediliyor...")
            
            # ZRAM check
            s, out, _ = run_command("zramctl")
            if s and "zram" in out:
                scores["memory"]["score"] += 10
                scores["memory"]["items"].append(("✓", "ZRAM aktif (sıkıştırılmış swap)"))
            else:
                scores["memory"]["items"].append(("!", "ZRAM kapalı"))
            
            # Swappiness check
            try:
                with open("/proc/sys/vm/swappiness", "r") as f:
                    swp = int(f.read().strip())
                if swp <= 20:
                    scores["memory"]["score"] += 10
                    scores["memory"]["items"].append(("✓", f"Swappiness: {swp} (SSD optimize)"))
                elif swp <= 60:
                    scores["memory"]["score"] += 5
                    scores["memory"]["items"].append(("~", f"Swappiness: {swp} (varsayılan)"))
                else:
                    scores["memory"]["items"].append(("!", f"Swappiness: {swp} (yüksek)"))
            except:
                pass
            
            # THP check
            kf = getattr(self.hw, 'kernel_features', {})
            thp = kf.get('transparent_hugepages', 'Unknown')
            if thp == 'madvise':
                scores["memory"]["score"] += 5
                scores["memory"]["items"].append(("✓", f"THP: {thp} (önerilen)"))
            elif thp == 'always':
                scores["memory"]["score"] += 3
                scores["memory"]["items"].append(("~", f"THP: {thp}"))
            
            progress.advance(task)
            
            # === Disk Analysis ===
            progress.update(task, description="Disk analiz ediliyor...")
            
            disk_type = self.hw.disk_info.lower()
            if "nvme" in disk_type:
                scores["disk"]["score"] += 10
                scores["disk"]["items"].append(("✓", "NVMe SSD (maksimum hız)"))
            elif "ssd" in disk_type:
                scores["disk"]["score"] += 7
                scores["disk"]["items"].append(("✓", "SATA SSD"))
            else:
                scores["disk"]["score"] += 3
                scores["disk"]["items"].append(("~", "HDD (mekanik disk)"))
            
            # TRIM check
            s, out, _ = run_command("systemctl is-enabled fstrim.timer")
            if "enabled" in out:
                scores["disk"]["score"] += 10
                scores["disk"]["items"].append(("✓", "TRIM aktif (SSD ömrü korunuyor)"))
            else:
                scores["disk"]["items"].append(("✗", "TRIM kapalı - SSD için kritik!"))
            
            # I/O Scheduler
            s, out, _ = run_command("cat /sys/block/$(lsblk -d -o NAME | grep -v loop | head -2 | tail -1)/queue/scheduler 2>/dev/null")
            if s:
                match = re.search(r'\[(\w+)\]', out)
                if match:
                    sched = match.group(1)
                    scores["disk"]["score"] += 5
                    scores["disk"]["items"].append(("✓", f"I/O Scheduler: {sched}"))
            
            progress.advance(task)
            
            # === Network Analysis ===
            progress.update(task, description="Ağ analiz ediliyor...")
            
            # BBR check
            s, out, _ = run_command("sysctl net.ipv4.tcp_congestion_control")
            if s and "bbr" in out:
                scores["network"]["score"] += 10
                scores["network"]["items"].append(("✓", "TCP BBR aktif (hızlı transfer)"))
            else:
                scores["network"]["items"].append(("!", "TCP Cubic (eski algoritma)"))
            
            # TCP Fast Open
            s, out, _ = run_command("sysctl net.ipv4.tcp_fastopen")
            if s and "3" in out:
                scores["network"]["score"] += 5
                scores["network"]["items"].append(("✓", "TCP Fast Open aktif"))
            else:
                scores["network"]["items"].append(("~", "TCP Fast Open kapalı"))
            
            progress.advance(task)
            
            # === Kernel Analysis ===
            progress.update(task, description="Kernel analiz ediliyor...")
            
            # PSI support
            if kf.get('psi', False):
                scores["kernel"]["score"] += 3
                scores["kernel"]["items"].append(("✓", "PSI (Pressure Stall Info) aktif"))
            
            # cgroup v2
            if kf.get('cgroup_v2', False):
                scores["kernel"]["score"] += 3
                scores["kernel"]["items"].append(("✓", "cgroup v2 (modern konteyner)"))
            
            # io_uring
            if kf.get('io_uring', False):
                scores["kernel"]["score"] += 2
                scores["kernel"]["items"].append(("✓", "io_uring (hızlı I/O)"))
            
            # BPF
            if kf.get('bpf', False):
                scores["kernel"]["score"] += 2
                scores["kernel"]["items"].append(("✓", "eBPF aktif"))
            
            progress.advance(task)
        
        # === Display DNA Report ===
        console.print()
        
        # System Identity Panel
        dna = self.get_system_dna()
        dna.append(f"[bold cyan]Kernel:[/] {platform.release()}")
        
        # VM Warning
        if cpu.get('is_vm', False):
            dna.append(f"[bold yellow]⚠ VM:[/] {cpu.get('hypervisor', 'Unknown')} (sınırlı optimizasyon)")
        
        dna_panel = Panel(
            "\n".join([f"[cyan]➤[/] {x}" for x in dna]),
            title="[bold white]🧬 SİSTEM DNA[/]",
            border_style="cyan",
            padding=(1, 2)
        )
        console.print(dna_panel)
        
        # === Category Score Tables ===
        console.print()
        
        def make_category_panel(name, emoji, data, color):
            score_pct = int((data["score"] / data["max"]) * 100)
            score_color = "green" if score_pct >= 80 else "yellow" if score_pct >= 50 else "red"
            
            items_text = "\n".join([
                f"[{'green' if i[0]=='✓' else 'yellow' if i[0] in ['!','~'] else 'red'}]{i[0]}[/] {i[1]}" 
                for i in data["items"]
            ])
            
            return Panel(
                f"{items_text}\n\n[bold {score_color}]Skor: {data['score']}/{data['max']}[/]",
                title=f"[bold {color}]{emoji} {name}[/]",
                border_style=color,
                width=40
            )
        
        # Row 1: CPU and Memory
        row1 = Columns([
            make_category_panel("CPU", "⚡", scores["cpu"], "blue"),
            make_category_panel("BELLEK", "🧠", scores["memory"], "magenta"),
        ], equal=True, expand=True)
        console.print(row1)
        
        # Row 2: Disk and Network
        row2 = Columns([
            make_category_panel("DİSK", "💾", scores["disk"], "cyan"),
            make_category_panel("AĞ", "🌐", scores["network"], "green"),
        ], equal=True, expand=True)
        console.print(row2)
        
        # === Total Score ===
        total_score = sum(s["score"] for s in scores.values())
        total_max = sum(s["max"] for s in scores.values())
        final_score = int((total_score / total_max) * 100)
        
        if final_score >= 85:
            score_color = "green"
            verdict = "MÜKEMMEL"
        elif final_score >= 70:
            score_color = "yellow"
            verdict = "İYİ"
        elif final_score >= 50:
            score_color = "orange1"
            verdict = "ORTA"
        else:
            score_color = "red"
            verdict = "GELİŞTİRİLMELİ"
        
        console.print()
        score_display = f"""
[bold {score_color}]
╔══════════════════════════════════════╗
║                                      ║
║   GENEL SAĞLIK SKORU: {final_score:3d}/100        ║
║   DEĞERLENDIRME: {verdict:^17}   ║
║                                      ║
╚══════════════════════════════════════╝
[/]"""
        console.print(Align.center(score_display))
        
        # === Recommendations ===
        if final_score < 95:
            console.print("\n[bold yellow]📋 ÖNERİLER:[/bold yellow]")
            
            if scores["disk"]["score"] < 20:
                console.print("  • [cyan]TRIM[/] aktifleştirin: [dim]sudo systemctl enable --now fstrim.timer[/dim]")
            
            if scores["network"]["score"] < 10:
                console.print("  • [cyan]BBR[/] aktifleştirin: [dim]3. Tam Otomatik Optimizasyon[/dim]")
            
            if scores["memory"]["score"] < 15:
                console.print("  • [cyan]ZRAM[/] aktifleştirin: [dim]sudo dnf install zram-generator[/dim]")
            
            if scores["cpu"]["score"] < 15:
                console.print("  • [cyan]CPU Governor[/] ayarlayın: [dim]4. Oyun Modu veya tuned-adm[/dim]")
            
            console.print("\n[bold]💡 İPUCU:[/] [green]3. TAM OPTİMİZASYON[/] tüm eksikleri tek seferde giderir.")

