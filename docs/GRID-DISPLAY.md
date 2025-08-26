# uGRID Display System

```
██████╗ ██╗███████╗██████╗ ██╗      █████╗ ██╗   ██╗
██╔══██╗██║██╔════╝██╔══██╗██║     ██╔══██╗╚██╗ ██╔╝
██║  ██║██║███████╗██████╔╝██║     ███████║ ╚████╔╝
██║  ██║██║╚════██║██╔═══╝ ██║     ██╔══██║  ╚██╔╝
██████╔╝██║███████║██║     ███████╗██║  ██║   ██║
╚═════╝ ╚═╝╚══════╝╚═╝     ╚══════╝╚═╝  ╚═╝   ╚═╝
```

*Universal Device Operating System*

## Tile-Based Grid Architecture

The **uGRID** system is uDOS's comprehensive tile-based display architecture capable of running screens, widgets, and interactive applications across multiple device classes. Built on 16×16 **uCELLs** with 4× resolution enhancement and advanced **uMAP** location mapping.

---

## 1) uGRID System Overview

### Core Architecture
- **uCELL**: Base 16×16 pixel square tile unit
- **uTILE**: Logical display element containing content (text, graphics, widgets)
- **uMAP**: Coordinate system for tile location mapping and navigation
- **4× Resolution**: Enhanced 64×64 effective detail within each uCELL
- **Screen Management**: Multiple screen contexts with widget overlay support

### System Capabilities
- **Screen Rendering**: Full-screen applications and dashboards
- **Widget System**: Modular components that can be positioned anywhere on grid
- **Multi-Resolution**: Seamless scaling from wearable (16×16) to wallboard (160×60)
- **Real-time Updates**: Dynamic content refresh with minimal system overhead
- **Cross-Platform**: Consistent display across terminal, web, and native applications

---

## 2) uCELL Specifications

### Base uCELL (16×16)
```
┌────────────────┐ 16px width
│ ░░░░░░░░░░░░░░ │
│ ░████████████░ │ ← 2px buffer (optional)
│ ░█          █░ │ ← 12×12 content area
│ ░█    TEXT  █░ │ ← baseline row 9
│ ░█          █░ │
│ ░████████████░ │
│ ░░░░░░░░░░░░░░ │
└────────────────┘ 16px height
```

### Text Box Configurations
- **12×12**: Default content area (2px buffer)
- **14×14**: Compact spacing (1px buffer)
- **10×10**: Extended spacing (3px buffer)
- **16×16**: Edge-to-edge (no buffer) for block graphics

### uCELL States
- **Active**: Currently focused/selected tile
- **Inactive**: Background tile
- **Disabled**: Non-interactive tile
- **Hidden**: Tile present but not rendered
- **Overlay**: Transparent tile with content over background

---

## 3) 4× Resolution System

### Enhanced Detail Grid (64×64 effective)
Each 16×16 uCELL can be subdivided into a **4×4 overlay grid** providing 64×64 effective resolution for high-detail graphics, icons, and micro-widgets.

```
uCELL 16×16 base     →     4×4 overlay grid (64×64 effective)
┌────────────────┐          ┌─┬─┬─┬─┬─┬─┬─┬─┬─┬─┬─┬─┬─┬─┬─┬─┐
│                │          │ │ │ │ │ │ │ │ │ │ │ │ │ │ │ │ │
│                │          ├─┼─┼─┼─┼─┼─┼─┼─┼─┼─┼─┼─┼─┼─┼─┼─┤
│                │    →     │ │ │ │ │ │ │ │ │ │ │ │ │ │ │ │ │
│                │          ├─┼─┼─┼─┼─┼─┼─┼─┼─┼─┼─┼─┼─┼─┼─┼─┤
└────────────────┘          │ │ │ │ │ │ │ │ │ │ │ │ │ │ │ │ │
                             └─┴─┴─┴─┴─┴─┴─┴─┴─┴─┴─┴─┴─┴─┴─┴─┘
```

### 4× Resolution Applications
- **Icons**: Crisp 64×64 iconography
- **Micro-widgets**: Small interactive elements
- **Dithering**: Smooth gradients and anti-aliasing
- **Detail overlays**: Status indicators, badges, notifications
- **Vector approximation**: Smooth curves using sub-pixel positioning

### Example: 4× Resolution Heart Icon
```
....████....████....
..████████████████..
.██████████████████.
.██████████████████.
..████████████████..
...██████████████...
....████████████....
.....██████████.....
......████████......
.......██████.......
........████........
.........██.........
```

---

## 4) uMAP Location System

### Coordinate System
uMAP uses a **zero-indexed coordinate system** for precise tile positioning and navigation.

