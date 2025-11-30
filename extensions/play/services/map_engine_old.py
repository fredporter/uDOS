#!/usr/bin/env python3
"""
uDOS v2.0.0 - Mapping System

Hierarchical TILE code grid system with timezone-based location detection.

Features:
- TILE code system (CONTINENT-COUNTRY-CITY[-DISTRICT[-BLOCK]])
- 5 zoom levels (World → Region → City → District → Block)
- Timezone-based location detection (TIZO/TZONE)
- Multi-layer mapping (SURFACE, CLOUD, SATELLITE, DUNGEON)
- Legacy cell reference support (A1-RL270 format)
- Coordinate conversions

Version: 2.0.0
Author: Fred Porter
"""

import json
import math
import csv
from pathlib import Path
from typing import Dict, List, Tuple, Optional, Union
from datetime import datetime
import sys

# Add project root to path
sys.path.append(str(Path(__file__).parent.parent.parent))
from core.utils.tizo_manager import TIZOLocationManager


class TileCodeSystem:
    """Hierarchical TILE code system for location representation (v2.0.0)."""

    def __init__(self, data_dir="core/data"):
        self.data_dir = Path(data_dir)
        self.locations_data = self._load_locations()
        self.timezone_cities = self.locations_data.get("timezone_cities", {})
        self.tile_system = self.locations_data.get("tile_system", {})
        self.continents = self.tile_system.get("continents", {})

    def _load_locations(self) -> Dict:
        """Load locations.json with TILE code data."""
        locations_file = self.data_dir / "locations.json"
        if locations_file.exists():
            with open(locations_file, 'r') as f:
                return json.load(f)
        return {}

    def tile_to_grid(self, tile_code: str) -> Optional[str]:
        """
        Convert TILE code to grid cell reference.

        Args:
            tile_code: TILE code (e.g., "AS-JP-TYO", "OC-AU-SYD-C1")

        Returns:
            Grid cell (e.g., "Y320", "AA340") or None if not found
        """
        # Check timezone_cities for known tiles
        for tz, city_data in self.timezone_cities.items():
            if city_data.get("tile", "").startswith(tile_code):
                grid_cell = city_data.get("grid_cell")
                if grid_cell:
                    return grid_cell

        # For partial tiles, try to find the base city
        parts = tile_code.split("-")
        if len(parts) >= 3:
            base_tile = "-".join(parts[:3])  # Get city-level tile
            for tz, city_data in self.timezone_cities.items():
                if city_data.get("tile") == base_tile:
                    grid_cell = city_data.get("grid_cell")
                    if grid_cell:
                        return grid_cell

        return None

    def grid_to_tile(self, grid_cell: str, precision: str = "city") -> Optional[str]:
        """
        Convert grid cell to nearest TILE code.

        Args:
            grid_cell: Grid cell reference (e.g., "Y320", "AA340")
            precision: "continent", "city", "district", or "block"

        Returns:
            TILE code or None
        """
        # Find city with matching grid cell
        for tz, city_data in self.timezone_cities.items():
            if city_data.get("grid_cell") == grid_cell:
                return city_data.get("tile")

        return None

    def decode_tile(self, tile_code: str) -> Dict:
        """
        Decode TILE code into human-readable information.

        Args:
            tile_code: TILE code (e.g., "AS-JP-TYO-C5-42")

        Returns:
            Dictionary with decoded information
        """
        parts = tile_code.split("-")

        result = {
            "tile": tile_code,
            "zoom_level": len(parts),
            "parts": {}
        }

        if len(parts) >= 1:
            continent_code = parts[0]
            continent_info = self.continents.get(continent_code, {})
            result["parts"]["continent"] = {
                "code": continent_code,
                "name": continent_info.get("name", "Unknown")
            }

        if len(parts) >= 2:
            result["parts"]["country"] = {
                "code": parts[1],
                "name": self._get_country_name(parts[1])
            }

        if len(parts) >= 3:
            city_code = parts[2]
            # Find city info from timezone_cities
            for tz, city_data in self.timezone_cities.items():
                if city_data.get("tile", "").startswith("-".join(parts[:3])):
                    result["parts"]["city"] = {
                        "code": city_code,
                        "name": city_data.get("name", "Unknown"),
                        "country": city_data.get("country", "Unknown"),
                        "coords": city_data.get("coords", [])
                    }
                    break

        if len(parts) >= 4:
            result["parts"]["district"] = {
                "code": parts[3]
            }

        if len(parts) >= 5:
            result["parts"]["block"] = {
                "code": parts[4]
            }

        return result

    def _get_country_name(self, country_code: str) -> str:
        """Get country name from ISO code."""
        # Basic mapping - expand as needed
        country_map = {
            "AU": "Australia", "JP": "Japan", "UK": "United Kingdom",
            "US": "USA", "DE": "Germany", "IN": "India",
            "CN": "China", "BR": "Brazil", "ZA": "South Africa",
            "NZ": "New Zealand", "SG": "Singapore"
        }
        return country_map.get(country_code, country_code)

    def get_city_by_timezone(self, timezone: str) -> Optional[Dict]:
        """
        Get city data by timezone code.

        Args:
            timezone: Timezone code (e.g., "AEST", "JST")

        Returns:
            City data dictionary or None
        """
        return self.timezone_cities.get(timezone)

    def zoom_out(self, tile_code: str) -> Optional[str]:
        """
        Zoom out by removing the most specific level.

        Args:
            tile_code: Current TILE code

        Returns:
            Parent TILE code or None if already at world level
        """
        parts = tile_code.split("-")
        if len(parts) > 1:
            return "-".join(parts[:-1])
        return None

    def zoom_in(self, tile_code: str, sublevel: str) -> str:
        """
        Zoom in by adding a sublevel.

        Args:
            tile_code: Current TILE code
            sublevel: Sublevel identifier (e.g., "C5", "42")

        Returns:
            New TILE code
        """
        return f"{tile_code}-{sublevel}"

    def get_zoom_level(self, tile_code: str) -> int:
        """
        Get the zoom level (1-5) of a TILE code.

        Returns:
            1=World, 2=Region, 3=City, 4=District, 5=Block
        """
        return len(tile_code.split("-"))


