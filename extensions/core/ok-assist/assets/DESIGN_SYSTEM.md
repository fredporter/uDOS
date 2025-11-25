# OK Assist Unified Design System

**System-wide reference linking ASCII art, Teletext graphics, and SVG diagrams**

## Overview

OK Assist generates content in three visual formats with shared design language:

1. **ASCII Art** (mono) - Text-based line art using C64 PetMe font reference
2. **Teletext Graphics** (color) - Block graphics using WST color palette
3. **SVG Diagrams/Sketches** (mono/greyscale) - Technical-Kinetic or Hand-Illustrative styles

All three formats share a common asset library and design vocabulary.

---

## Design Format Matrix

| Format | Colors | Resolution | Font Base | Use Case | Output |
|--------|--------|------------|-----------|----------|--------|
| **ASCII Art** | Mono (black/white) | 80×24 / 40×25 | C64 PetMe | Terminal UI, CLI diagrams | `.txt` |
| **Teletext** | 8-color WST palette | 40×25 / 80×25 | Teletext mosaic | Web rendering, maps | `.html` |
| **SVG Tech** | Mono + patterns | Scalable vector | Chicago/Geneva | Tools, systems, UI | `.svg` |
| **SVG Organic** | Mono/greyscale | Scalable vector | Geneva serif | Anatomy, nature, food | `.svg` |

---

## Shared Asset Library

### Character Set Reference: C64 PetMe

**Base Font**: `/extensions/assets/fonts/petme/PetMe64.ttf`

The C64 PetMe font family provides the foundational character set for all formats:

```
petme/
├── PetMe64.ttf       # Standard C64 8×8 characters
├── PetMe128.ttf      # C128 extended set
├── PetMe2X.ttf       # Double-width (16×8)
├── PetMe2Y.ttf       # Double-height (8×16)
├── PetMe1282Y.ttf    # C128 double-height
├── PetMe642Y.ttf     # C64 double-height
└── README.md
```

**Character Categories**:
- **0x00-0x1F**: Control chars, UI elements
- **0x20-0x7F**: Standard ASCII (letters, numbers, symbols)
- **0x80-0x9F**: Graphical elements (lines, corners, blocks)
- **0xA0-0xFF**: PETSCII graphics (extended blocks, patterns)

### Block Graphics (Teletext + ASCII)

**Teletext Mosaic Blocks** (2×3 pixel matrix):
```
Unicode E200-E23F (contiguous mosaic)
Unicode E240-E27F (separated mosaic)

Each char = 6 bits (TL, TR, ML, MR, BL, BR)
Example: E23F = ██ (full block)
         E215 = █░ (left half)
         E203 = ▀▀ (top half)
```

**ASCII/PETSCII Block Chars**:
```
Full blocks:  █ ▓ ▒ ░
Half blocks:  ▀ ▄ ▌ ▐
Quarter:      ▘ ▝ ▖ ▗
Shades:       ░ (25%) ▒ (50%) ▓ (75%) █ (100%)
```

**Mapping**:
```python
# Teletext → ASCII equivalents
TELETEXT_TO_ASCII = {
    'E23F': '█',  # Full block
    'E215': '▌',  # Left half
    'E22A': '▐',  # Right half
    'E203': '▀',  # Top half
    'E230': '▄',  # Bottom half
    'E221': '▘',  # Top-left quarter
    # ... 64 total mappings
}
```

### Color Palette System

**Teletext WST Colors** (8 colors):
```css
--teletext-black:   #000000;
--teletext-red:     #FF0000;
--teletext-green:   #00FF00;
--teletext-yellow:  #FFFF00;
--teletext-blue:    #0000FF;
--teletext-magenta: #FF00FF;
--teletext-cyan:    #00FFFF;
--teletext-white:   #FFFFFF;
```

**SVG Greyscale Mapping**:
```css
/* Map Teletext colors to greyscale values */
--svg-black:   #000000;  /* BLACK → 0% */
--svg-grey-12: #1F1F1F;  /* BLUE → 12% */
--svg-grey-25: #3F3F3F;  /* RED/MAGENTA → 25% */
--svg-grey-50: #7F7F7F;  /* GREEN/CYAN → 50% */
--svg-grey-75: #BFBFBF;  /* YELLOW → 75% */
--svg-white:   #FFFFFF;  /* WHITE → 100% */
```

