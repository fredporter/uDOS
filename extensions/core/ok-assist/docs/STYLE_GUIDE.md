# OK Assist SVG Style Guide

**Complete specification for Technical-Kinetic and Hand-Illustrative styles**

## Overview

OK Assist uses two distinct illustration styles optimized for different subject matter:

1. **Technical-Kinetic**: Clean, geometric, precise (tools, systems, UI)
2. **Hand-Illustrative**: Organic, flowing, natural (anatomy, plants, landscapes)

Both styles are:
- **Monochrome** (black/white with grayscale)
- **Vector-based** (infinite scalability)
- **Print-optimized** (high contrast, clear lines)
- **File-size conscious** (target <50KB)

---

## Technical-Kinetic Style

### When to Use
- Tools and equipment
- Mechanical systems and machinery
- UI diagrams and flowcharts
- Structural blueprints and plans
- System architecture diagrams
- Geometric knots and lashings
- Navigation instruments
- Electronic circuits
- Measurements and technical specifications

### Visual Characteristics

**Line Weights**:
```
Primary structural: 1.5px
Detail/guide lines: 0.5px
Texture/shading:    0.3px
Bold emphasis:      2.5px
```

**Typography**:
```
Primary:     Chicago 12pt (bold, titles)
Body:        Geneva 9pt (labels, descriptions)
Measurement: Geneva 8pt italic
Format:      Monospace, left-aligned
```

**Icons**:
- **Source**: CoreUI Icons (free set, MIT license)
- **Style**: Geometric, consistent line weight
- **Usage**: UI elements, controls, indicators, symbols
- **Common**: `cil-wrench`, `cil-settings`, `cil-warning`, `cil-check`

**Patterns**:
- **Source**: Mac OS System 1 bitmap patterns
- **Grid**: 8×8 pixels (perfectly repeating)
- **Types**:
  - Grayscale: `gray-12`, `gray-25`, `gray-37`, `gray-50`, `gray-62`, `gray-75`, `gray-87`
  - Texture: `crosshatch`, `diagonal`, `horizontal`, `vertical`, `dots`, `brick`, `scales`

**Shading Techniques**:
- **Crosshatch**: Perpendicular lines at 45° angles
- **Stipple**: Small dots (0.5px radius) in density patterns
- **Parallel lines**: Even spacing, consistent angle
- **Gradient simulation**: Varying line density

### Technical Specifications

**SVG Structure**:
```xml
<svg xmlns="http://www.w3.org/2000/svg"
     viewBox="0 0 800 600"
     width="800" height="600"
     class="technical-kinetic">

  <!-- Pattern definitions -->
  <defs>
    <pattern id="gray-50">...</pattern>
    <pattern id="crosshatch">...</pattern>
  </defs>

  <!-- Title and description -->
  <title>Diagram Title</title>
  <desc>Brief description for accessibility</desc>

  <!-- Content groups -->
  <g class="primary-structure">
    <line class="primary-line" x1="..." y1="..." x2="..." y2="..." />
  </g>

  <g class="detail">
    <line class="detail-line" x1="..." y1="..." x2="..." y2="..." />
  </g>

  <!-- Labels -->
  <text class="label-large" x="..." y="...">Label</text>
</svg>
```

**CSS Classes**:
```css
.technical-kinetic          /* Root container */
.primary-line               /* Main structural lines */
.detail-line                /* Measurements, guides */
.bold-line                  /* Emphasis */
.texture-line               /* Shading lines */
.fill-pattern               /* Pattern fills */
.label-large / .label-small /* Text labels */
.crosshatch / .stipple      /* Shading groups */
.dimension                  /* Dimension lines */
.callout                    /* Annotation boxes */
```

### Examples

**Axe Diagram (Technical-Kinetic)**:
- Bold outline (2.5px) for axe head
- Primary lines (1.5px) for handle
- Detail lines (0.5px) for grain direction
- Crosshatch pattern for steel head
- Horizontal pattern for wood handle
- CoreUI `cil-warning` icon for safety notes
- Dimension lines with arrows
- Chicago 12pt labels for parts

---

## Hand-Illustrative Style

### When to Use
- Human anatomy and organs
- Plants and botanical subjects
- Animals and wildlife
- Landscapes and terrain
- Food and cooking
- Natural materials (wood, stone, rope, fabric)
- Weather and atmospheric effects
- Water and fluid dynamics
- Geological formations

### Visual Characteristics

