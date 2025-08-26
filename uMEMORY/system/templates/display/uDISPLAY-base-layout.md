# uGRID Display Template - Base Layout

**Template**: uDISPLAY-base-layout.md
**Version**: v1.0.4.1
**Purpose**: Base 16×16 uCELL grid layout system
**Integration**: uGRID, uCELL, uTILE architecture

---

## 🎯 Base uCELL Template (16×16)

### Standard uCELL Layout
```
┌────────────────┐ 16px width
│ ░░░░░░░░░░░░░░ │
│ ░████████████░ │ ← 2px buffer (optional)
│ ░█          █░ │ ← 12×12 content area
│ ░█  [CONTENT]█░ │ ← baseline row 9
│ ░█          █░ │
│ ░████████████░ │
│ ░░░░░░░░░░░░░░ │
└────────────────┘ 16px height
```

### Text Box Configurations

#### 12×12 Default (2px buffer)
```css
.ucell-12x12 {
    width: 16px;
    height: 16px;
    padding: 2px;
    font-family: var(--font-primary);
    font-size: 10px;
    line-height: 12px;
}
```

#### 14×14 Compact (1px buffer)
```css
.ucell-14x14 {
    width: 16px;
    height: 16px;
    padding: 1px;
    font-family: var(--font-retro);
    font-size: 11px;
    line-height: 14px;
}
```

#### 10×10 Extended (3px buffer)
```css
.ucell-10x10 {
    width: 16px;
    height: 16px;
    padding: 3px;
    font-family: var(--font-display);
    font-size: 8px;
    line-height: 10px;
}
```

#### 16×16 Edge-to-edge (no buffer)
```css
.ucell-16x16 {
    width: 16px;
    height: 16px;
    padding: 0;
    font-family: var(--font-pixel);
    font-size: 12px;
    line-height: 16px;
}
```

---

## 🎨 Font Stack Integration

### CSS Variables (from font registry)
```css
:root {
    --font-primary: IBM Plex Mono, Menlo, Consolas, DejaVu Sans Mono, monospace;
    --font-retro: VT323, Press Start 2P, Silkscreen, Courier New, monospace;
    --font-display: Major Mono Display, Space Mono, Impact, monospace;
    --font-code: Fira Code, IBM Plex Mono, Hack, Menlo, Consolas, monospace;
    --font-terminal: VT323, Ubuntu Mono, DejaVu Sans Mono, Courier New, monospace;
    --font-pixel: Silkscreen, Press Start 2P, Courier New, monospace;
    --font-lcd: DSEG7 Classic, Major Mono Display, Courier New, monospace;
    --font-c64: C64 Pro Mono, VT323, Courier New, monospace;
}
```

### Context-Specific Font Usage
```css
/* Terminal display */
.display-terminal {
    font-family: var(--font-terminal);
    background: #000;
    color: #00ff00;
}

/* Web interface */
.display-web {
    font-family: var(--font-primary);
    background: #ffffff;
    color: #333333;
}

/* Retro mode */
.display-retro {
    font-family: var(--font-retro);
    background: #001122;
    color: #ffff00;
}

/* Code display */
.display-code {
    font-family: var(--font-code);
    background: #1e1e1e;
    color: #d4d4d4;
}
```

---

## 🔄 4× Resolution System

### Enhanced Detail Grid (64×64 effective)
```
Base uCELL 16×16        →     4×4 overlay (64×64)
┌────────────────┐             ┌─┬─┬─┬─┐
│                │             │1│2│3│4│
│                │      →      ├─┼─┼─┼─┤
│                │             │5│6│7│8│
│                │             ├─┼─┼─┼─┤
└────────────────┘             └─┴─┴─┴─┘
```

### 4× CSS Grid Implementation
```css
.ucell-4x {
    display: grid;
    grid-template-columns: repeat(4, 1fr);
    grid-template-rows: repeat(4, 1fr);
    width: 16px;
    height: 16px;
    gap: 0;
}

.ucell-4x .subpixel {
    width: 4px;
    height: 4px;
    font-size: 2px;
}
```

---

## 🎯 uCELL States

### State Classes
```css
/* Active tile */
.ucell.active {
    border: 1px solid var(--color-blue);
    box-shadow: 0 0 4px var(--color-blue);
}

/* Inactive tile */
.ucell.inactive {
    opacity: 0.7;
    border: 1px solid transparent;
}

/* Disabled tile */
.ucell.disabled {
    opacity: 0.3;
    pointer-events: none;
    filter: grayscale(100%);
}

/* Hidden tile */
.ucell.hidden {
    display: none;
}

/* Overlay tile */
.ucell.overlay {
    position: absolute;
    background: rgba(255, 255, 255, 0.9);
    backdrop-filter: blur(2px);
}
```

---

## 📐 Grid Layout Examples

### 4×4 Grid (64×64 total)
```html
<div class="ugrid ugrid-4x4">
    <div class="ucell ucell-12x12">A1</div>
    <div class="ucell ucell-12x12">A2</div>
    <div class="ucell ucell-12x12">A3</div>
    <div class="ucell ucell-12x12">A4</div>
    <div class="ucell ucell-12x12">B1</div>
    <!-- ... etc -->
</div>
```

### 8×8 Grid (128×128 total)
```html
<div class="ugrid ugrid-8x8">
    <!-- 64 uCELLs total -->
</div>
```

### Terminal Grid (80×24 equivalent)
```html
<div class="ugrid ugrid-terminal display-terminal">
    <!-- Sized for 80×24 character terminal -->
</div>
```

---

## 🎨 Color Palette Integration

### Polaroid Palette (Default)
```css
.palette-polaroid {
    --color-red: #FF1744;
    --color-green: #00E676;
    --color-yellow: #FFEB3B;
    --color-blue: #2196F3;
    --color-purple: #E91E63;
    --color-cyan: #00E5FF;
    --color-white: #FFFFFF;
    --color-black: #000000;
}
```

### Terminal ANSI Colors
```css
.display-terminal {
    --ansi-0: var(--color-black);
    --ansi-1: var(--color-red);
    --ansi-2: var(--color-green);
    --ansi-3: var(--color-yellow);
    --ansi-4: var(--color-blue);
    --ansi-5: var(--color-purple);
    --ansi-6: var(--color-cyan);
    --ansi-7: var(--color-white);
}
```

---

## 🚀 Usage Examples

### Simple Text Display
```html
<div class="ucell ucell-12x12">
    TEXT
</div>
```

### Icon Display (4× resolution)
```html
<div class="ucell ucell-4x">
    <div class="subpixel"></div>
    <div class="subpixel active"></div>
    <div class="subpixel active"></div>
    <div class="subpixel"></div>
    <!-- 12 more subpixels for icon -->
</div>
```

### Status Indicator
```html
<div class="ucell ucell-16x16 overlay">
    <span class="status-dot active"></span>
</div>
```

---

*uDOS v1.0.4.1 Display Template - uGRID Base Layout*
*Foundation for all uCELL, uTILE, and uMAP display systems*
