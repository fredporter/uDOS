"""
Map Renderer (Core)

Render location grids in ASCII form based on grid config.
"""

from typing import Optional

from core.locations import Location
from core.services.grid_config import load_grid_config


class MapRenderer:
    """ASCII grid rendering for locations."""

    def __init__(self):
        grid_cfg = load_grid_config()
        standard = grid_cfg.get("viewports", {}).get("standard", {})
        self.cols = int(standard.get("cols", 80))
        self.rows = int(standard.get("rows", 30))

    def render(self, location: Location) -> str:
        tiles = location.tiles
        if not tiles:
            return self._render_empty_grid()

        cell_ids = list(tiles.keys())
        if not cell_ids:
            return self._render_empty_grid()

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

        lines = []
        header = f"{location.name}"
        lines.append("+" + "-" * 78 + "+")
        lines.append(f"| {header:<76} |")
        lines.append(
            f"| Layer: L{location.layer} | Timezone: {location.timezone:<56} |"
        )
        lines.append("+" + "-" * 78 + "+")

        col_header = "   "
        for col in sorted(cols):
            col_header += f"{col:3} "
        lines.append(col_header)

        for row in sorted(rows):
            row_str = f"{row:2} "
            for col in sorted(cols):
                cell_id = f"{self._row_to_char(row)}{self._col_to_char(col)}"
                tile = tiles.get(cell_id)
                if tile:
                    char = self._render_tile(tile)
                else:
                    char = "."
                row_str += f"{char:3} "
            lines.append(row_str)

        lines.append("+" + "-" * 78 + "+")
        lines.append("| Legend: S=Structure V=Vehicle W=Waypoint P=POI M=Marker .=Empty |")
        lines.append("+" + "-" * 78 + "+")
        return "\n".join(lines)

    def _render_empty_grid(self) -> str:
        lines = [
            "+" + "-" * 62 + "+",
            "| No tiles found                                              |",
            "| This location has no tile data configured.                   |",
            "| Use PANEL command to view location details.                  |",
            "+" + "-" * 62 + "+",
        ]
        return "\n".join(lines)

    def _render_tile(self, tile) -> str:
        if tile.sprites:
            return tile.sprites[0].char
        if tile.objects:
            return tile.objects[0].char
        if tile.markers:
            marker = tile.markers[0]
            if marker.type == "waypoint":
                return "W"
            if marker.type == "poi":
                return "P"
            if marker.type == "entrance":
                return "E"
            return "M"
        return " "

    @staticmethod
    def _parse_row(cell_id: str) -> Optional[int]:
        try:
            if len(cell_id) >= 3:
                return int(cell_id[2:])
        except (ValueError, IndexError):
            pass
        return None

    @staticmethod
    def _parse_col(cell_id: str) -> Optional[int]:
        try:
            if len(cell_id) >= 2:
                col_char = cell_id[0]
                return ord(col_char.upper()) - ord("A")
        except (ValueError, IndexError):
            pass
        return None

    @staticmethod
    def _row_to_char(row: int) -> str:
        return str(row).zfill(2)

    @staticmethod
    def _col_to_char(col: int) -> str:
        return chr(ord("A") + col).upper()