class CellReferenceSystem:
    """APAC-centered 480×270 cell reference system - Production Implementation."""

    # Grid configuration (matches udos_map_480x270_cellkey specs)
    COLS = 480
    ROWS = 270
    LON_CENTRE = 120.0  # APAC center
    LAT_MAX = 85.0
    LAT_MIN = -85.0

    # Cell size for rendering
    CELL_SIZE_PX = (16, 16)
    DEG_PER_COL_AVG = 0.75
    DEG_PER_ROW_AVG = 0.6296296296296297

    @classmethod
    def wrap_longitude(cls, lon: float) -> float:
        """Wrap longitude around APAC center (120°E) - Production Algorithm."""
        shifted = lon - cls.LON_CENTRE
        while shifted < -180.0:
            shifted += 360.0
        while shifted >= 180.0:
            shifted -= 360.0
        return shifted

    @classmethod
    def lon_to_col(cls, lon: float) -> int:
        """Convert longitude to column index (0-based) - Production Algorithm."""
        x = (cls.wrap_longitude(lon) + 180.0) / 360.0 * cls.COLS
        return max(0, min(cls.COLS - 1, int(math.floor(x))))

    @classmethod
    def lat_to_row(cls, lat: float) -> int:
        """Convert latitude to row index (0-based) - Production Algorithm."""
        y = (cls.LAT_MAX - lat) / (cls.LAT_MAX - cls.LAT_MIN) * cls.ROWS
        return max(0, min(cls.ROWS - 1, int(math.floor(y))))

    @classmethod
    def col_to_letters(cls, col: int) -> str:
        """Convert column index to spreadsheet-style letters (A, B, ..., RL) - Production Algorithm."""
        n = col + 1
        letters = ""
        while n > 0:
            n, rem = divmod(n - 1, 26)
            letters = chr(65 + rem) + letters
        return letters

    @classmethod
    def letters_to_col(cls, letters: str) -> int:
        """Convert spreadsheet-style letters to column index (0-based)."""
        col = 0
        for char in letters.upper():
            col = col * 26 + (ord(char) - ord('A') + 1)
        return col - 1

    @classmethod
    def coord_to_cell(cls, lat: float, lon: float) -> str:
        """Convert lat/lon coordinates to cell reference (e.g., 'CR128')."""
        col = cls.lon_to_col(lon)
        row = cls.lat_to_row(lat)
        return f"{cls.col_to_letters(col)}{row + 1}"

    @classmethod
    def cell_to_coord(cls, cell_ref: str) -> Tuple[float, float]:
        """Convert cell reference to approximate lat/lon coordinates."""
        # Extract letters and numbers
        letters = ""
        numbers = ""
        for char in cell_ref:
            if char.isalpha():
                letters += char
            elif char.isdigit():
                numbers += char

        if not letters or not numbers:
            raise ValueError(f"Invalid cell reference: {cell_ref}")

        col = cls.letters_to_col(letters)
        row = int(numbers) - 1  # Convert to 0-based

        # Convert back to coordinates (center of cell)
        lon_wrapped = (col + 0.5) / cls.COLS * 360.0 - 180.0
        lon = lon_wrapped + cls.LON_CENTRE
        if lon > 180.0:
            lon -= 360.0
        elif lon < -180.0:
            lon += 360.0

        lat = cls.LAT_MAX - (row + 0.5) / cls.ROWS * (cls.LAT_MAX - cls.LAT_MIN)

        return lat, lon

    @classmethod
    def get_cell_bounds(cls, cell_ref: str) -> Dict[str, float]:
        """Get the bounding box of a cell."""
        lat_center, lon_center = cls.cell_to_coord(cell_ref)

        lat_span = (cls.LAT_MAX - cls.LAT_MIN) / cls.ROWS
        lon_span = 360.0 / cls.COLS

        return {
            "lat_min": lat_center - lat_span / 2,
            "lat_max": lat_center + lat_span / 2,
            "lon_min": lon_center - lon_span / 2,
            "lon_max": lon_center + lon_span / 2,
            "lat_center": lat_center,
            "lon_center": lon_center
        }


