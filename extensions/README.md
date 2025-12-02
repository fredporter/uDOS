# uDOS Extensions System v1.1.15

**Web GUI, Diagram Generation, AI Assistant, and Extension Framework**

## Overview

The uDOS extensions system provides dual-interface capabilities (Terminal + Web) with production-ready web infrastructure, comprehensive diagram generation, and AI-powered assistance.

**v1.1.15 Features** (Graphics Infrastructure Complete):
- **Mermaid Diagrams**: 12 diagram types with server-side rendering
- **GitHub Diagrams**: Native GeoJSON maps + ASCII STL 3D models
- **ASCII Graphics**: Unicode box-drawing + 2 house styles (51 diagrams)
- **Typora Support**: 13 diagram types with offline WYSIWYG editing
- **Nano Banana**: PNG→SVG vectorization with Gemini 2.5 Flash (Task 5)
- **Style Guides**: Technical-kinetic, hand-illustrative, hybrid templates
- **Vectorization**: potrace + vtracer integration
- Complete testing framework (327 tests)

**v1.1.1 Features** (327 tests):
- Production web server with health monitoring
- Teletext display with WebSocket streaming
- CLI→Web delegation API
- State synchronization engine
- Reusable web component library
- Browser extension (Chrome/Firefox/Edge)
- Mobile PWA with offline support

**v1.1.0 Features** (1,810 tests):
- RBAC integration for web access
- Encrypted memory tier access via web
- Knowledge library web interface
- AI prompt testing interface

## 📁 **Directory Structure**

```
extensions/
├── core/                       # ✅ CORE EXTENSIONS (v1.1.15)
│   ├── terminal/              # Retro terminal (PetMe font, Synthwave DOS)
│   ├── dashboard/             # System dashboard (NES.css, port 8888)
│   ├── mission-control/       # Mission tracker dashboard (port 5000)
│   ├── desktop/               # System 7 desktop environment
│   ├── teletext/              # BBC Teletext with WebSocket streaming
│   ├── ok_assistant/          # Gemini AI assistant integration
│   ├── svg_generator/         # Nano Banana PNG→SVG vectorization
│   ├── typora-diagrams/       # Typora diagram templates (13 types)
│   ├── shared/                # Base server, port manager, common utilities
│   └── extension_dev_tools.py # Development utilities
│
├── play/                       # ✅ PLAY EXTENSION
│   ├── commands/              # Game commands (MAP, TILE, SCENARIO)
│   ├── services/              # Game services (planet, XP, scenarios)
│   └── data/                  # Game data (GeoJSON maps, STL models)
│       ├── examples/          # survival_area_map.geojson
│       └── models/            # shelter/, tools/ STL files
│
├── api/                        # ✅ API SERVER (port 5001)
│   └── server.py              # REST API for all uDOS commands
│
├── assets/                     # ✅ SHARED ASSETS
│   ├── fonts/                 # PetMe, Chicago, Monaco, Mallard, etc.
│   └── styles/                # Shared stylesheets (Synthwave DOS, NES)
│
├── cloned/                     # ✅ EXTERNAL TOOLS (gitignored)
│   ├── micro/                 # Modern terminal editor (Go)
│   ├── typo/                  # Markdown editor (Node.js)
│   └── coreui/                # CoreUI framework
│
├── setup/                      # ✅ INSTALLATION SCRIPTS
│   └── (setup scripts for external tools)
│
├── server_manager.py           # ✅ UNIFIED SERVER CONTROL
├── SERVER-MANAGEMENT.md        # Server documentation
└── README.md                   # This file
```

**Examples**: terminal

### Backend Extensions (Flask/Express)
Extensions with backend servers use **relative paths**:

```html
<!-- HTML references -->
<link rel="stylesheet" href="../../assets/css/typography-system.css">
<script src="../../assets/js/typography-manager.js"></script>
```

```css
/* CSS references */
url('../../assets/fonts/ChicagoFLF.woff2')
url('../../assets/icons/scrollbar-up.svg')
```

**Examples**: markdown, dashboard, desktop, teletext

---

## 🎯 **v1.0.24 Reorganization**

The v1.0.24 extensions branch consolidates all web-based extensions:

