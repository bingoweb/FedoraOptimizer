"""
Backup and rollback system.
Manages configuration snapshots and restoration.
"""
import os
import shutil
import platform
from datetime import datetime
from ..utils import run_command, console

import logging

logger = logging.getLogger("FedoraOptimizerDebug")

class OptimizationBackup:
    """Backup and restore system for optimization rollback"""

    BACKUP_DIR = "/var/lib/fedoraclean/backups"

    def __init__(self):
        os.makedirs(self.BACKUP_DIR, exist_ok=True)

    def create_snapshot(self, name: str = None) -> str:
        """Create a backup snapshot of current optimization configs"""


        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        snapshot_name = name or f"snapshot_{timestamp}"
        snapshot_dir = os.path.join(self.BACKUP_DIR, snapshot_name)

        os.makedirs(snapshot_dir, exist_ok=True)

        # Files to backup
        backup_files = [
            "/etc/sysctl.d/99-fedoraclean-ai.conf",
            "/etc/sysctl.d/99-fedoraclean-net.conf",
            "/etc/dnf/dnf5.conf",
            "/etc/dnf/dnf.conf",
            "/etc/fstab",
        ]

        for src in backup_files:
            if os.path.exists(src):
                dst = os.path.join(snapshot_dir, os.path.basename(src))
                try:
                    shutil.copy2(src, dst)
                except Exception as e:
                    logger.warning(f"Backup copy failed for {src}: {e}")

        # Save current sysctl values
        s, out, _ = run_command("sysctl -a 2>/dev/null")
        if s:
            with open(os.path.join(snapshot_dir, "sysctl_dump.txt"), "w", encoding="utf-8") as f:
                f.write(out)

        # Save metadata
        with open(os.path.join(snapshot_dir, "metadata.txt"), "w", encoding="utf-8") as f:
            f.write(f"Created: {datetime.now().isoformat()}\n")
            f.write(f"Kernel: {platform.release()}\n")

        return snapshot_name

    def list_snapshots(self) -> list:
        """List available snapshots"""
        snapshots = []
        if os.path.exists(self.BACKUP_DIR):
            for name in os.listdir(self.BACKUP_DIR):
                path = os.path.join(self.BACKUP_DIR, name)
                if os.path.isdir(path):
                    meta_file = os.path.join(path, "metadata.txt")
                    created = "Unknown"
                    if os.path.exists(meta_file):
                        with open(meta_file, "r", encoding="utf-8") as f:
                            for line in f:
                                if line.startswith("Created:"):
                                    created = line.split(":", 1)[1].strip()
                                    break
                    snapshots.append({"name": name, "created": created})
        return sorted(snapshots, key=lambda x: x["created"], reverse=True)

    def restore_snapshot(self, snapshot_name: str) -> bool:
        """Restore configuration from a snapshot"""


        snapshot_dir = os.path.join(self.BACKUP_DIR, snapshot_name)
        if not os.path.exists(snapshot_dir):
            console.print(f"[red]Yedek bulunamadı: {snapshot_name}[/red]")
            return False

        # Restore files
        restore_map = {
            "99-fedoraclean-ai.conf": "/etc/sysctl.d/99-fedoraclean-ai.conf",
            "99-fedoraclean-net.conf": "/etc/sysctl.d/99-fedoraclean-net.conf",
            "dnf5.conf": "/etc/dnf/dnf5.conf",
            "dnf.conf": "/etc/dnf/dnf.conf",
        }

        for src_name, dst_path in restore_map.items():
            src = os.path.join(snapshot_dir, src_name)
            if os.path.exists(src):
                try:
                    shutil.copy2(src, dst_path)
                    console.print(f"[green]✓ Geri yüklendi: {dst_path}[/green]")
                except Exception as e:
                    console.print(f"[red]✗ Hata ({dst_path}): {e}[/red]")

        # Reload sysctl
        run_command("sysctl --system", sudo=True)

        return True