class MapEngine:
    """Mapping engine with TILE code system and legacy cell reference support."""

    def __init__(self, data_dir="core/data"):
        self.data_dir = Path(data_dir)

        # v2.0.0: TILE code system (primary)
        self.tile_system = TileCodeSystem(data_dir)
        self.current_tile = self.tile_system.tile_system.get("default_start", "OC-AU-SYD")
        self.current_layer = "SURFACE"
        self.zoom_level = 3  # City level by default

        # Legacy: Cell reference system (backwards compatibility)
        self.tizo_manager = TIZOLocationManager(data_dir)
        self.cell_system = CellReferenceSystem()

        # Load mapping data
        self.worldmap = self.load_worldmap()
        self.city_cells = {}
        self.world_cities = {}
        self.layers = self._initialize_layers()

        # Initialize with world cities and TIZO locations
        self.load_world_cities()
        self.initialize_tizo_cells()

    def _initialize_layers(self) -> Dict:
        """Initialize default map layers."""
        return {
            "SATELLITE": {"depth": 100, "type": "VIRTUAL", "accessible": True},
            "CLOUD": {"depth": 10, "type": "VIRTUAL", "accessible": True},
            "SURFACE": {"depth": 0, "type": "PHYSICAL", "accessible": True},
            "DUNGEON-1": {"depth": -1, "type": "PHYSICAL", "accessible": True},
            "DUNGEON-2": {"depth": -2, "type": "PHYSICAL", "accessible": False},
            "DUNGEON-3": {"depth": -3, "type": "PHYSICAL", "accessible": False},
            "MINES": {"depth": -10, "type": "PHYSICAL", "accessible": False},
            "CORE": {"depth": -100, "type": "PHYSICAL", "accessible": False}
        }

    # ========== TILE CODE METHODS (v2.0.0) ==========

    def move_to_tile(self, tile_code: str) -> str:
        """Move to a specific TILE location."""
        grid_cell = self.tile_system.tile_to_grid(tile_code)
        if grid_cell is None:
            return f"❌ Invalid TILE code: {tile_code}"

        self.current_tile = tile_code
        self.zoom_level = self.tile_system.get_zoom_level(tile_code)

        tile_info = self.tile_system.decode_tile(tile_code)
        city_name = tile_info.get("parts", {}).get("city", {}).get("name", "Unknown")

        return f"📍 Moved to {tile_code} ({city_name}) @ {grid_cell}"

    def set_location_by_timezone(self, timezone: str) -> str:
        """Set location based on timezone (TIZO detection)."""
        city_data = self.tile_system.get_city_by_timezone(timezone)
        if city_data is None:
            return f"❌ Unknown timezone: {timezone}"

        tile_code = city_data.get("tile")
        city_name = city_data.get("name")
        country = city_data.get("country")

        self.current_tile = tile_code
        self.zoom_level = 3  # City level

        return f"📍 Location set to {city_name}, {country}\n🌏 TILE: {tile_code}\n🕐 Timezone: {timezone} ({city_data.get('offset')})\n🗺️  Zoom Level: {self.zoom_level} (City)"

    def get_current_tile(self) -> str:
        """Get current TILE code."""
        return self.current_tile

    def zoom_in_tile(self, sublevel: str = "C1") -> str:
        """Zoom into a sublayer."""
        if self.zoom_level >= 5:
            return "❌ Already at maximum zoom level (Block)"

        new_tile = self.tile_system.zoom_in(self.current_tile, sublevel)
        self.current_tile = new_tile
        self.zoom_level += 1

        level_names = ["", "World", "Region", "City", "District", "Block"]
        return f"🔍 Zoomed to {level_names[self.zoom_level]} level: {new_tile}"

    def zoom_out_tile(self) -> str:
        """Zoom out to parent layer."""
        if self.zoom_level <= 1:
            return "❌ Already at minimum zoom level (World)"

        parent_tile = self.tile_system.zoom_out(self.current_tile)
        if parent_tile is None:
            return "❌ Cannot zoom out further"

        self.current_tile = parent_tile
        self.zoom_level -= 1

        level_names = ["", "World", "Region", "City", "District", "Block"]
        return f"🔍 Zoomed to {level_names[self.zoom_level]} level: {parent_tile}"

    def change_layer(self, layer_name: str) -> str:
        """Switch to a different layer."""
        layer_name = layer_name.upper()
        if layer_name not in self.layers:
            return f"❌ Unknown layer: {layer_name}"

        layer_info = self.layers[layer_name]
        if not layer_info.get("accessible", False):
            return f"🔒 Layer {layer_name} is not accessible"

        self.current_layer = layer_name
        return f"🔄 Switched to layer: {layer_name} (depth: {layer_info['depth']})"

    def get_current_status(self) -> str:
        """Get formatted status display with TILE information."""
        tile_info = self.tile_system.decode_tile(self.current_tile)
        parts = tile_info.get("parts", {})

        city = parts.get("city", {})
        city_name = city.get("name", "Unknown")
        country = city.get("country", "Unknown")

        continent = parts.get("continent", {})
        continent_name = continent.get("name", "Unknown")

        layer_info = self.layers.get(self.current_layer, {})
        layer_depth = layer_info.get("depth", 0)
        layer_type = layer_info.get("type", "UNKNOWN")

        level_names = ["", "World", "Region", "City", "District", "Block"]
        zoom_name = level_names[self.zoom_level] if self.zoom_level < len(level_names) else "Unknown"

        # Get accessible layers
        accessible = [name for name, data in self.layers.items() if data.get("accessible", False)]

        output = []
        output.append("=" * 60)
        output.append("🗺️  MAP STATUS")
        output.append("=" * 60)
        output.append("")
        output.append(f"📍 Location: {self.current_tile} ({city_name}, {country})")
        output.append(f"🌍 Layer: {self.current_layer}")
        output.append(f"   Depth: {layer_depth}")
        output.append(f"   Type: {layer_type}")
        output.append(f"   Zoom: Level {self.zoom_level} ({zoom_name})")
        output.append("")

        if len(accessible) > 1:
            output.append("🔗 Available Layers:")
            for layer in sorted(accessible, key=lambda x: self.layers[x]['depth'], reverse=True):
                depth = self.layers[layer]['depth']
                symbol = "☁️ " if depth > 0 else "⬇️ " if depth < 0 else "🌍"
                current = " ← YOU ARE HERE" if layer == self.current_layer else ""
                output.append(f"   {symbol} {layer} (depth {depth}){current}")

        output.append("=" * 60)
        return "\n".join(output)

    # ========== LEGACY METHODS (Backwards Compatibility) ==========

    def load_worldmap(self) -> Dict:
        """Load worldmap data."""
        worldmap_file = self.data_dir / "worldmap.json"
        if worldmap_file.exists():
            with open(worldmap_file, 'r') as f:
                return json.load(f)
        return {}

    def load_world_cities(self):
        """Load world cities data with pre-computed cell references."""
        world_cities_file = self.data_dir / "world_cities_cellkeys.csv"
        if not world_cities_file.exists():
            print(f"Warning: World cities file not found: {world_cities_file}")
            return

        try:
            import csv
            with open(world_cities_file, 'r', encoding='utf-8') as f:
                reader = csv.DictReader(f)
                for row in reader:
                    city_code = row['code3']
                    self.world_cities[city_code] = {
                        'name': row['city'],
                        'country': row['country'],
                        'lat': float(row['lat']),
                        'lon': float(row['lon']),
                        'cell_ref': row['cell_code'],
                        'col_index': int(row['col_index0']),
                        'row_index': int(row['row_index0'])
                    }
                    # Also add to city_cells for compatibility
                    self.city_cells[city_code] = self.world_cities[city_code]
        except Exception as e:
            print(f"Error loading world cities: {e}")

    def initialize_tizo_cells(self):
        """Initialize cell references for all TIZO cities."""
        if "TIZO_CITIES" not in self.tizo_manager.tizo_cities:
            return

        for tizo_code, city_data in self.tizo_manager.tizo_cities["TIZO_CITIES"].items():
            lat = city_data["coordinates"]["lat"]
            lon = city_data["coordinates"]["lon"]

            cell_ref = self.cell_system.coord_to_cell(lat, lon)

            self.city_cells[tizo_code] = {
                "name": city_data["name"],
                "country": city_data["country"],
                "continent": city_data["continent"],
                "coordinates": {"lat": lat, "lon": lon},
                "cell_ref": cell_ref,
                "timezone": city_data["timezone"],
                "timezone_offset": city_data["timezone_offset"],
                "population_code": city_data["population_code"],
                "udos_layers": city_data["udos_layers"],
                "connection_quality": city_data["connection_quality"]
            }

    def get_world_city_by_code(self, city_code: str) -> Optional[Dict]:
        """Get world city data by 3-letter code."""
        return self.world_cities.get(city_code.upper())

    def get_world_city_by_cell(self, cell_ref: str) -> Optional[Dict]:
        """Find world city in the specified cell."""
        for city_code, city_data in self.world_cities.items():
            if city_data["cell_ref"] == cell_ref:
                return {
                    "city_code": city_code,
                    **city_data
                }
        return None

    def get_world_cities_in_region(self, center_cell: str, radius_cells: int = 5) -> List[Dict]:
        """Get all world cities within a radius of cells from center."""
        try:
            center_lat, center_lon = self.cell_system.cell_to_coord(center_cell)
            center_col = self.cell_system.lon_to_col(center_lon)
            center_row = self.cell_system.lat_to_row(center_lat)
        except ValueError:
            return []

        cities_in_region = []
        for city_code, city_data in self.world_cities.items():
            col_distance = abs(city_data['col_index'] - center_col)
            row_distance = abs(city_data['row_index'] - center_row)
            cell_distance = max(col_distance, row_distance)

            if cell_distance <= radius_cells:
                cities_in_region.append({
                    "city_code": city_code,
                    "cell_distance": cell_distance,
                    **city_data
                })

        # Sort by cell distance
        cities_in_region.sort(key=lambda x: x["cell_distance"])
        return cities_in_region

    def search_world_cities(self, query: str, limit: int = 10) -> List[Dict]:
        """Search world cities by name or country."""
        query = query.lower()
        results = []

        for city_code, city_data in self.world_cities.items():
            score = 0
            name_lower = city_data['name'].lower()
            country_lower = city_data['country'].lower()

            if query in name_lower:
                score += 100 if name_lower.startswith(query) else 50
            if query in country_lower:
                score += 30
            if query == city_code.lower():
                score += 200

            if score > 0:
                results.append({
                    "city_code": city_code,
                    "score": score,
                    **city_data
                })

        # Sort by score and return top results
        results.sort(key=lambda x: x["score"], reverse=True)
        return results[:limit]

    def get_city_by_cell(self, cell_ref: str) -> Optional[Dict]:
        """Find any city (world or TIZO) in the specified cell."""
        # Check world cities first
        world_city = self.get_world_city_by_cell(cell_ref)
        if world_city:
            return world_city

        # Fall back to TIZO cities
        for tizo_code, city_data in self.city_cells.items():
            if city_data.get("cell_ref") == cell_ref and tizo_code not in self.world_cities:
                return {
                    "tizo_code": tizo_code,
                    **city_data
                }
        return None

    def get_cities_in_region(self, center_cell: str, radius_cells: int = 5) -> List[Dict]:
        """Get all cities within a radius of cells from center."""
        try:
            center_lat, center_lon = self.cell_system.cell_to_coord(center_cell)
        except ValueError:
            return []

        cities_in_region = []

        for tizo_code, city_data in self.city_cells.items():
            city_lat = city_data["coordinates"]["lat"]
            city_lon = city_data["coordinates"]["lon"]

            # Calculate cell distance (approximate)
            city_col = self.cell_system.lon_to_col(city_lon)
            city_row = self.cell_system.lat_to_row(city_lat)
            center_col = self.cell_system.lon_to_col(center_lon)
            center_row = self.cell_system.lat_to_row(center_lat)

            cell_distance = max(abs(city_col - center_col), abs(city_row - center_row))

            if cell_distance <= radius_cells:
                cities_in_region.append({
                    "tizo_code": tizo_code,
                    "cell_distance": cell_distance,
                    **city_data
                })

        # Sort by cell distance
        cities_in_region.sort(key=lambda x: x["cell_distance"])
        return cities_in_region

    def generate_ascii_map(self, center_cell: str, width: int = 40, height: int = 20) -> str:
        """Generate ASCII map view centered on a cell."""
        try:
            center_lat, center_lon = self.cell_system.cell_to_coord(center_cell)
            center_col = self.cell_system.lon_to_col(center_lon)
            center_row = self.cell_system.lat_to_row(center_lat)
        except ValueError:
            return f"Invalid cell reference: {center_cell}"

        # Calculate view bounds
        half_width = width // 2
        half_height = height // 2

        start_col = max(0, center_col - half_width)
        end_col = min(self.cell_system.COLS - 1, center_col + half_width)
        start_row = max(0, center_row - half_height)
        end_row = min(self.cell_system.ROWS - 1, center_row + half_height)

        # Build ASCII map
        lines = []
        lines.append(f"ASCII Map View - Center: {center_cell}")
        lines.append("=" * width)

        for row in range(start_row, end_row + 1):
            line = ""
            for col in range(start_col, end_col + 1):
                if col == center_col and row == center_row:
                    char = "◉"  # Center marker
                else:
                    # Check for cities in this cell
                    cell_ref = f"{self.cell_system.col_to_letters(col)}{row + 1}"
                    city = self.get_city_by_cell(cell_ref)
                    if city:
                        # Use first letter of TIZO code
                        char = city["tizo_code"][0]
                    else:
                        # Ocean/land representation (simplified)
                        char = "~" if (col + row) % 3 == 0 else "."

                line += char

            lines.append(line)

        lines.append("=" * width)
        lines.append("Legend: ◉=Center, Letters=Cities, ~=Ocean, .=Land")

        return "\n".join(lines)

    def get_navigation_info(self, current_cell: str, target_cell: str) -> Dict:
        """Get navigation information between two cells."""
        try:
            current_lat, current_lon = self.cell_system.cell_to_coord(current_cell)
            target_lat, target_lon = self.cell_system.cell_to_coord(target_cell)
        except ValueError as e:
            return {"error": str(e)}

        # Calculate distance using Haversine formula
        distance_km = self.calculate_distance(current_lat, current_lon, target_lat, target_lon)

        # Calculate cell distance
        current_col = self.cell_system.lon_to_col(current_lon)
        current_row = self.cell_system.lat_to_row(current_lat)
        target_col = self.cell_system.lon_to_col(target_lon)
        target_row = self.cell_system.lat_to_row(target_lat)

        cell_distance = max(abs(target_col - current_col), abs(target_row - current_row))

        # Calculate bearing
        bearing = self.calculate_bearing(current_lat, current_lon, target_lat, target_lon)

        return {
            "current_cell": current_cell,
            "target_cell": target_cell,
            "distance_km": round(distance_km, 1),
            "cell_distance": cell_distance,
            "bearing": round(bearing, 1),
            "direction": self.bearing_to_direction(bearing)
        }

    def calculate_distance(self, lat1: float, lon1: float, lat2: float, lon2: float) -> float:
        """Calculate distance between two points using Haversine formula."""
        lat1, lon1, lat2, lon2 = map(math.radians, [lat1, lon1, lat2, lon2])

        dlat = lat2 - lat1
        dlon = lon2 - lon1
        a = math.sin(dlat/2)**2 + math.cos(lat1) * math.cos(lat2) * math.sin(dlon/2)**2
        c = 2 * math.asin(math.sqrt(a))

        # Earth radius in kilometers
        r = 6371
        return c * r

    def calculate_bearing(self, lat1: float, lon1: float, lat2: float, lon2: float) -> float:
        """Calculate bearing from point 1 to point 2."""
        lat1, lon1, lat2, lon2 = map(math.radians, [lat1, lon1, lat2, lon2])

        dlon = lon2 - lon1
        y = math.sin(dlon) * math.cos(lat2)
        x = math.cos(lat1) * math.sin(lat2) - math.sin(lat1) * math.cos(lat2) * math.cos(dlon)

        bearing = math.atan2(y, x)
        bearing = math.degrees(bearing)
        bearing = (bearing + 360) % 360

        return bearing

    def bearing_to_direction(self, bearing: float) -> str:
        """Convert bearing to compass direction."""
        directions = ["N", "NNE", "NE", "ENE", "E", "ESE", "SE", "SSE",
                     "S", "SSW", "SW", "WSW", "W", "WNW", "NW", "NNW"]
        index = round(bearing / 22.5) % 16
        return directions[index]

    def export_city_cells(self, output_file: str):
        """Export TIZO cities with cell references to CSV."""
        with open(output_file, 'w', newline='', encoding='utf-8') as f:
            writer = csv.writer(f)
            writer.writerow([
                "tizo_code", "city", "country", "continent",
                "lat", "lon", "cell_ref", "timezone", "timezone_offset",
                "population_code", "connection_quality"
            ])

            for tizo_code, city_data in self.city_cells.items():
                writer.writerow([
                    tizo_code,
                    city_data["name"],
                    city_data["country"],
                    city_data["continent"],
                    city_data["coordinates"]["lat"],
                    city_data["coordinates"]["lon"],
                    city_data["cell_ref"],
                    city_data["timezone"],
                    city_data["timezone_offset"],
                    city_data["population_code"],
                    json.dumps(city_data["connection_quality"])
                ])

    def get_layer_access(self, tizo_code: str) -> List[str]:
        """Get accessible layers for a TIZO location."""
        if tizo_code in self.city_cells:
            return self.city_cells[tizo_code]["udos_layers"]
        return ["SURFACE"]


