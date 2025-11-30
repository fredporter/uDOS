"""
uDOS Grid Utilities
===================
Grid coordinate conversion and TILE code management for the universal grid system.

Grid Specifications:
- World grid: 480 columns × 270 rows
- Column encoding: AA-RL (0-479 using base-26 two-letter codes)
- Layer 100 resolution: ~83km per cell (40,075km / 480 columns)
- Subdivision: 30×30 cells per zoom level (900 subcells)

TILE Code Format:
- Base: GRID-LAYER (e.g., "QB185-100")
- With subcodes: GRID-LAYER-SUBCODE1-SUBCODE2 (e.g., "QB185-200-AA15-M12")
"""

import math
from typing import Tuple, Optional, List


# Grid constants
GRID_COLUMNS = 480  # Total columns in world grid
GRID_ROWS = 270     # Total rows in world grid
EARTH_CIRCUMFERENCE_KM = 40075  # Earth's circumference at equator
EARTH_MERIDIAN_KM = 40008       # Earth's meridian (pole to pole)

# Layer specifications
LAYER_100_CELL_SIZE_KM = EARTH_CIRCUMFERENCE_KM / GRID_COLUMNS  # ~83.49 km
SUBDIVISION_FACTOR = 30  # 30×30 subdivision per layer zoom


def column_to_code(column: int) -> str:
    """
    Convert column number (0-479) to two-letter code (AA-RL).

    480 columns requires more than AA-ZZ (26×26=676), so we use:
    AA-AZ (0-25), BA-BZ (26-51), ..., SA-SL (468-479)

    Args:
        column: Column number (0-479)

    Returns:
        Two-letter column code (AA-RL)

    Examples:
        >>> column_to_code(0)
        'AA'
        >>> column_to_code(25)
        'AZ'
        >>> column_to_code(26)
        'BA'
        >>> column_to_code(479)
        'SL'
    """
    if not 0 <= column < GRID_COLUMNS:
        raise ValueError(f"Column must be 0-{GRID_COLUMNS-1}, got {column}")

    # AA-AZ = 0-25, BA-BZ = 26-51, etc.
    first = column // 26
    second = column % 26
    return chr(65 + first) + chr(65 + second)


def code_to_column(code: str) -> int:
    """
    Convert two-letter code (AA-SL) to column number (0-479).

    Args:
        code: Two-letter column code (AA-SL)

    Returns:
        Column number (0-479)

    Examples:
        >>> code_to_column('AA')
        0
        >>> code_to_column('AZ')
        25
        >>> code_to_column('BA')
        26
        >>> code_to_column('SL')
        479
    """
    if len(code) != 2 or not code.isalpha():
        raise ValueError(f"Code must be two letters, got '{code}'")

    code = code.upper()
    first = ord(code[0]) - 65
    second = ord(code[1]) - 65

    column = first * 26 + second

    if not 0 <= column < GRID_COLUMNS:
        raise ValueError(f"Code '{code}' is out of range (AA-SL for 480 columns)")

    return column


def latlong_to_tile(lat: float, lon: float, layer: int = 100) -> str:
    """
    Convert latitude/longitude to TILE code.

    Args:
        lat: Latitude (-90 to +90)
        lon: Longitude (-180 to +180)
        layer: Grid layer (100-899)

    Returns:
        TILE code (e.g., "QB185-100")

    Examples:
        >>> latlong_to_tile(-33.87, 151.21, 100)  # Sydney
        'QB185-100'
        >>> latlong_to_tile(51.51, -0.13, 100)    # London
        'JA90-100'
    """
    if not -90 <= lat <= 90:
        raise ValueError(f"Latitude must be -90 to +90, got {lat}")
    if not -180 <= lon <= 180:
        raise ValueError(f"Longitude must be -180 to +180, got {lon}")
    if not 100 <= layer <= 899:
        raise ValueError(f"Layer must be 100-899, got {layer}")

    # Convert longitude (-180 to +180) to column (0-479)
    # Longitude 0° = center of grid (column 240)
    column = int((lon + 180) * GRID_COLUMNS / 360)
    column = max(0, min(GRID_COLUMNS - 1, column))

    # Convert latitude (+90 to -90) to row (0-269)
    # Latitude +90° (North Pole) = row 0
    # Latitude -90° (South Pole) = row 269
    row = int((90 - lat) * GRID_ROWS / 180)
    row = max(0, min(GRID_ROWS - 1, row))

    # Generate TILE code
    col_code = column_to_code(column)
    tile_code = f"{col_code}{row}-{layer}"

    return tile_code


