# uGRID Retro Display Template

**Template**: uDISPLAY-retro-pixel.md
**Version**: v1.0.4.1
**Purpose**: Retro gaming and pixel art display layouts
**Integration**: Press Start 2P, Silkscreen, pixel-perfect rendering

---

## 🕹️ Retro Display Architecture

### Pixel-Perfect Configuration
```css
.display-retro {
    font-family: var(--font-pixel);
    background: #001122;
    color: #ffff00;
    image-rendering: pixelated;
    image-rendering: -moz-crisp-edges;
    image-rendering: crisp-edges;
    -webkit-font-smoothing: none;
    font-smooth: never;
}
```

### Font Specifications

#### Press Start 2P (8-bit gaming)
```css
.font-8bit {
    font-family: 'Press Start 2P', 'Courier New', monospace;
    font-size: 8px;
    line-height: 16px;
    letter-spacing: 1px;
}
```

#### Silkscreen (pixel art)
```css
.font-pixel {
    font-family: 'Silkscreen', 'Press Start 2P', monospace;
    font-size: 12px;
    line-height: 16px;
    font-weight: 400;
}
```

#### C64 Pro Mono (Commodore 64)
```css
.font-c64 {
    font-family: var(--font-c64);
    font-size: 14px;
    line-height: 16px;
    color: #40e0d0;
    background: #40108a;
}
```

---

## 🎨 Retro Color Palettes

### Classic Arcade
```css
.palette-arcade {
    --arcade-bg: #000000;
    --arcade-fg: #ffffff;
    --arcade-red: #ff0040;
    --arcade-green: #00ff40;
    --arcade-blue: #4080ff;
    --arcade-yellow: #ffff00;
    --arcade-magenta: #ff40ff;
    --arcade-cyan: #40ffff;
}
```

### Commodore 64
```css
.palette-c64 {
    --c64-blue: #40108a;
    --c64-light-blue: #40e0d0;
    --c64-white: #ffffff;
    --c64-red: #883932;
    --c64-purple: #8b3f96;
    --c64-green: #55a049;
    --c64-dark-blue: #40318d;
    --c64-yellow: #bfce72;
    --c64-orange: #8b5429;
    --c64-brown: #574200;
    --c64-light-red: #b86962;
    --c64-dark-gray: #505050;
    --c64-medium-gray: #787878;
    --c64-light-green: #94e089;
    --c64-light-purple: #b86adb;
    --c64-light-gray: #9f9f9f;
}
```

### Game Boy Green
```css
.palette-gameboy {
    --gb-darkest: #0f380f;
    --gb-dark: #306230;
    --gb-light: #8bac0f;
    --gb-lightest: #9bbc0f;
}
```

### NES Palette
```css
.palette-nes {
    --nes-gray: #7c7c7c;
    --nes-blue: #0000fc;
    --nes-dark-blue: #0000bc;
    --nes-purple: #4428bc;
    --nes-dark-purple: #940084;
    --nes-red: #a80020;
    --nes-dark-red: #a81000;
    --nes-orange: #881400;
    --nes-brown: #503000;
    --nes-dark-green: #007800;
    --nes-green: #00b800;
    --nes-light-green: #58d854;
    --nes-yellow: #58f898;
    --nes-white: #fcfcfc;
}
```

---

## 📐 Pixel Grid Layouts

### 8×8 Sprite Grid
```html
<div class="ugrid sprite-8x8">
    <div class="pixel"></div>
    <div class="pixel active"></div>
    <div class="pixel active"></div>
    <div class="pixel"></div>
    <!-- 60 more pixels -->
</div>
```

```css
.sprite-8x8 {
    display: grid;
    grid-template-columns: repeat(8, 1fr);
    grid-template-rows: repeat(8, 1fr);
    width: 64px;
    height: 64px;
    gap: 0;
}

.pixel {
    width: 8px;
    height: 8px;
    background: transparent;
}

.pixel.active {
    background: currentColor;
}
```

### 16×16 Character Block
```css
.char-16x16 {
    display: grid;
    grid-template-columns: repeat(16, 1fr);
    grid-template-rows: repeat(16, 1fr);
    width: 128px;
    height: 128px;
    font-family: var(--font-pixel);
}
```

### 32×32 Icon Grid
```css
.icon-32x32 {
    display: grid;
    grid-template-columns: repeat(32, 1fr);
    grid-template-rows: repeat(32, 1fr);
    width: 256px;
    height: 256px;
    image-rendering: pixelated;
}
```

---

## 🎮 Gaming UI Components

### Health Bar
```html
<div class="health-bar">
    <div class="health-label">HP:</div>
    <div class="health-container">
        <div class="health-fill" style="width: 75%"></div>
    </div>
    <div class="health-text">75/100</div>
</div>
```

```css
.health-bar {
    display: flex;
    align-items: center;
    font-family: var(--font-8bit);
    font-size: 8px;
    color: #ffffff;
}

.health-container {
    width: 100px;
    height: 12px;
    border: 2px solid #ffffff;
    background: #000000;
    margin: 0 8px;
}

.health-fill {
    height: 100%;
    background: linear-gradient(to right, #ff0000, #ffff00, #00ff00);
    transition: width 0.3s ease;
}
```

