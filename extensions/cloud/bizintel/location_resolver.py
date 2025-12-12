"""
Location Resolver for Business Intelligence
Converts addresses and location descriptions to uDOS TILE codes and MeshCore grid positions.

Integration:
- uDOS grid system (TILE codes: AA000-SL269 with layer suffix)
- MeshCore mesh networking (device placement on grid)
- Google Geocoding API for address lookup
- Reverse geocoding for TILE → address

TILE Code Format:
- Base: 2-letter column (AA-SL) + row number (0-269)
- Full: Base + layer suffix (e.g., QB185-100 for Sydney world layer)
- Layers: 100 (world ~83km), 200 (region ~2.78km), 300 (city ~93m), 400 (district ~3m)

Example:
    resolver = LocationResolver()
    
    # Address → TILE code
    tile = resolver.resolve_address("123 George St, Sydney NSW 2000")
    # Returns: "JQ157-300" (Sydney CBD, city layer)
    
    # TILE → MeshCore position
    mesh_pos = resolver.tile_to_meshcore("JQ157-300")
    # Returns: {"grid_x": 338, "grid_y": 157, "layer": 300}
"""

import os
import re
from typing import Optional, Dict, Tuple
from dataclasses import dataclass
from math import floor

try:
    import requests
except ImportError:
    requests = None


@dataclass
class LocationData:
    """Resolved location data."""
    address: str
    lat: float
    lon: float
    tile_code: str           # Base TILE code (e.g., "JQ157")
    tile_code_full: str      # Full with layer (e.g., "JQ157-300")
    layer: int               # Grid layer (100-500)
    meshcore_position: Dict  # MeshCore grid coordinates
    confidence: str          # high, medium, low


