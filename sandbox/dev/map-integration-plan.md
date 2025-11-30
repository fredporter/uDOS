# Map Grid System Integration Plan
**Date**: 2025-11-30  
**Version**: 2.0.0  
**Status**: 📋 PLANNING

## Overview

Integrate existing planets, universe, and cities data with the new grid-first TILE code system, and implement ASCII/teletext-style map layer generation with location markers.

## Current Data Files Status

### 1. Universe Data (`core/data/universe.json`)
**Status**: ✅ Compatible (no grid data needed)
- Contains solar system/galaxy metadata
- Planet physical properties (radius, gravity, atmosphere)
- No location data required (celestial bodies)
- **Action**: No changes needed

### 2. Planets Data (`sandbox/user/planets.json`)
**Status**: ✅ Already Updated
- Earth location: `JF57-100` (London)
- Mars location: `null` (no location yet)
- **Action**: Add Mars base location when colonization scenarios implemented

### 3. Cities Data (`extensions/assets/data/cities.json`)
**Status**: ❌ NEEDS MIGRATION
- Currently uses old grid format (e.g., `AB320`, `AM240`)
- Grid cells don't match new system
- Missing TILE codes
- Missing lat/long coordinates
- **Action**: Convert to new TILE code format

### 4. World Map Data (`extensions/assets/data/map_layer_100.json`)
**Status**: ✅ Generated
- 36 major cities with TILE codes
- Includes lat/long, timezone, country data
- **Action**: Merge with cities.json data

## Integration Tasks

### Task 1: Migrate Cities Data ✅ PRIORITY

**Current Format** (cities.json):
```json
{
  "name": "Sydney",
  "country": "AU",
  "grid_cell": "AA340",
  "tzone": "AEST",
  "climate": "temperate"
}
```

**New Format** (integrated):
```json
{
  "name": "Sydney",
  "country": "Australia",
  "country_code": "AU",
  "tile_code": "QZ185-100",
  "grid_cell": "QZ185",
  "layer": 100,
  "latitude": -33.87,
  "longitude": 151.21,
  "timezone": {
    "name": "AEST",
    "offset": "+10:00"
  },
  "climate": "temperate",
  "languages": ["en"],
  "region": "Oceania",
  "continent": "Oceania",
  "type": "city",
  "population_class": "major"
}
```

**Steps**:
1. Create migration script to convert old grid cells to TILE codes
2. Add lat/long coordinates for all cities
3. Merge with map_layer_100.json data
4. Expand to 50+ major cities
5. Validate all TILE codes
6. Update metadata

### Task 2: Enhance Map Engine for City Data

**Add Methods**:
```python
# In MapEngine class
def load_cities(self) -> List[Dict]:
    """Load all cities from cities.json."""
    
def find_cities_in_region(self, tile_code: str, radius_km: float) -> List[Dict]:
    """Find cities within radius of a TILE code."""
    
def get_city_by_name(self, name: str) -> Optional[Dict]:
    """Get city data by name."""
    
def get_nearest_city(self, tile_code: str) -> Optional[Dict]:
    """Find nearest city to a TILE code."""
```

### Task 3: ASCII/Teletext Map Layer Generation

**Objectives**:
- Generate ASCII art maps for each layer
- Display city markers and labels
- Show grid coordinates
- Support multiple zoom levels
- Render in teletext style (80×24 or 40×25)

**Map Renderer Specifications**:

#### Layer 100 World Map (80×24 format)
```
┌──────────────────────────────────────────────────────────────────────────────┐
│ uDOS WORLD MAP - Layer 100 (~83km/cell)                           Page 100  │
├──────────────────────────────────────────────────────────────────────────────┤
│        AA    BA    CA    DA    EA    FA    GA    HA    IA    JA    KA    LA │
│  0   ·  ·  ·  ·  ·  ·  ·  ·  ·  ·  ·  ·  ·  ·  ·  ·  ·  ·  ·  ·  ·  ·  ·  ·  │
│ 30   ·  ·  ·  ·  ·  ·  ·  ·  ·  ·  ·  ·  ·  ·  ·  ·  ·  ·  ·  ·  ·  ·  ·  ·  │
│ 60   ·  ·  ·  ·  ·  ·  ·  ● NYC·  ● LON·  ·  ·  ·  ●  MOS ·  ·  ·  ·  ·  ·  │
│ 90   ·  ·  ·  ·  ·  ·  ·  ·  ·  ·  ·  ·  ·  ·  ·  ·  ·  ·  ● TYO·  ·  ·  ·  │
│120   ·  ·  ·  ·  ·  ·  ·  ·  ·  ·  ·  ·  ·  ·  ·  ·  ·  ·  ·  ·  ·  ·  ·  ·  │
│150   ·  ·  ·  ·  ·  ·  ·  ·  ·  ·  ·  ·  ·  ·  ·  ·  ·  ·  ·  ·  ·  ·  ·  ·  │
│180   ·  ·  ·  ·  ·  ·  ·  ·  ·  ·  ·  ·  ·  ·  ·  ·  ·  ·  ·  ·  ●  SYD ·  ·  │
│210   ·  ·  ·  ·  ·  ·  ·  ·  ·  ·  ·  ·  ·  ·  ·  ·  ·  ·  ·  ·  ·  ·  ·  ·  │
│        AA    BA    CA    DA    EA    FA    GA    HA    IA    JA    KA    LA │
├──────────────────────────────────────────────────────────────────────────────┤
│ Legend: ● Major City  ○ City  · Ocean/Land  [ZOOM IN] [SEARCH] [GOTO]      │
└──────────────────────────────────────────────────────────────────────────────┘
```

