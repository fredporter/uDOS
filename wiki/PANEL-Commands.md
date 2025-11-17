# PANEL Commands - Teletext Graphics System

Complete guide to the PANEL graphics and display system (v1.0.21)

---

## 🎨 Overview

The **PANEL System** provides character-based display panels with teletext-style graphics. Create buffers, draw with Unicode block characters, apply patterns, and export to markdown.

### Key Features
- **Character-based displays** with definable width × height boundaries
- **15 screen tiers** from Watch (20×10) to 8K (320×160 characters)
- **POKE command** for C64-style character manipulation at x,y coordinates
- **Teletext blocks** (█▓▒░), mosaic graphics, and Unicode support
- **Terrain rendering** with ASCII art symbols
- **Border display** (C64-style ▓ blocks)
- **Markdown export** for embedding diagrams

---

## 📋 Basic Commands

### PANEL CREATE
Create a new display panel

**Usage**:
```bash
PANEL CREATE <name> <width> <height> <tier>
```

**Examples**:
```bash
🔮 > PANEL CREATE dashboard 80 25 4
✅ Panel 'dashboard' created (80×25, Desktop tier)

🔮 > PANEL CREATE watch 20 10 0
✅ Panel 'watch' created (20×10, Watch tier)

🔮 > PANEL CREATE banner 120 20 6
✅ Panel 'banner' created (120×20, 4K tier)
```

**Screen Tiers** (0-14):
| Tier | Name | Dimensions | Use Case |
|:----:|:-----|:-----------|:---------|
| 0 | Watch | 20×10 | Tiny displays |
| 1 | Mobile | 40×20 | Phone screens |
| 2 | Tablet | 60×30 | Tablet displays |
| 3 | Laptop | 80×40 | Laptop screens |
| 4 | Desktop | 120×60 | Desktop monitors |
| 5 | 2K | 160×80 | 2K displays |
| 6 | 4K | 240×120 | 4K monitors |
| 7 | 8K | 320×160 | 8K displays |

---

### PANEL SHOW
Display panel contents

**Usage**:
```bash
PANEL SHOW <name> [border]
```

**Examples**:
```bash
🔮 > PANEL SHOW dashboard
┌────────────────────────────────┐
│ Dashboard Content Here         │
│                                │
└────────────────────────────────┘

🔮 > PANEL SHOW dashboard border
▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓
▓ Dashboard Content Here         ▓
▓                                ▓
▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓
```

**Border styles**:
- `border` - C64-style ▓ blocks
- No argument - Clean box drawing

---

### PANEL LIST
Show all panels

**Usage**:
```bash
PANEL LIST
```

**Example**:
```bash
🔮 > PANEL LIST
📋 Panels (3):
  dashboard (80×25, Desktop)
  watch (20×10, Watch)
  banner (120×20, 4K)
```

---

### PANEL INFO
Get panel statistics

**Usage**:
```bash
PANEL INFO <name>
```

**Example**:
```bash
🔮 > PANEL INFO dashboard
📊 Panel: dashboard
   Dimensions: 80×25 (2,000 cells)
   Tier: 4 (Desktop)
   Memory: 4.0 KB
   Fill: 42% (840 characters)
```

---

### PANEL CLEAR
Clear panel buffer

**Usage**:
```bash
PANEL CLEAR <name>
```

**Example**:
```bash
🔮 > PANEL CLEAR dashboard
✅ Panel 'dashboard' cleared
```

---

### PANEL DELETE
Remove panel

**Usage**:
```bash
PANEL DELETE <name>
```

**Example**:
```bash
🔮 > PANEL DELETE old_panel
✅ Panel 'old_panel' deleted
```

---

## ✏️ Drawing Commands

### PANEL POKE
Write single character at position (C64-style)

**Usage**:
```bash
PANEL POKE <name> <x> <y> <character>
```

**Examples**:
```bash
🔮 > PANEL POKE dashboard 10 5 █
✅ Character written

🔮 > PANEL POKE dashboard 0 0 @
✅ Top-left corner marked

🔮 > PANEL POKE watch 19 9 *
✅ Bottom-right marked
```

**Coordinates**: 0-based (0,0 = top-left)

---

### PANEL WRITE
Write text string at position

**Usage**:
```bash
PANEL WRITE <name> <x> <y> <text>
```

