# OK Assist - Unified Design System

**AI Content Generation: ASCII / Teletext / SVG**

System-wide extension generating content in three visual formats with shared design language based on **C64 PetMe** character set. Uses centralized `/extensions/assets/` for fonts, icons, and CSS.

## Overview

OK Assist integrates Google's Gemini API to generate diagrams and guides in three formats:

### 1. ASCII Art (Monochrome Terminal)
- **Character Set**: C64 PetMe/PETSCII (UTF-8 compatible)
- **Dimensions**: 80×24 (standard) or 40×25 (C64)
- **Output**: `.txt` files for CLI/terminal display
- **Usage**: Terminal UI, CLI diagrams, documentation

**Features**:
- Box drawing: `┌─┐│└┘╔═╗║╚╝`
- Block elements: `█▓▒░▀▄▌▐`
- PETSCII symbols: `♥★○●→←↑↓⚠✓✗`
- Monospaced precision

### 2. Teletext Graphics (8-Color Web)
- **Format**: HTML with mosaic block entities
- **Dimensions**: 40×25 (standard) or 80×25 (extended)
- **Colors**: WST 8-color palette (BLACK, RED, GREEN, YELLOW, BLUE, MAGENTA, CYAN, WHITE)
- **Output**: `.html` files for web rendering

**Features**:
- 2×3 pixel mosaic blocks (64 combinations)
- Unicode entities: `&#xE200;` - `&#xE27F;`
- Contiguous and separated modes
- Interactive web rendering

### 3. SVG Diagrams (Scalable Vector)
- **Styles**: Technical-Kinetic or Hand-Illustrative
- **Format**: Scalable vector graphics (<50KB)
- **Output**: `.svg` files for print/web/documentation

**Technical-Kinetic** (Tools, Systems, UI):
- CoreUI icons (1500+)
- Mac OS System 1 patterns
- Geometric precision
- Line weights: 1.5px primary, 0.5px detail, 2.5px bold

**Hand-Illustrative** (Anatomy, Nature, Food):
- Traditional engraving aesthetic
- Variable line weights (0.8-2.5px)
- Organic textures and shading
- Cross-contour and stipple techniques

## Unified Design System

All three formats share design vocabulary:

**Reference Point**: C64 PetMe character set
- ASCII uses PetMe64.ttf directly
- Teletext maps to mosaic equivalents
- SVG references PetMe as character baseline

**Asset Library**: `/extensions/assets/`
- **Fonts**: PetMe (C64), Chicago, Geneva, Monaco
- **Icons**: CoreUI (1500+), Mac System icons
- **Patterns**: Mac OS bitmap patterns, organic textures
- **CSS**: Shared style frameworks

See complete documentation: [`assets/DESIGN_SYSTEM.md`](assets/DESIGN_SYSTEM.md)

## Installation

### Requirements
```bash
pip install google-generativeai python-dotenv
```

### API Key Setup

Add to `.env` in project root:
```bash
# .env
GEMINI_API_KEY=your-google-api-key-here
```

Or export environment variable:
```bash
export GEMINI_API_KEY="your-key"
```

## Quick Start

### Generate ASCII Art

```python
from extensions.core.ok_assist.api.gemini import OKAssist

ok = OKAssist()  # Loads from .env

ascii_art = ok.generate_ascii(
    subject="water filter",
    description="Multi-layer gravel/sand/charcoal filtration",
    width=80,
    height=24,
    style="petme"  # C64 character set
)

print(ascii_art)
```

### Generate Teletext Graphics

```python
teletext_html = ok.generate_teletext(
    subject="forest map",
    description="Topographic map with trees, water, elevation",
    width=40,
    height=25,
    colors=["GREEN", "BLUE", "BROWN"],
    style="mosaic"
)

with open("map.html", "w") as f:
    f.write(teletext_html)
```

### Generate SVG Diagram

```python
# Technical diagram
svg_tech = ok.generate_svg(
    subject="bow saw construction",
    style="technical-kinetic",
    description="Frame, blade, tension cord with measurements",
    complexity="moderate"
)

# Organic illustration
svg_organic = ok.generate_svg(
    subject="oak leaf anatomy",
    style="hand-illustrative",
    description="Leaf structure with veins and petiole",
    complexity="detailed"
)
```

