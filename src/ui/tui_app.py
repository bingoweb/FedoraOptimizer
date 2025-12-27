```
"""
Fedora Optimizer - Advanced Terminal UI
Modern TUI with comprehensive error logging
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

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

# Import debug logger for error tracking
from modules.debug_logger import (
    log_errors,
    log_menu_action, 
    log_operation,
    log_warning,
    logger
)

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

    def pause_and_run(self, task_func, menu_name="İşlem"):
        """
        Execute task with error handling and debug logging.
        Chrome DevTools benzeri error tracking.
        """
        console.clear()
        
        # Log menu selection
        menu_number = menu_name.split()[0] if menu_name else "Unknown"
        log_menu_action(menu_number, menu_name)
        
        try:
            log_operation(menu_name, "START")
            task_func()
            log_operation(menu_name, "SUCCESS")
            
        except KeyboardInterrupt:
            log_warning(f"{menu_name} - Kullanıcı tarafından iptal edildi")
            console.print("\n[yellow]İşlem iptal edildi.[/yellow]")
            
        except Exception as e:
            log_operation(menu_name, "ERROR")
            logger.exception(f"Unhandled exception in {menu_name}")
            
            console.print(f"\n[red]❌ Hata oluştu: {type(e).__name__}[/red]")
            console.print(f"[red]Detay: {str(e)}[/red]")
            console.print(f"\n[yellow]💡 Debug console'u kontrol edin (debug.log)[/yellow]")
        
        input("\n[dim]Devam etmek için Enter'a basın...[/dim]")

    def run_task(self, live, key):
        """Execute optimization task based on key"""
        live.stop() # Stop live display before running a task
        if key == '1':
            self.pause_and_run(live, optimizer.full_audit)
        
        elif key == '2':
            def quick_opt():
                console.print("[bold cyan]⚡ AI-Driven Hızlı Optimizasyon[/bold cyan]\n")
                console.print("[dim]🔍 Sistem taranıyor...[/dim]")
                
                # Use AI Engine
                ai_engine = AIOptimizationEngine(optimizer.hw)
                proposals = ai_engine.analyze_and_propose_sysctl()
                
                if not proposals:
                    console.print("\n[green]✓ Tüm ayarlar zaten optimal! Değişiklik gerekmez.[/green]")
                    return
                
                # Display proposals
                ai_engine.display_proposals()
                
                # Ask for confirmation
                if Confirm.ask("\n[bold yellow]Bu değişiklikleri uygulamak istiyor musunuz?[/bold yellow]"):
                    applied = ai_engine.apply_proposals(category="quick")
                    console.print(f"\n[green]✓ {len(applied)} değişiklik uygulandı![/green]")
                else:
                    console.print("\n[dim]İptal edildi. Değişiklik yapılmadı.[/dim]")
            self.pause_and_run(live, quick_opt)
        
        elif key == '3':
            self.pause_and_run(live, optimizer.optimize_full_auto)
        
        elif key == '4':
            self.pause_and_run(live, gaming_opt.gaming_menu)
        
        elif key == '5':
            def io_opt():
                console.print("[bold cyan]💾 AI I/O Zamanlayıcı Analizi[/bold cyan]\n")
                console.print("[dim]🔍 Disk cihazları taranıyor...[/dim]")
                
                ai_engine = AIOptimizationEngine(optimizer.hw)
                proposals = ai_engine.analyze_io_scheduler()
                
                if not proposals:
                    console.print("\n[green]✓ Tüm disk zamanlayıcıları optimal! Değişiklik gerekmez.[/green]")
                    return
                
                ai_engine.display_proposals()
                
                if Confirm.ask("\n[bold yellow]Bu zamanlayıcı değişikliklerini uygulamak istiyor musunuz?[/bold yellow]"):
                    applied = ai_engine.apply_proposals(category="io")
                    console.print(f"\n[green]✓ {len(applied)} disk zamanlayıcısı optimize edildi![/green]")
                else:
                    console.print("\n[dim]İptal edildi. Değişiklik yapılmadı.[/dim]")
            self.pause_and_run(live, io_opt)
        
        elif key == '6':
            def net_opt():
                console.print("[bold cyan]🌐 AI Ağ Optimizasyonu Analizi[/bold cyan]\n")
                console.print("[dim]🔍 Ağ parametreleri taranıyor...[/dim]")
                
                ai_engine = AIOptimizationEngine(optimizer.hw)
                proposals = ai_engine.analyze_network_only()
                
                if not proposals:
                    console.print("\n[green]✓ Ağ ayarları zaten optimal! (BBR aktif, buffer'lar yeterli)[/green]")
                    return
                
                ai_engine.display_proposals()
                
                if Confirm.ask("\n[bold yellow]Bu ağ optimizasyonlarını uygulamak istiyor musunuz?[/bold yellow]"):
                    applied = ai_engine.apply_proposals(category="network")
                    console.print(f"\n[green]✓ {len(applied)} ağ parametresi optimize edildi![/green]")
                else:
                    console.print("\n[dim]İptal edildi. Değişiklik yapılmadı.[/dim]")
            self.pause_and_run(live, net_opt)
        
        elif key == '7':
            def kernel_opt():
                console.print("[bold cyan]🔧 AI Kernel Parametreleri Analizi[/bold cyan]\n")
                console.print("[dim]🔍 Mevcut kernel ayarları taranıyor...[/dim]")
                
                # Use AI Engine for analysis
                ai_engine = AIOptimizationEngine(optimizer.hw)
                proposals = ai_engine.analyze_and_propose_sysctl()
                
                if not proposals:
                    console.print("\n[green]✓ Tüm kernel parametreleri optimal! Değişiklik gerekmez.[/green]")
                    
                    # Still show current state for info
                    persona, _ = optimizer.analyze_usage_persona()
                    console.print(f"\n[dim]Algılanan profil: {persona}[/dim]")
                    return
                
                # Display proposals with explanations
                ai_engine.display_proposals()
                
                # Ask for confirmation
                if Confirm.ask("\n[bold yellow]Bu kernel parametrelerini uygulamak istiyor musunuz?[/bold yellow]"):
                    applied = ai_engine.apply_proposals(category="kernel")
                    console.print(f"\n[green]✓ {len(applied)} kernel parametresi optimize edildi![/green]")
                    console.print("[dim]Değişiklikler kalıcı olarak /etc/sysctl.d/ altına kaydedildi.[/dim]")
                else:
                    console.print("\n[dim]İptal edildi. Hiçbir değişiklik yapılmadı.[/dim]")
            self.pause_and_run(live, kernel_opt)
        
        elif key == '8':
            def rollback():
                console.print("[bold cyan]↩️ GERİ AL MERKEZİ[/bold cyan]\n")
                
                tx_manager = TransactionManager()
                last_tx = tx_manager.get_last_transaction()
                
                # Menu options
                console.print("[bold]Seçenekler:[/bold]\n")
                
                if last_tx:
                    elapsed = ""
                    try:
                        from datetime import datetime
                        tx_time = datetime.fromisoformat(last_tx['timestamp'])
                        diff = datetime.now() - tx_time
                        if diff.seconds < 3600:
                            elapsed = f"{diff.seconds // 60} dk önce"
                        else:
                            elapsed = f"{diff.seconds // 3600} saat önce"
                    except:
                        elapsed = last_tx['timestamp'][:16]
                    
                    console.print(f"  [bold cyan]1.[/] SON İŞLEMİ GERİ AL")
                    console.print(f"     [dim]└─ {last_tx['description']} ({elapsed})[/dim]\n")
                else:
                    console.print(f"  [dim]1. Son işlem yok[/dim]\n")
                
                console.print(f"  [bold cyan]2.[/] İŞLEM GEÇMİŞİ")
                console.print(f"     [dim]└─ Tüm kayıtlı işlemleri gör[/dim]\n")
                
                console.print(f"  [bold cyan]3.[/] VARSAYILANLARA DÖN")
                console.print(f"     [dim]└─ Tüm optimizasyonları sıfırla[/dim]\n")
                
                console.print(f"  [dim]0. Geri[/dim]\n")
                
                choice = Prompt.ask("Seçiminiz", default="0")
                
                if choice == "1" and last_tx:
                    if Confirm.ask(f"'{last_tx['description']}' geri alınsın mı?"):
                        tx_manager.undo_last()
                
                elif choice == "2":
                    transactions = tx_manager.list_transactions(limit=10)
                    if not transactions:
                        console.print("\n[yellow]Henüz işlem geçmişi yok.[/yellow]")
                        return
                    
                    console.print("\n[bold]İşlem Geçmişi:[/bold]\n")
                    for i, tx in enumerate(transactions, 1):
                        console.print(f"  {i}. [{tx['id']}] {tx['description']}")
                        console.print(f"     [dim]{tx['timestamp'][:16]} - {len(tx['changes'])} değişiklik[/dim]")
                    
                    sel = Prompt.ask("\nGeri alınacak işlem numarası (0=iptal)", default="0")
                    try:
                        idx = int(sel) - 1
                        if 0 <= idx < len(transactions):
                            tx = transactions[idx]
                            if Confirm.ask(f"'{tx['description']}' geri alınsın mı?"):
                                tx_manager.undo_by_id(tx['id'])
                    except:
                        pass
                
                elif choice == "3":
                    console.print("\n[bold red]⚠️ UYARI:[/bold red] Tüm optimizasyonlar varsayılana dönecek!")
                    console.print("[dim]Bu işlem geri alınamaz.[/dim]\n")
                    if Confirm.ask("Devam etmek istiyor musunuz?"):
                        tx_manager.reset_to_defaults()
            
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
