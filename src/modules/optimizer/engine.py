"""
AI Optimization Engine.
Core analysis logic, proposal generation, and optimization orchestration.
Refactored to use modular components (Scanner, ML Model).
"""
import logging
from typing import List, Dict
from rich.table import Table
from rich import box
from ..utils import run_command, console
from .hardware import HardwareDetector
from .models import OptimizationProposal
from .transaction import TransactionManager
from .backup import OptimizationBackup
from .scanner import SystemScanner
from .ml_logic import SmartOptimizerModel

logger = logging.getLogger("FedoraOptimizerDebug")

class AIOptimizationEngine:
    """
    AI-Driven Optimization Workflow Engine
    Coordinator for scanning, analysis (ML/Rule-based), and application.

    Pattern: SCAN → ML ANALYZE → PROPOSE → APPLY
    """

    REASONS = {
        "swappiness_nvme": "NVMe SSD tespit edildi. Düşük swappiness (5-10) disk yerine RAM kullanımını önceliklendirir.",
        "swappiness_ssd": "SATA SSD tespit edildi. Düşük swappiness (10-20) SSD ömrünü korur ve performansı artırır.",
        "swappiness_hdd": "HDD tespit edildi. Varsayılan swappiness (60) uygundur.",
        "bbr_enable": "TCP BBR algoritması, yüksek gecikmeli bağlantılarda %50'ye kadar hız artışı sağlar.",
        "fastopen": "TCP Fast Open, bağlantı kurulum süresini azaltır.",
        "scheduler_nvme": "NVMe için 'none' önerilir (Dahili kuyruk yönetimi).",
        "scheduler_ssd": "SATA SSD için 'mq-deadline' veya 'bfq' önerilir.",
        "scheduler_hdd": "HDD için 'bfq' scheduler önerilir.",
        "dirty_ratio": "Düşük dirty ratio, SSD performansını artırır (tazeleme sıklığı).",
        "trim_disabled": "TRIM aktif değil! SSD performansı için kritiktir.",
        "zram_disabled": "ZRAM kapalı. Sıkıştırılmış bellek kapasiteyi artırır.",
        "sched_latency": "Masaüstü/Gaming için düşük gecikmeli scheduler ayarları.",
        "server_perf": "Sunucu profili: Yüksek verim (throughput) odaklı ayarlar.",
        "workstation_heavy": "Workstation: Ağır yükler için optimize edilmiş bellek yönetimi."
    }

    def __init__(self, hw_detector: 'HardwareDetector'):
        self.hw = hw_detector
        self.scanner = SystemScanner(hw_detector)
        self.ml_model = SmartOptimizerModel()
        self.proposals: List[OptimizationProposal] = []
        self.current_profile = "General"

    def analyze_and_propose_sysctl(self, persona: str = "general") -> List[OptimizationProposal]:
        """
        Orchestrates the analysis process:
        1. Scan System State
        2. Predict Profile via ML
        3. Generate Proposals based on Profile + Hardware
        """
        self.proposals = []

        # 1. Scan
        state = self.scanner.scan_full_state()
        disk_type = state["disk_type"]

        # 2. AI Profile Prediction
        features = {
            "ram_gb": state["ram_total_gb"],
            "cpu_cores": state["cpu_cores"],
            "is_laptop": state["chassis"] in ["laptop", "notebook"],
            "has_nvme": disk_type == "nvme",
            "has_gpu": "NVIDIA" in self.hw.gpu_info or "AMD" in self.hw.gpu_info # Simple check
        }

        # Use ML prediction, but allow manual override via 'persona' arg if it's not 'general'
        predicted_profile = self.ml_model.predict_profile(features)

        if persona != "general":
            self.current_profile = persona
            logger.info(f"Using Manual Profile: {persona} (Overrides ML: {predicted_profile})")
        else:
            self.current_profile = predicted_profile
            logger.info(f"Using ML Profile: {self.current_profile}")

        console.print(f"[dim]🧠 AI Profil Tahmini: [bold cyan]{self.current_profile}[/bold cyan][/dim]")

        # 3. Parameter Scanning
        params_to_check = [
            "vm.swappiness", "vm.dirty_ratio", "vm.dirty_writeback_centisecs",
            "vm.max_map_count", "net.ipv4.tcp_congestion_control",
            "net.ipv4.tcp_fastopen", "net.core.rmem_max", "net.core.wmem_max",
            "net.core.netdev_max_backlog", "kernel.sched_autogroup_enabled",
            "kernel.sched_cfs_bandwidth_slice_us", "kernel.sched_itmt_enabled",
            "fs.inotify.max_user_watches",
        ]
        current_values = self.scanner.scan_sysctl_values(params_to_check)

        # 4. Generate Rules
        self._apply_base_rules(current_values, disk_type)
        self._apply_network_rules(current_values)
        self._apply_storage_rules(state, disk_type)
        self._apply_profile_rules(current_values, self.current_profile)
        self._apply_hardware_rules(state, current_values)

        return self.proposals

    def _apply_base_rules(self, current_values, disk_type):
        """Standard rules for all profiles"""
        # Swappiness
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
                param="vm.swappiness", current=current_swp, proposed=optimal,
                reason=reason, category="memory", priority="recommended"
            ))

        # Dirty Ratio (Disk write caching)
        if disk_type in ["nvme", "ssd"]:
            current_dirty = current_values.get("vm.dirty_ratio", "20")
            optimal_dirty = "5" if disk_type == "nvme" else "10"
            try:
                if current_dirty != "N/A" and int(current_dirty) > int(optimal_dirty):
                    self.proposals.append(OptimizationProposal(
                        param="vm.dirty_ratio", current=current_dirty, proposed=optimal_dirty,
                        reason=self.REASONS["dirty_ratio"], category="memory", priority="recommended"
                    ))
            except ValueError:
                pass

    def _apply_network_rules(self, current_values):
        """Universal network improvements"""
        current_cc = current_values.get("net.ipv4.tcp_congestion_control", "cubic")
        if "bbr" not in current_cc.lower():
            self.proposals.append(OptimizationProposal(
                param="net.ipv4.tcp_congestion_control", current=current_cc, proposed="bbr",
                reason=self.REASONS["bbr_enable"], category="network", priority="recommended"
            ))

        current_tfo = current_values.get("net.ipv4.tcp_fastopen", "1")
        if current_tfo != "3":
            self.proposals.append(OptimizationProposal(
                param="net.ipv4.tcp_fastopen", current=current_tfo, proposed="3",
                reason=self.REASONS["fastopen"], category="network", priority="optional"
            ))

    def _apply_storage_rules(self, state, disk_type):
        """TRIM and ZRAM"""
        if disk_type in ["nvme", "ssd"] and not state["trim_active"]:
            self.proposals.append(OptimizationProposal(
                param="fstrim.timer", current="disabled", proposed="enabled",
                reason=self.REASONS["trim_disabled"], category="disk", priority="critical",
                command="systemctl enable --now fstrim.timer"
            ))

        if not state["zram_active"]:
            s, _, _ = run_command("rpm -q zram-generator || dnf info zram-generator >/dev/null")
            if s:
                self.proposals.append(OptimizationProposal(
                    param="ZRAM", current="disabled", proposed="enabled",
                    reason=self.REASONS["zram_disabled"], category="memory", priority="optional",
                    command="dnf install -y zram-generator && systemctl enable --now zram-generator"
                ))

    def _apply_profile_rules(self, current_values, profile: str):
        """Rules based on ML-Predicted Profile"""

        # GAMING
        if profile == "Gaming":
            curr_map = current_values.get("vm.max_map_count", "65530")
            if curr_map.isdigit() and int(curr_map) < 1000000:
                self.proposals.append(OptimizationProposal(
                    param="vm.max_map_count", current=curr_map, proposed="2147483642",
                    reason="[GAMER] Steam oyunları için kritik bellek harita limiti.",
                    category="gaming", priority="critical"
                ))

            curr_slice = current_values.get("kernel.sched_cfs_bandwidth_slice_us", "5000")
            if curr_slice != "3000":
                self.proposals.append(OptimizationProposal(
                    param="kernel.sched_cfs_bandwidth_slice_us", current=curr_slice, proposed="3000",
                    reason="[GAMER] CPU zamanlayıcı gecikmesini düşürür.",
                    category="gaming", priority="recommended"
                ))

        # WORKSTATION / DEVELOPER
        if profile in ["Workstation", "Developer"]:
            curr_watch = current_values.get("fs.inotify.max_user_watches", "8192")
            if curr_watch.isdigit() and int(curr_watch) < 524288:
                self.proposals.append(OptimizationProposal(
                    param="fs.inotify.max_user_watches", current=curr_watch, proposed="524288",
                    reason="[WORKSTATION] IDE ve Docker için dosya izleme limitini artırır.",
                    category="system", priority="recommended"
                ))

        # SERVER
        if profile == "Server":
             # Optimization for throughput over latency
             pass # Add specific server rules if needed

    def _apply_hardware_rules(self, state, current_values):
        """Hardware specific quirks (Laptop, Intel Hybrid, GPU)"""
        if state["chassis"] in ["notebook", "laptop"]:
            curr_wb = current_values.get("vm.dirty_writeback_centisecs", "500")
            if curr_wb != "6000":
                self.proposals.append(OptimizationProposal(
                    param="vm.dirty_writeback_centisecs", current=curr_wb, proposed="6000",
                    reason="[LAPTOP] Pil ömrü için diski daha az sık uyandırır.",
                    category="power", priority="recommended"
                ))

        if state.get("cpu_hybrid", False):
            curr_itmt = current_values.get("kernel.sched_itmt_enabled", "N/A")
            if curr_itmt != "N/A" and curr_itmt != "1":
                self.proposals.append(OptimizationProposal(
                    param="kernel.sched_itmt_enabled", current=curr_itmt, proposed="1",
                    reason="[INTEL HYBRID] Thread Director (ITMT) aktivasyonu.",
                    category="cpu", priority="critical"
                ))
        
        # Buffer sizes for everyone, but higher priority for some
        current_rmem = current_values.get("net.core.rmem_max", "0")
        if current_rmem != "N/A":
            try:
                if int(current_rmem) < 16777216:
                    self.proposals.append(OptimizationProposal(
                        param="net.core.rmem_max", current=current_rmem, proposed="16777216",
                        reason="Ağ alım buffer'ını 16MB'a yükseltir.",
                        category="network", priority="recommended"
                    ))
            except ValueError:
                pass
        
        current_wmem = current_values.get("net.core.wmem_max", "0")
        if current_wmem != "N/A":
            try:
                if int(current_wmem) < 16777216:
                    self.proposals.append(OptimizationProposal(
                        param="net.core.wmem_max", current=current_wmem, proposed="16777216",
                        reason="Ağ gönderim buffer'ını 16MB'a yükseltir.",
                        category="network", priority="recommended"
                    ))
            except ValueError:
                pass

    def display_proposals(self) -> None:
        """Display proposals in a formatted table with explanations"""
        if not self.proposals:
            console.print("[green]✓ Tüm ayarlar zaten optimal![/green]")
            return

        categories = {}
        for p in self.proposals:
            categories.setdefault(p.category, []).append(p)

        console.print(f"\n[bold cyan]🧠 AI OPTİMİZASYON ÖNERİLERİ ({self.current_profile})[/bold cyan]\n")

        for cat, proposals in categories.items():
            console.print(f"[bold]{cat.title()}[/bold]")

            table = Table(box=box.ROUNDED, padding=(0, 1), expand=True)
            table.add_column("Parametre", style="cyan", width=28)
            table.add_column("Mevcut", style="red", width=10)
            table.add_column("Önerilen", style="green", width=10)
            table.add_column("Öncelik", width=10)
            table.add_column("Açıklama", style="dim white")

            for p in proposals:
                prio_text = "🔴" if p.priority == "critical" else \
                            "🟡" if p.priority == "recommended" else "⚪"
                table.add_row(p.param, p.current, p.proposed, prio_text, p.reason)

            console.print(table)
            console.print()

    def apply_proposals(self, backup_first: bool = True, category: str = "general") -> List[str]:
        """Apply approved proposals and return list of applied changes"""
        logger.info("="*60)
        logger.info(f"📦 APPLY_PROPOSALS STARTED - Category: {category}")
        
        applied = []
        changes_for_tx = []

        if backup_first:
            try:
                OptimizationBackup().create_snapshot()
                console.print("[green]✓ Yedek oluşturuldu.[/green]")
            except Exception as e:
                logger.warning(f"Backup failed: {e}")

        for i, p in enumerate(self.proposals, 1):
            logger.info(f"Applying {p.param} ({p.current} -> {p.proposed})")
            
            try:
                success = False
                if p.command:
                    s, _, _ = run_command(p.command, sudo=True)
                    success = s
                else:
                    cmd = f"sysctl -w {p.param}={p.proposed}"
                    s, _, _ = run_command(cmd, sudo=True)
                    success = s
                    
                    # Verification
                    _, verify_out, _ = run_command(f"sysctl -n {p.param}", sudo=True)
                    if verify_out and verify_out.strip() == p.proposed:
                        logger.info("   Verification Passed")
                    else:
                        logger.warning(f"   Verification Failed! Got {verify_out.strip() if verify_out else 'None'}")
                        success = False

                if success:
                    applied.append(f"{p.param}: {p.current} → {p.proposed}")
                    changes_for_tx.append({"param": p.param, "old": p.current, "new": p.proposed})
                    console.print(f"[green]✓ {p.param} uygulandı[/green]")
                else:
                    console.print(f"[red]✗ {p.param} uygulanamadı[/red]")

            except Exception as e:
                console.print(f"[red]Hata: {e}[/red]")
                logger.error(f"Error applying {p.param}: {e}")

        if changes_for_tx:
            try:
                tm = TransactionManager()
                desc = f"{category.title()} Optimize - {len(changes_for_tx)} items"
                tm.record_transaction(category, desc, changes_for_tx)
            except Exception as e:
                logger.warning(f"Transaction recording failed: {e}")

        if applied:
            self._persist_sysctl_changes()
        
        logger.info(f"📦 Applied {len(applied)} changes.")
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
                with open(conf_file, "a", encoding='utf-8') as f:
                    f.write("\n" + "\n".join(lines) + "\n")
            except Exception:
                pass
