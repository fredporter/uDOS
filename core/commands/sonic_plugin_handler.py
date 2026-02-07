"""
TUI integration example for modular Sonic plugin.

Shows how to add database sync commands to the TUI.
"""

from pathlib import Path
from typing import Dict, List

from core.commands.base import BaseCommandHandler
from core.services.logging_api import get_logger, LogTags

logger = get_logger("sonic-tui-plugin")


class SonicPluginHandler(BaseCommandHandler):
    """
    Extended SONIC handler with plugin system integration.

    Adds database sync commands to the existing SONIC TUI handler.
    """

    def handle(self, command: str, params: List[str], grid=None, parser=None) -> Dict:
        """Handle SONIC commands with plugin extensions."""

        if not params:
            return self._help()

        action = params[0].lower()

        # Plugin-specific commands
        if action == "sync":
            return self._sync_status()
        if action == "rebuild":
            return self._rebuild_db(params[1:])
        if action == "export":
            return self._export_csv(params[1:])
        if action == "plugin":
            return self._plugin_info()

        # Fall back to existing sonic_handler for plan/run/status
        # (or delegate to existing handler)
        return {"status": "error", "message": f"Unknown action: {action}"}

    def _sync_status(self) -> Dict:
        """Get database sync status."""
        try:
            from library.sonic.sync import get_sync_service

            sync = get_sync_service()
            status = sync.get_status()

            logger.info(f"{LogTags.LOCAL} SONIC: sync status check")

            return {
                "status": "ok",
                "sync": {
                    "last_sync": status.last_sync or "never",
                    "db_exists": status.db_exists,
                    "record_count": status.record_count,
                    "needs_rebuild": status.needs_rebuild,
                    "db_path": status.db_path,
                },
                "message": "Rebuild needed" if status.needs_rebuild else "Database up to date",
            }

        except ImportError:
            return {
                "status": "error",
                "message": "Sonic plugin not installed. Check library/sonic/",
            }
        except Exception as e:
            return {
                "status": "error",
                "message": f"Sync status failed: {e}",
            }

    def _rebuild_db(self, params: List[str]) -> Dict:
        """Rebuild device database from SQL source."""
        force = "--force" in params or "-f" in params

        try:
            from library.sonic.sync import get_sync_service

            sync = get_sync_service()

            # Check if rebuild needed
            status = sync.get_status()
            if not force and not status.needs_rebuild:
                return {
                    "status": "skip",
                    "message": "Database is up to date. Use --force to rebuild anyway.",
                    "record_count": status.record_count,
                }

            logger.info(f"{LogTags.LOCAL} SONIC: rebuilding device database (force={force})")

            # Execute rebuild
            result = sync.rebuild_database(force=force)

            if result["status"] == "ok":
                logger.info(f"{LogTags.LOCAL} SONIC: rebuild complete, {result['record_count']} records")
            else:
                logger.error(f"{LogTags.LOCAL} SONIC: rebuild failed - {result.get('message')}")

            return result

        except ImportError:
            return {
                "status": "error",
                "message": "Sonic plugin not installed.",
            }
        except Exception as e:
            return {
                "status": "error",
                "message": f"Rebuild failed: {e}",
            }

    def _export_csv(self, params: List[str]) -> Dict:
        """Export database to CSV."""
        output_path = None
        if params and not params[0].startswith("--"):
            output_path = Path(params[0])

        try:
            from library.sonic.sync import get_sync_service

            sync = get_sync_service()

            logger.info(f"{LogTags.LOCAL} SONIC: exporting to CSV")

            result = sync.export_to_csv(output_path=output_path)

            if result["status"] == "ok":
                logger.info(f"{LogTags.LOCAL} SONIC: exported {result['record_count']} records to {result['output_path']}")

            return result

        except ImportError:
            return {
                "status": "error",
                "message": "Sonic plugin not installed.",
            }
        except Exception as e:
            return {
                "status": "error",
                "message": f"Export failed: {e}",
            }

    def _plugin_info(self) -> Dict:
        """Get plugin information."""
        try:
            from extensions.sonic_loader import get_sonic_loader

            loader = get_sonic_loader()
            info = loader.get_plugin_info()
            available = loader.is_available()

            logger.info(f"{LogTags.LOCAL} SONIC: plugin info check")

            return {
                "status": "ok",
                "plugin": info,
                "available": available,
            }

        except ImportError:
            return {
                "status": "error",
                "message": "Plugin loader not available.",
            }
        except Exception as e:
            return {
                "status": "error",
                "message": f"Plugin info failed: {e}",
            }

    def _help(self) -> Dict:
        """Show help for extended SONIC commands."""
        return {
            "status": "ok",
            "syntax": [
                "SONIC SYNC           — Check database sync status",
                "SONIC REBUILD [--force] — Rebuild database from SQL",
                "SONIC EXPORT [path]  — Export database to CSV",
                "SONIC PLUGIN         — Show plugin information",
                "",
                "Legacy commands (via sonic/core/sonic_cli.py):",
                "SONIC STATUS         — Show Sonic component status",
                "SONIC PLAN [opts]    — Plan USB layout",
                "SONIC RUN [opts]     — Execute USB build",
            ],
            "note": "Modular plugin system via library/sonic/ and extensions/sonic_loader.py",
        }


# Example: How to use in TUI
def example_tui_usage():
    """
    Example showing how to integrate plugin handler into TUI.

    In core/tui/ucode.py or similar:
    """
    from core.commands.sonic_plugin_handler import SonicPluginHandler

    handler = SonicPluginHandler()

    # User types: SONIC SYNC
    result = handler.handle("SONIC", ["sync"])
    print(result)

    # User types: SONIC REBUILD --force
    result = handler.handle("SONIC", ["rebuild", "--force"])
    print(result)

    # User types: SONIC EXPORT sonic-devices.csv
    result = handler.handle("SONIC", ["export", "sonic-devices.csv"])
    print(result)

    # User types: SONIC PLUGIN
    result = handler.handle("SONIC", ["plugin"])
    print(result)


if __name__ == "__main__":
    """Quick test of plugin handler."""
    handler = SonicPluginHandler()

    print("=== SONIC SYNC ===")
    print(handler.handle("SONIC", ["sync"]))

    print("\n=== SONIC PLUGIN ===")
    print(handler.handle("SONIC", ["plugin"]))

    print("\n=== SONIC HELP ===")
    print(handler.handle("SONIC", []))