#### City Detail View (Layer 300)
```
┌──────────────────────────────────────────────────────────────────────────────┐
│ SYDNEY - Layer 300 (~93m/cell)                        QZ185-300  Page 300   │
├──────────────────────────────────────────────────────────────────────────────┤
│                                                                              │
│         ┌─────────────────────────────────────────┐                         │
│         │  ░░░░  ░░░  ▓▓▓▓  ░░░░  ░░░  ████  ░░  │  Harbor                  │
│         │  ░░░  ████  ████  ████  ████  ████  ░  │                          │
│         │  ░░  █CBD█  ████  ████  ████  ████  ░░ │  ██ Commercial           │
│         │  ░░  ████  ████  ●OPR  ████  ████  ░░  │  ▓▓ Residential          │
│         │  ░░░  ████  ████  ████  ████  ░░░  ░░  │  ░░ Water/Park           │
│         │  ░░░░  ░░░  ████  ░░░  ░░░░  ░░░  ░░░  │  ● Landmark              │
│         └─────────────────────────────────────────┘                         │
│                                                                              │
│  Landmarks: ● Opera House (OPR)  ● Harbour Bridge  ● CBD                    │
│  Grid: QZ185  Coordinates: 33.87°S, 151.21°E                                │
├──────────────────────────────────────────────────────────────────────────────┤
│ [ZOOM OUT] [ZOOM IN] [MOVE N/S/E/W] [LOCATE]                   SYDNEY, AU  │
└──────────────────────────────────────────────────────────────────────────────┘
```

**Character Set** (Teletext-Compatible):
```
· = Empty/Ocean
░ = Water/Light
▒ = Park/Medium
▓ = Residential
█ = Urban/Commercial
● = Major Landmark
○ = Minor Landmark
◆ = Points of Interest
▲ = Mountains
~ = Water
≈ = Ocean
```

### Task 4: Map Layer Generator Script

**Create**: `sandbox/scripts/generate_map_layers.py`

**Functionality**:
1. Generate ASCII art for each layer (100-500)
2. Place city markers based on TILE codes
3. Add labels for major cities
4. Export as text files or JSON with render data
5. Support multiple rendering styles (box-drawing, block, Unicode)

**Output Format**:
```json
{
  "layer": 100,
  "width": 80,
  "height": 24,
  "format": "ascii",
  "cells": [
    {"x": 0, "y": 0, "char": "·", "color": "blue"},
    {"x": 40, "y": 12, "char": "●", "color": "red", "label": "LON"}
  ],
  "markers": [
    {"tile_code": "JF57-100", "char": "●", "label": "LON", "name": "London"}
  ]
}
```

### Task 5: Map Command Integration

**Update**: `core/commands/map_handler.py`

**New Commands**:
```
MAP                    # Show world map (layer 100)
MAP LAYER 300          # Show specific layer
MAP ZOOM IN            # Increase layer (100→200→300)
MAP ZOOM OUT           # Decrease layer
MAP GOTO Sydney        # Navigate to city
MAP SEARCH water       # Find POIs
MAP MOVE N             # Move north one cell
MAP ROUTE LON NYC      # Show route between cities
MAP LEGEND             # Show map symbols
```

**ASCII Output Example**:
```python
def render_map(layer: int = 100, center_tile: str = None):
    """Render ASCII map for terminal display."""
    engine = get_map_engine()
    
    # Get viewport (what cells to display)
    viewport = calculate_viewport(center_tile or engine.current_tile, width=80, height=20)
    
    # Render grid
    grid = []
    for row in viewport['rows']:
        line = []
        for col in viewport['cols']:
            tile_code = f"{column_to_code(col)}{row}-{layer}"
            cell_info = engine.get_cell_info(tile_code)
            
            if 'name' in cell_info:  # City
                line.append('●')
            elif cell_info.get('type') == 'ocean':
                line.append('~')
            else:
                line.append('·')
        grid.append(''.join(line))
    
    return '\n'.join(grid)
```

### Task 6: Location Markers & Labels

**Marker System**:
```python
class MapMarker:
    """Represents a marker on the map."""
    
    def __init__(self, tile_code: str, marker_type: str, label: str = None):
        self.tile_code = tile_code
        self.type = marker_type  # 'city', 'landmark', 'poi', 'user'
        self.label = label
        self.char = self._get_char()
        self.color = self._get_color()
    
    def _get_char(self) -> str:
        """Get display character for marker type."""
        return {
            'city': '●',
            'landmark': '◆',
            'poi': '○',
            'user': '▲'
        }.get(self.type, '·')
```

