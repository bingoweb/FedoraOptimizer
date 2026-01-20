import subprocess
import shutil
import os
from rich.console import Console

console = Console()

class Theme:
    PRIMARY = "#3c6eb4"  # Fedora Blue
    SECONDARY = "#2980b9" # Darker Blue
    SUCCESS = "#27ae60"  # Nephritis Green
    WARNING = "#f39c12"  # Orange
    ERROR = "#c0392b"    # Red
    TEXT = "white"
    DIM_TEXT = "dim white"
    BORDER = "blue"      # Default border color

def run_command(command, sudo=False):
    """Runs a shell command and returns the output.
    Note: 'sudo' param is kept for compatibility but the app runs as root now.
    """
    # If app is running as root, we don't need to prepend sudo usually, 
    # but some commands might behave differently. 
    # For now, we trust the env is root.
    
    try:
        # Using subprocess with text=True for easier handling
        result = subprocess.run(
            command, 
            shell=True, 
            text=True, 
            capture_output=True
        )
        return result.returncode == 0, result.stdout, result.stderr
    except Exception as e:
        return False, "", str(e)

def get_directory_size(path):
    """Calculates the size of a directory in bytes."""
    total_size = 0
    try:
        for dirpath, dirnames, filenames in os.walk(path):
            for f in filenames:
                fp = os.path.join(dirpath, f)
                # skip if it is symbolic link
                if not os.path.islink(fp):
                    total_size += os.path.getsize(fp)
    except Exception:
        pass # Permission issues or others
    return total_size

def format_bytes(size, precision=2):
    """Formats bytes into human readable string with customizable precision."""
    # 2**10 = 1024
    power = 2**10
    n = 0
    power_labels = {0 : '', 1: 'K', 2: 'M', 3: 'G', 4: 'T'}
    while size >= power:
        size /= power
        n += 1
    return f"{size:.{precision}f} {power_labels[n]}B"
