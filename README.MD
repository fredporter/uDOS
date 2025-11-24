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
- SVG diagram generation with citations
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
- [**Quick Start Guide**](QUICK_START.md) - Get running in 5 minutes
- [**Installation Guide**](INSTALL.md) - Setup instructions
- [**Command Reference**](wiki/Command-Reference.md) - Complete command list

### 📊 Release Information
- [**Release v1.1.2**](wiki/Release-v1.1.2.md) - Full release notes
- [**Latest Development**](wiki/Latest-Development.md) - Recent milestones
- [**ROADMAP**](ROADMAP.MD) - Complete development plan
- [**CHANGELOG**](CHANGELOG.md) - Detailed version history

### 📚 Architecture & Development
- [**Architecture Overview**](wiki/Architecture.md) - System design
- [**Contributing Guide**](CONTRIBUTING.md) - Development workflow
- [**Credits & Licenses**](CREDITS.md) - Attributions and dependencies

---

## 🏗️ System Architecture

### Core Components

```
uDOS/
├── core/                  # Core system (Python)
│   ├── commands/         # Command handlers (60+ commands)
│   ├── services/         # Core services (security, AI, analytics)
│   ├── input/            # Input handling and prompts
│   ├── output/           # Output formatting and rendering
│   ├── knowledge/        # Knowledge management
│   ├── network/          # Networking and API services
│   ├── ui/               # UI components (selectors, prompts)
│   ├── theme/            # Theme system
│   ├── utils/            # Utility functions
│   └── interpreters/     # uCODE interpreter
│
├── extensions/           # Extension system
│   ├── core/             # Core extensions (terminal, teletext, web GUI)
│   ├── game-mode/        # Game mode commands and services
│   ├── setup/            # Installation scripts
│   └── templates/        # Extension scaffolding
│
├── knowledge/            # Knowledge library (8 categories)
│   ├── system/           # System documentation
│   ├── survival/         # Survival guides (28 files)
│   ├── medical/          # First aid (4 files)
│   ├── food/             # Foraging & preservation (5 files)
│   ├── water/            # Water sourcing & purification (6 files)
│   ├── making/           # Building & energy (2 files)
│   ├── tech/             # Technical skills (5 files)
│   └── reference/        # Maps & reference data
│
├── memory/               # User workspace (gitignored except templates)
│   ├── config/           # User configuration
│   ├── sandbox/          # Temporary work
│   ├── workflow/         # Active missions
│   ├── legacy/           # Archived outcomes
│   ├── personal/         # Personal content
│   ├── tests/            # Test suites (tracked)
│   └── [tiers]/          # 4-tier memory system
│
├── wiki/                 # Project wiki
└── dev/                  # Development workspace (mostly gitignored)
```

### Key Features

**Security & Access Control**
- Role-based access control (User/Power/Wizard/Root)
- 4-tier memory encryption (Private→Shared→Community→Public)
- Command-based security layer
- Installation integrity verification (CLONE/SPAWN/HYBRID)

**Dual Interface**
- Terminal UI with retro graphics (BBC Teletext)
- Web GUI with WebSocket streaming
- Browser extension for knowledge capture
- Mobile PWA with offline support

**Knowledge Management**
- 8-category offline library (74+ guides)
- AI prompt development and testing
- SVG diagram generation with citations
- Content validation and quality scoring

**Developer Tools**
- uCODE scripting language with debugger
- Session analytics and replay
- Intelligent error handling
- Comprehensive testing framework (1,062 tests)

---

## 🚀 Quick Start

### Installation

```bash
# Clone the repository
git clone https://github.com/fredporter/uDOS.git
cd uDOS

# Create virtual environment
python3 -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Run uDOS
./start_udos.sh  # On Windows: python uDOS.py
```

### First Run

```bash
# Interactive mode
./start_udos.sh

# Run a script
./start_udos.sh memory/tests/shakedown.uscript

# Show help
echo "HELP" | python uDOS.py
```

### Basic Commands

```
help              # Show all available commands
status            # System status
version           # Show version info

# Knowledge access
guide list        # List survival guides
learn search <topic>  # Search knowledge base
docs <command>    # Command documentation

# Memory system
memory tier       # Show 4-tier memory system
memory list       # List memory files
file edit <file>  # Edit file

# Web GUI (requires extension)
web start         # Start web server
web open          # Open in browser

# Security
config role       # Show current role
config install    # Installation type
```

---

## 🧪 Testing

### Run Tests

```bash
# All v1.1.x tests
pytest memory/tests/test_v1_1_*.py

# Specific milestone
pytest memory/tests/test_v1_1_0_*.py  # v1.1.0 (268 tests)
pytest memory/tests/test_v1_1_1_*.py  # v1.1.1 (327 tests)
pytest memory/tests/test_v1_1_2_*.py  # v1.1.2 (467 tests)

# With coverage
pytest memory/tests/ --cov=core --cov-report=html
```

### Test Results

```
Total: 1,062/1,062 passing (100%)

v1.1.0 - Core TUI:           268 tests ✅
v1.1.1 - Web Extension:      327 tests ✅
v1.1.2 - Security/Knowledge: 467 tests ✅
```

---

## 🗺️ Roadmap

### Completed Milestones

✅ **v1.1.0** - Core TUI Stabilisation (268 tests)
- AI assistant with role-based security
- Unified selector system (16+ terminals)
- Retro graphics and session analytics

✅ **v1.1.1** - Web Extension & Dual-Interface (327 tests)
- Production web server
- Browser extension
- Mobile PWA

✅ **v1.1.2** - Security & Offline Knowledge (467 tests)
- RBAC system
- 4-tier memory encryption
- Offline knowledge library
- AI prompt development

### Next Milestones

📋 **v1.1.3** - Adventure & Economy Systems (Q4 2026)
- Gamified survival progression
- Apocalypse adventure framework
- Zero-currency barter economy
- Community integration

📋 **v1.1.4+** - Advanced Features
- Tauri desktop app
- Device spawning
- P2P mesh networking
- Native mobile apps

[Full Roadmap →](ROADMAP.MD)

---

## 📝 License

See [LICENSE.txt](LICENSE.txt) for details.

**Copyright © 2025 uDOS Contributors**

---

## 🙏 Credits

- **Author**: Fred Porter
- **Contributors**: See [CREDITS.md](CREDITS.md)
- **Dependencies**: See [requirements.txt](requirements.txt)

---

## 📞 Support

- **Documentation**: [wiki/](wiki/)
- **Issues**: [GitHub Issues](https://github.com/fredporter/uDOS/issues)
- **Discussions**: [GitHub Discussions](https://github.com/fredporter/uDOS/discussions)

---

**Ready to get started? Check out the [Quick Start Guide](QUICK_START.md)!**