### Unified Multi-Format Generation

```python
# Generate all formats from single description
all_formats = ok.generate_all_formats(
    subject="campfire structure",
    description="Log cabin fire lay with tinder, kindling, fuel wood"
)

# Returns dict:
# - all_formats["ascii"]           → .txt
# - all_formats["teletext"]        → .html
# - all_formats["svg_technical"]   → .svg (geometric)
# - all_formats["svg_organic"]     → .svg (hand-drawn)
```

## Format Comparison

### Same Subject, Three Formats

**Water Filter Example**:

```python
ok = OKAssist()
subject = "DIY water filter"

# ASCII (80×24 terminal)
ascii = ok.generate_ascii(subject, width=80, height=24)
# Output: Box-drawing chars, block fills
# Use: CLI documentation, terminal display

# Teletext (40×25 web)
teletext = ok.generate_teletext(subject, width=40, height=25,
                                 colors=["BLUE", "CYAN", "YELLOW"])
# Output: Colorful mosaic blocks
# Use: Web maps, interactive displays

# SVG Technical (scalable vector)
svg = ok.generate_svg(subject, style="technical-kinetic")
# Output: Geometric diagram with CoreUI icons
# Use: Print documentation, high-res display
```

## Visual Style Guide

### ASCII Style (PetMe Character Set)

**Lines**:
```
Horizontal: ─ ━ ═
Vertical:   │ ┃ ║
Corners:    ┌ ┐ └ ┘ ╔ ╗ ╚ ╝
Junctions:  ┼ ╋ ├ ┤ ┬ ┴
```

**Blocks**:
```
Full:    █ (100%)
Dark:    ▓ (75%)
Medium:  ▒ (50%)
Light:   ░ (25%)
Halves:  ▀ ▄ ▌ ▐
Quarters: ▘ ▝ ▖ ▗
```

### Teletext Style (WST Mosaic)

**Entities**:
```html
Empty:  &#xE200;  (000000)
Full:   &#xE23F;  (111111)
Left:   &#xE215;  (101010)
Right:  &#xE22A;  (010101)
Top:    &#xE203;  (110000)
Bottom: &#xE230;  (001100)
```

**Colors**:
```html
<span class="bg-red">&#xE23F;</span>     RED
<span class="bg-green">&#xE23F;</span>   GREEN
<span class="bg-blue">&#xE23F;</span>    BLUE
```

### SVG Technical-Kinetic

**Specifications**:
- Line weights: 1.5px (primary), 0.5px (detail), 2.5px (bold), 0.3px (texture)
- Typography: Chicago 12pt (titles), Geneva 9pt (body), Monaco (mono)
- Icons: CoreUI `cil-*` (16×16 or 24×24)
- Patterns: Mac OS System 1 (gray-12, gray-50, crosshatch, diagonal)
- Shading: Crosshatch, stipple, parallel lines
- Subjects: Tools, machinery, systems, UI, structures, knots

### SVG Hand-Illustrative

**Specifications**:
- Line weights: 0.8px (fine), 1.5px (medium), 2.5px (bold), 0.4px (texture)
- Typography: Geneva 14pt italic bold (titles), 10pt (body), 8pt italic (captions)
- Shading: Wavy parallel, circular concentric, cross-contour, stipple density
- Textures: Woodgrain, water ripples, stone cracks, fabric weave, cloud fields
- Depth: Foreground (bold), midground (medium), background (fine, atmospheric)
- Subjects: Anatomy, plants, animals, landscapes, food, rope, natural materials

## Asset Cross-Reference

### Font Mappings

| Format | Primary Font | Path | Size |
|--------|--------------|------|------|
| ASCII | PetMe64 | `/assets/fonts/petme/PetMe64.ttf` | 8×8 |
| Teletext | PetMe2Y | `/assets/fonts/petme/PetMe2Y.ttf` | 8×16 |
| SVG Tech | Chicago/Geneva | `/assets/fonts/ChiKareGo2.woff2` | 9-12pt |
| SVG Organic | Geneva Serif | `/assets/fonts/FindersKeepers.woff2` | 10-14pt |

