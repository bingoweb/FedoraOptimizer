"""
Boot profile and systemd service optimization with Premium UI.
Professional, visually stunning output design.
"""
import logging
from rich.panel import Panel
from rich.table import Table
from rich.progress import Progress, SpinnerColumn, TextColumn, BarColumn
from rich import box
from ..utils import run_command, console


class BootOptimizer:
    """Boot time optimizer with premium UI."""
    
    SERVICE_INFO = {
        "NetworkManager-wait-online.service": {
            "icon": "🌐",
            "title": "Network Wait",
            "desc": "Ağ bekleme servisi",
            "impact": "5-15 sn"
        },
        "systemd-networkd-wait-online.service": {
            "icon": "📡",
            "title": "Networkd Wait",
            "desc": "systemd ağ bekleme",
            "impact": "3-10 sn"
        },
        "plymouth-quit-wait.service": {
            "icon": "🎨",
            "title": "Plymouth Wait",
            "desc": "Açılış animasyonu bekleme",
            "impact": "1-3 sn"
        }
    }
    
    def __init__(self):
        self.slow_services = list(self.SERVICE_INFO.keys())
        self.logger = logging.getLogger("FedoraOptimizerDebug")
    
    def _log(self, level, message):
        if self.logger:
            getattr(self.logger, level, self.logger.info)(message)
    
    def optimize_boot_profile(self) -> int:
        """Optimize boot profile with premium UI."""
        disabled_count = 0
        results = []
        
        self._log("info", "⚡ Boot profili optimizasyonu başlatılıyor...")
        
        # Header
        console.print()
        console.print(Panel(
            "[bold white]⚡ BOOT PROFİLİ OPTİMİZASYONU[/]",
            border_style="yellow",
            box=box.DOUBLE_EDGE,
            padding=(0, 2)
        ))
        console.print()
        
        console.print(
            Panel(
                "[dim]Yavaş başlangıç servislerini devre dışı bırakarak\n"
                "sistem açılış süresini önemli ölçüde kısaltır.[/]",
                border_style="dim",
                box=box.ROUNDED
            )
        )
        console.print()
        
        # Progress animation
        with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            BarColumn(),
            TextColumn("[progress.percentage]{task.percentage:>3.0f}%"),
            console=console,
            transient=True
        ) as progress:
            task = progress.add_task("Servisler analiz ediliyor...", total=len(self.slow_services))
            
            for service in self.slow_services:
                info = self.SERVICE_INFO[service]
                
                # Check status
                success, stdout, _ = run_command(
                    f"systemctl is-enabled {service}",
                    sudo=True
                )
                
                is_enabled = success and "enabled" in (stdout or "").lower()
                
                if is_enabled:
                    # Disable
                    disable_ok, _, _ = run_command(
                        f"systemctl disable {service}",
                        sudo=True
                    )
                    
                    if disable_ok:
                        results.append({
                            "service": service,
                            "info": info,
                            "status": "disabled",
                            "icon": "✅"
                        })
                        disabled_count += 1
                        self._log("info", f"✓ Devre dışı: {service}")
                    else:
                        results.append({
                            "service": service,
                            "info": info,
                            "status": "failed",
                            "icon": "⚠️"
                        })
                else:
                    results.append({
                        "service": service,
                        "info": info,
                        "status": "already",
                        "icon": "✔️"
                    })
                
                progress.update(task, advance=1)
        
        # Results table
        table = Table(
            title="[bold yellow]Servis Durumları[/]",
            box=box.ROUNDED,
            border_style="yellow",
            header_style="bold white on dark_orange",
            row_styles=["", "dim"]
        )
        table.add_column("", width=3)
        table.add_column("Servis", style="cyan", width=15)
        table.add_column("Açıklama", width=25)
        table.add_column("Kazanç", style="green", width=10, justify="center")
        table.add_column("Durum", width=15, justify="center")
        
        total_saved = 0
        for result in results:
            info = result["info"]
            
            # Parse impact
            impact = info["impact"]
            try:
                min_saved = int(impact.split("-")[0])
                total_saved += min_saved
            except:
                pass
            
            status_text = {
                "disabled": "[green]Devre Dışı ✓[/]",
                "already": "[dim]Zaten Devre Dışı[/]",
                "failed": "[yellow]Başarısız[/]"
            }.get(result["status"], "")
            
            table.add_row(
                info["icon"],
                info["title"],
                info["desc"],
                info["impact"],
                status_text
            )
        
        console.print(table)
        console.print()
        
        # Summary
        if disabled_count > 0:
            console.print(Panel(
                f"[bold green]✅ Boot Profili Optimize Edildi![/]\n\n"
                f"[white]• {disabled_count} servis devre dışı bırakıldı[/]\n"
                f"[white]• Tahmini kazanç: {total_saved}-{total_saved*2} saniye[/]\n"
                f"[white]• Bir sonraki açılışta etkili olacak[/]",
                border_style="green",
                box=box.ROUNDED
            ))
        else:
            console.print(Panel(
                f"[bold cyan]ℹ️  Zaten Optimize[/]\n\n"
                f"[white]Tüm yavaş servisler zaten devre dışı.[/]\n"
                f"[dim]Boot süreniz optimal durumda.[/]",
                border_style="cyan",
                box=box.ROUNDED
            ))
        
        console.print()
        self._log("info", f"✅ Boot optimizasyonu: {disabled_count} servis devre dışı")
        return disabled_count
    
    def get_boot_analysis(self) -> dict:
        """Analyze current boot time."""
        success, stdout, _ = run_command("systemd-analyze blame", sudo=False)
        
        if not success:
            return {"error": "Boot analizi yapılamadı"}
        
        lines = stdout.strip().split('\n')[:10] if stdout else []
        slow_services = []
        
        for line in lines:
            parts = line.split()
            if len(parts) >= 2:
                slow_services.append({
                    "service": parts[1],
                    "time": parts[0]
                })
        
        return {"slow_services": slow_services}
