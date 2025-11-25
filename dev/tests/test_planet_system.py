"""
uDOS v1.0.32 - Planet System Tests

Test suite for the Planet System including:
- PlanetManager CRUD operations
- CONFIG PLANET commands
- LOCATE commands
- Planet/Location data persistence

Run with: python memory/tests/test_planet_system.py
"""

import sys
import os
import json
import shutil
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

from core.services.planet_manager import PlanetManager


class TestResults:
    """Track test results."""
    def __init__(self):
        self.passed = 0
        self.failed = 0
        self.tests = []

    def add_result(self, name: str, passed: bool, message: str = ""):
        """Add a test result."""
        self.tests.append({
            'name': name,
            'passed': passed,
            'message': message
        })
        if passed:
            self.passed += 1
        else:
            self.failed += 1

    def print_summary(self):
        """Print test summary."""
        print("\n" + "="*70)
        print("TEST SUMMARY")
        print("="*70)

        for test in self.tests:
            status = "✅ PASS" if test['passed'] else "❌ FAIL"
            print(f"{status} - {test['name']}")
            if test['message']:
                print(f"       {test['message']}")

        print()
        print(f"Total: {self.passed + self.failed} tests")
        print(f"Passed: {self.passed}")
        print(f"Failed: {self.failed}")
        print("="*70)


def backup_planet_data():
    """Backup existing planet data."""
    config_dir = Path("memory/config")
    backup_dir = Path("memory/config/.backup_test")

    if config_dir.exists():
        if backup_dir.exists():
            shutil.rmtree(backup_dir)
        backup_dir.mkdir(parents=True, exist_ok=True)

        # Backup planets.json and current_planet.json
        for file in ['planets.json', 'current_planet.json']:
            src = config_dir / file
            if src.exists():
                shutil.copy2(src, backup_dir / file)


def restore_planet_data():
    """Restore backed up planet data."""
    config_dir = Path("memory/config")
    backup_dir = Path("memory/config/.backup_test")

    if backup_dir.exists():
        for file in ['planets.json', 'current_planet.json']:
            src = backup_dir / file
            dst = config_dir / file
            if src.exists():
                shutil.copy2(src, dst)

        # Clean up backup
        shutil.rmtree(backup_dir)


def clean_test_data():
    """Remove test planet data."""
    config_dir = Path("memory/config")
    for file in ['planets.json', 'current_planet.json']:
        path = config_dir / file
        if path.exists():
            path.unlink()


def test_planet_manager_init():
    """Test PlanetManager initialization."""
    results = TestResults()

    print("\n🧪 Test 1: PlanetManager Initialization")
    print("-" * 70)

    try:
        pm = PlanetManager()
        current = pm.get_current()

        # Should create default Earth planet
        results.add_result(
            "PlanetManager creates default Earth planet",
            current is not None and current.name == "Earth",
            f"Current planet: {current.name if current else None}"
        )

        results.add_result(
            "Default planet has correct solar system",
            current.solar_system == "Sol",
            f"Solar system: {current.solar_system}"
        )

        results.add_result(
            "Default planet has correct type",
            current.planet_type == "Earth",
            f"Type: {current.planet_type}"
        )

        results.add_result(
            "Default planet has Earth icon",
            current.icon == "🌍",
            f"Icon: {current.icon}"
        )

    except Exception as e:
        results.add_result("PlanetManager initialization", False, str(e))

    return results


def test_planet_crud():
    """Test planet CRUD operations."""
    results = TestResults()

    print("\n🧪 Test 2: Planet CRUD Operations")
    print("-" * 70)

    try:
        pm = PlanetManager()

        # Create Mars planet
        mars = pm.create_planet(
            name="Mars",
            solar_system="Sol",
            planet_type="Mars",
            icon="🔴",
            description="Red planet workspace"
        )

        results.add_result(
            "Create Mars planet",
            mars is not None and mars.name == "Mars",
            f"Created: {mars.icon} {mars.name}"
        )

        # List planets
        planets = pm.list_planets()
        results.add_result(
            "List planets returns both Earth and Mars",
            len(planets) == 2,
            f"Found {len(planets)} planets"
        )

        # Switch to Mars
        pm.set_planet("Mars")
        current = pm.get_current()
        results.add_result(
            "Switch to Mars planet",
            current.name == "Mars",
            f"Current: {current.name}"
        )

        # Switch back to Earth
        pm.set_planet("Earth")
        current = pm.get_current()
        results.add_result(
            "Switch back to Earth",
            current.name == "Earth",
            f"Current: {current.name}"
        )

        # Delete Mars
        pm.delete_planet("Mars")
        planets = pm.list_planets()
        results.add_result(
            "Delete Mars planet",
            len(planets) == 1 and planets[0].name == "Earth",
            f"Remaining: {len(planets)} planet(s)"
        )

    except Exception as e:
        results.add_result("Planet CRUD operations", False, str(e))

    return results


