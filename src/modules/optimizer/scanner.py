"""
Scanner Module.
Responsible for scanning the system state and current configuration.
Extracts raw data for the Analyzer.
"""
import logging
from typing import Dict, List, Optional
from ..utils import run_command
from .hardware import HardwareDetector

logger = logging.getLogger("FedoraOptimizerDebug")

class SystemScanner:
    """
    Scans system state, sysctl values, and hardware configuration.
    Acts as the 'Eyes' of the optimization engine.
    """

    def __init__(self, hw_detector: HardwareDetector):
        self.hw = hw_detector

    def scan_sysctl_values(self, params: List[str]) -> Dict[str, str]:
        """
        Scans current values for a list of sysctl parameters.
        Returns a dictionary {param: value}.
        """
        current_values = {}
        for param in params:
            try:
                s, out, _ = run_command(f"sysctl -n {param} 2>/dev/null")
                if s and out:
                    value = out.strip()
                    current_values[param] = value
                    logger.debug(f"🔍 SCAN: {param} = '{value}'")
                else:
                    current_values[param] = "N/A"
                    logger.debug(f"🔍 SCAN: {param} = N/A (not found)")
            except Exception as e:
                logger.warning(f"Error scanning {param}: {e}")
                current_values[param] = "Error"
        return current_values

    def scan_full_state(self) -> Dict:
        """
        Aggregates all system state information into a single context dictionary.
        This context is passed to the Analyzer/AI.
        """
        disk_type = self._detect_disk_type()

        # Check TRIM status
        trim_active = False
        try:
            _, out, _ = run_command("systemctl is-enabled fstrim.timer 2>/dev/null")
            trim_active = "enabled" in (out or "")
        except Exception:
            pass

        # Detect manual/legacy profiles
        legacy_profiles = self.hw.detect_workload_profile()

        state = {
            "disk_type": disk_type,
            "chassis": self.hw.chassis.lower(),
            "cpu_vendor": self.hw.cpu_microarch.get("vendor", "Unknown"),
            "cpu_cores": self.hw.cpu_info.get("cores", 4),
            "cpu_hybrid": self.hw.cpu_microarch.get("hybrid", False),
            "ram_total_gb": self.hw.ram_info.get("total", 8.0),
            "trim_active": trim_active,
            "zram_active": self.hw.kernel_features.get("zram", False),
            "legacy_profiles": legacy_profiles,
        }

        return state

    def _detect_disk_type(self) -> str:
        """Helper to get simple disk type string"""
        return self.hw.get_simple_disk_type()
