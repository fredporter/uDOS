# 🎨 CSS Framework Showcase

Classic retro styling frameworks integrated into uDOS for authentic vintage computing experiences.

## 🌈 Available Frameworks

### 1. 🖥️ classic.css - Mac OS 8.1
**Port: 8885** | [Demo](http://localhost:8885)
- Authentic Mac OS 8.1 interface components
- Window frames, menus, buttons, and dialog boxes
- Classic teal desktop background with patterns
- ChicagoFLF font integration

### 2. 🎮 NES.css - 8-bit Nintendo
**Port: 8884** | [Demo](http://localhost:8884)
- NES-style 8-bit interface elements
- Pixelated borders and retro gaming aesthetics
- Press Start 2P font recommended
- Pure CSS, no JavaScript required

### 3. 💾 system.css - Classic Mac System 6
**Port: 8883** | [Demo](http://localhost:8883)
- Apple System OS (1984-1991) monochrome interface
- Chicago 12pt and Geneva 9pt font recreations
- Perfect for file manager interfaces
- Minimal and clean black & white design

### 4. ✨ after-dark-css - Screensaver Magic
**Port: 8882** | [Demo](http://localhost:8882)
- After Dark™ screensaver animations in pure CSS
- Flying toasters, confetti factory, and more
- Nostalgic screensaver experiences
- ChicagoFLF font with authentic animations

## 🚀 Quick Start

```bash
# Start all CSS framework demos
cd /Users/fredbook/Code/uDOS/extensions/web/css-frameworks
python3 launch_all.py

# Or start individual frameworks
python3 -m http.server 8885 --directory classic-demo     # Mac OS 8.1
python3 -m http.server 8884 --directory nes-demo         # NES Style
python3 -m http.server 8883 --directory system-demo      # System 6
python3 -m http.server 8882 --directory afterdark-demo   # Screensavers
```

## 📖 Integration Guide

### Using in Your Projects

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

### Font Recommendations

```css
/* Mac OS 8.1 & After Dark */
@import url('https://fonts.googleapis.com/css2?family=Chicago');
font-family: 'ChicagoFLF', 'Chicago', 'Geneva', sans-serif;

/* NES Style */
@import url('https://fonts.googleapis.com/css2?family=Press+Start+2P');
font-family: 'Press Start 2P', monospace;

/* Classic Mac System */
font-family: 'Chicago', 'Geneva', monospace;
```

## 🎭 Style Demos

Each framework includes:
- **Component Gallery** - All available UI elements
- **Interactive Examples** - Working forms and dialogs
- **Color Palettes** - Available colors and themes
- **Layout Templates** - Common interface patterns
- **Integration Examples** - How to use with modern frameworks

## 📜 License Information

All frameworks are open source with permissive licenses:
- **classic.css**: MIT License
- **NES.css**: MIT License
- **system.css**: MIT License
- **after-dark-css**: MIT License (code), SIL OFL (fonts)

See `CREDITS.md` for complete attribution details.

## 🔗 External Resources

- [classic.css Documentation](https://github.com/npjg/classic.css)
- [NES.css Documentation](https://nostalgic-css.github.io/NES.css/)
- [system.css Documentation](https://sakofchit.github.io/system.css/)
- [after-dark-css Gallery](https://bryanbraun.github.io/after-dark-css/)

---

**Note**: These are showcase implementations. For production use, install frameworks directly via npm or CDN.
