"""
MAP command handler - Display location tile grid.

Renders a location's tile grid with objects, sprites, and markers using
ASCII/sextant graphics. Supports viewing current location or any location by ID.
"""

from typing import Dict, List, Optional, Tuple
from core.commands.base import BaseCommandHandler
from core.locations import load_locations, Location


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

        return {
            "status": "success",
            "location_id": location.id,
            "location_name": location.name,
            "region": location.region,
            "layer": location.layer,
            "timezone": location.timezone,
            "grid": grid_display,
            "width": 80,
            "height": 24,
        }

    def _render_grid(self, location: Location) -> str:
        """
        Render location tile grid with ASCII/sextant fallback.

        Args:
            location: Location to render

        Returns:
            String containing rendered grid
        """
        # Get tiles for this location
        tiles = location.tiles
        if not tiles:
            return self._render_empty_grid()

        # Determine grid size
        cell_ids = list(tiles.keys())
        if not cell_ids:
            return self._render_empty_grid()

        # Parse cell coordinates
        rows = set()
        cols = set()
        for cell_id in cell_ids:
            row = self._parse_row(cell_id)
            col = self._parse_col(cell_id)
            if row is not None and col is not None:
                rows.add(row)
                cols.add(col)

        if not rows or not cols:
            return self._render_empty_grid()

        # Build grid
        lines = []

        # Header
        header = f"  {location.name}"
        lines.append(f"┌{header}─" * 4 + "─┐")
        lines.append(f"│ Layer: L{location.layer} | Timezone: {location.timezone}")
        lines.append("├" + "─" * 76 + "┤")

        # Column headers
        col_header = "  "
        for col in sorted(cols):
            col_header += f"{col:3} "
        lines.append(col_header)

        # Grid content
        for row in sorted(rows):
            row_str = f"{row:2} "
            for col in sorted(cols):
                cell_id = f"{self._row_to_char(row)}{self._col_to_char(col)}"
                tile = tiles.get(cell_id)

                if tile:
                    # Render tile content
                    char = self._render_tile(tile)
                else:
                    char = "·"

                row_str += f"{char:3} "

            lines.append(row_str)

        # Footer
        lines.append("├" + "─" * 76 + "┤")
        lines.append(
            "│ Legend: 🏢=Structure  🚗=Vehicle  📍=Waypoint  🎴=Marker  ·=Empty"
        )
        lines.append("└" + "─" * 76 + "┘")

        return "\n".join(lines)

    def _render_empty_grid(self) -> str:
        """Render empty grid placeholder."""
        lines = [
            "┌─ No tiles found ────────────────────────────────────────────┐",
            "│                                                              │",
            "│ This location has no tile data configured.                   │",
            "│ Use PANEL command to view location details.                  │",
            "│                                                              │",
            "└──────────────────────────────────────────────────────────────┘",
        ]
        return "\n".join(lines)

    def _render_tile(self, tile) -> str:
        """
        Render a single tile with its content.

        Prioritize: sprites > objects > markers

        Args:
            tile: Tile object to render

        Returns:
            Single character representation
        """
        # Sprites have priority (usually players/NPCs)
        if tile.sprites:
            return tile.sprites[0].char

        # Objects (structures, terrain)
        if tile.objects:
            return tile.objects[0].char

        # Markers (waypoints, POIs)
        if tile.markers:
            marker = tile.markers[0]
            if marker.type == "waypoint":
                return "●"
            elif marker.type == "poi":
                return "◆"
            elif marker.type == "entrance":
                return "⊡"
            return "◇"

        # Empty tile
        return " "

    @staticmethod
    def _parse_row(cell_id: str) -> Optional[int]:
        """Parse row number from cell ID (e.g., 'AA10' -> 10)."""
        try:
            if len(cell_id) >= 3:
                return int(cell_id[2:])
        except (ValueError, IndexError):
            pass
        return None

    @staticmethod
    def _parse_col(cell_id: str) -> Optional[int]:
        """Parse column from cell ID (e.g., 'AA10' -> 0-25)."""
        try:
            if len(cell_id) >= 2:
                col_char = cell_id[0]
                return ord(col_char.upper()) - ord("A")
        except (ValueError, IndexError):
            pass
        return None

    @staticmethod
    def _row_to_char(row: int) -> str:
        """Convert row number to character (10 -> '10')."""
        return str(row).zfill(2)

    @staticmethod
    def _col_to_char(col: int) -> str:
        """Convert column number to character (0 -> 'A')."""
        return chr(ord("A") + col).upper()
