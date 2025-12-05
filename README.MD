# uDOS v1.2.3 - Knowledge & Map Layer Expansion

**uDOS** is an offline-first knowledge system for survival, self-sufficiency, and sustainable living. Built with a text-first philosophy, community-driven development, and a focus on practical skills over corporate control.

**Current Status**: ✅ **v1.2.3 Stable** (December 5, 2025)
**Latest Update**: Multi-layer map system + spatial data structures (Earth, solar system, galaxy)
**uPY Syntax**: ✨ **v2.0.2** - Three-format system (short/medium/long) for conditionals and functions
**Test Coverage**: **14/14 integration tests passing** (v1.2.3 features, 100% success rate)
**Knowledge Bank**: **230 comprehensive survival guides** across 8 categories
**Map System**: **4-layer TILE grid** (surface, cloud, satellite, underground)
**Spatial Data**: **Earth locations, solar system, Milky Way navigation**
**Architecture**: **Multi-dimensional mapping** with GeoJSON visualization
**Community**: Production ready with GitHub templates, discussions, and marketplace

---

## ✨ uPY v2.0.2 - Three-Format Syntax System (December 5, 2025)

**Major Language Update:** uPY now supports three formats for conditionals and functions - choose based on complexity!

### Syntax Highlights

**Three Bracket Types:**
- `{$variable}` - All variables (assignment, interpolation, system)
- `(command|params)` - Commands and functions
- `[condition]` - Short-form conditionals

**Three Complexity Levels:**

```upy
# SHORT FORM (1-2 actions)
[IF {$hp} < 30: HP (+20) | PRINT ('Healed!')]
@greet({$name}): PRINT ('Hello {$name}!')

# MEDIUM FORM (inline branching)
[IF {$gold} >= 100 THEN: ITEM (sword) ELSE: PRINT ('Need gold')]
[{$hp} < 30 ? HP (+20) : PRINT ('OK')]  # Ternary

# LONG FORM (complex logic, no indents required)
IF {$hp} < 30
  HP (+50)
  PRINT ('Emergency!')
  FLAG (critical)
ELSE IF {$hp} < 60
  HP (+20)
ELSE
  PRINT ('Healthy')
END IF

FUNCTION battle_check({$level})
  ROLL (1d20) → {$roll}
  IF {$roll} >= 15
    XP (+50)
    RETURN true
  ELSE
    RETURN false
  END IF
END FUNCTION
```

**Key Features:**
- ✅ Progressive complexity (beginner → advanced)
- ✅ No indentation required (line-by-line)
- ✅ Human-readable keywords (THEN, ELSE, END IF)
- ✅ Multiple delimiters (`:` `|` `?` `→`)
- ✅ Python-like function syntax

**Documentation:**
- [uCODE-Language.md](wiki/uCODE-Language.md) - Complete spec
- [uPY-Syntax-v2.0.1.md](wiki/uPY-Syntax-v2.0.1.md) - Full reference
- [uPY-Syntax-Rules.md](wiki/uPY-Syntax-Rules.md) - Quick card

---

## 🚀 v1.2.3 - Knowledge & Map Layer Expansion (December 4, 2025)

**Latest Release:** v1.2.3 introduces multi-layer mapping system with spatial data structures for comprehensive location awareness and celestial navigation.

### What's New in v1.2.3

🗺️ **4-Layer Map System** (500 lines)
- **Surface Layer (100)**: Elevation (-11km to 8.8km), 8 terrain types, 9 biomes
- **Cloud Layer (600)**: Weather systems, precipitation, atmospheric conditions
- **Satellite Layer (700)**: GPS coverage, orbital mechanics, communications
- **Underground Layer (50)**: Geology, caves, aquifers, bunkers, tunnels
- **Integration**: Ready for map engine layer switching (v1.2.4 MAP commands)

