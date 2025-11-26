# uDOS v1.0.0 - First Stable Public Release

**uDOS** is an offline-first knowledge system for survival, self-sufficiency, and sustainable living. Built with a text-first philosophy, community-driven development, and a focus on practical skills over corporate control.

**Current Status**: ✅ **v1.0.0 Stable** (November 2025)
**Test Coverage**: **1,810 tests passing** (100%)
**Knowledge Bank**: **166+ comprehensive survival guides** across 8 categories
**Documentation**: **62 wiki pages** (20,000+ lines, 100% coverage)
**Architecture**: **5-Tier Knowledge System** with private sandbox workspace
**Community**: Production ready with GitHub templates, discussions, and marketplace

---

## 🚀 v1.0.0 - First Stable Public Release!

**Latest Release:** v1.0.0 is the first production-ready stable release with clean sandbox architecture, 5-tier knowledge system, comprehensive testing, and community-ready infrastructure.

### What's in v1.0.0

📁 **Sandbox Workspace** - Clean private development environment
- Centralized `/sandbox` directory for all user work
- 10 organized subdirectories: trash, dev, docs, drafts, tests, logs, scripts, ucode, workflow, peek
- Flat file structure where practical (no deep nesting)
- All logs consolidated in `sandbox/logs/` (moved from `memory/logs/`)
- File processing inbox in `sandbox/peek/`
- User data moved to `sandbox/` (from `memory/sandbox/`)

🏛️ **5-Tier Knowledge System** - Refined data architecture
- **PRIVATE** (`/sandbox`) - Personal workspace, user-only access
- **SHARED** (`/memory/shared`) - Direct peer-to-peer sharing
- **GROUPS** (`/memory/groups`) - Team collaboration
- **COMMUNITY** (`/memory/community`) - Public user content (renamed from `public/`)
- **KNOWLEDGE** (`/knowledge`) - Curated system knowledge (read-only)

🧹 **Maintenance Commands** - Automated cleanup and organization
- **CLEAN** - Flush old logs, empty trash, archive drafts
- **TIDY** - Organize and categorize sandbox files
- Interactive prompts with `--all` flag for automation
- Configurable retention (default 30 days)
- Statistics and reporting

### Previous Releases

#### v1.5.0 - Infrastructure Complete!

🔧 **DEV MODE** - Secure development environment (master user only)
- Password-based authentication (SHA256)
- Permission system (10 dangerous commands protected)
- Session management (auto-save, 1-hour timeout)
- Activity logging (text + JSON audit trail)
- 29 comprehensive tests

⚙️ **Configuration Sync** - Unified .env ↔ user.json management
- Bidirectional synchronization with priority system
- Auto-migration and backup/restore
- 21 configuration fields with schema validation
- 26 comprehensive tests

🎨 **Asset Management** - Shared resources for extensions
- Auto-discovery from extensions/assets/
- Type-specific loaders (font, icon, pattern, CSS, JS)
- Smart caching with hot-reload
- Search and filtering (regex support)
- 22 patterns library (borders, backgrounds, textures)
- 656 assets cataloged
- 22 comprehensive tests

🏗️ **Architecture Cleanup** - Cleaner, flatter structure
- **Core**: Flattened from 17 to 11 directories (TUI only, read-only)
- **Extensions/Core**: Removed duplicates, centralized assets library
- **Memory**: Flattened from 28 to 16 directories (43% reduction)
- **Logs**: All logs in flat memory/logs/ (no subdirectories)
- **User Data**: Consolidated in memory/user/ (databases, configs, planets)
- **Planet System**: Workspace renamed to Planet, linked to universe.json

🌍 **Planet System** - Workspace metaphor
- Renamed "workspace" to "planet" (Earth, Mars, etc.)
- Links to knowledge/system/universe.json (Sol system data)
- Each planet has isolated workspace path
- Current planet in .env + planets.json sync

### Knowledge & Documentation

📚 **Knowledge Infrastructure**
- **166+ comprehensive survival guides** (water, fire, shelter, food, navigation, medical, tools, communication)
- **9 quick reference materials** (charts, field guides, seasonal calendars)
- **68+ multi-format diagrams** (ASCII, Teletext, SVG)
- **Mac OS System 1 aesthetic** with consistent design standards