**C64 Color to Greyscale**:
```css
/* 16-color C64 palette → mono */
--c64-black:      #000000 → #000;
--c64-white:      #FFFFFF → #FFF;
--c64-red:        #880000 → #333;
--c64-cyan:       #AAFFEE → #BBB;
--c64-purple:     #CC44CC → #555;
--c64-green:      #00CC55 → #777;
--c64-blue:       #0000AA → #222;
--c64-yellow:     #EEEE77 → #CCC;
--c64-orange:     #DD8855 → #888;
--c64-brown:      #664400 → #444;
--c64-light-red:  #FF7777 → #999;
--c64-dark-grey:  #333333 → #333;
--c64-grey:       #777777 → #777;
--c64-light-green:#AAFF66 → #AAA;
--c64-light-blue: #0088FF → #666;
--c64-light-grey: #BBBBBB → #BBB;
```

### Typography Hierarchy

**ASCII/Terminal** (80×24):
```
Headings:  ALL CAPS, ═══ underline, PetMe64
Body:      Mixed case, PetMe64
Mono:      Code blocks, PetMe64
Emphasis:  *asterisks*, _underscores_
```

**Teletext** (40×25):
```
Titles:    DOUBLE HEIGHT (2Y variants)
Headings:  ALL CAPS, WST colors
Body:      Mixed case, standard mosaic font
Labels:    Small caps, contiguous mosaic
```

**SVG Technical-Kinetic**:
```
Titles:    Chicago 12pt bold
Labels:    Geneva 9pt
Body:      Geneva 9pt regular
Mono:      Monaco 9pt (measurements, code)
Icons:     CoreUI 16×16 or 24×24
```

**SVG Hand-Illustrative**:
```
Titles:    Geneva 14pt italic bold
Labels:    Geneva 10pt regular
Body:      Geneva 10pt regular
Captions:  Geneva 8pt italic
Scientific: Geneva 10pt (genus/species)
```

---

## Pattern & Texture Library

### ASCII Patterns

**Lines** (from PetMe):
```
Horizontal:  ─ ━ ═ ⎯
Vertical:    │ ┃ ║ ⎪
Diagonal:    / \ ╱ ╲
Corners:     ┌ ┐ └ ┘ ╔ ╗ ╚ ╝
Junctions:   ┼ ╋ ├ ┤ ┬ ┴
```

**Fill Patterns**:
```
Solid:   ████████████
Dense:   ▓▓▓▓▓▓▓▓▓▓▓▓
Medium:  ▒▒▒▒▒▒▒▒▒▒▒▒
Light:   ░░░░░░░░░░░░
Dots:    ·.·.·.·.·.·.
Hatch:   ////\/\/\/\/
Cross:   ╳╳╳╳╳╳╳╳╳╳╳╳
```

### Teletext Mosaic Patterns

**Solid Fills**:
```html
<!-- Full blocks -->
<span class="bg-red">&#xE23F;&#xE23F;&#xE23F;</span>

<!-- Checkerboard -->
<span class="bg-white">&#xE215;&#xE22A;&#xE215;</span>

<!-- Gradients (density variation) -->
<span class="bg-black">&#xE200;</span>  <!-- 0% -->
<span class="bg-blue">&#xE215;</span>   <!-- 25% -->
<span class="bg-green">&#xE233;</span>  <!-- 50% -->
<span class="bg-yellow">&#xE22A;</span> <!-- 75% -->
<span class="bg-white">&#xE23F;</span>  <!-- 100% -->
```

**Textures**:
```
Brick:    ██ ██  / ██ ██
Dots:     ▘ ▝ / ▖ ▗ (alternating)
Diagonal: ▗ ▖ / ▝ ▘ (stepped)
Wave:     ▀▄▀▄▀▄
Grass:    ▒░▓░▒░▓
```

### SVG Mac OS System 1 Patterns

