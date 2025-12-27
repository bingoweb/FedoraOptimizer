"""
Fedora Optimizer - 2025 AI-Powered System Optimization Tool
Streamlined TUI with optional debug console
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

# Conditional debug imports - only if DEBUG_MODE env var is set
DEBUG_MODE = os.getenv('DEBUG_MODE', '0') == '1'
if DEBUG_MODE:
    try:
        from modules.debug_logger import (
            log_errors,
            log_menu_action,
            log_operation,
            log_warning,
            log_info,
            logger
        )
        print("[DEBUG MODE ENABLED - Logging to debug.log]")
    except ImportError:
        DEBUG_MODE = False
        print("[Debug logger not found - running without debug mode]")

from modules.optimizer import (
    FedoraOptimizer, 
    HardwareDetector,
    SysctlOptimizer, 
    IOSchedulerOptimizer, 
    OptimizationBackup,
    AIOptimizationEngine,
    TransactionManager
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
    
    VERSION = "0.4.0"
    
    def __init__(self):
        self.console = Console()
        self.theme = Theme()
        self.key_listener = KeyListener()
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

    def pause_and_run(self, live, task_func, menu_name="Unknown"):
        """Pause live display, run task with optional debug logging, resume"""
        live.stop()
        console.clear()
        
        # Log menu selection if debug mode
        if DEBUG_MODE:
            log_menu_action(menu_name.split()[0] if menu_name else "?", menu_name)
            log_operation(menu_name, "START")
        
        try:
            task_func()
            
            if DEBUG_MODE:
                log_operation(menu_name, "SUCCESS")
            
        except KeyboardInterrupt:
            if DEBUG_MODE:
                log_warning(f"{menu_name} - User cancelled")
            console.print("\n[yellow]İşlem iptal edildi.[/yellow]")
            
        except Exception as e:
            if DEBUG_MODE:
                log_operation(menu_name, "ERROR", str(e))
                logger.exception(f"Exception in {menu_name}")
            
            from modules.logger import log_exception
            log_exception(e)
            console.print(f"\n[red]❌ Hata: {type(e).__name__}[/red]")
            console.print(f"[red]Detay: {escape(str(e))}[/red]")
            
            if DEBUG_MODE:
                console.print(f"\n[yellow]💡 Debug console'da detayları gör (debug.log)[/yellow]")
        
        Prompt.ask("\n[bold]Devam etmek için Enter'a basın...[/bold]")
        live.start()

    def run_task(self, live, key):
        """Execute optimization task based on key"""
        if key == '1':
            self.pause_and_run(live, optimizer.full_audit, "1 - DERİN TARAMA")
        
        elif key == '2':
            def quick_optimize():
                optimizer.apply_dnf5_optimizations()
                optimizer.optimize_boot_profile()
            self.pause_and_run(live, quick_optimize, "2 - HIZLI OPTİMİZE")
        
        elif key == '3':
            self.pause_and_run(live, optimizer.optimize_full_auto, "3 - TAM OPTİMİZASYON")
        
        elif key == '4':
            self.pause_and_run(live, gaming_opt.optimize_gaming_profile, "4 - OYUN MODU")
        
        
        elif key == '5':
            def io_optimize():
                from rich.panel import Panel
                from rich import box
                console.print()
                console.print(Panel(
                    "[bold white]💾 I/O SCHEDULER OPTİMİZASYONU[/]",
                    border_style="cyan",
                    box=box.DOUBLE_EDGE
                ))
                console.print()
                
                persona, _ = optimizer.analyze_usage_persona()
                workload = "gaming" if persona == "Gamer" else "server" if persona == "Server" else "desktop"
                result = optimizer.io_opt.optimize_all_devices(workload)
                
                console.print(Panel(
                    f"[green]✅ I/O Scheduler Optimize Edildi![/]\n\n"
                    f"[white]• Profil: {workload}[/]\n"
                    f"[white]• Disk tipi: {optimizer.hw.get_simple_disk_type()}[/]",
                    border_style="green",
                    box=box.ROUNDED
                ))
            self.pause_and_run(live, io_optimize, "5 - I/O SCHEDULER")
        
        elif key == '6':
            def network_optimize():
                from rich.panel import Panel
                from rich import box
                console.print()
                console.print(Panel(
                    "[bold white]🌐 AĞ OPTİMİZASYONU[/]",
                    border_style="cyan",
                    box=box.DOUBLE_EDGE
                ))
                console.print()
                
                engine = AIOptimizationEngine(optimizer.hw)
                engine.analyze_and_propose_sysctl("general")
                
                # Filter network proposals
                net_proposals = [p for p in engine.proposals if p.category == "network"]
                if net_proposals:
                    engine.display_proposals()
                    if Confirm.ask("\n[yellow]Bu ağ optimizasyonlarını uygulansın mı?[/]"):
                        engine.apply_proposals(category="network")
                        console.print(Panel(f"[green]✅ {len(net_proposals)} ağ parametresi optimize edildi![/]", border_style="green"))
                else:
                    console.print(Panel("[green]✅ Ağ ayarları zaten optimal![/]", border_style="green"))
            self.pause_and_run(live, network_optimize, "6 - AĞ OPTİMİZE")
        
        elif key == '7':
            def kernel_optimize():
                from rich.panel import Panel
                from rich import box
                console.print()
                console.print(Panel(
                    "[bold white]⚙️  KERNEL PARAMETRELERİ[/]",
                    border_style="cyan",
                    box=box.DOUBLE_EDGE
                ))
                console.print()
                
                persona, _ = optimizer.analyze_usage_persona()
                engine = AIOptimizationEngine(optimizer.hw)
                engine.analyze_and_propose_sysctl(persona.lower() if persona != "General" else "general")
                
                if engine.proposals:
                    engine.display_proposals()
                    if Confirm.ask("\n[yellow]Bu kernel parametreleri uygulansın mı?[/]"):
                        engine.apply_proposals()
                        console.print(Panel(f"[green]✅ {len(engine.proposals)} kernel parametresi optimize edildi![/]", border_style="green"))
                else:
                    console.print(Panel("[green]✅ Kernel parametreleri zaten optimal![/]", border_style="green"))
            self.pause_and_run(live, kernel_optimize, "7 - KERNEL AYAR")

        
        elif key == '8':
            def show_rollback_menu():
                tm = TransactionManager()
                transactions = tm.get_all_transactions()
                
                if not transactions:
                    console.print("[yellow]Geri alınacak işlem yok.[/yellow]")
                    return
                
                console.print("\n[bold cyan]Geri Alınabilir İşlemler:[/]\n")
                for i, tx in enumerate(transactions, 1):
                    console.print(f"{i}. {tx['timestamp']} - {tx['type']}")
                
                choice = Prompt.ask("\nİşlem no", choices=[str(i) for i in range(1, len(transactions)+1)] + ["0"])
                if choice != "0":
                    tx_id = transactions[int(choice)-1]['uuid']
                    if Confirm.ask(f"[yellow]Bu işlemi geri almak istediğine emin misin?[/yellow]"):
                        tm.undo_transaction(tx_id)
                        console.print("[green]✓ İşlem geri alındı[/green]")
            
            self.pause_and_run(live, show_rollback_menu, "8 - GERİ AL")

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
