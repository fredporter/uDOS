# Mac OS System 1 Pattern Library Guide

## Overview

The uDOS SVG diagram system now uses **Mac OS System 1 classic bitmap patterns** - bold, geometric 8×8 pixel patterns that create the distinctive monochrome aesthetic of early Macintosh computers (1984).

This pattern library provides:
- **17 total patterns**: 7 grayscale tones + 10 texture patterns
- **Pixel-perfect 8×8 bitmap style**: Sharp, geometric, no anti-aliasing
- **Generic monospace fonts**: No external dependencies
- **Bold stroke weights**: 2-3px for primary lines (Mac OS aesthetic)
- **Monochrome palette**: Solid grays (#1A1A1A-#E6E6E6) and bitmap patterns both supported

---

## Pattern Catalog

### UI Components (System.css)

**Interface Elements** (based on Apple HI Guidelines 1984-1991):

Available via `macos_ui_components.py`:
- **Buttons**: Standard (59×20px), default (thick border), disabled (gray text), active (inverted)
- **Windows**: Title bar (19px), close box, racing stripes, details bar, content pane
- **Dialogs**: Modal (double border), modeless (like window), standard (single border)
- **Alert Boxes**: Icon space (32×32px), message text, button array
- **Checkboxes**: 12×12px square with checkmark
- **Radio Buttons**: 12px circle with inner fill
- **Text Boxes**: 16px height input fields
- **Menu Bars**: 20px height with menu items

**Design Constants**:
- Button border radius: 8px
- Title bar height: 19px
- Window border: 1px single / 2px modal double
- Fonts: Chicago 12pt (title), Geneva 9pt (body) → monospace simulation

### Grayscale Options

**Solid Grays (9 levels):**
- `#1A1A1A` (90% black) - Very dark shadows
- `#333333` (80% black) - Dark structural elements
- `#4D4D4D` (70% black) - Medium-dark fills
- `#666666` (60% black) - Medium gray
- `#808080` (50% gray) - Mid-tone
- `#999999` (40% gray) - Light-medium
- `#B3B3B3` (30% gray) - Light fills
- `#CCCCCC` (20% gray) - Very light
- `#E6E6E6` (10% gray) - Subtle backgrounds

**Bitmap Patterns (7 patterns):**
Pattern-based toning using bitmap density for texture effects:

| Pattern | Density | Usage | Visual |
|---------|---------|-------|--------|
| **white** | 0% | Backgrounds, empty areas, highlights | `#FFF` |
| **gray-12** | 12.5% | Very light tint, subtle highlights | `▫` |
| **gray-25** | 25% | Light backgrounds, soft shading | `▫▪` |
| **gray-37** | 37.5% | Light-medium tone, gentle gradients | `▫▪▪` |
| **gray-50** | 50% | Balanced mid-tone, neutral areas | `▪▫▪▫` |
| **gray-62** | 62.5% | Medium-dark shading | `▪▪▫` |
| **gray-75** | 75% | Dark backgrounds, heavy shadows | `▪▪▫` |
| **gray-87** | 87.5% | Very dark, near-black areas | `▪` |
| **black** | 100% | Solid black, high contrast elements | `#000` |

**Technical Implementation:**
```xml
<!-- 25% gray - Checkerboard sparse -->
<pattern id="gray-25" patternUnits="userSpaceOnUse" width="4" height="4">
  <rect width="4" height="4" fill="#FFF"/>
  <rect x="0" y="0" width="2" height="2" fill="#000"/>
  <rect x="2" y="2" width="2" height="2" fill="#000"/>
</pattern>

<!-- 50% gray - Dense checkerboard -->
<pattern id="gray-50" patternUnits="userSpaceOnUse" width="2" height="2">
  <rect width="2" height="2" fill="#FFF"/>
  <rect x="0" y="0" width="1" height="1" fill="#000"/>
  <rect x="1" y="1" width="1" height="1" fill="#000"/>
</pattern>
```

---

### Texture Patterns (10 patterns)

Bold geometric patterns for material representation:

#### **brick**
- **Use:** Masonry, stone walls, structural building
- **Style:** Offset rectangular blocks
- **Density:** Medium-bold
```
┌─┬─┐
├─┼─┤
└─┴─┘
```

#### **diagonal**
- **Use:** Directional flow, structural elements, metal surfaces
- **Style:** Bold diagonal lines (45°)
- **Density:** Medium
```
╲   ╲
 ╲   ╲
  ╲   ╲
```

#### **cross-hatch**
- **Use:** Very dense materials, cast iron, metal grilles
- **Style:** Bold grid pattern (horizontal + vertical)
- **Density:** Heavy
```
┼┼┼┼
┼┼┼┼
┼┼┼┼
```

#### **horizontal**
- **Use:** Layered materials, stratification, sediment layers
- **Style:** Bold horizontal bars
- **Density:** Medium-heavy
```
████

████
```

#### **vertical**
- **Use:** Wood grain, columnar structures, vertical barriers
- **Style:** Bold vertical bars
- **Density:** Medium-heavy
```
█ █ █
█ █ █
█ █ █
```

#### **dots**
- **Use:** Soft materials, skin, clouds, atmospheric effects
- **Style:** Regular dot grid
- **Density:** Medium-light
```
• • •
• • •
• • •
```

#### **scales**
- **Use:** Fish scales, roof tiles, armor, overlapping protective layers
- **Style:** Interlocking semicircle arcs
- **Density:** Medium
```
⌒⌒⌒
 ⌒⌒
⌒⌒⌒
```

#### **grid**
- **Use:** Technical drawings, measurement grids, coordinates
- **Style:** Single-pixel grid lines
- **Density:** Light structural
```
┌─┬─┐
├─┼─┤
└─┴─┘
```

#### **waves**
- **Use:** Water, organic flow, undulating surfaces
- **Style:** Blocky wave pattern
- **Density:** Medium
```
 ▄▀
▀  ▄
  ▀
```

#### **herringbone**
- **Use:** Decorative elements, fancy textiles, premium materials
- **Style:** Zigzag weave
- **Density:** Complex
```
╲ ╱
 ╳
╱ ╲
```

---

## Material Mapping Guide

### Structural & Mechanical

| Material | Primary Pattern | Alternative | Example Use |
|----------|----------------|-------------|-------------|
| Metal/tools | `cross-hatch` | `diagonal` | Tools, gears, machinery |
| Stone/masonry | `brick` | `scales` | Walls, foundations |
| Wood/timber | `vertical` | `horizontal` | Boards, planks, posts |
| Concrete | `gray-50` | `gray-62` | Buildings, slabs |
| Glass | `white` | `gray-12` | Windows, containers |

### Organic & Natural

| Material | Primary Pattern | Alternative | Example Use |
|----------|----------------|-------------|-------------|
| Skin/flesh | `dots` (light) | `gray-25` | Human body, animals |
| Fabric/cloth | `herringbone` | `grid` | Bandages, clothing |
| Water (still) | `gray-37` | `gray-25` | Containers, lakes |
| Water (flowing) | `waves` | `diagonal` | Rivers, streams |
| Vegetation | `dots` | `gray-50` | Leaves, grass |
| Soil/dirt | `gray-50` | `dots` | Ground, earth |

### Layered Materials (Filters, Barriers)

**Water Filter Example:**
```
Cloth filter    → cross-hatch (fine mesh)
Charcoal layer  → gray-75 (dense, dark)
Sand layer      → gray-37 (medium density)
Gravel layer    → dots (coarse particles)
```

**Wound Dressing Example:**
```
Bandage        → herringbone (woven fabric)
Gauze pad      → grid (loose weave)
Skin surface   → dots (organic texture)
Bleeding area  → gray-50 or gray-62
```

---

## Design Guidelines

### Typography

**Generic Monospace Font:**
```xml
<text font-family="monospace" font-size="14" font-weight="bold">
  Title Text
</text>
```

**Text Sizing (Bold Mac OS Style):**
- Title/Header: 18-28px, `font-weight="bold"`
- Section Labels: 14-16px, `font-weight="bold"`
- Body/Descriptions: 11-13px
- Annotations/Notes: 9-11px

### Line Weights

**Bold strokes (Mac OS aesthetic):**
- Primary outlines: `stroke-width="2"` or `"3"`
- Secondary details: `stroke-width="1.5"`
- Fine details: `stroke-width="1"`
- Pattern lines: Built into 8×8 bitmap patterns

### Color Palette

**MONOCHROME PALETTE:**
```xml
<!-- Correct usage -->
<rect fill="#000" />              <!-- Solid black -->
<rect fill="#FFF" />              <!-- Solid white -->
<rect fill="#666" />              <!-- Solid gray -->
<rect fill="url(#gray-50)" />    <!-- Pattern-based gray -->

<!-- Examples of solid grays -->
<rect fill="#1A1A1A" />           ✓ Very dark (90% black)
<rect fill="#808080" />           ✓ Mid-tone (50% gray)
<rect fill="#E6E6E6" />           ✓ Light (10% gray)
```

---

## Mac OS System 1 Design Philosophy

### Bold & Clear
- Use thick stroke weights (2-3px for main lines)
- High contrast between elements
- Clear separation between components
- No subtle anti-aliasing - sharp pixel-perfect edges

### Pattern Density
- Use grayscale patterns for tonal variation
- Texture patterns for material identification
- Never mix more than 2 pattern types in close proximity
- Maintain white space for clarity

### Pixel-Perfect Precision
- Align elements to whole pixel boundaries when possible
- Use 8×8 pattern grid as spacing guide
- Keep layout geometric and grid-based
- Sharp corners preferred over rounded

### Visual Hierarchy

**Primary subject:**
- Bold 2-3px outlines
- Detailed pattern fills
- High contrast with background

**Secondary elements:**
- 1.5px lines
- Lighter pattern density
- Subdued contrast

**Background:**
- Very light patterns (`gray-12`, `gray-25`)
- Pure white for maximum clarity

**Annotations:**
- 1px leader lines
- Minimal pattern interference
- Monospace font for technical precision

---

## Code Examples

### Basic Shape with Pattern

```xml
<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 400 300" width="400" height="300">
  <defs>
    <!-- Include pattern library -->
  </defs>

  <!-- Container with brick pattern -->
  <rect x="50" y="50" width="300" height="200"
        fill="url(#brick)"
        stroke="#000"
        stroke-width="3"/>

  <!-- Water inside with gray pattern -->
  <rect x="50" y="150" width="300" height="100"
        fill="url(#gray-37)"
        stroke="#000"
        stroke-width="2"/>

  <!-- Label -->
  <text x="200" y="30"
        font-family="monospace"
        font-size="16"
        font-weight="bold"
        text-anchor="middle"
        fill="#000">
    Water Container
  </text>
</svg>
```

### Multi-Layer Filter Diagram

```xml
<!-- Gravel layer (bottom) -->
<rect x="100" y="300" width="200" height="60"
      fill="url(#dots)"
      stroke="#000"
      stroke-width="2"/>
<text x="20" y="330" font-family="monospace" font-size="11" fill="#000">Gravel</text>

<!-- Sand layer -->
<rect x="100" y="220" width="200" height="80"
      fill="url(#gray-37)"
      stroke="#000"
      stroke-width="2"/>
<text x="20" y="260" font-family="monospace" font-size="11" fill="#000">Sand</text>

<!-- Charcoal layer -->
<rect x="100" y="150" width="200" height="70"
      fill="url(#gray-75)"
      stroke="#000"
      stroke-width="2"/>
<text x="20" y="185" font-family="monospace" font-size="11" fill="#000">Charcoal</text>

<!-- Cloth filter (top) -->
<rect x="100" y="130" width="200" height="20"
      fill="url(#cross-hatch)"
      stroke="#000"
      stroke-width="2"/>
<text x="20" y="140" font-family="monospace" font-size="11" fill="#000">Cloth</text>
```

---

## Pattern Selection Decision Tree

```
START: What material/effect do I need?

├─ Is it a structural solid?
│  ├─ Metal/mechanical? → cross-hatch or diagonal
│  ├─ Stone/masonry? → brick or scales
│  └─ Wood/timber? → vertical or horizontal
│
├─ Is it a soft/organic material?
│  ├─ Skin/flesh? → dots (light) or gray-25
│  ├─ Fabric/textile? → herringbone or grid
│  └─ Vegetation? → dots or gray-50
│
├─ Is it a fluid/flow?
│  ├─ Still water? → gray-37 or gray-25
│  ├─ Flowing water? → waves
│  └─ Air/wind? → diagonal (directional)
│
├─ Is it a tonal variation (shadow/highlight)?
│  ├─ Very light? → gray-12 or gray-25
│  ├─ Mid-tone? → gray-37 or gray-50
│  ├─ Dark? → gray-62 or gray-75
│  └─ Very dark? → gray-87 or black
│
└─ Is it a technical element?
   ├─ Grid/measurement? → grid
   ├─ Dense barrier? → cross-hatch
   └─ Decorative? → herringbone or scales
```

---

## File Size Optimization

**Target: <50KB per SVG**

**Tips:**
1. Pattern definitions are reusable - define once in `<defs>`
2. Use pattern IDs repeatedly: `fill="url(#gray-50)"`
3. Avoid unnecessary decimal precision: `x="100"` not `x="100.123456"`
4. Combine shapes when possible
5. Round coordinates to whole pixels

**Example Optimized SVG:**
```xml
<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 800 600">
  <defs>
    <!-- 17 patterns = ~8KB -->
  </defs>

  <!-- Diagram content = ~6KB -->
  <!-- Total: ~14KB (well under 50KB limit) -->
</svg>
```

---

## Accessibility

**Required Elements:**
```xml
<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 800 600">
  <title>Water Filter Multi-Barrier System</title>
  <desc>Cross-section diagram showing four-layer filtration: cloth, charcoal, sand, and gravel layers from top to bottom</desc>

  <!-- Diagram content -->
</svg>
```

**Text Guidelines:**
- All text must be `<text>` elements (screen-reader accessible)
- Never convert text to paths
- Use descriptive labels
- Maintain reading order (top to bottom, left to right)

---

## Tools & Resources

**Generator Script:**
```bash
# Generate diagram using Mac OS patterns
python dev/tools/generate_svg_diagram.py "water filter cross-section" water

# Test pattern library
python dev/tools/test_creative_patterns.py
```

**Pattern Library Location:**
- Pattern definitions: `dev/tools/generate_svg_diagram.py` (lines 22-185)
- Test generator: `dev/tools/test_creative_patterns.py`
- Example output: `knowledge/diagrams/fire/pattern-library-test-creative.svg`

**Reference:**
- Original Mac OS patterns: https://paulsmith.github.io/classic-mac-patterns/
- Frontend Masters blog: https://frontendmasters.com/blog/classic-mac-os-system-1-patterns/

---

## Version History

**v2.0 (November 2025)** - Mac OS System 1 Patterns
- Replaced woodcut/engraving patterns with 8×8 bitmap patterns
- Generic monospace fonts (no external dependencies)
- Bold stroke weights (2-3px)
- 17 total patterns (7 grayscale + 10 texture)
- Pixel-perfect geometric aesthetic

**v1.0 (November 2025)** - Creative Patterns
- Woodcut/engraving artistic patterns
- Mallard font family
- Fine line weights (0.3-1.5px)
- 21 patterns (7 grayscale + 5 basic + 9 creative)

---

## Quick Reference Card

```
GRAYSCALE:           TEXTURES:
gray-12  (12%)      brick        (masonry)
gray-25  (25%)      diagonal     (direction)
gray-37  (37%)      cross-hatch  (dense metal)
gray-50  (50%)      horizontal   (layers)
gray-62  (62%)      vertical     (wood grain)
gray-75  (75%)      dots         (soft/organic)
gray-87  (87.5%)    scales       (organic)
black    (100%)     grid         (technical)
white    (0%)       waves        (water/flow)
                    herringbone  (decorative)

UI COMPONENTS (system.css):
Buttons:     59×20px, 8px radius
Windows:     19px title bar
Dialogs:     2px double (modal)
Checkboxes:  12×12px
Text boxes:  16px height

STROKES:            FONTS:
Primary:   2-3px   Title:  18-28px bold
Secondary: 1.5px   Label:  14-16px bold
Fine:      1px     Body:   11-13px
                   Notes:  9-11px

RULES:
✓ Solid grays (#1A1A1A-#E6E6E6) for gradients
✓ Bitmap patterns for texture
✓ Generic monospace font
✓ Bold geometric style
✓ 8×8 pixel patterns
✓ <text> elements (never paths)
✗ NO solid grays (#808080)
✗ NO opacity/transparency
✗ NO anti-aliasing effects
```

---

*Last updated: November 24, 2025*
*Pattern library: 17 patterns | Design system: Mac OS System 1 (1984)*
