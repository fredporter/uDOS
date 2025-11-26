# uDOS Mapping System Documentation
## Hierarchical TILE Grid with Timezone-Based Location Detection

### Overview

The uDOS Mapping System provides a hierarchical grid-based navigation framework using alphanumeric **TILE codes** instead of lat/long coordinates. The system automatically detects user location via timezone and maps it to a base city tile for map functions.

**Key Concepts:**
- **TIZO/TZONE**: **T**ime**Z**one **I**dentified **O**rigin - timezone-based location detection (AEST→Sydney, JST→Tokyo)
- **TILE Codes**: Hierarchical alphanumeric grid system (AS-JP-TYO, EU-UK-LON, NA-US-NYC)
- **Map Layers**: Multi-layer visualization (Surface, Cloud, Satellite, Dungeons)
- **Hierarchical Zoom**: Zoom in/out by navigating tile sublayers

**Version History:**
- v1.0.3: Initial multi-layer system, timezone detection
- v1.0.4: Teletext rendering, web extension
- v2.0.0: TILE code system replaces lat/long (2024-11-26)

---

## TIZO/TZONE System (Location Detection)

### Purpose
TIZO (Timezone-Identified Zone Origin) is **not** a grid system. It's simply a method to detect user location at startup by mapping their timezone to a major city.

### How It Works
```
User Timezone (AEST) → City (Sydney) → TILE Code (OC-AU-SYD)
```

**Examples:**
- `AEST` → Sydney → `OC-AU-SYD`
- `JST` → Tokyo → `AS-JP-TYO`
- `EST` → New York → `NA-US-NYC`
- `GMT` → London → `EU-UK-LON`

This provides a sensible default map position without requiring manual location entry.

---

## TILE Code System (Map Grid)

### Hierarchical Structure

TILE codes use a hierarchical format: `CONTINENT-COUNTRY-CITY[-DISTRICT[-BLOCK]]`

**5 Zoom Levels:**

1. **World** (7 tiles) - Continents
   - `AS` (Asia), `EU` (Europe), `NA` (North America)
   - `SA` (South America), `AF` (Africa), `OC` (Oceania), `AN` (Antarctica)

2. **Region** - Countries (ISO 3166-1 alpha-2)
   - `AS-JP` (Japan), `EU-UK` (United Kingdom), `NA-US` (USA)

3. **City** - Major cities (3-letter codes)
   - `AS-JP-TYO` (Tokyo), `EU-UK-LON` (London), `NA-US-NYC` (New York)

4. **District** - City districts (A1-Z9 grid, 234 tiles)
   - `AS-JP-TYO-C5` (Shibuya), `NA-US-NYC-M3` (Manhattan)

5. **Block** - Street blocks (01-99)
   - `AS-JP-TYO-C5-42`, `NA-US-NYC-M3-17`

### TILE Code Examples

```
AS-JP-TYO          # Tokyo, Japan (city level)
AS-JP-TYO-C5       # Shibuya district, Tokyo
AS-JP-TYO-C5-42    # Specific block in Shibuya

EU-UK-LON          # London, UK
EU-UK-LON-W1       # Westminster district
EU-UK-LON-W1-23    # Specific block in Westminster

OC-AU-SYD          # Sydney, Australia
OC-AU-SYD-C1       # Sydney CBD
OC-AU-SYD-C1-05    # Block 5 in CBD
```

### Benefits Over Lat/Long

1. **Human-Readable**: `AS-JP-TYO` clearly means "Asia, Japan, Tokyo"
2. **Compact**: Shorter than coordinate strings
3. **Hierarchical**: Zoom by truncating (C5-42 → C5 → TYO → JP → AS)
4. **Decodable**: Convert to coordinates only when needed
5. **Consistent**: Same format worldwide

### Coordinate Conversion

TILE codes map to approximate center coordinates:

```python
# Encode coordinates to TILE
coords_to_tile(35.68, 139.69) → "AS-JP-TYO"

# Decode TILE to coordinates
tile_to_coords("AS-JP-TYO") → [35.68, 139.69]
```

Coordinates are stored in `locations.json` for reference, but all user locations are stored as TILE codes.

---

## Architecture

### Core Components

1. **MapEngine** (`core/services/map_engine.py`)
   - TILE code grid management
   - Multi-layer map coordination
   - Hierarchical zoom system
   - Position tracking and navigation

2. **Location System** (`core/data/locations.json`)
   - Timezone to city mappings (TIZO/TZONE detection)
   - TILE code definitions and hierarchy
   - Coordinate conversion reference
   - 12 major timezone cities

