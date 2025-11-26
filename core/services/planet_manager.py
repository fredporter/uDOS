"""
uDOS v1.0.32 - Planet Manager Service

Manages planet system (workspaces reimagined as planets) with solar system metaphor.
Provides location-aware context for survival knowledge and world maps.

Features:
- Planet CRUD operations (create, list, set, delete)
- Solar system selection (Earth, Mars, custom planets)
- Current location tracking (lat/lon for Earth)
- Per-planet memory/sandbox isolation
- Integration with world map data (250 cities, 50 countries)

Philosophy: The planet metaphor makes workspaces intuitive and connects to
real-world geography - essential for a survival handbook.

Version: 1.0.32
Author: uDOS Development Team
"""

import json
import os
from pathlib import Path
from typing import Dict, List, Optional, Tuple
from datetime import datetime
from dataclasses import dataclass, asdict


@dataclass
class Location:
    """Real-world location coordinates."""
    latitude: float
    longitude: float
    name: str = ""
    region: str = ""
    country: str = ""

    def to_dict(self) -> Dict:
        return asdict(self)

    @classmethod
    def from_dict(cls, data: Dict) -> 'Location':
        return cls(**data)


@dataclass
class Planet:
    """Planet configuration."""
    name: str
    solar_system: str  # "Sol", "Alpha Centauri", "Custom"
    planet_type: str   # "Earth", "Mars", "Custom"
    icon: str          # Emoji icon
    created: str
    last_accessed: str
    location: Optional[Location] = None
    description: str = ""

    def to_dict(self) -> Dict:
        data = asdict(self)
        if self.location:
            data['location'] = self.location.to_dict()
        return data

    @classmethod
    def from_dict(cls, data: Dict) -> 'Planet':
        if 'location' in data and data['location']:
            data['location'] = Location.from_dict(data['location'])
        return cls(**data)