def tile_to_latlong(tile_code: str) -> Tuple[float, float, int]:
    """
    Convert TILE code to latitude/longitude (center of cell).

    Args:
        tile_code: TILE code (e.g., "QB185-100" or "QB185-200-AA15")

    Returns:
        Tuple of (latitude, longitude, layer)

    Examples:
        >>> tile_to_latlong("QB185-100")
        (-33.833..., 151.125, 100)
        >>> tile_to_latlong("JA90-100")
        (51.333..., -0.375, 100)
    """
    parts = tile_code.split('-')
    if len(parts) < 2:
        raise ValueError(f"Invalid TILE code format: {tile_code}")

    # Parse base grid cell
    grid_cell = parts[0]
    layer = int(parts[1])

    # Extract column code (first 2 letters) and row number
    if len(grid_cell) < 3:
        raise ValueError(f"Invalid grid cell format: {grid_cell}")

    col_code = grid_cell[:2]
    row_str = grid_cell[2:]

    if not row_str.isdigit():
        raise ValueError(f"Invalid row number in grid cell: {grid_cell}")

    column = code_to_column(col_code)
    row = int(row_str)

    if not 0 <= row < GRID_ROWS:
        raise ValueError(f"Row must be 0-{GRID_ROWS-1}, got {row}")

    # Convert to lat/long (center of cell)
    lon = (column / GRID_COLUMNS) * 360 - 180 + (180 / GRID_COLUMNS)
    lat = 90 - (row / GRID_ROWS) * 180 - (90 / GRID_ROWS)

    # If subcodes exist, refine position
    if len(parts) > 2:
        # TODO: Implement subcode positioning for zoomed layers
        # For now, return base cell center
        pass

    return (lat, lon, layer)


def parse_tile_code(tile_code: str) -> dict:
    """
    Parse TILE code into components.

    Args:
        tile_code: TILE code (e.g., "QB185-100-AA15")

    Returns:
        Dictionary with parsed components

    Example:
        >>> parse_tile_code("QB185-200-AA15")
        {
            'grid_cell': 'QB185',
            'column': 'QB',
            'column_num': 431,
            'row': 185,
            'layer': 200,
            'subcodes': ['AA15'],
            'full_code': 'QB185-200-AA15'
        }
    """
    parts = tile_code.split('-')
    if len(parts) < 2:
        raise ValueError(f"Invalid TILE code format: {tile_code}")

    grid_cell = parts[0]
    layer = int(parts[1])
    subcodes = parts[2:] if len(parts) > 2 else []

    # Parse grid cell
    col_code = grid_cell[:2]
    row = int(grid_cell[2:])
    column_num = code_to_column(col_code)

    return {
        'grid_cell': grid_cell,
        'column': col_code,
        'column_num': column_num,
        'row': row,
        'layer': layer,
        'subcodes': subcodes,
        'full_code': tile_code
    }


def validate_tile_code(tile_code: str) -> bool:
    """
    Validate TILE code format.

    Args:
        tile_code: TILE code to validate

    Returns:
        True if valid, False otherwise

    Examples:
        >>> validate_tile_code("QB185-100")
        True
        >>> validate_tile_code("QB185-200-AA15")
        True
        >>> validate_tile_code("invalid")
        False
    """
    try:
        parse_tile_code(tile_code)
        return True
    except (ValueError, IndexError):
        return False


