# 🌀 uDOS — The User DOS Shell
*Version: v1.0.0 — Production Ready Distribution*

**uDOS** is a single-process, markdown-native, terminal-first operating system designed to give old devices new life and intelligent memory.  
It is for thinkers, tinkerers, writers, and dreamers — those who want a machine that remembers, evolves, and serves a singular user.

**🎯 v1.0 Production Features**:
- ✅ **Complete User Role System**: wizard/sorcerer/ghost/imp permission matrix
- ✅ **Single-User Installation**: Privacy-first architecture with local data control
- ✅ **Automated Setup & Validation**: First-time installation with integrity checks
- ✅ **Chester OK Companion**: Integrated assistant with personality system
- ✅ **VS Code Integration**: Native extension with uScript language support and 25+ tasks
- ✅ **Package Management**: Unified system for essential development tools
- ✅ **Template System**: Markdown-driven content generation with shortcode processing
- ✅ **Enhanced Logging**: Structured activity tracking and analytics
- ✅ **Sandbox Management**: Daily workspace organization and session tracking

**✅ v1.0 Production Foundation**:
- ✅ Complete user role system (wizard/sorcerer/ghost/imp)
- ✅ Single-user installation enforcement (privacy-first ethos)
- ✅ First-time setup with automated validation
- ✅ Comprehensive installation integrity checks
- ✅ Chester AI companion system integration
- ✅ VS Code native integration with 25+ pre-configured tasks
- ✅ Complete uDOS VS Code extension with uScript language support

---

## 🌱 Vision

- **Human-first, single-user design**: uDOS runs for *you* — not the cloud, not corporations.
- **Markdown as the OS language**: Every Move, Mission, Milestone, and Map lives in plain `.md`.
- **Process minimalism**: One shell, one thread, one memory — a living notebook with intent.
- **Memory with purpose**: All actions form a legacy, built from Moves and Missions over time.
- **Cross-platform longevity**: Runs natively on modern macOS and Linux — lightweight and thrives on old, repurposed machines.
- **Intelligent visualization**: Advanced mapping and analytics transform data into insights.

---

## 🧠 Core Concepts

