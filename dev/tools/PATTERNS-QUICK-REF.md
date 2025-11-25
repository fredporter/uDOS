# Mac OS System 1 Patterns - Quick Reference

## Grayscale Patterns

```
gray-12   ░         12.5%   Very light tint
gray-25   ░░        25%     Light backgrounds
gray-37   ░░░       37.5%   Light-medium tone
gray-50   ▒▒        50%     Balanced mid-tone
gray-62   ▓▓▓       62.5%   Medium-dark shading
gray-75   ▓▓▓▓      75%     Dark backgrounds
gray-87   ▓▓▓▓▓     87.5%   Very dark
black     ████      100%    Solid black
white     ----      0%      Solid white
```

## Texture Patterns

```
brick         ▞▚    Masonry, stone walls
diagonal      ╱╱╱   Direction, metal, structure
cross-hatch   ┼┼┼   Dense materials, cast iron
horizontal    ═══   Layers, stratification
vertical      ║║║   Wood grain, columns
dots          ∙∙∙   Soft materials, clouds
scales        ◠◡◠   Fish scales, roof tiles
grid          ┌┬┐   Technical drawings
waves         ≈≈≈   Water, organic flow
herringbone   ><    Decorative textiles
```

## Common Material Mappings

```
WATER FILTER:
  Cloth    → cross-hatch
  Charcoal → gray-75
  Sand     → gray-37
  Gravel   → dots

STRUCTURAL:
  Metal    → cross-hatch, diagonal
  Stone    → brick, scales
  Wood     → vertical, horizontal
  Glass    → gray-25, gray-12

ORGANIC:
  Skin     → dots (light)
  Fabric   → herringbone, grid
  Water    → gray-37, waves
  Soil     → gray-50, dots
```

## SVG Usage

```xml
<!-- Grayscale -->
<rect fill="url(#gray-50)" stroke="#000" stroke-width="2"/>

<!-- Texture -->
<rect fill="url(#brick)" stroke="#000" stroke-width="2"/>

<!-- Text (monospace) -->
<text font-family="monospace" font-size="14" font-weight="bold">
  Label
</text>
```

## Stroke Weights

```
Primary:   2-3px    Main outlines
Secondary: 1.5px    Detail lines
Fine:      1px      Annotations
```

## Text Sizes

```
Title:  18-28px bold
Label:  14-16px bold
Body:   11-13px
Notes:  9-11px
```

## Rules

```
✓ Pattern-based grays ONLY
✓ Generic monospace font
✓ Bold geometric style
✓ 8×8 pixel patterns
✓ <text> elements (never paths)

✗ NO solid grays (#808080)
✗ NO opacity/transparency
✗ NO anti-aliasing
```

---

**Test Generator:** `python dev/tools/test_creative_patterns.py`
**Full Guide:** `dev/tools/MAC-OS-PATTERNS-GUIDE.md`
