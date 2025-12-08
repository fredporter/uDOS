# Welcome to uDOS Wiki

**uDOS v1.2.20** - Workflow Management System - Offline-first survival knowledge system with workflow automation, mission control, TUI panels, and comprehensive testing framework.

**Production Ready**: 148 SHAKEDOWN tests | Workflow System | TUI Panels | 230+ Knowledge Guides

> 🗺️ *"The Hitchhiker's Guide to the Galaxy on a small computer - A Survival Handbook for Armageddon"*

---

## 🚀 Quick Links

| Getting Started | Reference | Advanced |
|:----------------|:----------|:---------|
| [Quick Start](../QUICK-START.md) | [Command Reference](Command-Reference) | [uCODE Manual](uCODE-Language) |
| [Installation](../INSTALL.md) | [Architecture](Architecture) | [Extensions System](Extensions-System) |
| [Interactive Tutorial](Tutorial-Getting-Started) | [Developers Guide](Developers-Guide) | [Theme System](Theme-System) ⭐ |
| [FAQ](FAQ) | [Troubleshooting](Troubleshooting-Complete) | [Extension Development](Extension-Development) |
| [uPY Quick Start](Tutorial-uPY-Quick-Start) ⭐ NEW | [uPY Cheat Sheet](uPY-Cheat-Sheet) ⭐ NEW | [Before & After Guide](uPY-Before-After) ⭐ NEW |

---

## ✅ v1.1.9+ - uPY Python-like Syntax (January 2025)

**Modern Scripting**: Python-inspired syntax for advanced uCODE automation

**Features Complete** (26/26 tests passing):
- ✅ **Variables** - Clean `$VARIABLE = value` assignment syntax
- ✅ **Emoji Codes** - 80+ codes with `:emoji:` syntax (`:heart:` `:sword:` `:check:`)
- ✅ **Functions** - Reusable code blocks with `FUNCTION [@NAME($PARAMS) ... ]`
- ✅ **JSON Integration** - Load/save with dot notation (`player.stats.health = 100`)
- ✅ **Inline Conditionals** - One-line `IF {condition | statement}` syntax
- ✅ **PRINT Enhancement** - Variable substitution and emoji support

**New Wiki Pages**:
- [Tutorial: uPY Quick Start](Tutorial-uPY-Quick-Start) ⭐ NEW - 15-minute beginner tutorial
- [uPY Before & After](uPY-Before-After) ⭐ NEW - Visual syntax comparison
- [uPY Cheat Sheet](uPY-Cheat-Sheet) ⭐ NEW - Quick syntax reference
- [Emoji Reference](Emoji-Reference) - Complete emoji code catalog (80+ symbols)
- [Function Programming Guide](Function-Programming-Guide) - Tutorial with examples

**Total Documentation:** 10 wiki pages, ~4,000 lines

**Example Script**:
```upy
# Load player data
JSON.load("player.json")

# Define health check function
FUNCTION [@CHECK-HEALTH($HP, $MAX)
    $PERCENT = ($HP / $MAX) * 100
    IF {$PERCENT >= 75 | RETURN ':heart: healthy'}
    IF {$PERCENT >= 50 | RETURN ':warning: moderate'}
    RETURN ':skull: critical'
]

# Check and display status
$STATUS = @CHECK-HEALTH(player.stats.health, player.stats.max_health)
PRINT("Status: $STATUS")

# Award quest reward
player.inventory.gold = player.inventory.gold + 100
player.inventory.items.append("Magic Sword")
JSON.save("player.json")
PRINT(":check: Quest reward granted!")
```

