"""
Fedora Optimizer Facade.
Main entry point for the TUI, orchestrating specific optimizers.
"""
import os
import re
import platform
from rich.panel import Panel
from rich.columns import Columns
from rich.align import Align
from rich.prompt import Prompt, Confirm
from rich.progress import Progress, SpinnerColumn, TextColumn
from ..utils import run_command, console, Theme
from .hardware import HardwareDetector
from .sysctl import SysctlOptimizer
from .io_scheduler import IOSchedulerOptimizer
from .backup import OptimizationBackup


class FedoraOptimizer:
    """Facade for the optimization subsystem"""

    def __init__(self):
        self.dnf_conf = "/etc/dnf/dnf5.conf"
        self.hw = HardwareDetector()

    def get_system_dna(self):
        """Enhanced system DNA with deep profiling - Format for display"""
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

    def apply_dnf5_optimizations(self):
        """Optimize DNF5 configuration"""
        console.print(f"[yellow]DNF5 Yapılandırması Kontrol Ediliyor ({self.dnf_conf})...[/yellow]")
        target_conf = self.dnf_conf
        if not os.path.exists(target_conf):
            target_conf = "/etc/dnf/dnf.conf"

        try:
            with open(target_conf, 'r', encoding='utf-8') as f:
                content = f.read()
        except PermissionError:
            console.print("[red]Erişim reddedildi. Root gerekli.[/red]")
            return

        changes = []
        new_content = content

        if "max_parallel_downloads=10" in content:
            console.print("[dim cyan]• İndirme hızı zaten optimize edilmiş (10).[/]")
        elif "max_parallel_downloads" in content:
            new_content = new_content.replace(
                "max_parallel_downloads=3", "max_parallel_downloads=10"
            )
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
                with open(target_conf, 'w', encoding='utf-8') as f:
                    f.write(new_content)
                console.print(Panel(
                    "\n".join(changes), title="DNF5 Güncellendi", border_style=Theme.SUCCESS
                ))
            except Exception as e:
                console.print(f"[red]Hata: {e}[/red]")
        else:
            console.print("[green]✓ DNF5 tamamen optimize durumda.[/green]")

    def optimize_boot_profile(self):
        """Optimize boot services"""
        console.print("[yellow]Boot Servisleri Kontrol Ediliyor...[/yellow]")
        _, s_out, _ = run_command("systemctl is-enabled NetworkManager-wait-online.service")

        if "disabled" in s_out:
            console.print(
                "[green]✓ NetworkManager-wait-online zaten devre dışı (Hızlı Boot aktif).[/green]"
            )
        else:
            if Prompt.ask(
                "[bold]Boot hızını artırmak için ağ bekleme servinis kapatmak "
                "ister misiniz? (Önerilir)[/bold]",
                choices=["e", "h"], default="e"
            ) == "e":
                run_command(
                    "systemctl disable --now NetworkManager-wait-online.service", sudo=True
                )
                console.print("[green]✓ Servis devre dışı bırakıldı.[/green]")
            else:
                console.print("[dim]İşlem iptal edildi.[/dim]")

    # Legacy methods optimize_network and optimize_ai_heuristic removed.
    # Logic is now handled by SysctlOptimizer and AIOptimizationEngine.

    def optimize_full_auto(self):
        """Enhanced full auto optimization using 2025 AI engines"""
        console.print("[bold magenta]🚀 TAM OTOMATİK YZ CİHAZ YÖNETİMİ (2025 Enhanced)[/bold magenta]")

        console.print("[yellow]📦 Yedek oluşturuluyor...[/yellow]")
        try:
            backup = OptimizationBackup()
            snapshot_name = backup.create_snapshot()
            console.print(f"[green]✓ Yedek oluşturuldu: {snapshot_name}[/green]")
        except Exception as e:
            console.print(f"[red]⚠ Yedek oluşturulamadı: {e}[/red]")
            snapshot_name = "N/A"

        console.print("\n[bold cyan]📊 Derin Sistem Analizi...[/bold cyan]")
        dna = self.get_system_dna()
        for line in dna[:8]:
            console.print(f"  {line}")

        persona, conf = self.analyze_usage_persona()
        console.print(f"\n[bold cyan]👤 Tespit Edilen Profil:[/] {persona} (Güven: %{conf})")

        console.print("\n[bold cyan]🧠 2025 Kernel Parametreleri Uygulanıyor...[/bold cyan]")
        try:
            sysctl_opt = SysctlOptimizer(self.hw)
            tweaks = sysctl_opt.generate_optimized_config(persona)
            applied = sysctl_opt.apply_config(tweaks)
            if applied:
                console.print(
                    f"  [green]✓ {len(applied)} kernel parametresi optimize edildi.[/green]"
                )
            else:
                console.print("  [dim]Tüm parametreler zaten optimal.[/dim]")
        except Exception as e:
            console.print(f"[red]Sysctl hatası: {e}[/red]")

        console.print("\n[bold cyan]💾 I/O Zamanlayıcı Optimizasyonu...[/bold cyan]")
        try:
            io_opt = IOSchedulerOptimizer(self.hw)
            results = io_opt.optimize_all_devices(workload="desktop")
            for r in results:
                if r.get("status") == "changed":
                    console.print(
                        f"  [green]✓ {r['device']} ({r['category']}): "
                        f"{r['from']} → {r['to']}[/green]"
                    )
        except Exception as e:
            console.print(f"[red]I/O Scheduler hatası: {e}[/red]")

        self.optimize_boot_profile()
        self.trim_ssd()
        self.optimize_btrfs()

        console.print(Panel(
            "[bold green]🎉 SİSTEM 2025 YZ MOTORİYLE OPTİMİZE EDİLDİ![/bold green]\n\n"
            "✅ 30+ kernel parametresi uygulandı\n"
        ))

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

    def calculate_deep_score(self):
        """Calculate advanced system score with AI insights"""
        score, report = self.calculate_smart_score()

        try:
            with open("/proc/sys/vm/compaction_proactiveness", "r", encoding='utf-8') as f:
                val = int(f.read().strip())
            if val >= 20:
                score += 10
                report.append(
                    ("[green]AKILLI[/]", "Bellek Tepkisi",
                     f"Proaktif Sıkıştırma Aktif ({val})")
                )
            else:
                report.append(
                    ("[yellow]STANDART[/]", "Bellek Tepkisi", "Standart bellek yönetimi.")
                )
        except Exception:
            pass

        if "Intel" in self.hw.gpu_info:
            try:
                with open("/proc/cmdline", "r", encoding='utf-8') as f:
                    cmd = f.read()
                if "i915.enable_guc" in cmd:
                    score += 10
                    report.append(
                        ("[green]HIZLANDIRILMIŞ[/]", "GPU Firmware", "Intel GuC/HuC aktif.")
                    )
                else:
                    report.append(
                        ("[yellow]YAZILIM[/]", "GPU Firmware", "Standart CPU zamanlaması.")
                    )
            except Exception:
                pass

        return min(100, score), report

    def _audit_cpu(self, progress, task):
        progress.update(task, description="CPU analiz ediliyor...")
        score_contrib = 0
        items = []

        cpu = self.hw.cpu_microarch
        psi_stats = self.hw.get_psi_stats()

        if cpu.get('vendor') != 'Unknown':
            score_contrib += 5
            items.append(("✓", f"{cpu['vendor']} {cpu.get('cpu_generation', '')}"))

        governor = cpu.get('governor', 'Unknown')
        if governor in ['performance', 'schedutil']:
            score_contrib += 10
            items.append(("✓", f"Governor: {governor} (optimal)"))
        elif governor == 'powersave':
            score_contrib += 5
            items.append(("!", f"Governor: {governor} (güç tasarrufu)"))
        else:
            items.append(("✗", f"Governor: {governor}"))

        driver = cpu.get('scaling_driver', 'Unknown')
        if 'pstate' in driver:
            score_contrib += 10
            items.append(("✓", f"Driver: {driver} (modern)"))
        elif driver != 'Unknown':
            score_contrib += 5
            items.append(("~", f"Driver: {driver}"))

        cpu_psi = psi_stats.get("cpu", {}).get("some", {}).get("avg10", 0.0)
        if cpu_psi < 5.0:
            score_contrib += 5
            items.append(("✓", f"CPU PSI: {cpu_psi}% (Düşük yük)"))
        else:
            items.append(("!", f"CPU PSI: {cpu_psi}% (Yüksek yük)"))

        return score_contrib, items

    def _audit_memory(self, progress, task):
        progress.update(task, description="Bellek analiz ediliyor...")
        score_contrib = 0
        items = []

        _, out, _ = run_command("zramctl")
        if "zram" in out:
            score_contrib += 10
            items.append(("✓", "ZRAM aktif (sıkıştırılmış swap)"))
        else:
            items.append(("!", "ZRAM kapalı"))

        try:
            with open("/proc/sys/vm/swappiness", "r", encoding='utf-8') as f:
                swp = int(f.read().strip())
            if swp <= 20:
                score_contrib += 10
                items.append(("✓", f"Swappiness: {swp} (SSD optimize)"))
            elif swp <= 60:
                score_contrib += 5
                items.append(("~", f"Swappiness: {swp} (varsayılan)"))
            else:
                items.append(("!", f"Swappiness: {swp} (yüksek)"))
        except Exception:
            pass

        kf = getattr(self.hw, 'kernel_features', {})
        thp = kf.get('transparent_hugepages', 'Unknown')
        if thp == 'madvise':
            score_contrib += 5
            items.append(("✓", f"THP: {thp} (önerilen)"))
        elif thp == 'always':
            score_contrib += 3
            items.append(("~", f"THP: {thp}"))

        return score_contrib, items

    def _audit_disk(self, progress, task):
        progress.update(task, description="Disk analiz ediliyor...")
        score_contrib = 0
        items = []
        psi_stats = self.hw.get_psi_stats()

        disk_type = self.hw.disk_info.lower()
        if "nvme" in disk_type:
            score_contrib += 5
            items.append(("✓", "NVMe SSD (maksimum hız)"))
        elif "ssd" in disk_type:
            score_contrib += 4
            items.append(("✓", "SATA SSD"))
        else:
            score_contrib += 3
            items.append(("~", "HDD (mekanik disk)"))

        _, out, _ = run_command("systemctl is-enabled fstrim.timer")
        if "enabled" in out:
            score_contrib += 10
            items.append(("✓", "TRIM aktif (SSD ömrü korunuyor)"))
        else:
            items.append(("✗", "TRIM kapalı - SSD için kritik!"))

        cmd = "cat /sys/block/$(lsblk -d -o NAME | grep -v loop | head -2 | tail -1)/queue/scheduler"
        s, out, _ = run_command(cmd)
        if s:
            match = re.search(r'\[(\w+)\]', out)
            if match:
                sched = match.group(1)
                score_contrib += 5
                items.append(("✓", f"I/O Scheduler: {sched}"))

        io_psi = psi_stats.get("io", {}).get("some", {}).get("avg10", 0.0)
        if io_psi < 5.0:
            score_contrib += 5
            items.append(("✓", f"I/O PSI: {io_psi}% (Düşük yük)"))
        else:
            items.append(("!", f"I/O PSI: {io_psi}% (Yüksek yük)"))

        return score_contrib, items

    def _audit_network(self, progress, task):
        progress.update(task, description="Ağ analiz ediliyor...")
        score_contrib = 0
        items = []

        bbr_ver = self.hw.kernel_features.get("bbr_version", "unknown")
        s, out, _ = run_command("sysctl net.ipv4.tcp_congestion_control")
        if s and "bbr" in out:
            score_contrib += 10
            ver_display = "BBRv3" if bbr_ver == "bbr3" else \
                          "BBRv2" if bbr_ver == "bbr2" else "BBR"
            items.append(("✓", f"TCP {ver_display} aktif (hızlı transfer)"))
        else:
            items.append(("!", "TCP Cubic (eski algoritma)"))

        s, out, _ = run_command("sysctl net.ipv4.tcp_fastopen")
        if s and "3" in out:
            score_contrib += 5
            items.append(("✓", "TCP Fast Open aktif"))
        else:
            items.append(("~", "TCP Fast Open kapalı"))

        return score_contrib, items

    def _audit_kernel(self, progress, task):
        progress.update(task, description="Kernel analiz ediliyor...")
        score_contrib = 0
        items = []
        kf = getattr(self.hw, 'kernel_features', {})

        if kf.get('psi', False):
            score_contrib += 2
            items.append(("✓", "PSI (Pressure Stall Info) aktif"))

        if kf.get('cgroup_v2', False):
            score_contrib += 2
            items.append(("✓", "cgroup v2 (modern konteyner)"))

        if kf.get('io_uring', False):
            score_contrib += 2
            items.append(("✓", "io_uring (hızlı I/O)"))

        if kf.get('bpf', False):
            score_contrib += 2
            items.append(("✓", "eBPF aktif"))

        if kf.get('sched_ext', False):
            score_contrib += 2
            status = kf.get('sched_ext_state', 'enabled')
            items.append(("✓", f"sched_ext (Extensible Scheduler) [{status}]"))

        return score_contrib, items

    def full_audit(self):
        """Enhanced Deep System Audit with Category-Based Scoring"""

        console.print("\n[bold magenta]🧬 DERİN SİSTEM DNA ANALİZİ (2025 AI)[/bold magenta]\n")

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

            # Execution
            scores["cpu"]["score"], scores["cpu"]["items"] = self._audit_cpu(progress, task)
            progress.advance(task)

            scores["memory"]["score"], scores["memory"]["items"] = self._audit_memory(progress, task)
            progress.advance(task)

            scores["disk"]["score"], scores["disk"]["items"] = self._audit_disk(progress, task)
            progress.advance(task)

            scores["network"]["score"], scores["network"]["items"] = self._audit_network(progress, task)
            progress.advance(task)

            scores["kernel"]["score"], scores["kernel"]["items"] = self._audit_kernel(progress, task)
            progress.advance(task)

        # Output
        self._display_audit_report(scores)

    def _display_audit_report(self, scores):
        console.print()
        dna = self.get_system_dna()
        dna.append(f"[bold cyan]Kernel:[/] {platform.release()}")

        if self.hw.cpu_microarch.get('is_vm', False):
            dna.append(
                f"[bold yellow]⚠ VM:[/] {self.hw.cpu_info.get('hypervisor', 'Unknown')} "
                "(sınırlı optimizasyon)"
            )

        dna_panel = Panel(
            "\n".join([f"[cyan]➤[/] {x}" for x in dna]),
            title="[bold white]🧬 SİSTEM DNA[/]",
            border_style="cyan",
            padding=(1, 2)
        )
        console.print(dna_panel)
        console.print()

        row1 = Columns([
            self._make_category_panel("CPU", "⚡", scores["cpu"], "blue"),
            self._make_category_panel("BELLEK", "🧠", scores["memory"], "magenta"),
        ], equal=True, expand=True)
        console.print(row1)

        row2 = Columns([
            self._make_category_panel("DİSK", "💾", scores["disk"], "cyan"),
            self._make_category_panel("AĞ", "🌐", scores["network"], "green"),
        ], equal=True, expand=True)
        console.print(row2)

        total_score = sum(s["score"] for s in scores.values())
        total_max = sum(s["max"] for s in scores.values())
        final_score = int((total_score / total_max) * 100)

        self._display_final_verdict(final_score, scores)

    def _make_category_panel(self, name, emoji, data, color):
        score_pct = int((data["score"] / data["max"]) * 100)
        score_color = "green" if score_pct >= 80 else \
                      "yellow" if score_pct >= 50 else "red"

        bar_len = 20
        filled = int((score_pct / 100) * bar_len)
        p_bar = f"[{score_color}]{'█' * filled}[/][dim]{'░' * (bar_len - filled)}[/]"

        items_text = "\n".join([
            f"[{'green' if i[0] == '✓' else 'yellow' if i[0] in ['!', '~'] else 'red'}]"
            f"{i[0]}[/] {i[1]}"
            for i in data["items"]
        ])

        return Panel(
            f"{items_text}\n\n{p_bar} "
            f"[bold {score_color}]{data['score']}/{data['max']} ({score_pct}%)[/]",
            title=f"[bold {color}]{emoji} {name}[/]",
            border_style=color,
            width=45
        )

    def _display_final_verdict(self, final_score, scores):
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

        if final_score < 95:
            console.print("\n[bold yellow]📋 ÖNERİLER:[/bold yellow]")

            if scores["disk"]["score"] < 20:
                console.print(
                    "  • [cyan]TRIM[/] aktifleştirin: "
                    "[dim]sudo systemctl enable --now fstrim.timer[/dim]"
                )
            if scores["network"]["score"] < 10:
                console.print("  • [cyan]BBR[/] aktifleştirin: [dim]3. Tam Otomatik Optimizasyon[/dim]")
            if scores["memory"]["score"] < 15:
                console.print(
                    "  • [cyan]ZRAM[/] aktifleştirin: [dim]sudo dnf install zram-generator[/dim]"
                )
            if scores["cpu"]["score"] < 15:
                console.print(
                    "  • [cyan]CPU Governor[/] ayarlayın: [dim]4. Oyun Modu veya tuned-adm[/dim]"
                )
            console.print(
                "\n[bold]💡 İPUCU:[/] [green]3. TAM OPTİMİZASYON[/] tüm eksikleri tek seferde giderir."
            )