**Bitmap Patterns** (8×8 pixel):
```xml
<!-- Gray-12 (light) -->
<pattern id="gray-12" patternUnits="userSpaceOnUse" width="8" height="8">
  <rect width="8" height="8" fill="#fff"/>
  <circle cx="2" cy="2" r="0.5" fill="#000"/>
  <circle cx="6" cy="6" r="0.5" fill="#000"/>
</pattern>

<!-- Gray-50 (medium checkerboard) -->
<pattern id="gray-50" patternUnits="userSpaceOnUse" width="8" height="8">
  <rect width="8" height="8" fill="#fff"/>
  <rect x="0" y="0" width="4" height="4" fill="#000"/>
  <rect x="4" y="4" width="4" height="4" fill="#000"/>
</pattern>

<!-- Crosshatch -->
<pattern id="crosshatch" patternUnits="userSpaceOnUse" width="8" height="8">
  <line x1="0" y1="0" x2="8" y2="8" stroke="#000" stroke-width="0.3"/>
  <line x1="8" y1="0" x2="0" y2="8" stroke="#000" stroke-width="0.3"/>
</pattern>

<!-- Diagonal stripes -->
<pattern id="diagonal" patternUnits="userSpaceOnUse" width="8" height="8">
  <line x1="0" y1="8" x2="8" y2="0" stroke="#000" stroke-width="0.5"/>
</pattern>
```

### SVG Organic Textures

**Natural Patterns**:
```xml
<!-- Woodgrain -->
<path d="M0,10 Q20,8 40,10 Q60,12 80,10" stroke="#000" stroke-width="0.4" fill="none"/>

<!-- Water ripples -->
<ellipse cx="50" cy="50" rx="10" ry="8" stroke="#000" stroke-width="0.3" fill="none"/>
<ellipse cx="50" cy="50" rx="20" ry="16" stroke="#000" stroke-width="0.3" opacity="0.6" fill="none"/>

<!-- Stipple (density shading) -->
<circle cx="10" cy="10" r="0.4" fill="#000"/>
<circle cx="15" cy="12" r="0.4" fill="#000"/>
<!-- Denser = more circles -->

<!-- Cross-contour (form following) -->
<path d="M0,0 Q10,5 20,0" stroke="#000" stroke-width="0.4" fill="none"/>
<path d="M0,5 Q10,10 20,5" stroke="#000" stroke-width="0.4" fill="none"/>
```

---

## Icon & Symbol System

### CoreUI Icons (Technical-Kinetic SVG)

**1500+ icons** from `/extensions/assets/icons/coreui/`:

**Categories**:
```
Tools:      cil-wrench, cil-hammer, cil-screwdriver
UI:         cil-menu, cil-settings, cil-chevron-*
Indicators: cil-warning, cil-check-circle, cil-x-circle
Navigation: cil-arrow-*, cil-compass, cil-map
Medical:    cil-medical-cross, cil-heart, cil-pulse
Nature:     cil-sun, cil-cloud, cil-fire, cil-drop
```

**Usage in SVG**:
```xml
<!-- Import CoreUI icon -->
<use href="/extensions/assets/icons/coreui/svg/free/cil-wrench.svg#icon"
     x="10" y="10" width="24" height="24"/>
```

### Teletext UI Blocks

**From `core/ui/teletext_prompt.py`**:
```python
# Selection indicators
SELECTED = '◉'      # Filled circle
UNSELECTED = '○'    # Empty circle
CHECKBOX_ON = '☑'   # Checked box
CHECKBOX_OFF = '☐'  # Empty box

# Arrows
ARROW_RIGHT = '→'
ARROW_LEFT = '←'
POINTER = '►'

# Status
SUCCESS = '✓'
ERROR = '✗'
WARNING = '⚠'
```

### ASCII Art Icons

**From PetMe PETSCII set**:
```
Hearts:  ♥ ♡
Stars:   ★ ☆
Arrows:  ← ↑ → ↓ ↖ ↗ ↘ ↙
Boxes:   ☐ ☑ ☒
Circles: ○ ◉ ◯ ●
Music:   ♪ ♫ ♬
Cards:   ♠ ♣ ♥ ♦
Chess:   ♔ ♕ ♖ ♗ ♘ ♙
```

---

## Format Conversion System

### Teletext → ASCII

