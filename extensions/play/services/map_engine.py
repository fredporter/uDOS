#!/usr/bin/env python3
"""
uDOS v2.0.0 - Universal Grid Map Engine

Grid-first TILE code system with multi-layer support and coordinate conversion.

Features:
- Grid-first TILE codes (GRID-LAYER format, e.g., "QB185-100")
- 480×270 world grid with AA-SL column encoding
- Multi-layer system (100-899, aligned with teletext pages)
- 30×30 subdivision per zoom level (900 subcells)
- Bi-directional lat/long ↔ TILE conversion
- Layer 100 base resolution: ~83km per cell

Layers:
- 100-199: World/continent level (~83km)
- 200-299: Region/country level (~2.7km)
- 300-399: City/district level (~93m)
- 400-499: Block/street level (~3m)
- 500-599: Building/room level (~10cm)
- 600-699: Cloud layer (virtual)
- 700-799: Satellite layer (virtual)
- 800-899: Space layer (virtual)

Version: 2.0.0
Author: Fred Porter
"""

import json
import math
from pathlib import Path
from typing import Dict, List, Tuple, Optional, Union
import sys

# Add project root to path
project_root = Path(__file__).parent.parent.parent.parent
sys.path.insert(0, str(project_root))

from core.utils.grid_utils import (
    latlong_to_tile,
    tile_to_latlong,
    parse_tile_code,
    validate_tile_code,
    get_adjacent_tiles,
    calculate_distance_km,
    column_to_code,
    code_to_column,
    GRID_COLUMNS,
    GRID_ROWS,
    LAYER_100_CELL_SIZE_KM
)


