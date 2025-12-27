"""
DNF/DNF5 package manager optimization.

Extracted from facade.py for better separation of concerns.
"""
import os
import re
from ..utils import run_command, console


class DNFOptimizer:
    """DNF5 configuration optimizer."""
    
    def __init__(self, config_path: str = "/etc/dnf/dnf5.conf"):
        """
        Initialize DNF optimizer.
        
        Args:
            config_path: Path to DNF config file
        """
        self.config_path = config_path
    
    def apply_optimizations(self) -> bool:
        """
        Apply DNF5 optimizations for faster package operations.
        
        Returns:
            bool: True if successful
        """
        if not os.path.exists(self.config_path):
            console.print(f"[yellow]⚠️  DNF config bulunamadı: {self.config_path}[/]")
            return False
        
        console.print("\n[bold cyan]📦 DNF5 Optimize Ediliyor...[/]\n")
        
        try:
            with open(self.config_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # Define optimizations
            optimizations = {
                "max_parallel_downloads": "10",
                "fastestmirror": "True",
                "deltarpm": "True"
            }
            
            changes = []
            for key, value in optimizations.items():
                pattern = rf'^{key}\s*=.*$'
                if re.search(pattern, content, re.MULTILINE):
                    # Update existing
                    content = re.sub(pattern, f"{key}={value}", content, flags=re.MULTILINE)
                    changes.append(f"Güncellendi: {key}={value}")
                else:
                    # Add new
                    content += f"\n{key}={value}\n"
                    changes.append(f"Eklendi: {key}={value}")
            
            # Write back
            with open(self.config_path, 'w', encoding='utf-8') as f:
                f.write(content)
            
            for change in changes:
                console.print(f"[green]✓[/] {change}")
            
            console.print(f"\n[green]✅ DNF5 başarıyla optimize edildi![/]\n")
            return True
            
        except Exception as e:
            console.print(f"[red]❌ DNF optimizasyonu başarısız: {e}[/]")
            return False
