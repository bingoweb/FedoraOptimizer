"""
Mock hardware detector for testing purposes.
"""
from typing import List, Dict, Any


class MockHardwareDetector:
    """Mock HardwareDetector for testing without requiring actual hardware."""
    
    def __init__(
        self,
        disk_type: str = "nvme",
        ram_gb: float = 16.0,
        chassis: str = "Desktop",
        cpu_vendor: str = "Intel",
        profiles: List[str] = None
    ):
        """
        Initialize mock hardware detector.
        
        Args:
            disk_type: Type of disk (nvme, ssd, hdd)
            ram_gb: Total RAM in GB
            chassis: System chassis type
            cpu_vendor: CPU vendor (Intel, AMD)
            profiles: Detected workload profiles
        """
        self.disk_info = self._generate_disk_info(disk_type)
        self.cpu_info = self._generate_cpu_info(cpu_vendor)
        self.ram_info = self._generate_ram_info(ram_gb)
        self.gpu_info = "Intel Iris Xe Graphics"
        self.net_info = "Ethernet + WiFi"
        self.chassis = chassis
        self._profiles = profiles or ["General"]
        self._disk_type = disk_type
        
        self.cpu_microarch = {
            "vendor": cpu_vendor,
            "generation": "12th Gen" if cpu_vendor == "Intel" else "Zen 3",
            "hybrid": cpu_vendor == "Intel",
            "governor": "powersave",
            "epp": "balance_performance"
        }
        
        self.kernel_features = {
            "psi": True,
            "io_uring": True,
            "bpf": True,
            "sched_ext": False,
            "bbr_version": "bbr",
            "zram": True,
            "transparent_hugepages": "madvise"
        }
    
    def _generate_disk_info(self, disk_type: str) -> str:
        """Generate disk info string based on type."""
        types = {
            "nvme": "NVMe SSD 512GB Samsung 980 PRO",
            "ssd": "SATA SSD 512GB Crucial MX500",
            "hdd": "HDD 1TB WD Blue"
        }
        return types.get(disk_type, "Unknown Disk")
    
    def _generate_cpu_info(self, vendor: str) -> Dict[str, Any]:
        """Generate CPU info dict."""
        cpus = {
            "Intel": {
                "model": "Intel Core i5-1235U",
                "cores": 12,
                "freq": "3.3 GHz",
                "threads": 16
            },
            "AMD": {
                "model": "AMD Ryzen 7 5800X",
                "cores": 8,
                "freq": "3.8 GHz",
                "threads": 16
            }
        }
        return cpus.get(vendor, {"model": "Unknown CPU", "cores": 4, "freq": "2.0 GHz", "threads": 4})
    
    def _generate_ram_info(self, total_gb: float) -> Dict[str, Any]:
        """Generate RAM info dict."""
        return {
            "total": total_gb,
            "type": "DDR4",
            "speed": "3200 MHz"
        }
    
    def get_simple_disk_type(self) -> str:
        """Return simplified disk type."""
        return self._disk_type
    
    def detect_workload_profile(self) -> List[str]:
        """Return mock workload profiles."""
        return self._profiles.copy()
    
    def get_psi_stats(self) -> Dict[str, Any]:
        """Return mock PSI stats."""
        return {
            "cpu": {"some": {"avg10": 2.5, "avg60": 1.8, "avg300": 1.2}},
            "memory": {"some": {"avg10": 1.0, "avg60": 0.8, "avg300": 0.5}},
            "io": {"some": {"avg10": 0.5, "avg60": 0.3, "avg300": 0.2}}
        }