3. **TeletextMosaicRenderer** (`core/services/teletext_renderer.py`)
   - 64 mosaic character generation (2×3 pixel patterns)
   - World Space Television (WST) color palette
   - ASCII-to-mosaic conversion algorithms
   - HTML output with teletext styling

4. **TeletextWebExtension** (`extensions/web/teletext_extension.py`)
   - Standalone HTTP server (localhost:8080)
   - Interactive web interface for teletext maps
   - Mobile-responsive design with touch controls
   - Export functionality (PNG, HTML)

5. **MapLayer** Class
   - Individual layer representation
   - TILE-based cell storage and metadata
   - Layer connections and accessibility
   - Visit tracking and state management

---

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

---

## Layer System

### Default Layers (by depth)

#### Sky/Virtual Layers (Positive Depth)
- **SATELLITE** (depth: +100) - Global satellite network
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
- **Grid**: Dictionary of TILE codes → cell data
- **Metadata**:
  - Created timestamp
  - Description
  - Accessibility (OPEN, LOCKED, DISCOVERED, HIDDEN)
  - Connections (list of accessible adjacent layers)

---

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
Current Location: Sydney, Australia
Timezone: AEST (+10:00)
TILE Code: OC-AU-SYD
Continent: Oceania
Accessible Layers: SURFACE, CLOUD, SATELLITE, DUNGEON-1
```

#### MAP VIEW [width] [height]
Generate ASCII map of current area
```bash
MAP VIEW             # Default 40×20 ASCII map
MAP VIEW 60 30       # Custom size ASCII map
```

#### MAP LOCATE <timezone|city|tile>
Set location by timezone, city name, or TILE code
```bash
MAP LOCATE AEST      # Move to Sydney (timezone)
MAP LOCATE Tokyo     # Move to Tokyo (city name)
MAP LOCATE AS-JP-TYO # Move to Tokyo (TILE code)
```

#### MAP GOTO <tile_code>
Move to specific TILE location
```bash
MAP GOTO OC-AU-SYD       # Go to Sydney
MAP GOTO AS-JP-TYO-C5    # Go to Shibuya district, Tokyo
MAP GOTO EU-UK-LON-W1-23 # Go to specific block in Westminster
```

#### MAP ZOOM <in|out|level>
Navigate hierarchical tile layers
```bash
MAP ZOOM IN          # Zoom into district level
MAP ZOOM OUT         # Zoom out to city/region level
MAP ZOOM 3           # Jump to specific zoom level (city)
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
Location: Sydney, Australia
TILE: OC-AU-SYD
Size: 40×20 characters
Style: Mosaic block art

📄 File saved: output/teletext/udos_teletext_map_20241126_143000.html
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

## Supported Cities and Timezones

### 12 Major Cities (Timezone Detection)

**Oceania:**
- Sydney, Australia - AEST (+10:00) - `OC-AU-SYD`
- Auckland, New Zealand - NZST (+12:00) - `OC-NZ-AKL`

**Asia:**
- Tokyo, Japan - JST (+09:00) - `AS-JP-TYO`
- Shanghai, China - CST (+08:00) - `AS-CN-SHA`
- Singapore - SGT (+08:00) - `AS-SG-SIN`
- Mumbai, India - IST (+05:30) - `AS-IN-BOM`

**Europe:**
- London, UK - GMT (+00:00) - `EU-UK-LON`
- Berlin, Germany - CET (+01:00) - `EU-DE-BER`

**Americas:**
- New York, USA - EST (-05:00) - `NA-US-NYC`
- Los Angeles, USA - PST (-08:00) - `NA-US-LAX`
- São Paulo, Brazil - BRT (-03:00) - `SA-BR-SAO`

**Africa:**
- Johannesburg, South Africa - SAST (+02:00) - `AF-ZA-JNB`

### Timezone to Location Mapping

At startup, uDOS detects your system timezone and automatically maps you to the closest major city:

```
System Timezone → City → TILE Code → Map Position
AEST → Sydney → OC-AU-SYD → Starting location set
```

---

## Data Storage

### locations.json Structure

All location data is stored in `core/data/locations.json`:

```json
{
  "timezone_cities": {
    "AEST": {
      "name": "Sydney",
      "tile": "OC-AU-SYD",
      "coords": [-33.87, 151.21],
      "offset": "+10:00"
    }
  },
  "tile_system": {
    "encoding": "CONTINENT-COUNTRY-CITY[-DISTRICT[-BLOCK]]",
    "levels": { ... }
  }
}
```

### User Profile Storage

User locations are stored as TILE codes in `sandbox/user/USER.UDT`:

