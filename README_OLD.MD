# uDOS v1.1.2 - Production Release

**uDOS** is a secure, dual-interface CLI framework with role-based access control, offline knowledge management, web GUI, and AI integration. Built for self-sufficiency, survival preparation, and sustainable living with a human-readable command system.

**Current Status**: ✅ **v1.1.2 Production Release** (Nov 24, 2025)
**Test Coverage**: **1,062 tests passing** (100%)
**Next**: v1.1.3 Adventure & Economy Systems (Q4 2026)

---

## 🚀 v1.1.2 Production Release

### Release Highlights

**Zero Breaking Changes** | **1,062 Tests Passing** | **Full v1.0.x Compatibility**

🔐 **Enterprise Security**
- RBAC with 4 user roles (User/Power/Wizard/Root)
- 4-tier memory encryption (AES-256/AES-128)
- Installation integrity verification (SHA-256)
- Command-based security hardening

🌐 **Dual Interface**
- Production web server with Teletext display
- CLI→Web delegation API with state sync
- Browser extension (Chrome/Firefox/Edge)
- Mobile PWA with offline capability

📚 **Offline Knowledge**
- 8-category library (foundation for 500+ guides)
- AI prompt development (no API calls required)
- SVG/citation pipeline with bibliography
- Content validation and quality scoring

🎯 **Production Ready**
- Cross-platform (macOS/Linux/Windows)
- 16+ terminal emulators validated
- Complete documentation (wiki + API docs)
- pip installable, offline-first

[📖 Full Release Notes](wiki/Release-v1.1.2.md) | [🗺️ Roadmap](ROADMAP.MD) | [📝 Changelog](CHANGELOG.md)

---

## 🎯 What's Included

### v1.1.0 - Core TUI Stabilisation (268 tests)

**AI Assistant & Role Security**
- Role-based API access (Wizard unrestricted, User offline-first)
- Offline fallback to 4-Tier Knowledge Bank
- Live session analytics with command trace
- Intelligent error handler with contextual solutions
- User feedback system (`FEEDBACK` and `REPORT` commands)

**TUI Reliability & Input System**
- Unified selector with automatic fallback (16+ terminals)
- Cross-platform retro graphics (BBC Teletext aesthetic)
- Session replay and pattern analysis
- Unified command handlers (DOCS, LEARN, MEMORY)
- POKE commands for system inspection

### v1.1.1 - Web Extension & Dual-Interface (327 tests)

**Web Infrastructure**
- Production server with health monitoring
- Teletext display with WebSocket streaming
- CLI→Web delegation for visual interactions
- State synchronization with event sourcing
- Reusable web component library

**Advanced Web Features**
- Browser extension for knowledge capture
- Mobile PWA with service workers
- Touch-optimized interface
- Offline caching and background sync

### v1.1.2 - Security & Offline Knowledge (467 tests)

**Advanced Security & Roles**
- **RBAC System** (58 tests): 4 roles with permission inheritance
- **Command Security** (59 tests): Centralized security layer, offline-first enforcement
- **4-Tier Memory** (58 tests): Private/Shared/Community/Public with encryption
- **Installation Types** (59 tests): CLONE/SPAWN/HYBRID with integrity checks

**Knowledge Bank & AI Integration**
- **Offline Knowledge** (60 tests): 8 categories, full-text search, versioning
- **AI Prompts** (61 tests): Template system, role-specific, validation
- **SVG/Citation** (59 tests): Diagram generation, APA/MLA/Chicago/IEEE formats
- **Validation** (53 tests): Content quality, freshness, contradiction detection

---

## 📊 Test Coverage

```
Total Tests: 1,062/1,062 passing (100%)

v1.1.0: 268 tests (AI, TUI, session analytics, retro graphics)
v1.1.1: 327 tests (web server, browser extension, mobile PWA)
v1.1.2: 467 tests (RBAC, 4-tier memory, offline knowledge, validation)

Platform Support:
✅ macOS 11+ (Intel & Apple Silicon)
✅ Linux (Ubuntu, Debian, Fedora, Arch)
✅ Windows 10/11 (WSL2 & native)

Terminal Emulators:
✅ 16+ tested (xterm, iTerm2, Windows Terminal, etc.)
```

---

## 📖 Documentation