```python
def teletext_to_ascii(teletext_html: str) -> str:
    """Convert Teletext mosaic blocks to ASCII art"""

    MOSAIC_MAP = {
        '&#xE200;': ' ',   # Empty
        '&#xE23F;': '█',   # Full
        '&#xE215;': '▌',   # Left half
        '&#xE22A;': '▐',   # Right half
        '&#xE203;': '▀',   # Top half
        '&#xE230;': '▄',   # Bottom half
        '&#xE233;': '▄▀',  # Corners
        '&#xE20C;': '▀▄',  # Sides
        # ... complete 64-char mapping
    }

    # Strip HTML, map mosaics, preserve layout
    ascii_art = parse_teletext_html(teletext_html)
    for mosaic, ascii_char in MOSAIC_MAP.items():
        ascii_art = ascii_art.replace(mosaic, ascii_char)

    return ascii_art
```

### ASCII → SVG

```python
def ascii_to_svg(ascii_art: str, style: str = "technical-kinetic") -> str:
    """Convert ASCII art diagram to SVG"""

    lines = ascii_art.split('\n')
    width = max(len(line) for line in lines) * 8  # 8px per char
    height = len(lines) * 12  # 12px per line

    svg = f'<svg viewBox="0 0 {width} {height}" xmlns="http://www.w3.org/2000/svg">\n'
    svg += f'<style>@import url("/extensions/assets/fonts/petme/petme.css");</style>\n'
    svg += '<g font-family="PetMe64" font-size="12">\n'

    for y, line in enumerate(lines):
        for x, char in enumerate(line):
            if char != ' ':
                svg += f'<text x="{x*8}" y="{y*12+10}">{char}</text>\n'

    svg += '</g>\n</svg>'
    return svg
```

### SVG → Teletext (Rasterization)

```python
def svg_to_teletext(svg_path: str, width: int = 40, height: int = 25) -> str:
    """Rasterize SVG to Teletext mosaic blocks"""

    # 1. Render SVG to bitmap (2×3 pixel cells)
    bitmap = rasterize_svg(svg_path, width*2, height*3)

    # 2. Map 2×3 pixel regions to mosaic chars
    teletext = []
    for y in range(height):
        row = []
        for x in range(width):
            # Sample 2×3 pixel region
            region = bitmap[y*3:(y+1)*3, x*2:(x+1)*2]
            # Convert to 6-bit pattern
            mosaic = bitmap_to_mosaic(region)
            row.append(f'&#xE{mosaic:03X};')
        teletext.append(''.join(row))

    return '\n'.join(teletext)
```

---

## Generation Workflows

### 1. Generate ASCII Art

```python
from extensions.core.ok_assist.api.gemini import OKAssist

ok = OKAssist()

ascii_art = ok.generate_ascii(
    subject="water filter",
    description="DIY multi-layer gravel/sand/charcoal filter",
    width=80,
    height=24,
    style="petme"  # Use C64 PetMe character set
)

# Output to terminal or file
print(ascii_art)
with open('knowledge/diagrams/ascii/water-filter.txt', 'w') as f:
    f.write(ascii_art)
```

### 2. Generate Teletext Graphics

```python
teletext_html = ok.generate_teletext(
    subject="forest map",
    description="Topographic map with trees, water, elevation contours",
    width=40,
    height=25,
    colors=["GREEN", "BLUE", "BROWN"],  # WST color palette
    style="mosaic"  # Use 2×3 mosaic blocks
)

# Output to web extension
with open('extensions/web/maps/forest-map.html', 'w') as f:
    f.write(teletext_html)
```

### 3. Generate SVG Diagram

```python
# Technical diagram
svg_tech = ok.generate_svg(
    subject="bow saw construction",
    description="Frame, blade, tension cord with measurements",
    style="technical-kinetic",
    complexity="moderate"
)

# Organic illustration
svg_organic = ok.generate_svg(
    subject="oak leaf anatomy",
    description="Leaf structure with veins, petiole, blade detail",
    style="hand-illustrative",
    complexity="detailed"
)
```

### 4. Cross-Format Generation

