"""RELOAD command handler - Control hot reload system."""

from typing import List, Dict
from core.commands.base import BaseCommandHandler
from core.services.hot_reload import get_hot_reload_manager
from core.tui.output import OutputToolkit

try:
    from core.services.logging_manager import get_logger
    logger = get_logger("reload-handler")
except ImportError:
    import logging
    logger = logging.getLogger("reload-handler")


class ReloadHandler(BaseCommandHandler):
    """Handler for RELOAD command - control hot reload system."""

    def handle(self, command: str, params: List[str], grid=None, parser=None) -> Dict:
        """
        Handle RELOAD command.

        Args:
            command: Command name (RELOAD)
            params: Subcommand
                - RELOAD on          Enable hot reload
                - RELOAD off         Disable hot reload
                - RELOAD status      Show hot reload status
                - RELOAD stats       Show reload statistics
            grid: Optional grid context
            parser: Optional parser

        Returns:
            Dict with hot reload status
        """
        reload_mgr = get_hot_reload_manager()
        
        if reload_mgr is None:
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
        """Show hot reload status."""
        stats = reload_mgr.stats()
        
        status_icon = "🟢" if stats["running"] else "🔴"
        status_text = "RUNNING" if stats["running"] else "STOPPED"
        
        lines = [
            OutputToolkit.banner(f"{status_icon} HOT RELOAD"),
            f"Status: {status_text}",
            f"Enabled: {'Yes' if stats['enabled'] else 'No'}",
            f"Watching: {stats['watch_dir']}",
            "",
            f"Reloads: {stats['reload_count']} successful, {stats['failed_count']} failed",
            f"Success rate: {stats['success_rate']:.1f}%",
            "",
            "Commands:",
            "  RELOAD on      - Start hot reload",
            "  RELOAD off     - Stop hot reload",
            "  RELOAD stats   - Show statistics"
        ]
        
        logger.info("[LOCAL] Displayed hot reload status")
        
        return {
            "status": "success",
            "output": "\n".join(lines)
        }

    def _enable_reload(self, reload_mgr) -> Dict:
        """Enable hot reload."""
        if reload_mgr.observer is not None:
            return {
                "status": "info",
                "output": OutputToolkit.section(
                    "ℹ️ HOT RELOAD",
                    "Hot reload is already running"
                )
            }
        
        success = reload_mgr.start()
        
        if success:
            logger.info("[LOCAL] Hot reload enabled")
            return {
                "status": "success",
                "output": OutputToolkit.section(
                    "✓ HOT RELOAD ENABLED",
                    f"Watching: {reload_mgr.watch_dir}\n"
                    "Handlers will auto-reload on save"
                )
            }
        else:
            logger.error("[LOCAL] Failed to enable hot reload")
            return {
                "status": "error",
                "output": OutputToolkit.section(
                    "✗ HOT RELOAD FAILED",
                    "Could not start file watcher.\n"
                    "Install watchdog: pip install watchdog"
                )
            }

    def _disable_reload(self, reload_mgr) -> Dict:
        """Disable hot reload."""
        if reload_mgr.observer is None:
            return {
                "status": "info",
                "output": OutputToolkit.section(
                    "ℹ️ HOT RELOAD",
                    "Hot reload is already stopped"
                )
            }
        
        stats = reload_mgr.stats()
        reload_mgr.stop()
        
        logger.info("[LOCAL] Hot reload disabled")
        
        return {
            "status": "success",
            "output": OutputToolkit.section(
                "✓ HOT RELOAD DISABLED",
                f"Session stats:\n"
                f"  Reloads: {stats['reload_count']}\n"
                f"  Failures: {stats['failed_count']}\n"
                f"  Success rate: {stats['success_rate']:.1f}%"
            )
        }

    def _show_stats(self, reload_mgr) -> Dict:
        """Show detailed statistics."""
        stats = reload_mgr.stats()
        
        lines = [
            OutputToolkit.banner("📊 HOT RELOAD STATISTICS"),
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
        
        logger.info("[LOCAL] Displayed hot reload statistics")
        
        return {
            "status": "success",
            "output": "\n".join(lines)
        }