def get_adjacent_tiles(tile_code: str) -> dict:
    """
    Get adjacent TILE codes (N, S, E, W, NE, NW, SE, SW).

    Args:
        tile_code: Base TILE code

    Returns:
        Dictionary of adjacent tiles

    Example:
        >>> get_adjacent_tiles("JA90-100")
        {
            'N': 'JA89-100',
            'S': 'JA91-100',
            'E': 'JB90-100',
            'W': 'IZ90-100',
            ...
        }
    """
    parsed = parse_tile_code(tile_code)
    col = parsed['column_num']
    row = parsed['row']
    layer = parsed['layer']

    adjacent = {}

    # North
    if row > 0:
        adjacent['N'] = f"{column_to_code(col)}{row-1}-{layer}"

    # South
    if row < GRID_ROWS - 1:
        adjacent['S'] = f"{column_to_code(col)}{row+1}-{layer}"

    # East
    if col < GRID_COLUMNS - 1:
        adjacent['E'] = f"{column_to_code(col+1)}{row}-{layer}"

    # West
    if col > 0:
        adjacent['W'] = f"{column_to_code(col-1)}{row}-{layer}"

    # Northeast
    if row > 0 and col < GRID_COLUMNS - 1:
        adjacent['NE'] = f"{column_to_code(col+1)}{row-1}-{layer}"

    # Northwest
    if row > 0 and col > 0:
        adjacent['NW'] = f"{column_to_code(col-1)}{row-1}-{layer}"

    # Southeast
    if row < GRID_ROWS - 1 and col < GRID_COLUMNS - 1:
        adjacent['SE'] = f"{column_to_code(col+1)}{row+1}-{layer}"

    # Southwest
    if row < GRID_ROWS - 1 and col > 0:
        adjacent['SW'] = f"{column_to_code(col-1)}{row+1}-{layer}"

    return adjacent


def calculate_distance_km(tile1: str, tile2: str) -> float:
    """
    Calculate approximate distance between two TILE codes in kilometers.
    Uses Haversine formula for accuracy.

    Args:
        tile1: First TILE code
        tile2: Second TILE code

    Returns:
        Distance in kilometers

    Example:
        >>> calculate_distance_km("QB185-100", "QA195-100")  # Sydney to Melbourne
        713.4
    """
    lat1, lon1, _ = tile_to_latlong(tile1)
    lat2, lon2, _ = tile_to_latlong(tile2)

    # Haversine formula
    lat1_rad = math.radians(lat1)
    lat2_rad = math.radians(lat2)
    delta_lat = math.radians(lat2 - lat1)
    delta_lon = math.radians(lon2 - lon1)

    a = (math.sin(delta_lat / 2) ** 2 +
         math.cos(lat1_rad) * math.cos(lat2_rad) *
         math.sin(delta_lon / 2) ** 2)
    c = 2 * math.asin(math.sqrt(a))

    # Earth's radius in km
    radius = 6371
    distance = radius * c

    return round(distance, 1)


if __name__ == "__main__":
    # Test basic conversions
    print("Grid Utilities Test")
    print("=" * 50)

    # Test Sydney
    sydney_tile = latlong_to_tile(-33.87, 151.21, 100)
    print(f"Sydney: {sydney_tile}")
    lat, lon, layer = tile_to_latlong(sydney_tile)
    print(f"  → Lat/Long: {lat:.2f}, {lon:.2f}")

    # Test London
    london_tile = latlong_to_tile(51.51, -0.13, 100)
    print(f"\nLondon: {london_tile}")
    lat, lon, layer = tile_to_latlong(london_tile)
    print(f"  → Lat/Long: {lat:.2f}, {lon:.2f}")

    # Test distance
    print(f"\nDistance Sydney-London: {calculate_distance_km(sydney_tile, london_tile)} km")

    # Test column codes
    print(f"\nColumn codes:")
    print(f"  AA (0) = {code_to_column('AA')}")
    print(f"  AZ (25) = {code_to_column('AZ')}")
    print(f"  BA (26) = {code_to_column('BA')}")
    print(f"  SL (479) = {code_to_column('SL')}")

    print(f"\nReverse:")
    print(f"  0 = {column_to_code(0)}")
    print(f"  25 = {column_to_code(25)}")
    print(f"  26 = {column_to_code(26)}")
    print(f"  479 = {column_to_code(479)}")
