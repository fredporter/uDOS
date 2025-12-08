# uDOS Mapping System (v1.2.x)

**Version:** v1.2.15 (December 2025)

The uDOS Mapping System provides a unified grid-based navigation framework using **TILE codes** with strict 2-letter column notation and optional layer suffixes. The system supports multi-layer visualization and hierarchical navigation without lat/long coordinates.

---

## Table of Contents

1. [TILE Code Format](#tile-code-format)
2. [Grid Structure](#grid-structure)
3. [Layer System](#layer-system)
4. [Location Detection](#location-detection)
5. [Commands](#commands)
6. [Examples](#examples)

---

## TILE Code Format

**Strict Format:** `[COLUMN][ROW][-LAYER]`

### Components

1. **COLUMN**: 2-letter code (AA-RL)
   - Represents 0-479 horizontal positions
   - Always 2 letters (AA, AB, AC, ..., RL)
   - Base-26 encoding

2. **ROW**: Numeric code (0-269)
   - Represents vertical positions
   - No zero-padding required

3. **LAYER**: Optional suffix (100-500)
   - World layer: 100 (~83km/cell)
   - Region layer: 200 (~2.78km/cell)
   - City layer: 300 (~93m/cell)
   - District layer: 400 (~3m/cell)
   - Block layer: 500 (~10cm/cell)

### Valid Examples

```
AA340           # Sydney grid position (layer unspecified)
AA340-100       # Sydney at world layer (~83km/cell)
JF57            # London grid position
JF57-300        # London at city layer (~93m/cell)
BZ42-200        # Custom position at region layer
```

### Invalid Formats (Deprecated)

```
❌ AS-JP-TYO         # Old hierarchical format (removed v1.1.12)
❌ [-33.87, 151.21]  # Lat/long coordinates (deprecated)
❌ A340              # Single-letter column (must be 2 letters)
❌ AA340-50          # Invalid layer (must be 100/200/300/400/500)
```

---

## Grid Structure

### Grid Dimensions

**Total Coverage:** 480 columns × 270 rows = 129,600 cells

**Column Encoding (AA-RL):**
- AA = 0, AB = 1, AC = 2, ..., AZ = 25
- BA = 26, BB = 27, ..., BZ = 51
- ...
- RA = 442, RB = 443, ..., RL = 479

**Row Range:** 0-269 (standard decimal)

### Major Cities

| City | TILE Code | Layer 100 | Population |
|------|-----------|-----------|------------|
| Sydney | AA340-100 | World | 5.3M |
| London | JF57-100 | World | 9.0M |
| Tokyo | QR68-100 | World | 14.0M |
| New York | KL82-100 | World | 8.3M |
| Paris | JC52-100 | World | 2.2M |

---

## Layer System

### Layer Hierarchy (100-899)

The uDOS layer system uses a comprehensive 100-899 numbering scheme aligned with teletext page numbers:

#### Earth Physical Layers (100-599)
| Layer | Name | Cell Size | Use Case |
|-------|------|-----------|----------|
| 100-199 | World/Continent | ~83 km | Continental navigation, countries |
| 200-299 | Region/Country | ~2.78 km | Regional planning, states/provinces |
| 300-399 | City/District | ~93 m | Urban navigation, neighborhoods |
| 400-499 | Block/Street | ~3 m | Building layout, precise locations |
| 500-599 | Building/Room | ~10 cm | Interior mapping, detailed work |

#### Virtual/Play Layers (600-799)
| Layer | Name | Type | Use Case |
|-------|------|------|----------|
| 600-699 | Cloud Layer | Virtual | Cloud computing metaphor, data layers |
| 700-799 | Satellite Layer | Virtual | Orbital perspective, global systems |

#### Space/Planetary Layers (800-899)
| Layer | Name | Type | Use Case |
|-------|------|------|----------|
| 800-849 | Space/Solar | Virtual | Solar system navigation, planets |
| 850-899 | Galaxy | Virtual | Galactic perspective, universe data |

### Layer Navigation

**Zoom In (Physical Earth):** Increase layer number
```
AA340-100 → AA340-200 → AA340-300 → AA340-400 → AA340-500
```

**Zoom Out (Physical Earth):** Decrease layer number
```
AA340-500 → AA340-400 → AA340-300 → AA340-200 → AA340-100
```

**Ascend (Virtual/Space):** Move to higher layers
```
AA340-100 → AA340-600 (Cloud) → AA340-700 (Satellite) → AA340-800 (Space)
```

**Pan (Same Layer):** Change column/row
```
AA340-300 → AB340-300 (east)
AA340-300 → AA341-300 (north)
```

---

## Location Detection

### Timezone-Based Detection

On first run, uDOS detects location via system timezone:

```
AEST (Australia/Sydney) → AA340-100
GMT (Europe/London) → JF57-100
JST (Asia/Tokyo) → QR68-100
EST (America/New_York) → KL82-100
```

### Manual Override

Set custom location:
```
CONFIG SET location AA340-100
MAP CENTER JF57-300
```

---

## Commands

### MAP Command

**View current location:**
```
MAP
```

**Center on TILE:**
```
MAP CENTER AA340-100
MAP CENTER JF57-300
```

**Change layer:**
```
MAP LAYER 200      # Region layer (Earth)
MAP LAYER 600      # Cloud layer (Virtual)
MAP LAYER 800      # Space layer (Planets/Galaxy)
MAP ZOOM IN        # Increase layer number (zoom in)
MAP ZOOM OUT       # Decrease layer number (zoom out)
MAP ASCEND         # Move to virtual/space layers
MAP DESCEND        # Return to physical Earth layers
```

### STATUS Command

**Show current position:**
```
STATUS location
```

Output:
```
Location: AA340-100 (Sydney, World Layer)
Grid: Column AA, Row 340
Layer: 100 (~83km/cell)
```

### MESH Commands (Layer 600-619)

**View mesh network devices:**
```
MESH DEVICES              # List all devices in mesh network
MESH INFO <tile>          # Show devices at specific TILE
MESH INFO AA340-300-D1    # Device details and status
```

**Network visualization:**
```
MESH HEATMAP              # Signal coverage grid visualization
MESH ROUTE <target>       # Show routing path to target device
MESH TOPOLOGY             # Display network graph as text grid
```

**Output Example (MESH INFO):**
```
🌐 Device: AA340-300-D1
━━━━━━━━━━━━━━━━━━━━━━━━
Status: ● Online
Signal: ████████░░ 82%
Type: uDOS Lite Node
Firmware: v1.2.4
Connections: 3 peers
Uptime: 4d 12h 33m
```

**Output Example (MESH HEATMAP - Text Grid):**
```
     AA   AB   AC   AD   AE
340  ████ ███░ ██░░ █░░░ ░░░░  Signal
341  ███░ ████ ███░ ██░░ █░░░  Strength
342  ██░░ ███░ ████ ███░ ██░░  Grid
343  █░░░ ██░░ ███░ ████ ███░
344  ░░░░ █░░░ ██░░ ███░ ████

Devices: ⊚=D1 ⊕=D2 ⊗=D3
```

### SCREWDRIVER Commands (Layer 650)

**Device management:**
```
SCREWDRIVER INFO <device>           # Device status and firmware version
SCREWDRIVER WHITELIST LIST          # Show whitelisted devices
SCREWDRIVER WHITELIST ADD <device>  # Add device to whitelist
```

**Firmware operations:**
```
SCREWDRIVER FLASH <device> <flashpack>  # Flash firmware (whitelisted only)
SCREWDRIVER ROLLBACK <device>           # Revert to previous firmware
SCREWDRIVER VERIFY <device>             # Check firmware signature
```

**Output Example (SCREWDRIVER INFO):**
```
🔧 Sonic Screwdriver
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Device: AA340-300-D1
Whitelisted: ✓ Yes
Current FW: v1.2.4 (Bank A)
Previous FW: v1.2.3 (Bank B)
Signature: ✓ Valid (Ed25519)
Health: ✓ All checks passed
Flash Slots: 2/2 available
```

---

## Examples

### Example 1: Sydney to London

```
# Start at Sydney
MAP CENTER AA340-100

# Zoom to city layer
MAP LAYER 300

# Pan to London
MAP CENTER JF57-300

# Zoom to district
MAP LAYER 400
```

### Example 2: Location Queries

```
# Where am I?
STATUS location
→ Location: AA340-100 (Sydney, World Layer)

# What's at this TILE?
MAP INFO JF57-100
→ London, United Kingdom
→ Population: 9.0M
→ Layer: 100 (World, ~83km/cell)

# Change default location
CONFIG SET location JF57-300
```

### Example 3: Layer Navigation (Full Range)

```
# Start at world layer
MAP CENTER AA340-100

# Zoom in progressively (Physical Earth)
MAP LAYER 200  # Region (~2.78km/cell)
MAP LAYER 300  # City (~93m/cell)
MAP LAYER 400  # District (~3m/cell)
MAP LAYER 500  # Building (~10cm/cell)

# Ascend to virtual layers
MAP LAYER 600  # MeshCore layer (device networking)
MAP LAYER 650  # Sonic Screwdriver (firmware provisioning)
MAP LAYER 700  # Satellite layer (orbital view)
MAP LAYER 800  # Space layer (solar system)
MAP LAYER 850  # Galaxy layer (Milky Way perspective)

# Return to physical world
MAP LAYER 100  # Back to world layer
```

### Example 4: MeshCore Device Grid

```
# Navigate to city layer
MAP CENTER AA340-300

# Switch to MeshCore layer
MAP LAYER 600

# View devices in current area
MESH DEVICES
→ Found 5 devices in AA340-300:
  ⊚ D1 - uDOS Lite Node (online)
  ⊕ D2 - Sensor Array (online)
  ⊗ D3 - Gateway (online)
  ⊙ D4 - Repeater (offline)
  ⊘ D5 - End Device (online)

# Display signal coverage
MESH HEATMAP
→ [Text grid showing signal strength]

# Find route to specific device
MESH ROUTE AA340-300-D5
→ Path: D1 → D3 → D5 (2 hops, 156ms)
```

### Example 5: Firmware Provisioning

```
# Switch to Sonic Screwdriver layer
MAP LAYER 650

# Check device status
SCREWDRIVER INFO AA340-300-D1
→ Device whitelisted, firmware v1.2.3, healthy

# Flash new firmware
SCREWDRIVER FLASH AA340-300-D1 udos-lite-v1.2.4.fp
→ Verifying signature... ✓
→ Flashing to Bank B... ████████████ 100%
→ Validating... ✓
→ Switching to Bank B... ✓
→ Health check... ✓ All passed
→ Firmware updated successfully!

# If something goes wrong
SCREWDRIVER ROLLBACK AA340-300-D1
→ Rolling back to Bank A (v1.2.3)... ✓
```

Coordinates are stored in `locations.json` for reference, but all user locations are stored as TILE codes.

---

## Text Grid Rendering (Layers 600-650)

### Grid Display Format

Layers 600-650 use **text-based grid rendering** as the foundation for all visualizations:

**12-Character Column System:**
```
+------------ +------------ +------------ +------------+
| AA340       | AB340       | AC340       | AD340       |
| ⊚D1 ⊕D2     | ░░░░        | ⊗D3         | ████        |
| 82% 76%     |             | 91%         | Signal      |
+------------ +------------ +------------ +------------+
```

**Viewport Tiers:**
- **Compact (40 cols)**: 3 columns × 12 chars + gutters = 38 chars
- **Standard (80 cols)**: 6 columns × 12 chars + gutters = 77 chars
- **Wide (120 cols)**: 9 columns × 12 chars + gutters = 116 chars
- **Ultra (160 cols)**: 12 columns × 12 chars + gutters = 155 chars

**Text Symbols:**
- Devices: ⊚ ⊕ ⊗ ⊙ ⊘ (5 device types)
- Signal: █ (100%) ▓ (75%) ▒ (50%) ░ (25%)
- Status: ● (online) ○ (offline) ◐ (connecting) ◑ (error)
- Routes: ─ │ ┌ ┐ └ ┘ ├ ┤ (path drawing)

**Grid Cell Format:**
```
TILE+DEVICE
AA340-600-D1  (TILE AA340, Layer 600, Device D1)
JF57-650      (TILE JF57, Layer 650, no device specified)
```

### MeshCore Layer Rendering (600-619)

**Network Topology Grid:**
```
       AA    AB    AC    AD    AE    AF
 340   ⊚D1───⊕D2   ░░░   ⊗D3   ░░░   ░░░
       │     │           │
 341   ⊙D4───┘     ░░░   └───⊘D5   ░░░
       │                     │
 342   └─────────────────────┘     ░░░

Legend: ⊚=Node ⊕=Gateway ⊗=Sensor ⊙=Repeater ⊘=End
```

**Signal Strength Heatmap:**
```
       AA    AB    AC    AD    AE    AF
 340   ████  ███░  ██░░  █░░░  ░░░░  ░░░░  100%-0%
 341   ███░  ████  ███░  ██░░  █░░░  ░░░░  Signal
 342   ██░░  ███░  ████  ███░  ██░░  █░░░  Coverage
 343   █░░░  ██░░  ███░  ████  ███░  ██░░  Grid
```

**Device Status Dashboard:**
```
┌─────────────────────────────────────┐
│ MeshCore Network - Layer 600        │
├─────────────────────────────────────┤
│ TILE: AA340-300                     │
│ Devices: 5 online, 1 offline        │
│ Coverage: 87% of area               │
│ Latency: 12ms avg                   │
├─────────────────────────────────────┤
│ ⊚ D1  Online   82% ████████░░       │
│ ⊕ D2  Online   76% ███████░░░       │
│ ⊗ D3  Online   91% █████████░       │
│ ⊙ D4  Offline   0% ░░░░░░░░░░       │
│ ⊘ D5  Online   68% ██████░░░░       │
└─────────────────────────────────────┘
```

### Sonic Screwdriver Layer Rendering (650)

**Firmware Status Grid:**
```
       AA340      AB340      AC340
 D1    ✓v1.2.4    ░░░░░░     ░░░░░░
       Bank A     ------     ------
       
 D2    ⚠v1.2.3    ✓v1.2.4    ░░░░░░
       Bank B     Bank A     ------
       
 D3    ✗v1.2.2    ⚠v1.2.3    ✓v1.2.4
       Rollback   Bank B     Bank A

Legend: ✓=Current ⚠=Previous ✗=Outdated
```

**Flash Progress Indicator:**
```
🔧 Flashing AA340-300-D1
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Verifying signature...    [████████████] ✓
Erasing Bank B...         [████████████] ✓
Writing firmware...       [████████░░░░] 76%
Progress: 3/5 steps       Elapsed: 8.2s
```

## Architecture

### Core Components

1. **MapEngine** (`core/services/map_engine.py`)
   - TILE code grid management
   - Multi-layer map coordination
   - Hierarchical zoom system
   - Position tracking and navigation
   - **Text grid rendering for layers 600-650**

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

## Layer System Details

### Layer Ranges and Types

#### Physical Earth Layers (100-599)
Represent real-world geography at different scales:
- **100-199**: World/Continent scale (~83km per cell)
  - Major continents, countries, oceans
  - Long-distance navigation and travel planning
- **200-299**: Region/Country scale (~2.78km per cell)
  - States, provinces, large cities
  - Regional planning and exploration
- **300-399**: City/District scale (~93m per cell)
  - Neighborhoods, districts, landmarks
  - Urban navigation and city exploration
- **400-499**: Block/Street scale (~3m per cell)
  - Buildings, streets, precise locations
  - Detailed navigation and mapping
- **500-599**: Building/Room scale (~10cm per cell)
  - Interior spaces, detailed work areas
  - Precision mapping and layout

#### Virtual/Play Layers (600-799)
Abstract data and gameplay layers:
- **600-609**: MeshCore Layer (Virtual)
  - Device-level mesh networking overlay
  - Network topology visualization (nodes, edges, routes)
  - Device clustering within TILE cells
  - Signal strength heatmaps and coverage maps
  - Text grid format: Device markers (D1, D2) at TILE positions
  - TILE+Device format: AA340-300-D1, JF57-100-D2
- **610-619**: Device Layer (Virtual)
  - Per-device overlays and status visualization
  - Individual device state tracking
  - Connection quality indicators
  - Device-specific metadata display
- **620-629**: AI Layer (Virtual)
  - Simulation grids and agent visualization
  - Automata state rendering
  - AI agent pathfinding displays
- **650**: Sonic Screwdriver Layer (Virtual)
  - Firmware provisioning interface
  - Device flashing status grid
  - Recovery mode indicators
  - Whitelist management visualization
- **680-689**: Cloud Compute Layer (Virtual)
  - Cloud computing metaphor
  - Data storage and processing visualization
  - Virtual environment mapping
- **690-699**: VR/AR Layer (Virtual)
  - Mixed-reality projection overlay
  - In-world spatial anchors
- **700-799**: Satellite Layer (Virtual)
  - Orbital perspective and global systems
  - Communication networks
  - Earth observation and monitoring

#### Space/Planetary Layers (800-899)
Celestial and galactic navigation:
- **800-849**: Space/Solar System
  - Solar system navigation (Sol)
  - Planets: Earth, Mars, Jupiter, etc.
  - Workspace metaphor (different planets = different projects)
- **850-899**: Galaxy/Universe
  - Milky Way galactic perspective
  - Deep space visualization
  - Universe-scale data organization

### Layer Properties

Each layer includes:
- **Number**: Layer identifier (100-899)
- **Name**: Human-readable layer name
- **Type**: PHYSICAL, VIRTUAL, or SPACE
- **Resolution**: Cell size at this layer
- **Grid**: Dictionary of TILE codes → cell data
- **Metadata**:
  - Created timestamp
  - Description
  - Accessibility (OPEN, LOCKED, DISCOVERED, HIDDEN)
  - Parent/child layer connections
  - Zoom level (1-9 for hundreds digit)

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
