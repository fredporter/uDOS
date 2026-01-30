"""
TUI Status Bar - Persistent display of system/server status

Shows:
- Current mode (ghost/user/admin)
- Active servers (wizard, extensions)
- System stats (memory, CPU, uptime)
- Function key quick reference

Author: uDOS Engineering
Version: v1.0.0
Date: 2026-01-30
"""

import os
import psutil
from pathlib import Path
from typing import Dict, Optional
from datetime import datetime
from enum import Enum


class ServerStatus(Enum):
    """Server availability status."""
    RUNNING = "🟢"
    STOPPED = "🔴"
    ERROR = "🟠"
    UNKNOWN = "⚫"


class TUIStatusBar:
    """Persistent status bar for uCODE TUI."""

    def __init__(self):
        """Initialize status bar."""
        self.wizard_port = 8765
        self.goblin_port = 8767
        self.last_update = None
        self.cache_ttl = 2  # seconds

    def get_status_line(self, user_role: str = "ghost") -> str:
        """
        Get a one-line status bar for persistent display.

        Format:
        [MODE: ghost] [WIZ: 🟢] [EXT: 🔴] [Mem: 45%] [CPU: 12%] [F1-F8 help]

        Args:
            user_role: Current user role (ghost, user, admin)

        Returns:
            Status bar string with width consideration
        """
        parts = []

        # Mode indicator
        mode_emoji = "👻" if user_role == "ghost" else "👤" if user_role == "user" else "🔐"
        mode_display = f"{mode_emoji} {user_role.upper()}"
        parts.append(f"[{mode_display}]")

        # Server status
        wizard_status = self._check_server("localhost", self.wizard_port)
        parts.append(f"[WIZ: {wizard_status.value}]")

        goblin_status = self._check_server("localhost", self.goblin_port)
        parts.append(f"[GOB: {goblin_status.value}]")

        # System stats
        mem_percent = self._get_memory_percent()
        cpu_percent = self._get_cpu_percent()
        parts.append(f"[Mem: {mem_percent}%]")
        parts.append(f"[CPU: {cpu_percent}%]")

        # Function key reference (abbreviated for status bar)
        parts.append("[F1-F8]")

        return " ".join(parts)

    def get_status_panel(self, user_role: str = "ghost") -> str:
        """
        Get a detailed multi-line status panel for full display.

        Returns:
            Formatted status panel with detailed information
        """
        lines = []
        lines.append("\n" + "=" * 70)
        lines.append("📊 SYSTEM STATUS")
        lines.append("=" * 70)

        # User mode
        mode_emoji = "👻" if user_role == "ghost" else "👤" if user_role == "user" else "🔐"
        lines.append(f"\nMode:             {mode_emoji} {user_role.upper()}")

        # Server status details
        lines.append("\n📡 Servers:")
        wizard_status = self._check_server("localhost", self.wizard_port)
        goblin_status = self._check_server("localhost", self.goblin_port)

        lines.append(f"  Wizard (8765):  {wizard_status.value} {wizard_status.name}")
        lines.append(f"  Goblin (8767):  {goblin_status.value} {goblin_status.name}")

        # System resources
        lines.append("\n💻 System Resources:")
        mem = psutil.virtual_memory()
        lines.append(f"  Memory:         {mem.percent}% ({mem.used // (1024**3)}GB / {mem.total // (1024**3)}GB)")

        cpu_percent = psutil.cpu_percent(interval=0.1)
        lines.append(f"  CPU:            {cpu_percent}%")

        # Uptime
        try:
            boot_time = datetime.fromtimestamp(psutil.boot_time())
            uptime = datetime.now() - boot_time
            hours, remainder = divmod(int(uptime.total_seconds()), 3600)
            minutes, _ = divmod(remainder, 60)
            lines.append(f"  Uptime:         {hours}h {minutes}m")
        except Exception:
            lines.append(f"  Uptime:         Unknown")

        # Function key reference
        lines.append("\n⌨️  Function Keys:")
        fkeys = [
            "F1: New File    ",
            "F2: File Pick   ",
            "F3: Workspace   ",
            "F4: Binder      ",
            "F5: Workflows   ",
            "F6: Settings    ",
            "F7: Fkey Help   ",
            "F8: Wizard      ",
        ]
        lines.append("  " + "    ".join(fkeys[:4]))
        lines.append("  " + "    ".join(fkeys[4:8]))

        lines.append("\n" + "=" * 70)

        return "\n".join(lines)

    @staticmethod
    def _check_server(host: str, port: int) -> ServerStatus:
        """
        Check if a server is running on the given host:port.

        Args:
            host: Hostname or IP
            port: Port number

        Returns:
            ServerStatus enum
        """
        try:
            import socket
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.settimeout(0.5)
            result = sock.connect_ex((host, port))
            sock.close()
            return ServerStatus.RUNNING if result == 0 else ServerStatus.STOPPED
        except Exception:
            return ServerStatus.UNKNOWN

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