```python
# Generate all three formats from single description
subject = "campfire structure"
description = "Log cabin fire lay with tinder bundle, kindling, fuel wood"

# ASCII for CLI
ascii_diagram = ok.generate_ascii(subject, description, width=80, height=24)

# Teletext for web map
teletext_map = ok.generate_teletext(subject, description, width=40, height=25,
                                     colors=["RED", "YELLOW", "BROWN"])

# SVG for print/high-res
svg_diagram = ok.generate_svg(subject, description,
                               style="technical-kinetic", complexity="moderate")

# Save all formats
save_diagram(ascii_diagram, 'knowledge/diagrams/ascii/fire-structure.txt')
save_diagram(teletext_map, 'knowledge/diagrams/teletext/fire-structure.html')
save_diagram(svg_diagram, 'knowledge/diagrams/fire/fire-structure.svg')
```

---

## Style Translation Rules

### ASCII → Teletext

| ASCII Element | Teletext Equivalent | Notes |
|---------------|---------------------|-------|
| `█` (full block) | `&#xE23F;` (full mosaic) | 1:1 mapping |
| `▀` (top half) | `&#xE203;` (top mosaic) | Direct conversion |
| `─` (line) | `─` or mosaic pattern | Keep or convert |
| Colors | WST palette | Map greyscale to colors |
| 80×24 layout | 40×25 layout | Scale down 2:1 |

### ASCII → SVG

| ASCII Element | SVG Technical | SVG Organic | Notes |
|---------------|---------------|-------------|-------|
| Box chars `┌─┐` | Geometric `<rect>` | Rounded corners | Lines become vectors |
| Fill `▓▓▓` | Pattern `gray-50` | Stipple/hatch | Convert to texture |
| Text labels | Geneva 9pt | Geneva 10pt | Font upgrade |
| Icons `♥ ★` | CoreUI icons | Hand-drawn | Symbol replacement |
| Arrows `→` | CoreUI `cil-arrow-right` | Curved path | Style-appropriate |

### Teletext → SVG

| Teletext Element | SVG Technical | SVG Organic | Notes |
|------------------|---------------|-------------|-------|
| Mosaic `&#xE23F;` | Filled `<rect>` | Textured region | Vectorize blocks |
| RED color | Gray-25 pattern | Medium stipple | Color to greyscale |
| YELLOW color | Gray-75 pattern | Light hatch | Brightness mapping |
| Double height | Scaled text | Bold italic | Size adjustment |
| Contiguous mode | Solid fills | Dense texture | Style translation |

---

## Asset Cross-Reference

### Font Mapping

| Format | Primary Font | Fallback | Size | Path |
|--------|--------------|----------|------|------|
| ASCII | PetMe64 | Monaco | 8×8 | `/assets/fonts/petme/PetMe64.ttf` |
| Teletext | Teletext Mosaic | PetMe64 | 12×20 | Built-in HTML entity |
| SVG Tech | Chicago/Geneva | Monaco | 9-12pt | `/assets/fonts/ChiKareGo2.woff2` |
| SVG Organic | Geneva Serif | Georgia | 10-14pt | `/assets/fonts/FindersKeepers.woff2` |

### Icon Mapping

| Concept | ASCII | Teletext | SVG Technical | SVG Organic |
|---------|-------|----------|---------------|-------------|
| Tool | `⚒` | `&#xE23F;` RED | `cil-wrench` | Hand-drawn tool |
| Check | `✓` | `☑` | `cil-check-circle` | Checkmark path |
| Warning | `⚠` | `⚠` YELLOW | `cil-warning` | Exclamation |
| Arrow | `→` | `►` | `cil-arrow-right` | Curved arrow |
| Heart | `♥` | `♥` RED | `cil-heart` | Anatomical heart |
| Tree | `🌲` | `▲` GREEN | `cil-tree` (custom) | Oak/pine sketch |

### Pattern Mapping

| Texture | ASCII Pattern | Teletext Mosaic | SVG Tech Pattern | SVG Organic |
|---------|---------------|-----------------|------------------|-------------|
| Solid | `████` | `&#xE23F;` × N | `gray-87` | Solid fill |
| Metal | `▓▓▓▓` | Separated mosaic | `crosshatch` | Parallel lines |
| Wood | `≡≡≡≡` | `─` pattern | `diagonal` | Woodgrain curves |
| Water | `≈≈≈≈` | Blue waves | `horizontal` | Ripple ellipses |
| Grass | `∴∴∴∴` | Green dots | `dots` | Wavy parallel |
| Stone | `▒▒▒▒` | Grey checkerboard | `gray-50` | Crack lines |

