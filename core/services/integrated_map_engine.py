#!/usr/bin/env python3
"""
uDOS v1.0.3 - Integrated Mapping System

Combines APAC-centered 480×270 cell reference grid with TIZO location codes
and multi-layer mapping system for comprehensive world navigation.

Features:
- Cell reference system (A1-RL270 format)
- TIZO location integration
- Multi-layer mapping (SURFACE, CLOUD, SATELLITE, DUNGEON)
- Coordinate conversions
- Distance calculations
- World navigation

Version: 1.0.3
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


class CellReferenceSystem:
    """APAC-centered 480×270 cell reference system."""

    # Grid configuration
    COLS = 480
    ROWS = 270
    LON_CENTRE = 120.0  # APAC center
    LAT_MAX = 85.0
    LAT_MIN = -85.0

    @classmethod
    def wrap_longitude(cls, lon: float) -> float:
        """Wrap longitude around APAC center (120°E)."""
        shifted = lon - cls.LON_CENTRE
        while shifted < -180.0:
            shifted += 360.0
        while shifted >= 180.0:
            shifted -= 360.0
        return shifted

    @classmethod
    def lon_to_col(cls, lon: float) -> int:
        """Convert longitude to column index (0-based)."""
        x = (cls.wrap_longitude(lon) + 180.0) / 360.0 * cls.COLS
        return max(0, min(cls.COLS - 1, int(math.floor(x))))

    @classmethod
    def lat_to_row(cls, lat: float) -> int:
        """Convert latitude to row index (0-based)."""
        y = (cls.LAT_MAX - lat) / (cls.LAT_MAX - cls.LAT_MIN) * cls.ROWS
        return max(0, min(cls.ROWS - 1, int(math.floor(y))))

    @classmethod
    def col_to_letters(cls, col: int) -> str:
        """Convert column index to spreadsheet-style letters (A, B, ..., RL)."""
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


class IntegratedMapEngine:
    """Integrated mapping engine combining cell references with TIZO locations."""

    def __init__(self, data_dir="data/system"):
        self.data_dir = Path(data_dir)
        self.tizo_manager = TIZOLocationManager(data_dir)
        self.cell_system = CellReferenceSystem()

        # Load mapping data
        self.worldmap = self.load_worldmap()
        self.city_cells = {}
        self.layers = {}

        # Initialize with TIZO cities
        self.initialize_tizo_cells()

    def load_worldmap(self) -> Dict:
        """Load worldmap data."""
        worldmap_file = self.data_dir / "worldmap.json"
        if worldmap_file.exists():
            with open(worldmap_file, 'r') as f:
                return json.load(f)
        return {}

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

    def get_city_by_cell(self, cell_ref: str) -> Optional[Dict]:
        """Find TIZO city in the specified cell."""
        for tizo_code, city_data in self.city_cells.items():
            if city_data["cell_ref"] == cell_ref:
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
    """Test the integrated mapping system."""
    print("🗺️  uDOS Integrated Mapping System Test")
    print("=" * 50)

    # Initialize mapping engine
    engine = IntegratedMapEngine()

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

    print(f"\n🎉 Integrated mapping system test complete!")


if __name__ == "__main__":
    main()