```
Grid Layout (8×6 example):
     0   1   2   3   4   5   6   7
   ┌───┬───┬───┬───┬───┬───┬───┬───┐
0  │0,0│1,0│2,0│3,0│4,0│5,0│6,0│7,0│
   ├───┼───┼───┼───┼───┼───┼───┼───┤
1  │0,1│1,1│2,1│3,1│4,1│5,1│6,1│7,1│
   ├───┼───┼───┼───┼───┼───┼───┼───┤
2  │0,2│1,2│2,2│3,2│4,2│5,2│6,2│7,2│
   ├───┼───┼───┼───┼───┼───┼───┼───┤
3  │0,3│1,3│2,3│3,3│4,3│5,3│6,3│7,3│
   ├───┼───┼───┼───┼───┼───┼───┼───┤
4  │0,4│1,4│2,4│3,4│4,4│5,4│6,4│7,4│
   ├───┼───┼───┼───┼───┼───┼───┼───┤
5  │0,5│1,5│2,5│3,5│4,5│5,5│6,5│7,5│
   └───┴───┴───┴───┴───┴───┴───┴───┘
```

### uMAP Address Format
- **Standard**: `X,Y` (e.g., `3,2` for column 3, row 2)
- **Extended**: `X,Y:W×H` (e.g., `3,2:2×1` for 2-wide, 1-tall area)
- **Named**: `@REGION_NAME` (e.g., `@HEADER`, `@SIDEBAR`, `@MAIN`)
- **Relative**: `+X,+Y` (e.g., `+1,+0` for one cell right)

### uMAP Regions
```
┌─────────────────────────────────────┐
│              @HEADER                │ ← 0,0:8×1
├─────────┬───────────────────────────┤
│@SIDEBAR │         @MAIN             │ ← 0,1:2×4 | 2,1:6×4
│         │                           │
│         │                           │
│         │                           │
├─────────┴───────────────────────────┤
│              @FOOTER                │ ← 0,5:8×1
└─────────────────────────────────────┘
```

### uMAP Navigation Commands
- `uGRID.goto(3,2)` - Move cursor to coordinate
- `uGRID.select(3,2:2×1)` - Select area
- `uGRID.focus(@MAIN)` - Focus named region
- `uGRID.navigate(+1,+0)` - Relative movement

---

## 5) uTILE Location Mapping

### Tile Addressing System
Each uTILE has multiple addressing methods for flexible access:

```
Physical Grid Position: [X,Y]
Logical ID: TILE_ID_XXXXXXXX  (8-char hex)
Named Reference: @TILE_NAME
Screen Context: SCREEN:TILE_PATH
```

### Tile Hierarchy
```
SCREEN_01
├── @HEADER
│   ├── TILE_A1B2C3D4 (Logo)
│   ├── TILE_E5F6G7H8 (Title)
│   └── TILE_I9J0K1L2 (Menu)
├── @MAIN
│   ├── WIDGET_M3N4O5P6 (Content)
│   ├── WIDGET_Q7R8S9T0 (Sidebar)
│   └── OVERLAY_U1V2W3X4 (Modal)
└── @FOOTER
    ├── TILE_Y5Z6A7B8 (Status)
    └── TILE_C9D0E1F2 (Controls)
```

### Location Mapping Functions
```bash
# Get tile at position
uGRID.getTile(3,2)          → TILE_A1B2C3D4

# Get position of tile
uGRID.getPosition(@LOGO)    → 0,0

# List tiles in region
uGRID.listTiles(@MAIN)      → [WIDGET_M3N4O5P6, WIDGET_Q7R8S9T0]

# Get tile neighbors
uGRID.getNeighbors(3,2)     → {N: 3,1, S: 3,3, E: 4,2, W: 2,2}
```

---

## 6) Core Display Sizes & Device Classes

| Grid (cols×rows) | Effective px | Device Class        | uMAP Regions | Typical Use        |
| ---------------- | ------------ | ------------------- | ------------ | ------------------ |
| 160×60           | 2560×960     | Wallboard           | 20+          | Control rooms      |
| 120×48           | 1920×768     | Large Dashboard     | 15+          | Management console |
| 80×30            | 1280×480     | Standard Terminal   | 8-12         | Development UI     |
| 64×24            | 1024×384     | Small Screen        | 6-8          | Compact terminal   |
| 48×20            | 768×320      | Tablet              | 4-6          | Touch interface    |
| 40×16            | 640×256      | Mobile              | 3-4          | Phone apps         |
| 32×24            | 512×384      | Compact 4:3         | 3-4          | Embedded systems   |
| 16×16            | 256×256      | Wearable            | 1-2          | Watch/IoT display  |

