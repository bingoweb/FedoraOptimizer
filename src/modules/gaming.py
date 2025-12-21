"""
Gaming Mode Optimizer - CachyOS/GameMode inspired optimizations
Part of FedoraClean Advanced AI Optimization Engine
"""

import os
import re
from .utils import run_command, console, Theme
from rich.panel import Panel
from rich.prompt import Prompt, Confirm


class GamingOptimizer:
    """Gaming-focused system optimization engine"""
    
    # Gaming-optimized kernel parameters
    GAMING_SYSCTL = {
        "vm.compaction_proactiveness": 50,
        "vm.page_lock_unfairness": 1,
        "vm.swappiness": 10,
        "kernel.sched_autogroup_enabled": 0,  # Disable for gaming
        "kernel.split_lock_detect": 0,  # Some games use split locks
    }
    
    def __init__(self, hw_detector=None):
        self.hw = hw_detector
        self.gamemode_installed = self._check_gamemode()
        self.bore_scheduler = self._check_bore_scheduler()
        self.compositor_status = None
        
    def _check_gamemode(self) -> bool:
        """Check if GameMode daemon is installed"""
        s, out, _ = run_command("which gamemoded")
        return s and out.strip() != ""
    
    def _check_bore_scheduler(self) -> bool:
        """Check if CachyOS BORE scheduler is available"""
        # BORE is part of EEVDF in newer kernels
        s, out, _ = run_command("cat /sys/kernel/sched_ext/state 2>/dev/null")
        if s and out.strip():
            return True
        
        # Check kernel version for BORE patches
        s, out, _ = run_command("uname -r")
        if s:
            kernel = out.strip().lower()
            return "cachyos" in kernel or "bore" in kernel
        return False
    
    def _check_compositor_status(self) -> dict:
        """Detect and check compositor status (KDE/GNOME)"""
        info = {
            "desktop": "Unknown",
            "compositor": "Unknown",
            "running": False,
            "can_disable": False
        }
        
        # Check for KDE
        s, out, _ = run_command("echo $XDG_CURRENT_DESKTOP")
        desktop = out.strip().upper()
        
        if "KDE" in desktop or "PLASMA" in desktop:
            info["desktop"] = "KDE Plasma"
            info["compositor"] = "KWin"
            # Check if running X11 (can disable) or Wayland (cannot easily disable)
            s, out, _ = run_command("echo $XDG_SESSION_TYPE")
            session = out.strip().lower()
            if session == "x11":
                info["can_disable"] = True
                # Check if compositor is enabled
                s, out, _ = run_command("qdbus org.kde.KWin /Compositor active 2>/dev/null")
                info["running"] = s and out.strip().lower() == "true"
            else:
                info["can_disable"] = False
                info["running"] = True  # Wayland requires compositor
        
        elif "GNOME" in desktop:
            info["desktop"] = "GNOME"
            info["compositor"] = "Mutter"
            info["can_disable"] = False  # Mutter cannot be disabled on GNOME
            info["running"] = True
        
        self.compositor_status = info
        return info
    
    def get_gaming_status(self) -> dict:
        """Get comprehensive gaming optimization status"""
        status = {
            "gamemode_installed": self.gamemode_installed,
            "gamemode_active": False,
            "bore_scheduler": self.bore_scheduler,
            "cpu_governor": "Unknown",
            "compositor": self._check_compositor_status(),
            "processes": []
        }
        
        # Check if GameMode is active
        if self.gamemode_installed:
            s, out, _ = run_command("gamemoded -s 2>/dev/null")
            status["gamemode_active"] = s and "active" in out.lower()
        
        # Check CPU governor
        s, out, _ = run_command("cat /sys/devices/system/cpu/cpu0/cpufreq/scaling_governor 2>/dev/null")
        if s:
            status["cpu_governor"] = out.strip()
        
        # Check for running games/game launchers
        game_processes = ["steam", "lutris", "heroic", "bottles", "wine", "proton"]
        s, out, _ = run_command("ps -eo comm")
        if s:
            procs = out.lower()
            for game in game_processes:
                if game in procs:
                    status["processes"].append(game)
        
        return status
    
    def apply_gaming_governor(self) -> bool:
        """Set CPU governor to performance"""
        console.print("[yellow]⚡ CPU Governor: Performance moduna geçiliyor...[/yellow]")
        
        # Check available governors
        s, out, _ = run_command("cat /sys/devices/system/cpu/cpu0/cpufreq/scaling_available_governors")
        if not s or "performance" not in out:
            console.print("[red]✗ Performance governor desteklenmiyor.[/red]")
            return False
        
        # Apply to all CPUs
        s, out, _ = run_command("ls /sys/devices/system/cpu/ | grep 'cpu[0-9]'")
        if s:
            cpus = out.strip().split('\n')
            for cpu in cpus:
                try:
                    with open(f"/sys/devices/system/cpu/{cpu}/cpufreq/scaling_governor", "w") as f:
                        f.write("performance")
                except:
                    pass
        
        console.print("[green]✓ Tüm CPU çekirdekleri Performance modunda.[/green]")
        return True
    
    def restore_balanced_governor(self) -> bool:
        """Restore CPU governor to balanced/powersave"""
        target = "schedutil"  # Default modern governor
        
        s, out, _ = run_command("cat /sys/devices/system/cpu/cpu0/cpufreq/scaling_available_governors")
        if s:
            if "schedutil" in out:
                target = "schedutil"
            elif "ondemand" in out:
                target = "ondemand"
            elif "powersave" in out:
                target = "powersave"
        
        s, out, _ = run_command("ls /sys/devices/system/cpu/ | grep 'cpu[0-9]'")
        if s:
            cpus = out.strip().split('\n')
            for cpu in cpus:
                try:
                    with open(f"/sys/devices/system/cpu/{cpu}/cpufreq/scaling_governor", "w") as f:
                        f.write(target)
                except:
                    pass
        
        console.print(f"[green]✓ CPU Governor '{target}' moduna geri döndü.[/green]")
        return True
    
    def toggle_kde_compositor(self, enable: bool) -> bool:
        """Enable/disable KDE compositor"""
        if not self.compositor_status:
            self._check_compositor_status()
        
        if self.compositor_status["desktop"] != "KDE Plasma":
            console.print("[yellow]⚠ Bu özellik sadece KDE Plasma masaüstünde çalışır.[/yellow]")
            return False
        
        if not self.compositor_status["can_disable"]:
            console.print("[yellow]⚠ Wayland oturumunda compositor kapatılamaz.[/yellow]")
            return False
        
        action = "resume" if enable else "suspend"
        s, _, _ = run_command(f"qdbus org.kde.KWin /Compositor {action}")
        
        if s:
            state = "açıldı" if enable else "kapatıldı"
            console.print(f"[green]✓ KWin Compositor {state}.[/green]")
            return True
        return False
    
    def apply_gaming_sysctl(self) -> list:
        """Apply gaming-optimized sysctl parameters"""
        console.print("[yellow]🎮 Gaming kernel parametreleri uygulanıyor...[/yellow]")
        
        applied = []
        for param, value in self.GAMING_SYSCTL.items():
            s, _, _ = run_command(f"sysctl -w {param}={value}", sudo=True)
            if s:
                applied.append(f"{param}={value}")
                console.print(f"  [green]✓[/] {param} = {value}")
        
        return applied
    
    def install_gamemode(self) -> bool:
        """Install GameMode if not present"""
        if self.gamemode_installed:
            console.print("[dim]GameMode zaten kurulu.[/dim]")
            return True
        
        if Confirm.ask("[bold]GameMode daemon kurulsun mu? (Oyun performansını artırır)[/bold]"):
            s, _, err = run_command("dnf5 install -y gamemode", sudo=True)
            if s:
                console.print("[green]✓ GameMode kuruldu.[/green]")
                console.print("[cyan]İpucu: Steam'de başlatma seçeneklerine 'gamemoderun %command%' ekleyin.[/cyan]")
                self.gamemode_installed = True
                return True
            else:
                console.print(f"[red]Kurulum hatası: {err}[/red]")
        return False
    
    def activate_gaming_mode(self) -> dict:
        """Activate full gaming mode"""
        results = {
            "governor": False,
            "compositor": False,
            "sysctl": [],
            "gamemode": False
        }
        
        console.print(Panel("[bold magenta]🎮 OYUN MODU AKTİVASYONU[/bold magenta]", border_style="magenta"))
        
        # 1. CPU Governor
        results["governor"] = self.apply_gaming_governor()
        
        # 2. Compositor (if KDE X11)
        comp_status = self._check_compositor_status()
        if comp_status["can_disable"] and comp_status["running"]:
            if Confirm.ask("[bold]KWin Compositor kapatılsın mı? (Latency düşer)[/bold]"):
                results["compositor"] = self.toggle_kde_compositor(False)
        
        # 3. Gaming sysctl
        results["sysctl"] = self.apply_gaming_sysctl()
        
        # 4. GameMode
        if self.gamemode_installed:
            s, _, _ = run_command("gamemoded -r")  # Request
            results["gamemode"] = s
            if s:
                console.print("[green]✓ GameMode daemon aktif.[/green]")
        
        console.print(Panel(
            "[bold green]🎮 OYUN MODU AKTİF![/bold green]\n"
            "[dim]Oyun bitince normal moda dönmek için tekrar bu menüyü kullanın.[/dim]",
            border_style="green"
        ))
        
        return results
    
    def deactivate_gaming_mode(self) -> bool:
        """Deactivate gaming mode and restore normal settings"""
        console.print(Panel("[bold yellow]🔄 NORMAL MODA DÖNÜLÜYOR[/bold yellow]", border_style="yellow"))
        
        # Restore governor
        self.restore_balanced_governor()
        
        # Enable compositor if applicable
        comp_status = self._check_compositor_status()
        if comp_status["desktop"] == "KDE Plasma" and comp_status["can_disable"]:
            self.toggle_kde_compositor(True)
        
        # Restore sysctl (via system defaults)
        run_command("sysctl -w vm.compaction_proactiveness=20", sudo=True)
        run_command("sysctl -w kernel.sched_autogroup_enabled=1", sudo=True)
        
        console.print("[green]✓ Normal mod geri yüklendi.[/green]")
        return True
    
    def gaming_menu(self):
        """Interactive gaming mode menu"""
        status = self.get_gaming_status()
        
        # Display current status
        status_text = f"""
[bold cyan]Mevcut Durum:[/bold cyan]
• GameMode Kurulu: {'[green]Evet[/]' if status['gamemode_installed'] else '[red]Hayır[/]'}
• GameMode Aktif: {'[green]Evet[/]' if status['gamemode_active'] else '[dim]Hayır[/]'}
• BORE Scheduler: {'[green]Tespit Edildi[/]' if status['bore_scheduler'] else '[dim]Standart Scheduler[/]'}
• CPU Governor: [yellow]{status['cpu_governor']}[/yellow]
• Masaüstü: {status['compositor']['desktop']}
• Compositor: {'[red]Kapalı[/]' if not status['compositor']['running'] else '[green]Çalışıyor[/]'}
• Aktif Oyun Süreçleri: {', '.join(status['processes']) if status['processes'] else '[dim]Yok[/]'}
"""
        console.print(Panel(status_text, title="[bold magenta]🎮 Oyun Modu Durumu[/bold magenta]", border_style="magenta"))
        
        console.print("""
[bold green]1.[/] Oyun Modunu Aktifleştir
[bold yellow]2.[/] Normal Moda Dön
[bold cyan]3.[/] GameMode Kur (dnf)
[bold dim]0.[/] Geri
""")
        
        choice = Prompt.ask("Seçim", choices=["0", "1", "2", "3"], default="0")
        
        if choice == "1":
            self.activate_gaming_mode()
        elif choice == "2":
            self.deactivate_gaming_mode()
        elif choice == "3":
            self.install_gamemode()
