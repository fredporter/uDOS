"""
uDOS v1.0.20b - Enhanced Map Data Manager
Handles TILE system, world geography, and ASCII/Teletext map rendering
"""

import json
import math
from pathlib import Path
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass


@dataclass
class TileData:
    """Represents a single TILE in the world map."""
    tile_id: str
    lat: float
    lon: float
    terrain: str
    elevation: int = 0
    climate: Optional[str] = None
    country: Optional[str] = None
    timezone: Optional[str] = None
    city: Optional[str] = None
    tizo: Optional[str] = None
    population: int = 0
    biome: Optional[str] = None
    water_bodies: List[str] = None
    landmarks: List[str] = None
    resources: List[str] = None
    ascii_char: Optional[str] = None
    teletext_char: Optional[str] = None
    color: Optional[str] = None

    def __post_init__(self):
        if self.water_bodies is None:
            self.water_bodies = []
        if self.landmarks is None:
            self.landmarks = []
        if self.resources is None:
            self.resources = []


@dataclass
class CityData:
    """Represents a city with grid location."""
    name: str
    country: str
    grid_cell: str  # Grid location (e.g., "Y320")
    tzone: str  # Timezone abbreviation (e.g., "JST")
    climate: str
    languages: List[str]
    region: str
    population: Optional[int] = None
    elevation: Optional[int] = None

    @property
    def tizo(self) -> str:
        """Return grid_cell as tizo for backwards compatibility."""
        return self.grid_cell

    @property
    def lat(self) -> float:
        """Approximate latitude from grid_cell. TODO: Improve conversion."""
        # Simple approximation: extract row number and convert to latitude
        # Grid is 270 rows tall, covering -90 to +90 degrees
        try:
            row_str = ''.join(c for c in self.grid_cell if c.isdigit())
            if row_str:
                row = int(row_str)
                # Row 0 is at 90° (North), row 270 is at -90° (South)
                return 90 - (row / 270 * 180)
        except:
            pass
        return 0.0

    @property
    def lon(self) -> float:
        """Approximate longitude from grid_cell. TODO: Improve conversion."""
        # Simple approximation: extract column letter and convert to longitude
        # Grid is 480 columns wide, covering -180 to +180 degrees
        try:
            col_str = ''.join(c for c in self.grid_cell if c.isalpha())
            if col_str:
                # Convert column letters to number (A=0, Z=25, AA=26, etc.)
                col = 0
                for c in col_str:
                    col = col * 26 + (ord(c.upper()) - ord('A'))
                # Column 0 is at -180° (West), column 480 is at +180° (East)
                return -180 + (col / 480 * 360)
        except:
            pass
        return 0.0


