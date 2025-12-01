"""
ASCII/Teletext Map Renderer for uDOS Grid System.

Renders maps with city markers, labels, and teletext-style graphics.
Supports multiple layers, zoom levels, and viewport navigation.
"""

import json
from typing import Dict, List, Tuple, Optional
from pathlib import Path

from core.utils.grid_utils import (
    parse_tile_code,
    column_to_code,
    code_to_column,
    tile_to_latlong,
    calculate_distance_km,
    GRID_COLUMNS,
    GRID_ROWS
)


# Character sets for different terrain/features
TERRAIN_CHARS = {
    'ocean': '~',
    'water': '≈',
    'land': '·',
    'mountain': '▲',
    'desert': '░',
    'forest': '▓',
    'urban': '█',
    'coastal': '▒',
}

MARKER_CHARS = {
    'city': '●',
    'landmark': '◆',
    'poi': '○',
    'user': '▲',
    'capital': '★',
}


class MapRenderer:
    """
    Renders ASCII/teletext-style maps with location markers.
    """

    def __init__(self, project_root: Optional[Path] = None):
        """
        Initialize the map renderer.

        Args:
            project_root: Root directory of project (for loading data)
        """
        self.project_root = project_root or Path(__file__).resolve().parents[2]
        self.cities = []
        self.layers = {}
        self._load_cities()

    def _load_cities(self):
        """Load city data from cities.json."""
        cities_file = self.project_root / "extensions" / "assets" / "data" / "cities.json"

        if cities_file.exists():
            with open(cities_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
                self.cities = data.get("cities", []) if isinstance(data, dict) else data

    def _load_layer(self, layer: int) -> Dict:
        """
        Load layer data from file.

        Args:
            layer: Layer number (100-899)

        Returns:
            Dictionary with layer data
        """
        if layer in self.layers:
            return self.layers[layer]

        layer_file = self.project_root / "extensions" / "assets" / "data" / f"map_layer_{layer}.json"

        if layer_file.exists():
            with open(layer_file, 'r', encoding='utf-8') as f:
                self.layers[layer] = json.load(f)
        else:
            self.layers[layer] = {"layer": layer, "cells": {}}

        return self.layers[layer]

    def calculate_viewport(
        self,
        center_tile: str,
        width: int = 60,
        height: int = 20
    ) -> Dict:
        """
        Calculate which grid cells to display in viewport.

        Args:
            center_tile: Center TILE code (e.g., "JF57-100")
            width: Viewport width in cells
            height: Viewport height in cells

        Returns:
            Dictionary with viewport info
        """
        parsed = parse_tile_code(center_tile)
        center_col = parsed['column_num']
        center_row = parsed['row']

        # Calculate visible range
        half_width = width // 2
        half_height = height // 2

        col_start = max(0, center_col - half_width)
        col_end = min(GRID_COLUMNS - 1, center_col + half_width)
        row_start = max(0, center_row - half_height)
        row_end = min(GRID_ROWS - 1, center_row + half_height)

        return {
            'cols': range(col_start, col_end + 1),
            'rows': range(row_start, row_end + 1),
            'center': (center_col, center_row),
            'width': col_end - col_start + 1,
            'height': row_end - row_start + 1
        }

    def get_cell_marker(self, tile_code: str, layer: int) -> Tuple[str, Optional[str]]:
        """
        Get display character and label for a grid cell.

        Args:
            tile_code: TILE code for cell
            layer: Layer number

        Returns:
            Tuple of (character, label or None)
        """
        grid_cell = tile_code.split('-')[0]

        # Check if there's a city at this location
        for city in self.cities:
            if city.get('grid_cell') == grid_cell and city.get('layer', 100) == layer:
                # Use 3-letter abbreviation for label
                label = city['name'][:3].upper()
                return MARKER_CHARS['city'], label

        # Check layer data
        layer_data = self._load_layer(layer)
        cell_info = layer_data.get('cells', {}).get(grid_cell, {})

        if 'name' in cell_info:
            return MARKER_CHARS.get(cell_info.get('type', 'poi'), '○'), cell_info['name'][:3].upper()

        # Determine terrain based on coordinates
        lat, lon, _ = tile_to_latlong(tile_code)

        # Simple ocean detection (very basic heuristic)
        # TODO: Replace with actual terrain data
        if lat is not None and lon is not None:
            # Rough ocean approximation
            if abs(lat) < 60:  # Not polar
                # Ocean if far from major landmasses (very rough)
                return TERRAIN_CHARS['ocean'], None

        return TERRAIN_CHARS['land'], None

    def render_map(
        self,
        center_tile: str = "JF57-100",  # London default
        width: int = 60,
        height: int = 20,
        show_grid: bool = True,
        show_labels: bool = True,
        show_border: bool = True
    ) -> str:
        """
        Render ASCII map for terminal display.

        Args:
            center_tile: Center TILE code
            width: Map width in characters
            height: Map height in characters
            show_grid: Show grid coordinate labels
            show_labels: Show city labels
            show_border: Show decorative border

        Returns:
            Rendered map as string
        """
        parsed = parse_tile_code(center_tile)
        layer = parsed['layer']

        viewport = self.calculate_viewport(center_tile, width, height)

        lines = []

        # Top border
        if show_border:
            lines.append("┌" + "─" * (width + 2) + "┐")
            layer_info = f"uDOS MAP - Layer {layer} | {center_tile}"
            padding = width + 2 - len(layer_info)
            lines.append(f"│ {layer_info}{' ' * (padding - 2)} │")
            lines.append("├" + "─" * (width + 2) + "┤")

        # Column labels (every 5 columns)
        if show_grid:
            col_labels = "│ "
            for col in viewport['cols']:
                if col % 5 == 0:
                    code = column_to_code(col)
                    col_labels += code
                else:
                    col_labels += "  "
            col_labels += " " * (width - len(col_labels) + 2) + " │"
            lines.append(col_labels)

        # Render grid cells
        cell_labels = {}  # Store labels for later placement

        for row in viewport['rows']:
            line = "│ " if show_border else ""

            # Row label
            if show_grid and row % 10 == 0:
                line += f"{row:3d} "
            else:
                line += "    "

            # Render each cell in row
            for col in viewport['cols']:
                tile_code = f"{column_to_code(col)}{row}-{layer}"
                char, label = self.get_cell_marker(tile_code, layer)

                # Store label position if exists
                if label and show_labels:
                    cell_labels[(col, row)] = label
                    line += "●"  # Use marker for labeled cells
                else:
                    line += char

            # Pad to width
            line += " " * (width - len(line) + (2 if show_border else 0))
            if show_border:
                line += " │"

            lines.append(line)

        # Bottom border
        if show_border:
            lines.append("├" + "─" * (width + 2) + "┤")
            legend = "● City  ○ POI  · Land  ~ Ocean"
            padding = width + 2 - len(legend)
            lines.append(f"│ {legend}{' ' * (padding - 2)} │")
            lines.append("└" + "─" * (width + 2) + "┘")

        # Add labels overlay (simplified - just list cities)
        if show_labels and cell_labels:
            lines.append("\nCities visible:")
            for (col, row), label in sorted(cell_labels.items())[:10]:  # Limit to 10
                tile_code = f"{column_to_code(col)}{row}-{layer}"
                # Find full city name
                grid_cell = tile_code.split('-')[0]
                for city in self.cities:
                    if city.get('grid_cell') == grid_cell:
                        lines.append(f"  ● {city['name']:20} ({tile_code})")
                        break

        return '\n'.join(lines)

    def render_world_map(self, highlight_cities: bool = True) -> str:
        """
        Render complete world map at layer 100.

        Args:
            highlight_cities: Show city markers

        Returns:
            Rendered world map
        """
        # Use center of grid
        center_col = GRID_COLUMNS // 2
        center_row = GRID_ROWS // 2
        center_tile = f"{column_to_code(center_col)}{center_row}-100"

        return self.render_map(
            center_tile=center_tile,
            width=80,
            height=30,
            show_grid=True,
            show_labels=highlight_cities,
            show_border=True
        )

    def render_city_detail(self, city_name: str, layer: int = 300) -> str:
        """
        Render detailed view of a specific city.

        Args:
            city_name: Name of city
            layer: Detail layer (300-500)

        Returns:
            Rendered city detail view
        """
        # Find city
        city = None
        for c in self.cities:
            if c['name'].lower() == city_name.lower():
                city = c
                break

        if not city:
            return f"City not found: {city_name}"

        # Get city TILE code at target layer
        base_tile = city['tile_code']
        parsed = parse_tile_code(base_tile)
        city_tile = f"{parsed['grid_cell']}-{layer}"

        # Render detailed view
        header = f"\n{'='*70}\n{city['name'].upper()} - {city['country']}\n{'='*70}\n"

        map_view = self.render_map(
            center_tile=city_tile,
            width=60,
            height=20,
            show_grid=True,
            show_labels=True,
            show_border=True
        )

        info = f"\nCoordinates: {city['latitude']:.4f}°, {city['longitude']:.4f}°\n"
        info += f"TILE Code: {city_tile}\n"
        info += f"Timezone: {city['timezone'].get('name', 'Unknown')}\n"
        info += f"Climate: {city['climate']}\n"

        return header + map_view + info

    def list_cities_in_view(self, center_tile: str, radius_km: float = 500) -> List[Dict]:
        """
        List all cities within radius of a TILE code.

        Args:
            center_tile: Center TILE code
            radius_km: Search radius in kilometers

        Returns:
            List of cities with distance
        """
        center_lat, center_lon, _ = tile_to_latlong(center_tile)

        if center_lat is None or center_lon is None:
            return []

        nearby = []

        for city in self.cities:
            city_tile = city['tile_code']
            distance = calculate_distance_km(center_tile, city_tile)

            if distance <= radius_km:
                nearby.append({
                    'name': city['name'],
                    'country': city['country'],
                    'tile_code': city_tile,
                    'distance_km': round(distance, 1)
                })

        # Sort by distance
        nearby.sort(key=lambda c: c['distance_km'])

        return nearby


def main():
    """Demo/test the map renderer."""
    renderer = MapRenderer()

    print("\n" + "="*70)
    print("uDOS MAP RENDERER DEMO")
    print("="*70 + "\n")

    # Render world map
    print("🗺️  World Map (Layer 100)\n")
    print(renderer.render_world_map())

    # Render city detail
    print("\n\n🏙️  City Detail View\n")
    print(renderer.render_city_detail("London", layer=300))

    # List nearby cities
    print("\n\n📍 Cities near London (500km radius)\n")
    nearby = renderer.list_cities_in_view("JF57-100", radius_km=500)
    for city in nearby[:10]:
        print(f"  {city['name']:20} {city['distance_km']:6.1f} km  ({city['tile_code']})")


if __name__ == "__main__":
    main()
