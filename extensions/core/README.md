# uDOS Core Extensions v1.0.24

Core extensions and shared components for the uDOS system.

## 📁 Directory Structure

```
extensions/core/
├── c64-terminal/         # Commodore 64 Terminal (PetMe font, Synthwave DOS palette)
├── character-editor/     # Multi-resolution character/font editor (8×8 to 128×128)
├── dashboard/            # NES Framework system dashboard
├── desktop/              # System 7 desktop environment
├── markdown/             # GitHub-flavored markdown viewer (uCODE + PANEL)
├── teletext/             # BBC Teletext interface (Mallard fonts)
├── css/                  # Shared CSS components
│   ├── typography-system.css
│   ├── udos-filepicker.css
│   ├── udos-grid.css
│   └── udos-syntax.css
├── js/                   # Shared JavaScript utilities
│   ├── typography-manager.js
│   ├── udos-controls.js
│   ├── udos-filepicker.js
│   ├── udos-option-selector.js
│   └── udos-panels.js
├── themes/               # Retro theme collection
│   ├── classic.css            # DOS
│   ├── classic-mac-patterns.css
│   ├── system.css             # Windows 3.x
│   ├── system-mac.css         # System 7
│   ├── nes.css                # 8-bit Nintendo
│   └── udos-v13-theme.css
├── docs/                 # Documentation
├── assets/               # Static assets (icons, images)
└── README.md             # This file
```

## 🎨 Core Extensions

### **C64 Terminal** (`c64-terminal/`)
Authentic Commodore 64 terminal interface with PetMe font and Synthwave DOS palette.
- **Phase 2** complete - Enhanced rendering

### **Character Editor** (`character-editor/`)
Multi-resolution pixel art tool for creating characters and fonts (8×8 to 128×128).
- **Phase 4** complete - Full rebuild with emoji designer

### **Dashboard** (`dashboard/`)
NES.css framework system dashboard with 6 widgets and retro gaming aesthetic.
- **Phase 6** complete - NES framework integration

### **Desktop** (`desktop/`)
System 7 desktop environment with Command Palette (Cmd/Ctrl+K) and window management.
- **Phase 7** complete - uDOS integration

### **Markdown Viewer** (`markdown/`)
GitHub-flavored markdown renderer with uCODE commands and PANEL callouts.
- **Phase 5** complete - GitHub CSS, Adobe Source fonts, typography stack

### **Teletext** (`teletext/`)
BBC Teletext broadcast interface with Mallard fonts and Mode 7 graphics.
- **Phase 3** complete - Synthwave DOS enhancement

## 🧩 Shared Components

### **CSS Framework** (`css/`)
- **typography-system.css** - Advanced typography with monospace optimization
- **udos-grid.css** - 16×16 pixel cell-based grid system
- **udos-syntax.css** - Syntax highlighting for code blocks
- **udos-filepicker.css** - File picker UI component styles

### **JavaScript Utilities** (`js/`)
- **typography-manager.js** - Dynamic font loading and management
- **udos-controls.js** - UI control elements
- **udos-filepicker.js** - File picker functionality
- **udos-option-selector.js** - Option selection widgets
- **udos-panels.js** - Panel management system

### **Themes** (`themes/`)
Retro computing theme collection:
- **classic.css** - DOS aesthetic
- **system.css** - Windows 3.x look
- **system-mac.css** - System 7 styling
- **nes.css** - 8-bit Nintendo theme
- **classic-mac-patterns.css** - Mac UI patterns
- **udos-v13-theme.css** - uDOS v1.3 theme

## 🚀 Usage

### Include Shared CSS
```html
<link rel="stylesheet" href="/extensions/core/css/udos-grid.css">
<link rel="stylesheet" href="/extensions/core/themes/system-mac.css">
<link rel="stylesheet" href="/extensions/core/css/typography-system.css">
```

### Include Shared JavaScript
```html
<script src="/extensions/core/js/typography-manager.js"></script>
<script src="/extensions/core/js/udos-controls.js"></script>
<script src="/extensions/core/js/udos-filepicker.js"></script>
```

### Initialize Components
```javascript
// Initialize typography system
TypographyManager.init();

// Initialize UI controls
UDOSControls.init();
```

## 📚 Documentation

See `docs/` directory for detailed guides:
- **CSS-FRAMEWORKS-GUIDE.md** - Framework integration
- **GRID-SYSTEM.md** - Grid system specification
- **README-Typography.md** - Typography system guide
- **SYSTEM-CSS-REFERENCE.md** - System theme reference
- **shared-components.md** - Component documentation

## 🎯 v1.0.24 Reorganization

All core extensions have been rebuilt and unified:
- ✅ Phase 1: Consolidation
- ✅ Phase 2: C64 Terminal Enhancement
- ✅ Phase 3: Teletext Synthwave DOS Enhancement
- ✅ Phase 4-4.7: Character Editor (Font Tools rebuild)
- ✅ Phase 5-5.1: Markdown Viewer + Typography
- ✅ Phase 6: Dashboard NES Framework
- ✅ Phase 7: System Desktop Integration
- ✅ Cleanup: Removed `/shared/` duplication, organized structure

## 🔧 Development

When adding new core components:
1. Place files in appropriate directories (`css/`, `js/`, `themes/`)
2. Update extension-specific README files
3. Add documentation to `docs/`
4. Follow Synthwave DOS color standards
5. Update this README with new component information
