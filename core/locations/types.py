"""
Type definitions for location system.
Dataclasses and TypedDicts for Location, Connection, Tile, and Coordinate objects.
"""

from dataclasses import dataclass
from typing import Any, Dict, List, Optional, Tuple


@dataclass
class Coordinate:
    """Geographic coordinate (latitude, longitude)."""

    lat: float
    lon: float

    def __iter__(self):
        """Allow unpacking as (lat, lon)."""
        yield self.lat
        yield self.lon

    def distance_to(self, other: "Coordinate") -> float:
        """Calculate approximate distance to another coordinate (in degrees)."""
        import math

        dlat = self.lat - other.lat
        dlon = self.lon - other.lon
        return math.sqrt(dlat**2 + dlon**2)


@dataclass
class LocationConnection:
    """Connection from one location to another."""

    to: str  # Location ID
    direction: str  # north, south, east, west, up, down, etc.
    label: str  # Description of destination
    requires: Optional[str] = None  # Optional requirement (e.g., "wormhole", "vehicle")

    def __repr__(self) -> str:
        req_str = f" (requires: {self.requires})" if self.requires else ""
        return f"→ {self.label} ({self.direction}){req_str}"


@dataclass
class TileObject:
    """Object in a tile (static element)."""

    char: str  # Unicode character to display
    label: str  # Description
    z: int  # Z-index (layering: 0=behind, 1=normal, 2=above, 3=top)
    blocks: bool = False  # Whether this blocks movement
    fg: Optional[str] = None  # Foreground color (optional)
    bg: Optional[str] = None  # Background color (optional)


@dataclass
class TileSprite:
    """Sprite in a tile (dynamic entity)."""

    id: str  # Unique sprite ID
    char: str  # Unicode character
    label: str  # Description
    z: int  # Z-index
    fg: Optional[str] = None
    bg: Optional[str] = None


@dataclass
class TileMarker:
    """Marker in a tile (waypoint, point of interest)."""

    type: str  # Type (spawn, landmark, city-center, etc.)
    label: str  # Description


@dataclass
class Tile:
    """A single tile in a location grid."""

    objects: List[TileObject] = None
    sprites: List[TileSprite] = None
    markers: List[TileMarker] = None

    def __post_init__(self):
        if self.objects is None:
            self.objects = []
        if self.sprites is None:
            self.sprites = []
        if self.markers is None:
            self.markers = []


@dataclass
class Location:
    """A location in the uDOS virtual world."""

    # Required fields
    id: str  # Location ID (e.g., "L300-BJ10")
    name: str  # Display name
    region: str  # Region key (e.g., "asia_east")
    description: str  # Long description

    # Geospatial fields
    layer: int  # Layer number (300=terrestrial, 306=orbital, etc.)
    cell: str  # Grid cell address (e.g., "BJ10")
    scale: str  # Scale (terrestrial, orbital, planetary, stellar, galactic, cosmic)
    continent: str  # Continent/region name
    timezone: str  # Timezone (e.g., "UTC+9", "UTC-5", "UTC+5:30")
    coordinates: Coordinate  # GPS coordinates

    # Classification fields
    type: str  # Type (major-city, geographical-landmark, space-station, etc.)
    region_type: (
        str  # Region type (metropolis, landmark, temple, mountain, desert, etc.)
    )

    # Navigation
    connections: List[LocationConnection] = None  # Connected locations

    # Content
    tiles: Dict[str, Tile] = None  # Tile grid with content

    def __post_init__(self):
        """Initialize default values for optional fields."""
        if self.connections is None:
            self.connections = []
        if self.tiles is None:
            self.tiles = {}

        # Ensure coordinates is a Coordinate object if it's a dict
        if isinstance(self.coordinates, dict):
            self.coordinates = Coordinate(**self.coordinates)

    def summary(self) -> str:
        """Get one-line summary of location."""
        return f"{self.name} ({self.continent}, {self.timezone})"

    def info(self) -> str:
        """Get multi-line info about location."""
        lines = [
            f"📍 {self.name}",
            f"   Region: {self.region}",
            f"   Type: {self.type} ({self.region_type})",
            f"   Layer: {self.layer} ({self.scale})",
            f"   Timezone: {self.timezone}",
            f"   Coordinates: {self.coordinates.lat:.4f}°N, {abs(self.coordinates.lon):.4f}°{'E' if self.coordinates.lon > 0 else 'W'}",
            f"   Connections: {len(self.connections)} exits",
            f"   Description: {self.description[:70]}...",
        ]
        return "\n".join(lines)

    def get_tile(self, cell_id: str) -> Optional[Tile]:
        """Get a specific tile by cell ID."""
        return self.tiles.get(cell_id)

    def has_connection_to(self, location_id: str) -> bool:
        """Check if location connects to another location."""
        return any(conn.to == location_id for conn in self.connections)

    def get_connection(self, location_id: str) -> Optional[LocationConnection]:
        """Get connection to a specific location."""
        for conn in self.connections:
            if conn.to == location_id:
                return conn
        return None

    def __str__(self) -> str:
        return self.summary()


class LocationDatabase:
    """Simple in-memory location database."""

    def __init__(self, locations: List[Location] = None):
        """Initialize database with optional list of locations."""
        self.locations = locations or []
        self._by_id = {loc.id: loc for loc in self.locations}

    def add(self, location: Location) -> None:
        """Add a location to the database."""
        if location.id in self._by_id:
            raise ValueError(f"Location {location.id} already exists")
        self.locations.append(location)
        self._by_id[location.id] = location

    def get(self, location_id: str) -> Optional[Location]:
        """Get a location by ID."""
        return self._by_id.get(location_id)

    def get_all(self) -> List[Location]:
        """Get all locations."""
        return self.locations[:]

    def find_by_region(self, region: str) -> List[Location]:
        """Find all locations in a region."""
        return [loc for loc in self.locations if loc.region == region]

    def find_by_continent(self, continent: str) -> List[Location]:
        """Find all locations on a continent."""
        return [loc for loc in self.locations if loc.continent == continent]

    def find_by_type(self, location_type: str) -> List[Location]:
        """Find locations by type."""
        return [loc for loc in self.locations if loc.type == location_type]

    def find_by_scale(self, scale: str) -> List[Location]:
        """Find locations by scale."""
        return [loc for loc in self.locations if loc.scale == scale]

    def count(self) -> int:
        """Count total locations."""
        return len(self.locations)
