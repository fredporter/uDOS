# Diagram Controls & Style Parameters

**v1.4.0 Phase 3 - Diagram & Sketch Controls**

Comprehensive control system for generating diagrams with consistent quality across complexity levels, styles, and perspectives.

---

## Table of Contents

1. [Complexity Controls](#complexity-controls)
2. [Style Variations](#style-variations)
3. [Perspective Options](#perspective-options)
4. [Annotation Layers](#annotation-layers)
5. [Format-Specific Controls](#format-specific-controls)
6. [Quality Parameters](#quality-parameters)
7. [Usage Examples](#usage-examples)

---

## Complexity Controls

### Simple (Essential Information Only)

**Target Audience:** Beginners, quick reference, emergency situations

**Specifications:**
- **Elements:** 3-5 key components maximum
- **Detail Level:** Essential information only
- **Labels:** Brief (1-3 words), large font
- **Instructions:** Critical steps only (3-5 steps max)
- **Colors:** 2-3 colors maximum (high contrast)
- **File Size:** <5KB (ASCII), <10KB (Teletext/SVG)

**When to Use:**
- Emergency quick-reference cards
- First-time learner guides
- Field identification charts
- Critical safety procedures

**Example: Simple Water Purification**
```
Components:
1. Dirty water container
2. Filter layers (combined visual)
3. Clean water container
4. One directional arrow

Labels: "IN", "FILTER", "OUT"
Steps: None (self-explanatory visual)
Colors: Blue (water), Gray (filter)
```

---

### Detailed (Comprehensive Information)

**Target Audience:** Learners, reference materials, training

**Specifications:**
- **Elements:** 6-12 components with relationships
- **Detail Level:** Comprehensive coverage of topic
- **Labels:** Descriptive (3-7 words), medium font
- **Instructions:** All important steps (6-12 steps)
- **Colors:** 4-6 colors (semantic coding)
- **File Size:** <15KB (ASCII), <30KB (Teletext/SVG)

**When to Use:**
- Training manuals
- Study guides
- Procedure documentation
- Skill development

**Example: Detailed Water Purification**
```
Components:
1. Water source (with quality indicators)
2. Pre-filter stage (cloth/gravel)
3. Main filter (sand, charcoal, gravel layers - separate)
4. Storage container
5. Boiling option (alternative)
6. Multiple arrows showing flow

Labels: "Dirty Water (may contain parasites)",
        "Pre-Filter: Remove Large Debris",
        "Sand Layer: 15cm", etc.
Steps: 1. Collect water, 2. Pre-filter, 3-4. Main filter,
       5. Boil 1 minute, 6. Store in clean container
Colors: Blue (dirty), Cyan (filtered), Yellow (caution),
        Gray (filter layers), Red (boil required)
```

---

### Technical (Expert-Level Precision)

**Target Audience:** Experts, engineers, detailed implementation

**Specifications:**
- **Elements:** 12+ components with detailed relationships
- **Detail Level:** Expert precision, all specifications
- **Labels:** Technical terminology, measurements, specs
- **Instructions:** Complete documentation (12-20 steps)
- **Colors:** Full palette (with semantic meaning)
- **File Size:** <25KB (ASCII), <50KB (Teletext/SVG)

**When to Use:**
- Engineering specifications
- Scientific documentation
- Detailed implementation guides
- Expert reference materials

**Example: Technical Water Purification**
```
Components:
1. Raw water input (with contamination types listed)
2. Sedimentation chamber (dimensions, residence time)
3. Coarse pre-filter (mesh size, material specs)
4. Activated charcoal layer (thickness, particle size, replacement schedule)
5. Fine sand layer (grain size distribution, depth)
6. Support gravel (gradation, depth)
7. Collection chamber
8. Overflow/backwash system
9. Multiple flow indicators
10. Pressure/flow rate measurements
11. Treatment effectiveness chart
12. Alternative configurations

Labels: "Input: 5-10 L/hr, turbidity <100 NTU",
        "Activated Charcoal: 10-15cm, 12×40 mesh,
         replace every 100L or 3 months", etc.
Dimensions: All in cm/mm, flow rates, volumes
Steps: Full construction and operation procedure
Colors: Color-coded contamination types, flow paths,
        effectiveness zones
```

---

## Style Variations

### Technical-Kinetic (Engineering Blueprint)

**Visual Characteristics:**
- Clean, precise lines (uniform 2-3px stroke weight)
- Perfect geometric alignment
- Grid-based layout
- Straight edges, 90° angles where possible
- Monospace or technical sans-serif fonts
- High precision, low organic feel

**Best For:**
- Engineering diagrams
- Construction plans
- Technical specifications
- Mechanical systems

**SVG Parameters:**
```python
{
    "stroke_width": "2px",
    "stroke_linecap": "square",
    "stroke_linejoin": "miter",
    "font_family": "monospace",
    "line_style": "straight",
    "alignment": "grid-snapped",
    "corner_radius": "0"
}
```

**Example Usage:**
- Shelter construction plans (precise measurements)
- Tool schematics (exact proportions)
- Fire lay structures (geometric arrangement)

---

### Hand-Illustrative (Sketch Notebook)

**Visual Characteristics:**
- Organic, slightly irregular strokes
- Natural line weight variation
- Hand-drawn appearance
- Curved edges, natural imperfections
- Handwriting-style or casual fonts
- High organic feel, approachable aesthetic

**Best For:**
- Field guides
- Nature identification
- Personal journals
- Educational materials

**SVG Parameters:**
```python
{
    "stroke_width": "1.5-3px (variable)",
    "stroke_linecap": "round",
    "stroke_linejoin": "round",
    "font_family": "cursive, casual sans-serif",
    "line_style": "slightly_wavy",
    "alignment": "natural",
    "corner_radius": "2-5px (variable)"
}
```

**Example Usage:**
- Plant identification guides
- Wildlife tracks
- Natural shelter designs
- Foraging maps

---

### Hybrid (Professional + Approachable)

**Visual Characteristics:**
- Mix of precise and organic elements
- Technical structure with hand-drawn details
- Grid layout with natural embellishments
- Straight main elements, curved details
- Clean sans-serif with hand-drawn accents
- Balanced precision and approachability

**Best For:**
- Training materials
- Public education
- Multi-audience guides
- Modern instructional design

**SVG Parameters:**
```python
{
    "stroke_width": "2px (structure), 1.5px (details)",
    "stroke_linecap": "round",
    "stroke_linejoin": "round",
    "font_family": "sans-serif (primary), cursive (accents)",
    "line_style": "straight (main), organic (secondary)",
    "alignment": "grid (structure), natural (details)",
    "corner_radius": "1-3px"
}
```

**Example Usage:**
- Medical procedures (precise + caring)
- Navigation techniques (technical + natural)
- Food preservation (modern + traditional)

---

## Perspective Options

### Isometric (30° 3D Projection)

**Specifications:**
- 30° angle from horizontal
- Three visible faces (top, front, right)
- No perspective distortion (parallel lines stay parallel)
- Equal scaling on all axes

**Best For:**
- Shelter construction
- 3D object assembly
- Layer visualization
- Spatial relationships

**Example:** Debris hut showing roof, front wall, and side wall

---

### Top-Down (Plan View)

**Specifications:**
- View from directly above
- Shows spatial layout
- Circular objects appear as circles
- Good for area/footprint

**Best For:**
- Site selection
- Floor plans
- Navigation maps
- Area coverage

**Example:** Campsite layout showing fire pit, shelter, water source positions

---

### Side (Elevation View)

**Specifications:**
- View from the side
- Shows vertical relationships
- Heights and depths clear
- Cross-sections effective

**Best For:**
- Layer diagrams
- Vertical construction
- Flow processes
- Height relationships

**Example:** Water filter showing vertical layers from top to bottom

---

### 3D Realistic (Perspective Rendering)

**Specifications:**
- Perspective distortion (distant objects smaller)
- Depth cues (shading, overlap)
- Realistic viewpoint
- Natural viewing angle

**Best For:**
- Photorealistic guides
- Complex assemblies
- Natural objects
- Contextual scenes

**Example:** Completed shelter in natural environment showing realistic perspective

---

## Annotation Layers

### Labels (Essential Text)

**Content:** Brief identifiers for components
**Placement:** Adjacent to objects, with leader lines if needed
**Font Size:** 12-16px (simple), 10-14px (detailed), 8-12px (technical)
**Style:** Plain text, high contrast

**Example:** "Water", "Sand Layer", "Output"

---

### Dimensions (Measurements)

**Content:** Sizes, distances, angles
**Placement:** Outside object boundaries with dimension lines
**Format:** Number + unit (e.g., "15cm", "30°", "5L")
**Style:** Technical font, dimension line arrows

**Example:** "←─ 15cm ─→", "⌀ 10cm", "30° angle"

---

### Callouts (Detailed Explanations)

**Content:** Extended descriptions, tips, context
**Placement:** Connected with leader lines, in margins
**Format:** Multi-line text in boxes/bubbles
**Style:** Smaller font, bordered containers

**Example:** "This layer removes particles >1mm. Replace after 100L throughput or when flow rate drops below 1L/hr."

---

### Notes (Additional Context)

**Content:** Tips, alternatives, related information
**Placement:** Bottom or side margins
**Format:** Numbered or bulleted lists
**Style:** Italic or distinguished font

**Example:** "Note: Activated charcoal can be made from hardwood in emergency situations."

---

### Warnings (Safety Information)

**Content:** Hazards, cautions, critical safety info
**Placement:** Prominent, near relevant components
**Format:** ⚠️ symbol + bold text
**Style:** High contrast (red/yellow), bordered

**Example:** "⚠️ BOIL ALL WATER 1 MINUTE after filtering to kill viruses and remaining bacteria"

---

## Format-Specific Controls

### ASCII Diagram Controls

**Grid:** 80×24 characters (standard terminal)
**Characters:** Box-drawing (─│┌┐└┘├┤┬┴┼), blocks (█▓▒░), ASCII art
**Limitations:** No curved lines, limited detail, monochrome
**Strengths:** Universal compatibility, tiny file size, CLI integration

**Control Parameters:**
```python
{
    "width": 80,
    "height": 24,
    "character_set": "box_drawing + blocks",
    "detail_level": "low_to_medium",
    "line_style": "straight",
    "shading": "block_density"  # █ ▓ ▒ ░
}
```

---

### Teletext Diagram Controls

**Grid:** 40×25 characters
**Blocks:** 2×3 mosaic cells (6 pixels per character)
**Colors:** 8-color palette (see TELETEXT_COLORS.md)
**Modes:** Contiguous/separated graphics, double-height

**Control Parameters:**
```python
{
    "width": 40,
    "height": 25,
    "color_palette": "wst_8_color",
    "graphics_mode": "separated",  # or "contiguous"
    "level": "2.5",  # 1, 2.5, or 3.5
    "double_height": False
}
```

---

### SVG Diagram Controls

**Canvas:** 800×600px default (scalable vector)
**Palette:** Mac OS System 1 (monochrome + 17 patterns)
**Precision:** Sub-pixel accuracy
**Features:** Gradients, patterns, filters, animations

**Control Parameters:**
```python
{
    "width": 800,
    "height": 600,
    "viewBox": "0 0 800 600",
    "palette": "macos_system1",
    "patterns": "bitmap_17_set",
    "stroke_width": "2-3px",
    "optimization": "production"
}
```

---

## Quality Parameters

### File Size Targets

- **ASCII:** <10KB (simple), <15KB (detailed), <25KB (technical)
- **Teletext:** <15KB (simple), <30KB (detailed), <40KB (technical)
- **SVG:** <25KB (simple), <35KB (detailed), <50KB (technical)

### Readability Standards

- **Minimum font size:** 8px (technical), 10px (detailed), 12px (simple)
- **Contrast ratio:** 4.5:1 minimum (WCAG AA), 7:1 preferred (AAA)
- **Line spacing:** 1.2-1.5× font size
- **Margin:** 5-10% of canvas on all sides

### Accessibility Requirements

- **Alt text:** All diagrams must have text descriptions
- **Color blindness:** Don't rely solely on color distinction
- **Screen readers:** Semantic structure, ARIA labels
- **Keyboard nav:** Interactive elements must be keyboard-accessible

---

## Usage Examples

### Example 1: Simple ASCII Fire Triangle

```python
from enhanced_prompts import create_enhanced_prompt, COMPLEXITY_SIMPLE, STYLE_TECHNICAL

prompt = create_enhanced_prompt(
    category="fire",
    topic="Fire Triangle",
    description="Basic fire triangle showing heat, fuel, oxygen",
    format_type="ascii",
    complexity=COMPLEXITY_SIMPLE,
    style=STYLE_TECHNICAL,
    annotations=["labels"]
)
```

### Example 2: Detailed SVG Water Filter

```python
from enhanced_prompts import create_enhanced_prompt, COMPLEXITY_DETAILED, STYLE_HYBRID

prompt = create_enhanced_prompt(
    category="water",
    topic="DIY Water Filter",
    description="Multi-layer water filter with sand, charcoal, gravel",
    format_type="svg",
    complexity=COMPLEXITY_DETAILED,
    style=STYLE_HYBRID,
    perspective="side",
    annotations=["labels", "dimensions", "callouts", "warnings"]
)
```

### Example 3: Technical Teletext CPR Procedure

```python
from enhanced_prompts import create_enhanced_prompt, COMPLEXITY_TECHNICAL, STYLE_TECHNICAL

prompt = create_enhanced_prompt(
    category="medical",
    topic="CPR Procedure",
    description="Complete CPR procedure with hand positions, compression depth, timing",
    format_type="teletext",
    complexity=COMPLEXITY_TECHNICAL,
    style=STYLE_TECHNICAL,
    perspective="top-down",
    annotations=["labels", "dimensions", "warnings", "notes"]
)
```

---

## Control Presets

### Quick Presets for Common Scenarios

**Emergency Reference Card:**
- Complexity: Simple
- Style: Technical
- Annotations: Labels only
- Format: ASCII (portable)

**Training Manual:**
- Complexity: Detailed
- Style: Hybrid
- Annotations: Labels, Callouts, Notes
- Format: SVG (quality)

**Expert Documentation:**
- Complexity: Technical
- Style: Technical
- Annotations: All types
- Format: SVG (precision)

**Field Guide:**
- Complexity: Detailed
- Style: Hand-Illustrative
- Annotations: Labels, Notes
- Format: SVG (illustrations)

---

**Version:** 1.0
**Last Updated:** November 25, 2025
**Author:** uDOS Development Team
**License:** See LICENSE.txt
