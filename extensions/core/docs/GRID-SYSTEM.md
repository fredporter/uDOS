# uDOS Grid System v1.2

16×16 pixel uCELL layout with Monaspace text block characters for consistent terminal and web interfaces.

## Overview

The uDOS Grid System provides a standardized layout framework based on the Display System specification:

- **uCELL**: 16×16 pixel base unit for all interface elements
- **uGRID**: Tile-based layout system with preset sizes
- **Text Block Characters**: Monaspace font symbols for UI elements
- **Box Drawing**: ASCII art borders and frames
- **Synthwave DOS Palette**: 8-color standard theme

## Files

- `udos-grid.css` - Complete grid system stylesheet
- `ugrid-demo.html` - Interactive demonstration and examples
- Integration in `dashboard/` and `terminal/` extensions

## Quick Start

```html
<!-- Include in your HTML -->
<link rel="stylesheet" href="../shared/udos-grid.css">
```

### Basic uCELL

```html
<div class="ucell ucell-buffer">
    A
</div>
```

### Header Bar

```html
<div class="ugrid-header">
    🚀 uDOS v1.2 Terminal
</div>
```

### Menu Grid (2×3)

```html
<div class="ugrid-menu">
    <div class="ugrid-menu-item">FILE</div>
    <div class="ugrid-menu-item">EDIT</div>
    <div class="ugrid-menu-item">VIEW</div>
    <div class="ugrid-menu-item">TOOLS</div>
    <div class="ugrid-menu-item">HELP</div>
    <div class="ugrid-menu-item">EXIT</div>
</div>
```

### Status Display

```html
<div class="ugrid-status">
    <span>Status: <span class="color-green">✓ Active</span></span>
    <span>User: <span class="color-cyan">Admin</span></span>
</div>
```

## Grid Sizes

| Size | Grid | Device | Use |
|------|------|--------|-----|
| Wearable | 16×16 | Watch | Single widget |
| Mobile | 40×16 | Phone | Compact interface |
| Terminal | 80×30 | Desktop | Standard CLI |
| Dashboard | 120×48 | Large | Multi-panel |

### Usage

```html
<div class="ugrid ugrid-terminal">
    <!-- 80×30 grid of uCELLs -->
</div>
```

## Text Block Characters

### Block Fills

```html
<span class="block-25">░</span>  <!-- 25% fill -->
<span class="block-50">▒</span>  <!-- 50% fill -->
<span class="block-75">▓</span>  <!-- 75% fill -->
<span class="block-full">█</span>  <!-- 100% fill -->
```

### Box Drawing

```
┌─────────────────┐
│  Header Text    │
├─────────────────┤
│  Content Area   │
└─────────────────┘
```

Characters:
- Lines: `─ │`
- Corners: `┌ ┐ └ ┘`
- Joins: `├ ┤ ┬ ┴ ┼`

### Arrows

```html
<span class="arrow-up">↑</span>
<span class="arrow-down">↓</span>
<span class="arrow-left">←</span>
<span class="arrow-right">→</span>
```

8-directional: `← → ↑ ↓ ↖ ↗ ↘ ↙`

### Symbols

```html
<span class="check color-green">✓</span> Success
<span class="cross-mark color-red">✗</span> Error
<span class="bullet">•</span> List item
<span class="circle">●</span> Status
<span class="square">■</span> Box
<span class="diamond">◆</span> Diamond
```

## Color Palette (Synthwave DOS)

```html
<span class="color-red">Red text</span>
<div class="bg-green">Green background</div>
```

Colors:
- `color-red` / `bg-red` - #FF1744
- `color-green` / `bg-green` - #00E676
- `color-yellow` / `bg-yellow` - #FFEB3B
- `color-blue` / `bg-blue` - #2196F3
- `color-purple` / `bg-purple` - #E91E63
- `color-cyan` / `bg-cyan` - #00E5FF
- `color-white` / `bg-white` - #FFFFFF
- `color-black` / `bg-black` - #000000

## Coordinate System

Zero-indexed positioning (x, y):

```
     0   1   2   3
   ┌───┬───┬───┬───┐
0  │0,0│1,0│2,0│3,0│
   ├───┼───┼───┼───┤
1  │0,1│1,1│2,1│3,1│
   └───┴───┴───┴───┘
```

