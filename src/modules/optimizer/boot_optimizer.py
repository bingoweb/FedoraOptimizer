"""
Boot profile and systemd service optimization.

Extracted from facade.py for better separation of concerns.
"""
from ..utils import run_command, console


class BootOptimizer:
    """Boot time and systemd service optimizer."""
    
    def __init__(self):
        """Initialize boot optimizer."""
        self.slow_services = [
            "NetworkManager-wait-online.service",
            "systemd-networkd-wait-online.service",
            "plymouth-quit-wait.service"
        ]
    
    def optimize_boot_profile(self) -> int:
        """
        Optimize boot profile by disabling slow, non-essential services.
        
        Returns:
            int: Number of services disabled
        """
        disabled_count = 0
        
        console.print("\n[bold cyan]⚡ Boot Profili Optimize Ediliyor...[/]\n")
        
        for service in self.slow_services:
            # Check if service is enabled
            success, _, _ = run_command(
                f"systemctl is-enabled {service}",
                sudo=True
            )
            
            if success:
                # Disable slow service
                disable_success, _, _ = run_command(
                    f"systemctl disable {service}",
                    sudo=True
                )
                
                if disable_success:
                    console.print(f"[green]✓ Devre dışı:[/] {service}")
                    disabled_count += 1
                else:
                    console.print(f"[yellow]  ⚠️  Devre dışı bırakılamadı:[/] {service}")
        
        if disabled_count > 0:
            console.print(f"\n[green]✅ {disabled_count} servis devre dışı bırakıldı![/]\n")
        else:
            console.print("\n[dim]Tüm servisler zaten optimize edilmiş.[/]\n")
        
        return disabled_count
