# uDOS v1.0.0 - Human-Readable Core

**uDOS** is a modular CLI framework with assistant integration, comprehensive diagnostics, and modern web extensions. Built to demonstrate clean architecture, human-readable command systems, and intelligent workflows.

**Status**: ✅ v1.0.0 Foundation Release - Refactored and ready for systematic improvement

---

## 🎯 What's New in v1.0.0

### Major Refactoring
- **60% code reduction** - From 3,249 to 1,297 lines through modular handlers
- **AI → Assistant** - Clearer terminology throughout
- **Organized docs** - `/docs` structure with planning, guides, and archives
- **Systematic roadmap** - 16 focused development rounds (v1.0.1 → v1.1.0)

### Clean Architecture
```
core/commands/
├── assistant_handler.py   # ASK, ANALYZE, EXPLAIN, GENERATE
├── file_handler.py         # NEW, DELETE, COPY, MOVE, EDIT, RUN
├── grid_handler.py         # Deprecated (migration messages)
├── map_handler.py          # Navigation and positioning
└── system_handler.py       # REPAIR, STATUS, DASHBOARD, etc.
```

See [`dev/docs/archive/REFACTORING-v1.0.0.md`](dev/docs/archive/REFACTORING-v1.0.0.md) for details.

---

## 📖 Documentation

