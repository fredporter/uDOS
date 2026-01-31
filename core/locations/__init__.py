"""
uDOS Location System
====================

This module provides location management for uDOS, including:
- Location database with 46+ playable locations across scales
- Timezone-aware operations
- Tile-based grid system for location maps
- Pathfinding and navigation utilities

Main Classes:
  Location - A location in the game world
  LocationDatabase - Query interface for locations
  LocationService - Advanced location operations (timezone, pathfinding)
  Coordinate - Optional external coordinates (not stored in core datasets)
  Tile - Grid cell with objects, sprites, markers

Quick Start:

  from core.locations import Location, LocationDatabase, LocationService

  # Load locations
  db = LocationDatabase.load()

  # Get a location
  tokyo = db.get('L300-BJ10')

  # Use service for advanced operations
  service = LocationService()
  local_time = service.get_local_time('L300-BJ10')
  path = service.find_path('L300-AA10', 'L300-BJ10')
"""

from .loader import LocationLoader, load_locations, get_location, get_default_database
from .service import LocationService
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

__version__ = "1.0.0"
__all__ = [
    # Types
    "Coordinate",
    "Location",
    "LocationConnection",
    "LocationDatabase",
    "Tile",
    "TileMarker",
    "TileObject",
    "TileSprite",
    # Service
    "LocationService",
    # Loader
    "LocationLoader",
    "load_locations",
    "get_location",
    "get_default_database",
]
