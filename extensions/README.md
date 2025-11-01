# uDOS Extensions

This directory contains information about extensions that enhance uDOS with additional editors, servers, fonts, and tools. All extensions are **MIT or OFL licensed** and available as GitHub forks.

> **For detailed contribution guidelines and development workflow, see the [Contributing Guide](https://github.com/fredporter/uDOS/wiki/Contributing) on the wiki.**

> **For complete licensing information and attributions, see [CREDITS.md](../CREDITS.md) in the root directory.**

---

## 🎯 Quick Start

**Choose your approach:**

### Option 1: Clone & Use (Recommended)
```bash
# Clone the tools you want:
git clone https://github.com/fredporter/udos-micro
git clone https://github.com/fredporter/udos-typo
git clone https://github.com/fredporter/udos-cmd
git clone https://github.com/fredporter/udos-fonts

# Follow each tool's README for installation
```

### Option 2: Fork & Customize
```bash
# Fork on GitHub UI first, then:
git clone https://github.com/yourusername/udos-micro
git clone https://github.com/yourusername/udos-typo

# Make your customizations and contribute back!
```

---

## 🔧 Available Extensions

All extensions are maintained as forks for stability and uDOS-specific customizations.

### 📝 Editors

#### micro - Modern Terminal Editor
- **uDOS Fork**: https://github.com/fredporter/udos-micro
- **Original**: https://github.com/zyedidia/micro
- **License**: MIT
- **Features**: Mouse support, multiple cursors, syntax highlighting for 75+ languages
- **Installation**: See [micro installation guide](https://github.com/fredporter/udos-micro#installation)
- **uDOS Integration**: Use with `EDIT --cli filename.txt`

#### typo - Web-Based Markdown Editor
- **uDOS Fork**: https://github.com/fredporter/udos-typo
- **Original**: https://github.com/rossrobino/typo
- **License**: MIT
- **Features**: Live preview, auto-save, slide mode, code execution blocks
- **Requirements**: Node.js 18+ and npm
- **Installation**: `git clone` → `npm install` → `npm run dev`
- **uDOS Integration**: Use with `SERVER START typo` then `EDIT --web filename.md`

#### cmd.js - Web Terminal Emulator
- **uDOS Fork**: https://github.com/fredporter/udos-cmd
- **Original**: https://github.com/mrchimp/cmd
- **License**: MIT
- **Features**: Full terminal in browser, command history, tab completion
- **Requirements**: Node.js 14+ and npm
- **Installation**: `git clone` → `npm install` → `npm start`
- **uDOS Integration**: Use with `SERVER START cmd` for browser terminal

---

### 🎨 Fonts

#### Monaspace - Coding Font Family
- **uDOS Fork**: https://github.com/fredporter/udos-fonts
- **Original**: https://github.com/githubnext/monaspace
- **License**: SIL Open Font License (OFL) 1.1
- **Variants**: Neon, Argon, Xenon, Radon, Krypton
- **Installation**: Download WOFF2/OTF files from releases
- **uDOS Integration**: Used in web terminal and font editor

---

## 🌐 Native Web Apps

These are original uDOS applications (tracked in this repository):

### 🎛️ Dashboard
- **Path**: `extensions/web/dashboard/`
- **Purpose**: System overview and control interface
- **Features**: Real-time stats, server management, file browser
- **Usage**: `DASHBOARD WEB` or `SERVER START dashboard`

### ✏️ Font Editor
- **Path**: `extensions/web/font-editor/`
- **Purpose**: 16×16 bitmap font creation tool
- **Features**: Pixel editor, preview, export to various formats
- **Usage**: `SERVER START font-editor`

### 📖 Markdown Viewer
- **Path**: `extensions/web/markdown-viewer/`
- **Purpose**: Enhanced markdown rendering with syntax highlighting
- **Features**: GitHub Flavored Markdown, code highlighting, print styles
- **Usage**: `SERVER START markdown-viewer`

### 💻 Terminal Interface
- **Path**: `extensions/web/terminal/`
- **Purpose**: uDOS command interface in browser
- **Features**: Command execution, history, file upload/download
- **Usage**: `SERVER START terminal`

### 🎨 Shared Components
- **Path**: `extensions/web/shared/`
- **Purpose**: Common CSS frameworks and JavaScript utilities
- **Contents**: classic.css, NES.css, system.css, uDOS grid system

---

## 📝 Editors

### micro - Modern Terminal Editor

A modern, intuitive terminal-based text editor with mouse support, multiple cursors, and syntax highlighting.

**Installation:**
```bash
# From uDOS command prompt:
EDIT --install-micro

# Or manually:
cd extensions
bash setup_micro.sh
```

**Features:**
- Mouse support and clipboard integration
- Multiple cursors and selections
- Syntax highlighting for 75+ languages
- Plugin system with 50+ plugins available
- Cross-platform (macOS, Linux, Windows)

**Usage:**
```
EDIT --cli myfile.txt        # Uses micro if installed
EDIT --editor micro test.md  # Force micro
```

**Resources:**
- [micro GitHub](https://github.com/zyedidia/micro)
- [Documentation](https://github.com/zyedidia/micro/tree/master/runtime/help)

---

### typo - Web-Based Markdown Editor

A Svelte/Node.js web application for editing markdown with live preview, auto-save, and slide mode.

**Installation:**
```bash
cd extensions
bash setup_typo.sh
```

**Requirements:**
- Node.js 18+ and npm

**Features:**
- Live markdown preview with GitHub Flavored Markdown
- File System Access API for seamless file editing
- Auto-save and slide presentation mode
- Code execution blocks (JavaScript, Python, etc.)
- Customizable themes

**Usage:**
```
SERVER START typo            # Start on port 5173
EDIT --web document.md       # Edit in browser
SERVER STATUS                # Check if running
SERVER STOP typo             # Stop server
```

**Resources:**
- [typo GitHub](https://github.com/rossrobino/typo)
- [Live Demo](https://typo.robino.dev/)
- See [`web/README.md`](web/README.md) for detailed integration guide

---

### cmd.js - Web Terminal Emulator

An HTML5 command-line terminal running in the browser, with Monaspace font integration and command history.

**Installation:**
```bash
cd extensions
bash setup_cmd.sh
```

**Requirements:**
- Node.js 14+ and npm
- Grunt (installed automatically)

**Features:**
- Full-featured terminal interface in the browser
- All 5 Monaspace font variants with real-time switching
- Command history with localStorage persistence
- Tab completion support
- Light/dark theme toggle
- Responsive design for desktop and mobile

**Usage:**
```
SERVER START cmd             # Start on port 3000
SERVER START cmd --port 8080 # Custom port
SERVER STATUS cmd            # Check server status
SERVER STOP cmd              # Stop server
```

**Terminal Commands:**
```
🔮 > help                    # Show available commands
🔮 > font neon               # Switch to Monaspace Neon
🔮 > fonts                   # List all font variants
🔮 > status                  # Terminal configuration
🔮 > clear                   # Clear screen
🔮 > invert                  # Toggle theme
```

**Font Variants:**
- **neon** - Default, clean and modern
- **argon** - Warm and readable
- **xenon** - Editorial slab serif
- **radon** - Handwriting style
- **krypton** - Technical and precise

**Architecture:**
- **Core**: mrchimp/cmd terminal library (MIT license)
- **Server**: http-server (static file serving)
- **Integration**: udos_cmd_bridge.html with Monaspace fonts
- **State**: Font preferences saved to browser localStorage
- **Future**: Backend API for uDOS command forwarding

**Resources:**
- [cmd.js GitHub](https://github.com/mrchimp/cmd)
- See [`web/cmd/README.md`](web/cmd/README.md) for detailed documentation

---

### font-editor - 16×16 Bitmap Font Creator

A retro-inspired web-based pixel editor for creating custom 16×16 monospace bitmap fonts.

**Installation:**
No installation needed - pure HTML/CSS/JS application.

**Usage:**
```bash
# Open directly in browser:
open extensions/web/font-editor/index.html

# Or with HTTP server:
cd extensions/web/font-editor
python3 -m http.server 8000
# Visit http://localhost:8000
```

**Features:**
- **16×16 Pixel Grid** - Standard uCELL format
- **Real-time Preview** - See your font rendered instantly
- **Auto-Save** - Changes saved to browser localStorage
- **Export/Import** - JSON format for sharing
- **120 Character Slots** - ASCII + Box Drawing + Block Elements
- **Editing Tools** - Clear, Fill, Flip H/V, Rotate, Invert
- **Copy/Paste** - Duplicate glyphs quickly
- **Keyboard Shortcuts** - Fast workflow
- **Retro Design** - Green-on-black terminal aesthetic

**Workflow:**
1. Open font-editor in browser
2. Select character from dropdown
3. Draw on 16×16 grid (click/drag)
4. Use tools to transform pixels
5. Export as JSON when complete
6. (Future) Convert to WOFF2 for terminal use

**File Format:**
Fonts export as JSON with binary pixel data:
```json
{
  "fontName": "uDOS Custom",
  "author": "Your Name",
  "glyphs": {
    "U+0041": ["0000000000000000", "0000000110000000", ...]
  }
}
```

**Resources:**
- See [`web/font-editor/README.md`](web/font-editor/README.md) for detailed documentation
- Integration with Monaspace via CSS unicode-range
- ~2KB per font vs 625KB for Monaspace (300× smaller)

---

## 🔤 Fonts

### Monaspace - Professional Coding Fonts

A superfamily of five coding fonts from GitHub Next with advanced typography features.

**Installation:**
```bash
cd extensions
bash setup_monaspace.sh
```

**Variants:**
- **Neon** - Neo-grotesque sans (clean and modern) - *Default*
- **Argon** - Humanist sans (warm and readable)
- **Xenon** - Slab serif (editorial and strong)
- **Radon** - Handwriting (casual and personal)
- **Krypton** - Mechanical sans (technical and precise)

**Features:**
- **Texture Healing™** - Advanced character spacing for readability
- **Coding Ligatures** - Enhanced symbol combinations
- **Powerline Symbols** - Terminal integration glyphs
- **Variable Font Technology** - Flexible weight and width control

**Usage:**
```
FONT LIST                    # View all variants with status
FONT SET ARGON               # Switch to Argon variant
FONT INFO                    # Current configuration
```

**Web Integration:**
- Automatically available to typo editor and cmd.js terminal
- WOFF2 format optimized for web performance
- Configure via `data/FONTS.UDO`

**CLI Terminal Use:**
For native terminal use (outside browser), install system fonts manually:
- **macOS**: Open Font Book → Add fonts from `extensions/clone/fonts/monaspace/`
- **Linux**: Copy to `~/.local/share/fonts/` and run `fc-cache -fv`
- **Windows**: Install OTF files to `C:\Windows\Fonts\`

**Resources:**
- [Monaspace GitHub](https://github.com/githubnext/monaspace)
- [Official Site](https://monaspace.githubnext.com/)
- [Configuration](../data/FONTS.UDO)

---

## 📂 Directory Structure

```
extensions/
├── README.md              # This file - Extension documentation
├── web/                   # Native uDOS web applications (tracked in git)
│   ├── dashboard/         # System overview and control interface
│   │   ├── index.html
│   │   ├── server.py
│   │   ├── css/
│   │   └── js/
│   ├── font-editor/       # 16×16 bitmap font creator
│   │   ├── index.html
│   │   ├── server.py
│   │   ├── css/
│   │   └── js/
│   ├── markdown-viewer/   # Enhanced markdown rendering
│   │   ├── index.html
│   │   ├── server.py
│   │   └── css/
│   ├── terminal/          # Web terminal interface
│   │   ├── index.html
│   │   ├── server.py
│   │   └── QUICKSTART.md
│   └── shared/            # Common CSS/JS components
│       ├── classic.css    # Mac OS 8.1 styling
│       ├── nes.css        # Retro gaming styling
│       ├── system.css     # Windows styling
│       └── udos-*.js      # uDOS utilities
└── (Third-party tools)    # Clone separately as needed
    ├── micro/             # Clone: fredporter/udos-micro
    ├── typo/              # Clone: fredporter/udos-typo
    ├── cmd/               # Clone: fredporter/udos-cmd
    └── monaspace/         # Clone: fredporter/udos-fonts
```

**Third-party tools are NOT included in uDOS repository.**
Clone them separately as needed from the GitHub forks.

---

## 🚀 Installation Guide

### For End Users (Recommended)

**Just want to use the tools?** Clone them directly:

```bash
# Choose what you need:
cd ~/tools  # or wherever you keep tools

# Modern terminal editor
git clone https://github.com/fredporter/udos-micro
cd udos-micro && make install  # Follow their install guide

# Web markdown editor
git clone https://github.com/fredporter/udos-typo
cd udos-typo && npm install && npm run dev

# Browser terminal
git clone https://github.com/fredporter/udos-cmd
cd udos-cmd && npm install && npm start

# Coding fonts
git clone https://github.com/fredporter/udos-fonts
# Download fonts from releases page
```

### For Developers & Customizers

**Want to modify or contribute?** Fork first:

1. **Fork on GitHub**: Go to each repo and click "Fork"
2. **Clone your fork**:
   ```bash
   git clone https://github.com/yourusername/udos-micro
   git clone https://github.com/yourusername/udos-typo
   ```
3. **Make changes** and submit pull requests back to `fredporter/udos-*`

### For uDOS Integration

**Want tight integration?** Use the OUTPUT command:

```bash
# In uDOS:
OUTPUT START typo      # Starts typo server
OUTPUT START cmd       # Starts cmd.js terminal
OUTPUT STATUS          # Check all running servers
OUTPUT STOP typo       # Stop specific server
```

---

## 🔧 Extension Management

### CLI Editors

The `EDIT` command auto-detects available editors:
1. User preference (set via `EDIT --editor <name>`)
2. micro (if installed)
3. nano (system default)
4. vim/vi (fallback)

**Configuration:**
- Preferences stored in `data/USER.UDT` under `EDITOR_PREFERENCES`
- View current config: `EDIT --config`

### Web Servers

The `SERVER` command manages web-based extensions:
- Process tracking with PID persistence
- Port conflict detection
- Browser auto-launch
- Graceful shutdown

**Available Servers:**
- **typo** - Markdown editor (default port 5173)
- **cmd** - Terminal emulator (default port 3000)

**State File:** `sandbox/.server_state.json`

### Font System

The `FONT` command manages Monaspace variants:
- Lists installed fonts and their status
- Sets user preferences for web interfaces
- Displays current configuration

**Configuration Files:**
- Font metadata: `data/FONTS.UDO`
- User preferences: `data/USER.UDT`

---

## 🚀 Coming Soon

Future extensions planned:
- **Backend API** - Flask/FastAPI for cmd.js command forwarding
- **FontForge** - Font editing capabilities
- **WebSocket Support** - Real-time terminal communication
- Additional editors and tools

---

## .gitignore

All downloaded/installed extension files are in the `clone/` folder and ignored by git. This keeps the repository clean while allowing full local installations.

**Tracked (synced with git):**
- `README.md` files
- `setup_*.sh` installer scripts
- Documentation files

**Ignored (local installations only):**
- `clone/` - All downloaded/built extensions
  - `clone/fonts/monaspace/` - Font files
  - `clone/web/typo/` - typo Node.js app
  - `clone/web/cmd/` - cmd.js repository
  - `clone/native/micro/` - micro binary

This structure ensures your git repository stays lightweight while supporting full local extension installations.

---

## 📖 Documentation

- **Main Wiki**: [uDOS Wiki](https://github.com/fredporter/uDOS/wiki)
- **Contributing**: [Contributing Guide](https://github.com/fredporter/uDOS/wiki/Contributing)
- **Command Reference**: [Command Reference](https://github.com/fredporter/uDOS/wiki/Command-Reference)
- **Development Workflow**: See wiki for Development Round process
