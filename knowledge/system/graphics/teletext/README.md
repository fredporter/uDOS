# Teletext Graphics Reference

Complete reference for teletext block graphics, colors, and effects in uDOS.

## Overview

Teletext graphics use Unicode block-drawing characters to create visual displays in text mode. This system provides extensive pattern support for:

- Maps and terrain visualization
- Data charts and graphs
- Progress bars and meters
- Decorative borders and frames
- ASCII art and diagrams

## Quick Reference

### Basic Blocks

```
█ full      Full block (solid)
▓ dark      Dark shade (75%)
▒ medium    Medium shade (50%)
░ light     Light shade (25%)
```

### Half Blocks

```
▀ top       Upper half block
▄ bottom    Lower half block
▌ left      Left half block
▐ right     Right half block
```

### Quarter Blocks

```
▘ topleft      Top-left quarter
▝ topright     Top-right quarter
▖ bottomleft   Bottom-left quarter
▗ bottomright  Bottom-right quarter
```

### Mosaic Patterns

```
▚ checkerboard  Alternating pattern
▞ diagonal1     Diagonal pattern
```

## Box Drawing Characters

### Single Line

```
┌ ┬ ┐  Top row
├ ┼ ┤  Middle row
└ ┴ ┘  Bottom row
─ │    Lines (horizontal, vertical)
```

### Double Line

```
╔ ╦ ╗  Top row
╠ ╬ ╣  Middle row
╚ ╩ ╝  Bottom row
═ ║    Lines (horizontal, vertical)
```

### Rounded Corners

```
╭ ─ ╮  Top
│   │  Sides
╰ ─ ╯  Bottom
```

## Terrain Characters

For map visualization:

```
Ocean/Water:
  █ ocean_deep      Deep ocean (darkest)
  ▓ ocean           Ocean
  ▒ ocean_shallow   Shallow water
  ░ coast           Coastal areas
  ≈ water           Generic water
  ~ river           Rivers
  ○ lake            Lakes

Land:
  · plains          Plains/grassland
  ≈ grassland       Grassland
  ♠ forest          Forest areas
  ♣ jungle          Dense jungle
  ∴ desert          Desert/sand
  ∙ tundra          Tundra
  ❄ ice             Ice/snow

Elevation:
  ∩ hills           Hills
  ▲ mountains       Mountains
  ▲ peaks           Mountain peaks

Urban:
  ▪ urban           Urban areas
  ■ city            Cities
  ● metro           Metropolitan areas
```

## ANSI Color Codes

### Foreground Colors

```
black, red, green, yellow, blue, magenta, cyan, white
```

### Background Colors

```
bg_black, bg_red, bg_green, bg_yellow, bg_blue, bg_magenta, bg_cyan, bg_white
```

### Text Effects

```
bold        Bold/bright text
dim         Dimmed text
italic      Italic text
underline   Underlined text
blink       Blinking text (slow)
reverse     Reversed colors
hidden      Hidden/concealed text
```

## Pattern Examples

### Gradient Pattern

```
████████████░░░░
███████████▓░░░░
██████████▒▓░░░░
█████████░▒▓░░░░
```

Uses: `gradient` pattern or sequence `█▓▒░`

### Checkerboard Pattern

```
█░█░█░█░
░█░█░█░█
█░█░█░█░
░█░█░█░█
```

Uses: `checkerboard` pattern

### Wave Pattern

```
≈~≈~≈~≈~≈~
~≈~≈~≈~≈~≈
≈~≈~≈~≈~≈~
```

Uses: `waves` pattern

### Progress Bar Styles

**Style 1: Block-based**
```
[████████████████████░░░░░░░░] 75%
```

**Style 2: Gradient**
```
[████████▓▓▓▓▒▒▒▒░░░░        ] 60%
```

**Style 3: Numeric**
```
Progress: ████████▓▓░░░░░░░░░░ 40/100
```

## Usage in uSCRIPT

### Creating Patterns

```
# Create panel
[PANEL|CREATE*terrain_demo*40*20*7]

# Fill with gradient
[PANEL|PATTERN*terrain_demo*0*0*40*5*gradient]

# Add ocean
[PANEL|TERRAIN*terrain_demo*0*5*40*8*ocean]

# Add forest
[PANEL|TERRAIN*terrain_demo*0*13*40*7*forest]

# Display
[PANEL|SHOW*terrain_demo]
```

### Block-by-Block Drawing

```
# Create canvas
[PANEL|CREATE*canvas*30*15*7]

# Draw ocean
[PANEL|BLOCK*canvas*0*0*ocean_deep]
[PANEL|BLOCK*canvas*1*0*ocean]
[PANEL|BLOCK*canvas*2*0*ocean_shallow]

# Draw coastline
[PANEL|FILL*canvas*3*0*1*15*coast]

# Draw land
[PANEL|TERRAIN*canvas*4*0*26*15*plains]
```

### Color Application

```
# Create colored display
[PANEL|CREATE*colored*40*10*7]

# Write text
[PANEL|WRITE*colored*10*5*STATUS: ONLINE]

# Apply green color
[PANEL|COLOR*colored*10*5*13*1*green]

# Display
[PANEL|SHOW*colored]
```

## Map Visualization

### Ocean Depth Levels

```
Depth Scale:
█ 0-1000m   (Deep ocean)
▓ 1000-200m (Ocean)
▒ 200-50m   (Shallow)
░ 0-50m     (Coast)
```

### Elevation Levels

```
Height Scale:
▲ 3000m+    (Peaks)
∩ 1000-3000m (Mountains)
· 500-1000m  (Hills)
· 0-500m     (Plains)
```

### Vegetation Density

```
Density Scale:
♣ Dense (Jungle)
♠ Medium (Forest)
≈ Light (Grassland)
· Sparse (Plains)
```

## Integration Examples

### Example 1: Simple Terrain Map

```
Ocean (█▓▒░) | Coast | Plains (·) | Forest (♠) | Mountains (∩▲)
█████▓▓▓▒▒▒░░······≈≈≈♠♠♠♠∩∩∩▲
```

### Example 2: Weather Map

```
☀ Clear
☁ Cloudy  ░░░
🌧 Rain   ▒▒▒
⛈ Storm   ▓▓▓
❄ Snow    ███
```

### Example 3: Population Density

```
░ Rural
▒ Suburban
▓ Urban
█ Metro
```

## Best Practices

1. **Consistency**: Use same character for same meaning across project
2. **Contrast**: Ensure patterns are distinguishable
3. **Performance**: Large panels may render slowly
4. **Accessibility**: Provide text labels for screen readers
5. **Documentation**: Document custom pattern meanings

## File Formats

All patterns can be:
- Embedded in markdown via `PANEL EMBED`
- Displayed in terminal via `PANEL SHOW`
- Stored in panel buffers for programmatic access

## Related Commands

- `PANEL CREATE` - Create display panel
- `PANEL BLOCK` - Place single block
- `PANEL PATTERN` - Fill with pattern
- `PANEL TERRAIN` - Fill with terrain
- `PANEL COLOR` - Apply colors
- `PANEL SHOW` - Display panel

## Version History

- **v1.0.21** - Initial teletext graphics system
  - Basic blocks, terrain patterns, colors
  - Pattern fill capabilities
  - Map visualization support

---

**uDOS v1.0.21** - Text-first computing for a resilient future.
