"""
uDOS v1.0.20b - Enhanced Mapping System Test Suite
Tests TILE system, geography data, ASCII rendering, and data architecture
"""

import unittest
import json
from pathlib import Path

from core.services.map_data_manager import MapDataManager, TileData, CityData


class TestMapDataManager(unittest.TestCase):
    """Test MapDataManager functionality."""

    def setUp(self):
        """Initialize manager for testing."""
        self.manager = MapDataManager()

    def test_manager_initialization(self):
        """Test manager initializes with data."""
        self.assertIsNotNone(self.manager)
        self.assertIsNotNone(self.manager.terrain_types)
        self.assertIsNotNone(self.manager.cities)

    def test_cities_loaded(self):
        """Test cities are loaded from JSON."""
        self.assertGreater(len(self.manager.cities), 0)

        # Check first city has required fields
        city = self.manager.cities[0]
        self.assertIsInstance(city, CityData)
        self.assertTrue(hasattr(city, 'name'))
        self.assertTrue(hasattr(city, 'tizo'))
        self.assertTrue(hasattr(city, 'lat'))
        self.assertTrue(hasattr(city, 'lon'))

    def test_terrain_types_loaded(self):
        """Test terrain types are loaded."""
        terrain_types = self.manager.terrain_types.get("terrain_types", {})
        self.assertGreater(len(terrain_types), 0)

        # Check specific terrain exists
        self.assertIn("ocean", terrain_types)
        self.assertIn("urban", terrain_types)
        self.assertIn("mountain", terrain_types)

    def test_lat_lon_to_tile_id(self):
        """Test coordinate to TILE ID conversion."""
        # Test Tokyo coordinates
        tile_id = self.manager.lat_lon_to_tile_id(35.6762, 139.6503)
        self.assertIsInstance(tile_id, str)
        self.assertIn("-", tile_id)

        # Test boundary cases
        tile_equator = self.manager.lat_lon_to_tile_id(0, 0)
        self.assertIsNotNone(tile_equator)

        tile_north_pole = self.manager.lat_lon_to_tile_id(90, 0)
        self.assertIsNotNone(tile_north_pole)

    def test_tile_id_to_lat_lon(self):
        """Test TILE ID to coordinate conversion."""
        # Create tile ID and convert back
        original_lat, original_lon = 40.7128, -74.0060  # New York
        tile_id = self.manager.lat_lon_to_tile_id(original_lat, original_lon)

        # Convert back
        lat, lon = self.manager.tile_id_to_lat_lon(tile_id)

        # Should be close to original (within tile size)
        self.assertAlmostEqual(lat, original_lat, delta=2.0)
        self.assertAlmostEqual(lon, original_lon, delta=2.0)

    def test_calculate_distance(self):
        """Test Haversine distance calculation."""
        # Tokyo to New York
        tokyo_lat, tokyo_lon = 35.6762, 139.6503
        ny_lat, ny_lon = 40.7128, -74.0060

        distance = self.manager.calculate_distance(tokyo_lat, tokyo_lon, ny_lat, ny_lon)

        # Should be approximately 10,850 km
        self.assertGreater(distance, 10000)
        self.assertLess(distance, 11500)

    def test_find_nearest_city(self):
        """Test finding nearest city to coordinates."""
        # Coordinates near Tokyo
        lat, lon = 35.5, 139.5

        nearest = self.manager.find_nearest_city(lat, lon)

        self.assertIsNotNone(nearest)
        self.assertIsInstance(nearest, CityData)
        # Should find a city with valid grid_cell
        self.assertIsNotNone(nearest.grid_cell)

    def test_get_city_by_tizo(self):
        """Test grid_cell lookup."""
        city = self.manager.get_city_by_tizo("Y320")

        self.assertIsNotNone(city)
        self.assertEqual(city.name, "Tokyo")
        self.assertEqual(city.country, "JP")

    def test_get_terrain_for_coords(self):
        """Test terrain determination."""
        # Tokyo coordinates - should return a valid terrain type
        terrain_tokyo = self.manager.get_terrain_for_coords(35.6762, 139.6503)
        self.assertIsNotNone(terrain_tokyo)
        self.assertIsInstance(terrain_tokyo, str)
        self.assertTrue(len(terrain_tokyo) > 0)

        # Middle of Pacific (should default to something sensible)
        terrain_ocean = self.manager.get_terrain_for_coords(0, 180)
        self.assertIsNotNone(terrain_ocean)

    def test_render_ascii_map(self):
        """Test ASCII map rendering."""
        # Render map centered on Tokyo
        map_lines = self.manager.render_ascii_map(35.6762, 139.6503, width=40, height=20)

        self.assertEqual(len(map_lines), 20)
        self.assertEqual(len(map_lines[0]), 40)

        # Check contains ASCII characters
        map_str = "".join(map_lines)
        self.assertGreater(len(map_str), 0)

    def test_get_map_stats(self):
        """Test map statistics."""
        stats = self.manager.get_map_stats()

        self.assertIn("total_cities", stats)
        self.assertIn("terrain_types", stats)
        self.assertIn("tile_size_degrees", stats)

        self.assertGreater(stats["total_cities"], 0)
        self.assertGreater(stats["terrain_types"], 0)