### Score Display
```html
<div class="score-display">
    <div class="score-label">SCORE</div>
    <div class="score-value">012350</div>
</div>
```

```css
.score-display {
    font-family: var(--font-8bit);
    font-size: 12px;
    color: #ffff00;
    text-align: center;
    text-shadow: 2px 2px 0px #000000;
}

.score-value {
    font-size: 16px;
    letter-spacing: 2px;
}
```

### Dialogue Box
```html
<div class="dialogue-box">
    <div class="dialogue-border">
        <div class="dialogue-content">
            <div class="dialogue-speaker">NPC:</div>
            <div class="dialogue-text">
                Welcome to uDOS! Press SPACE to continue...
            </div>
        </div>
    </div>
</div>
```

```css
.dialogue-box {
    position: relative;
    width: 400px;
    height: 120px;
    font-family: var(--font-8bit);
}

.dialogue-border {
    border: 4px solid #ffffff;
    background: #000080;
    height: 100%;
    padding: 16px;
    box-shadow: 4px 4px 0px #000000;
}

.dialogue-speaker {
    color: #ffff00;
    font-weight: bold;
    margin-bottom: 8px;
}

.dialogue-text {
    color: #ffffff;
    line-height: 16px;
}
```

---

## 🔮 Retro Effects

### Scanlines Effect
```css
.scanlines {
    position: relative;
    overflow: hidden;
}

.scanlines::before {
    content: '';
    position: absolute;
    top: 0;
    left: 0;
    right: 0;
    bottom: 0;
    background: repeating-linear-gradient(
        0deg,
        transparent,
        transparent 2px,
        rgba(0, 0, 0, 0.1) 2px,
        rgba(0, 0, 0, 0.1) 4px
    );
    pointer-events: none;
}
```

### Pixel Shimmer
```css
@keyframes pixel-shimmer {
    0% { opacity: 1; }
    50% { opacity: 0.8; }
    100% { opacity: 1; }
}

.pixel-shimmer {
    animation: pixel-shimmer 2s infinite;
}
```

### Chromatic Aberration
```css
.chromatic {
    position: relative;
}

.chromatic::before {
    content: attr(data-text);
    position: absolute;
    top: 0;
    left: 2px;
    color: #ff0000;
    opacity: 0.8;
    pointer-events: none;
}

.chromatic::after {
    content: attr(data-text);
    position: absolute;
    top: 0;
    left: -2px;
    color: #00ffff;
    opacity: 0.8;
    pointer-events: none;
}
```

---

## 🎨 Sprite Templates

### 8×8 Heart Icon
```html
<div class="sprite-8x8 heart-icon">
    <!-- Row 1 -->
    <div class="pixel"></div><div class="pixel active"></div><div class="pixel active"></div><div class="pixel"></div>
    <div class="pixel active"></div><div class="pixel active"></div><div class="pixel"></div><div class="pixel"></div>
    <!-- Row 2 -->
    <div class="pixel active"></div><div class="pixel active"></div><div class="pixel active"></div><div class="pixel active"></div>
    <div class="pixel active"></div><div class="pixel active"></div><div class="pixel active"></div><div class="pixel"></div>
    <!-- Continue pattern... -->
</div>
```

### 16×16 Star Icon
```css
.star-icon {
    width: 16px;
    height: 16px;
    background: url('data:image/svg+xml,<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 16 16"><path d="M8 1l2 6h6l-5 4 2 6-5-4-5 4 2-6-5-4h6z" fill="currentColor"/></svg>');
    image-rendering: pixelated;
}
```

---

## 🎯 Retro UI Patterns

### Menu System
```html
<div class="retro-menu">
    <div class="menu-title">MAIN MENU</div>
    <div class="menu-items">
        <div class="menu-item active">▶ NEW GAME</div>
        <div class="menu-item">  CONTINUE</div>
        <div class="menu-item">  OPTIONS</div>
        <div class="menu-item">  EXIT</div>
    </div>
</div>
```

```css
.retro-menu {
    font-family: var(--font-8bit);
    background: #000040;
    border: 4px solid #ffffff;
    padding: 20px;
    color: #ffffff;
}

.menu-title {
    text-align: center;
    font-size: 16px;
    color: #ffff00;
    margin-bottom: 20px;
    text-shadow: 2px 2px 0px #000000;
}

.menu-item {
    font-size: 12px;
    padding: 4px 0;
    cursor: pointer;
}

.menu-item.active {
    color: #ffff00;
    text-shadow: 1px 1px 0px #000000;
}
```

### Status Window
```html
<div class="status-window">
    <div class="status-header">STATUS</div>
    <div class="status-content">
        <div class="stat-line">LVL: 12</div>
        <div class="stat-line">EXP: 1250/2000</div>
        <div class="stat-line">HP:  85/100</div>
        <div class="stat-line">MP:  42/60</div>
    </div>
</div>
```

---

*uDOS v1.0.4.1 Retro Display Template*
*Pixel-perfect rendering with authentic 8-bit gaming aesthetics*