**Label Positioning**:
- Major cities: Show full name
- Minor cities: Show abbreviation (3 letters)
- POIs: Show on hover/select
- Grid coordinates: Show on edges

## Implementation Plan

### Phase 1: Data Migration (Priority: HIGH)
**Duration**: 2-3 hours

1. ✅ Create `sandbox/scripts/migrate_cities_data.py`
2. ✅ Convert all cities to new TILE code format
3. ✅ Add lat/long coordinates
4. ✅ Merge with map_layer_100.json
5. ✅ Validate all conversions
6. ✅ Update cities.json with new format

### Phase 2: Map Renderer (Priority: HIGH)
**Duration**: 4-6 hours

1. ✅ Create `core/ui/map_renderer.py`
2. ✅ Implement ASCII grid generation
3. ✅ Add marker placement system
4. ✅ Create label positioning algorithm
5. ✅ Support multiple character sets
6. ✅ Add color/styling support

### Phase 3: Map Commands (Priority: MEDIUM)
**Duration**: 3-4 hours

1. Update `core/commands/map_handler.py`
2. Implement MAP command variants
3. Add navigation (ZOOM, MOVE, GOTO)
4. Integrate with map renderer
5. Add search functionality
6. Create help text

### Phase 4: Enhanced Features (Priority: LOW)
**Duration**: 2-3 hours

1. Add terrain types (ocean, mountain, desert)
2. Implement pathfinding visualization
3. Add distance/scale indicators
4. Create minimap for context
5. Add bookmark/favorites system
6. Export maps as text/JSON

## Technical Specifications

### Map Viewport Calculation
```python
def calculate_viewport(center_tile: str, width: int = 80, height: int = 20):
    """Calculate which grid cells to display."""
    parsed = parse_tile_code(center_tile)
    center_col = parsed['column_num']
    center_row = parsed['row']
    
    # Calculate visible range
    half_width = width // 2
    half_height = height // 2
    
    col_start = max(0, center_col - half_width)
    col_end = min(GRID_COLUMNS - 1, center_col + half_width)
    row_start = max(0, center_row - half_height)
    row_end = min(GRID_ROWS - 1, center_row + half_height)
    
    return {
        'cols': range(col_start, col_end + 1),
        'rows': range(row_start, row_end + 1),
        'center': (center_col, center_row)
    }
```

### Cell Type Detection
```python
def get_cell_type(tile_code: str) -> str:
    """Determine cell type for rendering."""
    lat, lon, _ = tile_to_latlong(tile_code)
    
    # Simple heuristic (can be enhanced with real terrain data)
    if is_ocean(lat, lon):
        return 'ocean'
    elif is_mountain(lat, lon):
        return 'mountain'
    else:
        return 'land'
```

### Rendering Pipeline
```
1. Get viewport (center tile + dimensions)
2. For each cell in viewport:
   a. Get cell TILE code
   b. Load cell data from layer
   c. Determine cell type
   d. Select character/color
   e. Check for markers
3. Add labels for cities
4. Add grid coordinates
5. Add legend/UI elements
6. Return rendered string
```

## Data Structure Updates

### Enhanced cities.json
```json
{
  "metadata": {
    "version": "2.0.0",
    "total_cities": 50,
    "coordinate_system": "uDOS TILE grid (480x270, 83km @ layer 100)",
    "last_updated": "2025-11-30"
  },
  "cities": [
    {
      "name": "Sydney",
      "country": "Australia",
      "country_code": "AU",
      "tile_code": "QZ185-100",
      "grid_cell": "QZ185",
      "layer": 100,
      "latitude": -33.87,
      "longitude": 151.21,
      "timezone": {"name": "AEST", "offset": "+10:00"},
      "climate": "temperate",
      "languages": ["en"],
      "region": "Oceania",
      "continent": "Oceania",
      "type": "city",
      "population_class": "major",
      "landmarks": ["Opera House", "Harbour Bridge", "CBD"]
    }
  ]
}
```

### Map Layer with Terrain
```json
{
  "layer": 100,
  "cells": {
    "QZ185": {
      "name": "Sydney",
      "terrain": "coastal",
      "elevation_m": 58,
      "biome": "temperate_coastal"
    },
    "AA0": {
      "terrain": "ocean",
      "depth_m": -4000
    }
  }
}
```

## Success Metrics

- ✅ All 25+ cities migrated to new TILE format
- ✅ ASCII map renders at layer 100 (world view)
- ✅ City markers display correctly
- ✅ MAP command works with new system
- ✅ ZOOM IN/OUT functions properly
- ✅ Search finds cities by name
- ✅ Route calculation displays on map

## Next Steps

1. **Immediate**: Run migration script for cities.json
2. **Today**: Implement map renderer
3. **Tomorrow**: Update MAP command
4. **Week 1**: Add enhanced features (terrain, pathfinding)
5. **Week 2**: Documentation and polish

---

**Status**: Ready to begin implementation  
**Estimated Total Time**: 12-16 hours  
**Priority Order**: Data Migration → Renderer → Commands → Features
