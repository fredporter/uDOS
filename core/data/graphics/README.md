# Graphics System - ASCII/Teletext Diagrams

**Version:** 1.1.1
**Status:** Active (Content Generation Phase)

## Overview

The uDOS graphics system generates consistent, chunky teletext-style ASCII diagrams for all knowledge content. This system prioritizes:

- **Offline-first** - No API calls, all rendering local
- **Terminal-native** - Perfect rendering in any terminal
- **Consistent aesthetic** - Retro teletext chunky blocks
- **Programmatic generation** - Compose diagrams from reusable blocks
- **Text-first** - Accessible, copy-paste friendly

## Directory Structure

```
core/data/graphics/
├── blocks/                 # Consolidated block library
│   ├── teletext.json      # ALL blocks: diagrams, maps, mosaic patterns
│   ├── borders.json       # Border styles (heavy, double, light, rounded, block)
│   ├── patterns.json      # Fill patterns and textures (diagrams)
│   └── maps.json          # Map-specific terrain, biomes, transitions
├── templates/             # Diagram templates
│   ├── flow_diagram.json  # Vertical flow charts
│   ├── tree_diagram.json  # Hierarchical trees
│   └── grid_diagram.json  # Tables and grids
├── compositions/          # Pre-rendered example diagrams
│   ├── water_purification_flow.txt
│   ├── shelter_hierarchy_tree.txt
│   └── fire_methods_grid.txt
└── archive/               # Deprecated files (reference only)
    ├── README.md
    ├── ascii_blocks.json      # Consolidated into blocks/teletext.json
    └── teletext_mosaic.json   # Consolidated into blocks/teletext.json
```

## Quick Start

### Using the Graphics Compositor

```python
from core.services.graphics_compositor import GraphicsCompositor

gc = GraphicsCompositor()

# Create a flow diagram
flow = gc.create_flow([
    'Collect Water',
    'Filter Particles',
    'Boil 1-3 Minutes',
    'Cool & Store'
], style='chunky', width=30)

print(flow)
```

Output:
```
▐▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▌
▐    Collect Water         ▌
▐▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▌
             ┃
             ▼
▐▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▌
▐    Filter Particles      ▌
▐▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▌
             ┃
             ▼
...
```

### Convenience Functions

```python
from core.services.graphics_compositor import create_flow, create_tree, create_grid

# Flow diagram
flow = create_flow(['Step 1', 'Step 2', 'Step 3'])

# Tree hierarchy
tree = create_tree('Root', ['Child 1', 'Child 2', 'Child 3'])

# Grid/table
grid = create_grid(
    headers=['Method', 'Time', 'Difficulty'],
    rows=[
        ['Friction', '10min', 'Hard'],
        ['Flint', '2min', 'Easy']
    ]
)
```

## Available Styles

### Box Styles

- **heavy** - Bold, thick borders (┏━━┓)
- **double** - Double-line borders (╔══╗)
- **light** - Thin borders (┌──┐)
- **rounded** - Rounded corners (╭──╮)
- **block** - Solid block borders (█▀▀█)
- **chunky** - Teletext chunky style (▐▀▀▌)

### Diagram Types

#### 1. Flow Diagrams
Vertical process flows with arrows:
```python
flow = gc.create_flow(
    steps=['Start', 'Process', 'End'],
    style='chunky',  # or 'heavy', 'light'
    width=30
)
```

#### 2. Tree Diagrams
Hierarchical branching structures:
```python
tree = gc.create_tree(
    root='Main Category',
    children=['Sub 1', 'Sub 2', 'Sub 3'],
    width=20,
    indent=4
)
```

#### 3. Grid Diagrams
Tables and comparison charts:
```python
grid = gc.create_grid(
    headers=['Col1', 'Col2', 'Col3'],
    rows=[
        ['Data1', 'Data2', 'Data3'],
        ['Data4', 'Data5', 'Data6']
    ],
    col_width=15
)
```

## Block Library Reference

### Teletext Blocks (blocks/teletext.json)

**Consolidated library** containing all blocks for diagrams AND map rendering.

**Solid Blocks:**
- `█` Full block
- `▀` Upper half
- `▄` Lower half
- `▌` Left half
- `▐` Right half
- `░▒▓` Light/medium/dark shading

**Box Drawing:**
- Heavy: `┏━┓┗━┛┃━`
- Light: `┌─┐└─┘│─`
- Double: `╔═╗╚═╝║═`
- Rounded: `╭─╮╰─╯`

**Arrows:**
- `▲▼◀▶` Solid triangles
- `△▽◁▷` Outline triangles
- `⬆⬇⬅➡` Heavy arrows

**Connectors:**
- `┳┻┣┫╋` T-junctions and crosses
- `┏┓┗┛` Elbows and corners

**Geometric Shapes:**
- `○●` Circle (outline/filled)
- `□■` Square (outline/filled)
- `△▲▽▼` Triangles
- `◇◆` Diamond (outline/filled)
- `☆★` Star (outline/filled)

**Terrain (for maps):**
- `≈~∿` Water (deep/shallow/flow)
- `▲∩∪` Mountain/hill/valley
- `♣♠` Forest/jungle
- `,"` Grass/plain
- `░▒` Desert/tundra
- `❅❄` Ice/glacier

**Special Characters:**
- `•°±×÷∞` Math and symbols
- `↑↓←→` Directional arrows