class TestGeographyData(unittest.TestCase):
    """Test geography data files."""

    def setUp(self):
        """Set up data directory."""
        self.data_dir = Path(__file__).parent.parent.parent / "knowledge" / "system" / "geography"

    def test_cities_json_exists(self):
        """Test cities.json file exists."""
        cities_file = self.data_dir / "cities.json"
        self.assertTrue(cities_file.exists())

    def test_cities_json_valid(self):
        """Test cities.json is valid JSON."""
        cities_file = self.data_dir / "cities.json"

        with open(cities_file, 'r') as f:
            data = json.load(f)

        self.assertIn("cities", data)
        self.assertIn("metadata", data)
        self.assertIn("version", data["metadata"])
        self.assertIsInstance(data["cities"], list)

    def test_terrain_types_json_exists(self):
        """Test terrain_types.json exists."""
        terrain_file = self.data_dir / "terrain_types.json"
        self.assertTrue(terrain_file.exists())

    def test_terrain_types_valid(self):
        """Test terrain_types.json structure."""
        terrain_file = self.data_dir / "terrain_types.json"

        with open(terrain_file, 'r') as f:
            data = json.load(f)

        self.assertIn("terrain_types", data)

        # Check ocean terrain definition
        ocean = data["terrain_types"].get("ocean")
        self.assertIsNotNone(ocean)
        self.assertIn("ascii_char", ocean)
        self.assertIn("color", ocean)

    def test_tile_schema_exists(self):
        """Test TILE schema exists."""
        schema_file = self.data_dir / "tile_schema.json"
        self.assertTrue(schema_file.exists())


class TestGraphicsData(unittest.TestCase):
    """Test ASCII/Teletext graphics data."""

    def setUp(self):
        """Set up graphics directory."""
        self.graphics_dir = Path(__file__).parent.parent.parent / "knowledge" / "system" / "graphics"

    def test_ascii_blocks_exists(self):
        """Test ASCII blocks file exists."""
        ascii_file = self.graphics_dir / "ascii_blocks.json"
        self.assertTrue(ascii_file.exists())

    def test_ascii_blocks_valid(self):
        """Test ASCII blocks structure."""
        ascii_file = self.graphics_dir / "ascii_blocks.json"

        with open(ascii_file, 'r') as f:
            data = json.load(f)

        self.assertIn("categories", data)
        self.assertIn("box_drawing", data["categories"])
        self.assertIn("terrain", data["categories"])

    def test_teletext_mosaic_exists(self):
        """Test Teletext mosaic file exists."""
        teletext_file = self.graphics_dir / "teletext_mosaic.json"
        self.assertTrue(teletext_file.exists())

    def test_teletext_mosaic_valid(self):
        """Test Teletext mosaic structure."""
        teletext_file = self.graphics_dir / "teletext_mosaic.json"

        with open(teletext_file, 'r') as f:
            data = json.load(f)

        self.assertIn("patterns", data)
        self.assertIn("terrain_patterns", data)

        # Check patterns have required fields
        patterns = data["patterns"]
        self.assertIn("00", patterns)
        self.assertIn("binary", patterns["00"])
        self.assertIn("description", patterns["00"])


class TestDataArchitecture(unittest.TestCase):
    """Test data architecture separation."""

    def test_data_system_structure(self):
        """Test /knowledge/system/ directory structure."""
        base_dir = Path(__file__).parent.parent.parent / "knowledge" / "system"

        self.assertTrue(base_dir.exists())
        self.assertTrue((base_dir / "geography").exists())
        self.assertTrue((base_dir / "graphics").exists())
        self.assertTrue((base_dir / "reference").exists())

    def test_reference_data_exists(self):
        """Test reference data files exist."""
        ref_dir = Path(__file__).parent.parent.parent / "knowledge" / "system" / "reference"

        self.assertTrue((ref_dir / "metric.json").exists())
        self.assertTrue((ref_dir / "imperial.json").exists())


if __name__ == '__main__':
    print("="*60)
    print("uDOS v1.0.20b - Enhanced Mapping System Test Suite")
    print("="*60)
    print()

    # Run tests
    unittest.main(verbosity=2)