[🔗 uPY Syntax Documentation →](uCODE-Language#upy-syntax-v119) | [🔗 Command Reference →](Command-Reference#upy-commands-v119)

---

## 📜 v1.0.0 - First Stable Public Release (November 2025)

**Historical milestone - see current features in v1.2.20 above**

**What was in v1.0.0:**

**Week 1 Complete**: 123% of target achieved! 🎉

- ✅ **123 OK Assist generated guides** (12.3% of 1,000 goal) - Exceeded 100-guide target
- ✅ **80 SVG diagrams** (16% of 500 goal)
- ✅ **OK Assistant 2.5 Flash integration** with smart fallback to placeholders
- ✅ **~30,000 words** of comprehensive survival content
- ✅ **8 categories expanded**: Water (20), Fire (15), Shelter (15), Food (22), Navigation (10), Medical (21), Tools (10), Communication (10)

**OK Assist Content Quality**:
- Average guide length: 1,500 words (target: 800-1200)
- Structure: Overview, materials, step-by-step instructions, safety, common mistakes, related topics
- Generation: 0% API cost (within OK Assistant free tier)

**Next**: Week 2 targets 273 total guides (150 more) + 50 additional diagrams

[🔗 Development History →](Development-History) | [🔗 ROADMAP →](../ROADMAP.md)

---

## 🎨 v1.0.30 - Enhanced CLI with Teletext UI (November 2025)

- **Teletext Block Character UI** - Retro-inspired selection boxes, file trees, autocomplete panels
- **Built-in Micro Editor** - Syntax-highlighted editor for .md and .uscript files (434 lines)
- **Knowledge File Picker** - Specialized picker for /knowledge and /memory content (343 lines)
- **Smart Prompt Fallback** - Terminal compatibility detection with graceful degradation
- **Startup Welcome** - v1.0.30 feature showcase with demo launcher
- **Error Handling** - Fixed critical bugs, improved exception handling throughout
- **Testing** - 19/19 tests passing (100%): integration, UI, and error handling
- **Production Ready** - All features tested and documented

[🔗 Extensions Server Guide →](Extensions-System) | [🔗 Dashboard Builder →](Dashboard-Features)

---

## 🗺️ v1.0.20b - Enhanced Mapping & Reference Data (November 2025)

- **250 World Cities** - Complete TIZO code system with coordinates
- **50 Countries** - ISO codes, capitals, demographics, languages
- **120 Timezones** - Full IANA database with DST rules
- **24 Terrain Types** - Elevation, traversability, rendering symbols
- **18 Climate Zones** - Köppen classification with temp/rainfall data
- **8 TILE Commands** - INFO, SEARCH, NEARBY, WEATHER, TIMEZONE, TERRAIN, ROUTE, CONVERT
- **Clean Data Architecture** - System data vs user memory separation

[🔗 Explore TILE System →](TILE-Commands) | [🔗 Mapping System →](Mapping-System)

---

## 🧠 v1.0.20 - 4-Tier Knowledge Bank (November 2025)

- **PRIVATE Tier** - AES-256 encrypted personal data
- **SHARED Tier** - Explicit permission-based sharing
- **COMMUNITY Tier** - Group collaboration with access control
- **PUBLIC Tier** - Open knowledge base with SQLite FTS
- **5 Command Handlers** - MEMORY, PRIVATE, SHARED, COMMUNITY, KB
- **Cross-Tier Operations** - MEMORY SEARCH across all tiers
- **Security Built-In** - Encryption, permissions, audit logging

[🔗 4-Tier Knowledge Guide →](Knowledge-System) | [🔗 User Guide →](/docs/guides/4-TIER-KNOWLEDGE-BANK-USER-GUIDE.md)

---

## 🎨 v1.0.13 - Theme System Enhancement

- **Interactive Theme Creator** - Step-by-step wizard for custom themes
- **4 Starter Templates** - Minimal, Dark Modern, Light Professional, High Contrast
- **Theme Preview** - See themes before switching
- **Import/Export** - Share themes with .udostheme format
- **Validation & Safety** - Auto-fix and comprehensive checks
- **10+ New Commands** - Complete theme management suite

[🔗 Explore Theme System →](Theme-System)

---

## 🎨 Extensions & Retro Computing (v1.0.10)

- **Bundled Web Extensions** - Native dashboard, System 7 desktop, teletext interface
- **Core Extensions** - C64 Terminal, Teletext, System Desktop, Dashboard, Character Editor, Markdown Viewer
- **Retro Font System** - Chicago, Mallard, PetMe (extensions/core/fonts/)
- **Synthwave DOS Colors** - Standard VGA 16-color palette with transparency variants
- **Typography System** - 15+ classic computing fonts with licensing compliance
- **Setup Scripts** - Automated installation for external dependencies
- **Legal Compliance** - Proper attribution and font licensing assessment
- **Clean Architecture** - Separation between bundled and cloned content

[🔗 Explore Extensions System →](Extensions-System) | [🔗 Development History →](Development-History)

---

## ⚡ CLI Terminal Features (v1.0.6)

- **Enhanced Command History** - SQLite persistence with intelligent search
- **Advanced Tab Completion** - Fuzzy matching with context-aware suggestions
- **Dynamic Color Themes** - Accessibility support with colorblind options
- **Real-time Progress Indicators** - Animated progress bars for long operations
- **Session Management** - Workspace state persistence and restore
- **Adaptive Layouts** - Responsive terminal formatting for all screen sizes

[🔗 Explore CLI Features →](CLI-Features-v1-0-6)

---

## 📖 What is uDOS?

uDOS is an **educational CLI framework** that demonstrates:

- **Human-Readable Commands**: Natural language-style syntax organized by category
- **Grid System**: Flexible workspace organization for data visualization
- **Spatial Navigation**: Intuitive movement through MAP, GOTO, and directional commands
- **File Operations**: Streamlined LIST, LOAD, SAVE, EDIT workflow
- **Assisted Task**: OK Assist integration with OK and READ commands
- **Connection Awareness**: Automatic online/offline mode detection
- **Viewport Detection**: Adapts to terminal size and device type
- **Session History**: UNDO, REDO, RESTORE capabilities
- **Script Automation**: Execute batch operations with RUN command
- **Web Extensions**: Interactive browser-based interfaces
- **System Diagnostics**: STATUS, REPAIR, VIEWPORT monitoring

---

## 🎯 Core Commands

### File Operations
```bash
LIST                  # List directory contents
LOAD <file>          # Load file into memory
SAVE <file>          # Save current content
EDIT <file>          # Edit file
```

### Grid Management
```bash
GRID                 # Show current grid
NEW GRID             # Create new grid
GRID LIST            # List all grids
SHOW GRID <name>     # Display specific grid
```

### Navigation
```bash
MAP                  # Display current map
GOTO <location>      # Jump to location
MOVE <direction>     # Move in direction
LEVEL                # Show current level
GODOWN               # Descend one level
GOUP                 # Ascend one level
```

### System
```bash
STATUS               # System status
VIEWPORT             # Display info
REPAIR               # Run diagnostics
REBOOT               # Restart system
PALETTE              # Show color palette
```

---

## 🆕 What's New in v1.0.6

### ⚡ CLI Terminal Features
- **Enhanced Command History**: SQLite persistence with intelligent fuzzy search
- **Advanced Tab Completion**: Context-aware suggestions with fuzzy matching
- **Dynamic Color Themes**: Classic, Cyberpunk, Accessibility, and Monochrome modes
- **Real-time Progress Indicators**: Animated progress bars for long operations
- **Session Management**: Save/restore workspace state with auto-save
- **Adaptive Layouts**: Responsive formatting for mobile and wide screens

### 🎨 Accessibility Enhancements
- **High Contrast Mode**: Enhanced visibility for low vision users
- **Colorblind Support**: Deuteranopia, protanopia, and tritanopia accommodations
- **Screen Reader Optimization**: Accessible formatting throughout
- **Mobile Terminal Support**: Compact layouts for small screens

### 🚀 Performance & UX
- **SQLite Integration**: Persistent command history survives restarts
- **Background Processing**: Non-blocking progress indicators
- **Smart Deduplication**: No repeated commands in history
- **Cross-platform Compatibility**: Universal terminal support

### � New CLI Commands
```bash
HISTORY LIST [count]        # Show recent commands with search
HISTORY SEARCH <term>       # Fuzzy search through command history
HISTORY STATS               # Usage analytics and insights
THEME SET <name>            # Switch themes dynamically
THEME ACCESSIBILITY ON      # Enable accessibility features
SESSION SAVE [name]         # Save current workspace state
SESSION LOAD <id>           # Restore previous session
PROGRESS TEST               # Demo progress indicators
LAYOUT MODE <mode>          # Set responsive layout mode
```

[🔗 Full CLI Features Documentation →](CLI-Features-v1-0-6)

### �🖥️ Teletext Web Extension (v1.0.4)
- **Mosaic Block Art**: 64 2×3 pixel character combinations
- **WST Color Palette**: Classic teletext colors (8 colors)
- **Interactive Web Interface**: http://localhost:8080
- **Mobile-Responsive Design**: Touch-optimized controls
- **Export Functionality**: Save maps as standalone HTML

### 🗺️ Enhanced Mapping System (v1.0.4)
- **Global Cell Grid**: 480×270 APAC-centered reference system
- **TIZO Location Codes**: 20 major cities worldwide (MEL, SYD, LON, NYC, etc.)
- **Real-time Navigation**: Distance and bearing calculations
- **ASCII Map Generation**: Visual maps with position markers
- **Multi-layer Access**: Connection quality and layer systems

---

## 📈 Development History (v1.0.1 - v1.0.6)

### 🧪 v1.0.1 - System Commands Foundation
**Complete infrastructure and command framework**
- **13 core SYSTEM commands** implemented with comprehensive testing
- **Enhanced HELP system** with interactive command search and categorization
- **DASHBOARD command** with CLI and WEB modes for system overview
- **REPAIR system** with 5 diagnostic modes and auto-fix capabilities
- **PALETTE command** with visual color tests and grayscale gradients
- **TREE command** for repository structure visualization
- **Comprehensive test suite** with 20+ test cases achieving 100% pass rate

**Key Achievements**: Modular command handler architecture, 800+ lines of implementation

### 📁 v1.0.2 - Configuration & Modular Foundation
**Complete system overhaul with configuration management**
- **User configuration refactoring** from USER.UDO to structured user.json + .env
- **TIZO location system** with 20 global cities and timezone integration
- **Extension system overhaul** with CLONE-only approach and auto-install
- **Theme standardization** with v1.0.2 schema across 6 themes
- **Character/Object system** with NetHack-style RPG mechanics
- **Modular command handlers** reducing main handler by 70% (1700→500 lines)

**Key Achievements**: 1200+ lines of new modular handlers, complete theme system

### 🗺️ v1.0.3 - Integrated Mapping System
**Complete navigation and spatial reference system**
- **Global cell grid system** with 480×270 APAC-centered reference
- **TIZO location integration** with 20 major cities worldwide
- **8 MAP commands** for navigation, cell reference, and route calculation
- **ASCII map generation** with position markers and visualization
- **IntegratedMapEngine** with 400+ lines of core mapping functionality
- **Cell reference conversion** using spreadsheet-style A1-RL270 notation
- **Navigation calculations** with Haversine distance and bearing algorithms

**Key Achievements**: Complete spatial navigation system, <100ms map rendering

### 🖥️ v1.0.4 - Teletext Web Extension
**Retro visualization with modern web interface**
- **Teletext mosaic renderer** with 64 2×3 pixel block art combinations
- **WST color palette** with authentic 8-color teletext styling
- **Web extension interface** with standalone HTTP server (localhost:8080)
- **Mobile-responsive design** with touch-optimized controls
- **Pattern generation algorithms** for dynamic water, terrain, and cities
- **MAP TELETEXT and MAP WEB commands** for seamless integration
- **Export functionality** for standalone HTML map files

**Key Achievements**: 450+ lines mosaic renderer, interactive web interface

### 🌐 v1.0.5 - Web Server Infrastructure
**Universal server management and coordination**
- **OUTPUT command suite** with LIST, STATUS, START, STOP, HEALTH, RESTART
- **Centralized server management** for all web extensions
- **Port conflict resolution** with auto-detection and dynamic assignment
- **Health monitoring system** with real-time status and percentages
- **Server lifecycle management** with proper cleanup and error handling
- **Integration with ServerManager** for unified web extension control
- **Comprehensive logging** to sandbox/logs/servers/ for debugging

**Key Achievements**: Production-ready web infrastructure, multi-server coordination

### ⚡ v1.0.6 - CLI Terminal Features
**Modern intelligent command-line enhancements**
- **Enhanced command history** with SQLite persistence and fuzzy search
- **Advanced tab completion** with context-aware suggestions and fuzzy matching
- **Dynamic color themes** with accessibility and colorblind support
- **Real-time progress indicators** for long-running operations
- **Session management** with workspace state persistence and auto-save
- **Adaptive layouts** responsive to screen size changes
- **5 new core services** with 7,042 lines of modern CLI infrastructure

**Key Achievements**: 100% integration test coverage, universal accessibility support

[📖 View Complete Development History →](Development-History)

---

## 🎯 Who Is This For?

### 🎓 Learners
- **New Developers**: Learn CLI development, parsing, and OK Assist integration
- **Python Students**: Study modular architecture and design patterns
- **DevOps Trainees**: Understand automation and scripting

### 🛠️ Builders
- **Tool Creators**: Use uDOS as a framework for custom CLIs
- **Educators**: Teaching material for systems programming
- **Researchers**: Experiment with OK assisted interfaces

### 🎮 Enthusiasts
- **Retro Computing Fans**: Enjoy the 8-bit aesthetic
- **Terminal Lovers**: Appreciate a well-crafted CLI
- **Game Developers**: Explore text-based navigation systems

### 👨‍💻 Developers
- **Contributors**: Follow structured [Developers Guide](Developers-Guide)
- **VS Code Users**: Integrated development environment with power dev mode
- **Quality Assurance**: Operator checkpoints and automated testing

---

## 🔧 Developer Resources

### Quick Development Setup
```bash
# Open the integrated workspace
code uDOS.code-workspace

# Check virtual environment
# VS Code Task: "Check Virtual Environment"

# Run core functionality tests
# VS Code Task: "Shakedown Terminal Core"
```

### Development Workflow
- **[Developers Guide](Developers-Guide)** - Complete developer documentation with workflows, APIs, and best practices
- **[Architecture](Architecture)** - Technical system design and patterns
- **[Command Reference](Command-Reference)** - Complete API documentation
- **Power Dev Mode** - Integrated logging, testing, and wiki updates

### Quality Assurance
Each development round includes:
- ✅ Automated feature checklists
- ✅ Operator review checkpoints
- ✅ Wiki update requirements
- ✅ Comprehensive testing coverage

---

## 🗺️ Learning Paths

### 🌱 Beginner Path
1. [Installation Guide](Installation)
2. [Quick Start Tutorial](Quick-Start)
3. [Basic Commands](Command-Reference#basic-commands)
4. [Creating Panels](Panels-Tutorial)
5. [First Script](Your-First-Script)

### 🌿 Intermediate Path
1. [Architecture Overview](Architecture)
2. [uCODE Language](uCODE-Language)
3. [Script Automation](Script-Automation)
4. [Theming System](Theming)
5. [Offline Engine](Offline-Engine)

### 🌳 Advanced Path
1. [Extension Development](Extensions)
2. [Custom Commands](Custom-Commands)
3. [Parser Internals](Parser-Internals)
4. [Mapping System](Mapping-System)
5. [Contributing Code](Contributing)

---

## 📚 Documentation Sections

### Core Concepts
- [Architecture](Architecture) - System design and components
- [uCODE Language](uCODE-Language) - Internal command format
- [Grid System](Grid-System) - Multi-panel management
- [Session Logging](Session-Logging) - History and recovery

### Features
- [Content Generation](Content-Generation) - Gemini-assisted content creation with OK Assist
- [Connection Awareness](Connection-Awareness) - Online/offline modes
- [Viewport System](Viewport-System) - Terminal adaptation
- [Mapping System](Mapping-System) - NetHack-style navigation
- [Color Palette](Color-Palette) - Synthwave DOS color system

### Development
- [Contributing Guide](Contributing) - How to contribute
- [Development Workflow](Development-Workflow) - Dev process
- [Testing Strategy](Testing) - Quality assurance
- [API Reference](API-Documentation) - Complete API docs

### Tutorials
- [Quick Start](Quick-Start) - Get running in 5 minutes
- [Your First Script](Your-First-Script) - Automation basics
- [Building Extensions](Extension-Tutorial) - Add custom features
- [Theming Tutorial](Theming-Tutorial) - Customize the experience

---

## 🎨 Visual Features

### Synthwave DOS Color Palette
uDOS uses a professional 8-color system optimized for terminal visibility:

🔴 **Red** (196) - Errors, alerts
🟢 **Green** (46) - Success, confirmations
🟡 **Yellow** (226) - Warnings, highlights
🔵 **Blue** (21) - Information, links
🟣 **Purple** (201) - Magic, special events
🔷 **Cyan** (51) - Technology, data
⚪ **White** (15) - Default text
⚫ **Black** (16) - Backgrounds

[Learn more about the color system →](Color-Palette)

### ASCII Art & Visualization
- Unicode box-drawing logo
- Viewport splash screen
- Grayscale gradients
- Map rendering

---

## 🤝 Community

### Get Help
- 💬 [Discussions](https://github.com/fredporter/uDOS/discussions) - Ask questions
- 🐛 [Issues](https://github.com/fredporter/uDOS/issues) - Report bugs
- 📧 Contact - [Your contact info]

### Contribute
- 🔧 [Contributing Guide](Contributing) - How to help
- 🎯 [Good First Issues](https://github.com/fredporter/uDOS/labels/good%20first%20issue)
- 🗺️ [Roadmap](Roadmap) - Project direction

### Resources
- 📦 [GitHub Repository](https://github.com/fredporter/uDOS)
- 📝 [Changelog](Changelog) - Version history
- 🚀 [Roadmap](Roadmap) - Future plans

---

## 🏆 Project Status

**Current Version**: v1.2.20 (December 2025)

**Key Features**:
- ✅ Workflow Management System (W-key, missions, checkpoints)
- ✅ TUI Panel Navigation (W/C/D/L/T/S/0/ESC keys)
- ✅ 230+ Survival Knowledge Guides (water, fire, shelter, medical, etc.)
- ✅ uPY v2.0.2 Scripting Runtime
- ✅ TILE Grid System (AA00-RL269, layers 100-899)
- ✅ 148 SHAKEDOWN Tests (95.9% coverage)
- ✅ Archive System (.archive/ folders, BACKUP/UNDO/REDO)
- ✅ Extension System (dashboard, teletext, maps, assistant)
- ✅ Offline-First Architecture
- ✅ Smart Command Completion
- ✅ Mapping system
- ✅ Color palette system

**Coming Soon**:
- 🔜 Plugin system
- 🔜 Advanced theming
- 🔜 Network integration
- 🔜 Enhanced OK Assist features

[View full roadmap →](Roadmap)

---

## 📄 License

uDOS is open source software. See [LICENSE](https://github.com/fredporter/uDOS/blob/main/LICENSE) for details.

---

**Ready to begin?** Start with the [Quick Start Guide](Quick-Start) or dive into the [Architecture](Architecture)!

🔮 *May your terminals be colorful and your commands clear.*