class LocationResolver:
    """Resolve addresses to TILE codes and MeshCore positions."""
    
    # TILE code system constants
    GRID_WIDTH = 480   # Columns: AA (0) to SL (479)
    GRID_HEIGHT = 270  # Rows: 0 to 269
    
    # Layer definitions (cell sizes)
    LAYERS = {
        100: 83000,    # World layer: ~83km per cell
        200: 2780,     # Region layer: ~2.78km per cell
        300: 93,       # City layer: ~93m per cell
        400: 3,        # District layer: ~3m per cell
        500: 0.1       # Block layer: ~10cm per cell
    }
    
    # Column mapping (base-26: AA=0, AZ=25, BA=26, ..., SL=479)
    COLUMN_LETTERS = 'ABCDEFGHIJKLMNOPQRSTUVWXYZ'  # 26 letters (A-Z)
    
    def __init__(self, google_api_key: Optional[str] = None):
        """Initialize location resolver.
        
        Args:
            google_api_key: Google Geocoding API key (from .env if not provided)
        """
        self.google_api_key = google_api_key or os.getenv('GOOGLE_GEOCODING_API_KEY')
        self.geocoding_url = "https://maps.googleapis.com/maps/api/geocode/json"
    
    def resolve_address(
        self,
        address: str,
        preferred_layer: int = 300
    ) -> Optional[LocationData]:
        """Resolve address to TILE code and MeshCore position.
        
        Args:
            address: Full address string
            preferred_layer: Preferred grid layer (100-500)
            
        Returns:
            LocationData or None if geocoding fails
        """
        # Geocode address to lat/lon
        lat, lon, formatted_address = self._geocode_address(address)
        
        if lat is None or lon is None:
            return None
        
        # Convert to TILE code
        tile_code = self.latlon_to_tile(lat, lon)
        tile_code_full = f"{tile_code}-{preferred_layer}"
        
        # Convert to MeshCore position
        meshcore_pos = self.tile_to_meshcore(tile_code_full)
        
        return LocationData(
            address=formatted_address or address,
            lat=lat,
            lon=lon,
            tile_code=tile_code,
            tile_code_full=tile_code_full,
            layer=preferred_layer,
            meshcore_position=meshcore_pos,
            confidence='high' if formatted_address else 'low'
        )
    
    def _geocode_address(self, address: str) -> Tuple[Optional[float], Optional[float], Optional[str]]:
        """Geocode address using Google Geocoding API.
        
        Args:
            address: Address string
            
        Returns:
            Tuple of (lat, lon, formatted_address) or (None, None, None)
        """
        if not self.google_api_key or not requests:
            print("Google Geocoding API key not configured or requests not installed")
            return None, None, None
        
        params = {
            'address': address,
            'key': self.google_api_key
        }
        
        try:
            response = requests.get(self.geocoding_url, params=params, timeout=10)
            response.raise_for_status()
            data = response.json()
            
            if data['status'] == 'OK' and data['results']:
                result = data['results'][0]
                location = result['geometry']['location']
                formatted_address = result['formatted_address']
                
                return location['lat'], location['lng'], formatted_address
            else:
                print(f"Geocoding failed: {data.get('status')}")
                return None, None, None
        
        except Exception as e:
            print(f"Geocoding error: {e}")
            return None, None, None
    
    def latlon_to_tile(self, lat: float, lon: float) -> str:
        """Convert lat/lon to TILE code (base, no layer suffix).
        
        Args:
            lat: Latitude (-90 to 90)
            lon: Longitude (-180 to 180)
            
        Returns:
            TILE code (e.g., "JQ157")
        """
        # Normalize to 0-1 range
        x_norm = (lon + 180) / 360  # 0 = -180°, 1 = 180°
        y_norm = (lat + 90) / 180   # 0 = -90°, 1 = 90°
        
        # Map to grid
        grid_x = floor(x_norm * self.GRID_WIDTH)
        grid_y = floor(y_norm * self.GRID_HEIGHT)
        
        # Clamp to valid range
        grid_x = max(0, min(self.GRID_WIDTH - 1, grid_x))
        grid_y = max(0, min(self.GRID_HEIGHT - 1, grid_y))
        
        # Convert to TILE code
        column = self._number_to_column(grid_x)
        row = str(grid_y)
        
        return f"{column}{row}"
    
    def tile_to_latlon(self, tile_code: str) -> Tuple[float, float]:
        """Convert TILE code to approximate lat/lon (cell center).
        
        Args:
            tile_code: TILE code (base or full, e.g., "JQ157" or "JQ157-300")
            
        Returns:
            Tuple of (lat, lon)
        """
        # Strip layer suffix if present
        base_tile = tile_code.split('-')[0]
        
        # Parse column and row
        match = re.match(r'^([A-Z]{2})(\d+)$', base_tile)
        if not match:
            raise ValueError(f"Invalid TILE code: {tile_code}")
        
        column_str, row_str = match.groups()
        grid_x = self._column_to_number(column_str)
        grid_y = int(row_str)
        
        # Convert to normalized coordinates (cell center)
        x_norm = (grid_x + 0.5) / self.GRID_WIDTH
        y_norm = (grid_y + 0.5) / self.GRID_HEIGHT
        
        # Convert to lat/lon
        lon = x_norm * 360 - 180
        lat = y_norm * 180 - 90
        
        return lat, lon
    
    def tile_to_meshcore(self, tile_code_full: str) -> Dict:
        """Convert TILE code to MeshCore grid position.
        
        Args:
            tile_code_full: Full TILE code with layer (e.g., "JQ157-300")
            
        Returns:
            MeshCore position dict with grid_x, grid_y, layer, cell_size_m
        """
        # Parse TILE code
        parts = tile_code_full.split('-')
        base_tile = parts[0]
        layer = int(parts[1]) if len(parts) > 1 else 100
        
        # Extract grid position
        match = re.match(r'^([A-Z]{2})(\d+)$', base_tile)
        if not match:
            raise ValueError(f"Invalid TILE code: {tile_code_full}")
        
        column_str, row_str = match.groups()
        grid_x = self._column_to_number(column_str)
        grid_y = int(row_str)
        
        return {
            'grid_x': grid_x,
            'grid_y': grid_y,
            'layer': layer,
            'cell_size_m': self.LAYERS.get(layer, 83000),
            'tile_code': base_tile
        }
    
    def meshcore_to_tile(self, meshcore_position: Dict) -> str:
        """Convert MeshCore position to TILE code.
        
        Args:
            meshcore_position: Dict with grid_x, grid_y, layer
            
        Returns:
            Full TILE code (e.g., "JQ157-300")
        """
        grid_x = meshcore_position['grid_x']
        grid_y = meshcore_position['grid_y']
        layer = meshcore_position.get('layer', 100)
        
        column = self._number_to_column(grid_x)
        row = str(grid_y)
        
        return f"{column}{row}-{layer}"
    
    def _number_to_column(self, num: int) -> str:
        """Convert grid X coordinate to 2-letter column code.
        
        Args:
            num: Grid X (0-479)
            
        Returns:
            Column code (AA-SL)
        """
        if num < 0 or num >= self.GRID_WIDTH:
            raise ValueError(f"Grid X out of range: {num} (must be 0-{self.GRID_WIDTH-1})")
        
        # Base-26 encoding: AA-AZ (0-25), BA-BZ (26-51), ..., SL (479)
        # first_letter = num // 26
        # second_letter = num % 26
        first = self.COLUMN_LETTERS[num // 26]
        second = self.COLUMN_LETTERS[num % 26]
        
        return f"{first}{second}"
    
    def _column_to_number(self, column: str) -> int:
        """Convert 2-letter column code to grid X coordinate.
        
        Args:
            column: Column code (AA-SL)
            
        Returns:
            Grid X (0-479)
        """
        if len(column) != 2:
            raise ValueError(f"Column must be 2 letters: {column}")
        
        first_idx = self.COLUMN_LETTERS.index(column[0])
        second_idx = self.COLUMN_LETTERS.index(column[1])
        
        # Base-26: first * 26 + second
        return first_idx * 26 + second_idx
    
    def suggest_layer(self, address_type: str) -> int:
        """Suggest appropriate grid layer for address type.
        
        Args:
            address_type: Type of location (country, city, street, building)
            
        Returns:
            Suggested layer (100-500)
        """
        suggestions = {
            'country': 100,    # World layer
            'state': 100,
            'region': 200,     # Region layer
            'city': 200,
            'suburb': 300,     # City layer
            'street': 300,
            'building': 400,   # District layer
            'unit': 400,
            'room': 500        # Block layer
        }
        
        return suggestions.get(address_type.lower(), 300)
    
    def format_for_upy(self, location_data: LocationData) -> str:
        """Format location data for uPY workflow variables.
        
        Args:
            location_data: Resolved location data
            
        Returns:
            uPY script snippet with location variables
        """
        output = [
            "# Resolved Location",
            f"{{$LOCATION.ADDRESS}} = \"{location_data.address}\"",
            f"{{$LOCATION.LAT}} = {location_data.lat}",
            f"{{$LOCATION.LON}} = {location_data.lon}",
            f"{{$LOCATION.TILE}} = \"{location_data.tile_code}\"",
            f"{{$LOCATION.TILE_FULL}} = \"{location_data.tile_code_full}\"",
            f"{{$LOCATION.LAYER}} = {location_data.layer}",
            f"{{$LOCATION.MESHCORE_X}} = {location_data.meshcore_position['grid_x']}",
            f"{{$LOCATION.MESHCORE_Y}} = {location_data.meshcore_position['grid_y']}",
            "",
            "# Usage in workflow:",
            "# CLOUD BUSINESS SEARCH 'restaurants' --location {{$LOCATION.TILE}}",
            "# MAP PLACE DEVICE {{$LOCATION.TILE_FULL}}"
        ]
        
        return '\n'.join(output)