```json
{
  "location": {
    "current_tile": "AS-JP-TYO-C5",
    "home_tile": "OC-AU-SYD",
    "timezone": "JST",
    "layer": "SURFACE"
  }
}
```

No lat/long coordinates are stored - only TILE codes which can be decoded when needed.

---

## User Profile Integration

### USER.UDT Fields

The mapping system integrates with user profiles:

```json
{
  "location": {
    "current_tile": "AS-JP-TYO-C5",
    "home_tile": "OC-AU-SYD",
    "timezone": "JST",
    "layer": "SURFACE",
    "visited_tiles": ["OC-AU-SYD", "AS-JP-TYO", "EU-UK-LON"],
    "discovered_layers": ["SURFACE", "DUNGEON-1"]
  }
}
```

### First-Time Setup

During initial user setup, uDOS:
1. Auto-detects system timezone (e.g., AEST)
2. Maps timezone to city (AEST → Sydney)
3. Sets starting TILE code (OC-AU-SYD)
4. Initializes map position on SURFACE layer

No manual coordinate entry required!

---

## API Reference

### MapEngine Methods

#### Navigation
```python
move_to_tile(tile_code: str) -> str
# Move to specific TILE location

zoom_in() -> str
# Zoom into sublayer (city → district → block)

zoom_out() -> str
# Zoom out to parent layer (block → district → city)

change_layer(layer_name: str) -> str
# Switch to different layer (SURFACE, CLOUD, DUNGEON-1, etc.)

descend() -> str
# Move to lower connected layer

ascend() -> str
# Move to higher connected layer
```

#### Location Management
```python
set_location_by_timezone(timezone: str) -> str
# Set location based on timezone (AEST, JST, etc.)

get_current_tile() -> str
# Get current TILE code (e.g., "AS-JP-TYO-C5")

decode_tile(tile_code: str) -> dict
# Convert TILE to human-readable info and coordinates

encode_coords(lat: float, lon: float) -> str
# Convert coordinates to nearest TILE code

get_current_status() -> str
# Get formatted status display
```

#### Layer Access
```python
MapEngine.current_tile -> str
# Current TILE code

MapEngine.current_layer -> str
# Current layer name

MapEngine.zoom_level -> int
# Current zoom level (1-5)

MapEngine.layers[name] -> MapLayer
# Access specific layer
```

---

## Examples

### Basic Navigation with TILE Codes
```
> MAP STATUS
============================================================
🗺️  MAP STATUS
============================================================

📍 Location: OC-AU-SYD (Sydney, Australia)
🌍 Layer: SURFACE
   Depth: 0
   Type: PHYSICAL
   Zoom: Level 3 (City)

🔗 Available Layers:
   ☁️  CLOUD (depth 10)
   ⬇️  DUNGEON-1 (depth -1)
============================================================

> MAP GOTO AS-JP-TYO
📍 Moved to AS-JP-TYO (Tokyo, Japan)

> MAP ZOOM IN
🔍 Zoomed to district level: AS-JP-TYO-A1

> DESCEND
⬇️  Descended to DUNGEON-1
```

### Timezone-Based Location
```
> MAP LOCATE JST
📍 Location set to Tokyo, Japan
🌏 TILE: AS-JP-TYO
🕐 Timezone: JST (+09:00)
🗺️  Zoom Level: 3 (City)

> MAP STATUS
============================================================
🗺️  MAP STATUS
============================================================

📍 Location: AS-JP-TYO (Tokyo, Japan)
🌍 Layer: SURFACE
   Depth: 0
   Type: PHYSICAL

🕐 Timezone: JST (+09:00)
============================================================
```

### Hierarchical Zoom Navigation
```
> MAP LOCATE AEST
📍 Set to OC-AU-SYD (Sydney)

> MAP ZOOM IN
🔍 Zoomed to OC-AU-SYD-C1 (Sydney CBD district)

> MAP ZOOM IN
🔍 Zoomed to OC-AU-SYD-C1-01 (Block 1)

> MAP ZOOM OUT
🔍 Zoomed to OC-AU-SYD-C1 (district level)

> MAP ZOOM OUT
🔍 Zoomed to OC-AU-SYD (city level)

> MAP ZOOM OUT
🔍 Zoomed to OC-AU (Australia)

> MAP ZOOM OUT
🔍 Zoomed to OC (Oceania continent)
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
║             CLOUD LAYER                  ║
║        Location: OC-AU-SYD               ║
╠══════════════════════════════════════════╣
║                                          ║
║                    @                     ║
║                                          ║
╚══════════════════════════════════════════╝
@ = You (Sydney, Australia)
```

---

## Future Enhancements

### Planned Features