🖥️ **Dual Interface**
- Terminal CLI with retro Teletext graphics
- Web GUI with responsive design
- Seamless switching between interfaces
- Works completely offline

📝 **uCODE Scripting**
- Human-readable bracket syntax
- Markdown-compatible (.uscript files)
- Variables, conditionals, loops, error handling
- Comprehensive specification

📖 **Complete Documentation**
- **62 wiki pages** (20,000+ lines total)
- Getting Started tutorials with ASCII diagrams
- API reference for developers
- Troubleshooting guide
- Extension marketplace structure

🤝 **Community Ready**
- GitHub issue templates (4 types)
- Discussion templates (Ideas, Show & Tell, Q&A)
- Code of Conduct and contribution guidelines
- Community onboarding guide
- Extension marketplace infrastructure

### Beta Testing

**What We Need:**
- Install and test on your OS (macOS/Linux/Windows)
- Explore survival guides and knowledge features
- Report bugs or confusing parts
- Suggest improvements
- Optional: Contribute guides or extensions

**Timeline:** 8-12 weeks (Q1 2026)
**Commitment:** Flexible - as much or little as you want
**Requirements:** Python 3.9+, terminal familiarity helpful

👉 **[Join the Beta](https://github.com/fredporter/uDOS/discussions)** | **[Read Roadmap](ROADMAP.MD)**

---

## 🎯 What's Included

### 📚 Offline Knowledge System

**166+ Survival Guides:**
- 🌊 **Water** (26 guides) - Procurement, purification, storage
- 🔥 **Fire** (20 guides) - Starting methods, maintenance, safety
- 🏠 **Shelter** (20 guides) - Building, insulation, weatherproofing
- 🍎 **Food** (23 guides) - Foraging, preservation, cooking
- 🧭 **Navigation** (20 guides) - Methods, signaling, rescue
- ⚕️ **Medical** (27 guides) - First aid, emergency care, wellness
- 🔧 **Tools** (15 guides) - Equipment, maintenance, improvisation
- 📡 **Communication** (15 guides) - Signaling, community, security

**Quick Reference Library:**
- Survival priorities chart (Rule of 3s, STOP protocol)
- Edible plants guide (regional focus)
- Navigation techniques field guide
- First aid quick reference
- Essential knots guide
- Fire starting methods comparison
- Water purification methods comparison
- Seasonal calendar

### 🎨 Multi-Format Diagrams

**Three Output Formats:**
- **ASCII Art** - Terminal display with box-drawing characters
- **Teletext Graphics** - Retro BBC Micro aesthetic for web
- **SVG Diagrams** - Modern scalable graphics (Technical-Kinetic style)

**Design Standards:**
- Mac OS System 1 (1984) aesthetic
- Monochrome palette: Black, white, 9 grays
- 17 bitmap patterns (grayscale + texture)
- 8 UI components (buttons, windows, dialogs)
- Consistent across all formats

### 📝 uCODE Scripting v2.0

**Human-Readable Automation:**
```ucode
# Morning routine script
[SYSTEM|BLANK]
[SYSTEM|ECHO*Good morning! Starting daily routine...]

# Check priorities and weather
[KNOWLEDGE|SEASONAL*today]
[SYSTEM|STATUS]

# Review tasks
[MEMORY|RECALL*tasks]
```

**Features:**
- Markdown-compatible syntax
- Variables, conditionals, loops
- Error handling and debugging
- 650+ line specification
- Extensive examples

### 🖥️ Dual Interface

**Terminal CLI:**
- 60+ commands with intuitive syntax
- Retro Teletext graphics
- Works on 16+ terminal emulators
- Full offline capability

**Web GUI:**
- Modern responsive design
- Mac OS System 1 aesthetic
- Teletext display option
- Seamless CLI-to-web delegation

### 🛠️ Extension System

**Build & Share Extensions:**
- Custom commands and features
- Web applications and GUIs
- Knowledge domain expansions
- Theme customization
- Community marketplace ready

---

## 📊 Test Coverage

```
Total Tests: 1,810/1,810 passing (100%)
  - v1.3.0 base: 1,733 tests
  - v1.5.0 new:  77 tests (Config 26 + DEV MODE 29 + Assets 22)

Architecture Improvements:
✅ Core: 17 → 11 directories (35% reduction)
✅ Memory: 28 → 16 directories (43% reduction)
✅ Extensions/Core: Removed duplicates, centralized assets
✅ All logs: Flat memory/logs/ structure
✅ User data: Consolidated in memory/user/

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
- [**Quick Start**](QUICK-START.md) - Get running in 5 minutes
- [**Getting Started Tutorial**](wiki/Tutorial-Getting-Started.md) - Interactive learning
- [**Installation Guide**](INSTALL.md) - Detailed setup
- [**Community Onboarding**](wiki/Community-Onboarding.md) - Join the community

### 📚 User Guides
- [**Quick Reference**](wiki/Quick-Reference.md) - Essential commands
- [**Command Reference**](wiki/Command-Reference.md) - Complete command list
- [**uCODE Language**](wiki/uCODE-Language.md) - Scripting guide
- [**Troubleshooting**](wiki/Troubleshooting-Complete.md) - Fix common issues
- [**FAQ**](wiki/FAQ.md) - Frequently asked questions

### 🔧 Developer Resources
- [**API Reference**](wiki/API-Reference.md) - Developer API
- [**Architecture Guide**](wiki/Architecture-Contributor-Guide.md) - Codebase overview
- [**Extension Marketplace**](wiki/Extension-Marketplace.md) - Build & share extensions
- [**ASSETS Guide**](ASSETS-GUIDE.md) - Shared resources system
- [**DEV MODE Guide**](wiki/DEV-MODE-GUIDE.md) - Development environment
- [**Contributing**](CONTRIBUTING.md) - How to contribute

### 📊 Project Information
- [**ROADMAP**](ROADMAP.MD) - Development plan (v1.1.1 Content Generation)
- [**CHANGELOG**](CHANGELOG.md) - Version history
- [**Documentation Index**](wiki/Documentation-Index.md) - Complete docs map

---

## 🏗️ System Architecture

### Core Components

```
uDOS/
├── core/                  # Core system (Python)
│   ├── commands/         # Command handlers (60+ commands)
│   ├── services/         # Core services (AI, analytics, session mgmt)
│   ├── input/            # Input handling and prompts
│   ├── output/           # Output formatting and rendering
│   ├── knowledge/        # Knowledge management
│   ├── network/          # Networking and API services
│   ├── ui/               # UI components (selectors, prompts)
│   ├── theme/            # Theme system
│   ├── utils/            # Utility functions
│   ├── interpreters/     # uCODE interpreter
│   ├── tests/            # Test configuration
│   ├── scripts/          # Utility scripts
│   └── setup/            # Setup utilities
│
├── extensions/           # Extension system
│   ├── core/             # Core extensions (terminal, web GUI)
│   ├── web/              # Web interface
│   ├── templates/        # Extension scaffolding
│   └── community/        # Community extensions
│
├── knowledge/            # Knowledge library (166+ guides)
│   ├── water/            # Water (26 guides)
│   ├── fire/             # Fire (20 guides)
│   ├── shelter/          # Shelter (20 guides)
│   ├── food/             # Food (23 guides)
│   ├── navigation/       # Navigation (20 guides)
│   ├── medical/          # Medical (27 guides)
│   ├── tools/            # Tools (15 guides)
│   ├── communication/    # Communication (15 guides)
│   ├── reference/        # Quick reference materials (9 guides)
│   └── diagrams/         # Diagrams (68+ in ASCII/Teletext/SVG)
│
├── memory/               # User workspace (gitignored)
│   ├── user/             # User data files (USER.UDT, planets.json, *.db)
│   ├── planet/           # Planet workspaces (earth, mars, etc.)
│   ├── sandbox/          # Drafts & development
│   ├── workflow/         # uCODE scripts & missions
│   ├── logs/             # All system logs (flat structure)
│   ├── logs/             # System and session logs
│   ├── private/          # Tier 1: Encrypted (user-only)
│   ├── shared/           # Tier 2: Encrypted (team)
│   ├── groups/           # Tier 3: Community
│   └── public/           # Tier 4: Public knowledge
│
├── wiki/                 # Documentation (60 pages)
│
├── dev/                  # Developer resources
│   ├── planning/         # Roadmaps, beta materials
│   ├── docs/             # Generated documentation
│   └── tools/            # Development utilities
│
└── .github/              # Community infrastructure
    ├── ISSUE_TEMPLATE/   # Bug reports, features, extensions
    └── DISCUSSION_TEMPLATES/  # Ideas, Q&A, showcase
```

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

### First Commands

```
# Interactive mode
./start_udos.sh

# Basic commands
help              # Show all commands
status            # System status
knowledge         # Browse knowledge bank
guide             # Interactive tutorial

# Explore survival guides
knowledge water   # Water guides
READ knowledge/water/guides/solar-water-disinfection.md

# Try uCODE scripting
RUN memory/workflow/knowledge_generation.uscript
```

---

## 🌍 Project Philosophy

uDOS is built on six core principles:

🌍 **Offline-First** - Full functionality without internet
🤝 **Barter Over Currency** - Exchange knowledge, not wealth
🧠 **4-Tier Memory** - Personal → Shared → Group → Public
🎯 **Practical Over Political** - Real survival skills that matter
🎮 **Learn by Creating** - Education through game creation
👤 **Individual-User-Owned** - You control your data, not corporations

[Read More →](wiki/Philosophy.md)

---

## 🤝 Contributing

We welcome contributions from everyone! Here's how you can help:

**For Everyone:**
- 📚 Write survival guides using our templates
- 🐛 Report bugs or suggest features
- 💬 Help answer questions in Discussions
- ⭐ Star the repo to show support

**For Developers:**
- 🔧 Fix bugs or implement features
- 🎨 Build extensions
- 📖 Improve documentation
- ✅ Write tests

**For Beta Testers:**
- 🧪 Test v1.4.0 beta
- 📝 Complete feedback survey
- 💡 Share improvement ideas

**Get Started:**
- Read [Contributing Guide](CONTRIBUTING.md)
- Check [Good First Issues](https://github.com/fredporter/uDOS/labels/good%20first%20issue)
- Join [GitHub Discussions](https://github.com/fredporter/uDOS/discussions)
- Review [Code of Conduct](CODE_OF_CONDUCT.md)

---

## 📝 License

**MIT License** - See [LICENSE.txt](LICENSE.txt) for details.

uDOS is free and open source software. You're free to use, modify, and distribute it.

---

## 🙏 Credits

**Core Team:**
- Fred Porter (@fredporter) - Project Lead
- OK Assist (Gemini 2.5 Flash) - AI Content Generation
- Community Contributors - Beta testers, knowledge curators

**Technologies:**
- Python, pytest, click, rich - Core framework
- Mac OS System 1 - Design inspiration
- Teletext - Retro graphics format
- SVG - Modern vector graphics

[Full Credits →](CREDITS.md)

---

## 📞 Support & Community

**Get Help:**
- 📖 [Documentation](wiki/) - 31 comprehensive wiki pages
- 💬 [GitHub Discussions](https://github.com/fredporter/uDOS/discussions) - Q&A and community
- 🐛 [Issue Tracker](https://github.com/fredporter/uDOS/issues) - Report bugs
- 🎓 [Community Onboarding](wiki/Community-Onboarding.md) - Get started

**Stay Updated:**
- ⭐ Star the repo for updates
- 👀 Watch releases
- 💬 Join Discussions
- 📊 Follow [ROADMAP](ROADMAP.MD)

---

**🚀 Ready to dive in?**

1. [Install uDOS](INSTALL.md) - Get set up in 5 minutes
2. [Quick Start](QUICK-START.md) - Learn the basics
3. [Join Beta](https://github.com/fredporter/uDOS/discussions) - Help shape v1.4.0
4. [Browse Guides](knowledge/) - Explore survival knowledge

**Together, we're building the future of offline knowledge.** 🌍🤝
