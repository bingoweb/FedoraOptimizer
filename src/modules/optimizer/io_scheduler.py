"""
I/O Scheduler optimization module.
Detects drive types and applies optimal schedulers (bfq, mq-deadline, etc.).
"""
import re
from typing import List, Dict
from ..utils import run_command, console
from .hardware import HardwareDetector

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

    def detect_block_devices(self) -> List[Dict[str, str]]:
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
            with open(sched_path, "w", encoding="utf-8") as f:
                f.write(scheduler)
            return True
        except (OSError, PermissionError) as e:
            console.print(f"[red]Scheduler değiştirilemedi ({device}): {e}[/red]")
            return False

    def apply_read_ahead(self, device: str, category: str) -> bool:
        """Apply optimal read-ahead value"""
        ra_path = f"/sys/block/{device}/queue/read_ahead_kb"
        ra_value = self.READ_AHEAD.get(category, 256)
        try:
            with open(ra_path, "w", encoding="utf-8") as f:
                f.write(str(ra_value))
            return True
        except (OSError, PermissionError):
            return False

    def optimize_all_devices(self, workload: str = "desktop") -> List[Dict[str, str]]:
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
