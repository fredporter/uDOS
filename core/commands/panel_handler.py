"""
PANEL command handler - Display location information.

Shows detailed location metadata including timezone, connections,
and description. Formatted as an informational panel.

Includes instrumentation via HandlerLoggingMixin for performance tracking.
"""

from typing import Dict, List, Optional
from core.commands.base import BaseCommandHandler
from core.commands.handler_logging_mixin import HandlerLoggingMixin
from core.locations import load_locations, Location
from core.location_service import LocationService


class PanelHandler(BaseCommandHandler, HandlerLoggingMixin):
    """Display location information panel with automatic logging."""

    def __init__(self):
        """Initialize panel handler."""
        super().__init__()
        self.location_service = LocationService()

    def handle(self, command: str, params: List[str], grid, parser) -> Dict:
        """
        Handle PANEL command.

        Args:
            command: "PANEL"
            params: [location_id] or empty for current location
            grid: TUI grid for rendering
            parser: Command parser

        Returns:
            Dict with status and formatted panel
        """
        with self.trace_command(command, params) as trace:
            # Get location ID (from params or player state)
            if params:
                location_id = params[0]
            else:
                # Default to first location if no current location set
                location_id = "L300-BJ10"

            trace.mark_milestone('location_id_determined')

            # Load location
            try:
                db = load_locations()
                location = db.get(location_id)
                trace.add_event('location_loaded', {'location_id': location_id})
            except Exception as e:
                trace.record_error(e)
                trace.set_status('error')
                self.log_operation(command, 'location_load_failed', {
                    'location_id': location_id,
                    'error': str(e)
                })
                return {"status": "error", "message": f"Failed to load locations: {str(e)}"}

            if not location:
                trace.set_status('error')
                self.log_operation(command, 'location_not_found', {
                    'location_id': location_id
                })
                return {"status": "error", "message": f"Location {location_id} not found"}

            trace.mark_milestone('location_validated')

            # Get local time
            try:
                local_time = self.location_service.get_local_time(location_id)
                time_str = self.location_service.get_local_time_str(location_id)
                trace.add_event('local_time_calculated', {
                    'timezone': location.timezone,
                    'time': time_str[:20]
                })
            except Exception as e:
                time_str = f"(Timezone error: {str(e)})"
                local_time = None
                trace.add_event('timezone_error', {
                    'timezone': location.timezone,
                    'error': str(e)
                })

            trace.mark_milestone('timezone_resolved')

            # Build panel
            try:
                panel = self._build_panel(location, time_str)
                trace.add_event('panel_built', {
                    'panel_size': len(panel),
                    'location_id': location.id,
                    'location_name': location.name,
                    'tile_count': len(location.tiles),
                    'connection_count': len(location.connections) if location.connections else 0
                })
            except Exception as e:
                trace.record_error(e)
                trace.set_status('error')
                self.log_operation(command, 'panel_build_failed', {
                    'location_id': location_id,
                    'error': str(e)
                })
                raise

            trace.mark_milestone('panel_formatted')
            trace.set_status('success')

            return {
                "status": "success",
                "location_id": location.id,
                "location_name": location.name,
                "panel": panel,
                "output": panel,
                "height": 24,
                "full_location": location,
            }

    def _build_panel(self, location: Location, time_str: str) -> str:
        """
        Build location information panel.

        Args:
            location: Location to display
            time_str: Formatted local time string

        Returns:
            Formatted panel string
        """
        from core.tui.output import OutputToolkit
        
        lines = []
        lines.append(OutputToolkit.banner("LOCATION PANEL"))
        lines.append(f"Name: {location.name}")
        lines.append("")

        # Metadata section
        meta_rows = [
            ["region", location.region],
            ["type", f"{location.type} ({location.region_type})"],
            ["layer", f"L{location.layer} ({location.scale})"],
            ["continent", location.continent],
        ]
        lines.append(OutputToolkit.table(["field", "value"], meta_rows))

        # Geographic information
        lines.append("")
        lines.append(f"Timezone: {location.timezone}")
        lines.append(f"Local Time: {time_str}")

        # Description section
        lines.append("")
        lines.append("Description:")

        # Wrap description
        desc = location.description
        if not desc:
            desc = "(No description available)"

        wrapped = self._wrap_text(desc, 66)
        for line in wrapped:
            lines.append(f"  {line}")

        # Connections section
        lines.append("")
        lines.append("Exits:")

        if location.connections:
            for i, conn in enumerate(
                location.connections[:5]
            ):  # Show up to 5 connections
                direction = conn.direction.capitalize()
                label = conn.label[:50]  # Truncate long labels
                lines.append(f"  {direction:6} -> {label}")

            if len(location.connections) > 5:
                remaining = len(location.connections) - 5
                lines.append(f"  ... and {remaining} more connection(s)")
        else:
            lines.append("  (No connections)")

        # Tile markers count
        tile_count = len(location.tiles)
        marker_count = sum(len(t.markers) for t in location.tiles.values())
        sprite_count = sum(len(t.sprites) for t in location.tiles.values())
        obj_count = sum(len(t.objects) for t in location.tiles.values())

        lines.append("")
        lines.append(
            f"Grid Content: {tile_count} cells, {sprite_count} sprites, {obj_count} objects"
        )

        return "\n".join(lines)

    @staticmethod
    def _wrap_text(text: str, width: int) -> List[str]:
        """
        Wrap text to specified width.

        Args:
            text: Text to wrap
            width: Maximum line width

        Returns:
            List of wrapped lines
        """
        lines = []
        current_line = ""

        for word in text.split():
            if len(current_line) + len(word) + 1 <= width:
                if current_line:
                    current_line += " "
                current_line += word
            else:
                if current_line:
                    lines.append(current_line)
                current_line = word

        if current_line:
            lines.append(current_line)

        return lines if lines else ["(No description available)"]