### Icon Mappings

| Concept | ASCII | Teletext | SVG |
|---------|-------|----------|-----|
| Tool | `⚒` | `&#xE23F;` | `cil-wrench` |
| Check | `✓` | `☑` | `cil-check-circle` |
| Warning | `⚠` | `⚠` | `cil-warning` |
| Arrow → | `→` | `►` | `cil-arrow-right` |
| Heart | `♥` | `♥` | `cil-heart` |

### Pattern Mappings

| Texture | ASCII | Teletext | SVG Tech | SVG Organic |
|---------|-------|----------|----------|-------------|
| Solid | `████` | `&#xE23F;` | `gray-87` | Solid fill |
| Metal | `▓▓▓▓` | Separated | `crosshatch` | Parallel lines |
| Wood | `≡≡≡≡` | `─` pattern | `diagonal` | Woodgrain |
| Water | `≈≈≈≈` | Blue `~` | `horizontal` | Ripples |

See complete mappings: [`assets/design_assets.py`](assets/design_assets.py)

## Directory Structure

```
ok-assist/
├── README.md                          # This file
├── api/
│   ├── gemini.py                      # Unified API (ASCII/Teletext/SVG)
│   └── prompts/
│       ├── style_definitions.json     # Style parameters
│       ├── technical_kinetic_prompt.md # SVG technical spec
│       └── hand_illustrative_prompt.md # SVG organic spec
├── assets/
│   ├── DESIGN_SYSTEM.md               # Complete design documentation
│   └── design_assets.py               # Asset management utilities
├── css/
│   ├── technical-kinetic.css          # Technical SVG styles
│   ├── hand-illustrative.css          # Organic SVG styles
│   └── svg-common.css                 # Shared SVG utilities
├── docs/
│   ├── STYLE_GUIDE.md                 # Complete style reference
│   ├── INTEGRATION.md                 # Integration guide
│   └── EXAMPLES.md                    # Generated examples
└── examples/
    ├── generate_examples.py           # SVG generation demos
    └── generate_multi_format.py       # Multi-format demos
```

## Python API Reference

### OKAssist Class

```python
from extensions.core.ok_assist.api.gemini import OKAssist

ok = OKAssist(api_key=None, model="gemini-1.5-pro")
```

**Methods**:

#### generate_ascii()
```python
ascii_art = ok.generate_ascii(
    subject: str,
    description: str = "",
    width: int = 80,
    height: int = 24,
    style: Literal["petme", "box-drawing", "minimal"] = "petme"
) -> str
```

#### generate_teletext()
```python
teletext_html = ok.generate_teletext(
    subject: str,
    description: str = "",
    width: int = 40,
    height: int = 25,
    colors: list = None,  # WST color names
    style: Literal["mosaic", "contiguous", "separated"] = "mosaic"
) -> str
```

#### generate_svg()
```python
svg_code = ok.generate_svg(
    subject: str,
    style: Literal["technical-kinetic", "hand-illustrative"] = "technical-kinetic",
    description: str = "",
    complexity: Literal["simple", "moderate", "detailed", "complex"] = "moderate",
    width: int = 800,
    height: int = 600
) -> str
```

#### generate()
```python
# Unified API
content = ok.generate(
    subject: str,
    description: str = "",
    format: Literal["ascii", "teletext", "svg"] = "svg",
    style: Optional[str] = None,
    **kwargs
) -> str
```

#### generate_all_formats()
```python
# Generate all formats at once
all_formats = ok.generate_all_formats(
    subject: str,
    description: str = ""
) -> Dict[str, str]
# Returns: {"ascii": ..., "teletext": ..., "svg_technical": ..., "svg_organic": ...}
```

#### auto_detect_style()
```python
# Auto-detect SVG style from subject
style = ok.auto_detect_style(subject: str) -> str
# Returns: "technical-kinetic" or "hand-illustrative"
```

### Design Assets Manager

