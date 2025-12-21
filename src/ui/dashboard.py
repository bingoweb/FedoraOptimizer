from rich.layout import Layout
from rich.panel import Panel
from rich.console import Console
from rich.text import Text
from rich.table import Table
from rich import box
from datetime import datetime
import psutil
import platform
import socket
import os

from modules.utils import Theme
from rich.align import Align

class Dashboard:
    def __init__(self):
        # Network speed tracking
        self.last_net_io = psutil.net_io_counters()
        self.last_time = datetime.now()

    def get_color(self, val, safe, warn):
        if val < safe: return Theme.SUCCESS 
        if val < warn: return Theme.WARNING
        return Theme.ERROR

    def make_bar(self, percent, color, width=15):
        # Smoother, more professional bar
        filled = int(percent / 100 * width)
        return f"[{color}]{'━'*filled}[/][dim white]{'┄'*(width-filled)}[/]"

    def get_device_info(self):
        uname = platform.uname()
        hostname = socket.gethostname()
        distro = "Fedora Linux 43" 
        kernel = uname.release
        
        try:
             with open("/proc/cpuinfo", "r") as f:
                 for line in f:
                     if "model name" in line:
                         cpu_name = line.split(":")[1].strip()
                         break
        except: cpu_name = "Bilinmiyor"

        grid = Table.grid(expand=True, padding=(0,1))
        grid.add_column(style=f"bold {Theme.PRIMARY}")
        grid.add_column(style="white")
        
        grid.add_row("CİHAZ:", hostname)
        grid.add_row("OS:", distro)
        grid.add_row("KERNEL:", kernel.split('.')[0] + "...") # Shorten
        grid.add_row("CPU:", cpu_name[:25] + "...")
        grid.add_row("MİMARİ:", uname.machine)

        return Panel(
            Align.center(grid, vertical="middle"),
            title=f"[bold {Theme.TEXT}] SİSTEM BİLGİSİ [/]",
            border_style=Theme.BORDER,
            box=box.ROUNDED,
            padding=(1, 1)
        )

    def get_system_overview(self):
        cpu_p = psutil.cpu_percent()
        mem = psutil.virtual_memory()
        disk = psutil.disk_usage('/')
        
        grid = Table.grid(expand=True, padding=(0,2))
        grid.add_column("Icon", width=3)
        grid.add_column("Name", style="bold white", width=6)
        grid.add_column("Val", justify="right", style=Theme.PRIMARY, width=6)
        grid.add_column("Bar", justify="right", ratio=1)
        
        c_col = self.get_color(cpu_p, 50, 80)
        grid.add_row("⚡", "CPU", f"{cpu_p}%", self.make_bar(cpu_p, c_col))
        
        m_col = self.get_color(mem.percent, 60, 85)
        grid.add_row("🧠", "RAM", f"{mem.percent}%", self.make_bar(mem.percent, m_col))
        
        swap = psutil.swap_memory()
        s_col = self.get_color(swap.percent, 50, 80)
        grid.add_row("🔋", "SWP", f"{swap.percent}%", self.make_bar(swap.percent, s_col))

        d_col = self.get_color(disk.percent, 70, 90)
        grid.add_row("💿", "DSK", f"{disk.percent}%", self.make_bar(disk.percent, d_col))

        return Panel(
            grid,
            title=f"[bold {Theme.TEXT}] KAYNAK KULLANIMI [/]",
            border_style=Theme.BORDER,
            box=box.ROUNDED,
            padding=(1, 1)
        )

    def get_process_panel(self):
        procs = []
        for p in psutil.process_iter(['pid', 'name', 'cpu_percent', 'memory_percent']):
            try:
                p.info['name'] = p.info['name'][:15]
                procs.append(p.info)
            except: pass
            
        top_cpu = sorted(procs, key=lambda p: p['cpu_percent'], reverse=True)[:5]
        
        table = Table(box=None, expand=True, padding=(0,1), show_header=True, header_style=f"bold {Theme.PRIMARY}")
        table.add_column("PID", style="dim white", width=6)
        table.add_column("İŞLEM", style="white")
        table.add_column("CPU", justify="right", style=Theme.SUCCESS)
        table.add_column("RAM", justify="right", style="cyan")
        
        for p in top_cpu:
            table.add_row(
                str(p['pid']),
                p['name'].title(), # Title case looks better than UPPER
                f"{p['cpu_percent']:.1f}%",
                f"{p['memory_percent']:.1f}%"
            )
            
        return Panel(
            table,
            title=f"[bold {Theme.TEXT}] EN AKTİF İŞLEMLER [/]",
            border_style=Theme.BORDER,
            box=box.ROUNDED,
            padding=(0, 1)
        )

    def get_network_panel(self):
        now = datetime.now()
        cur_net = psutil.net_io_counters()
        dt = (now - self.last_time).total_seconds()
        if dt == 0: dt = 1
        
        up_speed = (cur_net.bytes_sent - self.last_net_io.bytes_sent) / dt
        down_speed = (cur_net.bytes_recv - self.last_net_io.bytes_recv) / dt
        
        self.last_net_io = cur_net
        self.last_time = now
        
        def fmt(s):
            if s > 1024**2: return f"{s/1024**2:.1f} MB/s"
            if s > 1024: return f"{s/1024:.1f} KB/s"
            return f"{s:.0f} B/s"

        grid = Table.grid(expand=True, padding=(0,1))
        grid.add_column(style="bold white")
        grid.add_column(justify="right", style=Theme.PRIMARY)
        
        grid.add_row("İNDİRME:", fmt(down_speed))
        grid.add_row("YÜKLEME:", fmt(up_speed))
        grid.add_row("", "")
        grid.add_row("[dim]TOPLAM İNEN:[/dim]", str(cur_net.bytes_recv // 1024**2) + " MB")
        grid.add_row("[dim]TOPLAM GİDEN:[/dim]", str(cur_net.bytes_sent // 1024**2) + " MB")
        
        return Panel(
            Align.center(grid, vertical="middle"),
            title=f"[bold {Theme.TEXT}] AĞ DURUMU [/]",
            border_style=Theme.BORDER,
            box=box.ROUNDED,
            padding=(1, 1)
        )

    def get_header(self):
        grid = Table.grid(expand=True)
        grid.add_column(justify="left", ratio=1)
        grid.add_column(justify="right")
        grid.add_row(
            f"[bold {Theme.PRIMARY}]FEDORA[/] [bold white]OPTİMİZER[/] [dim white]///[/] [bold {Theme.SUCCESS}] 2025 AI [/]",
            datetime.now().strftime("%H:%M")
        )
        return Panel(grid, style=f"{Theme.PRIMARY} on #1e1e1e", box=box.ROUNDED)

    def get_footer(self, message="Hazır"):
        return Panel(
            Text.from_markup(f"{message}"),
            border_style=Theme.BORDER,
            box=box.ROUNDED,
            padding=(0,1)
        )

dashboard_ui = Dashboard()