**Mosaic Patterns (2×3 WST blocks):**
- 64 binary-encoded patterns for pixel-level control
- Access via `blocks['mosaic_2x3']['patterns']`
- Terrain mappings: ocean, sea, lake, river, forest, mountain, etc.
- Advanced teletext rendering capabilities

### Pattern Library (blocks/patterns.json)

**Fills:**
- Solid: `█`
- Light: `░`
- Medium: `▒`
- Dark: `▓`
- Dots: `··`
- Cross-hatch: `╳`

**Backgrounds:**
- Water: `░░░`
- Fire: `▒▓▒`
- Earth: `▓▒░`
- Wood: `║│║`
- Stone: `▓▓▒`

**Separators:**
- Thin: `─────`
- Thick: `━━━━━`
- Double: `═════`
- Dotted: `┄┄┄┄┄`
- Dashed: `╌╌╌╌╌`

## Usage Examples

### Example 1: Water Purification Process

```python
gc = GraphicsCompositor()

steps = [
    "Collect Water Source",
    "Filter Large Particles",
    "Boil for 1-3 minutes",
    "Cool and store safely"
]

diagram = gc.create_flow(steps, style='chunky', width=35)
print(diagram)
```

### Example 2: Shelter Type Hierarchy

```python
tree = gc.create_tree(
    root="Emergency Shelter",
    children=["Natural", "Constructed", "Improvised"],
    width=22
)
print(tree)
```

### Example 3: Fire Starting Methods Comparison

```python
headers = ["Method", "Difficulty", "Time", "Materials"]
rows = [
    ["Friction", "Hard", "5-15min", "Dry wood"],
    ["Flint/Steel", "Medium", "1-3min", "Flint, steel"],
    ["Magnifier", "Easy", "30sec", "Glass, sun"]
]

grid = gc.create_grid(headers, rows, col_width=15)
print(grid)
```

### Example 4: Custom Boxes and Labels

```python
# Create a titled box
box = gc.create_box(
    width=40,
    height=5,
    title="Water Purification",
    style='heavy',
    content=["Line 1", "Line 2", "Line 3"]
)

# Create chunky labels
label = gc.create_label("CRITICAL", style='chunky')

# Create arrow connectors
arrow = gc.create_arrow_connector(
    length=20,
    direction='right',
    label='leads to'
)
```

## Content Generation Workflow

### Step 1: Generate Diagram

```python
from core.services.graphics_compositor import GraphicsCompositor

gc = GraphicsCompositor()
diagram = gc.create_flow(['Step 1', 'Step 2', 'Step 3'])
```

### Step 2: Save to Composition

```python
output_path = 'core/data/graphics/compositions/my_diagram.txt'
with open(output_path, 'w', encoding='utf-8') as f:
    f.write(f'"""\n')
    f.write(f'My Diagram Title\n')
    f.write(f'Description of what this diagram shows\n')
    f.write(f'"""\n\n')
    f.write(diagram)
```

### Step 3: Reference in Knowledge Guide

```markdown
# Water Purification Guide

## Process Overview

```
▐▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▌
▐   Collect Water Source    ▌
▐▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▌
             ┃
             ▼
...
```

Follow these steps carefully...
```

## Testing

Run the graphics compositor test suite:

```bash
python sandbox/tests/test_graphics_compositor.py
```

This will demonstrate:
- All box styles
- Flow diagrams
- Tree diagrams
- Grid diagrams
- Labels and connectors
- Complete survival scenario example

## Design Guidelines

### Consistency Rules

1. **Always use chunky style** for primary headers/titles
2. **Use heavy borders** for important content
3. **Use light borders** for secondary/detail content
4. **Maintain consistent spacing** (use template defaults)
5. **Label all diagram elements** clearly

### Aesthetic Principles

- **Chunky over minimal** - Embrace the retro teletext aesthetic
- **High contrast** - Use solid blocks for emphasis
- **Clear hierarchy** - Primary (chunky) → Secondary (heavy) → Detail (light)
- **Readable at any size** - Works in 80-column terminals
- **Copy-paste friendly** - Pure text, no special rendering needed

### Accessibility

- All diagrams must work in any terminal (no Unicode fallback needed)
- Clear labels and annotations
- Logical flow (top-to-bottom, left-to-right)
- Self-explanatory without color

## Future Enhancements (Post v1.1.1)

- **Interactive diagrams** - Terminal-based navigation
- **Animation sequences** - Step-by-step processes
- **Color theming** - Apply theme colors to diagrams
- **Export formats** - HTML, PNG, PDF rendering
- **Diagram library browser** - Browse/search all compositions

---

## Related Documentation

- **Teletext Pattern Reference** - See `sandbox/docs/teletext-patterns-reference.md`
- **SVG Graphics Extension** (v1.1.2) - See `sandbox/dev/svg-extension-spec-v1.1.2.md`
- **Knowledge System** - See `wiki/Knowledge-System.md`
- **Content Generation** - See `wiki/Content-Generation.md`
- **Theme System** - See `wiki/Theme-System.md`

## Support

For issues or questions:
- GitHub Issues: https://github.com/fredporter/uDOS/issues
- Discussions: https://github.com/fredporter/uDOS/discussions
- Wiki: https://github.com/fredporter/uDOS/wiki