| Term         | Description                                                             |
|--------------|-------------------------------------------------------------------------|
| **Move**     | A single input/output action — the atomic thought in uDOS with analytics |
| **Mission**  | A goal or project, composed of many moves with progress tracking        |
| **Milestone**| A significant checkpoint with objective-based completion metrics        |
| **Legacy**   | Archived results or final output from a completed uDOS instance        |
| **uMemory**  | Your personal memory: logs, state, and active history (privacy-protected) |
| **uKnowledge** | Shared Markdown reference knowledge, maps, guides, and general info   |
| **User Role**| NetHack-inspired permission system (wizard/sorcerer/ghost/imp)         |
| **Companion**| AI assistant system (Chester the Wizard's Assistant by default)       |
| **Map Layer**| Multi-dimensional data visualization from Earth's core to orbital space |
| **Shortcode**| Template-driven content generation with variable substitution          |

## ⚡ Quick Install

**Get uDOS running in under 5 minutes:**

```bash
curl -fsSL https://raw.githubusercontent.com/fredporter/uDOS/main/install-udos.sh | bash
```

**Manual Installation:**
```bash
git clone https://github.com/fredporter/uDOS.git ~/uDOS
cd ~/uDOS && ./install-udos.sh
```

**📚 Complete Installation Guide:** See [`docs/installation/`](docs/installation/) for detailed setup instructions, tutorials, and troubleshooting.

### 🔐 Core Ethos: One Installation Per User

uDOS enforces a **single-user installation model** for maximum privacy:
- **Privacy-First**: All user data stays in local `uMemory/` (gitignored)
- **Device-Bound**: Installation tied to specific hardware for security
- **No Sharing**: No multi-user accounts - new user = new installation
- **Data Sovereignty**: You own and control all your data completely

---

## 📁 Repo Structure (v1.0 Clean Architecture)

```text
/uDOS
├── 🏗️ CORE ARCHITECTURE (v1.0)
│
├── 📚 uKnowledge/               # Central shared knowledge bank
│   ├── packages/                # Package documentation
│   ├── companion/               # AI companion guides (Chester, etc.)
│   ├── general-library/         # General documentation
│   └── maps/                    # System maps and navigation
│
├── 🧠 uMemory/                  # ALL USER DATA (privacy-protected)
│   ├── user/                    # User identity and settings  
│   ├── users/                   # User role and permission system
│   ├── logs/                    # User activity logs
│   ├── state/                   # User state data
│   ├── missions/                # User missions
│   ├── milestones/              # User milestones  
│   ├── moves/                   # User action history
│   ├── templates/               # User-customized templates
│   └── legacy/                  # User legacy items
│
├── 🏖️ sandbox/                  # Daily working space (v1.0)
│   ├── today/                   # Current session workspace
│   ├── sessions/                # Historical daily sessions
│   ├── temp/                    # Temporary files (auto-cleanup)
│   ├── drafts/                  # Work in progress
│   └── finalized/               # Ready for uMemory storage
│
├── ⚙️ uCode/                    # Complete command centre
│   ├── ucode.sh                 # Main shell interface
│   ├── init-user.sh             # First-time setup and user validation
│   ├── user-roles.sh            # User role and permission management  
│   ├── validate-installation.sh # Installation integrity validation
│   ├── companion-system.sh     # AI companion management (Chester)
│   ├── packages/                # Package integration scripts
│   └── *.sh                     # System utilities
│
├── 🔧 uScript/                  # System scripts and execution environment
│   ├── system/                  # Core system scripts
│   ├── utilities/               # Utility scripts
│   ├── automation/              # Automation scripts
│   ├── examples/                # Example scripts
│   └── tests/                   # Script testing framework
│
├── 📋 uTemplate/                # Enhanced templates with mapping & analytics v1.1
│   ├── system/                  # System templates
│   ├── datasets/                # System datasets (locations, users, etc.)
│   ├── variables/               # System variables
│   ├── mapping/                 # 🗺️ Advanced mapping system (NEW v1.1)
│   │   ├── map-layers.md        # Multi-dimensional layer definitions
│   │   ├── process-map-shortcodes.sh  # Shortcode processor engine
│   │   ├── demo-map-integration.sh    # Interactive demo system
│   │   └── README.md            # Mapping system documentation
│   ├── installers/              # Multi-platform installer templates
│   ├── daily-move-log-v2.md     # 📊 Enhanced daily tracking (NEW v1.1)
│   ├── chester-uc-template.md   # Chester-enhanced template system
│   └── [TypeScript project]     # Template engine
│
├── 🚀 launcher/                 # macOS launchers (.app and .command)
├── 🔌 extension/                # VS Code extension (renamed from uExtension)
│   ├── src/                     # TypeScript extension source
│   ├── syntaxes/                # uScript language grammar
│   ├── snippets/                # uScript code snippets
│   └── *.vsix                   # Packaged extension files
├── 📦 package/                  # Package management system (v1.0)
│   ├── manifest.json            # Package definitions and auto-install
│   ├── install-queue.txt        # Startup installation queue
│   └── README.md                # Package system documentation
├── 🚀 install/                  # Installation and setup system (v1.0)
│   ├── install-udos.sh          # Main installation script
│   ├── setup-wizard.sh          # First-time setup wizard
│   ├── user-provisioning.sh     # User role setup
│   └── README.md                # Installation documentation
├── 📊 progress/                 # Development tracking and archived files
├── 📖 CHANGELOG.md              # Version history (v1.1 updates)
├── 📖 README.md                 # You're reading it
└── 📖 .vscode/                  # VS Code integration (25+ pre-configured tasks)
    ├── tasks.json               # One-click operations
    └── settings.json            # Optimized configuration
```

### 🗺️ Advanced Mapping System (NEW v1.1)

uDOS now includes a sophisticated geospatial visualization framework with multi-dimensional capabilities:

#### Virtual Layer Architecture
```ascii
                    ┌─────────────────────────────────┐
                    │     ATMOSPHERE (+∞)            │  🛰️ Satellites & Weather
                    ├─────────────────────────────────┤
                    │     AVIATION (+10km)           │  ✈️ Flight Paths & Traffic
                    ├─────────────────────────────────┤
                    │     CLOUDS (+2km)              │  ☁️ Weather Systems
                    ├─────────────────────────────────┤
                    │     SURFACE (0m)               │  🌍 Geography & Cities
                    ├─────────────────────────────────┤
                    │     SUBSURFACE (-100m)         │  🚇 Infrastructure
                    ├─────────────────────────────────┤
                    │     GEOLOGICAL (-1km)          │  🪨 Rock & Minerals
                    ├─────────────────────────────────┤
                    │     CORE (-6,371km)            │  🌋 Tectonic Data
                    └─────────────────────────────────┘
```

#### Key Features
- **20+ Shortcode Types**: Template-driven map generation
- **3 Projection Systems**: Mercator, Robinson, 3D Orthographic
- **Temporal Navigation**: Historical data, real-time feeds, predictive models
- **Interactive Processing**: Automatic shortcode extraction and visualization
- **ASCII Dashboards**: Enhanced data presentation with visual blocks

### 📊 Enhanced Analytics (NEW v1.1)

#### Smart Daily Tracking
- **Activity Dashboards**: ASCII-powered progress visualization
- **Performance Metrics**: Command timing and success rate analysis
- **Objective Tracking**: Goal-oriented productivity system
- **Predictive Insights**: Pattern recognition and workflow optimization

#### Enhanced Logging v2.1.0
- **JSON Analytics**: Structured performance data collection
- **Multi-format Export**: JSON, CSV, Markdown output options
- **Auto-archival**: Intelligent cleanup of historical data
- **Error Context**: Comprehensive error tracking with command context

### 🎯 Architectural Principles (v1.1)

- **📚 uKnowledge**: System documentation and shared knowledge (version controlled)
- **🧠 uMemory**: ALL user data - completely private and local-only (gitignored)  
- **🏖️ sandbox**: Daily working space for organized session management (v1.0)
- **⚙️ uCode**: Central command and control system with enhanced logging (v1.1)
- **🔧 uScript**: System-level script execution environment
- **📋 uTemplate**: Enhanced templates with mapping & analytics system (v1.1)
- **📦 package**: Bundled application management with auto-install (v1.0)
- **🚀 install**: Installation and user provisioning system (v1.0)
- **🔌 extension**: VS Code integration with uScript language support (v1.0)
- **🔐 Single-User**: One installation per user for maximum privacy and security

---

## 🚀 Running uDOS v1.0

uDOS v1.0 features complete VS Code integration with user role system and installation validation. **No Docker, no containers, no complexity!**

### ⚡ Quick Start (VS Code - Recommended)

1. **Clone and enter**: `git clone [repo] && cd uDOS`
2. **Install extension**: Run VS Code task `� Install uDOS VS Code Extension` 
3. **Start system**: Run VS Code task `🌀 Start uDOS` or `./uCode/ucode.sh`
4. **Validate setup**: Run `🔍 Check uDOS Setup` task

The VS Code extension provides uScript language support, Chester AI integration, and direct command execution.

### 🎯 VS Code Tasks Available (v1.0)

**Core Operations**:
- **🌀 Start uDOS** - Launch the main shell with user validation
- **� Initialize User** - First-time setup and role assignment
- **✅ Validate Installation** - Comprehensive integrity and privacy checks
- **👑 Show User Role** - Display current user permissions

**Development**:
- **📊 Generate Dashboard** - Create status dashboard  
- **🌳 Generate File Tree** - Build repository structure
- **📝 Create New Mission** - Start a new project
- **🤖 Start Chester** - Launch AI companion system

**System**:
- **🧹 Clean uDOS** - Reset system state (preserves user data)
- **🔍 Check Setup** - Quick system health check

### 🖥️ Native Terminal (Alternative)

```bash
cd ~/uDOS
./uCode/ucode.sh
```

###  Legacy Hardware Support

uDOS can run on older machines via:
- Lightweight Linux distributions + VS Code
- Offline environments (scripts run without cloud dependencies)
- Raspberry Pi or similar ARM devices

For legacy setup instructions, see `OPTIMIZATION.md`.

---

## 🗺️ Documentation & Development Planning

For complete system documentation and development planning:

➡️ [`docs/README.md`](docs/README.md) — Complete documentation index and navigation  
➡️ [`docs/future-roadmap.md`](docs/future-roadmap.md) — Comprehensive development planning  
➡️ [`docs/development-strategy.md`](docs/development-strategy.md) — Strategic development framework  
➡️ [`docs/technical-architecture.md`](docs/technical-architecture.md) — System architecture guide  
➡️ [`CHANGELOG.md`](CHANGELOG.md) — Version history and migration guides

**Note**: All roadmap content consolidated into main documentation (July 2025)

---

## 🤖 AI Companion System

uDOS v1.0 includes **Chester** - the Wizard's Assistant:

- **Personality-Driven**: Small dog personality with helpful traits
- **uc-Template Integration**: Enhanced templates with Chester's guidance  
- **Gemini CLI Integration**: Powered by Google's AI with personality parameters
- **Development Focus**: Dedicated to uDOS development and user assistance

Launch Chester: `./uCode/companion-system.sh start_chester`

---

## 🔐 User Role System (v1.0)

uDOS implements a NetHack-inspired role system:

| Role | Description | Permissions |
|------|-------------|-------------|
| **🧙‍♂️ Wizard** | Primary user (default) | Full system access, companion management |
| **🔮 Sorcerer** | Advanced user | Scripting, automation, companion interaction |
| **👻 Ghost** | Observer | Read-only access, template usage |
| **😈 Imp** | Sandbox user | Restricted testing environment |

**Key Features**:
- ✅ Single-user installation enforcement
- ✅ Device-bound security
- ✅ Permission matrix for all system components
- ✅ Privacy-first architecture

---

## 🧬 Collaboration & Development

uDOS v1.0 is a **co-created system** between:

- **👤 The Wizard**: The user and architect of uDOS (you!)
- **🤖 Chester**: The AI companion and development assistant
- **👥 The Community**: Contributors to the open-source uDOS ecosystem

**Chester** (formerly "Otter") is now the dedicated AI companion with:
- Small dog personality traits (helpful, loyal, energetic)
- Specialized knowledge of uDOS development
- Integration with uc-template system for enhanced guidance
- Focus on user empowerment and privacy protection

Every session, file, command, and mission is part of this collaboration.  
We build together. We remember together. We maintain privacy together.

---

## 🧬 Philosophy

uDOS is not a traditional operating system — it is a **privacy-first memory companion**.

It does not multitask in the cloud.  
It does not update without your consent.  
It does not forget your data exists.  
It does not share without your explicit permission.

Every session is remembered locally.  
Every command is logged privately.  
Every mission leaves a trace you control.

Everything is Markdown.  
Everything is yours.  
Everything stays local.

---

**uDOS v1.0.0 — Production Ready**

*Built for humans who think in Markdown and live in terminals.*

---

*🔐 Your data. Your device. Your companion. Your choice.*