### Responsive Grid Behavior
```
Wallboard (160×60)    →  Full multi-panel dashboard
Dashboard (120×48)    →  Primary + secondary panels
Terminal (80×30)      →  Header + main + footer
Small (64×24)         →  Compact layout
Mobile (40×16)        →  Single column, stacked
Wearable (16×16)      →  Single widget focus
```

---

## 7) Widget System Architecture

### Widget Types
- **Static**: Fixed content tiles (text, images, blocks)
- **Interactive**: User input elements (buttons, forms, menus)
- **Dynamic**: Real-time updating content (clocks, charts, feeds)
- **Composite**: Multi-tile spanning widgets
- **Overlay**: Floating widgets over background content

### Widget Positioning
```
# Absolute positioning
widget.position = {x: 3, y: 2, width: 2, height: 1}

# Region-based positioning
widget.region = "@MAIN"
widget.anchor = "center"

# Flow positioning
widget.flow = "after:WIDGET_A1B2C3D4"
widget.wrap = true
```

### Widget Lifecycle
1. **Define**: Widget specification and properties
2. **Place**: Position assignment in uMAP
3. **Render**: Content generation and display
4. **Update**: Real-time content refresh
5. **Remove**: Cleanup and position release

---

## 8) Screen Management

### Screen Contexts
Each **Screen** is a complete uGRID layout that can be switched between:

```
SCREEN_DASHBOARD    → Main operational view
SCREEN_SETTINGS     → Configuration interface
SCREEN_MONITOR      → System status display
SCREEN_DEBUG        → Development tools
```

### Screen Transitions
- **Instant**: Immediate switch between screens
- **Slide**: Directional transition animation
- **Fade**: Cross-fade between screen contents
- **Overlay**: Modal screen over background

### Multi-Screen Support
```bash
# Screen management
uGRID.screen.create("DASHBOARD")
uGRID.screen.switch("SETTINGS")
uGRID.screen.overlay("MODAL_DIALOG")
uGRID.screen.split("LEFT:MAIN", "RIGHT:MONITOR")
```

---

## 9) Block Graphics & Visual Elements

### Unicode Block Set
- **░ ▒ ▓ █** - Density gradients (25%, 50%, 75%, 100%)
- **▀ ▄ ▌ ▐** - Half blocks (top, bottom, left, right)
- **▘ ▝ ▖ ▗** - Quarter blocks (corners)
- **┌ ┐ └ ┘** - Box drawing corners
- **─ │ ┬ ┴ ┤ ├ ┼** - Box drawing lines and junctions

### Layer System (L/D/C/T)
```
LAYER_LIGHT       → High contrast, light background
LAYER_DARK        → High contrast, dark background
LAYER_COLOUR      → Themed color palette
LAYER_TRANSPARENT → See-through overlays
```

### Block Tile Examples
```
Solid Fill:          Gradient Fill:       Border Box:
█████████████        ░░▒▒▓▓███▓▓▒▒░░       ┌───────────┐
█████████████        ░░▒▒▓▓███▓▓▒▒░░       │           │
█████████████        ░░▒▒▓▓███▓▓▒▒░░       │   CONTENT │
█████████████        ░░▒▒▓▓███▓▓▒▒░░       │           │
█████████████        ░░▒▒▓▓███▓▓▒▒░░       └───────────┘
```

---

## 10) Font & Typography System

### uGRID Font Stack
- **Primary**: MODE7GX0.TTF (authentic teletext aesthetics)
- **Secondary**: Pixel Operator (clean pixel font)
- **Fallback**: GNU Unifont (comprehensive Unicode)
- **System**: Platform-specific monospace (Menlo, Consolas, etc.)

### Text Positioning Rules
- **Baseline**: Row 9 of 16 in uCELL
- **Centering**: Horizontal and vertical within text box
- **Sizing**: 10×10, 12×12, or 14×14 text box variants
- **Alignment**: Left, center, right within text box boundaries

### Typography Examples
```
┌────────────────┐  ┌────────────────┐  ┌────────────────┐
│      TITLE     │  │  ◄ MENU ITEM   │  │  VALUE: 1234   │
└────────────────┘  └────────────────┘  └────────────────┘
   Centered           Left-aligned        Right-aligned
```

---

## 11) uGRID API Reference

### Core Functions
```bash
# Grid initialization
uGRID.init(width, height, device_class)
uGRID.resize(new_width, new_height)
uGRID.setDevice(device_class)

# Tile management
uGRID.createTile(x, y, content, type)
uGRID.updateTile(tile_id, new_content)
uGRID.removeTile(tile_id)
uGRID.moveTile(tile_id, new_x, new_y)

# Region operations
uGRID.defineRegion(name, x, y, width, height)
uGRID.fillRegion(region_name, pattern)
uGRID.clearRegion(region_name)

# Navigation
uGRID.focus(x, y)
uGRID.navigate(direction)
uGRID.getPosition()
uGRID.getFocused()

# Rendering
uGRID.render()
uGRID.refresh()
uGRID.invalidate(tile_id)
```

