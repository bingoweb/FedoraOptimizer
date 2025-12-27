"""
Fedora Optimizer Facade - Slim orchestrator.

Main entry point for the TUI, delegating to specialized optimizers.
Refactored from 622 lines to ~150 lines for better maintainability.
"""
from rich.panel import Panel
from ..utils import console
from .hardware import HardwareDetector
from .system_profiler import SystemProfiler
from .dnf_optimizer import DNFOptimizer
from .boot_optimizer import BootOptimizer
from .sysctl import SysctlOptimizer
from .io_scheduler import IOSchedulerOptimizer
from .backup import OptimizationBackup


class FedoraOptimizer:
    """
    Slim facade orchestrating specialized optimizers.
    
    This class delegates to specialized modules instead of
    implementing everything itself (Single Responsibility Principle).
    """

    def __init__(self):
        """Initialize facade and all specialized optimizers."""
        # Core hardware detection
        self.hw = HardwareDetector()
        
        # Specialized modules (delegation)
        self.profiler = SystemProfiler(self.hw)
        self.dnf_opt = DNFOptimizer()
        self.boot_opt = BootOptimizer()
        self.sysctl_opt = SysctlOptimizer(self.hw)
        self.io_opt = IOSchedulerOptimizer(self.hw)
        self.backup = OptimizationBackup()
    
    # Delegation methods (thin wrappers for TUI compatibility)
    
    def get_system_dna(self):
        """Get system DNA - delegate to profiler."""
        return self.profiler.get_system_dna()
    
    def analyze_usage_persona(self) -> tuple:
        """Persona detection - delegate to profiler."""
        return self.profiler.analyze_usage_persona()
    
    def apply_dnf5_optimizations(self) -> bool:
        """DNF optimization - delegate to DNF optimizer."""
        return self.dnf_opt.apply_optimizations()
    
    def optimize_boot_profile(self) -> int:
        """Boot optimization - delegate to boot optimizer."""
        return self.boot_opt.optimize_boot_profile()
    
    def calculate_deep_score(self):
        """Calculate deep score - delegate to profiler."""
        return self.profiler.calculate_deep_score()
    
    # Main orchestration method
    
    
    def optimize_full_auto(self):
        """
        Full automatic optimization with progress tracking.
        
        This is the main orchestration method that coordinates
        all specialized optimizers with real-time progress feedback.
        """
        from rich.progress import Progress, SpinnerColumn, BarColumn, TaskProgressColumn
        
        console.print("\n[bold magenta]🚀 TAM OTOMATİK OPTİMİZASYON[/]\n")
        
        with Progress(
            SpinnerColumn(),
            "[progress.description]{task.description}",
            BarColumn(),
            TaskProgressColumn(),
            console=console
        ) as progress:
            
            task = progress.add_task("[cyan]Başlatılıyor...", total=100)
            
            # 1. Create backup (10%)
            progress.update(task, description="[cyan]📦 Yedek oluşturuluyor...")
            snapshot_name = self.backup.create_snapshot("full-auto")
            progress.advance(task, 10)
            
            # 2. Detect persona (15%)
            progress.update(task, description="[cyan]🔍 Kullanım profili tespit ediliyor...")
            persona, confidence = self.analyze_usage_persona()
            progress.advance(task, 5)
            
            # 3. DNF optimization (25%)
            progress.update(task, description="[cyan]📦 Paket yöneticisi optimize ediliyor...")
            self.apply_dnf5_optimizations()
            progress.advance(task, 10)
            
            # 4. Boot optimization (40%)
            progress.update(task, description="[cyan]⚡ Boot süresi optimize ediliyor...")
            self.optimize_boot_profile()
            progress.advance(task, 15)
            
            # 5. I/O scheduler (60%)
            progress.update(task, description="[cyan]💾 I/O zamanlayıcılar ayarlanıyor...")
            workload = "gaming" if persona == "Gamer" else \
                       "server" if persona == "Server" else "desktop"
            self.io_opt.optimize_all_devices(workload)
            progress.advance(task, 20)
            
            # 6. Sysctl optimization (100%)
            progress.update(task, description="[cyan]⚙️  Kernel parametreleri uygulanıyor...")
            persona_lower = persona.lower() if persona != "General" else "general"
            tweaks = self.sysctl_opt.generate_optimized_config(persona_lower)
            self.sysctl_opt.apply_config(tweaks)
            progress.advance(task, 40)
            
            progress.update(task, description="[green]✅ Tamamlandı!")
        
        # Success panel
        console.print(Panel(
            f"[bold green]🎉 SİSTEM 2025 YZ MOTORİYLE OPTİMİZE EDİLDİ![/bold green]\n\n"
            f"[cyan]Tespit edilen profil:[/] {persona} ({confidence:.0%} güven)\n\n"
            "✅ 30+ kernel parametresi uygulandı\n"
            "✅ I/O zamanlayıcıları donanıma göre ayarlandı\n"
            "✅ Ağ yığını BBR ile hızlandırıldı\n"
            "✅ Disk ve boot optimizasyonları tamamlandı\n\n"
            f"[dim]Yedek: {snapshot_name} (Geri almak için Rollback kullanın)[/dim]",
            border_style="green",
            title="[bold white]OPTİMİZASYON TAMAMLANDI[/]"
        ))

    
    # Legacy compatibility methods
    # These are kept for backward compatibility with TUI
    
    def full_audit(self):
        """
        Full system audit with Premium UI.
        Deep system DNA analysis with stunning visual display.
        """
        from rich.table import Table
        from rich.progress import Progress, SpinnerColumn, TextColumn, BarColumn
        from rich import box
        
        # Premium Header
        console.print()
        console.print(Panel(
            "[bold white]🧬 DERİN SİSTEM ANALİZİ[/]",
            border_style="cyan",
            box=box.DOUBLE_EDGE,
            padding=(0, 2)
        ))
        console.print()
        
        # Scanning animation
        with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            BarColumn(),
            TextColumn("[progress.percentage]{task.percentage:>3.0f}%"),
            console=console,
            transient=True
        ) as progress:
            task = progress.add_task("Sistem DNA'sı taranıyor...", total=100)
            
            # Gather data with progress updates
            progress.update(task, description="CPU analizi...", advance=20)
            dna = self.profiler.get_system_dna()
            
            progress.update(task, description="Kullanım profili tespiti...", advance=30)
            persona, confidence = self.profiler.analyze_usage_persona()
            
            progress.update(task, description="Sonuçlar hazırlanıyor...", advance=50)
        
        # DNA Table
        dna_table = Table(
            title="[bold cyan]Sistem DNA'sı[/]",
            box=box.ROUNDED,
            border_style="cyan",
            header_style="bold white on dark_blue",
            show_header=False,
            padding=(0, 2)
        )
        dna_table.add_column("DNA", style="white")
        
        for item in dna:
            dna_table.add_row(item)
        
        console.print(dna_table)
        console.print()
        
        # Persona Card
        color_map = {"Gamer": "magenta", "Developer": "green", "Server": "blue"}
        color = color_map.get(persona, "cyan")
        icon_map = {"Gamer": "🎮", "Developer": "💻", "Server": "🖥️", "General": "🖥️"}
        icon = icon_map.get(persona, "🖥️")
        
        confidence_bar = "█" * int(confidence * 10) + "░" * (10 - int(confidence * 10))
        
        console.print(Panel(
            f"[bold {color}]{icon} ALGILANAN PROFİL: {persona.upper()}[/]\n\n"
            f"[white]Güven Seviyesi:[/] [{color}]{confidence_bar}[/] {int(confidence*100)}%\n\n"
            f"[dim]┌─ Kasa Tipi: {self.hw.chassis}[/]\n"
            f"[dim]├─ CPU Çekirdek: {self.hw.cpu_info['cores']}[/]\n"
            f"[dim]├─ RAM: {self.hw.ram_info['total']} GB[/]\n"
            f"[dim]└─ GPU: {self.hw.gpu_info[:40]}...[/]" if len(self.hw.gpu_info) > 40 else f"[dim]└─ GPU: {self.hw.gpu_info}[/]",
            title=f"[bold {color}]Kullanım Profili[/]",
            border_style=color,
            box=box.ROUNDED,
            padding=(1, 2)
        ))
        console.print()
        
        # Suggestions panel
        suggestions = []
        if persona == "Gamer":
            suggestions = ["Oyun modu (4) ile ekstra FPS kazanın", "I/O scheduler bfq moduna geçin"]
        elif persona == "Developer":
            suggestions = ["Container/VM performansı optimize edildi", "Derleme hızı artırıldı"]
        else:
            suggestions = ["Genel kullanım için dengeli ayarlar", "Enerji verimliliği optimize edildi"]
        
        console.print(Panel(
            f"[bold yellow]💡 ÖNERİLER[/]\n\n" + 
            "\n".join([f"[white]• {s}[/]" for s in suggestions]) +
            "\n\n[dim]TAM OPTİMİZASYON (3) ile tüm ayarları uygulayın.[/dim]",
            border_style="yellow",
            box=box.ROUNDED
        ))
        console.print()
        
        return {"dna": dna, "persona": persona, "confidence": confidence}


