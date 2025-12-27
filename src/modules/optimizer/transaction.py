"""
Transaction manager for optimizations.
Tracks individual changes for granular rollback capability.
"""
import os
import re
import json
import uuid
from datetime import datetime
from typing import List, Dict, Optional
from ..utils import run_command, console

class TransactionManager:
    """
    Transaction-based rollback manager

    Tracks all optimization changes and allows:
    - undo_last(): Undo the most recent transaction
    - undo_by_id(): Undo a specific transaction
    - list_transactions(): View all recorded transactions
    """

    TRANSACTION_FILE = "/var/lib/fedoraclean/transactions.json"

    def __init__(self):
        os.makedirs(os.path.dirname(self.TRANSACTION_FILE), exist_ok=True)
        self._ensure_file()

    def _ensure_file(self):
        if not os.path.exists(self.TRANSACTION_FILE):
            with open(self.TRANSACTION_FILE, "w", encoding="utf-8") as f:
                json.dump([], f)

    def _load_transactions(self) -> List[Dict]:
        try:
            with open(self.TRANSACTION_FILE, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception:
            return []

    def _save_transactions(self, transactions: List[Dict]):
        try:
            with open(self.TRANSACTION_FILE, "w", encoding="utf-8") as f:
                json.dump(transactions, f, indent=2, ensure_ascii=False)
        except Exception as e:
            console.print(f"[red]Transaction kayıt hatası: {e}[/red]")

    def record_transaction(self, category: str, description: str,
                          changes: List[Dict]) -> str:
        """
        Record a new transaction

        Args:
            category: Type of optimization (quick, kernel, network, io, gaming)
            description: Human-readable description
            changes: List of {param, old, new} dicts

        Returns:
            Transaction ID
        """


        tx_id = str(uuid.uuid4())[:8]
        transaction = {
            "id": tx_id,
            "timestamp": datetime.now().isoformat(),
            "category": category,
            "description": description,
            "changes": changes
        }

        transactions = self._load_transactions()
        transactions.append(transaction)

        # Keep only last 50 transactions
        if len(transactions) > 50:
            transactions = transactions[-50:]

        self._save_transactions(transactions)
        return tx_id

    def list_transactions(self, limit: int = 10) -> List[Dict]:
        """List recent transactions, most recent first"""
        transactions = self._load_transactions()
        return list(reversed(transactions[-limit:]))

    def get_last_transaction(self) -> Optional[Dict]:
        """Get the most recent transaction"""
        transactions = self._load_transactions()
        return transactions[-1] if transactions else None

    def undo_last(self) -> bool:
        """Undo the most recent transaction"""
        last = self.get_last_transaction()
        if not last:
            console.print("[yellow]Geri alınacak işlem yok.[/yellow]")
            return False

        return self.undo_by_id(last["id"])

    def undo_by_id(self, tx_id: str) -> bool:
        """
        Undo a specific transaction by restoring old values

        Returns True if successful
        """
        transactions = self._load_transactions()

        # Find the transaction
        target = None
        for tx in transactions:
            if tx["id"] == tx_id:
                target = tx
                break

        if not target:
            console.print(f"[red]İşlem bulunamadı: {tx_id}[/red]")
            return False

        console.print(f"[yellow]↩️ Geri alınıyor: {target['description']}[/yellow]")
        console.print(f"[dim]Tarih: {target['timestamp'][:16]}[/dim]\n")

        restored = 0
        failed = 0

        for change in target["changes"]:
            param = change["param"]
            old_value = change["old"]

            # Check if it's a sysctl parameter or a command
            if param.startswith("/") or "." not in param:
                # Special case: I/O scheduler or file path
                if "Scheduler" in param:
                    # Extract device from param like "I/O Scheduler (nvme0n1)"

                    match = re.search(r'\((\w+)\)', param)
                    if match:
                        dev = match.group(1)
                        sched_path = f"/sys/block/{dev}/queue/scheduler"
                        # Fix: Use sh -c for proper sudo echo redirection
                        s, _, _ = run_command(f"sh -c 'echo {old_value} > {sched_path}'", sudo=True)
                        if s:
                            console.print(f"  [green]✓[/] {param}: {old_value}")
                            restored += 1
                        else:
                            failed += 1
                else:
                    # Skip non-restorable items
                    console.print(f"  [dim]⊘ {param}: Geri alınamaz[/dim]")
            else:
                # Standard sysctl parameter
                s, _, _ = run_command(f"sysctl -w {param}={old_value}", sudo=True)
                if s:
                    console.print(f"  [green]✓[/] {param} = {old_value}")
                    restored += 1
                else:
                    console.print(f"  [red]✗[/] {param}: Geri alınamadı")
                    failed += 1

        # Remove transaction from history
        transactions = [tx for tx in transactions if tx["id"] != tx_id]
        self._save_transactions(transactions)

        # Update sysctl config file - remove the applied changes
        self._cleanup_sysctl_config(target["changes"])

        console.print(f"\n[green]✓ {restored} parametre geri alındı.[/green]")
        if failed > 0:
            console.print(f"[yellow]⚠ {failed} parametre geri alınamadı.[/yellow]")

        return True

    def _cleanup_sysctl_config(self, changes: List[Dict]):
        """Remove applied changes from sysctl config file"""
        conf_files = [
            "/etc/sysctl.d/99-fedoraclean-ai.conf",
            "/etc/sysctl.d/99-fedoraclean-net.conf"
        ]

        params_to_remove = [c["param"] for c in changes if "." in c["param"]]

        for conf_file in conf_files:
            if not os.path.exists(conf_file):
                continue

            try:
                with open(conf_file, "r", encoding="utf-8") as f:
                    lines = f.readlines()

                # Filter out lines containing removed parameters
                new_lines = []
                for line in lines:
                    keep = True
                    for param in params_to_remove:
                        if line.strip().startswith(param):
                            keep = False
                            break
                    if keep:
                        new_lines.append(line)

                with open(conf_file, "w", encoding="utf-8") as f:
                    f.writelines(new_lines)
            except Exception:
                pass

    def reset_to_defaults(self) -> bool:
        """
        Reset all system optimizations to default state.
        
        This will:
        1. Undo all recorded transactions in reverse order
        2. Remove all FedoraClean configuration files
        3. Run sysctl --system to reload defaults
        
        Returns:
            bool: True if successful
        """
        console.print("\n[bold yellow]🔄 Tüm optimizasyonlar varsayılana döndürülüyor...[/bold yellow]\n")
        
        # Load all transactions
        transactions = self._load_transactions()
        
        if not transactions:
            console.print("[yellow]Geri alınacak işlem bulunamadı.[/yellow]")
        else:
            console.print(f"[dim]{len(transactions)} işlem bulundu, geri alınıyor...[/dim]\n")
            
            # Undo all transactions in reverse order (newest first)
            for i, tx in enumerate(reversed(transactions), 1):
                console.print(f"[dim]{i}/{len(transactions)} - {tx['description']}[/dim]")
                
                # Undo each change in the transaction
                for change in tx["changes"]:
                    param = change["param"]
                    old_value = change["old"]
                    
                    # Only undo sysctl parameters
                    if "." in param and not param.startswith("/"):
                        success, _, _ = run_command(f"sysctl -w {param}={old_value}", sudo=True)
                        if success:
                            console.print(f"  [green]✓[/] {param} = {old_value}")
        
        # Clear transaction history
        console.print("\n[dim]İşlem geçmişi temizleniyor...[/dim]")
        self._save_transactions([])
        
        # Remove config files
        config_files = [
            "/etc/sysctl.d/99-fedoraclean.conf",
            "/etc/sysctl.d/99-fedoraclean-ai.conf",
            "/etc/sysctl.d/99-fedoraclean-net.conf"
        ]
        
        console.print("\n[dim]Konfigürasyon dosyaları temizleniyor...[/dim]")
        for config_file in config_files:
            if os.path.exists(config_file):
                try:
                    os.remove(config_file)
                    console.print(f"[green]✓ Silindi:[/] {config_file}")
                except Exception as e:
                    console.print(f"[red]✗ Silinemedi ({config_file}):[/] {e}")
        
        # Reload system defaults
        console.print("\n[dim]Sistem varsayılanları yükleniyor...[/dim]")
        run_command("sysctl --system", sudo=True)
        
        console.print("\n[bold green]✅ Tüm optimizasyonlar başarıyla varsayılana döndürüldü![/bold green]")
        console.print("[dim]Sistem orijinal haline geldi.[/dim]\n")
        
        return True