🌍 **Spatial Data Structures** (720 lines)
- **Locations**: 4 major cities with TILE codes and survival resources
  - Sydney (AA340-100), London (JF57-100), Tokyo (LB110-100), NYC (QD95-100)
  - Survival landmarks: Great Barrier Reef, Amazon, Sahara
- **Planets**: Solar system with orbital mechanics and colonization data
  - Mars survival rating 3/10 (water ice, thin atmosphere, colonization potential)
- **Galaxies**: Milky Way structure, navigation stars, celestial orientation
  - 5 key stars: Sirius, Polaris, Betelgeuse, Rigel, Vega
  - 7 constellations for emergency navigation

📍 **GeoJSON Visualization** (130 lines)
- Sample TILE grid export (5 tiles: Sydney, London, Tokyo, NYC, Pacific)
- GitHub Maps compatible format
- Foundation for full 129,600-cell export (v1.2.4)
- Compatible with geojson.io and Mapshaper

✅ **Integration Testing**
- 14 comprehensive tests (100% passing, 0.05s execution)
- Map layer structure validation
- Spatial data integrity checks
- GeoJSON format compliance
- Map engine compatibility confirmed

---

## 🎯 Previous Major Releases

### v1.2.2 - DEV MODE Debugging System (December 3, 2025)

**Latest Release:** v1.1.12 completes the migration to .upy format with COMMAND(args) syntax. All backward compatibility removed, migration tools included.

### What's New in v1.1.12

🔄 **uPY Migration Complete**
- **.upy Format Only**: Old .uscript format completely removed
  - Use `COMMAND(args)` syntax instead of `[MODULE|COMMAND*ARGS]`
  - Migration tool: `python bin/migrate_upy.py old.uscript new.upy`
  - All 64 tests passing (command registry, preprocessor, parser)

- **Backward Compatibility Removed**
  - Deprecated interpreters archived (3,167 lines)
  - Old format files archived (13 files, ~5,500 lines)
  - Clean v1.1.12 codebase (no legacy code)

- **New Architecture**
  - UPYParser with COMMAND(args) syntax
  - UPYPreprocessor for Python 3 validation
  - Command registry for discovery
  - Shell integration (bin/udos, bin/uenv.sh)

📝 **Migration Tools & Examples**
- `bin/migrate_upy.py` - Automated conversion tool
- 3 new example files:
  - `hello-world.upy` - Simple introduction
  - `rpg-combat.upy` - Combat mechanics demo
  - `shakedown.upy` - System validation

✅ **Production Ready**
- All tests passing (64/64, 0.05s)
- Clean codebase (no deprecated code)
- Migration documentation complete
- Breaking change: .uscript support removed

---

## 🎯 Previous Major Releases

### v1.1.7 - Nano Banana PNG→SVG Pipeline (December 1, 2025)

🎨 **Nano Banana System Complete (8/8 Tasks)**
- **PNG→SVG Pipeline**: Full diagram generation powered by Gemini 2.5 Flash Image
  - Generate vector diagrams with `GENERATE SVG <description>`
  - 3 visual styles: technical-kinetic, hand-illustrative, hybrid
  - 4 diagram types: flowchart, architecture, kinetic-flow, schematic
  - Standard mode: 15-20s average | Pro mode: 30-45s average

- **4 Production Workflow Examples** (`sandbox/workflow/examples/`)
  - `nano_banana_quick_start.uscript` - Beginner tutorial (60 lines)
  - `nano_banana_batch.uscript` - Batch generation with tracking (80 lines)
  - `nano_banana_quality_check.uscript` - Validation + retry logic (90 lines)
  - `nano_banana_styles_demo.uscript` - All style/type combinations (70 lines)

- **Testing Framework**
  - Smoke tests: 5/6 passing (0.03s runtime)
  - Integration tests: Full coverage (documented for v1.1.8 refactor)
  - Live API tests: Ready for manual execution

📚 **Comprehensive Documentation**
- **Tutorial: Nano Banana Quick Start** - 15-20 minute beginner guide
- **Command Reference** - Complete GENERATE SVG documentation
- **Nano Banana Integration Guide** - Workflow examples and best practices
- **Wiki Navigation** - Updated with v1.1.7 content

