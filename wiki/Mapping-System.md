# uDOS Mapping System Documentation
## Multi-Layer Grid Navigation with Real-World Integration

### Overview

The uDOS Mapping System provides a multi-layered grid-based navigation framework with advanced visualization capabilities. Originally inspired by NetHack dungeon levels, it now integrates real-world geographic locations with modern features including:

- **TIZO Cell Grid System** (A1-RL270 addressing)
- **Teletext Mosaic Visualization** (64 block art characters)
- **Web Extension Interface** (Interactive teletext maps)
- **Real-World Geographic Integration** (20+ TIZO cities)
- **Multi-Layer Navigation** (Surface, Cloud, Satellite, Dungeons)

**Version History:**
- v1.0.3: TIZO cell system, enhanced navigation commands
- v1.0.4: Teletext rendering, web extension, mosaic block art

---

## Architecture

### Core Components

1. **MapEngine** (`core/services/map_engine.py`)
   - TIZO cell grid management (A1-RL270 system)
   - Multi-layer map coordination
   - Real-world location integration
   - Position tracking and navigation

2. **TeletextMosaicRenderer** (`core/services/teletext_renderer.py`)
   - 64 mosaic character generation (2×3 pixel patterns)
   - World Space Television (WST) color palette
   - ASCII-to-mosaic conversion algorithms
   - HTML output with teletext styling

3. **TeletextWebExtension** (`extensions/web/teletext_extension.py`)
   - Standalone HTTP server (localhost:8080)
   - Interactive web interface for teletext maps
   - Mobile-responsive design with touch controls
   - Export functionality (PNG, HTML)

4. **MapLayer** Class
   - Individual layer representation
   - Grid cell storage and metadata
   - Layer connections and accessibility
   - Visit tracking and state management

5. **WorldLocation** Class
   - Real-world geographic data (TIZO cities)
   - Coordinate mapping (lat/lon to cell references)
   - Timezone and connection quality information

---

## TIZO Cell Grid System

### Cell Reference Format

The TIZO system uses A1-RL270 format for global addressing:
- **Columns**: A-RL (484 columns, ~74km each)
- **Rows**: 1-270 (270 rows, ~74km each)
- **Coverage**: Global grid covering entire Earth surface
- **Cell Size**: Approximately 74km × 74km each

### Examples
```
JN196    # Melbourne, Australia cell
JV189    # Sydney, Australia cell
CB54     # London, UK cell
FD142    # New York, USA cell
```

### Coordinate Mapping

Cell centers map to latitude/longitude:
- **Latitude Range**: +85° to -85° (170° total)
- **Longitude Range**: -180° to +180° (360° total)
- **Cell Resolution**: ~0.63° per cell (~74km at equator)

---

## Layer System

### Default Layers (by depth)

#### Sky/Virtual Layers (Positive Depth)
- **SATELLITE-OC** (depth: +100) - Oceania satellite network
- **CLOUD-OC** (depth: +10) - Oceania cloud computing layer

#### Surface Layer (Zero Depth)
- **SURFACE** (depth: 0) - Physical world representation

#### Underground/Dungeon Layers (Negative Depth)
- **DUNGEON-1** (depth: -1) - First dungeon level
- **DUNGEON-2** (depth: -2) - Second dungeon level
- **DUNGEON-3** (depth: -3) - Third dungeon level
- **MINES** (depth: -10) - Data mining operations
- **CORE** (depth: -100) - System core (deepest)

### Layer Properties

Each layer has:
- **Name**: Human-readable identifier
- **Depth**: Vertical position (0=surface, -=underground, +=sky)
- **Type**: PHYSICAL, VIRTUAL, or HYBRID
- **Grid**: Dictionary of cell references → cell data
- **Metadata**:
  - Created timestamp
  - Description
  - Accessibility (OPEN, LOCKED, DISCOVERED, HIDDEN)
  - Connections (list of accessible adjacent layers)

---

## Teletext Visualization System

### Mosaic Character Set

The teletext renderer implements 64 unique mosaic characters:
- **Pattern**: 2×3 pixel grid per character
- **Encoding**: 6-bit pattern (0-63 decimal)
- **Style**: Classic teletext block art aesthetic

### Character Examples
```
█  ▀  ▄  ▌  ▐  ▗  ▖  ▘  ▝  ▞  ▚  ▟  ▙  ▛  ▜
```

### WST Color Palette