```html
<div class="ugrid-custom" style="grid-template-columns: repeat(4, var(--ucell-size))">
    <div class="upos-0-0">0,0</div>
    <div class="upos-1-0">1,0</div>
    <!-- etc -->
</div>
```

## Pre-built Components

### ASCII Box

```html
<div class="ascii-box">
┌─────────────────────────┐
│   Box Title             │
├─────────────────────────┤
│   Content line 1        │
│   Content line 2        │
└─────────────────────────┘
</div>
```

### Status Box

```html
<div class="ascii-status-box">
System Status: ✓ Online
Connections: 5 active
Uptime: 24h 15m
</div>
```

### Progress Bar (Block Characters)

```html
<div class="block-progress">
    <span class="block-progress-fill">████████</span>
    <span class="block-progress-empty">░░</span>
</div>
```

### uCELL Indicators

```html
<span class="ucell-indicator online"></span>  <!-- ● green -->
<span class="ucell-indicator offline"></span> <!-- ○ gray -->
<span class="ucell-indicator warning"></span> <!-- ⚠ yellow -->
<span class="ucell-indicator error"></span>   <!-- ✗ red -->
```

### Navigation Arrows

```html
<span class="nav-arrow">←</span>
<span class="nav-arrow">→</span>
<span class="nav-arrow disabled">↑</span>
```

## uCELL Specification

```
┌────────────────┐ 16px total
│ ░░░░░░░░░░░░░░ │
│ ░████████████░ │ ← 2px buffer
│ ░█  CONTENT █░ │ ← 12×12 content area
│ ░████████████░ │
│ ░░░░░░░░░░░░░░ │
└────────────────┘
```

- **Total Size**: 16×16 pixels
- **Buffer**: 2px border around content
- **Content Area**: 12×12 pixels
- **Font**: Monaspace at 12px
- **Line Height**: 16px
- **Baseline**: Row 9 of 16

## CSS Variables

```css
:root {
    /* uCELL Dimensions */
    --ucell-size: 16px;
    --ucell-buffer: 2px;
    --ucell-content: 12px;

    /* Text Block Characters */
    --char-block-25: '░';
    --char-block-50: '▒';
    --char-block-75: '▓';
    --char-block-full: '█';

    /* Line Drawing */
    --char-h-line: '─';
    --char-v-line: '│';
    --char-tl-corner: '┌';
    /* etc */
}
```

## Responsive Scaling

The grid automatically scales on smaller screens:

- **Desktop**: 16px cells
- **Tablet**: 12px cells
- **Mobile**: 10px cells

## Integration Examples

### Dashboard Tile with uGrid

```html
<div class="tile">
    <div class="tile-header">
        <span class="ucell-indicator online"></span>
        <span class="nav-arrow">→</span>
    </div>
    <div class="ascii-status-box">
    Status: ✓ Running
    Port: 8890
    </div>
</div>
```

### Terminal with Box Border

```html
<div class="terminal-box">
┌─────────────────────────────┐
│  🔮 uDOS CMD Terminal       │
├─────────────────────────────┤
│  $ status                   │
│  ✓ System Online            │
│  ✓ 5 servers running        │
└─────────────────────────────┘
</div>
```

## Demo

Open `ugrid-demo.html` in a browser to see all components in action.

**Keyboard Shortcuts**:
- `T` - Toggle light/dark theme

## Browser Support

- Chrome/Edge 90+
- Firefox 88+
- Safari 14+

Requires support for:
- CSS Grid
- CSS Custom Properties
- Unicode box drawing characters

## Font Requirements

- **Monaspace** - Primary monospace font
- **Noto Color Emoji** - Emoji support

Both are loaded via CDN in the demo files.

## Best Practices

1. **Consistent Spacing**: Always use 16×16 cell multiples
2. **Buffer Space**: Leave 2px buffer for readability
3. **Monospace Font**: Use Monaspace for exact character spacing
4. **Color Contrast**: Follow Synthwave DOS palette for accessibility
5. **Grid Alignment**: Align elements to grid boundaries

## Performance

- **Lightweight**: < 10KB CSS (uncompressed)
- **No JavaScript**: Pure CSS implementation
- **GPU Accelerated**: Uses CSS Grid for performance
- **Print Ready**: Includes print styles

## Credits

Based on the uDOS Display System specification from v1.0.4, modernized for v1.2 with:
- Monaspace font integration
- Web component styling
- Responsive grid system
- Flat design aesthetic

---

**uDOS v1.2** - Simple, lean, fast