def test_location_management():
    """Test location setting and retrieval."""
    results = TestResults()

    print("\n🧪 Test 3: Location Management")
    print("-" * 70)

    try:
        pm = PlanetManager()

        # Set location for Earth
        location = pm.set_location(
            planet_name="Earth",
            latitude=51.5074,
            longitude=-0.1278,
            name="London",
            region="England",
            country="UK"
        )

        results.add_result(
            "Set location for Earth",
            location is not None,
            f"Location: {location.name}"
        )

        # Get location
        retrieved = pm.get_location("Earth")
        results.add_result(
            "Retrieve location",
            retrieved is not None and retrieved.name == "London",
            f"Retrieved: {retrieved.name}"
        )

        results.add_result(
            "Location coordinates match",
            abs(retrieved.latitude - 51.5074) < 0.01 and abs(retrieved.longitude + 0.1278) < 0.01,
            f"Coords: {retrieved.latitude:.2f}°, {retrieved.longitude:.2f}°"
        )

        # Clear location
        pm.set_location(
            planet_name="Earth",
            latitude=0,
            longitude=0,
            name="",
            region="",
            country=""
        )

        cleared = pm.get_location("Earth")
        results.add_result(
            "Clear location",
            cleared is None or cleared.name == "",
            "Location cleared"
        )

    except Exception as e:
        results.add_result("Location management", False, str(e))

    return results


def test_data_persistence():
    """Test that planet data persists to JSON files."""
    results = TestResults()

    print("\n🧪 Test 4: Data Persistence")
    print("-" * 70)

    try:
        # Create a planet and set location
        pm1 = PlanetManager()
        pm1.create_planet("TestPlanet", "Custom", "Custom", "🪐", "Test planet")
        pm1.set_planet("TestPlanet")
        pm1.set_location("TestPlanet", 10.0, 20.0, "TestCity", "TestRegion", "TestCountry")

        # Create new manager instance (should load from disk)
        pm2 = PlanetManager()

        # Check if TestPlanet exists
        planets = pm2.list_planets()
        planet_names = [p.name for p in planets]
        results.add_result(
            "Planet persists across instances",
            "TestPlanet" in planet_names,
            f"Found planets: {planet_names}"
        )

        # Check current planet
        current = pm2.get_current()
        results.add_result(
            "Current planet persists",
            current.name == "TestPlanet",
            f"Current: {current.name}"
        )

        # Check location
        location = pm2.get_location("TestPlanet")
        results.add_result(
            "Location persists",
            location is not None and location.name == "TestCity",
            f"Location: {location.name if location else None}"
        )

        # Clean up test planet - must switch to Earth first
        pm2.set_planet("Earth")
        pm2.delete_planet("TestPlanet")

    except Exception as e:
        results.add_result("Data persistence", False, str(e))

    return results
def test_solar_systems():
    """Test solar system presets."""
    results = TestResults()

    print("\n🧪 Test 5: Solar System Presets")
    print("-" * 70)

    try:
        pm = PlanetManager()

        # Access SOLAR_SYSTEMS from class or instance
        solar_systems = pm.get_solar_systems()

        results.add_result(
            "Sol system exists",
            "Sol" in solar_systems,
            f"Planets: {list(solar_systems.get('Sol', {}).get('planets', {}).keys())}"
        )

        results.add_result(
            "Alpha Centauri system exists",
            "Alpha Centauri" in solar_systems,
            f"Planets: {list(solar_systems.get('Alpha Centauri', {}).get('planets', {}).keys())}"
        )

        results.add_result(
            "Custom system exists",
            "Custom" in solar_systems,
            "Allows user-defined planets"
        )

        # Create planet in each system
        pm.create_planet("TestMars", "Sol", "Mars", "🔴", "Test Mars")
        pm.create_planet("TestProxima", "Alpha Centauri", "Exoplanet", "🌑", "Test Proxima")
        pm.create_planet("TestCustom", "Custom", "Custom", "🪐", "Test Custom")

        planets = pm.list_planets()
        solar_systems_in_use = set(p.solar_system for p in planets)

        results.add_result(
            "Planets created in different solar systems",
            "Sol" in solar_systems_in_use and "Alpha Centauri" in solar_systems_in_use and "Custom" in solar_systems_in_use,
            f"Solar systems in use: {solar_systems_in_use}"
        )

        # Clean up test planets - switch to Earth first
        pm.set_planet("Earth")
        for name in ["TestMars", "TestProxima", "TestCustom"]:
            try:
                pm.delete_planet(name)
            except:
                pass

    except Exception as e:
        results.add_result("Solar system presets", False, str(e))

    return results
def run_all_tests():
    """Run all planet system tests."""
    print("="*70)
    print("🪐 uDOS v1.0.32 - PLANET SYSTEM TEST SUITE")
    print("="*70)

    # Backup existing data
    print("\n📦 Backing up existing planet data...")
    backup_planet_data()

    # Clean slate for tests
    print("🧹 Cleaning test environment...")
    clean_test_data()

    # Run tests
    all_results = TestResults()

    test_suites = [
        test_planet_manager_init,
        test_planet_crud,
        test_location_management,
        test_data_persistence,
        test_solar_systems,
    ]

    for test_suite in test_suites:
        results = test_suite()
        # Merge results
        all_results.passed += results.passed
        all_results.failed += results.failed
        all_results.tests.extend(results.tests)

    # Print summary
    all_results.print_summary()

    # Restore data
    print("\n♻️  Restoring original planet data...")
    restore_planet_data()

    # Return exit code
    return 0 if all_results.failed == 0 else 1


if __name__ == "__main__":
    sys.exit(run_all_tests())