class MapDataManager:
    """
    Manages world geography data, TILE system, and map rendering.

    Responsibilities:
    - Load geography data from /knowledge/system/geography/
    - Generate TILE grid covering world
    - Render ASCII/Teletext maps
    - Handle coordinate conversions
    - Provide city/location lookups
    """

    def __init__(self, data_dir: Optional[Path] = None):
        """
        Initialize Map Data Manager.

        Args:
            data_dir: Path to knowledge/system/geography/ (default: auto-detect)
        """
        if data_dir is None:
            data_dir = Path(__file__).parent.parent.parent / "knowledge" / "system" / "geography"

        self.data_dir = data_dir
        self.graphics_dir = Path(__file__).parent.parent.parent / "knowledge" / "system" / "graphics"

        # Load data
        self.terrain_types = self._load_json("terrain_types.json")
        self.cities = self._load_cities()
        self.ascii_blocks = self._load_json("ascii_blocks.json", self.graphics_dir)
        self.teletext_mosaic = self._load_json("teletext_mosaic.json", self.graphics_dir)

        # TILE grid parameters
        self.tile_size = 1.0  # degrees (latitude/longitude)
        self.tiles: Dict[str, TileData] = {}

    def _load_json(self, filename: str, directory: Optional[Path] = None) -> dict:
        """Load JSON file from data directory."""
        if directory is None:
            directory = self.data_dir

        filepath = directory / filename
        if not filepath.exists():
            return {}

        with open(filepath, 'r') as f:
            return json.load(f)

    def _load_cities(self) -> List[CityData]:
        """Load city data."""
        data = self._load_json("cities.json")
        cities = []

        for city_dict in data.get("cities", []):
            cities.append(CityData(
                name=city_dict["name"],
                country=city_dict["country"],
                grid_cell=city_dict["grid_cell"],
                tzone=city_dict["tzone"],
                climate=city_dict["climate"],
                languages=city_dict["languages"],
                region=city_dict["region"],
                population=city_dict.get("population"),
                elevation=city_dict.get("elevation")
            ))

        return cities

    def lat_lon_to_tile_id(self, lat: float, lon: float) -> str:
        """
        Convert latitude/longitude to TILE ID.

        Args:
            lat: Latitude (-90 to 90)
            lon: Longitude (-180 to 180)

        Returns:
            TILE ID (format: GRID-ROW-COL)
        """
        # Normalize coordinates
        lat = max(-90, min(90, lat))
        lon = max(-180, min(180, lon))

        # Calculate grid position
        grid_x = int((lon + 180) / self.tile_size)
        grid_y = int((90 - lat) / self.tile_size)

        # Generate grid letter (A-Z for 26x26 sections)
        section_x = grid_x // 26
        section_y = grid_y // 26
        grid_letter = chr(65 + (section_y % 26))
        grid_number = section_x % 26

        return f"{grid_letter}{grid_number}-{grid_y}"

    def tile_id_to_lat_lon(self, tile_id: str) -> Tuple[float, float]:
        """
        Convert TILE ID to center latitude/longitude.

        Args:
            tile_id: TILE ID (format: GRID-ROW-COL)

        Returns:
            (latitude, longitude) tuple
        """
        parts = tile_id.split('-')
        if len(parts) != 2:
            raise ValueError(f"Invalid tile_id format: {tile_id}")

        grid_code = parts[0]
        row = int(parts[1])

        # Decode grid letter and number
        grid_letter = grid_code[0]
        grid_number = int(grid_code[1:])

        section_y = ord(grid_letter) - 65
        section_x = grid_number

        # Calculate lat/lon
        lat = 90 - (row * self.tile_size) - (self.tile_size / 2)
        lon = -180 + ((section_x * 26 * self.tile_size) + (self.tile_size / 2))

        return (lat, lon)

    def get_terrain_for_coords(self, lat: float, lon: float) -> str:
        """
        Determine terrain type for coordinates.

        Args:
            lat: Latitude
            lon: Longitude

        Returns:
            Terrain type (ocean, land, mountain, etc.)
        """
        # Simple heuristic - in real implementation would use elevation data
        # For now, assume ocean if far from cities

        # Check if near any city
        for city in self.cities:
            dist = self.calculate_distance(lat, lon, city.lat, city.lon)
            if dist < 50:  # Within 50km of a city
                return "urban"
            elif dist < 200:  # Within 200km
                return "rural"

        # Check latitude for climate zones
        abs_lat = abs(lat)

        if abs_lat > 66:  # Polar regions
            return "tundra"
        elif abs_lat > 60:  # Subpolar
            return "forest"
        elif abs_lat < 23:  # Tropical
            # Check if coastal (within 100km of ocean in simplified model)
            return "grassland"
        else:  # Temperate
            return "plain"

    def calculate_distance(self, lat1: float, lon1: float, lat2: float, lon2: float) -> float:
        """
        Calculate distance between two coordinates (Haversine formula).

        Args:
            lat1, lon1: First coordinate
            lat2, lon2: Second coordinate

        Returns:
            Distance in kilometers
        """
        R = 6371  # Earth radius in km

        lat1_rad = math.radians(lat1)
        lat2_rad = math.radians(lat2)
        delta_lat = math.radians(lat2 - lat1)
        delta_lon = math.radians(lon2 - lon1)

        a = (math.sin(delta_lat / 2) ** 2 +
             math.cos(lat1_rad) * math.cos(lat2_rad) *
             math.sin(delta_lon / 2) ** 2)
        c = 2 * math.asin(math.sqrt(a))

        return R * c

    def find_nearest_city(self, lat: float, lon: float) -> Optional[CityData]:
        """
        Find nearest city to coordinates.

        Args:
            lat: Latitude
            lon: Longitude

        Returns:
            Nearest CityData or None
        """
        if not self.cities:
            return None

        nearest = None
        min_distance = float('inf')

        for city in self.cities:
            dist = self.calculate_distance(lat, lon, city.lat, city.lon)
            if dist < min_distance:
                min_distance = dist
                nearest = city

        return nearest

    def get_city_by_tizo(self, tizo: str) -> Optional[CityData]:
        """
        Get city by TIZO code.

        Args:
            tizo: TIZO code (e.g., "T001")

        Returns:
            CityData or None
        """
        for city in self.cities:
            if city.tizo == tizo:
                return city
        return None

    def render_ascii_map(self, center_lat: float, center_lon: float,
                         width: int = 40, height: int = 20) -> List[str]:
        """
        Render ASCII map centered on coordinates.

        Args:
            center_lat: Center latitude
            center_lon: Center longitude
            width: Map width in characters
            height: Map height in characters

        Returns:
            List of strings (map rows)
        """
        map_lines = []

        # Calculate lat/lon range
        lat_range = height * 0.5  # Approximate degrees per character
        lon_range = width * 0.5

        for y in range(height):
            line = ""
            for x in range(width):
                # Calculate coords for this position
                lat = center_lat + ((height / 2 - y) * (lat_range / height))
                lon = center_lon + ((x - width / 2) * (lon_range / width))

                # Get terrain
                terrain = self.get_terrain_for_coords(lat, lon)

                # Get ASCII character
                terrain_info = self.terrain_types.get("terrain_types", {}).get(terrain, {})
                char = terrain_info.get("ascii_char", "?")

                line += char

            map_lines.append(line)

        return map_lines

    def get_map_stats(self) -> Dict[str, any]:
        """
        Get statistics about loaded map data.

        Returns:
            Dictionary with stats
        """
        return {
            "total_cities": len(self.cities),
            "terrain_types": len(self.terrain_types.get("terrain_types", {})),
            "tile_size_degrees": self.tile_size,
            "ascii_categories": len(self.ascii_blocks.get("categories", {})),
            "teletext_patterns": len(self.teletext_mosaic.get("patterns", {}))
        }
