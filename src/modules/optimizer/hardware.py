"""
Hardware detection module.
Profiles the system hardware and software configuration.
"""
import os
import re
import platform
import shutil
import logging
from typing import List, Dict
import psutil
from ..utils import run_command

logger = logging.getLogger("FedoraOptimizerDebug")



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

    def get_simple_disk_type(self) -> str:
        """Returns 'nvme', 'ssd', or 'hdd'"""
        disk = self.disk_info.lower()
        if "nvme" in disk:
            return "nvme"
        elif "ssd" in disk:
            return "ssd"
        return "hdd"

    def _get_chassis_type(self) -> str:
        s, out, _ = run_command("hostnamectl status")
        if s:
            match = re.search(r"Chassis:\s+(\w+)", out)
            if match:
                return match.group(1).title()

        if os.path.exists("/sys/class/dmi/id/chassis_type"):
            try:
                with open("/sys/class/dmi/id/chassis_type", "r", encoding='utf-8') as f:
                    type_id = f.read().strip()
                if type_id in ["9", "10", "14"]:
                    return "Laptop"
            except Exception:
                pass
        return "Desktop"

    def _get_cpu_details(self) -> Dict:
        info = {"model": "Unknown", "cores": 0, "freq": "Unknown"}
        try:
            with open("/proc/cpuinfo", "r", encoding='utf-8') as f:
                content = f.read()

            model_match = re.search(r"model name\s+:\s+(.+)", content)
            if model_match:
                info["model"] = model_match.group(1).strip()

            info["cores"] = psutil.cpu_count(logical=True)
            freq = psutil.cpu_freq()
            if freq:
                info["freq"] = f"{freq.max:.0f} MHz" if freq.max > 0 else \
                               f"{freq.current:.0f} MHz"
        except Exception as e:
            logger.debug(f"CPU details detection error: {e}")
        return info

    def _get_cpu_microarchitecture(self) -> Dict:
        ma = {
            "vendor": "Unknown", "family": "Unknown", "model_id": "Unknown",
            "microcode": "Unknown", "topology": "SMP", "hybrid": False,
            "governor": "Unknown", "driver": "Unknown", "epp": "Unknown",
            "is_vm": False, "hypervisor": "None"
        }

        s, out, _ = run_command("systemd-detect-virt")
        if s and "none" not in out:
            ma["is_vm"] = True
            ma["hypervisor"] = out.strip()

        try:
            with open("/proc/cpuinfo", "r", encoding='utf-8') as f:
                content = f.read()
            v_match = re.search(r"vendor_id\s+:\s+(.+)", content)
            if v_match:
                ma["vendor"] = v_match.group(1).strip()

            if "Intel" in ma["vendor"] and psutil.cpu_count(logical=False) > 8:
                if os.path.exists("/sys/devices/system/cpu/cpu0/topology/cluster_id"):
                    ma["hybrid"] = True
                    ma["topology"] = "Hybrid (Big.LITTLE)"
        except Exception as e:
            logger.debug(f"CPU microcode detection error: {e}")

        try:
            base = "/sys/devices/system/cpu/cpu0/cpufreq"
            if os.path.exists(f"{base}/scaling_driver"):
                with open(f"{base}/scaling_driver", "r", encoding='utf-8') as f:
                    ma["driver"] = f.read().strip()
            if os.path.exists(f"{base}/scaling_governor"):
                with open(f"{base}/scaling_governor", "r", encoding='utf-8') as f:
                    ma["governor"] = f.read().strip()

            epp_path = f"{base}/energy_performance_preference"
            if os.path.exists(epp_path):
                with open(epp_path, "r", encoding='utf-8') as f:
                    ma["epp"] = f.read().strip()
        except Exception as e:
            logger.debug(f"CPU config detection error: {e}")

        return ma

    def _get_ram_details(self) -> Dict:
        info = {"total": 0, "type": "DDR4", "speed": "Unknown"}
        try:
            mem = psutil.virtual_memory()
            info["total"] = round(mem.total / (1024**3), 1)

            if shutil.which("dmidecode"):
                s, out, _ = run_command("dmidecode --type memory")
                if s:
                    if "DDR5" in out:
                        info["type"] = "DDR5"
                    elif "DDR4" in out:
                        info["type"] = "DDR4"
                    elif "DDR3" in out:
                        info["type"] = "DDR3"

                    speeds = re.findall(r"Speed: (\d+) MT/s", out)
                    if not speeds:
                        speeds = re.findall(r"Speed: (\d+) MHz", out)
                    if speeds:
                        info["speed"] = f"{max(map(int, speeds))} MT/s"
        except Exception as e:
            logger.debug(f"RAM details detection error: {e}")
        return info

    def _get_gpu_details(self) -> str:
        s, out, _ = run_command("lspci | grep -i vga")
        if s:
            gpu = out.split(":", 2)[-1].strip()
            gpu = re.sub(r'\(.*?\)', '', gpu).strip()
            gpu = re.sub(r'\[.*?\]', '', gpu).strip()
            return gpu
        return "Unknown GPU"

    def _get_disk_details(self) -> str:
        disks = []
        s, out, _ = run_command("lsblk -d -o NAME,rota,tran")
        if s:
            for line in out.split('\n')[1:]:
                if not line.strip():
                    continue
                parts = line.split()
                if len(parts) >= 3:
                    name, rota, tran = parts[0], parts[1], parts[2]
                    if "loop" in name or "zram" in name:
                        continue

                    dtype = "HDD" if rota == "1" else "SSD"

                    if "nvme" in tran or "nvme" in name:
                        dtype = "NVMe SSD"
                    elif "usb" in tran:
                        dtype = "USB Drive"

                    disks.append(dtype)

        if not disks:
            return "Unknown Storage"
        if "NVMe SSD" in disks:
            return "NVMe SSD"
        if "SSD" in disks:
            return "SATA SSD"
        return "HDD"

    def _get_nvme_health(self) -> Dict:
        info = {
            "available": False, "temperature": "N/A",
            "wear_level": "N/A", "data_written_tb": "N/A"
        }

        if not shutil.which("nvme"):
            return info

        s, out, _ = run_command("lsblk -d -o NAME,TRAN")
        nvme_dev = None
        if s:
            for line in out.split('\n'):
                if "nvme" in line:
                    nvme_dev = f"/dev/{line.split()[0]}"
                    break

        if nvme_dev:
            s, out, _ = run_command(f"nvme smart-log {nvme_dev}", sudo=True)
            if s:
                info["available"] = True

                match = re.search(r"temperature\s+:\s+(\d+)\s+C", out)
                if match:
                    info["temperature"] = f"{match.group(1)}°C"

                match = re.search(r"percentage_used\s+:\s+(\d+)%", out)
                if match:
                    info["wear_level"] = f"{match.group(1)}%"

                match = re.search(r"data_units_written\s+:\s+[\d,]+", out)
                if match:
                    info["data_written_tb"] = "Unknown"

        return info

    def _get_net_details(self) -> str:
        stats = psutil.net_if_stats()
        active_iface = "None"
        speed = 0

        for iface, data in stats.items():
            if data.isup and not iface.startswith("lo"):
                active_iface = iface
                speed = data.speed
                break

        is_wifi = "wlan" in active_iface or "wl" in active_iface
        conn_type = "Wi-Fi" if is_wifi else "Ethernet"

        return f"{conn_type} ({speed} Mbps) - {active_iface}"

    def _get_bios_settings(self) -> Dict:
        info = {
            "vendor": "Unknown", "version": "",
            "uefi": False, "secure_boot": "Unknown",
            "virtualization": "Unknown"
        }

        if os.path.exists("/sys/class/dmi/id/bios_vendor"):
            try:
                with open("/sys/class/dmi/id/bios_vendor", "r", encoding='utf-8') as f:
                    info["vendor"] = f.read().strip()
                with open("/sys/class/dmi/id/bios_version", "r", encoding='utf-8') as f:
                    info["version"] = f.read().strip()
            except Exception:
                pass

        info["uefi"] = os.path.exists("/sys/firmware/efi")

        try:
            with open("/proc/cpuinfo", "r", encoding='utf-8') as f:
                c = f.read()
            if "vmx" in c or "svm" in c:
                info["virtualization"] = "VT-x/AMD-V Destekli"
            else:
                info["virtualization"] = "Sanallaştırma Yok"
        except Exception as e:
            logger.debug(f"BIOS details detection error: {e}")

        return info

    def _get_kernel_features(self) -> Dict:
        features = {
            "kernel_version": platform.release(),
            "psi": False, "cgroup_v2": False,
            "io_uring": False, "bpf": False, "sched_ext": False,
            "zram": False, "zswap": False,
            "transparent_hugepages": "Unknown",
            "bbr_version": "cubic", "btrfs_noatime": False
        }

        features["psi"] = os.path.exists("/proc/pressure/cpu")
        features["cgroup_v2"] = os.path.exists("/sys/fs/cgroup/cgroup.controllers")

        s, _, _ = run_command("grep io_uring_setup /proc/kallsyms")
        features["io_uring"] = s

        try:
            with open("/proc/sys/net/ipv4/tcp_congestion_control", "r", encoding='utf-8') as f:
                features["bbr_version"] = f.read().strip()
        except Exception as e:
            logger.debug(f"BBR version detection error: {e}")

        try:
            with open("/sys/kernel/mm/transparent_hugepage/enabled", "r", encoding='utf-8') as f:
                match = re.search(r'\[(\w+)\]', f.read())
                if match:
                    features["transparent_hugepages"] = match.group(1)
        except Exception as e:
            logger.debug(f"Transparent hugepages detection error: {e}")

        try:
            with open("/proc/swaps", "r", encoding='utf-8') as f:
                if "zram" in f.read():
                    features["zram"] = True
        except Exception as e:
            logger.debug(f"Hardware detection error: {e}")

        try:
            with open("/sys/module/zswap/parameters/enabled", "r", encoding='utf-8') as f:
                if f.read().strip() == "Y":
                    features["zswap"] = True
        except Exception as e:
            logger.debug(f"ZSwap detection error: {e}")

        return features

    def get_psi_stats(self) -> Dict:
        """Read detailed Pressure Stall Information"""
        stats = {}
        for res in ["cpu", "io", "memory"]:
            try:
                path = f"/proc/pressure/{res}"
                if os.path.exists(path):
                    with open(path, "r", encoding='utf-8') as f:
                        data = {}
                        for line in f:
                            parts = line.strip().split()
                            if len(parts) > 1:
                                kind = parts[0]
                                kv = {}
                                for p in parts[1:]:
                                    k, v = p.split('=')
                                    kv[k] = float(v)
                                data[kind] = kv
                        stats[res] = data
            except Exception:
                # Some kernels don't support PSI
                pass
        return stats

    def detect_workload_profile(self) -> List[str]:
        """Detect system usage profile based on installed packages/running procs"""
        profiles = ["General"]

        s, out, _ = run_command("ps -eo comm")
        procs = out.lower() if s else ""

        if "steam" in procs or "lutris" in procs or "heroic" in procs or "wine" in procs:
            if "Gamer" not in profiles:
                profiles.append("Gamer")

        dev_tools = ["code", "node", "python", "docker", "gcc", "git"]
        if any(t in procs for t in dev_tools):
            if "Developer" not in profiles:
                profiles.append("Developer")

        if self.chassis == "Server" or "fileserver" in profiles:
            profiles.append("Server")
            if "General" in profiles:
                profiles.remove("General")

        return profiles