✅ **Complete Development Cycle**
- 6 hours development time (4h workflows/tests, 2h docs)
- 15 files created, 3,356 lines written
- 6 commits, 1 release tag
- Production ready and fully documented

---

## 🎯 Previous Major Releases

### v1.1.6 - Production Logging & Configuration (November 28, 2025)

📊 **Production Logging System**
- **Flat-File Architecture**: Simple, reliable logging without database overhead
  - Daily log rotation with configurable retention
  - Structured JSON logging for easy parsing
  - Multiple log levels (DEBUG, INFO, WARNING, ERROR)
  - Search utilities and statistics

- **LoggingManager Service** (`core/services/logging_manager.py`, 432 lines)
  - Centralized logging configuration
  - Category-based log organization
  - Context injection for rich metadata
  - Backward-compatible with existing code

- **SessionLogger** (`core/services/session_logger.py`, 166 lines)
  - Session-aware logging for game/scenario tracking
  - Move tracking and statistics
  - Newline sanitization for clean logs

🔧 **Configuration System Improvements**
- **Single Source of Truth**: Eliminated variable duplication
  - Username now lives ONLY in `user.json` (not `.env`)
  - Clear separation: `.env` = system config, `user.json` = user data
  - No sync issues, no confusion

- **System Variables Documentation** (`core/docs/SYSTEM-VARIABLES.md`)
  - Canonical variable reference
  - NO DUPLICATION principle established
  - Migration guide from older versions
  - Code examples and best practices

✅ **Complete Test Coverage**
- 34/34 logging tests passing (100%)
- 28/32 integration tests passing (87.5%)
- Test suite: 21 LoggingManager + 13 SessionLogger

---

## 🎯 Previous Major Releases

### v1.1.5 - SVG Graphics Extension (November 28, 2025)
- AI-powered vector diagram generation
- 4 artistic styles (lineart, blueprint, sketch, isometric)
- Natural language → scalable SVG diagrams
- Gemini API integration with offline fallback

### v1.1.1 - Modern Syntax Update (November 27, 2025)

**Latest Release:** v1.1.1 modernizes uCODE scripting with bracket notation, template strings, and one-line conditionals.

### What's New in v1.1.1

📝 **Modern uCODE Syntax**
- **PRINT Command**: New primary output with `${var}` template strings
  - `PRINT "Hello ${name}"` - Template substitution
  - `PRINT[text]` - Three equivalent bracket formats
  - Replaces verbose ECHO syntax

- **Bracket Notation**: Clean, consistent syntax
  - `SET[var = value]` - Assignment with brackets
  - `GET[var]` - Retrieval with brackets
  - Context-sensitive normalization

- **One-Line IF**: Curly braces for conditions
  - `IF{x > 5} THEN PRINT[Value is large]`
  - `IF{status == "ready"} THEN SET[active=true]`
  - Complex operators: `>`, `<`, `==`, `!=`, `AND`, `OR`, `NOT`

📚 **Enhanced Documentation**
- New **uCODE Syntax Quick Reference** (300+ lines)
- Syntax comparison tables (old vs new)
- Migration guide from v1.0.x
- Updated inline code comments throughout

✅ **Complete Test Coverage**
- 35/35 tests passing (100%)
- Bracket syntax: 11/11 ✅
- SET/GET brackets: 14/14 ✅
- One-line IF: 10/10 ✅

---

## 🚀 v1.0.0 - First Stable Public Release

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
- **Memory**: Unified workspace structure (workflows, system, bank, shared)
- **Logs**: Consolidated in memory/workflows/logs/
- **User Data**: Consolidated in memory/system/user/ (databases, configs, planets)
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
✅ All workflows: Unified in memory/workflows/ (missions, checklists, sessions, logs)
✅ User data: Consolidated in memory/system/user/

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
