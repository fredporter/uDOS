# uDOS Layer Architecture

The **Layer Architecture** (introduced in v1.1.12) is a standardized system for organizing game world locations across different spatial scales.

## Overview

uDOS uses a **grid-based layer system** where each layer represents a different zoom level of the game world:

- **Grid System**: 480 × 270 tiles (2-letter column codes AA-RL + row numbers 0-269)
- **Layer System**: 100-899 (hundreds digit indicates layer type)
- **TILE Code Format**: `COLUMN+ROW-LAYER` (e.g., `AA340-100` for Sydney at world layer)

## Layer Ranges

### 100-199: Physical Earth (Core)
Earth-based locations managed by `core/` system.

| Layer | Name | Scale | Resolution | Module |
|-------|------|-------|------------|--------|
| 100 | World | ~83km/cell | Continents, major cities | `core/uDOS_grid.py` |
| 200 | Region | ~2.78km/cell | Cities, towns, districts | `core/uDOS_grid.py` |
| 300 | City | ~93m/cell | Buildings, streets, blocks | `core/uDOS_grid.py` |
| 400 | District | ~3m/cell | Rooms, interior spaces | `core/uDOS_grid.py` |
| 500 | Block | ~10cm/cell | Objects, fine detail | `core/uDOS_grid.py` |

**Example TILE Codes:**
```
AA340-100   → Sydney, Australia (world layer)
AA340-200   → Sydney CBD (region layer)
JF57-100    → London, UK (world layer)
```

### 200-399: Virtual Earth (Core)
Non-physical Earth locations (virtual spaces, alternate dimensions).

**Reserved for future expansion** - examples:
- 200-299: Virtual reality spaces
- 300-399: Alternate timelines, parallel dimensions

### 400-599: Dungeons (Extensions)
Underground dungeons, caves, and procedurally generated spaces.

| Layer Range | Purpose | Location |
|-------------|---------|----------|
| 400-499 | Procedural dungeons | `extensions/play/services/game_mechanics/dungeon_service.py` |
| 500-599 | Quest-specific dungeons | `extensions/play/` |

**Example TILE Codes:**
```
BH15-400    → Dungeon entrance (floor 1)
BH15-401    → Dungeon floor 2
BH15-450    → Boss room
```

### 600-899: Space (Extensions)
Space-based locations, stations, planets, starships.

| Layer Range | Purpose | Location |
|-------------|---------|----------|
| 600-699 | Solar system | `extensions/play/services/game_mechanics/space_service.py` |
| 700-799 | Galaxy map | `extensions/play/` |
| 800-899 | Starship interiors | `extensions/play/` |

**Example TILE Codes:**
```
AA100-600   → Earth orbit
AA100-650   → ISS interior
CD200-700   → Mars (solar system view)
```

## Core vs Extensions Boundary

### Core Layers (100-399)
**Location**: `core/` directory
**Purpose**: Earth-based, real-world locations
**Stability**: Stable, production-ready, minimal changes
**Requirements**: Must work offline, no external dependencies

**Files**:
- `core/uDOS_grid.py` - Grid and layer management
- `core/data/geography.json` - Location metadata
- `extensions/assets/data/major_cities.json` - City database

### Extension Layers (400-899)
**Location**: `extensions/play/` directory
**Purpose**: Gameplay mechanics (dungeons, space travel)
**Stability**: Experimental, can change
**Requirements**: Optional, can have dependencies

**Files**:
- `extensions/play/services/game_mechanics/dungeon_service.py`
- `extensions/play/services/game_mechanics/space_service.py`
- `extensions/play/data/` - Gameplay data

## TILE Code Format

### Structure
```
COLUMN + ROW + "-" + LAYER
```

**Examples**:
```
AA340       → Grid position only (Sydney)
AA340-100   → Sydney at world layer
AA340-200   → Sydney at region layer
BH15-400    → Dungeon floor 1
```

### Column Codes (AA-RL)
Two-letter codes representing columns 0-479:
- AA = column 0
- AB = column 1
- BA = column 26
- RL = column 479

**Conversion**:
```python
def column_to_code(col: int) -> str:
    """Convert column number (0-479) to 2-letter code."""
    first = chr(ord('A') + col // 26)
    second = chr(ord('A') + col % 26)
    return first + second

def code_to_column(code: str) -> int:
    """Convert 2-letter code to column number."""
    first = ord(code[0]) - ord('A')
    second = ord(code[1]) - ord('A')
    return first * 26 + second
```

