"""
uDOS v1.0.0 - Grid Command Handler

Handles grid/panel operations (deprecated)
Most grid commands have been removed. This handler provides
migration messages to newer alternatives.
"""

from .base_handler import BaseCommandHandler


class GridCommandHandler(BaseCommandHandler):
    """Handles grid module commands (mostly deprecated)."""

    def handle(self, command, params, grid):
        """
        Handle grid commands - most have been removed.

        Args:
            command: Command name
            params: Command parameters
            grid: Grid instance

        Returns:
            Migration message or error
        """
        if command in ["PANEL", "CREATE", "LIST", "SHOW", "DISPLAY", "PANELS"]:
            return (f"❌ GRID panel commands have been removed in uDOS v1.0\n\n"
                   f"The panel system has been simplified. Commands now work\n"
                   f"directly with files and the terminal output.\n\n"
                   f"💡 Alternatives:\n"
                   f"   • Use TREE to view repository structure\n"
                   f"   • Use EDIT to edit files\n"
                   f"   • Use SHOW to view files\n")
        else:
            return self.get_message("ERROR_UNKNOWN_GRID_COMMAND", command=command)
