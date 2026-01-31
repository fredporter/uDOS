"""RELOAD command handler - Control the hot reload watcher system.

RELOAD controls the automatic file watcher that hot-reloads handlers when they are saved.

Commands:
  RELOAD            Show status
  RELOAD on         Enable hot reload watcher
  RELOAD off        Disable hot reload watcher
  RELOAD status     Show current status
  RELOAD stats      Show statistics

Note: Use RESTART 1 for a one-time manual hot reload without enabling the watcher.
"""

from typing import List, Dict
from core.commands.base import BaseCommandHandler
from core.services.hot_reload import get_hot_reload_manager

try:
    from core.services.logging_service import get_logger
    logger = get_logger("reload-handler")
except ImportError:
    import logging
    logger = logging.getLogger("reload-handler")


class ReloadHandler(BaseCommandHandler):
    """Handler for RELOAD command - control hot reload watcher."""

    def handle(self, command: str, params: List[str], grid=None, parser=None) -> Dict:
        """Handle RELOAD command - control hot reload watcher.

        Args:
            command: Command name (RELOAD)
            params: Subcommand: on, off, status, stats
            grid: Optional grid context
            parser: Optional parser

        Returns:
            Dict with hot reload status
        """
        reload_mgr = get_hot_reload_manager()
        
        if reload_mgr is None:
            from core.tui.output import OutputToolkit
            return {
                "status": "error",
                "message": "Hot reload not initialized",
                "output": OutputToolkit.section(
                    "⚠️ HOT RELOAD",
                    "Hot reload system not available.\nRequires: pip install watchdog"
                )
            }
        
        if not params or params[0].lower() == "status":
            return self._show_status(reload_mgr)
        
        subcommand = params[0].lower()
        
        if subcommand == "on":
            return self._enable_reload(reload_mgr)
        elif subcommand == "off":
            return self._disable_reload(reload_mgr)
        elif subcommand == "stats":
            return self._show_stats(reload_mgr)
        else:
            return {
                "status": "error",
                "message": f"Unknown RELOAD subcommand: {subcommand}",
                "output": "Usage: RELOAD [on|off|status|stats]"
            }

    def _show_status(self, reload_mgr) -> Dict:
        """Show hot reload watcher status."""
        from core.tui.output import OutputToolkit
        
        stats = reload_mgr.stats()

        status_icon = "🟢" if stats["running"] else "🔴"
        status_text = "RUNNING" if stats["running"] else "STOPPED"

        lines = [
            OutputToolkit.banner(f"{status_icon} HOT RELOAD WATCHER"),
            f"Status: {status_text}",
            f"Enabled: {'Yes' if stats['enabled'] else 'No'}",
            f"Watching: {stats['watch_dir']}",
            "",
            f"Reloads: {stats['reload_count']} successful, {stats['failed_count']} failed",
            f"Success rate: {stats['success_rate']:.1f}%",
            "",
            "Commands:",
            "  RELOAD on      - Start watcher",
            "  RELOAD off     - Stop watcher",
            "  RELOAD stats   - Show statistics",
            "",
            "Note: Watcher auto-reloads handlers when you save them.",
            "      Use RESTART 1 for a one-time manual reload.",
        ]

        logger.info("[LOCAL] Displayed hot reload watcher status")

        return {
            "status": "success",
            "output": "\n".join(lines)
        }

    def _enable_reload(self, reload_mgr) -> Dict:
        """Enable hot reload watcher."""
        from core.tui.output import OutputToolkit
        
        if reload_mgr.observer is not None:
            return {
                "status": "info",
                "output": OutputToolkit.section(
                    "ℹ️ HOT RELOAD WATCHER",
                    "File watcher is already running"
                )
            }
        
        success = reload_mgr.start()
        
        if success:
            logger.info("[LOCAL] Hot reload watcher enabled")
            return {
                "status": "success",
                "output": OutputToolkit.section(
                    "✓ HOT RELOAD WATCHER ENABLED",
                    f"Watching: {reload_mgr.watch_dir}\n"
                    "Handlers will auto-reload when you save them"
                )
            }
        else:
            logger.error("[LOCAL] Failed to enable hot reload watcher")
            return {
                "status": "error",
                "output": OutputToolkit.section(
                    "✗ HOT RELOAD WATCHER FAILED",
                    "Could not start file watcher.\n"
                    "Install watchdog: pip install watchdog"
                )
            }

    def _disable_reload(self, reload_mgr) -> Dict:
        """Disable hot reload watcher."""
        from core.tui.output import OutputToolkit
        
        if reload_mgr.observer is None:
            return {
                "status": "info",
                "output": OutputToolkit.section(
                    "ℹ️ HOT RELOAD WATCHER",
                    "File watcher is already stopped"
                )
            }
        
        stats = reload_mgr.stats()
        reload_mgr.stop()
        
        logger.info("[LOCAL] Hot reload watcher disabled")
        
        return {
            "status": "success",
            "output": OutputToolkit.section(
                "✓ HOT RELOAD WATCHER DISABLED",
                f"Session stats:\n"
                f"  Reloads: {stats['reload_count']}\n"
                f"  Failures: {stats['failed_count']}\n"
                f"  Success rate: {stats['success_rate']:.1f}%"
            )
        }

    def _show_stats(self, reload_mgr) -> Dict:
        """Show detailed statistics."""
        from core.tui.output import OutputToolkit
        
        stats = reload_mgr.stats()
        
        lines = [
            OutputToolkit.banner("📊 HOT RELOAD WATCHER STATISTICS"),
            f"Status: {'RUNNING' if stats['running'] else 'STOPPED'}",
            f"Watch directory: {stats['watch_dir']}",
            "",
            "Reload History:",
            f"  Successful: {stats['reload_count']}",
            f"  Failed: {stats['failed_count']}",
            f"  Success rate: {stats['success_rate']:.1f}%",
            "",
            "Tip: Edit a handler in core/commands/, save it,",
            "     and it will reload automatically (if RELOAD on)"
        ]
        
        logger.info("[LOCAL] Displayed hot reload watcher statistics")
        
        return {
            "status": "success",
            "output": "\n".join(lines)
        }
