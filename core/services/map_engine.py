# uDOS v1.0.0 - Multi-Layer Mapping System
# Inspired by NetHack dungeon levels with real-world integration

import json
import os
from datetime import datetime
from typing import Dict, List, Tuple, Optional

class MapLayer:
    """
    Represents a single map layer (e.g., surface, underground, virtual).
    Inspired by NetHack dungeon levels but with real-world integration.
    """
    def __init__(self, name: str, depth: int, layer_type: str = "VIRTUAL"):
        """
        Initialize a map layer.

        Args:
            name: Layer name (e.g., "Surface", "Dungeon-1", "Cloud")
            depth: Vertical position (0=surface, negative=underground, positive=sky/virtual)
            layer_type: PHYSICAL, VIRTUAL, or HYBRID
        """
        self.name = name
        self.depth = depth
        self.layer_type = layer_type
        self.grid = {}  # Dictionary of coordinates -> cell data
        self.metadata = {
            "created_at": datetime.now().isoformat(),
            "description": "",
            "accessibility": "OPEN",  # OPEN, LOCKED, DISCOVERED, HIDDEN
            "connections": []  # Links to other layers
        }

    def set_cell(self, x: int, y: int, content: str, properties: Dict = None):
        """Set content at grid position."""
        coord = (x, y)
        self.grid[coord] = {
            "content": content,
            "properties": properties or {},
            "visited": False,
            "timestamp": datetime.now().isoformat()
        }

    def get_cell(self, x: int, y: int) -> Optional[Dict]:
        """Get cell data at position."""
        return self.grid.get((x, y))

    def mark_visited(self, x: int, y: int):
        """Mark a cell as visited."""
        if (x, y) in self.grid:
            self.grid[(x, y)]["visited"] = True

    def get_bounds(self) -> Tuple[int, int, int, int]:
        """Get the bounding box of the layer (min_x, min_y, max_x, max_y)."""
        if not self.grid:
            return (0, 0, 0, 0)
        coords = list(self.grid.keys())
        xs = [c[0] for c in coords]
        ys = [c[1] for c in coords]
        return (min(xs), min(ys), max(xs), max(ys))


class WorldLocation:
    """
    Represents a real-world geographic location.
    Links virtual map positions to actual coordinates.
    """
    def __init__(self, country: str, city: str = "", latitude: float = 0.0,
                 longitude: float = 0.0, timezone: str = "UTC"):
        self.country = country
        self.city = city
        self.latitude = latitude
        self.longitude = longitude
        self.timezone = timezone
        self.region = ""
        self.continent = ""

    def to_dict(self) -> Dict:
        """Convert to dictionary for serialization."""
        return {
            "country": self.country,
            "city": self.city,
            "latitude": self.latitude,
            "longitude": self.longitude,
            "timezone": self.timezone,
            "region": self.region,
            "continent": self.continent
        }

    @classmethod
    def from_dict(cls, data: Dict) -> 'WorldLocation':
        """Create from dictionary."""
        loc = cls(
            data.get("country", ""),
            data.get("city", ""),
            data.get("latitude", 0.0),
            data.get("longitude", 0.0),
            data.get("timezone", "UTC")
        )
        loc.region = data.get("region", "")
        loc.continent = data.get("continent", "")
        return loc


