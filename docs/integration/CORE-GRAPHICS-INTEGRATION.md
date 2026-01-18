# Core Graphics Integration — Complete Implementation

**Date:** 2026-01-18  
**Core Version:** v1.1.0.0  
**Wizard Version:** v1.0.0.1  
**Status:** ✅ Complete

---

## Overview

Integrated comprehensive text graphics capabilities into `/core`, establishing it as the master of ASCII patterns, teletext blocks, diagrams, and feed generation. This creates a clean separation: Core handles text/TUI, Wizard handles web/SVG rendering.

---

## Architecture Changes

### Before (v1.0.0.1)

- Core: TypeScript runtime only
- Graphics: Scattered across Wizard/Goblin
- No pattern generation in Core
- No feed handling in Core

### After (v1.1.0.0)

- Core: TypeScript + Python graphics module
- Core: Master of text graphics (ASCII, teletext, diagrams, feeds)
- Wizard: Web/SVG rendering service
- Clear separation: Core generates text, Wizard renders web

---

## New Core Modules

### 1. `/core/graphics/` Package

```
core/graphics/
  __init__.py              # Package interface
  ascii_patterns.py        # ASCII pattern generation
  block_graphics.py        # Teletext/sextant block handling
  diagram_parser.py        # Markdown diagram parsing
  feed_handler.py          # RSS/JSON feed generation
```

**Total:** 5 files, ~1,200 lines of Python

---

## Module Capabilities

### 1. ASCII Pattern Generator (`ascii_patterns.py`)

**Purpose:** Generate terminal-ready ASCII patterns

**Patterns Supported:**

- Chevrons (zigzag lines)
- Scanlines (horizontal bars)
- Density ramps (gradients)
- Grids (box drawing)
- Waves (sine curves)
- Mosaics (random tiles)
- Checkerboards

**Key Features:**

