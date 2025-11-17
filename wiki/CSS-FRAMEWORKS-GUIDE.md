# uDOS CSS Frameworks Integration Guide

**Version:** uDOS v1.3 Stable
**Last Updated:** November 1, 2025

This guide provides complete documentation for integrating and using retro CSS frameworks in uDOS web extensions. Each framework recreates authentic vintage computing aesthetics from the 1980s and 1990s.

---

## Table of Contents

1. [Quick Reference](#quick-reference)
2. [system.css - Mac System 6](#systemcss---mac-system-6)
3. [NES.css - 8-bit Gaming](#nescss---8-bit-gaming)
4. [classic.css - Mac OS 8.1](#classiccss---mac-os-81)
5. [After Dark CSS - Screensavers](#after-dark-css---screensavers)
6. [Implementation Patterns](#implementation-patterns)
7. [Troubleshooting](#troubleshooting)

---

## Quick Reference

### Framework Selection Matrix

| Use Case | Framework | Era | Fonts | Colors |
|----------|-----------|-----|-------|--------|
| Document editors | system.css | 1984-1991 | Chicago, Monaco | Monochrome |
| Terminals/Consoles | NES.css | 1983-1990 | Press Start 2P | 8-bit palette |
| Dashboards | classic.css | 1989-1997 | ChicagoFLF | System 7 |
| Screensavers | After Dark CSS | 1989 | ChicagoFLF | Classic Mac |

### CDN Links

```html
<!-- system.css v0.1.11 (20KB) -->
<link rel="stylesheet" href="https://unpkg.com/@sakun/system.css">

<!-- NES.css latest (282KB) -->
<link rel="stylesheet" href="https://unpkg.com/nes.css@latest/css/nes.min.css">

<!-- classic.css (3.9KB) - Download required -->
<link rel="stylesheet" href="shared/classic.css">

<!-- Press Start 2P font for NES.css -->
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link href="https://fonts.googleapis.com/css2?family=Press+Start+2P&display=swap" rel="stylesheet">
```

---

## system.css - Mac System 6

**Repository:** https://github.com/sakofchit/system.css
**Documentation:** https://sakofchit.github.io/system.css/
**Used in:** Font Editor, Markdown Viewer

### Overview

Recreates Apple's monochrome System 6 interface (1984-1991). The final version of macOS before color was introduced. Pure black and white design with pixel-perfect components.

### Key Components

#### Windows
```html
<div class="window">
  <div class="title-bar">
    <button aria-label="Close"></button>
    <h1 class="title">Document Title</h1>
    <button aria-label="Resize"></button>
  </div>
  <div class="separator"></div>
  <div class="window-pane">
    <!-- Content here -->
  </div>
  <div class="status-bar">
    <p class="status-bar-field">Status message</p>
  </div>
</div>
```

#### Buttons
```html
<button class="btn">Standard Button</button>
<button class="btn" disabled>Disabled</button>
```

#### Forms
```html
<div class="field-row">
  <label for="text-input">Label:</label>
  <input id="text-input" type="text">
</div>

<div class="field-row">
  <input type="checkbox" id="check1">
  <label for="check1">Checkbox</label>
</div>

<div class="field-row">
  <input type="radio" id="radio1" name="group">
  <label for="radio1">Radio</label>
</div>
```

#### Scrollable Areas
```html
<div class="window-pane" style="height: 300px; overflow-y: scroll;">
  <!-- Scrollable content -->
</div>
```

#### Details Bar
```html
<div class="details-bar">
  <span>File: font.json</span>
  <span>Modified: 2025-11-01</span>
</div>
```

### Typography

- **Chicago_12**: Headers, titles, menu items
- **Monaco**: Code blocks, monospace text
- **Geneva_9**: Body text, smaller UI elements

### Best Practices

1. **Keep it monochrome** - No colors beyond black and white
2. **Use semantic HTML** - Buttons are `<button>`, links are `<a>`
3. **Maintain 1px borders** - Authentic System 6 precision
4. **Test scrollbars** - Custom scrollbars only work in Chromium
5. **Embrace constraints** - Limited palette forces clarity

### Example: Complete Window

```html
<!DOCTYPE html>
<html lang="en">
<head>
  <title>Font Editor</title>
  <link rel="stylesheet" href="https://unpkg.com/@sakun/system.css">
  <style>
    body {
      background: #c0c0c0;
      display: flex;
      justify-content: center;
      align-items: center;
      min-height: 100vh;
      margin: 0;
    }
  </style>
</head>
<body>
  <div class="window" style="width: 800px;">
    <div class="title-bar">
      <button aria-label="Close"></button>
      <h1 class="title">Font Editor</h1>
      <button aria-label="Resize"></button>
    </div>
    <div class="separator"></div>
    <div class="details-bar">
      <span>📁 font.json</span>
      <span>⌨️ Shortcuts: S=Save, E=Export, G=Grid</span>
    </div>
    <div class="separator"></div>
    <div class="window-pane">
      <h2>16x16 Bitmap Font Editor</h2>
      <p>Click grid cells to edit glyphs.</p>
      <div class="field-row">
        <button class="btn">Save</button>
        <button class="btn">Export</button>
        <button class="btn">Clear</button>
      </div>
    </div>
  </div>
</body>
</html>
```

---

## NES.css - 8-bit Gaming

**Repository:** https://github.com/nostalgic-css/NES.css
**Documentation:** https://nostalgic-css.github.io/NES.css/
**Used in:** Terminal

### Overview

NES-style CSS framework bringing 8-bit Nintendo aesthetics to web interfaces. Pixel-art components, retro colors, and Press Start 2P font for authentic gaming nostalgia.

### Key Components

#### Containers
```html
<!-- Default container -->
<div class="nes-container">
  <p>Standard container</p>
</div>

<!-- Dark theme -->
<div class="nes-container is-dark">
  <p>Dark container</p>
</div>

<!-- With title -->
<div class="nes-container is-dark with-title">
  <p class="title">Terminal Output</p>
  <p>Content here</p>
</div>

<!-- Rounded corners -->
<div class="nes-container is-rounded">
  <p>Rounded container</p>
</div>
```

#### Buttons
```html
<!-- Primary button -->
<button class="nes-btn is-primary">Execute</button>

<!-- Success button -->
<button class="nes-btn is-success">Clear</button>

<!-- Warning button -->
<button class="nes-btn is-warning">Settings</button>

<!-- Error button -->
<button class="nes-btn is-error">Delete</button>

<!-- Disabled -->
<button class="nes-btn is-disabled">Disabled</button>
```

#### Inputs
```html
<!-- Text input -->
<input type="text" class="nes-input">

<!-- Dark theme input -->
<input type="text" class="nes-input is-dark">

<!-- With label -->
<div class="nes-field">
  <label for="name">Name:</label>
  <input type="text" id="name" class="nes-input">
</div>
```

#### Badges
```html
<span class="nes-badge">
  <span class="is-dark">v1.3</span>
</span>

<span class="nes-badge">
  <span class="is-primary">READY</span>
</span>

<span class="nes-badge">
  <span class="is-success">ONLINE</span>
</span>

<span class="nes-badge">
  <span class="is-warning">0 CMD</span>
</span>

<span class="nes-badge">
  <span class="is-error">ERROR</span>
</span>
```

#### Text & Icons
```html
<!-- Text styles -->
<p class="nes-text is-primary">Primary text</p>
<p class="nes-text is-success">Success text</p>
<p class="nes-text is-warning">Warning text</p>
<p class="nes-text is-error">Error text</p>
<p class="nes-text is-disabled">Disabled text</p>

<!-- Icons (sprites) -->
<i class="nes-icon trophy is-large"></i>
<i class="nes-icon star"></i>
<i class="nes-icon heart"></i>
```

### Typography

NES.css requires **Press Start 2P** font from Google Fonts:

```html
<link href="https://fonts.googleapis.com/css2?family=Press+Start+2P&display=swap" rel="stylesheet">

<style>
  * {
    font-family: 'Press Start 2P', cursive;
  }
</style>
```

### Color Palette

NES.css uses classic 8-bit colors:
- **Primary**: `#209cee` (blue)
- **Success**: `#92cc41` (green)
- **Warning**: `#f7d51d` (yellow)
- **Error**: `#e76e55` (red)
- **Dark**: `#212529` (near-black)

### Best Practices

1. **Use semantic classes** - `.is-primary`, `.is-success`, etc.
2. **Embrace pixelation** - Don't fight the 8-bit aesthetic
3. **Limit text length** - Press Start 2P is wide and bold
4. **Test scaling** - Font can be hard to read at small sizes
5. **Consider dark mode** - `.is-dark` works well for terminals

### Example: Terminal Interface

```html
<!DOCTYPE html>
<html lang="en">
<head>
  <title>uDOS Terminal</title>
  <link rel="stylesheet" href="https://unpkg.com/nes.css@latest/css/nes.min.css">
  <link href="https://fonts.googleapis.com/css2?family=Press+Start+2P&display=swap" rel="stylesheet">
  <style>
    * {
      font-family: 'Press Start 2P', cursive;
    }
    body {
      background: #212529;
      padding: 20px;
    }
    .terminal-container {
      max-width: 900px;
      margin: 0 auto;
    }
    .terminal-header {
      display: flex;
      gap: 10px;
      margin-bottom: 15px;
      flex-wrap: wrap;
    }
    #output-container {
      min-height: 400px;
      max-height: 500px;
      overflow-y: auto;
      margin-bottom: 15px;
      font-size: 10px;
    }
    .nes-input {
      width: 100%;
      margin-bottom: 15px;
    }
    .toolbar {
      display: flex;
      gap: 10px;
      flex-wrap: wrap;
    }
  </style>
</head>
<body>
  <div class="terminal-container">
    <!-- Header with badges -->
    <div class="terminal-header">
      <span class="nes-badge"><span class="is-success">v1.3</span></span>
      <span class="nes-badge"><span class="is-primary">READY</span></span>
      <span class="nes-badge"><span class="is-warning">0 CMD</span></span>
    </div>

    <!-- Output area -->
    <div id="output-container" class="nes-container is-dark with-title">
      <p class="title">Terminal Output</p>
      <div id="output">
        <pre>
████████████████████████████████████████
  uDOS v1.3 Terminal - Press START
████████████████████████████████████████

▶ Ready for commands...
        </pre>
      </div>
    </div>

    <!-- Input area -->
    <input type="text" id="input" class="nes-input is-dark" placeholder="Enter command...">

    <!-- Toolbar -->
    <div class="toolbar">
      <button class="nes-btn is-primary">Help</button>
      <button class="nes-btn is-success">Clear</button>
      <button class="nes-btn is-warning">Dashboard</button>
      <button class="nes-btn">Settings</button>
    </div>
  </div>
</body>
</html>
```

---

## classic.css - Mac OS 8.1

**Repository:** https://github.com/npjg/classic.css
**Used in:** Dashboard (planned)

### Overview

Authentic Mac OS 8.1 interface components with System 7.1.1 styling. Focuses on window chrome, button bevels, and classic scrollbars. Requires ChicagoFLF font.

### Key Components

#### Windows
```html
<div class="content">
  <div class="title">Dashboard</div>
  <div class="window-content">
    <!-- Content here -->
  </div>
  <div class="footer">
    Status: Online
  </div>
</div>
```

#### Buttons
```html
<button class="classic-btn">Standard</button>
<button class="classic-btn default">Default</button>
```

### CSS Variables

classic.css uses CSS variables for button shadows:

```css
:root {
  --button-box-shadow:
    inset -1px -1px 0px #000,
    inset 1px 1px 0px #fff,
    inset -2px -2px 0px #808080,
    inset 2px 2px 0px #ddd;
}
```

### Font Requirements

Requires ChicagoFLF font (included in classic.css):

```css
@font-face {
  font-family: 'ChicagoFLF';
  src: url('ChicagoFLF.ttf') format('truetype');
}
```

### Best Practices

1. **Use with After Dark CSS** - Designed to work together
2. **Test button states** - Hover/active have specific bevels
3. **Background patterns** - Classic Mac striped backgrounds
4. **Window chrome** - Double borders for authenticity

---

## After Dark CSS - Screensavers

**Repository:** https://github.com/bryanbraun/after-dark-css
**Demo:** http://bryanbraun.github.io/after-dark-css/
**Used in:** Dashboard (screensaver mode - planned)

### Overview

Pure CSS recreations of After Dark™ screensavers from 1989. Flying Toasters, Starfield, and more. No JavaScript required.

### Available Screensavers

1. **Flying Toasters** - Iconic flying toasters and toast
2. **Starfield** - Moving star animation
3. **Confetti Factory** - Falling confetti
4. **Daredevil Dan** - Stick figure walking
5. **Messages** - Scrolling text messages

### Implementation

```html
<link rel="stylesheet" href="after-dark.css">

<div id="flying-toasters">
  <div class="toaster"></div>
  <div class="toast"></div>
  <!-- More elements -->
</div>
```

### Best Practices

1. **Use as overlay** - Activate on idle/settings
2. **Preserve functionality** - Screensaver shouldn't block UI
3. **Test performance** - CSS animations can be CPU-intensive
4. **Provide exit** - Click/keypress to dismiss

---

## Implementation Patterns

### Pattern 1: Single Framework

Use one framework for entire extension:

```html
<!DOCTYPE html>
<html lang="en">
<head>
  <link rel="stylesheet" href="https://unpkg.com/@sakun/system.css">
</head>
<body>
  <div class="window">
    <!-- All system.css components -->
  </div>
</body>
</html>
```

### Pattern 2: Hybrid Approach

Combine frameworks with custom overrides:

```html
<!DOCTYPE html>
<html lang="en">
<head>
  <link rel="stylesheet" href="shared/classic.css">
  <link rel="stylesheet" href="shared/after-dark.css">
  <style>
    /* Custom overrides */
    .content {
      background: #fff;
    }
  </style>
</head>
<body>
  <div class="content">
    <!-- classic.css window -->
    <div id="screensaver" style="display: none;">
      <!-- After Dark overlay -->
    </div>
  </div>
</body>
</html>
```

### Pattern 3: Custom Styles

Add framework, override specific components:

```html
<head>
  <link rel="stylesheet" href="https://unpkg.com/nes.css@latest/css/nes.min.css">
  <style>
    /* Custom terminal styles */
    #output-container {
      min-height: 400px;
      max-height: 500px;
      overflow-y: auto;
      font-size: 10px;
    }

    /* Custom scrollbar */
    #output-container::-webkit-scrollbar {
      width: 12px;
    }

    #output-container::-webkit-scrollbar-thumb {
      background: #92cc41;
      border: 2px solid #212529;
    }
  </style>
</head>
```

---

## Troubleshooting

### Fonts Not Loading

**Problem:** Custom fonts not appearing
**Solution:**
1. Check CDN links in `<head>`
2. Verify `font-display: swap` for fallbacks
3. Test with Chrome DevTools Network tab
4. Use local font files as backup

### Scrollbars Not Styled

**Problem:** system.css scrollbars look default
**Solution:**
- Custom scrollbars only work in Chromium browsers
- Firefox/Safari use default scrollbars
- Consider this acceptable degradation

### Layout Breaking

**Problem:** Components don't align
**Solution:**
1. Use framework HTML structure exactly
2. Don't mix `.window` and `.nes-container`
3. Check for CSS specificity conflicts
4. Validate HTML structure

### Performance Issues

**Problem:** Slow rendering with After Dark CSS
**Solution:**
1. Limit animated elements
2. Use `will-change: transform` for animations
3. Test on lower-end devices
4. Provide option to disable animations

### Color Conflicts

**Problem:** Wrong colors with NES.css
**Solution:**
- Don't override `.is-primary`, `.is-success` colors
- Use semantic classes instead of custom colors
- Embrace the 8-bit palette

---

## Resources

### Documentation
- **system.css:** https://sakofchit.github.io/system.css/
- **NES.css:** https://nostalgic-css.github.io/NES.css/
- **classic.css:** https://github.com/npjg/classic.css
- **After Dark CSS:** http://bryanbraun.github.io/after-dark-css/

### uDOS Guides
- `/docs/CSS-FRAMEWORK-ATTRIBUTION.md` - Complete attribution
- `/docs/SYSTEM-CSS-INTEGRATION.md` - Font Editor/Markdown Viewer integration
- `/extensions/web/shared/SYSTEM-CSS-REFERENCE.md` - system.css quick reference
- `/wiki/Style-Guide.md` - uDOS styling conventions

### Support
- **GitHub Issues:** Report bugs for each framework
- **uDOS GitHub:** https://github.com/fredporter/uDOS

---

**Happy retro styling!** 🎮🖥️✨