- **Phase 1**: Consolidated all extensions into `core/`
- **Phase 2**: Rebuilt Retro Terminal with PetMe font and Synthwave DOS palette
- **Phase 3**: Rebuilt Teletext with BBC standards and Mallard font
- **Phase 4**: Created central `/extensions/assets/` for shared resources
- **Phase 5**: Archived old c64-terminal and historical assets
- **Phase 4**: Created Character Editor with multi-resolution support
- **Phase 4.5-4.7**: Synthwave DOS colors, migration tools, refinements
- **Phase 5**: GitHub-flavored Markdown Viewer with uCODE and PANEL support
- **Phase 5.1**: Typography stack (Adobe Source Family fonts)
- **Phase 6**: Dashboard with NES.css framework
- **Phase 7**: System Desktop with System 7 CSS
- **Cleanup**: Archived redundant files, verified editors

### What's in `/archive`

The archive directory contains superseded implementations:

- **old-bundled-web/**: Original `bundled/web/` folder with first-generation extensions (dashboard, font-editor, markdown-viewer, system-desktop, teletext, styling frameworks). Now superseded by integrated `/core` versions.

- **old-clones/**: External CSS frameworks that have been integrated:
  - `classicy-desktop` → System 7 CSS in `/core/desktop`
  - `c64css3` → C64 Terminal in `/core/c64-terminal`
  - `nes-style` → NES Dashboard in `/core/dashboard`

- **obsolete/**: Future archival location for deprecated experiments

These files are preserved for reference and git history but are not actively maintained.

## 🚀 **Quick Start**

### **Install External Tools**
```bash
# Micro editor (CLI text editor with file picker)
./extensions/setup/setup_micro.sh

# Typo editor (Web markdown editor - requires Node 18/20/22)
./extensions/setup/setup_typo.sh
```

### **Use Core Extensions**
All core extensions are immediately available via uDOS:

```bash
# Launch extensions
python uDOS.py --extension dashboard     # NES Framework dashboard
python uDOS.py --extension desktop       # System 7 desktop
python uDOS.py --extension markdown      # GitHub markdown viewer
python uDOS.py --extension teletext      # BBC Teletext interface
python uDOS.py --extension retro-terminal  # Retro Terminal
python uDOS.py --extension character-editor  # Character/font editor
```

## 🎨 **Core Extensions**

### **Retro Terminal** (`/core/retro-terminal`)
- **Description**: Authentic retro terminal interface
- **Technology**: PetMe font + Synthwave DOS palette CSS
- **Features**: 40×25 text mode, PETSCII graphics, authentic colors
- **v1.0.24**: Complete rebuild with accurate font rendering

### **Character Editor** (`/core/character-editor`)
- **Description**: Multi-resolution character and font editor
- **Technology**: HTML5 Canvas + JavaScript
- **Features**: 8×8 to 128×128 grids, import/export, preview modes
- **v1.0.24**: New tool for custom font creation

### **Dashboard** (`/core/dashboard`)
- **Description**: NES.css framework system dashboard
- **Technology**: NES.css + Press Start 2P font
- **Features**: 6 widgets, real-time metrics, retro gaming aesthetic
- **v1.0.24**: Complete redesign with NES framework

### **Desktop** (`/core/desktop`)
- **Description**: System 7 desktop environment with uDOS integration
- **Technology**: System 7 CSS + Chicago font + Synthwave DOS
- **Features**: Window management, Command Palette (Cmd/Ctrl+K), desktop icons
- **v1.0.24**: Full System 7 implementation with keyboard shortcuts

### **Markdown Viewer** (`/core/markdown`)
- **Description**: GitHub-flavored markdown renderer
- **Technology**: GitHub CSS (light/dark) + Adobe Source fonts
- **Features**: uCODE commands, PANEL callouts, syntax highlighting
- **Typography**: Source Sans Pro (body), Source Serif Pro (headings), Source Code Pro (code)
- **v1.0.24**: Complete overhaul with GitHub CSS and typography stack

### **Teletext** (`/core/teletext`)
- **Description**: BBC Teletext broadcast interface
- **Technology**: Mallard font + Mode 7 graphics CSS
- **Features**: 40×25 character grid, Teletext graphics, Level 1 standard
- **v1.0.24**: Rebuild with authentic BBC Teletext rendering

### **Shared Libraries** (`/core/shared`)
- **Description**: Synthwave DOS color system and global CSS
- **Technology**: CSS custom properties + theme system
- **Features**: Unified color palette, theme variables, responsive utilities
- **v1.0.24**: Synthwave DOS integration across all extensions

## 🛠️ **External Tools**

### **micro Editor** (`/cloned/micro`)
- **Repository**: https://github.com/zyedidia/micro
- **Description**: Modern terminal-based text editor (Go)
- **Version**: 2.0.14
- **Features**: Syntax highlighting, plugin system, file picker, modern keybindings
- **Installation**: Binary download via `setup_micro.sh`
- **Status**: ✅ Installed and verified

### **typo Editor** (`/cloned/typo`)
- **Repository**: https://github.com/rossrobino/typo
- **Description**: Web-based markdown editor (Svelte)
- **Features**: Real-time preview, file picker, clean interface
- **Installation**: npm build via `setup_typo.sh`
- **Requirements**: Node.js 18, 20, or 22 (⚠️ not compatible with Node v24)
- **Status**: Dependencies installed, build requires Node version adjustment

## 🎨 **Retro Fonts**

All fonts are properly licensed for use in uDOS:

- **Chicago**: Apple System font (public domain)
- **Mallard**: BBC Teletext font (CC BY-SA 4.0)
- **Monaco**: Apple monospace font (system font)
- **sysfont**: System 7 bitmap fonts (OFL)
- **PetMe**: Commodore 64 PETSCII font (embedded in C64 Terminal)
- **Press Start 2P**: 8-bit gaming font (embedded in Dashboard)
- **Adobe Source Family**: Sans/Serif/Code Pro (embedded in Markdown Viewer)

See `/extensions/fonts/README.md` for detailed licensing information.

## 🔧 **Development Guidelines**

### **Adding Core Extensions**
1. Create extension in `core/[extension-name]/`
2. Include README.md with description and usage
3. Follow Synthwave DOS color standards (`core/shared/`)
4. Add CREDITS.md documenting dependencies
5. Update this README with extension details
6. Commit to v1.0.24-extensions branch

### **Adding External Tools**
1. Create setup script in `setup/setup_[name].sh`
2. Configure to clone/download into `cloned/[name]/`
3. Test installation process thoroughly
4. Document requirements and status
5. Update this README

### **Creating New Extensions**

Use the templates in `templates/` to scaffold new extensions:

```bash
# Copy template
cp -r extensions/templates/extension-template extensions/my-extension

# Follow template README
cd extensions/my-extension
```

### **Extension Structure**

Each core extension follows this structure:

```
core/[extension-name]/
├── index.html              # Main interface
├── static/
│   ├── [name].css         # Extension-specific styles
│   └── [name].js          # Extension logic
├── assets/                 # Images, icons, media
├── README.md              # Extension documentation
└── CREDITS.md             # Dependency attribution
```

### **Synthwave DOS Integration**

All extensions use the unified color system from `/core/shared/`:

```css
/* Import in your extension CSS */
@import url('../shared/synthwave-dos.css');

