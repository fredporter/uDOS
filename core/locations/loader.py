"""
Location loader - Parses locations.json and creates Location objects.
Provides utilities for loading, validating, and accessing location data.
"""

import json
from pathlib import Path
from typing import Dict, List, Optional

from .types import (
    Coordinate,
    Location,
    LocationConnection,
    LocationDatabase,
    Tile,
    TileMarker,
    TileObject,
    TileSprite,
)


class LocationLoader:
    """Load and parse locations from JSON file."""

    def __init__(self, locations_file: Optional[Path] = None):
        """
        Initialize loader with path to locations.json.

        Args:
            locations_file: Path to locations.json (defaults to core/locations.json)
        """
        if locations_file is None:
            # Auto-locate from module directory
            locations_file = Path(__file__).parent.parent / "locations.json"

        self.locations_file = Path(locations_file)
        self._raw_data = None
        self._locations_db = None

    def load(self) -> LocationDatabase:
        """
        Load locations from JSON file and return database.

        Returns:
            LocationDatabase with all parsed locations

        Raises:
            FileNotFoundError: If locations.json not found
            ValueError: If JSON is invalid or structure is incorrect
        """
        if not self.locations_file.exists():
            raise FileNotFoundError(f"Locations file not found: {self.locations_file}")

        # Load and parse JSON
        try:
            with open(self.locations_file, "r", encoding="utf-8") as f:
                self._raw_data = json.load(f)
        except json.JSONDecodeError as e:
            raise ValueError(f"Invalid JSON in {self.locations_file}: {e}")

        # Parse locations
        locations = []
        for loc_data in self._raw_data.get("locations", []):
            try:
                location = self._parse_location(loc_data)
                locations.append(location)
            except Exception as e:
                raise ValueError(f"Error parsing location {loc_data.get('id')}: {e}")

        # Create database
        self._locations_db = LocationDatabase(locations)
        return self._locations_db

    def _parse_location(self, data: Dict) -> Location:
        """Parse a single location from JSON data."""
        # Parse coordinates
        coords_data = data.get("coordinates", {})
        coordinates = Coordinate(
            lat=float(coords_data.get("lat", 0)), lon=float(coords_data.get("lon", 0))
        )

        # Parse connections
        connections = []
        for conn_data in data.get("connections", []):
            connection = LocationConnection(
                to=conn_data.get("to", ""),
                direction=conn_data.get("direction", ""),
                label=conn_data.get("label", ""),
                requires=conn_data.get("requires"),
            )
            connections.append(connection)

        # Parse tiles
        tiles = {}
        for cell_id, tile_data in data.get("tiles", {}).items():
            # Parse objects
            objects = []
            for obj_data in tile_data.get("objects", []):
                obj = TileObject(
                    char=obj_data.get("char", "?"),
                    label=obj_data.get("label", "object"),
                    z=int(obj_data.get("z", 0)),
                    blocks=bool(obj_data.get("blocks", False)),
                    fg=obj_data.get("fg"),
                    bg=obj_data.get("bg"),
                )
                objects.append(obj)

            # Parse sprites
            sprites = []
            for sprite_data in tile_data.get("sprites", []):
                sprite = TileSprite(
                    id=sprite_data.get("id", ""),
                    char=sprite_data.get("char", "?"),
                    label=sprite_data.get("label", "sprite"),
                    z=int(sprite_data.get("z", 0)),
                    fg=sprite_data.get("fg"),
                    bg=sprite_data.get("bg"),
                )
                sprites.append(sprite)

            # Parse markers
            markers = []
            for marker_data in tile_data.get("markers", []):
                marker = TileMarker(
                    type=marker_data.get("type", ""), label=marker_data.get("label", "")
                )
                markers.append(marker)

            # Create tile
            tile = Tile(objects=objects, sprites=sprites, markers=markers)
            tiles[cell_id] = tile

        # Create location
        location = Location(
            id=data.get("id", ""),
            name=data.get("name", ""),
            region=data.get("region", ""),
            description=data.get("description", ""),
            layer=int(data.get("layer", 0)),
            cell=data.get("cell", ""),
            scale=data.get("scale", "terrestrial"),
            continent=data.get("continent", ""),
            timezone=data.get("timezone", "UTC+0"),
            coordinates=coordinates,
            type=data.get("type", ""),
            region_type=data.get("region_type", ""),
            connections=connections,
            tiles=tiles,
        )

        return location

    def get_database(self) -> LocationDatabase:
        """Get loaded database (loads if not already loaded)."""
        if self._locations_db is None:
            self.load()
        return self._locations_db


def load_locations(locations_file: Optional[Path] = None) -> LocationDatabase:
    """
    Convenience function to load locations database.

    Args:
        locations_file: Optional path to locations.json

    Returns:
        LocationDatabase with all locations
    """
    loader = LocationLoader(locations_file)
    return loader.load()


def get_location(
    location_id: str, db: Optional[LocationDatabase] = None
) -> Optional[Location]:
    """
    Get a single location by ID.

    Args:
        location_id: Location ID (e.g., "L300-BJ10")
        db: Optional pre-loaded LocationDatabase (loads if not provided)

    Returns:
        Location object or None if not found
    """
    if db is None:
        db = load_locations()
    return db.get(location_id)


# Module-level cache for singleton database
_default_db = None


def get_default_database() -> LocationDatabase:
    """Get or create the default locations database."""
    global _default_db
    if _default_db is None:
        _default_db = load_locations()
    return _default_db