8-color World Space Television standard:
- **Black** (#000000)
- **Red** (#FF0000)
- **Green** (#00FF00)
- **Yellow** (#FFFF00)
- **Blue** (#0000FF)
- **Magenta** (#FF00FF)
- **Cyan** (#00FFFF)
- **White** (#FFFFFF)

### HTML Output Features

Generated teletext maps include:
- **Pixel-perfect character rendering** (CSS with exact fonts)
- **WST color palette styling** (background and foreground)
- **Mobile-responsive design** (touch-optimized controls)
- **Export functionality** (PNG image, HTML download)
- **Interactive controls** (zoom, pan, layer switching)

---

## Commands

### Enhanced Navigation Commands (v1.0.3+)

#### MAP STATUS
Display current location and system status
```bash
MAP STATUS           # Show detailed position info with TIZO cell
```

**Output Example:**
```
🗺️  Map Status
==============================
Current Location: Melbourne, Australia
TIZO Code: MEL
Cell Reference: JN196
Coordinates: -37.81°, 144.96°
Timezone: AEST (+10:00)
Accessible Layers: SURFACE, CLOUD-OC, SATELLITE-OC, DUNGEON-1
```

#### MAP VIEW [width] [height]
Generate ASCII map of current area
```bash
MAP VIEW             # Default 40×20 ASCII map
MAP VIEW 60 30       # Custom size ASCII map
```

#### MAP CITIES [cell] [radius]
List cities globally or in a region
```bash
MAP CITIES           # List all TIZO cities
MAP CITIES JN196 5   # Cities within 5 cells of JN196
```

#### MAP CELL <cell_reference>
Get detailed information about a specific cell
```bash
MAP CELL JN196       # Information about Melbourne cell
MAP CELL CB54        # Information about London cell
```

#### MAP NAVIGATE <from> <to>
Calculate navigation between locations
```bash
MAP NAVIGATE MEL SYD # Navigate Melbourne to Sydney
MAP NAVIGATE JN196 JV189  # Navigate by cell reference
```

#### MAP LOCATE <tizo_code>
Set location to a TIZO city
```bash
MAP LOCATE MEL       # Move to Melbourne
MAP LOCATE LON       # Move to London
MAP LOCATE NYC       # Move to New York
```

#### MAP GOTO <cell_reference|lat lon>
Move to specific coordinates or cell
```bash
MAP GOTO JN196       # Go to specific cell
MAP GOTO -37.81 144.96  # Go to coordinates
```

#### MAP LAYERS
Show accessible layers from current location
```bash
MAP LAYERS           # List available layers and connection quality
```

### Teletext Visualization Commands (v1.0.4+)

#### MAP TELETEXT [width] [height]
Generate teletext-style map with mosaic block art
```bash
MAP TELETEXT         # Default 40×20 teletext map
MAP TELETEXT 60 30   # Custom size teletext map
```

**Output Example:**
```
🖥️  Teletext Map Generated
===================================
Location: Melbourne, Australia
Cell: JN196
Size: 40×20 characters
Style: Mosaic block art

📄 File saved: output/teletext/udos_teletext_map_20251102_032408.html
🌐 Open in web browser to view
💡 Use MAP WEB to start local server
```

#### MAP WEB [server]
Open teletext maps in browser or start web server
```bash
MAP WEB              # Open latest teletext map in browser
MAP WEB SERVER       # Start HTTP server at localhost:8080
```

**Server Mode Features:**
- **Interactive Interface**: Zoom, pan, layer controls
- **Mobile Support**: Touch-optimized responsive design
- **Export Options**: PNG image, HTML download
- **Real-time Updates**: Live map generation and display
- **Multi-map Access**: All generated teletext maps available

---

## TIZO City Network

### Supported Cities (20 Total)

**Oceania:**
- MEL: Melbourne, Australia (JN196)
- SYD: Sydney, Australia (JV189)
- AKL: Auckland, New Zealand (LB194)

**Asia:**
- TYO: Tokyo, Japan (IB172)
- BJS: Beijing, China (IB72)
- HKG: Hong Kong (HV105)
- SIN: Singapore (GD89)
- BOM: Mumbai, India (FV105)
- DEL: Delhi, India (FE89)

**Europe:**
- LON: London, UK (CB54)
- BER: Berlin, Germany (CT52)
- FRA: Frankfurt, Germany (CS52)
- MOS: Moscow, Russia (DK41)

**Middle East/Africa:**
- DXB: Dubai, UAE (EW78)
- JNB: Johannesburg, South Africa (CD241)

**Americas:**
- NYC: New York, USA (FD142)
- LA: Los Angeles, USA (BD158)
- SFO: San Francisco, USA (BC149)
- TOR: Toronto, Canada (FE123)
- VAN: Vancouver, Canada (BD125)

### Connection Quality

Each city has region-specific connection speeds:
- **NATIVE**: Local region (fastest)
- **FAST**: Adjacent regions
- **STANDARD**: Distant regions
- **SLOW**: Antipodal regions

---

## World Map Data

### Supported Timezones

- UTC - Coordinated Universal Time
- EST - Eastern Standard Time (-05:00)
- CST - Central Standard Time (-06:00)
- MST - Mountain Standard Time (-07:00)
- PST - Pacific Standard Time (-08:00)
- GMT - Greenwich Mean Time (+00:00)
- CET - Central European Time (+01:00)
- JST - Japan Standard Time (+09:00)
- AEST - Australian Eastern (+10:00)
- IST - Indian Standard Time (+05:30)
- And more...

### Major Cities

Each city includes:
- Country and continent
- Latitude/longitude coordinates
- Timezone
- Region
- Grid mapping (x, y, layer)
- Optional dungeon entrance

**Available Cities:**
- New York, USA
- London, UK
- Tokyo, Japan
- Sydney, Australia
- Paris, France
- San Francisco, USA
- Mumbai, India
- Berlin, Germany
- Singapore
- São Paulo, Brazil

---

## Grid Coordinate System

### Coordinate Mapping

Real-world coordinates map to grid positions:
- **Longitude** → X axis (east/west)
- **Latitude** → Y axis (north/south)

Simplified mapping:
```
Grid X = floor(longitude)
Grid Y = floor(latitude)
```

Example: Tokyo (35.6762°N, 139.6503°E) → Grid (140, 36)

### Precision Modes

Defined in WORLDMAP.UDO:
- **WORLD** - 1° = 1 grid unit (continental scale)
- **COUNTRY** - 0.1° = 1 grid unit (national scale)
- **CITY** - 0.01° = 1 grid unit (urban scale)
- **DISTRICT** - 0.001° = 1 grid unit (neighborhood scale)
- **UCELL_16x16** - Terminal grid (16x16 character cells)

---

## User Profile Integration

### USER.UDO Fields

The mapping system integrates with user profiles:

```json
{
  "WORLD_LOCATION": {
    "COUNTRY": "Japan",
    "CITY": "Tokyo",
    "CONTINENT": "ASIA",
    "LATITUDE": 35.6762,
    "LONGITUDE": 139.6503,
    "REGION": "Kanto",
    "TIMEZONE": "JST"
  },
  "LOCATION_DATA": {
    "MAP_POSITION": {
      "X": 140,
      "Y": 36,
      "LAYER": "SURFACE"
    },
    "DUNGEON_LEVEL": 0,
    "VISITED_LAYERS": ["SURFACE", "DUNGEON-1"],
    "DISCOVERED_LOCATIONS": ["Tokyo", "London"]
  }
}
```

### First-Time Setup

During initial user setup, uDOS prompts for:
1. Name/alias
2. Timezone (auto-detected)
3. Text location description
4. **World map city selection** (optional)
   - Choose from list of major cities
   - Auto-configures coordinates, timezone, region
   - Sets initial map position

---

## API Reference

### MapEngine Methods

#### Navigation
```python
move(dx: int, dy: int) -> str
# Move relative to current position

goto(x: int, y: int) -> str
# Teleport to coordinates

change_layer(layer_name: str) -> str
# Switch to different layer

descend() -> str
# Move to lower connected layer

ascend() -> str
# Move to higher connected layer
```

#### Location Management
```python
set_real_world_location(city: str = None,
                       country: str = None,
                       latitude: float = None,
                       longitude: float = None,
                       timezone: str = "UTC")
# Set user's real-world location

get_current_status() -> str
# Get formatted status display

get_layer_map(width: int, height: int) -> str
# Generate ASCII map of current layer
```

#### Layer Access
```python
MapEngine.layers[name] -> MapLayer
# Access specific layer

MapEngine.current_layer -> str
# Current layer name

MapEngine.position -> Tuple[int, int]
# Current (x, y) coordinates

MapEngine.real_world_location -> WorldLocation
# Real-world location object
```

---

## Examples

### Basic Navigation
```
> MAP STATUS
============================================================
🗺️  MAP STATUS
============================================================

📍 Position: (0, 0)
🌍 Layer: SURFACE
   Depth: 0
   Type: PHYSICAL

🔗 Available Layers:
   ☁️  CLOUD (depth 10)
   ⬇️  DUNGEON-1 (depth -1)
============================================================

> GOTO 100 50
📍 Teleported to (100, 50) on SURFACE

> DESCEND
⬇️  Descended to DUNGEON-1

> WHERE
Current position: (100, 50) in DUNGEON-1 (depth: -1)
```

### Real-World Integration
```
> LOCATE Tokyo
📍 Location set to Tokyo, Japan
🌏 Coordinates: 35.6762°, 139.6503°
🕐 Timezone: JST
🗺️  Map position: (140, 36)

> MAP STATUS
============================================================
🗺️  MAP STATUS
============================================================

📍 Position: (140, 36)
🌍 Layer: SURFACE
   Depth: 0
   Type: PHYSICAL

🌏 Real World Location:
   City: Tokyo, Japan
   Coordinates: 35.6762°, 139.6503°
   Timezone: JST
============================================================
```

### Layer Exploration
```
> LAYER
🗺️  AVAILABLE LAYERS:

  ☁️  SATELLITE       (depth:  100)
  ☁️  CLOUD           (depth:   10)
  🌍 SURFACE         (depth:    0) ← YOU ARE HERE
  ⛏️  DUNGEON-1       (depth:   -1)
  ⛏️  DUNGEON-2       (depth:   -2)
  ⛏️  DUNGEON-3       (depth:   -3)
  ⛏️  MINES           (depth:  -10)
  ⛏️  CORE            (depth: -100)

> LAYER CLOUD
🔄 Switched to layer: CLOUD

> MAP VIEW
╔══════════════════════════════════════════╗
║             CLOUD                        ║
╠══════════════════════════════════════════╣
║                                          ║
║                                          ║
║                    @                     ║
║                                          ║
║                                          ║
╚══════════════════════════════════════════╝
@ = You (140, 36)
```

---

## Future Enhancements

### Planned Features

1. **Procedural Dungeon Generation**
   - Random dungeon layouts
   - Treasure placement
   - Monster encounters

2. **Waypoint System**
   - Save named locations
   - Quick travel between waypoints
   - Breadcrumb trails

3. **Mini-Map in Prompt**
   - Small ASCII map in prompt line
   - Real-time position indicator

4. **Location-Based Events**
   - Timezone-aware greetings
   - Weather integration
   - Local time display

5. **Multi-User Shared Maps**
   - Collaborative exploration
   - Shared discoveries
   - Message system

6. **Advanced Grid Precision**
   - Zoom levels
   - Sub-grid navigation
   - Fractal layering

---

## NetHack Inspiration

This system draws heavily from NetHack's dungeon navigation:

- **Stairways**: ASCEND/DESCEND for layer transitions
- **Depth Tracking**: Negative values for dungeon levels
- **Discovery**: Layers start HIDDEN or LOCKED
- **Connectivity**: Explicit connections between levels
- **Symbols**: @ for player, · for visited, ? for unexplored

---

## Technical Notes

### Performance

- Lazy loading of layer grids
- Visited cells tracked efficiently
- Worldmap loaded once at startup
- User position auto-saved on changes

### Data Persistence

- Current position saved to USER.UDO
- Layer history tracked
- Real-world location persisted
- Move count integrated with session tracking

### Extensibility

The system is designed to be extended:
- New layers easily added
- Custom grid systems supported
- Plugin architecture for layer behaviors
- Event hooks for position changes

---

## Troubleshooting

### Common Issues

**Q: "Unknown city" error when using LOCATE**
A: Check available cities with `LOCATE` (no arguments) or see WORLDMAP.UDO

**Q: "No path between realms" when changing layers**
A: Layers must be connected. Use ASCEND/DESCEND for dungeon navigation.

**Q: Map position not saved**
A: Ensure USER.UDO is writable. Check sandbox/ permissions.

**Q: Coordinates seem wrong**
A: Remember coordinates use simplified lat/lon mapping (rounded integers)

---

## Credits

- Inspired by NetHack (DevTeam)
- Geographic data from public sources
- Timezone data: IANA Time Zone Database
- City coordinates: GeoNames

---

## Version History

**v1.0 (2025-10-30)**
- Initial multi-layer system
- 8 default layers
- 10 major cities
- Real-world integration
- NetHack-style navigation
- First-time setup integration