1. **Sublayer Maps**
   - District-level maps for major cities
   - Custom tile art for each district
   - Points of interest within tiles

2. **Procedural Dungeon Generation**
   - Random dungeon layouts per tile
   - Treasure placement based on TILE hash
   - Monster encounters tied to location

3. **Waypoint System**
   - Save named TILE locations
   - Quick travel between waypoints
   - Breadcrumb trail history

4. **Mini-Map in Prompt**
   - Small ASCII map in prompt line
   - Real-time TILE indicator
   - Nearby tile preview

5. **Location-Based Events**
   - Timezone-aware greetings
   - Weather integration by TILE
   - Local time display

6. **Multi-User Shared Maps**
   - Collaborative exploration
   - Shared TILE discoveries
   - Message system at tiles

7. **Advanced TILE Features**
   - Custom tiles (user-created districts)
   - Tile ownership and claiming
   - Tile metadata and notes

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

- Lazy loading of tile sublayers
- Visited tiles tracked efficiently in hash map
- Location data loaded once at startup from `core/data/locations.json`
- TILE codes stored as strings (minimal memory)
- Coordinate conversion only when needed for display

### Data Persistence

- Current TILE saved to `sandbox/user/USER.UDT`
- Layer history tracked per session
- Visited tiles list maintained
- Move count integrated with session tracking
- No coordinate storage required

### Extensibility

The system is designed to be extended:
- New tiles easily added to hierarchy
- Custom sublayer definitions supported
- Plugin architecture for tile behaviors
- Event hooks for tile transitions
- Modular TILE encoding/decoding

### TILE Code Benefits

1. **Compact Storage**: "AS-JP-TYO" vs "35.6762, 139.6503"
2. **Human Readable**: Clear geographic hierarchy
3. **Hierarchical**: Easy parent/child navigation
4. **Decodable**: Convert to coordinates when needed
5. **Extensible**: Add new tiles without schema changes

---

## Troubleshooting

### Common Issues

**Q: "Unknown timezone" error at startup**
A: Your timezone may not be mapped. Check `core/data/locations.json` or manually set location with `MAP LOCATE <city>`

**Q: "Invalid TILE code" when using MAP GOTO**
A: TILE codes must follow format: CONTINENT-COUNTRY-CITY[-DISTRICT[-BLOCK]]
Examples: AS-JP-TYO, EU-UK-LON-W1, NA-US-NYC-M3-17

**Q: "No sublayer available" when zooming in**
A: Not all tiles have district/block sublayers defined yet. Stick to city-level tiles or create custom sublayers.

**Q: Map position not saved**
A: Ensure `sandbox/user/USER.UDT` is writable. Check permissions.

**Q: TILE code doesn't match real location**
A: TILE codes are approximations based on major cities. Use `MAP GOTO` to set precise custom tiles.

---

## Credits

- Inspired by NetHack dungeon navigation (DevTeam)
- TILE code system design: Fred Porter
- Timezone detection: Python `pytz` library
- City coordinates: GeoNames database
- Teletext rendering: World Space Television standard

---

## Version History

**v2.0.0 (2024-11-26)**
- Replaced lat/long with hierarchical TILE code system
- Simplified TIZO to timezone-based detection only
- Consolidated location data to single `locations.json`
- Updated all wiki documentation
- Reduced core/data complexity by 60%

**v1.0.4 (2024-11-02)**
- Teletext mosaic rendering
- Web extension interface
- 64 block art characters

**v1.0.3 (2024-10-30)**
- Initial multi-layer system
- TIZO city network (20 cities)
- Enhanced navigation commands
- NetHack-style layer transitions

**v1.0.0 (2024-10-30)**
- Basic grid system
- Simple navigation
- First-time setup integration


### 16×16 Pixel uCELL Layout

The uDOS Grid System provides a standardized layout framework based on 16×16 pixel base units (uCELLs) for consistent terminal and web interfaces.

**Grid Specification:**
- **Size**: 480 columns × 270 rows = 129,600 cells
- **Column Format**: 2-letter codes (AA-RL) - Excel-style progression
- **Cell Format**: `{2-LETTER}{ROW}` (e.g., AA340, AB320, AM240)
- **Examples**: AA340 (Sydney), AB320 (Tokyo), AM240 (London)

#### uCELL Specification

```
┌────────────────┐ 16px total
│ ░░░░░░░░░░░░░░ │
│ ░████████████░ │ ← 2px buffer
│ ░█  CONTENT █░ │ ← 12×12 content area
│ ░████████████░ │
│ ░░░░░░░░░░░░░░ │
└────────────────┘
```