**Line Weights (Variable)**:
```
Fine detail:     0.8px
Medium organic:  1.5px
Bold contour:    2.5px
Texture:         0.4px
```

**Typography**:
```
Title:       Geneva 14pt (italic, bold)
Body:        Geneva 10pt (regular)
Caption:     Geneva 8pt (italic)
Scientific:  Geneva 9pt (italic, light)
Format:      Serif-style, centered or flowing
```

**Shading Patterns**:
- **Wavy lines**: Parallel flowing lines following form
- **Circular fields**: Concentric circles for atmospheric effects
- **Topographical**: Contour lines following elevation/depth
- **Stipple**: Variable density dots (0.6px radius)
- **Cross-contour**: Lines wrapping around 3D forms

**Natural Textures**:
```xml
<!-- Woodgrain -->
<pattern id="woodgrain">
  <path d="M0,0 Q5,2 10,0 Q15,2 20,0" />
  <path d="M0,4 Q5,6 10,4 Q15,6 20,4" />
  ...
</pattern>

<!-- Water ripples -->
<pattern id="water-ripple">
  <ellipse cx="10" cy="5" rx="8" ry="2" />
  <ellipse cx="10" cy="10" rx="12" ry="3" />
  ...
</pattern>

<!-- Stone texture -->
<pattern id="stone-texture">
  <path d="M0,0 L3,2 L1,5 L4,7..." />
  <!-- Irregular polygon cracks -->
</pattern>
```

### Organic Shading Techniques

**Form Following**:
- Lines curve to follow 3D form
- Denser spacing in shadows
- Wider spacing in highlights
- Variable line weight suggests depth

**Atmospheric Perspective**:
- Foreground: Bold lines (2.5px), full opacity
- Midground: Medium lines (1.5px), 80% opacity
- Background: Fine lines (0.8px), 50% opacity

**Biological Detail**:
- **Veins** (leaves, anatomy): Fine lines (0.8px) branching pattern
- **Muscle fibers**: Parallel wavy lines (0.4px texture)
- **Cross-sections**: Concentric rings or cellular patterns
- **Surface texture**: Stipple density variations

### Technical Specifications

**SVG Structure**:
```xml
<svg xmlns="http://www.w3.org/2000/svg"
     viewBox="0 0 700 900"
     width="700" height="900"
     class="hand-illustrative">

  <!-- Pattern definitions -->
  <defs>
    <pattern id="woodgrain">...</pattern>
    <pattern id="water-ripple">...</pattern>
  </defs>

  <!-- Title and description -->
  <title>Illustration Title</title>
  <desc>Detailed description</desc>

  <!-- Layered by depth -->
  <g class="background">
    <path class="bg-far" d="..." />
  </g>

  <g class="midground">
    <path class="midground" d="..." />
  </g>

  <g class="foreground">
    <path class="contour-line" d="..." />
    <g class="wavy-shade">
      <path class="texture-line" d="..." />
    </g>
  </g>

  <!-- Labels -->
  <text class="label-title" x="..." y="...">Title</text>
  <text class="label-scientific" x="..." y="...">Scientific name</text>
</svg>
```

**CSS Classes**:
```css
.hand-illustrative         /* Root container */
.primary-line              /* Main organic lines */
.fine-line / .contour-line /* Detail / bold outlines */
.texture-line              /* Shading strokes */
.wavy-shade                /* Organic shading group */
.circular-shade            /* Atmospheric patterns */
.stipple                   /* Dot textures */
.woodgrain / .water-ripple /* Natural textures */
.vein / .muscle-fiber      /* Biological details */
.foreground / .midground / .background /* Depth layers */
```

### Examples

**Plant Anatomy (Hand-Illustrative)**:
- Bold contour (2.5px) for main stem
- Fine veins (0.8px) branching pattern
- Wavy shading lines following leaf curve
- Stipple texture for flower center
- Circular patterns for pollen detail
- Geneva 14pt italic title
- Geneva 9pt italic scientific names

---

## Gemini API Prompts

### Technical-Kinetic Prompt Template

```
Create a monochrome SVG technical diagram of {subject} in Technical-Kinetic style:

STYLE REQUIREMENTS:
- Clean vector lines: 1.5px primary, 0.5px detail, 2.5px bold
- CoreUI icon style for UI elements and controls
- Mac OS System 1 bitmap patterns (8×8 grid) for fills
- Crosshatch or stipple shading for depth
- Geometric precision and measurement clarity
- Monospace labels (Chicago 12pt titles, Geneva 9pt body)

TECHNICAL CONSTRAINTS:
- SVG viewBox and dimensions properly defined
- Pattern definitions in <defs> section
- Grouped elements by function
- Text elements NOT converted to paths
- File size target: <50KB
- Minified output (remove whitespace, comments)

CONTENT:
{detailed_description}

OUTPUT FORMAT:
Pure SVG code starting with <?xml version="1.0"?>
No explanations, just valid SVG markup.
```

