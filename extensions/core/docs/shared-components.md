# uDOS Web Extensions - Shared Assets

This directory contains unified design assets shared across all uDOS web extensions.

## 📁 Directory Contents

```
shared/
├── udos-theme.css     # Unified stylesheet (800+ lines)
├── udos-syntax.css    # uCODE syntax highlighting
├── udos-panels.js     # Panel rendering system
└── README.md          # This file
```

## 🎨 Visual Identity System

### Monaspace Font Family

Five typeface variants with texture healing and ligatures:

- **Monaspace Neon**: Grotesque sans, geometric precision
- **Monaspace Argon**: Humanist sans, warm and friendly
- **Monaspace Xenon**: Slab serif, authoritative
- **Monaspace Radon**: Neo-grotesque, balanced
- **Monaspace Krypton**: Mechanical sans, technical

### Polaroid Color Palette

| Color  | Hex Code | Usage                          |
|--------|----------|--------------------------------|
| Red    | #FF1744  | Errors, critical alerts        |
| Green  | #00E676  | Success, confirmations         |
| Yellow | #FFEB3B  | Warnings, attention            |
| Blue   | #2196F3  | Information, links             |
| Purple | #E91E63  | Highlights, special features   |
| Cyan   | #00E5FF  | Active states, emphasis        |

**Grayscale Spectrum**: 6 levels from `#000000` (black) to `#FFFFFF` (white)

### Theme Variants

| Theme          | Icon | Primary Color | Use Case                    |
|----------------|------|---------------|-----------------------------|
| DUNGEON        | ⚔️   | Gold          | Text adventures, RPGs       |
| GALAXY         | 🚀   | Cyan          | Sci-fi, space exploration   |
| FOUNDATION     | 📊   | White         | Professional, productivity  |
| SCIENCE        | 🔬   | Pale Green    | Technical, scientific       |
| PROJECT        | 📋   | Dark Gray     | Minimal, focused work       |

## 🧩 Integration Guide

### 1. Link Stylesheet

Add to your HTML `<head>`:

```html
<!-- uDOS Unified Stylesheet -->
<link rel="stylesheet" href="../shared/udos-theme.css">
<link rel="stylesheet" href="../shared/udos-syntax.css">

<!-- uDOS Panel System -->
<script src="../shared/udos-panels.js"></script>
```

### 2. Set Default Theme

Add `data-theme` attribute to `<body>`:

```html
<body data-theme="GALAXY">
  <!-- Your content -->
</body>
```

### 3. Create Theme Switcher

```html
<select id="theme-select" onchange="changeTheme(this.value)">
  <option value="DUNGEON">⚔️ DUNGEON</option>
  <option value="GALAXY" selected>🚀 GALAXY</option>
  <option value="FOUNDATION">📊 FOUNDATION</option>
  <option value="SCIENCE">🔬 SCIENCE</option>
  <option value="PROJECT">📋 PROJECT</option>
</select>

<script>
function changeTheme(theme) {
  document.body.setAttribute('data-theme', theme);
  if (window.UDOSPanels) {
    window.UDOSPanels.setTheme(theme);
  }
  localStorage.setItem('udos-theme', theme);
}
</script>
```

### 4. Use Component Classes

```html
<!-- Panel -->
<div class="udos-panel">
  <div class="panel-header">Panel Title</div>
  <div class="panel-content">Panel body...</div>
</div>

<!-- Code Block -->
<pre><code class="language-ucode">
[MAP|EXPLORE*north]
</code></pre>

<!-- Table -->
<table class="udos-table">
  <thead>
    <tr><th>Column 1</th><th>Column 2</th></tr>
  </thead>
  <tbody>
    <tr><td>Data 1</td><td>Data 2</td></tr>
  </tbody>
</table>

<!-- Progress Bar -->
<div class="progress-bar">
  <div class="progress-fill" style="--progress: 75;"></div>
</div>
```

### 5. Use Utility Classes

```html
<!-- Colors -->
<span class="color-red">Error message</span>
<div class="bg-cyan">Highlighted section</div>

<!-- Typography -->
<p class="font-neon">Monaspace Neon text</p>
<h2 class="text-xl">Large heading</h2>

<!-- Spacing -->
<div class="p-4">Padded container</div>
<section class="mb-6">Section with margin</section>
```

## 🎭 uCODE Panel Embeds

### Basic Syntax

In markdown files:

````markdown
```ucode panel:name width:80 height:24
╔════════════════════════════════════════════════════════════════════════════╗
║  Panel content with [MODULE|COMMAND*PARAM] syntax highlighting            ║
╚════════════════════════════════════════════════════════════════════════════╝
```
````

### Panel Parameters

| Parameter | Type   | Default | Description                       |
|-----------|--------|---------|-----------------------------------|
| `panel`   | string | -       | Panel name/identifier (required)  |
| `width`   | int    | 80      | Character width                   |
| `height`  | int    | 24      | Line height                       |
| `bg`      | color  | auto    | Background color (theme-aware)    |
| `fg`      | color  | auto    | Foreground color (theme-aware)    |

### Panel Rendering

The `UDOSPanelSystem` automatically:

1. **Finds** all ` ```ucode` code blocks
2. **Parses** metadata from first line (`panel:name width:N height:N`)
3. **Creates** styled `.ucode-panel` containers
4. **Highlights** `[MODULE|COMMAND*PARAM]` syntax
5. **Applies** current theme colors
6. **Updates** dynamically when theme changes

### JavaScript API

```javascript
// Global panel system instance
window.UDOSPanels

