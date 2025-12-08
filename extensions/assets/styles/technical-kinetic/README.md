# Technical-Kinetic Style Guide

**Version:** 1.1.6
**Status:** Production Ready
**Author:** uDOS Design System---

## Overview

The **Technical-Kinetic** style is uDOS's signature aesthetic for SVG diagrams, combining **Mid-Century Modern (MCM) geometry** with **kinetic flow elements** to create monochrome, information-dense technical illustrations.

### Core Principles

1. **Monochrome Only**: Pure black (#000000) and white (#FFFFFF) - NO GRAY
2. **MCM Geometry**: Clean circles, rectangles, 45°/90° angles
3. **Kinetic Flow**: Exaggerated curves, gears, conduits to show motion
4. **Vector Patterns**: Hatching, stipple, wavy lines for shading (NO solid fills)
5. **Sans-Serif Typography**: Helvetica/Arial, 12-16pt headers, 8-10pt labels

---

## Diagram Types

### 1. Flowchart
Process diagrams with kinetic flow

**Required Elements:**
- Curved conduits with arrows
- Gears/cogs at decision points
- Exaggerated curves for motion
- Clear labels (8-10pt)
- Hatching for emphasis

**Example:** Water purification process, fire-starting sequence

### 2. Architecture
System structure diagrams

**Required Elements:**
- Perfect geometric shapes
- 45° or 90° connections
- Layered components
- Stipple backgrounds
- 2px structure / 3px emphasis

**Example:** Shelter structure, tool anatomy

### 3. Organic
Natural subjects with hand-drawn feel

**Required Elements:**
- Flowing outlines
- Wavy line shading
- Undulating patterns
- Varied line weight (2-3px)
- Leader line labels

**Example:** Plant identification, animal tracking

### 4. Schematic
Technical diagrams with measurements

**Required Elements:**
- Perfect proportions
- Dimension lines + arrows
- Annotation callouts
- Hatching for cross-sections
- Scale indicators

**Example:** Trap design, knot diagrams

---

## Reference Images

To ensure consistent style, load these reference images when generating diagrams using Nano Banana (Gemini 2.5 Flash Image):

| File | Demonstrates | Usage |
|------|--------------|-------|
| `01-flowchart-clean.png` | Curved conduits, kinetic flow | All flowcharts |
| `02-architecture-mcm.png` | MCM geometry, perfect shapes | Architecture diagrams |
| `03-kinetic-flow.png` | Gears, levers, motion | Process flows |
| `04-hatching-pattern.png` | Vector shading patterns | All shading/emphasis |
| `05-typography.png` | Sans-serif labels, sizing | All text elements |
| `06-curved-conduits.png` | Flow elements, arrows | Connections/flows |
| `07-gears-cogs.png` | Mechanical elements | Transformations/decisions |

### Creating Reference Images

⚠️ **IMPORTANT**: Reference images must be created manually to demonstrate the style accurately.

**Guidelines:**
1. Create in Inkscape, Adobe Illustrator, or similar vector tool
2. Export as high-resolution PNG (1200x900, 300dpi)
3. Use ONLY black (#000000) and white (#FFFFFF)
4. Demonstrate 2-3 specific elements per image
5. Keep files under 500KB each
6. Name files sequentially: `01-name.png`, `02-name.png`, etc.

**Placeholder Generation:**
```bash
# Generate placeholder reference images (basic examples)
python sandbox/scripts/generate_style_guide_placeholders.py technical-kinetic
```

---

## Generation Workflow

### Command-Line

```bash
# Single generation
GENERATE SVG "water purification filter" --style technical-kinetic --type flowchart

# With specific requirements
GENERATE SVG "shelter structure" --style technical-kinetic --type architecture \
  --requirements "show layers,add measurements,use stipple for ground"
```

### uCODE

```uscript
# Single diagram
[GENERATE|svg|water/filtration-system|style=technical-kinetic|type=flowchart]

# Batch generation
for category in $categories
  [GENERATE|svg|$category/overview|style=technical-kinetic|type=architecture]
  [GENERATE|svg|$category/process|style=technical-kinetic|type=flowchart]
done

# With validation
$svg_path = [GENERATE|svg|fire/bow-drill|style=technical-kinetic|type=schematic]
$validation = [VALIDATE|technical-kinetic|$svg_path]

if $validation.compliant = false then
  [LOG|WARN|Regenerating non-compliant SVG]
  [GENERATE|svg|fire/bow-drill|style=technical-kinetic|strict=true]
fi
```

---

## Pipeline Architecture

```
User Request
    │
    ├─→ 1. Load style.json + reference images (up to 14)
    │
    ├─→ 2. Build Technical-Kinetic prompt
    │
    ├─→ 3. Call Gemini 2.0 Flash (Nano Banana)
    │      → Returns high-quality PNG (1200x900, 300dpi)
    │      → Pure monochrome line art, 2-3px strokes
    │
    ├─→ 4. Vectorize PNG → SVG (potrace/vtracer)
    │      → Trace edges, preserve stroke weights
    │      → Generate clean SVG paths
    │
    ├─→ 5. Validate Technical-Kinetic compliance
    │      → Monochrome check
    │      → No gradients/raster/gray fills
    │      → Stroke consistency
    │
    └─→ 6. Save SVG to sandbox/drafts/svg/
```

---

## Validation Checklist

All generated SVGs must pass:

- ✅ Valid XML (well-formed SVG)
- ✅ Monochrome only (black/white, no gray)
- ✅ No gradients (linearGradient, radialGradient)
- ✅ No raster images (no `<image>` tags)
- ✅ No solid gray fills
- ✅ Consistent stroke width (2-3px)
- ✅ File size < 50KB

**Automated Validation:**
```python
from core.services.vectorizer import get_vectorizer_service

vectorizer = get_vectorizer_service()
validation = vectorizer.validate_technical_kinetic(svg_content)

if not validation["compliant"]:
    print("Validation errors:", validation["errors"])
```

---

## Examples

### Water Purification Flowchart
```
[Curved conduit with arrow] → [Gear decision point] → [Hatched filter]
     ↓                             ↓                        ↓
  Labels              Kinetic flow indicator         Vector shading
```

### Shelter Architecture
```
┌────────────────┐
│  Perfect rect  │  ← 90° angles, 2px stroke
│  Stipple bg    │  ← Vector pattern, not gray fill
└────────────────┘
```

---

## Troubleshooting

### Issue: Generated SVG has gray fills
**Solution:** Increase strictness in prompt, regenerate with `--strict` flag

### Issue: Vectorization produces jagged edges
**Solution:** Ensure PNG is high-res (1200x900), check potrace is installed

### Issue: Reference images not loading
**Solution:** Verify files exist in `extensions/assets/styles/technical-kinetic/references/`

### Issue: API returns text instead of image
**Solution:** Verify using Gemini 2.0 Flash Image model (not text model)

---

## Future Enhancements

- [ ] Multi-turn refinement with Nano Banana Pro
- [ ] Style guide versioning system
- [ ] Automated reference image generation
- [ ] Interactive style guide editor
- [ ] Real-time preview in web interface

---

**Document Status:** ✅ PRODUCTION READY
**Last Updated:** November 30, 2025
**Next Review:** December 2025