/* Use theme variables */
background-color: var(--dos-bg);
color: var(--dos-text);
border-color: var(--dos-border);
```

### **Font Management**

Fonts are centralized in `/fonts/` and referenced via CSS:

```css
@font-face {
    font-family: 'Chicago';
    src: url('/extensions/fonts/chicago/ChicagoFLF.ttf');
}
```

## ⚖️ **Legal Compliance**

All bundled fonts are legally distributable:
- **ChicagoFLF**: Public domain
- **Chicago 12.1**: CC BY-SA 3.0
- **Mallard family**: CC BY-SA 3.0
- **sysfont**: SIL Open Font License 1.1

See `/extensions/fonts/README.md` for complete legal analysis.

## 🎯 **Platform Support**

### **Tested Platforms**
- ✅ macOS (Intel & Apple Silicon)
- ✅ Linux (Ubuntu, Debian, Arch)
- ✅ Windows (WSL2 recommended)

### **Browser Compatibility** (for web extensions)
- ✅ Chrome/Chromium 90+
- ✅ Firefox 88+
- ✅ Safari 14+
- ✅ Edge 90+

## 📚 **Additional Resources**

- **Extension Documentation**: Individual README.md files in each `/core` extension
- **CREDITS**: Attribution in CREDITS.md files throughout `/core`
- **Templates**: Extension scaffolding in `/templates`
- **Archive**: Historical implementations in `/archive` (reference only)
- **uDOS Wiki**: Complete extension development guides
- **Git History**: Full development timeline on v1.0.24-extensions branch

---

**🎉 v1.0.24 Extensions: Unified core structure, retro aesthetics, modern functionality.**
