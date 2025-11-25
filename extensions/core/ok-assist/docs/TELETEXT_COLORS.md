# Teletext Color Palette & Enhancement Guide

**v1.4.0 Phase 3 - Teletext Format Enhancement**

This guide documents the World System Teletext (WST) color system and enhancement features for creating accessible, retro-style diagrams.

---

## Table of Contents

1. [WST Color System](#wst-color-system)
2. [Level 1 Features (Basic)](#level-1-features)
3. [Level 2.5 Features (Enhanced)](#level-25-features)
4. [Level 3.5 Features (Advanced)](#level-35-features)
5. [Color Palette Guidelines](#color-palette-guidelines)
6. [Mosaic Block System](#mosaic-block-system)
7. [Interactive Navigation Patterns](#interactive-navigation-patterns)
8. [Accessibility Considerations](#accessibility-considerations)

---

## WST Color System

### Standard 8-Color Palette (Level 1)

Teletext uses an 8-color palette based on RGB primaries:

| Color   | Code | RGB Value | Hex Code | Usage Guidelines |
|---------|------|-----------|----------|------------------|
| **Black**   | 0 | (0, 0, 0) | #000000 | Background, text, outlines |
| **Red**     | 1 | (255, 0, 0) | #FF0000 | Danger, fire, warnings, blood |
| **Green**   | 2 | (0, 255, 0) | #00FF00 | Safety, vegetation, go signals |
| **Yellow**  | 3 | (255, 255, 0) | #FFFF00 | Caution, highlights, sun |
| **Blue**    | 4 | (0, 0, 255) | #0000FF | Water, sky, cold, information |
| **Magenta** | 5 | (255, 0, 255) | #FF00FF | Medical, accent, contrast |
| **Cyan**    | 6 | (0, 255, 255) | #00FFFF | Ice, water treatment, tech |
| **White**   | 7 | (255, 255, 255) | #FFFFFF | Text, highlights, snow |

### Control Codes

```
Text Colors:
  0x80-0x87: Set text color (black through white)

Graphics Colors:
  0x90-0x97: Set graphics color (black through white)

Modes:
  0x99: Contiguous graphics (blocks touch)
  0x9A: Separated graphics (1px gap between blocks)
  0x9C: Black background
  0x9D: New background (uses current text color)
  0x1C: Double height (top half)
  0x1D: Double height (bottom half)
```

---

## Level 1 Features (Basic)

**Capabilities:**
- 8-color palette (RGB primaries + black/white)
- 40×25 character grid
- Mosaic blocks (2×3 pixel cells)
- Contiguous/separated graphics mode
- Double-height text
- Flash attribute (text/graphics flash on/off)

**Limitations:**
- Cannot mix text and graphics in same cell
- Limited smooth curves
- No alpha/transparency
- Fixed 40×25 resolution

**Best For:**
- Simple diagrams with bold colors
- Step-by-step instructions
- Icon-based interfaces
- Retro game-style visualizations

---

## Level 2.5 Features (Enhanced)

**Additional Capabilities:**
- Smooth mosaics (anti-aliased edges)
- Separated graphics mode improvements
- Enhanced control code support
- Better character/graphics mixing

**Enhancements:**
- Smoother diagonal lines
- Improved color separation
- Better readability

**Best For:**
- Detailed survival diagrams
- Technical illustrations
- UI components with rounded edges
- More sophisticated visualizations

---

## Level 3.5 Features (Advanced)

**Advanced Capabilities:**
- Dynamic content loading
- Page linking/navigation
- Real-time updates
- Extended control codes

**Interactive Features:**
- Clickable regions (for web teletext)
- Multi-page navigation
- Animated sequences
- Data-driven updates

**Best For:**
- Interactive survival guides
- Multi-step procedures
- Dynamic reference materials
- Navigation systems

---

## Color Palette Guidelines

### Survival Category Color Conventions

**Water (Primary: Blue, Cyan)**
- Blue (#0000FF): Deep water, ocean, lakes
- Cyan (#00FFFF): Purified water, ice, treatment systems
- White (#FFFFFF): Snow, frost, steam
- Yellow (#FFFF00): Contaminated/questionable water warning

**Fire (Primary: Red, Yellow)**
- Red (#FF0000): Flames, embers, danger zones
- Yellow (#FFFF00): Light, heat, caution areas
- Black (#000000): Char, ash, extinguished
- White (#FFFFFF): Smoke, intense heat

**Shelter (Primary: Green, Yellow)**
- Green (#00FF00): Natural materials, vegetation cover
- Yellow (#FFFF00): Construction materials, framework
- Black (#000000): Shadows, ground, interior
- White (#FFFFFF): Snow shelters, reflective materials

**Food (Primary: Green, Yellow)**
- Green (#00FF00): Edible plants, safe foods
- Red (#FF0000): Toxic plants, danger, stop
- Yellow (#FFFF00): Caution, test unknown foods
- Black (#000000): Cooked, charred, preserved

**Medical (Primary: Red, Magenta)**
- Red (#FF0000): Blood, severe injuries, emergency
- Magenta (#FF00FF): Medical supplies, treatment
- White (#FFFFFF): Bandages, sterile materials
- Yellow (#FFFF00): Moderate injury, caution
- Green (#00FF00): Safe, treated, recovered

**Navigation (Primary: Blue, Cyan, Yellow)**
- Blue (#0000FF): North, water features, compass
- Yellow (#FFFF00): Sun, stars, light sources
- Green (#00FF00): Safe routes, go signals
- Red (#FF0000): Danger, wrong way, hazards

**Tools (Primary: Cyan, White)**
- Cyan (#00FFFF): Metal, blades, technology
- White (#FFFFFF): Stone, bone, light materials
- Yellow (#FFFF00): Wood, handles, natural materials
- Black (#000000): Shadows, depth, worn areas

**Communication (Primary: Yellow, Cyan)**
- Yellow (#FFFF00): Signals, light sources, attention
- Cyan (#00FFFF): Radio, technology, modern comm
- Red (#FF0000): Emergency, SOS, urgent
- Green (#00FF00): Acknowledged, message received

### Color Combination Rules

**High Contrast Pairings** (for readability):
- Black on White / White on Black
- Black on Yellow / Yellow on Black
- Blue on White / White on Blue
- Red on White / White on Red

**Avoid These Combinations** (poor readability):
- Red on Blue / Blue on Red
- Yellow on White / White on Yellow
- Green on Cyan / Cyan on Green
- Magenta on Red / Red on Magenta

**Complementary Pairs** (for emphasis):
- Red & Cyan
- Green & Magenta
- Blue & Yellow

---

## Mosaic Block System

### 2×3 Pixel Cell Structure

Each teletext character cell can display a 2×3 mosaic of colored blocks:

```
┌─┬─┐
├─┼─┤  = 6 individually controllable pixels
├─┼─┤
└─┴─┘
```

### Block Patterns (6-bit encoding)

The 6 pixels are encoded as bits 0-5 (64 possible patterns):

```
Bit positions:    Binary:    Decimal:  Pattern:
┌───┬───┐        ┌───┬───┐           ┌─┬─┐
│ 0 │ 1 │        │ 0 │ 1 │     1  =  │ │█│
├───┼───┤        ├───┼───┤           ├─┼─┤
│ 2 │ 3 │        │ 0 │ 0 │           │ │ │
├───┼───┤        ├───┼───┤           ├─┼─┤
│ 4 │ 5 │        │ 0 │ 0 │           │ │ │
└───┴───┘        └───┴───┘           └─┴─┘

     4  =  │ │ │        16 =  │█│ │        63 = │█│█│
           ├─┼─┤              ├─┼─┤             ├─┼─┤
           │█│ │              │ │ │             │█│█│
           ├─┼─┤              ├─┼─┤             ├─┼─┤
           │ │ │              │ │ │             │█│█│
           └─┴─┘              └─┴─┘             └─┴─┘
```

### Common Patterns

**Horizontal Lines:**
- Top: 3 (bits 0-1)
- Middle: 12 (bits 2-3)
- Bottom: 48 (bits 4-5)
- All: 63

**Vertical Lines:**
- Left: 21 (bits 0,2,4)
- Right: 42 (bits 1,3,5)
- Both: 63

**Diagonal Lines:**
- Top-left to bottom-right: 37 (0,3,5)
- Top-right to bottom-left: 26 (1,2,4)

**Shapes:**
- Square/Rectangle: 63 (all bits)
- Corners: Various combinations
- Arrows: Directional patterns

---

## Interactive Navigation Patterns

### Multi-Page Navigation

```
Page Structure:
┌─────────────────────────────────────┐
│ WATER PURIFICATION GUIDE    [1/5]  │ ← Header
├─────────────────────────────────────┤
│                                     │
│     [Content Area]                  │ ← Main diagram
│                                     │
├─────────────────────────────────────┤
│ ← Prev | Menu | Next →             │ ← Navigation
└─────────────────────────────────────┘
```

### Interactive Elements (for web teletext)

**Clickable Regions:**
```html
<area shape="rect" coords="x1,y1,x2,y2" href="page.html">
```

**Highlighted Selection:**
- Use inverse video (swap foreground/background)
- Flash attribute for attention
- Color change on hover

**Navigation Patterns:**
1. **Linear:** Previous ← Current → Next
2. **Tree:** Up to menu, down to sub-topics
3. **Grid:** Arrow keys navigate 2D layout
4. **Index:** Jump to page number

---

## Accessibility Considerations

### Color Blindness Support

**Protanopia (Red-Blind):**
- Don't rely solely on red/green distinction
- Use shape, pattern, position as additional cues
- Prefer blue/yellow contrasts

**Deuteranopia (Green-Blind):**
- Similar to protanopia
- Blue/yellow, black/white work well

**Tritanopia (Blue-Blind):**
- Avoid blue/yellow as sole distinction
- Use red/green, black/white

**General Guidelines:**
- Always include text labels
- Use patterns in addition to colors
- Ensure sufficient contrast ratios
- Test with grayscale conversion

### Screen Reader Support

**Text Equivalents:**
- Provide alt text for graphics
- Use semantic HTML structure
- Include ARIA labels where needed

**Navigation:**
- Skip links for keyboard users
- Logical tab order
- Clear focus indicators

---

## Example Teletext Diagram Specification

### Water Filter Cross-Section (Detailed, Blue/Cyan palette)

```
Specifications:
- Format: Teletext Level 2.5
- Dimensions: 40×25 characters
- Primary Colors: Blue (#0000FF), Cyan (#00FFFF), White (#FFFFFF)
- Graphics Mode: Separated (for clarity)
- Text: White on black
- Layout: Side-view cross-section

Content Structure:
Rows 1-2:   Title and header
Rows 3-22:  Main diagram (filter layers)
Rows 23-24: Legend and navigation
Row 25:     Footer (page info)

Color Usage:
- Blue: Dirty water input
- Cyan: Filtered water output
- White: Filter layers (charcoal, sand, gravel)
- Yellow: Warning indicators
- Black: Container, background

Annotations:
- Labels: "INPUT", "OUTPUT", layer names
- Arrows: Water flow direction (blue → cyan)
- Dimensions: Layer thickness in cm
- Warnings: "BOIL AFTER FILTERING"
```

---

## Resources

**Teletext Standards:**
- World System Teletext (WST) Specification
- ETS 300 706: Enhanced Teletext specification
- Ceefax/Prestel historical archives

**Tools:**
- edit.tf: Online teletext editor
- Teletext Generator: Python library
- ZXNet: Teletext emulator

**Examples:**
- BBC Ceefax archives (1974-2012)
- Teletext art gallery (block graphics showcase)
- Modern teletext revival projects

---

**Version:** 1.0
**Last Updated:** November 25, 2025
**Author:** uDOS Development Team
**License:** See LICENSE.txt