**Examples**:
```bash
🔮 > PANEL WRITE dashboard 5 10 "System Status: OK"
✅ Text written (17 characters)

🔮 > PANEL WRITE banner 0 0 "=== WELCOME TO uDOS ==="
✅ Text written (23 characters)

🔮 > PANEL WRITE watch 2 2 "12:45"
✅ Time displayed
```

**Features**:
- Auto-wraps at panel boundary
- Supports Unicode
- Emoji compatible

---

### PANEL FILL
Fill rectangular area with character

**Usage**:
```bash
PANEL FILL <name> <x> <y> <width> <height> <character>
```

**Examples**:
```bash
🔮 > PANEL FILL dashboard 0 0 80 1 ═
✅ Top border filled

🔮 > PANEL FILL dashboard 10 5 20 10 ▒
✅ Rectangle filled (200 cells)

🔮 > PANEL FILL background 0 0 120 60 ░
✅ Background pattern applied
```

**Use cases**:
- Borders and lines
- Background fills
- Box drawing
- Separators

---

## 🎨 Graphics Commands

### PANEL BLOCK
Place teletext block graphic

**Usage**:
```bash
PANEL BLOCK <name> <x> <y> <block_type>
```

**Block Types**:

**Shading** (4):
- `full` → █ (solid)
- `dark` → ▓ (75%)
- `medium` → ▒ (50%)
- `light` → ░ (25%)

**Half blocks** (4):
- `top` → ▀ (top half)
- `bottom` → ▄ (bottom half)
- `left` → ▌ (left half)
- `right` → ▐ (right half)

**Quarter blocks** (4):
- `topleft` → ▘
- `topright` → ▝
- `bottomleft` → ▖
- `bottomright` → ▗

**Mosaic** (3):
- `checkerboard` → ▚
- `diagonal1` → ▞
- `diagonal2` → ▚

**Examples**:
```bash
🔮 > PANEL BLOCK dashboard 5 5 full
✅ Solid block placed: █

🔮 > PANEL BLOCK map 20 10 dark
✅ Shaded block: ▓

🔮 > PANEL BLOCK ui 0 0 topleft
✅ Corner block: ▘
```

---

### PANEL PATTERN
Fill area with pattern

**Usage**:
```bash
PANEL PATTERN <name> <x> <y> <width> <height> <pattern>
```

**Patterns**:
- `checkerboard` - Alternating █░
- `gradient` - Smooth █▓▒░
- `waves` - Ocean ≈~
- `dots` - Sparse · ·
- `diagonal` - Stripes ▞▚

**Examples**:
```bash
🔮 > PANEL PATTERN background 0 0 80 25 gradient
✅ Gradient applied (2,000 cells)

🔮 > PANEL PATTERN ocean 10 5 60 15 waves
✅ Wave pattern: ≈≈~≈~≈

🔮 > PANEL PATTERN grid 0 0 40 20 checkerboard
✅ Checkerboard: █░█░█░
```

---

### PANEL TERRAIN
Fill area with terrain graphics

**Usage**:
```bash
PANEL TERRAIN <name> <x> <y> <width> <height> <terrain>
```

**Terrain Types** (16):

**Water**:
- `ocean_deep` → █ (deep ocean)
- `ocean` → ▓ (ocean)
- `ocean_shallow` → ▒ (shallow)
- `coast` → ░ (coastal)
- `water` → ≈ (water)
- `river` → ~ (flowing)
- `lake` → ○ (still water)

**Land**:
- `plains` → · (flat)
- `grassland` → ≈ (grass)
- `forest` → ♠ (trees)
- `jungle` → ♣ (dense)
- `desert` → ∴ (sand)
- `tundra` → ∙ (frozen)
- `ice` → ❄ (snow/ice)

**Elevation**:
- `hills` → ∩ (rolling)
- `mountains` → ▲ (peaks)

**Examples**:
```bash
🔮 > PANEL TERRAIN worldmap 0 10 80 5 ocean
✅ Ocean rendered: ▓▓▓▓▓

🔮 > PANEL TERRAIN worldmap 20 5 30 3 mountains
✅ Mountains: ▲▲▲▲▲

🔮 > PANEL TERRAIN biome 5 5 20 10 forest
✅ Forest: ♠♠♠♠♠
```

---

### PANEL COLOR
Apply color to region (if terminal supports)

**Usage**:
```bash
PANEL COLOR <name> <x> <y> <width> <height> <color>
```