class PlanetManager:
    """
    Manages planets (workspaces) with solar system metaphor.

    Default planet: Earth (connects to existing world map data)
    Users can create custom planets (Mars, fictional worlds, etc.)
    """

    # Predefined solar systems
    SOLAR_SYSTEMS = {
        "Sol": {
            "name": "Sol System",
            "description": "Our home solar system",
            "planets": {
                "Earth": {"icon": "🌍", "type": "terrestrial"},
                "Mars": {"icon": "🔴", "type": "terrestrial"},
                "Jupiter": {"icon": "🪐", "type": "gas giant"},
            }
        },
        "Alpha Centauri": {
            "name": "Alpha Centauri System",
            "description": "Nearest star system to Sol",
            "planets": {
                "Proxima b": {"icon": "🌏", "type": "exoplanet"},
            }
        },
        "Custom": {
            "name": "Custom System",
            "description": "User-created planets",
            "planets": {}
        }
    }

    def __init__(self, config_dir: Optional[Path] = None):
        """
        Initialize Planet Manager.

        Args:
            config_dir: Configuration directory (default: memory/)
        """
        if config_dir is None:
            config_dir = Path("memory/user")

        self.config_dir = Path(config_dir)
        self.config_dir.mkdir(parents=True, exist_ok=True)

        self.planets_file = self.config_dir / "planets.json"
        self.universe_file = Path("knowledge/system/universe.json")
        # Current planet now stored in planets.json under "current_planet" key

        # Initialize if needed
        if not self.planets_file.exists():
            self._init_default_planets()

    def _init_default_planets(self):
        """Initialize with default Earth planet."""
        earth = Planet(
            name="Earth",
            solar_system="Sol",
            planet_type="Earth",
            icon="🌍",
            created=datetime.now().isoformat(),
            last_accessed=datetime.now().isoformat(),
            location=None,
            description="Our home planet with comprehensive survival knowledge"
        )

        planets = {"Earth": earth.to_dict()}
        self._save_planets(planets)
        self._set_current("Earth")

    def _save_planets(self, planets: Dict):
        """Save planets to JSON file with new structure."""
        # Get current planet
        current_planet = os.getenv('PLANET', 'Earth')

        data = {
            "current_planet": current_planet,
            "user_planets": {name: asdict(planet) for name, planet in planets.items()},
            "reference_universe": "knowledge/system/universe.json"
        }

        with open(self.planets_file, 'w') as f:
            json.dump(data, f, indent=2)

    def _load_planets(self) -> Dict:
        """Load planets from JSON file with new structure."""
        if not self.planets_file.exists():
            return {}

        with open(self.planets_file, 'r') as f:
            data = json.load(f)

        # Handle new structure
        if "user_planets" in data:
            return {name: Planet.from_dict(planet_data)
                    for name, planet_data in data["user_planets"].items()}

        # Handle old structure (backward compatibility)
        return {name: Planet.from_dict(planet_data)
                for name, planet_data in data.items()}

    def _set_current(self, planet_name: str):
        """Set current active planet in .env and planets.json."""
        # Update .env file
        env_path = Path(".env")
        if env_path.exists():
            lines = env_path.read_text().split('\n')
            updated = False
            for i, line in enumerate(lines):
                if line.startswith('UDOS_CURRENT_PLANET='):
                    lines[i] = f"UDOS_CURRENT_PLANET='{planet_name}'"
                    updated = True
                    break
            if updated:
                env_path.write_text('\n'.join(lines))

        # Update planets.json
        if self.planets_file.exists():
            with open(self.planets_file, 'r') as f:
                data = json.load(f)
            data["current_planet"] = planet_name
            with open(self.planets_file, 'w') as f:
                json.dump(data, f, indent=2)

    def get_current(self) -> Optional[Planet]:
        """Get current active planet from .env or planets.json."""
        # Try .env first
        current_name = os.getenv('PLANET')

        # Fall back to planets.json
        if not current_name and self.planets_file.exists():
            with open(self.planets_file, 'r') as f:
                data = json.load(f)
            current_name = data.get("current_planet")

        if not current_name:
            return None

        planets = self._load_planets()
        return planets.get(current_name)

    def list_planets(self) -> List[Planet]:
        """List all planets."""
        planets = self._load_planets()
        return list(planets.values())

    def create_planet(
        self,
        name: str,
        solar_system: str = "Sol",
        planet_type: str = "Custom",
        icon: str = "🪐",
        description: str = ""
    ) -> Planet:
        """
        Create a new planet.

        Args:
            name: Planet name (must be unique)
            solar_system: Solar system name
            planet_type: Type of planet
            icon: Emoji icon
            description: Planet description

        Returns:
            Created planet

        Raises:
            ValueError: If planet name already exists
        """
        planets = self._load_planets()

        if name in planets:
            raise ValueError(f"Planet '{name}' already exists")

        planet = Planet(
            name=name,
            solar_system=solar_system,
            planet_type=planet_type,
            icon=icon,
            created=datetime.now().isoformat(),
            last_accessed=datetime.now().isoformat(),
            description=description
        )

        planets[name] = planet
        self._save_planets({k: v.to_dict() for k, v in planets.items()})

        return planet

    def set_planet(self, name: str) -> Planet:
        """
        Set active planet.

        Args:
            name: Planet name

        Returns:
            Activated planet

        Raises:
            ValueError: If planet doesn't exist
        """
        planets = self._load_planets()

        if name not in planets:
            raise ValueError(f"Planet '{name}' not found")

        # Update last accessed
        planet = planets[name]
        planet.last_accessed = datetime.now().isoformat()
        self._save_planets({k: v.to_dict() for k, v in planets.items()})

        self._set_current(name)
        return planet

    def delete_planet(self, name: str):
        """
        Delete a planet.

        Args:
            name: Planet name

        Raises:
            ValueError: If planet doesn't exist or is current
        """
        planets = self._load_planets()

        if name not in planets:
            raise ValueError(f"Planet '{name}' not found")

        current = self.get_current()
        if current and current.name == name:
            raise ValueError(f"Cannot delete active planet. Switch to another planet first.")

        del planets[name]
        self._save_planets({k: v.to_dict() for k, v in planets.items()})

    def set_location(
        self,
        planet_name: str,
        latitude: float,
        longitude: float,
        name: str = "",
        region: str = "",
        country: str = ""
    ) -> Location:
        """
        Set location for a planet (typically Earth).

        Args:
            planet_name: Planet name
            latitude: Latitude (-90 to 90)
            longitude: Longitude (-180 to 180)
            name: Location name
            region: Region/state
            country: Country

        Returns:
            Updated location

        Raises:
            ValueError: If planet doesn't exist or coordinates invalid
        """
        if not -90 <= latitude <= 90:
            raise ValueError("Latitude must be between -90 and 90")
        if not -180 <= longitude <= 180:
            raise ValueError("Longitude must be between -180 and 180")

        planets = self._load_planets()

        if planet_name not in planets:
            raise ValueError(f"Planet '{planet_name}' not found")

        location = Location(
            latitude=latitude,
            longitude=longitude,
            name=name,
            region=region,
            country=country
        )

        planet = planets[planet_name]
        planet.location = location

        self._save_planets({k: v.to_dict() for k, v in planets.items()})

        return location

    def get_location(self, planet_name: Optional[str] = None) -> Optional[Location]:
        """
        Get location for a planet.

        Args:
            planet_name: Planet name (default: current planet)

        Returns:
            Location if set, None otherwise
        """
        if planet_name is None:
            planet = self.get_current()
            if not planet:
                return None
        else:
            planets = self._load_planets()
            planet = planets.get(planet_name)

        return planet.location if planet else None

    def get_solar_systems(self) -> Dict:
        """Get available solar systems."""
        return self.SOLAR_SYSTEMS

    def get_planet_info(self, name: str) -> Optional[Planet]:
        """Get planet information."""
        planets = self._load_planets()
        return planets.get(name)
