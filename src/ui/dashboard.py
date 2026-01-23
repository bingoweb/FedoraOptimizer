"""
Dashboard UI module for Fedora Optimizer.
"""
import socket
import platform
from datetime import datetime

import psutil
from rich import box
from rich.align import Align
from rich.panel import Panel
from rich.table import Table
from rich.text import Text

from modules.utils import Theme, format_bytes


class Dashboard:
    """
    Dashboard class to render system statistics and information.
    """
    def __init__(self):
        # Network speed tracking
        self.last_net_io = psutil.net_io_counters()
        self.last_time = datetime.now()

    def get_color(self, val, safe, warn):
        """Returns color based on value thresholds."""
        if val < safe:
            return Theme.SUCCESS
        if val < warn:
            return Theme.WARNING
        return Theme.ERROR

    def make_bar(self, percent, color, width=15):
        """Creates a text-based progress bar."""
        # Smoother, more professional bar
        filled = int(percent / 100 * width)
        return f"[{color}]{'━'*filled}[/][dim white]{'┄'*(width-filled)}[/]"

    def get_device_info(self):
        """Renders device information panel."""
        uname = platform.uname()
        hostname = socket.gethostname()
        distro = "Fedora Linux 43"
        kernel = uname.release

        try:
            with open("/proc/cpuinfo", "r", encoding="utf-8") as f:
                for line in f:
                    if "model name" in line:
                        cpu_name = line.split(":")[1].strip()
                        break
        except Exception: # pylint: disable=broad-except
            cpu_name = "Bilinmiyor"

        # Cleanup CPU name
        cpu_clean = cpu_name.replace("Intel(R)", "").replace("Core(TM)", "")
        cpu_clean = cpu_clean.replace("AMD", "").replace("Processor", "").replace(
            "CPU", "").replace("@", "")
        cpu_clean = " ".join(cpu_clean.split())

        # Better kernel version (Major.Minor)
        k_parts = kernel.split('.')
        k_ver = f"{k_parts[0]}.{k_parts[1]}" if len(k_parts) >= 2 else kernel

        # Calculate Uptime
        try:
            boot_time = datetime.fromtimestamp(psutil.boot_time())
            now = datetime.now()
            uptime = now - boot_time
            days = uptime.days
            hours, remainder = divmod(uptime.seconds, 3600)
            minutes, _ = divmod(remainder, 60)

            uptime_str = ""
            if days > 0: uptime_str += f"{days}g "
            if hours > 0: uptime_str += f"{hours}s "
            uptime_str += f"{minutes}dk"
            uptime_str = uptime_str.strip()
        except Exception: # pylint: disable=broad-except
            uptime_str = "?"

        grid = Table.grid(expand=True, padding=(0, 1))
        grid.add_column(style=f"bold {Theme.PRIMARY}")
        grid.add_column(style="white")

        grid.add_row("CİHAZ:", hostname)
        grid.add_row("OS:", distro)
        grid.add_row("KERNEL:", k_ver)
        grid.add_row("CPU:", cpu_clean[:25] + ("…" if len(cpu_clean) > 25 else ""))
        grid.add_row("MİMARİ:", uname.machine)
        grid.add_row("ÇALIŞMA:", uptime_str)

        return Panel(
            Align.center(grid, vertical="middle"),
            title=f"[bold {Theme.TEXT}] SİSTEM BİLGİSİ [/]",
            border_style=Theme.BORDER,
            box=box.ROUNDED,
            padding=(1, 1)
        )

    def get_system_overview(self):
        """Renders system resource overview panel."""
        cpu_p = psutil.cpu_percent()
        mem = psutil.virtual_memory()
        disk = psutil.disk_usage('/')

        grid = Table.grid(expand=True, padding=(0, 2))
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
        """Renders active processes panel."""
        procs = []
        for p in psutil.process_iter([
            'pid', 'name', 'cpu_percent', 'memory_percent', 'memory_info'
        ]):
            try:
                name = p.info['name']
                if len(name) > 15:
                    p.info['name'] = name[:14] + "…"
                procs.append(p.info)
            except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess):
                pass

        top_cpu = sorted(procs, key=lambda p: p['cpu_percent'], reverse=True)[:5]

        table = Table(
            box=None,
            expand=True,
            padding=(0, 1),
            show_header=True,
            header_style=f"bold {Theme.PRIMARY}"
        )
        table.add_column("PID", style="dim white", width=6)
        table.add_column("İŞLEM", style="white")
        table.add_column("CPU", justify="right")
        table.add_column("RAM", justify="right")

        for p in top_cpu:
            cpu_val = p['cpu_percent']
            mem_val = p['memory_percent']
            mem_bytes = p['memory_info'].rss

            c_color = self.get_color(cpu_val, 50, 80)
            m_color = self.get_color(mem_val, 50, 80)

            table.add_row(
                str(p['pid']),
                p['name'].title(),  # Title case looks better than UPPER
                f"[{c_color}]{cpu_val:.1f}%[/]",
                f"[{m_color}]{format_bytes(mem_bytes, precision=1)}[/]"
            )

        return Panel(
            table,
            title=f"[bold {Theme.TEXT}] EN AKTİF İŞLEMLER [/]",
            border_style=Theme.BORDER,
            box=box.ROUNDED,
            padding=(0, 1)
        )

    def get_network_panel(self):
        """Renders network status panel."""
        now = datetime.now()
        cur_net = psutil.net_io_counters()
        dt = (now - self.last_time).total_seconds()
        if dt == 0:
            dt = 1

        up_speed = (cur_net.bytes_sent - self.last_net_io.bytes_sent) / dt
        down_speed = (cur_net.bytes_recv - self.last_net_io.bytes_recv) / dt

        self.last_net_io = cur_net
        self.last_time = now

        def fmt(s):
            return f"{format_bytes(s, precision=1)}/s"

        grid = Table.grid(expand=True, padding=(0, 1))
        grid.add_column(style="bold white")
        grid.add_column(justify="right", style=Theme.PRIMARY)

        grid.add_row("İNDİRME:", fmt(down_speed))
        grid.add_row("YÜKLEME:", fmt(up_speed))
        grid.add_row("", "")
        grid.add_row("[dim]TOPLAM İNEN:[/dim]", format_bytes(cur_net.bytes_recv))
        grid.add_row("[dim]TOPLAM GİDEN:[/dim]", format_bytes(cur_net.bytes_sent))

        return Panel(
            Align.center(grid, vertical="middle"),
            title=f"[bold {Theme.TEXT}] AĞ DURUMU [/]",
            border_style=Theme.BORDER,
            box=box.ROUNDED,
            padding=(1, 1)
        )

    def get_header(self):
        """Renders the main dashboard header."""
        grid = Table.grid(expand=True)
        grid.add_column(justify="left", ratio=1)
        grid.add_column(justify="right")
        grid.add_row(
            f"[bold {Theme.PRIMARY}]FEDORA[/] [bold white]OPTİMİZER[/] "
            f"[dim white]///[/] [bold {Theme.SUCCESS}] 2025 AI [/]",
            datetime.now().strftime("%H:%M")
        )
        return Panel(grid, style=f"{Theme.PRIMARY} on #1e1e1e", box=box.ROUNDED)

    def get_footer(self, message="Hazır"):
        """Renders the dashboard footer."""
        return Panel(
            Text.from_markup(f"{message}"),
            border_style=Theme.BORDER,
            box=box.ROUNDED,
            padding=(0, 1)
        )


dashboard_ui = Dashboard()
