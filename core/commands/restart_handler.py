"""
REBOOT Command Handler

Command:
    REBOOT  # Hot reload handlers and restart the TUI

This is the only restart path. No menus, no numbered options.
"""

from __future__ import annotations

import os
import sys
from pathlib import Path

from .base import BaseCommandHandler
from .handler_logging_mixin import HandlerLoggingMixin


class RestartHandler(BaseCommandHandler, HandlerLoggingMixin):
    """REBOOT command handler - hot reload + TUI restart."""

    def handle(self, command, params, grid, parser):
        """Handle REBOOT command with logging."""
        from core.services.logging_api import get_logger
        from core.services.user_service import get_user_manager
        from core.tui.output import OutputToolkit

        logger = get_logger("core", category="reboot", name="reboot-handler")
        output = OutputToolkit()
        user_mgr = get_user_manager()
        user = user_mgr.current()

        with self.trace_command(command, params) as trace:
            if command.upper() != "REBOOT":
                return {
                    "status": "error",
                    "message": "Unknown command. Use REBOOT.",
                }

            if params:
                return {
                    "status": "warning",
                    "message": "REBOOT takes no options. Running default reboot.",
                }

            logger.event(
                "info",
                "reboot.start",
                f"Reboot initiated by {user.username if user else 'unknown'}",
                ctx={"command": command},
            )

            lines = []
            lines.append("")
            lines.append(output.banner("REBOOT"))
            lines.append("Hot reload: refreshing handlers...")

            try:
                from core.services.hot_reload import get_hot_reload_manager, reload_all_handlers

                reload_mgr = get_hot_reload_manager()
                dispatcher = reload_mgr.dispatcher if reload_mgr else None
                stats = reload_all_handlers(logger=logger, dispatcher=dispatcher)
                reloaded = stats.get("reloaded", 0)
                failed = stats.get("failed", 0)
                lines.append(f"✓ Reloaded {reloaded} handlers ({failed} failed)")

                if reload_mgr is None:
                    lines.append("⚠️  Hot reload watcher not initialized")
            except Exception as exc:
                lines.append(f"❌ Hot reload failed: {exc}")
                logger.error("[REBOOT] Hot reload error: %s", exc)

            lines.append("Restarting TUI...")

            # Flush output before replacing the process
            output_text = "\n".join(lines) + "\n"
            sys.stdout.write(output_text)
            sys.stdout.flush()

            # Restart current Python process
            try:
                argv = [sys.executable] + sys.argv
                if len(argv) == 1:
                    # Fallback to uDOS.py at repo root
                    repo_root = Path(__file__).resolve().parents[2]
                    argv = [sys.executable, str(repo_root / "uDOS.py")]
                os.execv(sys.executable, argv)
            except Exception as exc:
                logger.error("[REBOOT] Failed to restart TUI: %s", exc)
                return {
                    "status": "error",
                    "message": f"Failed to restart TUI: {exc}",
                }

            return {"status": "success"}