```python
from extensions.core.ok_assist.assets.design_assets import DesignAssets

# Get font path
font = DesignAssets.get_font_path("ascii", "regular")

# Get icon for format
icon = DesignAssets.get_icon("tool", "ascii")  # Returns: ⚒

# Get pattern
pattern = DesignAssets.get_pattern("metal", "svg_tech")  # Returns: crosshatch

# Convert ASCII to Teletext
teletext_entity = DesignAssets.ascii_to_teletext("█")  # Returns: &#xE23F;

# Color conversions
grey = DesignAssets.color_to_greyscale("RED")  # Returns: #555555
```

## Examples

### Generate Water Filter (All Formats)

```bash
python extensions/core/ok-assist/examples/generate_multi_format.py
```

Generates:
- `knowledge/diagrams/ascii/water-filter.txt`
- `knowledge/diagrams/teletext/water-filter.html`
- `knowledge/diagrams/water/water-filter-technical.svg`

### Command Line Usage

```bash
# Generate ASCII diagram
python -m extensions.core.ok_assist.api.gemini "fire triangle" ascii petme

# Generate Teletext graphics
python -m extensions.core.ok_assist.api.gemini "forest map" teletext mosaic

# Generate SVG with auto-detection
python -m extensions.core.ok_assist.api.gemini "human heart" svg auto

# Output: human-heart.svg (auto-detects hand-illustrative style)
```

## Quality Standards

All generated content must meet:

1. **File Size**:
   - ASCII: <10KB
   - Teletext HTML: <50KB
   - SVG: <50KB

2. **Accessibility**:
   - ASCII: Plain text, screen-reader friendly
   - Teletext: Alt text, semantic HTML
   - SVG: `<title>`, `<desc>` elements

3. **Format Standards**:
   - ASCII: UTF-8, PetMe64 compatible, exact dimensions
   - Teletext: Valid HTML5, Unicode entities
   - SVG: Editable text (not paths), valid XML

4. **Visual Quality**:
   - Clear, recognizable shapes
   - Appropriate style for subject
   - Consistent with design system
   - Proper labeling and legends

## Integration

See complete integration guide: [`docs/INTEGRATION.md`](docs/INTEGRATION.md)

### With Existing Diagram Generators

```python
# In dev/tools/generate_medical_diagrams.py
from extensions.core.ok_assist.api.gemini import OKAssist

ok = OKAssist()

# Generate ASCII for terminal
ascii_diagram = ok.generate_ascii("CPR hand position", width=80, height=24)

# Generate Teletext for web
teletext_map = ok.generate_teletext("emergency zones", colors=["RED", "YELLOW", "GREEN"])

# Generate SVG for documentation
svg_diagram = ok.generate_svg("arterial pressure points", style="hand-illustrative")
```

### With Web Extensions

```html
<!-- Include Teletext graphics -->
<link rel="stylesheet" href="/extensions/assets/css/teletext-renderer.css">

<!-- Display Teletext mosaic -->
<iframe src="knowledge/diagrams/teletext/water-filter.html"></iframe>

<!-- Display SVG with styles -->
<link rel="stylesheet" href="/extensions/core/ok-assist/css/technical-kinetic.css">
<object data="knowledge/diagrams/water/filter-system.svg" class="technical-kinetic"></object>
```

## Troubleshooting

### API Key Not Found
```
ValueError: API key required
```
**Solution**: Add `GEMINI_API_KEY` to `.env` file in project root

### Import Error
```
ImportError: google-generativeai not installed
```
**Solution**: `pip install google-generativeai`

### Large File Size
SVG exceeds 50KB target
**Solution**: Reduce complexity level or simplify description

### Style Not Applied
CSS not loading in web view
**Solution**: Check asset paths, verify `/extensions/assets/css/` accessible

## Credits

- **Gemini API**: Google Generative AI
- **C64 PetMe Fonts**: PetMe font family
- **CoreUI Icons**: 1500+ MIT licensed icons
- **Mac OS Patterns**: System 1 bitmap patterns
- **Design System**: Fred Porter

## License

MIT License - See project LICENSE.txt

---

**Last Updated**: November 25, 2025
**Version**: 1.0
**Integration**: System-wide extension
**Assets**: `/extensions/assets/`