class MapEngine:
    """Universal grid-based map engine with multi-layer support."""
    
    def __init__(self, data_dir: Optional[Path] = None):
        """
        Initialize map engine.
        
        Args:
            data_dir: Directory containing map data (default: extensions/assets/data)
        """
        if data_dir is None:
            data_dir = project_root / "extensions" / "assets" / "data"
        
        self.data_dir = Path(data_dir)
        self.layers = {}  # Cache for layer data
        self.current_layer = 100  # Default layer
        self.current_tile = None  # Current position
        
        # Load layer 100 (base world map) if available
        self.load_layer(100)
    
    def load_layer(self, layer: int) -> bool:
        """
        Load map data for a specific layer.
        
        Args:
            layer: Layer number (100-899)
            
        Returns:
            True if layer loaded successfully
        """
        layer_file = self.data_dir / f"map_layer_{layer}.json"
        
        if not layer_file.exists():
            # Create empty layer structure
            self.layers[layer] = {
                'layer': layer,
                'resolution_km': self._get_layer_resolution(layer),
                'cells': {}
            }
            return False
        
        try:
            with open(layer_file, 'r') as f:
                self.layers[layer] = json.load(f)
            return True
        except Exception as e:
            print(f"Error loading layer {layer}: {e}")
            return False
    
    def _get_layer_resolution(self, layer: int) -> float:
        """
        Calculate cell resolution for a layer.
        
        Args:
            layer: Layer number (100-899)
            
        Returns:
            Cell size in kilometers
        """
        # Each layer zoom increases resolution by factor of 30
        if layer < 100 or layer > 899:
            return LAYER_100_CELL_SIZE_KM
        
        zoom_levels = (layer - 100) // 100
        return LAYER_100_CELL_SIZE_KM / (30 ** zoom_levels)
    
    def get_cell_info(self, tile_code: str) -> Dict:
        """
        Get information about a map cell.
        
        Args:
            tile_code: TILE code (e.g., "QB185-100")
            
        Returns:
            Dictionary with cell information
        """
        if not validate_tile_code(tile_code):
            return {'error': 'Invalid TILE code'}
        
        # Parse TILE code
        parsed = parse_tile_code(tile_code)
        layer = parsed['layer']
        grid_cell = parsed['grid_cell']
        
        # Get coordinates
        lat, lon, _ = tile_to_latlong(tile_code)
        
        # Get cell data if layer is loaded
        cell_data = {}
        if layer in self.layers:
            cell_data = self.layers[layer]['cells'].get(grid_cell, {})
        
        # Build info dict
        info = {
            'tile_code': tile_code,
            'grid_cell': grid_cell,
            'column': parsed['column'],
            'column_num': parsed['column_num'],
            'row': parsed['row'],
            'layer': layer,
            'latitude': lat,
            'longitude': lon,
            'resolution_km': self._get_layer_resolution(layer),
            'subcodes': parsed['subcodes'],
            **cell_data
        }
        
        return info
    
    def set_cell_data(self, tile_code: str, data: Dict) -> bool:
        """
        Set data for a map cell.
        
        Args:
            tile_code: TILE code
            data: Data to store in cell
            
        Returns:
            True if successful
        """
        if not validate_tile_code(tile_code):
            return False
        
        parsed = parse_tile_code(tile_code)
        layer = parsed['layer']
        grid_cell = parsed['grid_cell']
        
        # Ensure layer is loaded
        if layer not in self.layers:
            self.load_layer(layer)
        
        # Update cell data
        self.layers[layer]['cells'][grid_cell] = data
        
        return True
    
    def save_layer(self, layer: int) -> bool:
        """
        Save layer data to disk.
        
        Args:
            layer: Layer number to save
            
        Returns:
            True if successful
        """
        if layer not in self.layers:
            return False
        
        layer_file = self.data_dir / f"map_layer_{layer}.json"
        layer_file.parent.mkdir(parents=True, exist_ok=True)
        
        try:
            with open(layer_file, 'w') as f:
                json.dump(self.layers[layer], f, indent=2)
            return True
        except Exception as e:
            print(f"Error saving layer {layer}: {e}")
            return False
    
    def move_to(self, tile_code: str) -> Dict:
        """
        Move to a specific TILE code.
        
        Args:
            tile_code: TILE code to move to
            
        Returns:
            Info about new location
        """
        info = self.get_cell_info(tile_code)
        if 'error' not in info:
            self.current_tile = tile_code
            self.current_layer = parse_tile_code(tile_code)['layer']
        
        return info
    
    def move_direction(self, direction: str) -> Dict:
        """
        Move in a cardinal direction from current position.
        
        Args:
            direction: 'N', 'S', 'E', 'W', 'NE', 'NW', 'SE', 'SW'
            
        Returns:
            Info about new location
        """
        if not self.current_tile:
            return {'error': 'No current position'}
        
        adjacent = get_adjacent_tiles(self.current_tile)
        
        if direction not in adjacent:
            return {'error': f'Cannot move {direction} from current position'}
        
        new_tile = adjacent[direction]
        return self.move_to(new_tile)
    
    def zoom_in(self, subcode: Optional[str] = None) -> Dict:
        """
        Zoom to next layer (increase precision 30x).
        
        Args:
            subcode: Optional subcode for specific subcell (e.g., "AA15")
            
        Returns:
            Info about zoomed location
        """
        if not self.current_tile:
            return {'error': 'No current position'}
        
        parsed = parse_tile_code(self.current_tile)
        current_layer = parsed['layer']
        
        # Check layer bounds
        if current_layer >= 899:
            return {'error': 'Maximum zoom level reached'}
        
        # Calculate next layer (100 → 200, 200 → 300, etc.)
        next_layer = ((current_layer // 100) + 1) * 100
        
        # Build new TILE code
        if subcode:
            new_tile = f"{parsed['grid_cell']}-{next_layer}-{subcode}"
        else:
            # Default to center cell (O15 in 30×30 grid)
            new_tile = f"{parsed['grid_cell']}-{next_layer}-O15"
        
        return self.move_to(new_tile)
    
    def zoom_out(self) -> Dict:
        """
        Zoom to previous layer (decrease precision 30x).
        
        Returns:
            Info about zoomed location
        """
        if not self.current_tile:
            return {'error': 'No current position'}
        
        parsed = parse_tile_code(self.current_tile)
        current_layer = parsed['layer']
        
        # Check layer bounds
        if current_layer <= 100:
            return {'error': 'Minimum zoom level reached'}
        
        # Calculate previous layer (200 → 100, 300 → 200, etc.)
        prev_layer = ((current_layer // 100) - 1) * 100
        
        # Build new TILE code (remove subcodes)
        new_tile = f"{parsed['grid_cell']}-{prev_layer}"
        
        return self.move_to(new_tile)
    
    def find_nearby_cities(self, tile_code: str, max_distance_km: float = 500) -> List[Dict]:
        """
        Find cities near a TILE code.
        
        Args:
            tile_code: Center TILE code
            max_distance_km: Maximum search radius in km
            
        Returns:
            List of nearby cities with distances
        """
        # This will be populated once we have city data in layer 100
        # For now, return empty list
        return []
    
    def search_location(self, query: str) -> List[Dict]:
        """
        Search for locations by name.
        
        Args:
            query: Search query (city name, country, etc.)
            
        Returns:
            List of matching locations
        """
        results = []
        query_lower = query.lower()
        
        # Search layer 100 (base world map)
        if 100 in self.layers:
            for grid_cell, data in self.layers[100]['cells'].items():
                name = data.get('name', '').lower()
                if query_lower in name:
                    tile_code = f"{grid_cell}-100"
                    info = self.get_cell_info(tile_code)
                    info['match_score'] = 1.0 if name == query_lower else 0.5
                    results.append(info)
        
        # Sort by match score
        results.sort(key=lambda x: x.get('match_score', 0), reverse=True)
        
        return results
    
    def get_current_location(self) -> Optional[Dict]:
        """
        Get info about current location.
        
        Returns:
            Info dict or None
        """
        if not self.current_tile:
            return None
        
        return self.get_cell_info(self.current_tile)
    
    def calculate_route(self, from_tile: str, to_tile: str) -> Dict:
        """
        Calculate route between two TILE codes.
        
        Args:
            from_tile: Starting TILE code
            to_tile: Destination TILE code
            
        Returns:
            Route information
        """
        # Simple direct route for now
        distance = calculate_distance_km(from_tile, to_tile)
        
        from_info = parse_tile_code(from_tile)
        to_info = parse_tile_code(to_tile)
        
        # Calculate grid steps
        col_diff = to_info['column_num'] - from_info['column_num']
        row_diff = to_info['row'] - from_info['row']
        
        grid_steps = abs(col_diff) + abs(row_diff)
        
        return {
            'from': from_tile,
            'to': to_tile,
            'distance_km': distance,
            'grid_steps': grid_steps,
            'direction': self._get_direction(col_diff, row_diff)
        }
    
    def _get_direction(self, col_diff: int, row_diff: int) -> str:
        """Get compass direction from column/row differences."""
        if col_diff == 0 and row_diff == 0:
            return "same location"
        
        # Determine primary direction
        if abs(col_diff) > abs(row_diff):
            # More east-west
            primary = "east" if col_diff > 0 else "west"
        else:
            # More north-south
            primary = "south" if row_diff > 0 else "north"
        
        # Add secondary direction if significant
        if abs(col_diff) > 0 and abs(row_diff) > 0:
            secondary = "south" if row_diff > 0 else "north"
            if abs(col_diff) < abs(row_diff):
                secondary = "east" if col_diff > 0 else "west"
            return f"{primary}-{secondary}"
        
        return primary


# Convenience function for getting map engine instance
_map_engine_instance = None

def get_map_engine() -> MapEngine:
    """Get or create global MapEngine instance."""
    global _map_engine_instance
    
    if _map_engine_instance is None:
        _map_engine_instance = MapEngine()
    
    return _map_engine_instance


if __name__ == "__main__":
    # Test map engine
    print("=" * 70)
    print("MAP ENGINE TEST")
    print("=" * 70)
    
    engine = MapEngine()
    
    # Test Sydney
    sydney_tile = "QZ185-100"
    info = engine.get_cell_info(sydney_tile)
    print(f"\nSydney ({sydney_tile}):")
    print(f"  Coordinates: {info['latitude']:.2f}, {info['longitude']:.2f}")
    print(f"  Resolution: {info['resolution_km']:.2f} km/cell")
    
    # Test London
    london_tile = "JF57-100"
    info = engine.get_cell_info(london_tile)
    print(f"\nLondon ({london_tile}):")
    print(f"  Coordinates: {info['latitude']:.2f}, {info['longitude']:.2f}")
    print(f"  Resolution: {info['resolution_km']:.2f} km/cell")
    
    # Test route
    route = engine.calculate_route(sydney_tile, london_tile)
    print(f"\nRoute Sydney → London:")
    print(f"  Distance: {route['distance_km']:,.1f} km")
    print(f"  Grid steps: {route['grid_steps']}")
    print(f"  Direction: {route['direction']}")
    
    # Test movement
    print(f"\n" + "=" * 70)
    print("MOVEMENT TEST")
    print("=" * 70)
    
    engine.move_to(sydney_tile)
    print(f"\nCurrent position: {engine.current_tile}")
    
    # Move north
    result = engine.move_direction('N')
    print(f"After moving north: {result['tile_code']}")
    
    # Move east
    result = engine.move_direction('E')
    print(f"After moving east: {result['tile_code']}")
    
    # Zoom in
    result = engine.zoom_in()
    print(f"After zooming in: {result['tile_code']}")
    print(f"  Resolution: {result['resolution_km']:.4f} km/cell")
    
    print(f"\n" + "=" * 70)
    print("✅ MAP ENGINE OPERATIONAL")
    print("=" * 70)
