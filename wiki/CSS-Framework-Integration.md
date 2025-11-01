# 🎨 CSS Framework Integration

uDOS includes comprehensive integration with classic retro CSS frameworks, bringing authentic vintage computing experiences to modern web development.

## 🌈 Available Frameworks

### 🖥️ classic.css - Mac OS 8.1
- **Author**: npjg
- **License**: MIT
- **Purpose**: Authentic Mac OS 8.1 interface components
- **Features**: Window frames, menus, teal desktop patterns, ChicagoFLF font
- **Demo Port**: 8885

### 🎮 NES.css - 8-bit Nintendo
- **Author**: B.C.Rikko
- **License**: MIT
- **Purpose**: NES-style (8bit-like) CSS Framework
- **Features**: Pixelated borders, retro gaming aesthetics, Press Start 2P font
- **Demo Port**: 8884

### 💾 system.css - Classic Mac System 6
- **Author**: Sakun Srivatsa (@sakofchit)
- **License**: MIT
- **Purpose**: Apple System OS (1984-1991) monochrome interface
- **Features**: Black & white design, Chicago/Geneva fonts, classic Mac elements
- **Demo Port**: 8883

### ✨ after-dark-css - Screensaver Magic
- **Author**: Bryan Braun
- **License**: MIT (code), SIL OFL (fonts), Berkeley Systems (images)
- **Purpose**: After Dark™ screensaver recreations in pure CSS
- **Features**: Flying toasters, matrix rain, geometric patterns, pure CSS animations
- **Demo Port**: 8882

## 🚀 Quick Start

### Launch All Framework Demos

```bash
# Navigate to CSS frameworks directory
cd extensions/web/css-frameworks

# Start all demo servers
python3 launch_all.py
```

### Individual Framework Usage

```html
<!-- Mac OS 8.1 Style -->
<link rel="stylesheet" href="https://unpkg.com/classic.css">

<!-- NES 8-bit Style -->
<link rel="stylesheet" href="https://unpkg.com/nes.css/css/nes.min.css">

<!-- Classic Mac System 6 -->
<link rel="stylesheet" href="https://unpkg.com/@sakun/system.css">

<!-- After Dark CSS (download required) -->
<link rel="stylesheet" href="path/to/after-dark.css">
```

## 🎭 Demo Features

### Classic.css Demo (Port 8885)
- **Mac OS 8.1 Interface**: Authentic window frames and title bars
- **Component Gallery**: Buttons, dialogs, menus, desktop icons
- **Color Palette**: Classic teal and grayscale colors
- **Interactive Examples**: Clickable icons and menu interactions
- **Usage Guide**: CDN installation and basic window structure

### NES.css Demo (Port 8884)
- **8-bit Gaming Interface**: Nintendo-style components
- **Game Elements**: Health bars, leaderboards, achievement system
- **Sound Effects**: 8-bit beeps and game sounds (Web Audio API)
- **Controller Layout**: Classic NES controller visualization
- **Comprehensive Components**: Buttons, dialogs, forms, progress bars

### System.css Demo (Port 8883)
- **File Manager Interface**: Left sidebar with file list, right content area
- **Markdown Viewer**: Live documentation rendering
- **Classic Mac Elements**: Monochrome design, authentic scrollbars
- **Window Management**: Multiple dialog examples
- **Documentation Integration**: Browse uDOS wiki content

### After Dark CSS Demo (Port 8882)
- **Multiple Screensavers**: Flying toasters, matrix rain, starfield
- **Pure CSS Animations**: No JavaScript dependencies for animations
- **Interactive Controls**: Switch between different screensaver modes
- **Auto-Cycling**: Automatic rotation every 30 seconds
- **Keyboard Controls**: Space bar to manually cycle through

## 🔧 Integration Examples

### Dashboard Enhancement

The uDOS dashboard already uses classic.css for its Mac OS 8.1 styling:

```html
<!-- Current dashboard implementation -->
<link rel="stylesheet" href="../shared/classic.css">
```

### Markdown Viewer Enhancement

The system.css integration provides a perfect markdown file manager:

```html
<!-- File manager with markdown rendering -->
<div class="file-manager">
    <div class="sidebar">
        <!-- File list -->
    </div>
    <div class="content-area">
        <!-- Rendered markdown -->
    </div>
</div>
```

### Terminal Styling

NES.css provides excellent retro terminal styling:

```html
<!-- Retro terminal interface -->
<div class="nes-container is-dark">
    <pre class="nes-textarea">[user@udos]$ help</pre>
</div>
```

## 📖 Font Recommendations

### Mac OS Styles (classic.css, system.css, after-dark-css)
```css
@import url('https://fonts.googleapis.com/css2?family=Chicago');
font-family: 'ChicagoFLF', 'Chicago', 'Geneva', sans-serif;
```

### Gaming Style (NES.css)
```css
@import url('https://fonts.googleapis.com/css2?family=Press+Start+2P');
font-family: 'Press Start 2P', monospace;
```

### Terminal Style
```css
font-family: 'Monaco', 'Menlo', 'Courier New', monospace;
```

## 🎨 Style Customization

### Creating Custom Themes

Each framework supports customization:

```css
/* Classic.css customization */
.window {
    background: #f0f0f0; /* Custom window background */
}

/* NES.css customization */
.nes-btn.is-custom {
    background: #ff6b6b;
    border-color: #ff5252;
}

/* System.css customization */
.title-bar {
    background: #333; /* Dark title bar */
}
```

### Mixing Frameworks

While not recommended for production, you can combine elements:

```html
<!-- Hybrid approach for demos -->
<div class="window"> <!-- system.css window -->
    <div class="nes-container"> <!-- NES.css container -->
        <button class="classic-btn">Mixed Style</button>
    </div>
</div>
```

## 🔗 Framework Resources

### Official Documentation
- [classic.css GitHub](https://github.com/npjg/classic.css)
- [NES.css Documentation](https://nostalgic-css.github.io/NES.css/)
- [system.css Documentation](https://sakofchit.github.io/system.css/)
- [after-dark-css Gallery](https://bryanbraun.github.io/after-dark-css/)

### Installation Methods

#### npm/yarn
```bash
npm install nes.css
npm install @sakun/system.css
```

#### CDN Links
```html
<!-- NES.css -->
<link href="https://unpkg.com/nes.css/css/nes.min.css" rel="stylesheet">

<!-- System.css -->
<link href="https://unpkg.com/@sakun/system.css" rel="stylesheet">
```

#### Local Installation
```bash
# Clone and customize
git clone https://github.com/npjg/classic.css.git
git clone https://github.com/bryanbraun/after-dark-css.git
```

## 📜 License Compliance

All frameworks use permissive licenses:

- **classic.css**: MIT License
- **NES.css**: MIT License (code), Creative Commons (docs)
- **system.css**: MIT License
- **after-dark-css**: MIT License (code), SIL OFL (fonts)

Full attribution details are maintained in `CREDITS.md`.

## 🚀 Future Integration

### Planned Enhancements
- **Theme Switcher**: Dynamic framework switching in dashboard
- **Component Library**: Reusable components from all frameworks
- **Hybrid Layouts**: Best-of-all-worlds interface combinations
- **Extension Templates**: Framework-specific extension templates

### Contributing

To add new CSS framework integrations:

1. Create demo directory in `extensions/web/css-frameworks/`
2. Build comprehensive component showcase
3. Update `launch_all.py` with new server configuration
4. Add framework attribution to `CREDITS.md`
5. Update this documentation

---

*Experience the nostalgia of classic computing interfaces with modern web technologies!*
