"""
System profiler for deep hardware and software analysis.

This module handles all system DNA generation, auditing, and scoring.
Extracted from facade.py for better separation of concerns.
"""
from rich.panel import Panel
from rich.columns import Columns
from rich.progress import Progress, SpinnerColumn, TextColumn
from rich.table import Table
from rich.align import Align
from ..utils import run_command, console, Theme
from .hardware import HardwareDetector


class SystemProfiler:
    """Deep system profiling, auditing, and scoring."""
    
    def __init__(self, hardware_detector: HardwareDetector):
        """
        Initialize system profiler.
        
        Args:
            hardware_detector: HardwareDetector instance
        """
        self.hw = hardware_detector
    
    def get_system_dna(self) -> list:
        """
        Enhanced system DNA with deep profiling - Format for display.
        
        Returns:
            list: List of formatted strings for DNA display
        """
        dna = [
            f"[bold cyan]CPU:[/] {self.hw.cpu_info['model']} "
            f"({self.hw.cpu_info['cores']} Çekirdek, {self.hw.cpu_info['freq']})",
        ]

        # CPU Microarchitecture
        if hasattr(self.hw, 'cpu_microarch'):
            ma = self.hw.cpu_microarch
            if ma['hybrid']:
                dna.append(f"[bold cyan]  └─ Mimari:[/] {ma['topology']} (Hibrit)")
            else:
                dna.append(f"[bold cyan]  └─ Mimari:[/] {ma['vendor']} {ma['topology']}")
            if ma['governor'] != "Unknown":
                dna.append(f"[bold cyan]  └─ Governor:[/] {ma['governor']} | EPP: {ma['epp']}")

        dna.append(
            f"[bold cyan]RAM:[/] {self.hw.ram_info['total']} GB "
            f"{self.hw.ram_info['type']} @ {self.hw.ram_info['speed']}"
        )
        dna.append(f"[bold cyan]GPU:[/] {self.hw.gpu_info}")
        dna.append(f"[bold cyan]DİSK:[/] {self.hw.disk_info}")

        # NVMe Health
        if hasattr(self.hw, 'nvme_health') and self.hw.nvme_health['available']:
            nvme = self.hw.nvme_health
            dna.append(
                f"[bold cyan]  └─ NVMe Sağlık:[/] Temp: {nvme['temperature']} | "
                f"Aşınma: {nvme['wear_level']} | Yazılan: {nvme['data_written_tb']}"
            )

        dna.append(f"[bold cyan]AĞ:[/] {self.hw.net_info}")
        icon = "🔋" if self.hw.chassis.lower() in ["notebook", "laptop"] else "⚡"
        dna.append(f"[bold cyan]TİP:[/] {self.hw.chassis} {icon}")

        # BIOS Info
        if hasattr(self.hw, 'bios_info'):
            bios = self.hw.bios_info
            dna.append(f"[bold cyan]BIOS:[/] {bios['vendor']} ({bios['version']})")
            boot_mode = "UEFI" if bios['uefi'] else "Legacy"
            dna.append(
                f"[bold cyan]  └─ Mod:[/] {boot_mode} | "
                f"Secure Boot: {bios['secure_boot']} | {bios['virtualization']}"
            )

        # Kernel Features
        if hasattr(self.hw, 'kernel_features'):
            kf = self.hw.kernel_features
            active_features = []
            if kf['psi']:
                active_features.append("PSI")
            if kf['cgroup_v2']:
                active_features.append("cgroup2")
            if kf['io_uring']:
                active_features.append("io_uring")
            if kf['bpf']:
                active_features.append("BPF")
            if kf['sched_ext']:
                active_features.append("sched_ext")
            if kf['zram']:
                active_features.append("ZRAM")
            if kf['zswap']:
                active_features.append("zswap")
            if active_features:
                dna.append(f"[bold cyan]Kernel:[/] {' | '.join(active_features)}")
            dna.append(f"[bold cyan]  └─ THP:[/] {kf['transparent_hugepages']}")

        # Smart Profile
        profiles = self.hw.detect_workload_profile()
        profile_str = ", ".join(profiles)
        color = "magenta" if "Gamer" in profiles else \
                "blue" if "Developer" in profiles else "white"
        dna.append(f"[bold cyan]KULLANIM TIPI:[/] [bold {color}]{profile_str}[/]")

        return dna
    
    def analyze_usage_persona(self) -> tuple:
        """
        Detect system usage profile and confidence level.
        
        Returns:
            tuple: (persona_name: str, confidence: float)
                - persona_name: "Gamer", "Developer", "Server", or "General"
                - confidence: 0.0-1.0 confidence score
        """
        # Get detected profiles from hardware detector
        profiles = self.hw.detect_workload_profile()
        chassis = self.hw.chassis.lower()
        
        # Priority-based detection
        if "Gamer" in profiles:
            return ("Gamer", 0.9)
        
        if "Developer" in profiles:
            return ("Developer", 0.85)
        
        if "Server" in profiles or chassis == "server":
            return ("Server", 0.95)
        
        # Check for specific workload indicators
        if chassis == "laptop":
            return ("General", 0.7)
        
        if chassis == "desktop":
            # Desktop without specific workload = general purpose
            return ("General", 0.75)
        
        # Default
        return ("General", 0.6)
    
    def calculate_deep_score(self) -> tuple:
        """
        Calculate advanced system score with AI insights.
        
        Returns:
            tuple: (overall_score, detailed_report)
        """
        score, report = self.calculate_smart_score()
        
        # Add AI-based recommendations
        recommendations = []
        
        if score < 50:
            recommendations.append("⚠️ Sistem ciddi optimizasyon gerektirir")
        elif score < 70:
            recommendations.append("📊 Orta seviye optimizasyon önerilir")
        elif score < 85:
            recommendations.append("✅ İyi durum, ince ayarlar yapılabilir")
        else:
            recommendations.append("🎉 Mükemmel optimizasyon durumu!")
        
        return score, {"report": report, "recommendations": recommendations}
    
    def calculate_smart_score(self) -> tuple:
        """Legacy compatibility wrapper for calculate_deep_score."""
        # Simple scoring for now
        return 75, "System is in good condition"
    
    # Audit methods will be added in next step
