"""
uDOS v1.2.21 - Simplified Planet/Galaxy Manager

Stores current planet and galaxy metadata in user.json only.
No workspace isolation - just metadata for context and theming.

Stored in user.json:
- USER_PROFILE.PLANET (e.g., "Earth", "Mars")
- USER_PROFILE.GALAXY (e.g., "Milky Way", "Andromeda")
- USER_PROFILE.LOCATION (TILE code for user location)

Version: 1.2.21
Author: uDOS Development Team
"""

from typing import Optional
from core.config import get_config


class PlanetManager:
    """
    Simplified planet/galaxy manager.
    Stores metadata in user.json only (no workspace isolation).
    """

    # Available planets (for reference/selection)
    PLANETS = {
        "Earth": {"icon": "🌍", "galaxy": "Milky Way"},
        "Mars": {"icon": "🔴", "galaxy": "Milky Way"},
        "Jupiter": {"icon": "🪐", "galaxy": "Milky Way"},
        "Proxima b": {"icon": "🌏", "galaxy": "Alpha Centauri"},
    }

    # Available galaxies
    GALAXIES = {
        "Milky Way": {"icon": "🌌"},
        "Andromeda": {"icon": "🌠"},
        "Alpha Centauri": {"icon": "⭐"},
    }

    def __init__(self):
        """Initialize Planet Manager with config."""
        self.config = get_config()

    def get_current_planet(self) -> str:
        """Get current planet from user.json (default: Earth)."""
        return self.config.get_user('USER_PROFILE.PLANET', 'Earth')

    def set_current_planet(self, planet: str) -> None:
        """
        Set current planet in user.json.
        
        Args:
            planet: Planet name (e.g., 'Earth', 'Mars')
        """
        if planet not in self.PLANETS:
            raise ValueError(f"Unknown planet: {planet}. Available: {', '.join(self.PLANETS.keys())}")
        
        self.config.set_user('USER_PROFILE.PLANET', planet)
        
        # Auto-set galaxy based on planet
        galaxy = self.PLANETS[planet]['galaxy']
        self.config.set_user('USER_PROFILE.GALAXY', galaxy)
        
        self.config.save()

    def get_current_galaxy(self) -> str:
        """Get current galaxy from user.json (default: Milky Way)."""
        return self.config.get_user('USER_PROFILE.GALAXY', 'Milky Way')

    def set_current_galaxy(self, galaxy: str) -> None:
        """
        Set current galaxy in user.json.
        
        Args:
            galaxy: Galaxy name (e.g., 'Milky Way', 'Andromeda')
        """
        if galaxy not in self.GALAXIES:
            raise ValueError(f"Unknown galaxy: {galaxy}. Available: {', '.join(self.GALAXIES.keys())}")
        
        self.config.set_user('USER_PROFILE.GALAXY', galaxy)
        self.config.save()

    def get_planet_icon(self, planet: Optional[str] = None) -> str:
        """Get icon for planet (default: current planet)."""
        if planet is None:
            planet = self.get_current_planet()
        return self.PLANETS.get(planet, {}).get('icon', '🪐')

    def get_galaxy_icon(self, galaxy: Optional[str] = None) -> str:
        """Get icon for galaxy (default: current galaxy)."""
        if galaxy is None:
            galaxy = self.get_current_galaxy()
        return self.GALAXIES.get(galaxy, {}).get('icon', '🌌')

    def list_planets(self) -> dict:
        """List all available planets."""
        return self.PLANETS

    def list_galaxies(self) -> dict:
        """List all available galaxies."""
        return self.GALAXIES
