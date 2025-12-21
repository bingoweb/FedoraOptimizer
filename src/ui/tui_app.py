"""
Fedora Optimizer - 2025 AI-Powered System Optimization Tool
Streamlined TUI focused solely on optimization
"""

import sys
import os
import time
from rich.console import Console
from rich.layout import Layout
from rich.live import Live
from rich.panel import Panel
from rich.text import Text
from rich.table import Table
from rich import box
from rich.prompt import Prompt, Confirm
from rich.markup import escape
from rich.align import Align

# Path fix
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from modules.optimizer import (
    FedoraOptimizer, 
    HardwareDetector,
    SysctlOptimizer, 
    IOSchedulerOptimizer, 
    OptimizationBackup
)
from modules.gaming import GamingOptimizer
from modules.logger import log_info, log_exception, get_log_path
from modules.utils import Theme, console
from ui.dashboard import dashboard_ui
from ui.input_helper import KeyListener

# Global instances
optimizer = FedoraOptimizer()
gaming_opt = GamingOptimizer(optimizer.hw)


class OptimizerApp:
    """Streamlined Optimization-Only TUI Application"""
    
    def __init__(self):
        self.layout = Layout()
        self.message = f"[bold {Theme.PRIMARY}]KOMUT:[/] [white]1-9[/] Seçenekler - [white]0[/] Çıkış"
        
        # Auto-Resize terminal
        sys.stdout.write("\x1b[8;38;120t")
        sys.stdout.flush()
        
        # Init CPU percent
        import psutil
        psutil.cpu_percent(interval=None)

    def make_layout(self):
        """Create the main layout"""
        self.layout.split(
            Layout(name="header", size=3),
            Layout(name="main", ratio=1),
            Layout(name="footer", size=3)
        )
        self.layout["main"].split_row(
            Layout(name="sidebar", ratio=1, minimum_size=30),
            Layout(name="body", ratio=3),
        )
        return self.layout

    def get_sidebar(self):
        """Render optimization menu"""
        menu_items = [
            ("1", "🔍 DERİN TARAMA", "Sistem DNA analizi"),
            ("2", "⚡ HIZLI OPTİMİZE", "Temel optimizasyonlar"),
            ("3", "🚀 TAM OPTİMİZASYON", "Tüm AI özellikleri"),
            ("4", "🎮 OYUN MODU", "Gaming optimizasyonu"),
            ("5", "💾 I/O SCHEDULER", "Disk zamanlayıcı"),
            ("6", "🌐 AĞ OPTİMİZE", "TCP/BBR ayarları"),
            ("7", "🔧 KERNEL AYAR", "Sysctl parametreleri"),
            ("8", "↩️ GERİ AL", "Rollback"),
            ("", "", ""),
            ("0", "❌ ÇIKIŞ", ""),
        ]
        
        table = Table(box=None, expand=True, show_header=False, padding=(0, 1))
        table.add_column("Key", width=3)
        table.add_column("Name", width=18)
        table.add_column("Desc", style="dim")
        
        for key, name, desc in menu_items:
            if key == "":
                table.add_row("", "", "")
            else:
                style = f"bold {Theme.PRIMARY}" if key in ["3", "4"] else "white"
                table.add_row(f"[{style}]{key}[/]", f"[{style}]{name}[/]", desc)
        
        return Panel(
            Align.center(table, vertical="middle"),
            title=f"[bold {Theme.TEXT}] OPTİMİZASYON MENÜSÜ [/]",
            border_style=Theme.PRIMARY,
            box=box.ROUNDED,
            padding=(1, 1)
        )

    def get_body(self):
        """Render main body with system overview"""
        # Create a grid layout for the body
        body_layout = Layout()
        body_layout.split_column(
            Layout(name="top", ratio=1),
            Layout(name="bottom", ratio=1)
        )
        body_layout["top"].split_row(
            Layout(dashboard_ui.get_device_info(), ratio=1),
            Layout(dashboard_ui.get_system_overview(), ratio=1)
        )
        body_layout["bottom"].split_row(
            Layout(dashboard_ui.get_process_panel(), ratio=1),
            Layout(dashboard_ui.get_network_panel(), ratio=1)
        )
        return body_layout

    def get_header(self):
        """Application header"""
        from datetime import datetime
        grid = Table.grid(expand=True)
        grid.add_column(justify="left", ratio=1)
        grid.add_column(justify="center", ratio=2)
        grid.add_column(justify="right", ratio=1)
        grid.add_row(
            f"[bold {Theme.PRIMARY}]FEDORA[/] [bold white]OPTİMİZER[/]",
            f"[dim]2025 AI-Powered System Optimization[/]",
            f"[{Theme.SUCCESS}]{datetime.now().strftime('%H:%M:%S')}[/]"
        )
        return Panel(grid, style=f"{Theme.PRIMARY} on #1a1a2e", box=box.ROUNDED)

    def get_footer(self):
        """Footer with controls"""
        return Panel(
            Text.from_markup(self.message),
            border_style=Theme.BORDER,
            box=box.ROUNDED,
            padding=(0, 1)
        )

    def pause_and_run(self, live, task_func):
        """Pause live display, run task, resume"""
        live.stop()
        console.clear()
        try:
            task_func()
        except Exception as e:
            log_exception(e)
            console.print(f"[red]Hata: {escape(str(e))}[/red]")
        
        Prompt.ask("\n[bold]Devam etmek için Enter'a basın...[/bold]")
        live.start()

    def run_task(self, live, key):
        """Execute optimization task based on key"""
        if key == '1':
            self.pause_and_run(live, optimizer.full_audit)
        
        elif key == '2':
            def quick_opt():
                console.print("[bold cyan]⚡ Hızlı Optimizasyon...[/bold cyan]\n")
                optimizer.apply_dnf5_optimizations()
                optimizer.optimize_boot_profile()
                optimizer.trim_ssd()
                console.print("\n[green]✓ Hızlı optimizasyon tamamlandı![/green]")
            self.pause_and_run(live, quick_opt)
        
        elif key == '3':
            self.pause_and_run(live, optimizer.optimize_full_auto)
        
        elif key == '4':
            self.pause_and_run(live, gaming_opt.gaming_menu)
        
        elif key == '5':
            def io_opt():
                console.print("[bold cyan]💾 I/O Zamanlayıcı Optimizasyonu...[/bold cyan]\n")
                io_optimizer = IOSchedulerOptimizer(optimizer.hw)
                results = io_optimizer.optimize_all_devices()
                for r in results:
                    if r.get('status') == 'changed':
                        console.print(f"[green]✓ {r['device']} ({r['category']}): {r['from']} → {r['to']}[/green]")
                    else:
                        console.print(f"[dim]• {r['device']}: {r.get('scheduler', 'N/A')} (optimal)[/dim]")
            self.pause_and_run(live, io_opt)
        
        elif key == '6':
            self.pause_and_run(live, optimizer.optimize_network)
        
        elif key == '7':
            def kernel_opt():
                console.print("[bold cyan]🔧 Kernel Parametreleri Uygulanıyor...[/bold cyan]\n")
                persona, _ = optimizer.analyze_usage_persona()
                sysctl_opt = SysctlOptimizer(optimizer.hw)
                tweaks = sysctl_opt.generate_optimized_config(persona)
                applied = sysctl_opt.apply_config(tweaks)
                if applied:
                    console.print(f"\n[green]✓ {len(applied)} parametre optimize edildi.[/green]")
                    for key, val in applied[:10]:
                        console.print(f"  • {key} = {val}")
                else:
                    console.print("[dim]Tüm parametreler zaten optimal.[/dim]")
            self.pause_and_run(live, kernel_opt)
        
        elif key == '8':
            def rollback():
                backup = OptimizationBackup()
                snapshots = backup.list_snapshots()
                if not snapshots:
                    console.print("[yellow]Henüz yedek yok.[/yellow]")
                    return
                console.print("[bold]Mevcut Yedekler:[/bold]\n")
                for i, s in enumerate(snapshots, 1):
                    console.print(f"  {i}. {s['name']} ({s['created']})")
                choice = Prompt.ask("\nGeri yüklenecek yedek numarası", default="1")
                try:
                    idx = int(choice) - 1
                    if 0 <= idx < len(snapshots):
                        if Confirm.ask(f"'{snapshots[idx]['name']}' geri yüklensin mi?"):
                            backup.restore_snapshot(snapshots[idx]['name'])
                except:
                    console.print("[red]Geçersiz seçim.[/red]")
            self.pause_and_run(live, rollback)

    def run(self):
        """Main application loop"""
        self.make_layout()
        
        try:
            with KeyListener() as listener:
                with Live(self.layout, refresh_per_second=4, screen=True) as live:
                    while True:
                        # Update UI
                        self.layout["header"].update(self.get_header())
                        self.layout["sidebar"].update(self.get_sidebar())
                        self.layout["body"].update(self.get_body())
                        self.layout["footer"].update(self.get_footer())
                        
                        # Handle input
                        key = listener.get_key()
                        
                        if key:
                            if key == '0':
                                break
                            elif key in ['1', '2', '3', '4', '5', '6', '7', '8']:
                                listener.stop()
                                self.run_task(live, key)
                                listener.start()
                        
                        time.sleep(0.05)
                        
        except Exception as e:
            log_exception(e)
            console.print(f"[red]Uygulama Hatası: {escape(str(e))}[/red]")
            raise


def main():
    """Entry point"""
    if os.geteuid() != 0:
        console.print("[bold red]Bu uygulama root yetkisi gerektirir![/bold red]")
        console.print("[dim]Kullanım: sudo ./run.sh[/dim]")
        sys.exit(1)
    
    try:
        app = OptimizerApp()
        app.run()
    except KeyboardInterrupt:
        pass
    except Exception as e:
        console.clear()
        log_exception(e)
        console.print(f"[red]Kritik Hata: {e}[/red]")
        sys.exit(1)


if __name__ == "__main__":
    main()
