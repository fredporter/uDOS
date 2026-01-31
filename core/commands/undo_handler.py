"""UNDO command handler - Restore from previous BACKUP using RESTORE."""

from typing import List, Dict
from pathlib import Path
from core.commands.base import BaseCommandHandler
from core.commands.handler_logging_mixin import HandlerLoggingMixin
from core.tui.output import OutputToolkit


class UndoHandler(BaseCommandHandler, HandlerLoggingMixin):
    """Handler for UNDO command - Simple restore from backup (UNDO RESTORE wrapper)."""

    def handle(self, command: str, params: List[str], grid=None, parser=None) -> Dict:
        """Handle UNDO command.

        Args:
            command: Command name (UNDO)
            params: Parameters - currently only supports 'RESTORE'
            grid: Grid object
            parser: Parser object

        Returns:
            Output dict
        """
        with self.trace_command(command, params) as trace:
            result = self._handle_impl(command, params, grid, parser)
            if isinstance(result, dict):
                status = result.get("status")
                if status:
                    trace.set_status(status)
            return result

    def _handle_impl(
        self, command: str, params: List[str], grid=None, parser=None
    ) -> Dict:
        """Handle UNDO command implementation.

        Args:
            command: Command name
            params: [RESTORE|--help]
            grid: Grid object
            parser: Parser object

        Returns:
            Output dict
        """
        # No params or --help shows menu
        if not params or params[0].lower() in ["--help", "-h", "help"]:
            return self._show_help()

        action = params[0].upper()

        # UNDO RESTORE - Simple wrapper for RESTORE command
        if action == "RESTORE":
            return self._undo_restore(params[1:])
        else:
            return {
                "status": "error",
                "message": f"Unknown UNDO action: {action}",
                "hint": "Use: UNDO RESTORE [scope] [--force]",
                "available": ["RESTORE"],
            }

    def _show_help(self) -> Dict:
        """Show UNDO command help.

        Returns:
            Output dict with help text
        """
        help_text = """
╔════════════════════════════════════════╗
║         UNDO COMMAND HELP              ║
╚════════════════════════════════════════╝

UNDO is a simple wrapper around RESTORE that lets you undo
recent changes by restoring from your latest backup.

SYNTAX:
  UNDO [ACTION] [SCOPE] [OPTIONS]

ACTIONS:
  RESTORE       Restore from latest backup (default if no action given)
  --help        Show this help

SCOPE (for RESTORE):
  current       Current directory only (default: workspace)
  +subfolders   Current + subdirectories
  workspace     Entire workspace
  all           Everything (repo root)

OPTIONS:
  --force       Overwrite existing files without confirmation

EXAMPLES:
  # Show help
  UNDO --help

  # Undo changes to workspace (restore from latest backup)
  UNDO RESTORE workspace

  # Undo changes with force overwrite
  UNDO RESTORE workspace --force

  # Undo current directory
  UNDO RESTORE current

WORKFLOW:
  1. Make changes to files
  2. Run: BACKUP workspace my-checkpoint
  3. Make more changes
  4. Want to go back? Run: UNDO RESTORE workspace
  5. Files restored to last BACKUP state

NOTES:
  • UNDO is a simple wrapper around RESTORE
  • Restores from the most recent backup
  • Use BACKUP before making risky changes
  • Backups stored in .backup/ directory
  • All operations logged to audit trail

RECOVERY:
  • View available backups: BACKUP workspace (shows existing)
  • Specify exact backup: RESTORE workspace /path/to/backup
  • See full RESTORE help: HELP RESTORE
"""
        return {"output": help_text.strip(), "status": "info", "command": "UNDO"}

    def _undo_restore(self, params: List[str]) -> Dict:
        """Wrapper for RESTORE command via UNDO.

        Args:
            params: [scope] [--force]

        Returns:
            Output dict
        """
        # Default scope is workspace
        scope = "workspace"
        force = False

        # Parse parameters
        if params:
            if params[0].lower() in ["current", "+subfolders", "workspace", "all"]:
                scope = params[0].lower()
                if len(params) > 1 and params[1].lower() == "--force":
                    force = True
            elif params[0].lower() == "--force":
                force = True

        # Call RESTORE handler
        try:
            from core.commands.maintenance_handler import MaintenanceHandler
            from core.services.logging_service import get_logger
            from core.services.unified_logging import get_unified_logger

            logger = get_logger("undo-handler")
            unified = get_unified_logger()

            # Build params for RESTORE
            restore_params = [scope]
            if force:
                restore_params.append("--force")

            # Create maintenance handler and call RESTORE
            maintenance = MaintenanceHandler()
            result = maintenance._handle_restore(restore_params)

            # Log the UNDO action
            unified.log_core(
                category="undo",
                message=f"UNDO RESTORE executed",
                metadata={
                    "scope": scope,
                    "force": force,
                    "status": result.get("status", "unknown"),
                },
            )

            # Wrap output to indicate it's from UNDO
            if result.get("status") == "success":
                output = result.get("output", "")
                undo_note = f"""
╔════════════════════════════════════════╗
║      UNDO RESTORE SUCCESSFUL           ║
╚════════════════════════════════════════╝

{output}

✅ Changes have been undone.
   Your workspace has been restored to the latest backup state.
"""
                return {
                    "status": "success",
                    "message": result.get("message", "Undo successful"),
                    "output": undo_note,
                    "command": "UNDO",
                }
            else:
                return result

        except Exception as e:
            return {
                "status": "error",
                "message": f"UNDO RESTORE failed: {str(e)}",
                "hint": f"Ensure a backup exists. Try: BACKUP workspace pre-undo",
            }