// Methods
UDOSPanels.processCodeBlocks()           // Convert all ucode blocks
UDOSPanels.setTheme('GALAXY')            // Change active theme
UDOSPanels.createPanel(params, content)  // Manually create panel
```

## 📱 Responsive Design

### Breakpoints

```css
/* Mobile: < 640px */
@media (max-width: 640px) {
  .ucode-panel { max-width: 100%; overflow-x: auto; }
}

/* Tablet: 640px - 1024px */
@media (min-width: 640px) and (max-width: 1024px) {
  .container { max-width: 768px; }
}

/* Desktop: 1024px - 1920px */
@media (min-width: 1024px) {
  .container { max-width: 1280px; }
}

/* Ultra-wide: > 1920px */
@media (min-width: 1920px) {
  .container { max-width: 1600px; }
}
```

### Grid System

```html
<!-- 2-column grid -->
<div class="viewport-grid grid-2">
  <div class="grid-item">Column 1</div>
  <div class="grid-item">Column 2</div>
</div>

<!-- 3-column grid -->
<div class="viewport-grid grid-3">
  <div class="grid-item">Col 1</div>
  <div class="grid-item">Col 2</div>
  <div class="grid-item">Col 3</div>
</div>

<!-- 4-column grid -->
<div class="viewport-grid grid-4">
  <!-- Responsive: 4 cols → 2 cols → 1 col -->
</div>
```

## ♿ Accessibility Features

### Focus Indicators

All interactive elements have visible focus states:

```css
button:focus-visible,
a:focus-visible {
  outline: 2px solid var(--theme-accent);
  outline-offset: 2px;
}
```

### Reduced Motion

Respects `prefers-reduced-motion`:

```css
@media (prefers-reduced-motion: reduce) {
  * {
    animation-duration: 0.01ms !important;
    transition-duration: 0.01ms !important;
  }
}
```

### High Contrast

Supports `prefers-contrast: high`:

```css
@media (prefers-contrast: high) {
  .ucode-panel {
    border-width: 3px;
    border-color: var(--udos-white);
  }
}
```

### Screen Reader Support

- Semantic HTML5 elements
- ARIA labels where needed
- Skip-to-content links
- Meaningful alt text

## 🔧 Customization

### CSS Custom Properties

Override theme colors:

```css
:root {
  --udos-red: #YOUR_COLOR;
  --theme-primary: #YOUR_COLOR;
  --char-width: 9px;  /* Adjust character width */
}
```

### Extending Components

Add custom panel styles:

```css
.ucode-panel.my-custom-panel {
  border-color: #FF00FF;
  background: linear-gradient(45deg, #000, #111);
}
```

### Font Customization

Use different Monaspace variant:

```css
.markdown-body code {
  font-family: var(--font-argon); /* Instead of Neon */
}
```

## 📊 Component Library

### Available Components

1. **Panels** (`.udos-panel`)
   - Standard, dashboard, status, error, warning, success, info

2. **Code Blocks** (`.ucode-panel`)
   - Syntax-highlighted uCODE embeds

3. **Tables** (`.udos-table`)
   - Striped rows, hover effects, responsive

4. **Progress Bars** (`.progress-bar`)
   - CSS-animated, theme-aware

5. **Grids** (`.viewport-grid`)
   - 1-4 column layouts, responsive

6. **Status Icons** (`.status-icon`)
   - Success (✓), error (✗), warning (⚠), info (ℹ)

## 🧪 Testing Checklist

Before deploying:

- [ ] All themes render correctly
- [ ] Panel embeds process successfully
- [ ] Syntax highlighting works
- [ ] Theme switcher updates all elements
- [ ] Responsive layouts adapt properly
- [ ] Accessibility features functional
- [ ] No console errors
- [ ] Font loading successful

## 📚 Examples

See `extensions/web/markdown-viewer/examples/ucode-panels.md` for comprehensive examples of:

- Basic panel syntax
- uCODE command highlighting
- Dashboard layouts
- Map rendering
- Status panels (success/error/warning/info)
- Command reference tables
- Progress bars
- All theme variants

## 🤝 Integration Status

| Extension       | Status | Notes                          |
|-----------------|--------|--------------------------------|
| markdown-viewer | ✅     | Complete with theme switcher   |
| typo            | 🔄     | Pending stylesheet integration |
| font-editor     | 🔄     | Pending stylesheet integration |
| cmd             | 🔄     | Pending stylesheet integration |
| dashboard       | 📋     | Planned for v1.3              |

## 🐛 Troubleshooting

### Panels Not Rendering

1. Check JavaScript console for errors
2. Verify `udos-panels.js` is loaded
3. Ensure code blocks use ` ```ucode` language
4. Confirm metadata format: `panel:name width:N height:N`

### Theme Not Applying

1. Check `data-theme` attribute on `<body>`
2. Verify `udos-theme.css` is loaded
3. Ensure CSS custom properties are defined
4. Check browser DevTools for CSS conflicts

### Fonts Not Loading

1. Verify font files exist in `extensions/web/fonts/monaspace/`
2. Check CORS headers if loading from different origin
3. Use browser DevTools Network tab to debug
4. Fallback: System monospace fonts still work

## 📖 Further Reading

- `/docs/CUSTOMIZATION-GUIDE.md` - User customization framework
- `/docs/V1.2-RELEASE.md` - Release notes and features
- `/wiki/Style-Guide.md` - Complete uDOS style guide
- `/extensions/web/markdown-viewer/examples/` - Live examples

---

**Version**: 1.2.0
**Last Updated**: 2024
**License**: See LICENSE.txt in repository root