---

## Implementation

### Unified Generator API

```python
class OKAssist:
    """Unified content generation across all formats"""

    def generate(self,
                 subject: str,
                 description: str,
                 format: Literal["ascii", "teletext", "svg"],
                 style: Optional[str] = None,
                 **kwargs) -> str:
        """
        Generate diagram in specified format

        Args:
            subject: What to draw
            description: Details
            format: "ascii", "teletext", or "svg"
            style: Format-specific style
                   - ascii: "petme", "box-drawing", "minimal"
                   - teletext: "mosaic", "contiguous", "separated"
                   - svg: "technical-kinetic", "hand-illustrative"
            **kwargs: Format-specific parameters

        Returns:
            Generated content (string)
        """
        if format == "ascii":
            return self.generate_ascii(subject, description,
                                       style=style or "petme", **kwargs)
        elif format == "teletext":
            return self.generate_teletext(subject, description,
                                          style=style or "mosaic", **kwargs)
        elif format == "svg":
            return self.generate_svg(subject, description,
                                     style=style or self.auto_detect_style(subject),
                                     **kwargs)
        else:
            raise ValueError(f"Unknown format: {format}")

    def generate_all_formats(self, subject: str, description: str) -> Dict[str, str]:
        """Generate ASCII, Teletext, and SVG from single description"""
        return {
            "ascii": self.generate_ascii(subject, description, width=80, height=24),
            "teletext": self.generate_teletext(subject, description, width=40, height=25),
            "svg_technical": self.generate_svg(subject, description, style="technical-kinetic"),
            "svg_organic": self.generate_svg(subject, description, style="hand-illustrative")
        }
```

### Shared Asset Manager

```python
class DesignAssets:
    """Centralized asset management for all formats"""

    ASSETS_ROOT = Path("/extensions/assets")

    @classmethod
    def get_font_path(cls, format: str, variant: str = "regular") -> Path:
        """Get font file path for format"""
        font_map = {
            "ascii": "petme/PetMe64.ttf",
            "teletext": "petme/PetMe2Y.ttf",  # Double-height
            "svg_tech": "ChiKareGo2.woff2",
            "svg_organic": "FindersKeepers.woff2"
        }
        return cls.ASSETS_ROOT / "fonts" / font_map[format]

    @classmethod
    def get_icon(cls, concept: str, format: str) -> str:
        """Get icon representation for concept in format"""
        icon_map = {
            "tool": {
                "ascii": "⚒",
                "teletext": "&#xE23F;",
                "svg": "cil-wrench"
            },
            # ... complete icon mapping
        }
        return icon_map.get(concept, {}).get(format, "")

    @classmethod
    def get_pattern(cls, texture: str, format: str) -> str:
        """Get pattern/texture for format"""
        # Return pattern definition or reference
        pass
```

---

## Quality Standards

All formats must meet:

1. **Resolution**: Appropriate for target display
   - ASCII: 80×24 (standard) or 40×25 (C64)
   - Teletext: 40×25 (standard) or 80×25 (extended)
   - SVG: Scalable vector (target 800×600 viewport)

2. **File Size**:
   - ASCII: <10KB
   - Teletext HTML: <50KB
   - SVG: <50KB

3. **Accessibility**:
   - ASCII: Plain text, screen-reader friendly
   - Teletext: Alt text, semantic HTML
   - SVG: `<title>`, `<desc>` elements, ARIA labels

4. **Character Set**:
   - ASCII: UTF-8, PetMe64 compatible
   - Teletext: Unicode mosaic entities (E200-E27F)
   - SVG: UTF-8 text (not paths), editable

5. **Color/Contrast**:
   - ASCII: High contrast mono
   - Teletext: WST 8-color palette
   - SVG: Mono or greyscale patterns

---

**Last Updated**: November 25, 2025
**OK Assist Version**: 1.0
**Asset Library**: `/extensions/assets/`
