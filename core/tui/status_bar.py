"""TUI Status Bar - Persistent display of system/server status

Shows:
- Current mode (ghost/user/admin)
- Active servers (wizard, extensions)
- System stats (memory, CPU, uptime)
- Function key quick reference

Author: uDOS Engineering
Version: v1.0.0
Date: 2026-01-30
"""

from __future__ import annotations

from datetime import datetime
from enum import Enum
import socket

import psutil

from core.services.loopback_host_utils import is_loopback_host
from core.services.unified_config_loader import get_bool_config
from core.services.viewport_service import ViewportService
from core.tui.output import OutputToolkit
from core.utils.text_width import truncate_to_width


class ServerStatus(Enum):
    """Server availability status."""

    RUNNING = "●"
    STOPPED = "○"
    ERROR = "▲"
    UNKNOWN = "·"


class TUIStatusBar:
    """Persistent status bar for uCODE."""

    def __init__(self):
        """Initialize status bar."""
        self.wizard_port = 8765
        self.last_update = None
        self.cache_ttl = 2  # seconds

    def get_status_line(
        self, user_role: str = "ghost", ghost_mode: bool = False
    ) -> str:
        """Get a one-line status bar for persistent display.

        Format:
        [MODE: ghost] [WIZ: ●] [Mem: 45%] [CPU: 12%] [F1-F10]

        Args:
            user_role: Current user role (ghost, user, admin)

        Returns:
            Status bar string with width consideration
        """
        parts = []

        # Mode indicator
        mode_label = (
            "GHOST"
            if ghost_mode or user_role == "ghost"
            else "USER"
            if user_role == "user"
            else "ADMIN"
        )
        parts.append(f"[MODE: {mode_label}]")
        if ghost_mode:
            parts.append("[GHOST MODE]")

        # Server status
        wizard_status = self._check_server("127.0.0.1", self.wizard_port)
        parts.append(f"[WIZ: {wizard_status.value}]")

        # System stats
        mem_percent = self._get_memory_percent()
        cpu_percent = self._get_cpu_percent()
        parts.append(f"[Mem: {mem_percent}%]")
        parts.append(f"[CPU: {cpu_percent}%]")

        # Function key reference (abbreviated for status bar)
        parts.append("[F1-F10]")

        line = " ".join(parts)
        return truncate_to_width(line, ViewportService().get_cols())

    def get_status_panel(
        self, user_role: str = "ghost", ghost_mode: bool = False
    ) -> str:
        """Get a detailed multi-line status panel for full display.

        Returns:
            Formatted status panel with detailed information
        """
        lines = []
        width = ViewportService().get_cols()
        rule = "-" * min(70, width)
        lines.append("\n" + rule)
        lines.append(OutputToolkit.invert(" SYSTEM STATUS ".ljust(min(70, width))))
        lines.append(rule)

        # User mode
        mode_label = "GHOST MODE" if ghost_mode else user_role.upper()
        lines.append(f"\nMode:             {mode_label}")

        # Server status details
        lines.append("\nServers:")
        wizard_status = self._check_server("127.0.0.1", self.wizard_port)
        lines.append(f"  Wizard (8765):  {wizard_status.value} {wizard_status.name}")

        # System resources
        lines.append("\nSystem Resources:")
        mem = psutil.virtual_memory()
        lines.append(
            f"  Memory:         {mem.percent}% ({mem.used // (1024**3)}GB / {mem.total // (1024**3)}GB)"
        )

        cpu_percent = psutil.cpu_percent(interval=0.1)
        lines.append(f"  CPU:            {cpu_percent}%")

        # Column stats + meters
        try:
            boot_time = datetime.fromtimestamp(psutil.boot_time())
            uptime = datetime.now() - boot_time
            hours, remainder = divmod(int(uptime.total_seconds()), 3600)
            minutes, _ = divmod(remainder, 60)
        except Exception:
            hours, minutes = 0, 0

        mem_stat = OutputToolkit.stat_block("Mem", f"{int(mem.percent)}%", invert=True)
        cpu_stat = OutputToolkit.stat_block("CPU", f"{int(cpu_percent)}%", invert=True)
        uptime_stat = OutputToolkit.stat_block(
            "Uptime", f"{hours}h {minutes}m", invert=True
        )
        stats_row = OutputToolkit.columns(
            [
                mem_stat,
                OutputToolkit.progress_block(int(mem.percent), 100, label="Memory"),
            ],
            [
                cpu_stat,
                OutputToolkit.progress_block(int(cpu_percent), 100, label="CPU"),
            ],
        )
        lines.append("\n" + stats_row)
        lines.append(
            OutputToolkit.columns(
                [uptime_stat],
                [
                    OutputToolkit.progress_block(
                        int(minutes + hours * 60), 240, label="Session"
                    )
                ],
            )
        )
        if get_bool_config("UDOS_TUI_FULL_METERS", False):
            lines.append(
                OutputToolkit.progress_block_full(int(mem.percent), 100, label="Memory")
            )
            lines.append(
                OutputToolkit.progress_block_full(int(cpu_percent), 100, label="CPU")
            )

        # Function key reference
        lines.append("\nFunction Keys:")
        fkeys = [
            "F1: Help        ",
            "F2: Status      ",
            "F3: Logs        ",
            "F4: Ext         ",
            "F5: Refresh     ",
            "F6: Panels      ",
            "F7: Missions    ",
            "F8: Env         ",
            "F9: Settings    ",
            "F10: Exit       ",
        ]
        lines.append("  " + "    ".join(fkeys[:4]))
        lines.append("  " + "    ".join(fkeys[4:8]))
        lines.append("  " + "    ".join(fkeys[8:10]))

        lines.append("\n" + rule)
        clamped = [truncate_to_width(line, width) for line in lines]
        return "\n".join(clamped)

    @staticmethod
    def _check_server(host: str, port: int) -> ServerStatus:
        """Check if a server is running on the given host:port.

        Args:
            host: Hostname or IP
            port: Port number

        Returns:
            ServerStatus enum
        """
        normalized = (host or "").strip().lower()
        if not is_loopback_host(normalized):
            return ServerStatus.UNKNOWN
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(0.5)
        try:
            result = sock.connect_ex((normalized, port))
            return ServerStatus.RUNNING if result == 0 else ServerStatus.STOPPED
        except Exception:
            return ServerStatus.UNKNOWN
        finally:
            sock.close()

    @staticmethod
    def _get_memory_percent() -> int:
        """Get memory usage percentage."""
        try:
            return int(psutil.virtual_memory().percent)
        except Exception:
            return 0

    @staticmethod
    def _get_cpu_percent() -> int:
        """Get CPU usage percentage."""
        try:
            return int(psutil.cpu_percent(interval=0.1))
        except Exception:
            return 0
