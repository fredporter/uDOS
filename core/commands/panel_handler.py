"""
PANEL command handler - Display location information.

Shows detailed location metadata including timezone, coordinates, connections,
and description. Formatted as an informational panel.
"""

from typing import Dict, List, Optional
from core.commands.base import BaseCommandHandler
from core.locations import load_locations, Location
from core.location_service import LocationService
from core.tui.output import OutputToolkit


class PanelHandler(BaseCommandHandler):
    """Display location information panel."""

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
        # Get location ID (from params or player state)
        if params:
            location_id = params[0]
        else:
            # Default to first location if no current location set
            location_id = "L300-BJ10"

        # Load location
        try:
            db = load_locations()
            location = db.get(location_id)
        except Exception as e:
            return {"status": "error", "message": f"Failed to load locations: {str(e)}"}

        if not location:
            return {"status": "error", "message": f"Location {location_id} not found"}

        # Get local time
        try:
            local_time = self.location_service.get_local_time(location_id)
            time_str = self.location_service.get_local_time_str(location_id)
        except Exception as e:
            time_str = f"(Timezone error: {str(e)})"
            local_time = None

        # Build panel
        panel = self._build_panel(location, time_str)

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
        lat_str = (
            f"{location.coordinates.lat:.4f}N"
            if location.coordinates.lat >= 0
            else f"{abs(location.coordinates.lat):.4f}S"
        )
        lon_str = (
            f"{location.coordinates.lon:.4f}E"
            if location.coordinates.lon >= 0
            else f"{abs(location.coordinates.lon):.4f}W"
        )
        lines.append("")
        lines.append(f"Coordinates: {lat_str}, {lon_str}")
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
