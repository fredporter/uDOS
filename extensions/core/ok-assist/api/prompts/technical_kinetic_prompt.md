# Technical-Kinetic SVG Generation Prompt

## Subject: {subject}

## Description
{description}

---

## STYLE: Technical-Kinetic

### Visual Requirements

**Monochrome Aesthetic**:
- Base colors: Black (#000000) and White (#FFFFFF)
- Grayscale fills: Use Mac OS System 1 bitmap patterns
- No color gradients - use pattern density instead

**Line Weights** (consistent throughout):
- Primary structural lines: **1.5px** (main shapes, outlines)
- Detail/guide lines: **0.5px** (measurements, construction lines, dashed guides)
- Bold emphasis: **2.5px** (important features, cut lines, safety zones)
- Texture shading: **0.3px** (crosshatch, stipple, pattern fills)

**Geometry**:
- Clean, precise vector paths
- Straight lines and perfect curves
- Right angles and measured spacing
- Grid-aligned when possible

---

### Typography

Use **monospace fonts** (simulate Chicago/Geneva):

```
Title text:       font-size="16" font-weight="bold" font-family="monospace"
Body labels:      font-size="11" font-family="monospace"
Measurements:     font-size="9" font-style="italic" font-family="monospace"
```

**Text placement**:
- Left-aligned for descriptions
- Centered for titles
- Right-aligned for measurements
- Keep text horizontal (0° rotation preferred)

---

### Icons and Symbols

**CoreUI Icon Style**:
- Use geometric, consistent-weight icons for:
  - Tools: `cil-wrench`, `cil-screwdriver`, `cil-hammer`
  - UI elements: `cil-settings`, `cil-menu`, `cil-chevron-*`
  - Indicators: `cil-warning`, `cil-check-circle`, `cil-x-circle`
  - Navigation: `cil-arrow-*`, `cil-compass`

**Icon specifications**:
- Size: 16×16px or 24×24px (consistent within diagram)
- Line weight: 1.5px
- Style: Outlined (not filled solid)
- Placement: Grid-aligned

---

### Patterns and Fills

**Mac OS System 1 Bitmap Patterns** (8×8 pixel repeating):

Define in `<defs>` section:

```xml
<defs>
  <!-- Grayscale patterns -->
  <pattern id="gray-12" patternUnits="userSpaceOnUse" width="8" height="8">
    <rect width="8" height="8" fill="#EDEDED"/>
    <path d="M0,0 L0,1 M4,0 L4,1 M0,4 L0,5 M4,4 L4,5" stroke="#000" stroke-width="1"/>
  </pattern>

  <pattern id="gray-50" patternUnits="userSpaceOnUse" width="8" height="8">
    <rect width="8" height="8" fill="#FFF"/>
    <path d="M0,0 L4,0 L4,4 L0,4 Z M4,4 L8,4 L8,8 L4,8 Z" fill="#000"/>
  </pattern>

  <!-- Crosshatch -->
  <pattern id="crosshatch" patternUnits="userSpaceOnUse" width="8" height="8">
    <path d="M0,0 L8,8 M8,0 L0,8" stroke="#000" stroke-width="0.3"/>
  </pattern>

  <!-- Diagonal lines -->
  <pattern id="diagonal" patternUnits="userSpaceOnUse" width="8" height="8">
    <path d="M0,0 L8,8 M-2,6 L2,10 M6,-2 L10,2" stroke="#000" stroke-width="0.5"/>
  </pattern>
</defs>
```

**Pattern usage**:
- Solid fills: `fill="url(#gray-50)"`
- Light shading: `fill="url(#gray-12)"`
- Medium shading: `fill="url(#gray-37)"`
- Dark shading: `fill="url(#gray-75)"`
- Textures: `fill="url(#crosshatch)"` for metal, `fill="url(#diagonal)"` for wood

---

### Shading Techniques

**Crosshatch** (for metal, hard surfaces):
```xml
<g class="crosshatch-shading">
  <line x1="10" y1="10" x2="50" y2="50" stroke="#000" stroke-width="0.3"/>
  <line x1="50" y1="10" x2="10" y2="50" stroke="#000" stroke-width="0.3"/>
  <!-- Repeat at regular intervals -->
</g>
```

**Stipple** (for gradual shading):
```xml
<g class="stipple-shading">
  <circle cx="12" cy="15" r="0.5" fill="#000"/>
  <circle cx="18" cy="17" r="0.5" fill="#000"/>
  <!-- Vary density for gradient effect -->
</g>
```

**Parallel lines** (for directional surfaces):
```xml
<g class="parallel-shading">
  <line x1="10" y1="20" x2="90" y2="20" stroke="#000" stroke-width="0.3"/>
  <line x1="10" y1="24" x2="90" y2="24" stroke="#000" stroke-width="0.3"/>
  <!-- Even spacing, consistent angle -->
</g>
```

---

### Document Structure

```xml
<?xml version="1.0" encoding="UTF-8"?>
<svg xmlns="http://www.w3.org/2000/svg"
     viewBox="0 0 {width} {height}"
     width="{width}"
     height="{height}">

  <title>{subject}</title>
  <desc>{description}</desc>

  <defs>
    <!-- Pattern definitions here -->
  </defs>

  <!-- Main content grouped logically -->
  <g id="primary-structure">
    <!-- Primary shapes with 1.5px lines -->
  </g>

  <g id="details">
    <!-- Detail lines with 0.5px weight -->
  </g>

  <g id="shading">
    <!-- Texture patterns and fills -->
  </g>

  <g id="labels">
    <!-- Text elements (NOT paths) -->
  </g>

  <g id="measurements">
    <!-- Dimension lines and values -->
  </g>

  <g id="icons">
    <!-- CoreUI-style icons -->
  </g>
</svg>
```

---

### Technical Constraints

**File Size**:
- Target: <50KB
- Optimize: Remove comments, extra whitespace, editor metadata
- Keep: Accessible title/desc, semantic grouping

**Validation**:
- Must include: `viewBox`, `width`, `height`, `<title>`, `<desc>`
- Text must be editable: Use `<text>` elements, NOT `<path>`
- Patterns must be defined in `<defs>` and reused
- Group related elements with `<g id="...">`

**Accessibility**:
```xml
<title>Descriptive title of diagram</title>
<desc>Detailed description of content and purpose</desc>
<text aria-label="Important label text">Label</text>
```

---

## Examples of Good Technical-Kinetic SVGs

### 1. Tool Diagram (Axe)
- Bold outline (2.5px) for blade and handle
- Crosshatch shading on metal
- Diagonal pattern for wood grain
- Measurement lines (0.5px dashed)
- Labels with leaders pointing to features
- CoreUI tool icons for cutting directions

### 2. System Diagram (Water Filter)
- Container outlines (1.5px)
- Flow arrows (1.5px with arrowheads)
- Layer fills (gray-25, gray-50, gray-75 patterns)
- Labels identifying each component
- CoreUI icons for flow direction
- Stipple shading for porous materials

### 3. UI Mockup (Window)
- Window frame (1.5px)
- Title bar (filled with gray-12)
- Buttons using CoreUI icons
- Text fields (outlined 0.5px)
- Drop shadows (parallel line shading)
- Grid alignment visible

---

## Output Requirements

**Format**: Pure SVG code only
**Start with**: `<?xml version="1.0" encoding="UTF-8"?>`
**No explanations**: Just the SVG markup
**Validation**: Must render correctly in browsers
**Size check**: Keep under 50KB

Generate the SVG now.