### 🚀 Getting Started
- [**Quick Start Guide**](wiki/Quick-Start.md) - Get running in 5 minutes
- [Installation](wiki/Quick-Start.md#installation) - Setup instructions
- [Command Reference](wiki/Command-Reference.md) - Complete command list (60+ commands)

### 📊 Testing & Performance
- [**v1.0.26 Plan**](docs/planning/v1.0.26-PLAN.md) - Current development plan
- [**macOS Test Results**](docs/planning/PHASE3-MACOS-RESULTS.md) - Platform verification
- [Performance Benchmarks](memory/tests/performance_v1_0_26.py) - Automated performance tests

### 📚 Development
- [**ROADMAP.MD**](ROADMAP.MD) - **Complete v1.0.x-v1.1.0 development plan**
- [Contributing Guide](CONTRIBUTING.MD) - Development workflow
- [Testing Guide](dev/docs/guides/TESTING.md) - Testing procedures
- [Development Setup](dev/docs/guides/DEVELOPMENT.md) - Dev environment

### 🗺️ v1.0.x Development Path to Stable Release

| Version | Status | Focus | Timeline |
|---------|--------|-------|----------|
| v1.0.0-v1.0.16 | ✅ Complete | Foundation, uCODE, Theme System | Nov 2025 |
| v1.0.17 | ✅ Complete | Interactive Debugger (94 tests) | Nov 15, 2025 |
| v1.0.16c | 📋 Next | Dual-Mode, Project Templates | Dec 2025 |
| v1.0.18 | 📋 Planned | Adventures, XP System | Jan 2026 |
| v1.0.19 | 📋 Planned | Workflow, Barter Economy | Feb 2026 |
| v1.0.20-21 | 📋 Planned | Knowledge Bank, Survival Guides | Mar 2026 |
| v1.0.22 | 📋 Planned | 1000+ Page Documentation | Apr 2026 |
| v1.0.23 | 📋 Planned | Final Polish, 1000+ Tests | May 2026 |
| **v1.1.0** | 🎯 Goal | **STABLE RELEASE** | **Jul 2026** |

**Post-Stable (v1.1.x)**: Device spawning, P2P mesh, advanced features

**See [ROADMAP.MD](ROADMAP.MD) for detailed breakdown of each version.**
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
├── core/                  # Core Python modules (commands, services, utils)
├── data/                  # System configuration (USER.UDT, themes, templates)
├── docs/                  # Development documentation (gitignored)
│   ├── development/      # Session summaries, dev round notes
│   ├── guides/           # Development guides
│   ├── planning/         # Project planning documents
│   └── references/       # Dev references (colors, screen sizes)
├── extensions/            # Extension system
│   ├── bundled/          # Built-in extensions (web interfaces)
│   ├── cloned/           # External dependencies (gitignored)
│   ├── templates/        # Extension scaffolding (CLI & web)
│   ├── fonts/            # Font assets with licenses
│   └── setup/            # Installation scripts
├── knowledge/             # Knowledge base system (tracked)
│   ├── demos/            # Example scripts & interactive demos
│   ├── survival/         # Survival guides
│   ├── skills/           # Skill documentation
│   ├── system/           # System knowledge files
│   └── [categories]/     # Water, food, medical, tech, etc.
├── memory/                # Runtime data & testing
│   ├── tests/            # Test suite (pytest)
│   ├── scripts/          # Maintainer scripts
│   ├── missions/         # Mission definitions
│   └── [runtime]/        # Config, logs, modules, scenarios
├── wiki/                  # GitHub wiki source (tracked)
├── sandbox/               # Working directory (gitignored)
├── scripts/               # Utility scripts (config management)
├── uDOS.py                # Entry point
├── start_udos.sh          # Launch script
└── README.MD              # This file
```

### Core System (`/core`)

Modular Python architecture with clean separation:

```
core/
├── commands/              # Specialized command handlers
│   ├── assist_handler.py
│   ├── file_handler.py
│   ├── knowledge_handler.py
│   ├── map_handler.py
│   ├── private_handler.py
│   ├── scenario_play_handler.py
│   ├── system_handler.py
│   └── tile_handler.py
├── services/              # Core services & utilities
│   ├── knowledge_service.py
│   ├── map_data_manager.py
│   ├── option_selector.py
│   ├── server_manager.py
│   └── viewport_manager.py
├── utils/                 # Shared utilities
│   ├── teletext_mosaic_renderer.py
│   └── tile_utils.py
├── uDOS_commands.py      # Main command dispatcher
├── uDOS_env.py           # Environment configuration
├── uDOS_files.py         # File operations
├── uDOS_gemini.py        # AI integration
├── uDOS_graphics.py      # PANEL system (v1.0.21)
├── uDOS_grid.py          # Grid/panel management
├── uDOS_interactive.py   # Interactive mode
├── uDOS_logger.py        # Logging system
├── uDOS_main.py          # Main application loop
├── uDOS_offline.py       # Offline mode
├── uDOS_parser.py        # CLI to uCODE parser
├── uDOS_prompt.py        # Dynamic prompt
├── uDOS_server.py        # Web server management
├── uDOS_settings.py      # Configuration
├── uDOS_splash.py        # Splash screen
├── uDOS_startup.py       # Startup sequence
├── uDOS_tree.py          # Directory tree generation
├── uDOS_ucode.py         # uCODE interpreter
└── __init__.py           # Package initialization
```

### Key Directories

**`/core`** - Core system (tracked)
- Command handlers, services, utilities
- Main application loop and interpreter
- Graphics, grid, and file systems

**`/data`** - User configuration (tracked)
- `USER.UDT` - User profile and settings
- `system/` → Symbolic link to `/knowledge/system/`
- `themes/` - Theme configurations
- `templates/` - Command templates

**`/docs`** - Development documentation (gitignored)
- Session summaries and dev round notes
- Planning documents and roadmaps
- Development guides and references
- Color palettes, screen size specs

**`/extensions`** - Extension system (mixed tracking)
- `bundled/web/` - Built-in web extensions (tracked)
  - `dashboard/`, `font-editor/`, `shared/`, `system-desktop/`, `system-style/`, `teletext/`
- `cloned/` - External dependencies (gitignored)
  - `c64css3/`, `classicy-desktop/`, `micro/`, `nes-style/`
- `core/` - Shared extension components (tracked)
  - `assets/`, `css/`, `js/`, `themes/`, `docs/`
- `templates/` - Extension scaffolding (tracked)
  - `cli-extension-template/`, `web-extension-template/`
- `fonts/` - Licensed font assets (tracked)
  - Chicago, Mallard family, sysfont
- `setup/` - Installation scripts (tracked)

**`/knowledge`** - Knowledge base (tracked)
- `demos/` - Example scripts (`.uscript`), interactive demos, asset bundles
- `system/` - Core system knowledge files
  - `geography/`, `graphics/`, `help_templates/`, `reference/`, `templates/`, `themes/`
- `community/` - Collaboration, conflict resolution, local resilience, mutual aid
- `food/` - Food production and preservation
- `making/` - Crafting and building
- `medical/` - Health and first aid
- `reference/` - General reference materials
- `skills/` - Art, music, writing
- `survival/` - Emergency preparedness
- `tech/` - Technology guides
- `water/` - Water sourcing and purification
- `well-being/` - Mental health, mindfulness, physical health, relationships
- 500+ curated survival and reference documents

**`/memory`** - Runtime & testing (tracked)
- `tests/` - Complete pytest test suite
  - `e2e/`, `integration/`, `scripts/`, `test_files/`, `unit/`
- `config/` - Runtime configuration
- `logs/` - System logs (`servers/`, `sessions/`)
- `modules/stdlib/` - Standard library modules
- `missions/` - Mission definitions
- `scenarios/` - Scenario files
- `themes/` - Custom themes
- `workflow/` - Workflow management (`active/`, `archived/`, `completed/`)
- `workspace/` - User workspace (`drafts/`, `experiments/`, `tools/`)
- `personal/`, `private/`, `shared/`, `groups/`, `public/` - 4-tier knowledge storage
- `legacy/` - Legacy data (`learnings/`, `outcomes/`, `resources/`)

**`/wiki`** - GitHub wiki source (tracked)
- Complete user-facing documentation
- Command references (PANEL, KNOWLEDGE, TILE)
- Getting started guides and tutorials
- Architecture and design documentation

**`/sandbox`** - Working directory (gitignored)
- Temporary files and experiments
- Not distributed with releases

Run `TREE` command in uDOS to generate/update `structure.txt` with complete repository structure.

---

## Learning Objectives

This project demonstrates:
- **Modular Architecture** - Separation of concerns (parsing, execution, UI)
- **Data-Driven Design** - Commands and terminology in JSON
- **Hybrid Systems** - Human-readable layer over structured backend
- **API Integration** - Gemini OK Assisted Task integration patterns
- **Testing Strategies** - Automated script-based testing
- **Development Tooling** - VS Code workspace configuration

---

## Current Status

**Version 1.3.0** - Production-ready with OK Assisted Task integration and intelligent startup:
- ✅ Enhanced startup system with auto-repair
- ✅ Gemini OK Assisted Task integration (ASK, ANALYZE, DEBUG commands)
- ✅ Configuration management with secure .env handling
- ✅ File operations with UNDO/REDO
- ✅ GitHub-style web dashboard
- ✅ Four web extensions (dashboard, markdown-viewer, font-editor, typo, cmd)
- ✅ Offline capabilities with pattern-matching OK Assisted Task
- ✅ Professional command reference and documentation

**Latest Release (October 2025)**:
- v1.3.0: Enhanced startup, Gemini OK Assisted Task, configuration management
- Complete health diagnostics with auto-repair
- OK Assisted Task-assisted error debugging
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