class MapEngine:
    """
    Core mapping engine for uDOS.
    Manages multi-layered maps with NetHack-style navigation.
    Integrates virtual positions with real-world locations.
    """
    def __init__(self, worldmap_file: str = "data/system/worldmap.json"):
        self.worldmap_file = worldmap_file
        self.layers: Dict[str, MapLayer] = {}
        self.current_layer = "SURFACE"
        self.position = (0, 0)  # Current x, y position
        self.real_world_location: Optional[WorldLocation] = None
        self.worldmap_data = {}

        # Initialize default layers (NetHack-inspired)
        self._init_default_layers()

        # Load world map data
        self._load_worldmap()

    def _init_default_layers(self):
        """Initialize the default layer structure."""
        # Virtual/Sky layers (positive depth)
        self.layers["CLOUD"] = MapLayer("Cloud Network", 10, "VIRTUAL")
        self.layers["SATELLITE"] = MapLayer("Satellite View", 100, "VIRTUAL")

        # Surface layer (depth 0)
        self.layers["SURFACE"] = MapLayer("Surface World", 0, "PHYSICAL")

        # Underground layers (negative depth) - NetHack style
        self.layers["DUNGEON-1"] = MapLayer("Dungeon Level 1", -1, "VIRTUAL")
        self.layers["DUNGEON-2"] = MapLayer("Dungeon Level 2", -2, "VIRTUAL")
        self.layers["DUNGEON-3"] = MapLayer("Dungeon Level 3", -3, "VIRTUAL")

        # Deep layers
        self.layers["MINES"] = MapLayer("Mines of Data", -10, "VIRTUAL")
        self.layers["CORE"] = MapLayer("System Core", -100, "VIRTUAL")

        # Set up layer connections (stairs/portals)
        self.layers["SURFACE"].metadata["connections"] = ["CLOUD", "DUNGEON-1"]
        self.layers["DUNGEON-1"].metadata["connections"] = ["SURFACE", "DUNGEON-2"]
        self.layers["DUNGEON-2"].metadata["connections"] = ["DUNGEON-1", "DUNGEON-3"]
        self.layers["DUNGEON-3"].metadata["connections"] = ["DUNGEON-2", "MINES"]

    def _load_worldmap(self):
        """Load world map data from WORLDMAP.UDO."""
        if not os.path.exists(self.worldmap_file):
            self.worldmap_data = self._get_default_worldmap()
            self._save_worldmap()
        else:
            try:
                with open(self.worldmap_file, 'r') as f:
                    self.worldmap_data = json.load(f)
            except:
                self.worldmap_data = self._get_default_worldmap()

    def _save_worldmap(self):
        """Save world map data to file."""
        os.makedirs(os.path.dirname(self.worldmap_file), exist_ok=True)
        with open(self.worldmap_file, 'w') as f:
            json.dump(self.worldmap_data, f, indent=2)

    def _get_default_worldmap(self) -> Dict:
        """Get default world map with timezones, cities, countries."""
        return {
            "VERSION": "1.0",
            "LAST_UPDATED": datetime.now().isoformat(),
            "TIMEZONES": {
                "UTC": {"offset": "+00:00", "name": "Coordinated Universal Time"},
                "EST": {"offset": "-05:00", "name": "Eastern Standard Time"},
                "PST": {"offset": "-08:00", "name": "Pacific Standard Time"},
                "GMT": {"offset": "+00:00", "name": "Greenwich Mean Time"},
                "CET": {"offset": "+01:00", "name": "Central European Time"},
                "JST": {"offset": "+09:00", "name": "Japan Standard Time"},
                "AEST": {"offset": "+10:00", "name": "Australian Eastern Standard Time"},
                "IST": {"offset": "+05:30", "name": "Indian Standard Time"}
            },
            "CONTINENTS": {
                "NORTH_AMERICA": {
                    "name": "North America",
                    "countries": ["USA", "Canada", "Mexico"]
                },
                "EUROPE": {
                    "name": "Europe",
                    "countries": ["UK", "France", "Germany", "Spain", "Italy"]
                },
                "ASIA": {
                    "name": "Asia",
                    "countries": ["China", "Japan", "India", "South Korea"]
                },
                "OCEANIA": {
                    "name": "Oceania",
                    "countries": ["Australia", "New Zealand"]
                },
                "SOUTH_AMERICA": {
                    "name": "South America",
                    "countries": ["Brazil", "Argentina", "Chile"]
                },
                "AFRICA": {
                    "name": "Africa",
                    "countries": ["South Africa", "Egypt", "Nigeria", "Kenya"]
                }
            },
            "CITIES": {
                "New York": {
                    "country": "USA",
                    "continent": "NORTH_AMERICA",
                    "latitude": 40.7128,
                    "longitude": -74.0060,
                    "timezone": "EST",
                    "region": "Northeast",
                    "grid_mapping": {"x": -74, "y": 41, "layer": "SURFACE"}
                },
                "London": {
                    "country": "UK",
                    "continent": "EUROPE",
                    "latitude": 51.5074,
                    "longitude": -0.1278,
                    "timezone": "GMT",
                    "region": "England",
                    "grid_mapping": {"x": 0, "y": 52, "layer": "SURFACE"}
                },
                "Tokyo": {
                    "country": "Japan",
                    "continent": "ASIA",
                    "latitude": 35.6762,
                    "longitude": 139.6503,
                    "timezone": "JST",
                    "region": "Kanto",
                    "grid_mapping": {"x": 140, "y": 36, "layer": "SURFACE"}
                },
                "Sydney": {
                    "country": "Australia",
                    "continent": "OCEANIA",
                    "latitude": -33.8688,
                    "longitude": 151.2093,
                    "timezone": "AEST",
                    "region": "New South Wales",
                    "grid_mapping": {"x": 151, "y": -34, "layer": "SURFACE"}
                },
                "Paris": {
                    "country": "France",
                    "continent": "EUROPE",
                    "latitude": 48.8566,
                    "longitude": 2.3522,
                    "timezone": "CET",
                    "region": "Île-de-France",
                    "grid_mapping": {"x": 2, "y": 49, "layer": "SURFACE"}
                },
                "San Francisco": {
                    "country": "USA",
                    "continent": "NORTH_AMERICA",
                    "latitude": 37.7749,
                    "longitude": -122.4194,
                    "timezone": "PST",
                    "region": "West Coast",
                    "grid_mapping": {"x": -122, "y": 38, "layer": "SURFACE"}
                },
                "Mumbai": {
                    "country": "India",
                    "continent": "ASIA",
                    "latitude": 19.0760,
                    "longitude": 72.8777,
                    "timezone": "IST",
                    "region": "Maharashtra",
                    "grid_mapping": {"x": 73, "y": 19, "layer": "SURFACE"}
                },
                "Berlin": {
                    "country": "Germany",
                    "continent": "EUROPE",
                    "latitude": 52.5200,
                    "longitude": 13.4050,
                    "timezone": "CET",
                    "region": "Brandenburg",
                    "grid_mapping": {"x": 13, "y": 53, "layer": "SURFACE"}
                }
            }
        }

    def set_real_world_location(self, city: str = None, country: str = None,
                                latitude: float = None, longitude: float = None,
                                timezone: str = "UTC"):
        """
        Set the user's real-world location and sync with map position.
        """
        # Try to find city in worldmap
        if city and city in self.worldmap_data.get("CITIES", {}):
            city_data = self.worldmap_data["CITIES"][city]
            self.real_world_location = WorldLocation(
                country=city_data["country"],
                city=city,
                latitude=city_data["latitude"],
                longitude=city_data["longitude"],
                timezone=city_data["timezone"]
            )
            self.real_world_location.region = city_data.get("region", "")
            self.real_world_location.continent = city_data.get("continent", "")

            # Sync map position to grid mapping
            grid_map = city_data.get("grid_mapping", {})
            if grid_map:
                self.position = (grid_map.get("x", 0), grid_map.get("y", 0))
                self.current_layer = grid_map.get("layer", "SURFACE")
        else:
            # Manual location setting
            self.real_world_location = WorldLocation(
                country=country or "Unknown",
                city=city or "",
                latitude=latitude or 0.0,
                longitude=longitude or 0.0,
                timezone=timezone
            )
            # Convert lat/lon to grid position (simplified)
            if latitude is not None and longitude is not None:
                self.position = (int(longitude), int(latitude))

    def move(self, dx: int, dy: int) -> str:
        """
        Move on current layer.

        Args:
            dx: Change in x coordinate
            dy: Change in y coordinate

        Returns:
            Status message
        """
        new_x = self.position[0] + dx
        new_y = self.position[1] + dy

        self.position = (new_x, new_y)

        # Mark cell as visited
        if self.current_layer in self.layers:
            self.layers[self.current_layer].mark_visited(new_x, new_y)

        return f"📍 Moved to ({new_x}, {new_y}) on {self.current_layer}"

    def goto(self, x: int, y: int) -> str:
        """
        Teleport to specific coordinates on current layer.
        """
        self.position = (x, y)
        if self.current_layer in self.layers:
            self.layers[self.current_layer].mark_visited(x, y)
        return f"📍 Teleported to ({x}, {y}) on {self.current_layer}"

    def change_layer(self, layer_name: str) -> str:
        """
        Switch to a different layer.
        """
        layer_name = layer_name.upper()

        if layer_name not in self.layers:
            return f"❌ ERROR: Layer '{layer_name}' does not exist"

        # Check if current layer has connection to target layer
        current = self.layers.get(self.current_layer)
        if current and layer_name not in current.metadata.get("connections", []):
            return f"⚠️  No direct connection from {self.current_layer} to {layer_name}"

        self.current_layer = layer_name
        return f"🔄 Switched to layer: {layer_name}"

    def descend(self) -> str:
        """Move down one layer (NetHack-style > command)."""
        current = self.layers.get(self.current_layer)
        if not current:
            return "❌ ERROR: Invalid current layer"

        # Find connected layer with lower depth
        connections = current.metadata.get("connections", [])
        lower_layers = [
            name for name in connections
            if self.layers[name].depth < current.depth
        ]

        if not lower_layers:
            return "⚠️  Cannot descend from this layer"

        # Choose the first lower layer
        target = lower_layers[0]
        self.current_layer = target
        return f"⬇️  Descended to {target}"

    def ascend(self) -> str:
        """Move up one layer (NetHack-style < command)."""
        current = self.layers.get(self.current_layer)
        if not current:
            return "❌ ERROR: Invalid current layer"

        # Find connected layer with higher depth
        connections = current.metadata.get("connections", [])
        higher_layers = [
            name for name in connections
            if self.layers[name].depth > current.depth
        ]

        if not higher_layers:
            return "⚠️  Cannot ascend from this layer"

        # Choose the first higher layer
        target = higher_layers[0]
        self.current_layer = target
        return f"⬆️  Ascended to {target}"

    def get_current_status(self) -> str:
        """Get current position and layer information."""
        layer = self.layers.get(self.current_layer)
        status = []

        status.append("=" * 60)
        status.append("🗺️  MAP STATUS")
        status.append("=" * 60)
        status.append("")

        # Current position
        status.append(f"📍 Position: ({self.position[0]}, {self.position[1]})")
        status.append(f"🌍 Layer: {self.current_layer}")
        if layer:
            status.append(f"   Depth: {layer.depth}")
            status.append(f"   Type: {layer.layer_type}")

        status.append("")

        # Real world location
        if self.real_world_location:
            loc = self.real_world_location
            status.append("🌏 Real World Location:")
            if loc.city:
                status.append(f"   City: {loc.city}, {loc.country}")
            else:
                status.append(f"   Country: {loc.country}")
            status.append(f"   Coordinates: {loc.latitude:.4f}°, {loc.longitude:.4f}°")
            status.append(f"   Timezone: {loc.timezone}")
            status.append("")

        # Available connections
        if layer:
            connections = layer.metadata.get("connections", [])
            if connections:
                status.append("🔗 Available Layers:")
                for conn in connections:
                    conn_layer = self.layers.get(conn)
                    if conn_layer:
                        symbol = "⬆️ " if conn_layer.depth > layer.depth else "⬇️ "
                        status.append(f"   {symbol}{conn} (depth {conn_layer.depth})")

        status.append("=" * 60)
        return "\n".join(status)

    def get_layer_map(self, width: int = 40, height: int = 20) -> str:
        """
        Generate ASCII map of current layer around current position.
        """
        layer = self.layers.get(self.current_layer)
        if not layer:
            return "❌ Invalid layer"

        x, y = self.position

        # Calculate viewport
        half_w = width // 2
        half_h = height // 2

        lines = []
        lines.append(f"╔{'═' * (width + 2)}╗")
        lines.append(f"║ {self.current_layer.center(width)} ║")
        lines.append(f"╠{'═' * (width + 2)}╣")

        for row in range(y + half_h, y - half_h, -1):
            line = "║ "
            for col in range(x - half_w, x + half_w):
                if col == x and row == y:
                    line += "@"  # Player position
                else:
                    cell = layer.get_cell(col, row)
                    if cell:
                        if cell.get("visited"):
                            line += "·"
                        else:
                            line += "?"
                    else:
                        line += " "
            line += " ║"
            lines.append(line)

        lines.append(f"╚{'═' * (width + 2)}╝")
        lines.append(f"@ = You ({x}, {y})")

        return "\n".join(lines)