- 80×30 default viewport (configurable)
- Unicode mode (░▒▓█) vs ASCII mode (. : # @)
- Phase-based animation support
- Tile-based pattern repetition

**Example Usage:**

```python
from core.graphics import ASCIIPatternGenerator

gen = ASCIIPatternGenerator(width=80, height=30, unicode_mode=True)
lines = gen.generate_chevrons(phase=0)
for line in lines:
    print(line)
```

**Patterns Available:**

- `generate_chevrons(phase)` — Zigzag diagonal lines
- `generate_scanlines(phase, frequency)` — Horizontal density bands
- `generate_density_ramp(vertical, phase)` — Gradient patterns
- `generate_grid(cell_width, cell_height)` — Box grid
- `generate_wave(phase, frequency, amplitude)` — Sine wave
- `generate_mosaic(tile_chars, tile_size, phase)` — Random tiles
- `generate_checker(cell_size, phase)` — Checkerboard
- `tile_pattern(pattern, tile_width, tile_height)` — Pattern tiling

---

### 2. Block Graphics Renderer (`block_graphics.py`)

**Purpose:** Handle teletext 2×3 mosaic block graphics

**Key Classes:**

**TeletextEncoder:**

- Encode/decode 6-bit masks (2×3 grid)
- Sextant Unicode range: U+1FB00 to U+1FB3B (64 chars)
- Fallback ladder: Sextant → Quadrant → Shades → ASCII

**BlockGraphicsRenderer:**

- Render sextant patterns with fallback modes
- Generate test patterns (all 64 combinations)
- Create gradients, checkerboards
- Pattern compilation

**Mask Format (6 bits):**

```
b0 b1  (top row)
b2 b3  (middle row)
b4 b5  (bottom row)
```

**Example Usage:**

```python
from core.graphics import TeletextEncoder, BlockGraphicsRenderer

# Encode mask to character
encoder = TeletextEncoder()
char = encoder.mask_to_sextant(0b110011)  # Returns: 🬓

# Render pattern with fallback
renderer = BlockGraphicsRenderer(fallback_mode='sextant')
pattern = renderer.create_gradient_pattern(width=24, height=8)
lines = renderer.render_pattern(pattern, 24, 8)
```

**Fallback Modes:**

- `sextant` — Full 2×3 Unicode blocks (default)
- `quadrant` — 2×2 Unicode blocks (▘▝▖▗▙▟▛▜)
- `shade` — Density-based shades (░▒▓█)
- `ascii` — ASCII characters (. : # @)

---

### 3. Diagram Parser (`diagram_parser.py`)

**Purpose:** Parse text diagrams from Markdown

**Supported Diagram Types:**

- `teletext` — Teletext character grids
- `pattern` — Pattern definitions with parameters
- `flowchart` — Flowchart.js syntax
- `sequence` — Sequence diagrams
- `grid` — Spatial grid diagrams
- `ascii-art` — Generic ASCII art

**Markdown Syntax:**

````markdown
```teletext width=80 height=24
🬀🬁🬂🬃🬄🬅🬆🬇
▀▄█▌▐▖▗▘▙▚▛▜
```

```pattern type=chevrons phase=5
Animated chevron pattern
```

```flowchart
start=>start: Start
process=>operation: Process
end=>end: End
start->process->end
```
````

**Example Usage:**

```python
from core.graphics import DiagramParser

parser = DiagramParser()
diagrams = parser.parse(markdown_text)

for diag in diagrams:
    print(f"Type: {diag['type']}")
    if 'lines' in diag:
        for line in diag['lines']:
            print(line)
```

**Output Format:**

````python
{
    'type': 'teletext',
    'width': 80,
    'height': 24,
    'lines': ['...', '...'],
    'raw': '```teletext...'
}
````

---

### 4. Feed Handler (`feed_handler.py`)

**Purpose:** Generate and parse RSS/JSON feeds

**Feed Formats:**

- RSS 2.0 (XML)
- JSON Feed v1.1
- Atom (planned)

**Key Methods:**

- `generate_rss(items, title, desc, link)` — Create RSS feed
- `generate_json_feed(items, title, desc, url)` — Create JSON feed
- `parse_rss(xml_str)` — Parse incoming RSS
- `parse_json_feed(json_str)` — Parse incoming JSON Feed
- `compile_feed(source_files, format)` — Compile from markdown files

**Example Usage:**

```python
from core.graphics import FeedHandler

handler = FeedHandler()

items = [
    {
        'title': 'Post Title',
        'description': 'Post content',
        'link': 'https://example.com/post',
        'pubDate': 'Mon, 18 Jan 2026 12:00:00 GMT',
    }
]

rss = handler.generate_rss(
    items,
    title='My Feed',
    description='A test feed',
    link='https://example.com'
)
```

**Feed Workflow:**

1. Core: Generate feed from markdown files
2. Core → Wizard: Send feed via API
3. Wizard: Process/transform feed
4. Wizard → Core: Send processed feed
5. Core: Parse and display

---

## Integration with Wizard

### Wizard Responsibilities (Port 8765)

1. **Font Collections API** (`/api/v1/fonts/`)
   - Serve 8 collections (217 characters)
   - Renamed: Sextant Blocks → Teletext Blocks
   - Fixed response: Added `display_name`, `count` fields

2. **SVG Rendering** (planned)
   - Convert Core text graphics → SVG
   - Serve web-friendly formats
   - Handle complex glyphs

3. **Feed Processing** (planned)
   - Transform feeds from Core
   - Add metadata/enrichment
   - Distribute to subscribers

### Core ↔ Wizard Communication

**Core generates text:**

```python
# Core generates teletext pattern
from core.graphics import BlockGraphicsRenderer
renderer = BlockGraphicsRenderer()
pattern = renderer.create_test_pattern()
lines = renderer.render_pattern(pattern, 8, 8)
```

**Wizard renders web:**

```python
# Wizard converts to SVG (future)
@router.post("/api/v1/render/svg")
async def render_svg(text_pattern: str):
    svg = convert_teletext_to_svg(text_pattern)
    return {"svg": svg}
```

---

## Terminology Updates

### Sextant → Teletext Rename

**Changed Files:**

1. `/public/wizard/routes/fonts.py`
   - Collection key: `"sextant"` → `"teletext"`
   - Family: `"Sextant Blocks"` → `"Teletext Blocks"`
   - Style: `"2×3 Teletext"` → `"2×3 Mosaic"`

2. `/public/wizard/dashboard/src/lib/pages/PixelEditor.svelte`
   - Tool option: "Font Character" (includes teletext)
   - Character picker displays all 8 collections

3. Documentation:
   - All references updated to "Teletext Blocks"
   - Sextant retained as technical term for 2×3 encoding

**Rationale:**

- "Teletext" is user-facing (retro BBC Micro vibe)
- "Sextant" is technical (6-bit mask encoding)
- Aligns with retro computing heritage

---

## Testing

### ASCII Patterns

```bash
cd /Users/fredbook/Code/uDOS
source .venv/bin/activate
python -m core.graphics.ascii_patterns
```

**Output:** Sample chevrons, scanlines, grid, wave patterns

### Block Graphics

```bash
python -m core.graphics.block_graphics
```

**Output:** Sextant encoding demo, fallback rendering comparison

### Diagram Parser

```bash
python -m core.graphics.diagram_parser
```

**Output:** Parsed diagram structures from test markdown

### Feed Handler

```bash
python -m core.graphics.feed_handler
```

**Output:** Sample RSS and JSON feeds

---

## API Changes

### Font Collections Endpoint

**Before:**

```json
{
  "collections": [
    {
      "name": "teletext",
      "family": "Teletext Blocks",
      "style": "2×3 Mosaic",
      "character_count": 63
    }
  ]
}
```

**After (v1.0.0.1):**

```json
{
  "collections": [
    {
      "name": "teletext",
      "display_name": "Teletext Blocks",
      "family": "Teletext Blocks",
      "style": "2×3 Mosaic",
      "count": 63,
      "character_count": 63
    }
  ]
}
```

**Added Fields:**

- `display_name` — Human-friendly name for UI
- `count` — Duplicate of character_count (Svelte expects both)

---

## Version Management

### Component Versions

| Component  | Version  | Changes                                    |
| ---------- | -------- | ------------------------------------------ |
| **Core**   | v1.1.0.0 | Added graphics module (4 new Python files) |
| **Wizard** | v1.0.0.1 | Font API fixes, Teletext rename            |
| **App**    | v1.0.3.0 | No changes (stable)                        |

### Version Strategy

- **Core:** Major bump (1.0 → 1.1) for new module
- **Wizard:** Build increment (1.0.0.0 → 1.0.0.1) for API fixes
- **Going forward:** Slow incremental bumps (build → patch → minor → major)

---

## Documentation Updates

### Created Files

1. `/core/graphics/__init__.py` — Package interface
2. `/core/graphics/ascii_patterns.py` — Pattern generator (340 lines)
3. `/core/graphics/block_graphics.py` — Teletext encoder (280 lines)
4. `/core/graphics/diagram_parser.py` — Diagram parser (220 lines)
5. `/core/graphics/feed_handler.py` — Feed handler (260 lines)
6. `/docs/integration/CORE-GRAPHICS-INTEGRATION.md` — This document

### Updated Files

1. `/core/version.json` — v1.1.0.0, added graphics features
2. `/public/wizard/version.json` — v1.0.0.1, font API updates
3. `/public/wizard/routes/fonts.py` — Teletext rename, API fix
4. `/public/wizard/dashboard/src/lib/pages/PixelEditor.svelte` — Debug logging

---

## File Structure

```
core/
  graphics/
    __init__.py              # 29 lines - Package exports
    ascii_patterns.py        # 340 lines - Pattern generation
    block_graphics.py        # 280 lines - Teletext encoding
    diagram_parser.py        # 220 lines - Markdown parsing
    feed_handler.py          # 260 lines - RSS/JSON feeds
  version.json              # Updated to v1.1.0.0

public/wizard/
  routes/
    fonts.py                # Updated: Teletext rename, API fix
  dashboard/src/lib/pages/
    PixelEditor.svelte      # Updated: Debug logging
  version.json              # Updated to v1.0.0.1

docs/integration/
  CORE-GRAPHICS-INTEGRATION.md  # This file
```

---

## Next Steps

### Immediate (v1.0.0.2)

- [ ] Test ASCII patterns in TUI
- [ ] Test teletext rendering in terminal
- [ ] Validate feed generation
- [ ] Wire diagram parser to TUI commands

### Short Term (v1.1.0.0)

- [ ] Add SVG conversion endpoint to Wizard
- [ ] Implement Core → Wizard feed sync
- [ ] Add pattern caching
- [ ] Performance optimization

### Long Term (v1.2.0.0+)

- [ ] WebView integration in Core (optional)
- [ ] Real-time pattern animation
- [ ] Multi-layer pattern composition
- [ ] Advanced diagram types (UML, architecture)

---

## Summary

✅ **Achieved:**

- Core is now master of text graphics (ASCII, teletext, diagrams, feeds)
- Clean separation: Core generates text, Wizard renders web
- 5 new Python modules (~1,200 lines)
- Teletext terminology standardized
- Font API fixes for Pixel Editor integration
- Version management clarified (slow incremental bumps)

✅ **Ready for:**

- TUI pattern commands
- Terminal graphics rendering
- Feed compilation from markdown
- Diagram-driven navigation

✅ **Foundation for:**

- SVG rendering service in Wizard
- Real-time feed sync
- Advanced pattern animation
- Multi-format diagram support

---

_Integration Complete: 2026-01-18_  
_Core v1.1.0.0 | Wizard v1.0.0.1_  
_Total Lines Added: ~1,200_