### 🚀 Getting Started
- [**Quick Start Guide**](wiki/Quick-Start.md) - Get running in 5 minutes
- [Installation](wiki/Quick-Start.md#installation) - Setup instructions
- [Command Reference](wiki/Command-Reference.md) - Complete command list

### 📚 Development
- [**ROADMAP.MD**](ROADMAP.MD) - **v1.0.x systematic development plan**
- [Contributing Guide](dev/docs/guides/CONTRIBUTING.md) - Development workflow
- [Testing Guide](dev/docs/guides/TESTING.md) - Testing procedures
- [Development Setup](dev/docs/guides/DEVELOPMENT.md) - Dev environment

### 🗺️ Development Rounds (v1.0.x)
Each round focuses on ONE component with complete testing cycle:

| Round | Component | Focus |
|-------|-----------|-------|
| v1.0.1 | System Commands | HELP, STATUS, REPAIR, DASHBOARD |
| v1.0.2 | File Operations | NEW, EDIT, COPY, MOVE, RUN |
| v1.0.3 | Assistant Integration | ASK, ANALYZE, EXPLAIN, GENERATE |
| v1.0.4 | Map System | Navigation, layers, positioning |
| v1.0.5 | Web Servers | Port management, server lifecycle |
| v1.0.6 | CLI Terminal | Viewport, colors, interactive prompts |
| v1.0.7 | Web Dashboard | classic.css, system stats |
| v1.0.8 | Web Terminal | NES.css, xterm.js integration |
| v1.0.9 | Markdown Viewer | system.css, file browser |
| v1.0.10 | Font Editor | Monaspace, pixel art tools |
| v1.0.11 | Typo Editor | Advanced text editing |
| v1.0.12 | Knowledge System | Research, notes, linking |
| v1.0.13 | Theme System | DUNGEON, GALAXY, FOUNDATION |
| v1.0.14 | Extension System | Plugin architecture, LIBRARY.UDO |
| v1.0.15 | uCODE Language | Scripting, control flow |
| v1.0.16 | Security | Permissions, encryption, audit |
| v1.1.0 | **Stable Release** | Integration and polish |

**See [ROADMAP.MD](ROADMAP.MD) for detailed breakdown of each round.**

### 📖 Reference
- [uCODE Manual](wiki/uCODE-Language.md) - Internal scripting system
- [Mapping System](wiki/Mapping-System.md) - NetHack-style navigation
- [Architecture](wiki/Architecture.md) - How uDOS works
- [Style Guide](wiki/Style-Guide.md) - Code conventions

### 📁 Documentation Hub
All docs organized in [`/dev/docs`](dev/docs/):
- [`dev/docs/guides/`](dev/docs/guides/) - User and developer guides
- [`dev/docs/planning/`](dev/docs/planning/) - Development planning
- [`dev/docs/archive/`](dev/docs/archive/) - Historical refactoring docs

---

## Quick Start

```bash
# Clone the repository
git clone https://github.com/fredporter/uDOS.git
cd uDOS

# Activate virtual environment
source .venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Run uDOS
./start_udos.sh
```

**First-time setup will guide you through:**
- Name and project details
- Theme selection (DUNGEON_CRAWLER, CYBERPUNK, MINIMAL)
- Creates personalized `data/STORY.UDO`

**For AI features (optional):**
```bash
echo 'GEMINI_API_KEY=your_key_here' > .env
```

**Note:** uDOS works fully offline without an API key.

---

## Core Features

- ✅ **Hybrid Parser** - User-friendly commands → structured `uCODE`
- ✅ **Themed Lexicon** - Customizable terminology and messages
- ✅ **Multi-Panel System** - Organized text buffer management
- ✅ **Session Logging** - Complete interaction history
- ✅ **Script Execution** - Automation via `.uscript` files
- ✅ **Connection Awareness** - Auto-detect online/offline mode
- ✅ **Viewport Detection** - Adapts to terminal size and device type
- ✅ **Smart Completion** - Context-aware tab completion with dropdown
- ✅ **Error Recovery** - REPAIR, UNDO/REDO, RESTORE capabilities
- ✅ **Offline Engine** - Pattern-matching AI for offline operation

---

## 🆕 v1.3 Major Features

**Enhanced Startup System:**
- ✅ **Intelligent health checks** - Python version, dependencies, configuration validation
- ✅ **Auto-repair capabilities** - Missing directories, packages, config files
- ✅ **User-friendly diagnostics** - Color-coded status, actionable recommendations
- ✅ **AI-assisted debugging** - Diagnostic reports with DEBUG command
- ✅ **Silent/report modes** - Automation-friendly operation

**Gemini AI Integration:**
- ✅ **Full CLI integration** - ASK, ANALYZE, EXPLAIN, GENERATE, DEBUG commands
- ✅ **Gemini 2.5 Flash** - Latest Google AI model with conversation history
- ✅ **Context-aware** - Workspace and system information included
- ✅ **Offline fallback** - Works without API key using pattern-matching
- ✅ **Secure configuration** - CLI-only .env editing, API key masking

**Configuration Management:**
- ✅ **CONFIG command** - List, get, set, validate settings
- ✅ **Secure storage** - .env file with masked display
- ✅ **Dynamic updates** - Change settings without restart
- ✅ **Installation tracking** - Unique ID, username, workspace preferences

**Retro CSS Framework Integration:**
- ✅ **system.css** - Mac System 6 aesthetic for Font Editor & Markdown Viewer
- ✅ **NES.css** - 8-bit gaming style for Terminal
- ✅ **classic.css + After Dark CSS** - Mac OS 8.1 + screensavers for Dashboard
- ✅ **Authentic 1980s/90s computing** - Period-accurate fonts, components, animations
- ✅ **Complete attribution** - All frameworks properly credited and licensed

**File Management & Web Dashboard:**
- ✅ **Complete file operations** - CREATE, DELETE, RENAME, COPY, MOVE with UNDO/REDO
- ✅ **GitHub-style dashboard** - Dark/Light themes, extension management
- ✅ **Modern web extensions** - Font editor, markdown viewer, terminal, typo editor
- ✅ **Workspace system** - Organized sandbox/memory/data structure

**Quick start with v1.3:**
```
ASK "explain uDOS features"    # AI assistance
CONFIG list                     # View configuration
DASH WEB                        # Open dashboard (Mac OS 8.1 style)
OUTPUT START font-editor        # Mac System 6 font editor
OUTPUT START terminal           # NES 8-bit terminal
DEBUG "startup error"           # AI error diagnosis
```

---

## 🆕 Extension System

**Web Extensions - Production Ready with Retro Styling:**

### 🌐 **Web Extension Management**
- **OUTPUT Command** - Manage web-based tools with authentic retro aesthetics
  - **typo** - Markdown editor (Port 5173)
  - **markdown-viewer** - Mac System 6 style rendering with uCODE syntax (Port 8889) ✨
  - **font-editor** - Mac System 6 bitmap font creator (Port 8888) ✨
  - **cmd/terminal** - NES 8-bit web terminal emulator (Port 8890) ✨
  - **dashboard** - Mac OS 8.1 + After Dark control panel (Port 8887) 🔜
- **Non-Blocking Architecture** - Servers run in background
- **Features**: Start/stop tracking, auto-launch, log management
- **Examples**:
  ```
  OUTPUT LIST             # List all extensions
  OUTPUT START typo       # Start editor
  OUTPUT STATUS           # Check servers
  DASH WEB                # Open retro dashboard
  ```

### 🎨 **Retro CSS Frameworks**
- **system.css** - Apple System 6 (1984-1991)
  - Monochrome Mac aesthetic
  - Pixel-perfect windows, scrollbars
  - Chicago_12, Monaco fonts
  - Used in: Font Editor, Markdown Viewer

- **NES.css** - Nintendo Entertainment System
  - 8-bit gaming style
  - Pixelated borders, retro colors
  - Press Start 2P font
  - Used in: Terminal

- **classic.css + After Dark CSS** - Mac OS 8.1 + Screensavers
  - Mac OS 8.1 window chrome
  - Flying Toasters screensaver effects
  - ChicagoFLF typography
  - Used in: Dashboard (in progress)

See `/docs/CSS-FRAMEWORK-ATTRIBUTION.md` for complete framework credits and licensing.

### 📝 **CLI & Web Editors**
- **EDIT Command** - Unified file editing
  - Built-in: `nano`, `vim`, `vi`
  - Modern: `micro` (installable)
  - Web: `typo` (Svelte markdown editor)
- **Examples**:
  ```
  EDIT myfile.md              # Auto-detect editor
  EDIT --web document.md      # Open in browser
  EDIT --editor nano test.txt # Force specific editor
  ```

### 🔤 **Monaspace Fonts**
- **FONT Command** - Professional coding fonts
  - 5 variants: Neon (default), Argon, Xenon, Radon, Krypton
  - Features: Texture Healing™, ligatures, Powerline
  - Install: `bash extensions/setup_monaspace.sh`

### 🎨 **Font Editor**
- **16×16 bitmap font editor** in browser with Mac System 6 styling ✨
  - 120 character slots with editing tools
  - Live preview, auto-save, JSON export
  - Authentic monochrome Mac interface
  - Access: `OUTPUT START font-editor`

### 📖 **Markdown Viewer**
- **Mac System 6 style rendering** ✨
  - Custom uCODE syntax highlighting
  - .md and .UDO file support
  - Classic Mac window chrome
  - Chicago/Monaco fonts
  - Access: `OUTPUT START markdown-viewer`

### � **Web Terminal**
- **NES 8-bit gaming aesthetic** ✨
  - Retro command execution
  - Press Start 2P font
  - Pixelated borders and buttons
  - Command counter badges
  - Access: `OUTPUT START terminal`

### 📊 **Web Dashboard**
- **Mac OS 8.1 + After Dark screensavers** 🔜
  - Classic Mac window chrome
  - Flying Toasters animations
  - Extension start/stop/open controls
  - Live status, activity log
  - Responsive design (desktop + mobile)
  - Access: `DASH WEB`

See [Web Extensions Guide](docs/WEB-OUTPUT-GUIDE.md) and [CSS Integration Guide](docs/SYSTEM-CSS-INTEGRATION.md) for detailed documentation.

---

## 📁 Folder Structure

### Root Directory

```
uDOS/
├── core/                  # Core Python modules (20 files)
├── data/                  # System configuration (COMMANDS.UDO, LEXICON.UDO, etc.)
├── wiki/                  # GitHub wiki source (11 pages)
├── sandbox/               # Working directory (gitignored)
│   ├── tests/            # Test scripts and files
│   └── logs/             # Server logs
├── memory/                # Permanent user data (tracked)
├── knowledge/             # Reference library
├── examples/              # Visual examples (HELP, DASH outputs)
├── extensions/            # Web extension system
│   ├── web/              # Web-based extensions
│   │   ├── font-editor/  # 16×16 bitmap font editor
│   │   ├── markdown-viewer/  # GitHub markdown renderer
│   │   └── cmd/          # Web terminal (planned)
│   └── setup_*.sh        # Installation scripts
├── history/               # Historical files (organized by type)
│   ├── concepts/         # Old design documents
│   ├── data/             # Old configuration formats
│   ├── dev/docs/         # Dev round summaries and notes
│   ├── docs_active/      # Previous active documentation
│   └── extensions/       # Extension backups
├── uDOS.py                # Entry point
├── start_udos.sh          # Launch script
├── structure.txt          # Auto-generated tree (TREE command)
└── README.MD              # This file
```

### Core System (`/core`)

All Python modules organized in one place:

```
core/
├── uDOS_main.py          # Main application loop
├── uDOS_commands.py      # Command handler
├── uDOS_parser.py        # CLI to uCODE parser
├── uDOS_ucode.py         # uCODE interpreter
├── uDOS_grid.py          # Grid/panel system
├── uDOS_map.py           # Mapping engine
├── uDOS_viewport.py      # Display viewport
├── uDOS_viewport_viz.py  # Visualization
├── uDOS_tree.py          # Tree generator
├── uDOS_history.py       # Action history
├── uDOS_health.py        # System health
├── uDOS_connection.py    # Online/offline modes
├── uDOS_offline.py       # Offline engine
├── uDOS_completer.py     # Tab completion
├── uDOS_prompt.py        # Dynamic prompt
├── uDOS_splash.py        # Splash screen
├── uDOS_user.py          # User profile manager
├── uDOS_logger.py        # Logging system
├── uDOS_setup.py         # Setup wizard
└── __init__.py           # Package initialization
```

### Key Directories

**`/data`** - System configuration (tracked)
- `COMMANDS.UDO` (v1.1) - Command definitions with uCODE templates
- `LEXICON.UDO` - Themed terminology
- `PALETTE.UDO` - Color palette
- `PROMPTS.UDO` - Offline AI prompts
- `FONTS.UDO` - Font configurations
- `*.UDT` - Templates

**`/sandbox`** - Working directory (NOT tracked)
- Temporary files and session logs
- Test scripts and experiments in `/tests`
- Server logs in `/logs`
- Use `CLEAN` to review and commit to `/memory`

**`/memory`** - Permanent user data (tracked)
- Research findings and knowledge
- Completed missions and projects
- Historical records
- `/scripts` - Maintainer scripts (deploy_wiki.sh, etc.)

**`/wiki`** - GitHub wiki source (tracked)
- Markdown files deployed via `memory/scripts/deploy_wiki.sh`
- Complete documentation and guides (11 pages)

**`/history`** - Historical files (tracked)
- `/concepts` - Old design documents
- `/data` - Outdated configuration formats
- `/docs` - **Dev round summaries and completed notes** ⭐
- `/docs_active` - Previous active documentation
- `/extensions` - Extension backups

Run `TREE` command in uDOS to generate/update `structure.txt` with complete repository structure.

---

## Learning Objectives

This project demonstrates:
- **Modular Architecture** - Separation of concerns (parsing, execution, UI)
- **Data-Driven Design** - Commands and terminology in JSON
- **Hybrid Systems** - Human-readable layer over structured backend
- **API Integration** - Gemini AI integration patterns
- **Testing Strategies** - Automated script-based testing
- **Development Tooling** - VS Code workspace configuration

---

## Current Status

**Version 1.3.0** - Production-ready with AI integration and intelligent startup:
- ✅ Enhanced startup system with auto-repair
- ✅ Gemini AI integration (ASK, ANALYZE, DEBUG commands)
- ✅ Configuration management with secure .env handling
- ✅ File operations with UNDO/REDO
- ✅ GitHub-style web dashboard
- ✅ Four web extensions (dashboard, markdown-viewer, font-editor, typo, cmd)
- ✅ Offline capabilities with pattern-matching AI
- ✅ Professional command reference and documentation

**Latest Release (October 2025)**:
- v1.3.0: Enhanced startup, Gemini AI, configuration management
- Complete health diagnostics with auto-repair
- AI-assisted error debugging
- Secure API key management

See [V1.3-COMPLETE-RELEASE.md](dev/docs/V1.3-COMPLETE-RELEASE.md) for full v1.3 documentation and [ROADMAP.MD](ROADMAP.MD) for future plans.

---

## Contributing

See [Contributing Guide](https://github.com/fredporter/uDOS/wiki/Contributing) for the Development Round workflow and contribution guidelines.

---

## License

This program is free software licensed under the GNU General Public License v3.0.

**uDOS v1.3** - Copyright (C) 2025 Fred Porter

See [LICENSE.txt](LICENSE.txt) for the complete license text.

