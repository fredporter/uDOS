# Hand-Illustrative Line-Art SVG Generation Prompt

## Subject: {subject}

## Description
{description}

---

## STYLE: Hand-Illustrative Line-Art

### Visual Requirements

**Monochrome Engraving Aesthetic**:
- Base: Black ink on white paper (#000000 on #FFFFFF)
- No color or color gradients
- Organic, flowing lines with natural variation
- Traditional woodcut/engraving appearance
- Hand-drawn precision (not sketchy or rough)

**Variable Line Weights**:
- Fine detail: **0.8px** (hair, tiny features, subtle texture)
- Medium standard: **1.5px** (main contours, form definition)
- Bold contour: **2.5px** (outer edges, major separations)
- Texture shading: **0.4px** (wavy lines, stipple, cross-contour)

**Organic Forms**:
- Smooth, flowing curves (not geometric)
- Natural asymmetry and irregularity
- Rounded line caps and joins: `stroke-linecap="round" stroke-linejoin="round"`
- Form-following contours

---

### Typography

Use **serif-style monospace** (simulate Geneva italic):

```
Title text:       font-size="18" font-weight="bold" font-style="italic" font-family="serif"
Body captions:    font-size="11" font-family="serif"
Scientific:       font-size="10" font-style="italic" font-family="serif"
```

**Text placement**:
- Curved along natural contours when appropriate
- Italic for scientific/Latin names
- Small capitals for emphasis

---

### Shading Techniques

**Wavy Parallel Lines** (for fields and surfaces):
```xml
<path d="M10,20 Q30,18 50,20 Q70,22 90,20"
      stroke="#000" stroke-width="0.4" fill="none"/>
<path d="M10,24 Q30,22 50,24 Q70,26 90,24"
      stroke="#000" stroke-width="0.4" fill="none"/>
<!-- Spacing varies for depth: closer = darker -->
```

**Circular Concentric** (for atmospheric fields, clouds, gas):
```xml
<ellipse cx="100" cy="100" rx="20" ry="15"
         stroke="#000" stroke-width="0.4" fill="none"/>
<ellipse cx="100" cy="100" rx="25" ry="19"
         stroke="#000" stroke-width="0.4" fill="none"/>
<ellipse cx="100" cy="100" rx="30" ry="23"
         stroke="#000" stroke-width="0.4" fill="none"/>
<!-- Smoothly expanding rings -->
```

**Cross-Contour** (for rounded forms, anatomy, fruit):
```xml
<!-- Lines that wrap around the form following its curvature -->
<path d="M20,50 Q40,45 60,50" stroke="#000" stroke-width="0.4" fill="none"/>
<path d="M18,55 Q40,50 62,55" stroke="#000" stroke-width="0.4" fill="none"/>
<path d="M16,60 Q40,55 64,60" stroke="#000" stroke-width="0.4" fill="none"/>
<!-- Curves follow the three-dimensional form -->
```

**Stipple Density** (for gradual tonal transitions):
```xml
<g class="stipple-light">
  <circle cx="15" cy="20" r="0.6" fill="#000"/>
  <circle cx="25" cy="22" r="0.6" fill="#000"/>
  <!-- Sparse dots for light areas -->
</g>

<g class="stipple-dense">
  <circle cx="50" cy="50" r="0.6" fill="#000"/>
  <circle cx="53" cy="51" r="0.6" fill="#000"/>
  <circle cx="51" cy="53" r="0.6" fill="#000"/>
  <!-- Dense clustering for dark areas -->
</g>
```

---

### Natural Texture Patterns

**Woodgrain**:
```xml
<g class="woodgrain">
  <path d="M0,10 Q20,8 40,10 Q60,12 80,10"
        stroke="#000" stroke-width="0.4" fill="none"/>
  <path d="M0,15 Q20,13 40,15 Q60,17 80,15"
        stroke="#000" stroke-width="0.4" fill="none"/>
  <!-- Irregular wavy lines, some branching -->
</g>
```

**Water Ripples**:
```xml
<g class="water-ripple">
  <ellipse cx="50" cy="50" rx="10" ry="8"
           stroke="#000" stroke-width="0.4" fill="none"/>
  <ellipse cx="50" cy="50" rx="18" ry="14"
           stroke="#000" stroke-width="0.4" fill="none"/>
  <!-- Expanding, slightly irregular -->
</g>
```

**Stone/Rock Texture**:
```xml
<g class="stone-texture">
  <!-- Irregular cracks and fissures -->
  <path d="M10,20 L15,25 L12,30" stroke="#000" stroke-width="0.6" fill="none"/>
  <path d="M30,15 L28,22 L32,28" stroke="#000" stroke-width="0.6" fill="none"/>
  <!-- Stipple for rough surface -->
  <circle cx="20" cy="25" r="0.5" fill="#000"/>
  <circle cx="23" cy="27" r="0.5" fill="#000"/>
</g>
```

**Fabric/Rope Weave**:
```xml
<g class="rope-weave">
  <!-- Diagonal crossed lines -->
  <path d="M0,0 Q10,5 20,0" stroke="#000" stroke-width="0.8" fill="none"/>
  <path d="M5,0 Q15,5 25,0" stroke="#000" stroke-width="0.8" fill="none"/>
  <!-- Opposite angle -->
  <path d="M0,5 Q10,0 20,5" stroke="#000" stroke-width="0.8" fill="none"/>
</g>
```

**Cloud/Atmospheric Fields**:
```xml
<g class="cloud-field">
  <!-- Soft, irregular circular patterns -->
  <circle cx="20" cy="30" r="8" stroke="#000" stroke-width="0.3" fill="none"/>
  <circle cx="28" cy="32" r="10" stroke="#000" stroke-width="0.3" fill="none"/>
  <circle cx="22" cy="38" r="6" stroke="#000" stroke-width="0.3" fill="none"/>
  <!-- Overlapping, varying sizes -->
</g>
```

---

### Depth Layering

**Foreground** (darkest, sharpest):
- Bold outlines (2.5px)
- Dense shading
- High detail
- Crisp edges

**Midground** (medium):
- Standard weight (1.5px)
- Moderate shading
- Good detail
- Clear definition

**Background** (lightest, softest):
- Fine lines (0.8px)
- Minimal shading
- Simplified forms
- Atmospheric perspective

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
    <!-- Optional pattern definitions for textures -->
  </defs>

  <!-- Layered by depth -->
  <g id="background" opacity="0.4">
    <!-- Background elements with fine lines -->
  </g>

  <g id="midground" opacity="0.7">
    <!-- Middle depth with medium lines -->
  </g>

  <g id="foreground">
    <!-- Foreground with bold contours and detail -->
  </g>

  <g id="labels">
    <!-- Text labels (NOT paths) -->
  </g>
</svg>
```

---

### Subject-Specific Guidelines

**Human Anatomy**:
- Bold outer contours (2.5px)
- Cross-contour shading following muscle forms
- Stipple for skin texture
- Fine lines for hair and subtle details
- Anatomical accuracy with clear labeling

**Plants**:
- Varying line weights (fine veins, medium stem, bold outline)
- Parallel wavy lines for leaf shading
- Stipple for petal texture
- Natural curves and organic asymmetry
- Root systems with branching tapering lines

**Landscapes**:
- Background mountains with fine atmospheric lines
- Midground trees with detailed foliage
- Foreground with bold elements and rich texture
- Water using ripple patterns
- Sky using soft circular fields

**Food**:
- Cross-section views showing internal structure
- Texture appropriate to surface (smooth, rough, fibrous)
- Form-following shading
- Botanical accuracy for plants
- Appetizing presentation

**Animals**:
- Fur/feather direction shown with line flow
- Anatomical structure clear
- Eyes detailed and expressive
- Natural poses and proportions
- Environmental context

**Rope/Fiber**:
- Weave pattern visible
- Individual strands defined
- Twist direction consistent
- Fraying shown at ends
- Tension and drape natural

---

## Examples of Good Hand-Illustrative SVGs

### 1. Human Heart (Anatomy)
- Bold outer contour (2.5px)
- Chambers defined with medium lines (1.5px)
- Vessels with tapering lines
- Cross-contour shading following curved surfaces
- Stipple for muscle texture
- Labels with curved leader lines

### 2. Oak Leaf (Botany)
- Bold leaf outline with natural irregularity
- Veins in branching pattern (1.5px → 0.8px taper)
- Parallel wavy lines showing surface curvature
- Serrated edges defined
- Natural asymmetry

### 3. Mountain Landscape
- Background peaks with fine lines (0.8px)
- Midground trees with moderate detail
- Foreground rocks with dense stipple texture
- Water ripples in river
- Clouds using soft circular patterns
- Depth through line weight and detail variation

---

## Technical Constraints

**File Size**:
- Target: <50KB
- Optimize: Consolidate similar paths, remove redundant markup
- Keep: Natural organic quality, readable text

**Validation**:
- Must include: `viewBox`, `width`, `height`, `<title>`, `<desc>`
- Rounded line caps/joins: `stroke-linecap="round" stroke-linejoin="round"`
- Text must be editable: Use `<text>` elements, NOT `<path>`
- Natural curves: Use `<path>` with quadratic/cubic Beziers

**Accessibility**:
```xml
<title>Descriptive title</title>
<desc>Detailed description of illustrated subject</desc>
```

---

## Output Requirements

**Format**: Pure SVG code only
**Start with**: `<?xml version="1.0" encoding="UTF-8"?>`
**No explanations**: Just the SVG markup
**Validation**: Must render correctly in browsers
**Size check**: Keep under 50KB
**Aesthetic**: Traditional engraving/woodcut quality

Generate the SVG now.
