# Graphics System - Block Libraries (v1.1.15+)

**Version:** 1.1.15
**Status:** Maintenance (Active for map rendering)

## Overview

**⚠️ NOTE**: As of v1.1.15, diagram generation has moved to `core/data/diagrams/` with improved organization and templates. This directory now primarily contains block libraries used for map rendering.

For new diagram generation, see:
- `GENERATE SVG --survival <category>/<prompt>` - Survival diagrams
- `GENERATE ASCII <type> <content>` - ASCII graphics
- `core/data/diagrams/` - New diagram system

This directory maintains:
- **Block libraries** (`blocks/*.json`) - Character sets for map rendering
- **Teletext renderer** - Used by map_handler.py
- **Historical reference** (`.archive/`) - Old GraphicsCompositor system

## Directory Structure

```
core/data/graphics/
├── blocks/                # Block libraries (ACTIVE)
│   ├── teletext.json     # Teletext characters for map rendering
│   ├── borders.json      # Border styles
│   ├── patterns.json     # Fill patterns
│   └── maps.json         # Terrain blocks
├── README.md             # This file
└── .archive/             # Old GraphicsCompositor system (v1.1.1-1.1.14)
    ├── README.md         # Archive documentation
    ├── templates/        # Old diagram templates (DEPRECATED)
    ├── compositions/     # Old pre-rendered diagrams (DEPRECATED)
    └── components.json   # Old component definitions (DEPRECATED)
```

**For new diagrams**, see:
```
core/data/diagrams/
├── blocks/               # Block-shaded survival diagrams (25 files)
├── plain/                # Plain ASCII survival diagrams (26 files)
├── mermaid/              # Mermaid diagram templates
└── templates/            # Generation templates
    ├── survival_prompts.json  # 13 optimized prompts
    ├── style_guide_pro.md     # Professional style
    ├── style_guide_strict.md  # Strict compliance
    └── style_guide_refined.md # Refined aesthetic
```

## Current Usage (v1.1.15+)

### Generate Survival Diagrams

```bash
# Generate optimized survival diagrams
GENERATE SVG --survival water/purification_flow --pro
GENERATE SVG --survival shelter/build_sequence --strict
GENERATE SVG --survival fire/methods_comparison --refined

# List all available survival prompts
GENERATE --survival-help

# Generate ASCII graphics
GENERATE ASCII box "Water Sources" 40 5
GENERATE ASCII list "1. Boil\n2. Filter\n3. Purify" 30
```

### Browse Diagram Library

```bash
# Browse existing diagrams
DIAGRAM LIST                    # Show all diagrams
DIAGRAM SEARCH water            # Find water-related diagrams
DIAGRAM SHOW water_filter       # Display specific diagram
DIAGRAM TYPES                   # Show categories
```

### Using Block Libraries (Advanced)

The block libraries in `blocks/*.json` are used by the teletext renderer for map visualization:

```python
from core.output.teletext_renderer import TeletextMosaicRenderer

renderer = TeletextMosaicRenderer()
map_visual = renderer.render_map(grid_data)
```

## Block Library Reference

See `.archive/README.md` for historical GraphicsCompositor documentation.

For current diagram generation capabilities, see `core/data/diagrams/README.md`.

---

## Migration from v1.1.14 → v1.1.15

**Old commands (DEPRECATED)**:
```bash
DIAGRAM GENERATE source.md --style technical
DIAGRAM GENERATE knowledge/water/ --batch
```

**New commands (v1.1.15+)**:
```bash
GENERATE SVG --survival water/purification_flow --pro
GENERATE ASCII box "Content" 40 5
```

**What changed**:
- ✅ DIAGRAM GENERATE removed (redundant with GENERATE command)
- ✅ GraphicsCompositor archived (replaced with refined system)
- ✅ New survival prompt templates (13 optimized prompts)
- ✅ Three style modes (Professional, Strict, Refined)
- ✅ Better ASCII generation with 7 types
- ✅ Improved diagram organization

**What's preserved**:
- ✅ Block libraries (`blocks/*.json`) - Still used for maps
- ✅ Teletext renderer - Still used by map_handler.py
- ✅ All existing diagrams accessible via `DIAGRAM SHOW <name>`

---

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
- **SVG Graphics Extension** (v1.1.2) - See `dev/svg-extension-spec-v1.1.2.md`
- **Knowledge System** - See `wiki/Knowledge-System.md`
- **Content Generation** - See `wiki/Content-Generation.md`
- **Theme System** - See `wiki/Theme-System.md`

## Support

For issues or questions:
- GitHub Issues: https://github.com/fredporter/uDOS/issues
- Discussions: https://github.com/fredporter/uDOS/discussions
- Wiki: https://github.com/fredporter/uDOS/wiki
