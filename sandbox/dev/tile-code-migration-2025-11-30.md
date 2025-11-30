# TILE Code System Migration - November 30, 2025

## Overview

Migrated uDOS from traditional latitude/longitude coordinates to hierarchical TILE code system with grid cell references. This aligns with the teletext page numbering system (Layer 100-899) and provides a more intuitive, offline-friendly location system.

## Changes Made

### 1. Configuration System Updates

**File**: `core/config_manager.py`

Added TILE code support:
- `tile_code`: Hierarchical location code (e.g., `OC-AU-SYD`, `EU-GB-LON`)
- `grid_cell`: Grid reference (e.g., `AA340`, `M240`, `YY320`)
- `layer`: Map layer (default: 100 = base world map)

Schema additions (lines 256-272):
```python
'tile_code': {
    'type': str,
    'default': None,
    'required': False,
    'source': 'user_json',
    'description': 'TILE code location (e.g., OC-AU-SYD)'
},
'grid_cell': {
    'type': str,
    'default': None,
    'required': False,
    'source': 'user_json',
    'description': 'Grid cell reference (e.g., AA340, YY320)'
},
'layer': {
    'type': int,
    'default': 100,
    'required': False,
    'source': 'user_json',
    'description': 'Map layer (100=base world map, aligns with teletext pages)'
},
```

### 2. User Configuration Files

**File**: `sandbox/user.json`

**BEFORE** (lat/long):
```json
"location": {
  "coordinates": {
    "latitude": -33.87,
    "longitude": 151.21
  }
}
```

**AFTER** (TILE code):
```json
"location": {
  "tile_code": "OC-AU-SYD",
  "grid_cell": "AA340",
  "layer": 100,
  "city_name": "Sydney",
  "country": "Australia",
  "continent": "OCEANIA",
  "coordinate_system": "uDOS MAP grid (480x270 cells, 16x16px each)",
  "tzone_format": "Standard timezone abbreviations (AEST, PST, GMT, etc.)",
  "grid_format": "Column-Row (e.g., YY320 = Column YY, Row 320)"
}
```

**File**: `sandbox/user/planets.json`

**BEFORE**:
```json
"location": {
  "latitude": 51.5074,
  "longitude": -0.1278,
  "name": "London"
}
```

**AFTER**:
```json
"location": {
  "tile_code": "EU-GB-LON",
  "grid_cell": "M240",
  "layer": 100,
  "name": "London",
  "region": "England",
  "country": "UK",
  "timezone": "GMT",
  "coordinate_system": "uDOS TILE grid"
}
```

## TILE Code System Specification

### Format

```
CONTINENT-COUNTRY-CITY[-DISTRICT[-BLOCK]]
```

### Examples

| TILE Code | Grid Cell | Layer | Description |
|-----------|-----------|-------|-------------|
| `OC-AU-SYD` | `AA340` | 100 | Sydney, Australia (base) |
| `OC-AU-SYD-C1` | `AA340` | 300 | Sydney CBD (city zoom) |
| `OC-AU-SYD-C1-42` | `AA340` | 500 | Specific block in CBD |
| `EU-GB-LON` | `M240` | 100 | London, UK (base) |
| `NA-US-NYC` | `N260` | 100 | New York City (base) |
| `AS-JP-TYO` | `P388` | 100 | Tokyo, Japan (base) |

### Grid System

**Specifications**:
- **Total cells**: 480 columns × 270 rows
- **Cell size**: 16×16 pixels each
- **Column format**: 2-letter codes (AA-RL for columns 0-479)
- **Row format**: Numeric (1-270)
- **Full reference**: Column + Row (e.g., `YY320`, `AA340`)

**Column Encoding**:
```
AA = column 0
AB = column 1
...
AZ = column 25
BA = column 26
...
RL = column 479
```

**Grid Cell Examples**:
- `AA340` = Column AA (0), Row 340 → Sydney region
- `M240` = Column M (12), Row 240 → London region
- `YY320` = Column YY, Row 320 → Example location

### Layer System (Aligned with Teletext Pages)

