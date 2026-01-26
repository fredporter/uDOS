"""
MAP command handler - Display location tile grid.

Renders a location's tile grid with objects, sprites, and markers using
ASCII/sextant graphics. Supports viewing current location or any location by ID.
"""

from typing import Dict, List, Optional, Tuple
from .base import BaseCommandHandler
from core.locations import load_locations, Location
from core.services.map_renderer import MapRenderer


class MapHandler(BaseCommandHandler):
    """Display location tile grid."""

    def handle(self, command: str, params: List[str], grid, parser) -> Dict:
        """
        Handle MAP command.

        Args:
            command: "MAP"
            params: [location_id] or empty for current location
            grid: TUI grid for rendering
            parser: Command parser

        Returns:
            Dict with status, location info, and rendered grid
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

        # Render grid
        try:
            grid_display = self._render_grid(location)
        except Exception as e:
            return {"status": "error", "message": f"Failed to render grid: {str(e)}"}

        # Import OutputToolkit only when needed (avoid circular import)
        from core.tui.output import OutputToolkit

        renderer = MapRenderer()
        cols = renderer.cols
        rows = renderer.rows
        output = "\n".join(
            [
                OutputToolkit.banner(f"MAP {location.id}"),
                grid_display,
            ]
        )

        return {
            "status": "success",
            "message": f"Map for {location.name}",
            "output": output,
            "location_id": location.id,
            "location_name": location.name,
            "region": location.region,
            "layer": location.layer,
            "timezone": location.timezone,
            "grid": grid_display,
            "width": cols,
            "height": rows,
        }

    def _render_grid(self, location: Location) -> str:
        renderer = MapRenderer()
        return renderer.render(location)