**Colors**:
- Basic: `red`, `green`, `blue`, `yellow`, `cyan`, `magenta`, `white`, `black`
- Extended: `orange`, `purple`, `brown`, `gray`

**Example**:
```bash
🔮 > PANEL COLOR dashboard 0 0 80 1 blue
✅ Header colored blue

🔮 > PANEL COLOR map 10 10 5 5 green
✅ Forest region colored
```

---

## 📚 Reference Commands

### PANEL BLOCKS
List all block types

**Usage**:
```bash
PANEL BLOCKS
```

**Output**:
```
🎨 Block Types (24):

Shading:
  full     █  Solid block
  dark     ▓  Dark shade (75%)
  medium   ▒  Medium shade (50%)
  light    ░  Light shade (25%)

Half:
  top      ▀  Top half
  bottom   ▄  Bottom half
  left     ▌  Left half
  right    ▐  Right half

Quarter:
  topleft  ▘  Top-left
  ...
```

---

### PANEL COLORS
List available colors

**Usage**:
```bash
PANEL COLORS
```

---

### PANEL TERRAINS
List terrain types

**Usage**:
```bash
PANEL TERRAINS
```

---

### PANEL SIZE
List screen tiers

**Usage**:
```bash
PANEL SIZE
```

**Output**:
```
📺 Screen Tiers:

Tier 0: Watch      20×10   (200 cells)
Tier 1: Mobile     40×20   (800 cells)
Tier 2: Tablet     60×30   (1,800 cells)
Tier 3: Laptop     80×40   (3,200 cells)
Tier 4: Desktop    120×60  (7,200 cells)
...
```

---

## 💾 Export Commands

### PANEL EMBED
Export panel to markdown

**Usage**:
```bash
PANEL EMBED <name> <filename.md>
```

**Example**:
```bash
🔮 > PANEL EMBED dashboard report.md
✅ Panel exported to report.md

Output file:
```markdown
# Dashboard

\`\`\`
┌────────────────────────────────┐
│ System Status: OK              │
│ Memory: 42%                    │
│ CPU: 18%                       │
└────────────────────────────────┘
\`\`\`
```

**Use cases**:
- Documentation diagrams
- ASCII art export
- Report generation
- Embed in knowledge guides

---

## 🎯 Examples

### Progress Bar
```bash
PANEL CREATE progress 50 3 1
PANEL FILL progress 0 0 50 1 ═
PANEL WRITE progress 2 1 "Loading..."
PANEL FILL progress 2 2 30 1 █
PANEL FILL progress 32 2 18 1 ░
PANEL SHOW progress
```

Output:
```
══════════════════════════════════════════════════
  Loading...
  ██████████████████████████████░░░░░░░░░░░░░░░░░░
```

---

### Simple Map
```bash
PANEL CREATE map 40 20 2
PANEL TERRAIN map 0 0 40 10 ocean
PANEL TERRAIN map 0 10 40 10 plains
PANEL TERRAIN map 15 8 10 6 mountains
PANEL TERRAIN map 5 12 5 4 forest
PANEL SHOW map border
```

---

### Dashboard
```bash
PANEL CREATE dash 80 25 3
PANEL FILL dash 0 0 80 1 ═
PANEL WRITE dash 30 0 " SYSTEM DASHBOARD "
PANEL FILL dash 0 24 80 1 ═
PANEL WRITE dash 2 2 "CPU: 23%"
PANEL FILL dash 10 2 23 1 █
PANEL WRITE dash 2 4 "RAM: 67%"
PANEL FILL dash 10 4 67 1 ▓
PANEL SHOW dash
```

---

## 🔗 Integration

### Works With

**v1.0.20 Knowledge System**:
- Embed panels in knowledge guides
- Export diagrams to markdown
- Store panel templates in SHARED tier

**v1.0.3 GRID System**:
- Multiple panels per workspace
- Panel layering
- Named buffer management

**Markdown Viewer**:
- Live preview of embedded panels
- Syntax highlighting in code blocks
- GitHub-compatible output

---

## 📚 Related Documentation

- [Command Reference](Command-Reference) - All uDOS commands
- [TILE Commands](TILE-Commands) - Geographic data system
- [GRID System](GRID-System) - Multi-panel management
- [Getting Started](Getting-Started) - Basic usage

---

*Character-based graphics for the modern terminal.*