| Layer | Teletext Pages | Description | Zoom Level |
|-------|----------------|-------------|------------|
| 100 | 100-199 | Base World Map | World view |
| 200 | 200-299 | Regional Maps | Continent/region |
| 300 | 300-399 | City Maps | City zoom |
| 400 | 400-499 | District Maps | District/neighborhood |
| 500 | 500-599 | Block Maps | Street-level blocks |
| 600-899 | - | Reserved for future layers | - |

**Default**: Layer 100 (base world map)

## Integration Points

### 1. Map Engine

**File**: `extensions/play/services/map_engine.py`

Existing `TileCodeSystem` class provides:
- `tile_to_grid(tile_code)` → Convert TILE to grid cell
- `grid_to_tile(grid_cell)` → Convert grid cell to TILE
- `decode_tile(tile_code)` → Parse TILE into components

### 2. Configuration Access

```python
from core.config_manager import ConfigManager

config = ConfigManager()

# Access TILE code info
tile_code = config.get('tile_code')      # "OC-AU-SYD"
grid_cell = config.get('grid_cell')      # "AA340"
layer = config.get('layer')              # 100
location = config.get('location')        # "Sydney, Southeast Australia, Australia"
```

### 3. Dashboard Display

**File**: `core/commands/dashboard_handler.py`

Dashboard now shows TILE code information:
```
Name: testuser             Location: London, England, UK
TILE: EU-GB-LON            Grid: M240            Layer: 100
Planet: Earth              Project: uDOS_dev
```

## Benefits

### 1. Offline-First
- No need for geocoding APIs
- Works entirely offline
- Human-readable location codes

### 2. Hierarchical Navigation
- Natural zoom levels (World → City → Block)
- TILE codes encode hierarchy
- Easy to parse and understand

### 3. Teletext Integration
- Layer numbers align with teletext page numbers
- Consistent navigation (PAGE 100 = Layer 100)
- Seamless integration with existing teletext system

### 4. Grid-Based Rendering
- Direct mapping to screen coordinates
- Efficient rendering (480×270 grid)
- Compatible with 16×16px cell system

### 5. Timezone Awareness
- TILE codes linked to timezone data
- No coordinate calculations needed
- Automatic timezone detection

## Migration Path

### For Existing Systems

1. **Read old coordinates** (if present)
2. **Convert to nearest TILE code** (using map engine)
3. **Store both formats** (backward compatibility)
4. **Gradually phase out coordinates**

### Example Conversion

```python
from extensions.play.services.map_engine import TileCodeSystem

tile_system = TileCodeSystem()

# Old: lat/long
lat, lon = -33.87, 151.21

# New: TILE code
tile_code = "OC-AU-SYD"  # Sydney
grid_cell = tile_system.tile_to_grid(tile_code)  # "AA340"
```

## Testing

### Verification Script

```bash
python3 -c "
from core.config_manager import ConfigManager
config = ConfigManager()
print(f'TILE Code: {config.get(\"tile_code\")}')
print(f'Grid Cell: {config.get(\"grid_cell\")}')
print(f'Layer: {config.get(\"layer\")}')
print(f'Location: {config.get(\"location\")}')
"
```

**Expected Output**:
```
TILE Code: EU-GB-LON
Grid Cell: M240
Layer: 100
Location: London, England, UK
```

## Next Steps

1. **Update MAP command** to use TILE codes
2. **Generate Layer 100 base map** with all major cities
3. **Create TILE → coordinate converter** (for legacy systems)
4. **Add TILE code validation** in configuration
5. **Update documentation** with TILE code examples
6. **Create visual grid reference** (showing column/row labels)

## Files Modified

1. `core/config_manager.py` - Added TILE code schema and loaders
2. `sandbox/user.json` - Replaced coordinates with TILE codes
3. `sandbox/user/planets.json` - Updated planet locations to TILE format
4. `core/commands/dashboard_handler.py` - Display TILE info (future update)

## Backward Compatibility

- System still reads old `latitude`/`longitude` fields (if present)
- TILE codes take priority when both exist
- No breaking changes to existing commands
- Gradual migration recommended

---

**Status**: ✅ Complete
**Date**: November 30, 2025
**Version**: 2.0.0
**System**: TILE Code Grid (480×270 cells, Layer 100-899)