**Dimensions:**
- **Total Size**: 16×16 pixels
- **Buffer**: 2px border around content
- **Content Area**: 12×12 pixels
- **Font**: Monaspace at 12px
- **Line Height**: 16px
- **Baseline**: Row 9 of 16

#### Grid Sizes

| Size | Grid | Device | Use |
|------|------|--------|-----|
| Wearable | 16×16 | Watch | Single widget |
| Mobile | 40×16 | Phone | Compact interface |
| Terminal | 80×30 | Desktop | Standard CLI |
| Dashboard | 120×48 | Large | Multi-panel |

#### Text Block Characters

**Block Fills:**
- `░` (25% fill) - Light shade
- `▒` (50% fill) - Medium shade
- `▓` (75% fill) - Dark shade
- `█` (100% fill) - Solid block

**Box Drawing:**
```
┌─────────────────┐
│  Header Text    │
├─────────────────┤
│  Content Area   │
└─────────────────┘
```

**Characters:**
- Lines: `─ │`
- Corners: `┌ ┐ └ ┘`
- Joins: `├ ┤ ┬ ┴ ┼`

**Arrows (8-directional):**
`← → ↑ ↓ ↖ ↗ ↘ ↙`

**Symbols:**
- `✓` Check (success)
- `✗` Cross (error)
- `•` Bullet
- `●` Circle
- `■` Square
- `◆` Diamond

#### Coordinate System

Zero-indexed positioning (x, y):

```
     0   1   2   3
   ┌───┬───┬───┬───┐
0  │0,0│1,0│2,0│3,0│
   ├───┼───┼───┼───┤
1  │0,1│1,1│2,1│3,1│
   └───┴───┴───┴───┘
```

#### CSS Variables

```css
:root {
    /* uCELL Dimensions */
    --ucell-size: 16px;
    --ucell-buffer: 2px;
    --ucell-content: 12px;

    /* Text Block Characters */
    --char-block-25: '░';
    --char-block-50: '▒';
    --char-block-75: '▓';
    --char-block-full: '█';

    /* Line Drawing */
    --char-h-line: '─';
    --char-v-line: '│';
    --char-tl-corner: '┌';
    /* etc */
}
```

#### Responsive Scaling

The grid automatically scales on smaller screens:

- **Desktop**: 16px cells
- **Tablet**: 12px cells
- **Mobile**: 10px cells

#### Integration in Web Extensions

```html
<!-- Include uGrid stylesheet -->
<link rel="stylesheet" href="../shared/udos-grid.css">

<!-- Basic uCELL -->
<div class="ucell ucell-buffer">A</div>

<!-- Header Bar -->
<div class="ugrid-header">
    🚀 uDOS v1.0.0 Terminal
</div>

<!-- Menu Grid (2×3) -->
<div class="ugrid-menu">
    <div class="ugrid-menu-item">FILE</div>
    <div class="ugrid-menu-item">EDIT</div>
    <div class="ugrid-menu-item">VIEW</div>
    <div class="ugrid-menu-item">TOOLS</div>
    <div class="ugrid-menu-item">HELP</div>
    <div class="ugrid-menu-item">EXIT</div>
</div>

<!-- Status Display -->
<div class="ugrid-status">
    <span>Status: <span class="color-green">✓ Active</span></span>
    <span>User: <span class="color-cyan">Admin</span></span>
</div>
```

#### Pre-built Components

**ASCII Box:**
```html
<div class="ascii-box">
┌─────────────────────────┐
│   Box Title             │
├─────────────────────────┤
│   Content line 1        │
│   Content line 2        │
└─────────────────────────┘
</div>
```

**Progress Bar:**
```html
<div class="block-progress">
    <span class="block-progress-fill">████████</span>
    <span class="block-progress-empty">░░</span>
</div>
```

**uCELL Indicators:**
```html
<span class="ucell-indicator online"></span>  <!-- ● green -->
<span class="ucell-indicator offline"></span> <!-- ○ gray -->
<span class="ucell-indicator warning"></span> <!-- ⚠ yellow -->
<span class="ucell-indicator error"></span>   <!-- ✗ red -->
```

#### Best Practices

1. **Consistent Spacing**: Always use 16×16 cell multiples
2. **Buffer Space**: Leave 2px buffer for readability
3. **Monospace Font**: Use Monaspace for exact character spacing
4. **Color Contrast**: Follow Synthwave DOS palette for accessibility
5. **Grid Alignment**: Align elements to grid boundaries

---

## Version History

**v1.0 (2025-10-30)**
- Initial multi-layer system
- 8 default layers
- 10 major cities
- Real-world integration
- NetHack-style navigation
- First-time setup integration