### Row Numbers (0-269)
Simple integer row numbers: `0`, `1`, `2`, ..., `269`

### Layer Suffix (Optional)
- Format: `-XXX` (3 digits, 100-899)
- Default: Omit suffix for layer-agnostic operations
- Explicit: Include suffix for layer-specific operations

## Usage Examples

### Basic Location (World Layer)
```python
# uCODE
SET LOCATION = "AA340-100"   # Sydney, world layer
GET TILE_NAME                # Returns: "Sydney, AU"

# Python
from core.uDOS_grid import Grid
grid = Grid()
location = grid.get_tile_info("AA340-100")
# {'name': 'Sydney', 'country': 'AU', 'layer': 100}
```

### Zooming Between Layers
```python
# Start at world layer
SET LOCATION = "AA340-100"   # Sydney (83km view)

# Zoom in to region
SET LOCATION = "AA340-200"   # Sydney CBD (2.78km view)

# Zoom in to city
SET LOCATION = "AA340-300"   # Downtown blocks (93m view)
```

### Dungeon Navigation
```python
# Enter dungeon at grid position BH15
SET LOCATION = "BH15-400"    # Floor 1
MOVE DOWN                    # Descend to floor 2
GET LOCATION                 # Returns: "BH15-401"
```

### Space Travel
```python
# Launch from Earth
SET LOCATION = "AA100-600"   # Earth orbit
TRAVEL MARS                  # Navigate to Mars
GET LOCATION                 # Returns: "CD200-600"
```

## Layer Management in Code

### Registering New Layers
```python
# In extensions/play/services/game_mechanics/custom_service.py

from core.uDOS_grid import Grid

def register_custom_layer():
    """Register custom layer with grid system."""
    grid = Grid()

    # Register layer 650 (custom space station interiors)
    grid.register_layer(
        layer_id=650,
        name="Space Station Interior",
        scale="10m/cell",
        category="space",
        provider="custom_service"
    )
```

### Validating TILE Codes
```python
from core.utils.common import is_valid_tile_code

# Validate format
is_valid_tile_code("AA340-100")  # True
is_valid_tile_code("AA340")      # True (no layer)
is_valid_tile_code("ZZ999-100")  # False (invalid column)
is_valid_tile_code("AA340-50")   # False (layer < 100)
is_valid_tile_code("AA340-900")  # False (layer > 899)
```

## Design Principles

### 1. Separation of Concerns
- **Core layers (100-399)**: Real-world, stable, production-ready
- **Extension layers (400-899)**: Gameplay, experimental, optional

### 2. Consistency
- All TILE codes use same format (COLUMN+ROW-LAYER)
- All layers use 480×270 grid
- Layer ranges group related content (100s = Earth, 400s = Dungeons, etc.)

### 3. Extensibility
- New layer ranges can be added (900-999 reserved for future use)
- Extensions can define custom layers within their ranges
- Core system provides validation and utilities

### 4. Backwards Compatibility
- Layer suffix is optional (defaults to layer 100)
- Old coordinate formats are deprecated but supported via migration tools
- TILE codes are forward-compatible (new layers don't break old code)

## Migration from Old Formats

### Deprecated Formats (v1.x)
```python
# ❌ Old hierarchical format (DEPRECATED)
"OC-AU-SYD"  # Continent-Country-City

# ❌ Old coordinate format (DEPRECATED)
[-33.87, 151.21]  # Latitude, Longitude

# ✅ New TILE code format (v1.1.12+)
"AA340-100"  # Grid position + layer
```

### Migration Tools
```bash
# Convert old .udt files to TILE codes
python dev/tools/migrate_tile_codes.py memory/user/locations.udt

# Validate TILE codes in files
python dev/tools/validate_tiles.py --check-all
```

## See Also

- [Mapping System](Mapping-System.md) - Full mapping documentation
- [Dev vs Sandbox Guide](Dev-Sandbox-Guide.md) - File organization
- [Developers Guide](Developers-Guide.md) - Core vs extensions architecture
- `core/uDOS_grid.py` - Grid implementation
- `extensions/play/services/game_mechanics/` - Extension layer implementations
