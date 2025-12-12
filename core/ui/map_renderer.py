"""
ASCII/Teletext Map Renderer for uDOS Grid System.

Renders maps with city markers, labels, and teletext-style graphics.
Supports multiple layers, zoom levels, and viewport navigation.

Extended in v1.2.14 to support Layer 600-650 grid rendering for
MeshCore networking and Sonic Screwdriver firmware provisioning.
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
from core.utils.column_formatter import ColumnFormatter, ColumnConfig

# v1.2.14: Import grid rendering system for Layer 600-650
try:
    from core.ui.grid_renderer import GridRenderer, ViewportTier
    from core.ui.grid_template_loader import GridTemplateLoader
    GRID_SUPPORT = True
except ImportError:
    GRID_SUPPORT = False


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
        self.formatter = ColumnFormatter(ColumnConfig(width=80))
        self._load_cities()
        
        # v1.2.14: Initialize grid renderer for Layer 600-650
        if GRID_SUPPORT:
            self.grid_renderer = GridRenderer()
            self.template_loader = GridTemplateLoader()
        else:
            self.grid_renderer = None
            self.template_loader = None

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

    def render_grid_layer(
        self,
        tile_code: str,
        layer: int = 600,
        template: Optional[str] = None,
        viewport: Optional[ViewportTier] = None
    ) -> str:
        """
        Render Layer 600-650 grid visualization.
        
        Args:
            tile_code: Base TILE code (e.g., "AA340-600")
            layer: Layer number (600-650)
            template: Template name (meshcore_topology, screwdriver_status, etc.)
            viewport: Viewport tier (auto-detect if None)
            
        Returns:
            Rendered grid string
        """
        if not GRID_SUPPORT:
            return "Grid rendering not available (missing grid_renderer module)"
        
        # Validate layer range
        if not (600 <= layer <= 899):
            return f"Layer {layer} not supported for grid rendering (use 600-899)"
        
        # Auto-detect viewport if not specified
        if viewport is None:
            viewport = ViewportTier.STANDARD
        
        # If template specified, use template loader
        if template:
            if self.template_loader:
                try:
                    # Extract base TILE from tile_code
                    parsed = parse_tile_code(tile_code)
                    base_tile = parsed['grid_cell']
                    
                    # Render template with tile variable
                    variables = {'tile_base': base_tile}
                    return self.template_loader.render_template(template, variables)
                except Exception as e:
                    return f"Template rendering failed: {e}"
            else:
                return "Template loader not available"
        
        # Default: render empty grid with layer info
        self.grid_renderer.set_viewport(viewport)
        self.grid_renderer.create_grid(4, viewport.columns)
        
        parsed = parse_tile_code(tile_code)
        self.grid_renderer.header = f"Layer {layer} - {parsed['grid_cell']} Grid View"
        self.grid_renderer.footer = "Use MESH or SCREWDRIVER commands to populate grid"
        
        return self.grid_renderer.render(border=True)
    
    def render_meshcore_topology(
        self,
        tile_code: str,
        viewport: Optional[ViewportTier] = None
    ) -> str:
        """
        Render MeshCore network topology grid (Layer 600-609).
        
        Args:
            tile_code: Base TILE code
            viewport: Viewport tier
            
        Returns:
            Rendered network topology grid
        """
        return self.render_grid_layer(
            tile_code,
            layer=600,
            template='meshcore_topology',
            viewport=viewport
        )
    
    def render_meshcore_heatmap(
        self,
        tile_code: str,
        viewport: Optional[ViewportTier] = None
    ) -> str:
        """
        Render MeshCore signal strength heatmap (Layer 600-609).
        
        Args:
            tile_code: Base TILE code
            viewport: Viewport tier
            
        Returns:
            Rendered signal heatmap
        """
        return self.render_grid_layer(
            tile_code,
            layer=600,
            template='meshcore_heatmap',
            viewport=viewport
        )
    
    def render_screwdriver_status(
        self,
        tile_code: str,
        viewport: Optional[ViewportTier] = None
    ) -> str:
        """
        Render Sonic Screwdriver firmware status grid (Layer 650).
        
        Args:
            tile_code: Base TILE code
            viewport: Viewport tier
            
        Returns:
            Rendered firmware status grid
        """
        return self.render_grid_layer(
            tile_code,
            layer=650,
            template='screwdriver_status',
            viewport=viewport
        )
    
    def render_screwdriver_devices(
        self,
        tile_code: str,
        device_manager = None,
        viewport: Optional[ViewportTier] = None
    ) -> str:
        """
        Render Sonic Screwdriver device grid with live firmware status.
        
        Args:
            tile_code: TILE code for device grid
            device_manager: MeshCoreDeviceManager instance
            viewport: Viewport tier
            
        Returns:
            Rendered device grid with firmware status
        """
        if not GRID_SUPPORT:
            return "Grid rendering not available"
        
        if device_manager is None:
            try:
                from extensions.play.meshcore_device_manager import MeshCoreDeviceManager
                device_manager = MeshCoreDeviceManager()
            except ImportError:
                return "Device manager not available"
        
        # Parse tile code
        tile_base = tile_code.split('-')[0] if '-' in tile_code else tile_code
        
        # Get devices in this tile
        devices = [d for d in device_manager.devices.values() if d.tile == tile_base]
        
        if not devices:
            return f"No devices found in tile {tile_base}"
        
        # Create grid
        renderer = GridRenderer()
        viewport = viewport or ViewportTier.from_width(80)
        
        lines = []
        lines.append(f"Sonic Screwdriver - Firmware Status (Layer 650)")
        lines.append(f"Tile: {tile_base}  |  Devices: {len(devices)}")
        lines.append("")
        
        # Header
        lines.append(f"{'Device':<8} {'Type':<12} {'Version':<10} {'Status':<8} {'Bank':<6} {'Signal':<8}")
        lines.append("-" * 60)
        
        # Device rows with firmware status
        for device in devices:
            # Determine active bank (simulated)
            active_bank = "A"  # Would come from provisioner in real usage
            
            # Firmware status symbol
            status_map = {
                "✓": "CURRENT",
                "⚠": "OUTDATED",
                "✗": "INCOMPAT"
            }
            status_name = status_map.get(device.firmware_status.value, "UNKNOWN")
            
            lines.append(
                f"{device.id:<8} "
                f"{device.type.value:<12} "
                f"v{device.firmware_version:<9} "
                f"{device.firmware_status.value:<8} "
                f"{active_bank:<6} "
                f"{device.signal:>3}%"
            )
        
        lines.append("")
        
        # Summary
        total = len(devices)
        current = sum(1 for d in devices if d.firmware_status.value == "✓")
        outdated = sum(1 for d in devices if d.firmware_status.value == "⚠")
        incompatible = sum(1 for d in devices if d.firmware_status.value == "✗")
        
        lines.append(f"Summary: {current} current, {outdated} outdated, {incompatible} incompatible")
        
        return '\n'.join(lines)
    
    def render_screwdriver_flash_progress(
        self,
        device_id: str,
        flash_manager = None,
        viewport: Optional[ViewportTier] = None
    ) -> str:
        """
        Render live firmware flash progress for device.
        
        Args:
            device_id: Device being flashed
            flash_manager: FlashPackManager instance
            viewport: Viewport tier
            
        Returns:
            Rendered flash progress grid
        """
        if not GRID_SUPPORT:
            return "Grid rendering not available"
        
        if flash_manager is None:
            try:
                from extensions.play.screwdriver_flash_packs import FlashPackManager
                flash_manager = FlashPackManager()
            except ImportError:
                return "Flash manager not available"
        
        # Get flash progress
        progress = flash_manager.get_flash_progress(device_id)
        
        if not progress:
            return f"No active flash operation for {device_id}"
        
        lines = []
        lines.append(f"Firmware Flash Progress - {device_id}")
        lines.append("")
        
        # Progress bar
        bar_width = 40
        filled = int(bar_width * progress.percentage / 100)
        bar = "█" * filled + "░" * (bar_width - filled)
        
        lines.append(f"Stage: {progress.stage.value}")
        lines.append(f"Progress: [{bar}] {progress.percentage}%")
        lines.append(f"Written: {progress.bytes_written:,} / {progress.total_bytes:,} bytes")
        
        if progress.elapsed_seconds > 0:
            lines.append(f"Elapsed: {progress.elapsed_seconds:.1f}s")
            if progress.percentage > 0:
                remaining = progress.estimated_remaining
                lines.append(f"Remaining: ~{remaining:.1f}s")
        
        if progress.error_message:
            lines.append("")
            lines.append(f"Error: {progress.error_message}")
        
        return '\n'.join(lines)
    
    def render_screwdriver_job_status(
        self,
        job_id: str,
        provisioner = None,
        viewport: Optional[ViewportTier] = None
    ) -> str:
        """
        Render provision job status grid.
        
        Args:
            job_id: Provision job ID
            provisioner: ScrewdriverProvisioner instance
            viewport: Viewport tier
            
        Returns:
            Rendered job status grid
        """
        if not GRID_SUPPORT:
            return "Grid rendering not available"
        
        if provisioner is None:
            try:
                from extensions.play.screwdriver_provisioner import ScrewdriverProvisioner
                provisioner = ScrewdriverProvisioner()
            except ImportError:
                return "Provisioner not available"
        
        # Get job
        job = provisioner.get_job_status(job_id)
        
        if not job:
            return f"Job {job_id} not found"
        
        lines = []
        lines.append(f"Provision Job Status - {job.job_id}")
        lines.append("")
        
        lines.append(f"Status: {job.status}")
        lines.append(f"Strategy: {job.strategy.value}")
        lines.append(f"Target Version: v{job.target_version}")
        lines.append("")
        
        lines.append(f"Devices: {len(job.device_ids)}")
        lines.append(f"  ✓ Success: {job.success_count}")
        lines.append(f"  ✗ Failures: {job.failure_count}")
        lines.append(f"  ⟲ Rollbacks: {job.rollback_count}")
        lines.append("")
        
        # Progress bar
        if len(job.device_ids) > 0:
            completed = job.success_count + job.failure_count
            pct = int(100 * completed / len(job.device_ids))
            bar_width = 40
            filled = int(bar_width * pct / 100)
            bar = "█" * filled + "░" * (bar_width - filled)
            
            lines.append(f"Progress: [{bar}] {pct}%")
            lines.append(f"Completed: {completed}/{len(job.device_ids)}")
        
        return '\n'.join(lines)
    
    def auto_select_viewport(self, terminal_width: int) -> ViewportTier:
        """
        Auto-detect optimal viewport tier based on terminal width.
        
        Args:
            terminal_width: Terminal width in characters
            
        Returns:
            Appropriate ViewportTier
        """
        if not GRID_SUPPORT:
            return None
        
        return ViewportTier.from_width(terminal_width)


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
    
    # v1.2.14: Demo grid rendering for Layer 600-650
    if GRID_SUPPORT:
        print("\n\n" + "="*70)
        print("Layer 600-650 Grid Rendering (v1.2.14)")
        print("="*70 + "\n")
        
        print("🌐 MeshCore Network Topology (Layer 600)\n")
        print(renderer.render_meshcore_topology("JF57-600"))
        
        print("\n\n📡 MeshCore Signal Heatmap (Layer 600)\n")
        print(renderer.render_meshcore_heatmap("JF57-600"))
        
        print("\n\n🔧 Sonic Screwdriver Firmware Status (Layer 650)\n")
        print(renderer.render_screwdriver_status("JF57-650"))
        
        print("\n\n✅ Grid rendering integration complete!")
    else:
        print("\n\n⚠️  Grid rendering not available (install grid_renderer module)")


if __name__ == "__main__":
    main()