def main():
    """Test the mapping system."""
    print("🗺️  uDOS Mapping System Test")
    print("=" * 50)

    # Initialize mapping engine
    engine = MapEngine()

    # Test Melbourne location
    mel_data = engine.city_cells.get("MEL")
    if mel_data:
        print(f"\n📍 Melbourne (MEL):")
        print(f"  Cell Reference: {mel_data['cell_ref']}")
        print(f"  Coordinates: {mel_data['coordinates']['lat']}, {mel_data['coordinates']['lon']}")
        print(f"  Timezone: {mel_data['timezone']} ({mel_data['timezone_offset']})")

        # Test cell to coordinate conversion
        cell_lat, cell_lon = engine.cell_system.cell_to_coord(mel_data['cell_ref'])
        print(f"  Cell Center: {cell_lat:.2f}, {cell_lon:.2f}")

        # Show nearby cities
        print(f"\n🏙️  Cities near {mel_data['cell_ref']}:")
        nearby = engine.get_cities_in_region(mel_data['cell_ref'], 10)
        for city in nearby[:5]:
            print(f"  {city['name']} ({city['tizo_code']}) - {city['cell_ref']} - {city['cell_distance']} cells away")

        # Test navigation
        syd_data = engine.city_cells.get("SYD")
        if syd_data:
            nav_info = engine.get_navigation_info(mel_data['cell_ref'], syd_data['cell_ref'])
            print(f"\n🧭 Navigation MEL → SYD:")
            print(f"  Distance: {nav_info['distance_km']} km")
            print(f"  Cell Distance: {nav_info['cell_distance']} cells")
            print(f"  Bearing: {nav_info['bearing']}° ({nav_info['direction']})")

        # Generate ASCII map
        print(f"\n🗺️  ASCII Map View (Melbourne region):")
        ascii_map = engine.generate_ascii_map(mel_data['cell_ref'], 30, 10)
        print(ascii_map)

    # Export city data
    print("\n💾 Exporting city cell data...")
    engine.export_city_cells("output/tizo_city_cells.csv")
    print("✅ Exported to output/tizo_city_cells.csv")

    print(f"\n🎉 Mapping system test complete!")


if __name__ == "__main__":
    main()