### Hand-Illustrative Prompt Template

```
Create a monochrome SVG illustration of {subject} in Hand-Illustrative line-art style:

STYLE REQUIREMENTS:
- Variable line weight: 0.8px fine, 1.5px medium, 2.5px bold
- Organic flowing curves with rounded line caps/joins
- Wavy parallel lines for shading fields
- Circular/concentric patterns for atmospheric effects
- Topographical contour detail
- Traditional engraving/woodcut aesthetic
- Hand-drawn precision (not sketchy)

SHADING TECHNIQUES:
- Form-following wavy lines (0.4px texture weight)
- Stipple density variations (0.6px dots)
- Cross-contour wrapping around forms
- Natural textures: woodgrain, water ripples, stone cracks

TECHNICAL CONSTRAINTS:
- SVG viewBox and dimensions properly defined
- Pattern definitions for organic textures
- Layered by depth (foreground/mid/background)
- Text elements NOT converted to paths
- File size target: <50KB
- Minified output

CONTENT:
{detailed_description}

OUTPUT FORMAT:
Pure SVG code starting with <?xml version="1.0"?>
No explanations, just valid SVG markup.
```

---

## File Size Optimization

### Target Sizes
- Simple diagrams: 5-10KB
- Detailed illustrations: 10-25KB
- Complex technical: 15-35KB
- **Maximum**: 50KB (enforced)

### Optimization Techniques

**1. Minification**:
```bash
# Remove unnecessary whitespace
svgo --multipass --pretty diagram.svg

# Specific optimizations
svgo --disable=removeViewBox \
     --enable=removeMetadata \
     --enable=removeComments \
     diagram.svg
```

**2. Path Simplification**:
- Reduce decimal precision to 2 places
- Combine consecutive path commands
- Use relative commands (l, c, q vs L, C, Q)

**3. Pattern Reuse**:
- Define patterns once in `<defs>`
- Reference with `fill="url(#pattern-id)"`
- Share patterns across similar elements

**4. Smart Grouping**:
```xml
<!-- Good: Shared styles -->
<g stroke="#000" stroke-width="1.5" fill="none">
  <line x1="..." y1="..." x2="..." y2="..." />
  <line x1="..." y1="..." x2="..." y2="..." />
</g>

<!-- Avoid: Repeated attributes -->
<line stroke="#000" stroke-width="1.5" fill="none" x1="..." />
<line stroke="#000" stroke-width="1.5" fill="none" x1="..." />
```

**5. Text Optimization**:
- Keep text as `<text>` elements (editable)
- Use `textLength` attribute to control width
- Share `font-family` and `font-size` via CSS

---

## Quality Checklist

### Before Export

**Technical-Kinetic**:
- [ ] Line weights consistent (1.5px primary, 0.5px detail)
- [ ] CoreUI icons properly integrated
- [ ] Mac OS patterns correctly referenced
- [ ] Labels use Chicago/Geneva fonts
- [ ] Measurements clearly marked
- [ ] File size under 50KB
- [ ] viewBox and dimensions defined
- [ ] Validated SVG syntax

**Hand-Illustrative**:
- [ ] Variable line weights follow form (0.8-2.5px)
- [ ] Organic shading patterns applied
- [ ] Natural textures appropriate to subject
- [ ] Depth layering (foreground/mid/background)
- [ ] Labels use serif-style fonts
- [ ] Anatomical/botanical accuracy
- [ ] File size under 50KB
- [ ] viewBox and dimensions defined
- [ ] Validated SVG syntax

### Accessibility
- [ ] `<title>` element present
- [ ] `<desc>` element provides context
- [ ] Semantic grouping with `<g>` elements
- [ ] Text elements readable (not paths)
- [ ] ARIA labels where appropriate
- [ ] Color not sole means of information

---

## Version History

**v1.0.0** (November 25, 2025)
- Initial style guide
- Technical-Kinetic specification
- Hand-Illustrative specification
- Gemini API prompt templates
- Optimization guidelines

---

**Maintained by**: uDOS Project
**Location**: `/extensions/core/ok-assist/docs/STYLE_GUIDE.md`
