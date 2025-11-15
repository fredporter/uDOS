# uDOS v1.0.17 - Interactive Debugger Complete

**uDOS** is a modular CLI framework with assistant integration, comprehensive diagnostics, and modern web extensions. Built to demonstrate clean architecture, human-readable command systems, and intelligent workflows.

**Current Status**: ✅ v1.0.17 Complete - Interactive Debugger Shipped (Nov 15, 2025)
**Next**: v1.0.18 - Apocalypse Adventures & Experience System

---

## 🎯 v1.0.x Objective: Stable Release by July 2026

### Current Progress
- **17/24 versions complete (71%)**
- **Next milestone**: v1.0.18-v1.0.23 (6 versions remaining)
- **Timeline**: 8 months to v1.1.0 stable release
- **Focus**: Core features, offline capability, survival knowledge

### Advanced Features → v1.1.x (Post-Stable)
The following features have been moved to v1.1.x to focus on stable v1.0.x release:
- **Device Spawning**: Laptop-to-mobile synchronization
- **P2P Mesh Networking**: Decentralized communication
- **Multi-User Features**: Collaborative workflows
- **Advanced Security**: Encryption, secure sharing
- **Network Sharing**: Community knowledge exchange

### v1.0.x Core Deliverables
- ✅ **Complete uCODE language** (v1.0.14-v1.0.16) - Variables, functions, modules
- ✅ **Interactive debugger** (v1.0.17) - Full debugging suite with 94 tests
- 📋 **Offline-first operation** (v1.0.16c) - COMMAND/ASSIST dual modes
- 📋 **500+ survival guides** (v1.0.20-v1.0.21) - Complete offline knowledge base
- 📋 **1000+ page handbook** (v1.0.22) - Comprehensive documentation
- 📋 **Production polish** (v1.0.23) - Performance, testing, stability

---

## 🆕 What's New in v1.0.17 (Latest)

### Interactive Debugger - COMPLETE ✅
**94/94 tests passing | Full command suite | Production ready**

```bash
# Debug any uCODE script
DEBUG my_script.uscript

# Set breakpoints (regular or conditional)
BREAK 10                    # Regular breakpoint
BREAK 20 IF counter > 50    # Conditional breakpoint

# Step through execution
STEP                        # Step over
STEP INTO                   # Step into function
STEP OUT                    # Step out of function
CONTINUE                    # Continue to next breakpoint

# Inspect variables
INSPECT x                   # Check variable value
INSPECT ALL                 # Show all variables
WATCH counter               # Watch variable changes

# Modify during debugging
MODIFY x = 100             # Change variable value mid-execution

# Performance profiling
PROFILE AUTO ON            # Enable automatic profiling
PROFILE                    # View execution times
PROFILE TOP 10             # See slowest lines

# Variable history
HISTORY x                  # See all changes to variable
HISTORY counter 5          # Last 5 changes

# Call stack
STACK                      # View current call stack
```

**Features:**
- ✅ Breakpoints (set, clear, list, disable/enable)
- ✅ Conditional breakpoints (`IF` conditions)
- ✅ Step execution (over, into, out)
- ✅ Variable inspection and modification
- ✅ Watch expressions
- ✅ Performance profiling
- ✅ Variable history tracking
- ✅ Call stack display
- ✅ 94/94 comprehensive tests

**Documentation**: See `docs/development/v1.0.17-COMPLETE.md`

---

## 📖 Documentation

### 🚀 Getting Started
- [**Quick Start Guide**](wiki/Quick-Start.md) - Get running in 5 minutes
- [Installation](wiki/Quick-Start.md#installation) - Setup instructions
- [Command Reference](wiki/Command-Reference.md) - Complete command list

### 📚 Development
- [**ROADMAP.MD**](ROADMAP.MD) - **Complete v1.0.x-v1.1.0 development plan**
- [Contributing Guide](dev/docs/guides/CONTRIBUTING.md) - Development workflow
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
- `PROMPTS.UDO` - Offline OK Assisted Task prompts
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