### Event System
```bash
# Grid events
uGRID.on("tile_focus", callback)
uGRID.on("tile_click", callback)
uGRID.on("grid_resize", callback)
uGRID.on("screen_switch", callback)

# Tile events
tile.on("update", callback)
tile.on("hover", callback)
tile.on("activate", callback)
```

---

## 12) Performance & Optimization

### Rendering Optimization
- **Dirty Rectangle**: Only redraw changed tiles
- **Viewport Culling**: Skip off-screen tile rendering
- **Layer Caching**: Cache static layer content
- **Batch Updates**: Group multiple tile changes

### Memory Management
- **Tile Pooling**: Reuse tile objects
- **Content Compression**: Minimize tile content size
- **Lazy Loading**: Load tile content on demand
- **Garbage Collection**: Clean up unused tiles

### Performance Targets
```
Tile Update Rate:    60 FPS (16.67ms per frame)
Grid Resize:         < 100ms for any size change
Screen Switch:       < 50ms transition time
Memory Usage:        < 1MB per 100 tiles
```

---

## 13) Integration with uDOS Core

### uCORE Commands
```bash
ucode grid init 80 30                    # Initialize 80×30 grid
ucode grid tile create 3 2 "Hello"       # Create tile at 3,2
ucode grid region define MAIN 2 1 6 4    # Define main region
ucode grid screen switch DASHBOARD       # Switch to dashboard screen
```

### uDATA Integration
```json
{
  "grid_config": {
    "width": 80, "height": 30,
    "device_class": "terminal",
    "regions": [
      {"name": "HEADER", "x": 0, "y": 0, "w": 80, "h": 1},
      {"name": "MAIN", "x": 0, "y": 1, "w": 60, "h": 28},
      {"name": "SIDEBAR", "x": 60, "y": 1, "w": 20, "h": 28}
    ]
  }
}
```

### File System Integration
- **Grid Layouts**: `uCORE/templates/grid-*.json`
- **Widget Definitions**: `uCORE/templates/widget-*.json`
- **Screen Configs**: `uCORE/templates/screen-*.json`
- **Theme Data**: `uCORE/templates/theme-*.json`

---

## 14) Development Examples

### Basic Grid Setup
```bash
#!/bin/bash
# Initialize 80×30 terminal grid
ucode grid init 80 30 terminal

# Define layout regions
ucode grid region define HEADER 0 0 80 1
ucode grid region define SIDEBAR 0 1 20 28
ucode grid region define MAIN 20 1 60 28
ucode grid region define FOOTER 0 29 80 1

# Create header tiles
ucode grid tile create 0 0 "uDOS v1.0.4.1" static
ucode grid tile create 70 0 "12:34:56" dynamic

# Start main application
ucode grid screen switch MAIN_APP
```

### Widget Creation
```bash
# Create a clock widget spanning 2×1 tiles
ucode grid widget create CLOCK 78 0 2 1 \
  --type dynamic \
  --update 1000 \
  --content '$(date +"%H:%M")'

# Create interactive menu
ucode grid widget create MENU 0 1 20 10 \
  --type interactive \
  --content @menu-main.json \
  --on_select "ucode menu handle"
```

### 4× Resolution Graphics
```bash
# Create high-detail icon using 4× overlay
ucode grid tile create 5 5 "" overlay_4x
ucode grid overlay draw 5 5 << 'EOF'
....████....████....
..████████████████..
.██████████████████.
.██████████████████.
..████████████████..
...██████████████...
....████████████....
.....██████████.....
......████████......
.......██████.......
........████........
.........██.........
EOF
```

---

## 15) Compatibility & Standards

### Cross-Platform Support
- **Terminal**: Full ASCII/Unicode block graphics
- **Web**: HTML5 Canvas with CSS Grid fallback
- **Native**: OpenGL/Metal/Direct3D acceleration
- **Mobile**: Touch-optimized gesture support

### Accessibility Features
- **High Contrast**: Automatic contrast adjustment
- **Screen Readers**: Semantic markup for tiles
- **Keyboard Navigation**: Full keyboard accessibility
- **Focus Indicators**: Clear visual focus states

### Standards Compliance
- **Unicode**: Full Unicode block character support
- **Color**: ANSI color codes with RGB extensions
- **Layout**: CSS Grid compatible positioning
- **Performance**: 60 FPS rendering target

---

**uGRID Display System provides uDOS with a comprehensive, scalable, and high-performance tile-based display architecture supporting everything from wearable devices to wall-mounted dashboards with consistent 16×16 uCELL foundation and advanced 4× resolution capabilities.**
