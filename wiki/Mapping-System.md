# uDOS Mapping System Documentation
## Multi-Layer Grid Navigation with Real-World Integration

### Overview

The uDOS Mapping System provides a multi-layered grid-based navigation framework inspired by NetHack dungeon levels, integrated with real-world geographic locations. It allows users to navigate through virtual layers (dungeons, cloud networks, satellite views) while maintaining a connection to actual physical locations.

---

## Architecture

### Core Components

1. **MapEngine** (`uDOS_map.py`)
   - Multi-layer map management
   - Position tracking
   - Real-world location integration
   - NetHack-style layer transitions

2. **MapLayer** Class
   - Individual layer representation
   - Grid cell storage
   - Metadata (connections, accessibility)
   - Visit tracking

3. **WorldLocation** Class
   - Real-world geographic data
   - Timezone information
   - Coordinate mapping (lat/lon to grid)

4. **WORLDMAP.UDO** Dataset
   - Timezones (15 major zones)
   - Continents (7 regions)
   - Countries (10+ nations)
   - Cities (10 major metros with coordinates)
   - Virtual layer definitions

---

## Layer System

### Default Layers (by depth)

#### Sky/Virtual Layers (Positive Depth)
- **SATELLITE** (depth: +100) - Satellite data network
- **CLOUD** (depth: +10) - Cloud computing layer

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
- **Grid**: Dictionary of (x,y) coordinates → cell data
- **Metadata**:
  - Created timestamp
  - Description
  - Accessibility (OPEN, LOCKED, DISCOVERED, HIDDEN)
  - Connections (list of accessible adjacent layers)

---

## Commands

### Core Navigation Commands

#### MAP [STATUS|VIEW|LAYER]
Display current position, layer info, or ASCII map
```
MAP STATUS    # Show detailed position info
MAP VIEW      # Display ASCII map of current area
MAP           # Alias for MAP STATUS
```

#### GOTO <x> <y>
Teleport to specific coordinates on current layer
```
GOTO 100 50   # Jump to position (100, 50)
GOTO -20 30   # Negative coordinates supported
```

#### MOVE <dx> <dy>
Move relative to current position
```
MOVE 5 0      # Move 5 units east
MOVE 0 -3     # Move 3 units south
MOVE -2 2     # Move 2 west, 2 north
```

#### LAYER [name]
Switch to different layer or list available layers
```
LAYER              # List all accessible layers
LAYER CLOUD        # Switch to cloud layer
LAYER DUNGEON-1    # Enter first dungeon level
```

#### DESCEND
Move down one layer (NetHack `>` command)
```
DESCEND            # Go to next lower connected layer
```

#### ASCEND
Move up one layer (NetHack `<` command)
```
ASCEND             # Return to next higher connected layer
```

#### LOCATE <city>
Set real-world location to a major city
```
LOCATE Tokyo       # Set location to Tokyo, Japan
LOCATE "New York"  # Use quotes for multi-word cities
```

#### WHERE
Alias for MAP STATUS
```
WHERE              # Show current location
```

### Themed Command Aliases (DUNGEON_CRAWLER)

From LEXICON.UDO:
- `CHART` → MAP
- `SURVEY` → WHERE
- `REALM` → LAYER
- `DELVE` → DESCEND
- `CLIMB` → ASCEND
- `TELEPORT` → GOTO
- `WALK` → MOVE
- `ANCHOR` → LOCATE

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
