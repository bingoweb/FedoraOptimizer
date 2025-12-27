"""
AI Optimization Engine.
Core analysis logic, proposal generation, and optimization orchestration.
"""
from typing import List, Dict
from rich.table import Table
from ..utils import run_command, console
from .hardware import HardwareDetector
from .models import OptimizationProposal
from .transaction import TransactionManager
from .backup import OptimizationBackup


class AIOptimizationEngine:
    """
    AI-Driven Optimization Workflow Engine

    Pattern: SCAN → ANALYZE → EXPLAIN → CONFIRM → APPLY
    """

    # Reason templates for different optimization types (Turkish)
    REASONS = {
        "swappiness_nvme": "NVMe SSD tespit edildi. Düşük swappiness (5-10) "
                           "disk yerine RAM kullanımını önceliklendirir.",
        "swappiness_ssd": "SATA SSD tespit edildi. Düşük swappiness (10-20) "
                          "SSD ömrünü korur ve performansı artırır.",
        "swappiness_hdd": "HDD tespit edildi. Varsayılan swappiness (60) uygundur.",
        "bbr_enable": "TCP BBR algoritması, yüksek gecikmeli bağlantılarda "
                      "%50'ye kadar hız artışı sağlar.",
        "fastopen": "TCP Fast Open, bağlantı kurulum süresini azaltır.",
        "scheduler_nvme": "NVMe için 'none' önerilir (Dahili kuyruk yönetimi).",
        "scheduler_ssd": "SATA SSD için 'mq-deadline' veya 'bfq' önerilir.",
        "scheduler_hdd": "HDD için 'bfq' scheduler önerilir.",
        "dirty_ratio": "Düşük dirty ratio, SSD performansını artırır (tazeleme sıklığı).",
        "trim_disabled": "TRIM aktif değil! SSD performansı için kritiktir.",
        "zram_disabled": "ZRAM kapalı. Sıkıştırılmış bellek kapasiteyi artırır.",
        "sched_latency": "Masaüstü için düşük gecikmeli scheduler ayarları.",
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
            "trim_active": False,
            "zram_active": self.hw.kernel_features.get("zram", False),
            "profiles": self.hw.detect_workload_profile(),
        }

        # Check TRIM
        _, out, _ = run_command("systemctl is-enabled fstrim.timer 2>/dev/null")
        state["trim_active"] = "enabled" in out

        return state

    def _detect_disk_type(self) -> str:
        return self.hw.get_simple_disk_type()

    def analyze_and_propose_sysctl(self, persona: str = "general") -> List[OptimizationProposal]:
        """Analyze current state and generate optimization proposals"""
        self.proposals = []
        state = self.scan_current_state()
        disk_type = state["disk_type"]
        profiles = state.get("profiles", [])

        # Key parameters to analyze
        params_to_check = [
            "vm.swappiness",
            "vm.dirty_ratio",
            "net.ipv4.tcp_congestion_control",
            "net.ipv4.tcp_fastopen",
            "kernel.sched_autogroup_enabled",
            "vm.max_map_count",
            "kernel.sched_cfs_bandwidth_slice_us",
            "fs.inotify.max_user_watches",
            "vm.dirty_writeback_centisecs",
            "kernel.sched_itmt_enabled",
        ]

        current_values = self.scan_current_sysctl(params_to_check)

        # 1. Swappiness
        self._analyze_swappiness(current_values, disk_type)

        # 2. Network (BBR & FastOpen)
        self._analyze_network_basics(current_values)

        # 3. Dirty Ratio
        if disk_type in ["nvme", "ssd"]:
            self._analyze_dirty_ratio(current_values, disk_type)

        # 4. Scheduler & Latency
        if state["chassis"] == "desktop":
            curr_ag = current_values.get("kernel.sched_autogroup_enabled", "0")
            if curr_ag == "0":
                self.proposals.append(OptimizationProposal(
                    param="kernel.sched_autogroup_enabled",
                    current="0", proposed="1",
                    reason=self.REASONS["sched_latency"],
                    category="scheduler", priority="recommended"
                ))

        # 5. TRIM & ZRAM
        self._analyze_storage_features(state, disk_type)

        # 6. Profile Specifics
        if "Gamer" in profiles or persona == "Gamer":
            self._analyze_gamer_profile(current_values)
        if "Developer" in profiles or persona == "Developer":
            self._analyze_dev_profile(current_values)

        # 7. Hardware Specifics
        self._analyze_hardware_specifics(state, current_values)

        return self.proposals

    def _analyze_swappiness(self, current_values, disk_type):
        """Analyze swappiness parameter based on disk type and propose optimal value."""
        current_swp = current_values.get("vm.swappiness", "60")
        if disk_type == "nvme":
            optimal = "5"
            reason = self.REASONS["swappiness_nvme"]
        elif disk_type == "ssd":
            optimal = "10"
            reason = self.REASONS["swappiness_ssd"]
        else:
            optimal = "60"
            reason = self.REASONS["swappiness_hdd"]

        if current_swp != optimal:
            self.proposals.append(OptimizationProposal(
                param="vm.swappiness",
                current=current_swp,
                proposed=optimal,
                reason=reason,
                category="memory",
                priority="recommended"
            ))

    def _analyze_network_basics(self, current_values):
        """Analyze network parameters (BBR, TCP FastOpen) and propose improvements."""
        current_cc = current_values.get("net.ipv4.tcp_congestion_control", "cubic")
        if "bbr" not in current_cc.lower():
            self.proposals.append(OptimizationProposal(
                param="net.ipv4.tcp_congestion_control",
                current=current_cc, proposed="bbr",
                reason=self.REASONS["bbr_enable"],
                category="network", priority="recommended"
            ))

        current_tfo = current_values.get("net.ipv4.tcp_fastopen", "1")
        if current_tfo != "3":
            self.proposals.append(OptimizationProposal(
                param="net.ipv4.tcp_fastopen",
                current=current_tfo, proposed="3",
                reason=self.REASONS["fastopen"],
                category="network", priority="optional"
            ))

    def _analyze_dirty_ratio(self, current_values, disk_type):
        """Analyze vm.dirty_ratio parameter for SSD/NVMe optimization."""
        current_dirty = current_values.get("vm.dirty_ratio", "20")
        optimal_dirty = "5" if disk_type == "nvme" else "10"
        try:
            if current_dirty != "N/A" and int(current_dirty) > int(optimal_dirty):
                self.proposals.append(OptimizationProposal(
                    param="vm.dirty_ratio",
                    current=current_dirty, proposed=optimal_dirty,
                    reason=self.REASONS["dirty_ratio"],
                    category="memory", priority="recommended"
                ))
        except ValueError:
            pass

    def _analyze_storage_features(self, state, disk_type):
        """Analyze storage features like TRIM and ZRAM and propose enablement if missing."""
        if disk_type in ["nvme", "ssd"] and not state["trim_active"]:
            self.proposals.append(OptimizationProposal(
                param="fstrim.timer",
                current="disabled", proposed="enabled",
                reason=self.REASONS["trim_disabled"],
                category="disk", priority="critical",
                command="systemctl enable --now fstrim.timer"
            ))

        if not state["zram_active"]:
            s, _, _ = run_command("rpm -q zram-generator || dnf info zram-generator >/dev/null")
            if s:
                self.proposals.append(OptimizationProposal(
                    param="ZRAM",
                    current="disabled", proposed="enabled",
                    reason=self.REASONS["zram_disabled"],
                    category="memory", priority="optional",
                    command="dnf install -y zram-generator && "
                            "systemctl enable --now zram-generator"
                ))

    def _analyze_gamer_profile(self, current_values):
        """Analyze and propose gamer-specific optimizations (vm.max_map_count, scheduler)."""
        curr_map = current_values.get("vm.max_map_count", "65530")
        if curr_map.isdigit() and int(curr_map) < 1000000:
            self.proposals.append(OptimizationProposal(
                param="vm.max_map_count",
                current=curr_map, proposed="2147483642",
                reason="[GAMER] Steam oyunları için kritik bellek harita limiti.",
                category="gaming", priority="critical"
            ))

        curr_slice = current_values.get("kernel.sched_cfs_bandwidth_slice_us", "5000")
        if curr_slice != "3000":
            self.proposals.append(OptimizationProposal(
                param="kernel.sched_cfs_bandwidth_slice_us",
                current=curr_slice, proposed="3000",
                reason="[GAMER] CPU zamanlayıcı gecikmesini düşürür.",
                category="gaming", priority="recommended"
            ))

    def _analyze_dev_profile(self, current_values):
        """Analyze and propose developer-specific optimizations (inotify watches)."""
        curr_watch = current_values.get("fs.inotify.max_user_watches", "8192")
        if curr_watch.isdigit() and int(curr_watch) < 524288:
            self.proposals.append(OptimizationProposal(
                param="fs.inotify.max_user_watches",
                current=curr_watch, proposed="524288",
                reason="[DEV] IDE ve Docker için dosya izleme limitini artırır.",
                category="system", priority="recommended"
            ))

    def _analyze_hardware_specifics(self, state, current_values):
        """Analyze hardware-specific optimizations (laptop power, Intel hybrid, GPU)."""
        # Laptop
        if state["chassis"] in ["notebook", "laptop"]:
            curr_wb = current_values.get("vm.dirty_writeback_centisecs", "500")
            if curr_wb != "6000":
                self.proposals.append(OptimizationProposal(
                    param="vm.dirty_writeback_centisecs",
                    current=curr_wb, proposed="6000",
                    reason="[LAPTOP] Pil ömrü için diski daha az sık uyandırır.",
                    category="power", priority="recommended"
                ))

        # Intel Hybrid
        if state.get("cpu_hybrid", False):
            curr_itmt = current_values.get("kernel.sched_itmt_enabled", "0")
            if curr_itmt != "1":
                self.proposals.append(OptimizationProposal(
                    param="kernel.sched_itmt_enabled",
                    current=curr_itmt, proposed="1",
                    reason="[INTEL HYBRID] Thread Director (ITMT) aktivasyonu.",
                    category="cpu", priority="critical"
                ))

        # Intel GPU (GuC/HuC)
        if "Intel" in self.hw.gpu_info:
            try:
                with open("/proc/cmdline", "r", encoding='utf-8') as f:
                    cmdline = f.read()
                if "i915.enable_guc" not in cmdline:
                    self.proposals.append(OptimizationProposal(
                        param="i915.enable_guc",
                        current="disabled", proposed="2",
                        reason="[INTEL GPU] Iris Xe performans için GuC/HuC Firmware.",
                        category="gpu", priority="recommended",
        
        # Additional network checks - buffer sizes
        current_rmem = current_values.get("net.core.rmem_max", "0")
        if current_rmem != "N/A":
            try:
                if int(current_rmem) < 16777216:
                    self.proposals.append(OptimizationProposal(
                        param="net.core.rmem_max",
                        current=current_rmem,
                        proposed="16777216",
                        reason="Ağ alım buffer'ını 16MB'a yükseltir, yüksek bant genişliği için kritik",
                        category="network",
                        priority="recommended"
                    ))
            except ValueError:
                pass
        
        current_wmem = current_values.get("net.core.wmem_max", "0")
        if current_wmem != "N/A":
            try:
                if int(current_wmem) < 16777216:
                    self.proposals.append(OptimizationProposal(
                        param="net.core.wmem_max",
                        current=current_wmem,
                        proposed="16777216",
                        reason="Ağ gönderim buffer'ını 16MB'a yükseltir, upload performansı için önemli",
                        category="network",
                        priority="recommended"
                    ))
            except ValueError:
                pass
        
        return self.proposals

    def display_proposals(self) -> None:
        """Display proposals in a formatted table with explanations"""
        if not self.proposals:
            console.print("[green]✓ Tüm ayarlar zaten optimal![/green]")
            return

        categories = {}
        for p in self.proposals:
            categories.setdefault(p.category, []).append(p)

        console.print("\n[bold cyan]🧠 AI OPTİMİZASYON ÖNERİLERİ[/bold cyan]\n")

        for cat, proposals in categories.items():
            console.print(f"[bold]{cat.title()}[/bold]")

            table = Table(box=None, padding=(0, 1), expand=True)
            table.add_column("Parametre", style="cyan", width=28)
            table.add_column("Mevcut", style="red", width=10)
            table.add_column("Önerilen", style="green", width=10)
            table.add_column("Öncelik", width=10)

            for p in proposals:
                prio_text = "🔴" if p.priority == "critical" else \
                            "🟡" if p.priority == "recommended" else "⚪"
                table.add_row(p.param, p.current, p.proposed, prio_text)

            console.print(table)
            for p in proposals:
                console.print(f"  [dim]→ {p.reason}[/dim]")
            console.print()

    def apply_proposals(self, backup_first: bool = True, category: str = "general") -> List[str]:
        """Apply approved proposals and return list of applied changes"""
        applied = []
        changes_for_tx = []

        if backup_first:
            try:
                OptimizationBackup().create_snapshot()
                console.print("[green]✓ Yedek oluşturuldu.[/green]")
            except Exception:
                pass

        for p in self.proposals:
            try:
                success = False
                if p.command:
                    s, _, _ = run_command(p.command, sudo=True)
                    success = s
                else:
                    s, _, _ = run_command(f"sysctl -w {p.param}={p.proposed}", sudo=True)
                    success = s

                if success:
                    applied.append(f"{p.param}: {p.current} → {p.proposed}")
                    changes_for_tx.append({
                        "param": p.param, "old": p.current, "new": p.proposed
                    })
                    console.print(f"[green]✓ {p.param} uygulandı[/green]")
                else:
                    console.print(f"[red]✗ {p.param} uygulanamadı[/red]")
            except Exception as e:
                console.print(f"[red]Hata: {e}[/red]")

        if changes_for_tx:
            try:
                tm = TransactionManager()
                desc = f"{category.title()} Optimize - {len(changes_for_tx)} items"
                tm.record_transaction(category, desc, changes_for_tx)
            except Exception:
                pass

        if applied:
            self._persist_sysctl_changes()

        return applied

    def _persist_sysctl_changes(self):
        conf_file = "/etc/sysctl.d/99-fedoraclean.conf"
        lines = []
        for p in self.proposals:
            if not p.command:
                lines.append(f"# {p.reason}")
                lines.append(f"{p.param} = {p.proposed}")

        if lines:
            try:
                # Append to the main config file
                with open(conf_file, "a", encoding='utf-8') as f:
                    f.write("\n" + "\n".join(lines) + "\n")
            except Exception:
                pass
