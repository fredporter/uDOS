# uDOS v1.3.1 - Universal Device Operating System

**A globally-aware, timezone-integrated development platform with AI-enhanced workflows and wizard user capabilities.**

```
    ██╗   ██╗██████╗  ██████╗ ███████╗
    ██║   ██║██╔══██╗██╔═══██╗██╔════╝
    ██║   ██║██║  ██║██║   ██║███████╗
    ██║   ██║██║  ██║██║   ██║╚════██║
    ╚██████╔╝██████╔╝╚██████╔╝███████║
     ╚═════╝ ╚═════╝  ╚═════╝ ╚══════╝

    Universal Device Operating System
    ═══════════════ v1.3.1 ══════════════
```

---

## [ ] Documentation System

*Manual Shelf: pick your guide, from quick start to deep architecture*

```
┌──────────────────────────────┐
│ uDOS Documentation Library   │
│ Practical Guides & Standards │
└──────────────────────────────┘
```

- **[ARCHITECTURE Guide](docs/technical/ARCHITECTURE.md)** [10-50-00] – System architecture explained  
- **[Core Concepts](docs/technical/Core-Concepts.md)** [10-50-01] – Foundations and philosophy  
- **[User Guide](docs/user-guides/USER-GUIDE.md)** [10-50-03] – Practical user manual  
- **[Wizard README](wizard/README.md)** [50-00-00] – Developer environment details  
- **[uCode Developer Guide](docs/development/uCode-Developer-Guide.md)** [10-50-02] – Writing and extending uCode  
- **[VS Code Dev Mode Guide](docs/development/VS-Code-Dev-Mode-Guide.md)** [10-10-05] – Editor integration  
- **[Smart Input System](docs/technical/Smart-Input-System.md)** [10-30-00] – Input/output design  
- **[Template Standard](docs/reference/Template-Standard.md)** [10-40-00] – Templates and consistency  
- **[Markdown Spec](docs/reference/Markdown-Spec.md)** [10-50-01] – Documentation format  
- **[Filename Convention](docs/reference/Filename-Convention.md)** [10-50-04] – Naming standards  
- **[Style Guide](docs/reference/Style-Guide.md)** [10-50-02] – Coding and writing style  

## 🚀 What's New in v1.3.1

### ✨ Major Features

#### 🎨 Font System Optimization
- **Streamlined Font Library**: Removed legacy Amiga, C64, and redundant Mode 7 fonts
- **System Font Integration**: Added 10 professional system fonts (Monaco, Menlo, SF Mono, etc.)
- **Programming Font Support**: Fira Code, JetBrains Mono, Source Code Pro
- **MODE7GX0 Default**: Authentic BBC Mode 7 square font as default
- **Performance Improvements**: Reduced font loading overhead and dependencies

#### 🧠 Enhanced Smart Input System
- **Autocomplete Engine**: 50+ predefined commands with category-based suggestions
- **Keyboard Navigation**: Arrow keys for suggestion selection and command history
- **Real-time Feedback**: Instant command suggestions as you type
- **uMEMORY Integration**: Smart loading of system resources and configurations

#### 🎯 UI/UX Improvements
- **Clean HTML Structure**: Removed duplicate elements and optimized layout
- **Fixed Icon Handlers**: All emoji and dashboard icons now properly functional
- **Status Bar Integration**: Real-time updates for font, theme, and system status
- **Professional Interface**: Flat design with authentic retro computing aesthetics

#### 🔧 System Integration
- **uMEMORY Resource Loading**: Direct access to color palettes, fonts, and configurations
- **Enhanced Startup Graphics**: Progressive 6-phase startup sequence with visual feedback
- **Teletext Demonstrations**: Authentic BBC Mode 7 block demonstrations
- **Cross-platform Compatibility**: Better font fallbacks and system integration

#### 🎯 uCode Universal Interface
- **MODE7GX Teletext Fonts**: Authentic BBC micro computing experience with 1:1.3 aspect ratio
- **Whirlwind Rapid Mode**: Enhanced development workflow capabilities
- **Multi-module Architecture**: Full access to uCORE, uSERVER, uMEMORY, and all system modules

#### 📚 Modular Architecture Revolution
- **ucode-modular.sh**: Clean 350-line core shell with intelligent command routing
- **Visual Basic-style uCode Scripts**: 9 comprehensive modules handling complex functionality
- **Dual Interface Support**: Both shortcode format `[COMMAND]` and full commands
- **Smart Command Routing**: Automatic detection between core commands and uCode scripts
- **Separation of Concerns**: Core handles routing, uCode scripts handle complexity

#### 🎯 Complete uCode Script Library
- **MEMORY.ucode**: Advanced memory management with search, organization, backup
- **MISSION.ucode**: Mission control system with planning, tracking, reporting  
- **PACKAGE.ucode**: Package management with dependencies and versioning
- **LOG.ucode**: Intelligent logging with filtering, analysis, monitoring
- **DEV.ucode**: Complete development toolkit with testing, building, debugging
- **RENDER.ucode**: Visual rendering system with ASCII art, charts, animations
- **DASH.ucode**: Interactive dashboard with real-time monitoring
- **PANEL.ucode**: System control panel with configuration management
- **TREE.ucode**: Clean directory structure visualization (detailed docs in `docs/uDOS-System-Documentation.md`)

#### 🔌 Extension System
- **Plugin-based Architecture**: Modular system for expanding functionality
- **Deployment Manager**: Comprehensive deployment system (drone, standalone, server, portable, cloud, developer)
- **Smart Input Enhanced**: Advanced form builders, wizards, and AI-powered input validation
- **Extension Registry**: Centralized management and discovery system

#### 🌐 Web Content Integration
- **URL to Markdown Converter**: Extract web content as clean markdown files
- **Batch Processing**: Convert multiple URLs efficiently with `udos-url2md-batch`
- **Metadata Tracking**: Automatic source tracking and timestamp generation
- **uDOS Integration**: Web content automatically saved to uMEMORY datagets

#### 🧙‍♂️ Wizard Development Environment
- **Renamed from uDEV**: Now called "wizard" for better user understanding
- **Exclusive development environment** for advanced users
- **Automated session logging** with comprehensive activity tracking
- **VS Code integration** with dedicated development workspace
- **Task management** integration with AI-enhanced workflows

See **wizard/README.md** for full details of the Wizard environment, including session logging, workflows, tools, VS Code integration, and reports.

#### 🌍 Global Timezone Integration (v1.2+)
- **38 timezone codes** automatically mapped from city dataset
- **Real-time timezone detection** with automatic file timestamping
- **Global compatibility** across all development workflows
- **DST awareness** with automatic daylight saving time handling

#### 🤖 Enhanced ASSIST Mode (v1.2+)
- **Sandbox task management** for organized development workflows
- **Natural language processing** for intuitive task creation
- **AI-powered automation** with context-aware assistance
- **Collaborative development** support with team workflows

#### 📁 v1.3 Architecture Benefits
- **Maintainability**: Modular design makes updates and debugging easier
- **Extensibility**: New commands can be added as uCode scripts without modifying core
- **Performance**: Optimized command processing and resource management
- **Clean Code**: Separation between routing logic and functional implementation
- **Comprehensive Validation**: Input validation and deployment verification

## 🏗️ Directory Structure

```
[00-00-00] uDOS/
├── [10-00-00] uCORE/          # Core system files (read-only in production)
│   ├── code/                  # Main system scripts [10-20-00]
│   ├── launcher/              # Cross-platform launching [10-10-00]
│   └── extensions/            # Extension system [10-30-00]
│       ├── registry.json      # Extension registry
│       ├── extensions.sh      # Extension manager
│       └── development/       # Extension development
├── [20-00-00] uMEMORY/        # User data & customizations  
├── [30-00-00] uKNOWLEDGE/     # Shared knowledge bank (Wizard managed)
├── [40-00-00] sandbox/        # User workspace & drafts
└── [50-00-00] wizard/         # Development environment (renamed from uDEV)
    ├── logs/                  # Development session logs
    ├── workflows/             # Workflow automation
    ├── tools/                 # Development tools
    ├── notes/                 # Strategy and planning documents
    ├── experiments/           # External packages and experimental tools
    ├── reports/               # Generated reports and summaries
    └── vscode/                # VS Code integration
```

## 🏗️ System Architecture Overview

### 🏢 Multi-Role Framework
- **6-tier role hierarchy**: Ghost(10) → Tomb(20) → Drone(40) → Imp(60) → Sorcerer(80) → Wizard(100)
- **Role-based permissions**: Each role contains its own permission configuration
- **Role isolation**: Independent permission systems per role level
- **Security model**: Granular access control for multi-role architecture

### 🔧 Core System (`uCORE/`)
- **`code/`** - Core utilities, uCODE shell, and system commands
- **`datasets/`** - Location mappings, timezone data, and system configurations
- **`install/`** - Installation scripts and role configurations for distribution
- **`launcher/`** - Platform-specific application launchers and installers
- **`templates/`** - System templates for hex filenames, forms, and configurations

### 🧠 User Memory System (`uMEMORY/`)
- **Hex filename convention**: 8-character encoding with temporal-spatial organization
- **Personal data archive**: Missions, moves, memories, milestones
- **Flat structure design**: Direct access to all user data
- **Privacy protection**: Completely isolated from distributed system

### 👨‍💻 Development Environment (`wizard/`)
- **Level 100 access**: Complete system access and development capabilities
- **`notes/`** - Development logs in hex format (63+ files, ALWAYS SYNCED)
- **`tools/`** - Development utilities and script executors
- **`utilities/`** - System utilities for hex conversion and maintenance
- **`vscode/`** - VS Code integration and configuration

### 📦 Script Management (`uSCRIPT/`)
- **Multi-language execution engine**: Python, Shell, JavaScript, uCODE
- **Role-aware security**: Execution permissions based on installation type
- **Production vs development**: Clear separation of stable vs experimental scripts
- **`library/`** - Organized by language (automation/, javascript/, python/, shell/, ucode/)

### 🏠 User Workspace (`sandbox/`)
- **Active workspace**: Where most user activity occurs daily
- **Task management**: In-progress and completed task organization
- **Experimentation area**: Safe space for testing and development
- **Archive pipeline**: Content moves to uMEMORY/ as daily sessions complete

### 📚 Knowledge Base (`uKNOWLEDGE/`)
- **Shared knowledge system**: Documentation and learning resources
- **Community content**: Shareable knowledge base across installations
- **Reference system**: Quick access to system documentation

### 📖 Documentation (`docs/`)
- **Complete system documentation**: Architecture guides and user manuals
- **[System Documentation](docs/uDOS-System-Documentation.md)**: File naming conventions, security model, and system standards
- **Style guides**: Development standards and conventions
- **API documentation**: Integration guides and technical references

### 🧙‍♂️ VS Code Extension Development (`wizard/vscode/`)
- **Extension source code**: Complete VS Code integration for uDOS
- **Development workspace**: Isolated development environment
- **Platform integration**: Cross-platform VS Code support
- **Extension distribution**: Packaged for VS Code marketplace

## 🔌 Extension System

uDOS v1.3 introduces a powerful extension system for modular functionality:

### Available Extensions
- **🚁 Deployment Manager**: Multi-platform deployment system (drone, standalone, server, portable, cloud, developer)
- **🧠 Smart Input Enhanced**: Advanced form builders, wizards, and AI-powered input validation
- **🤖 AI Assistant**: Intelligent automation and assistance capabilities

### Extension Usage
```bash
# List available extensions
./uCORE/extensions/extensions.sh LIST

# Run deployment manager
./uCORE/extensions/extensions.sh RUN deployment-manager DRONE /path/to/target

# Create interactive forms
./uCORE/extensions/extensions.sh RUN smart-input-enhanced FORM CREATE "contact-form"

# Run mission creation wizard
./uCORE/extensions/extensions.sh RUN smart-input-enhanced WIZARD mission-creation

# Convert web content to markdown
udos-url2md https://example.com
udos-url2md -t "My Article" https://blog.example.com/post
udos-url2md-batch urls.txt
```

## 🌟 Key Features v1.2

- **🚀 Cross-Platform Launchers**: Native launching for macOS, Windows, Linux
- **🔧 VS Code Integration**: Full development environment support
- **📋 Standardized Documentation**: Consistent markdown standards and location coding
- **💾 User Memory System**: Centralized user data management
- **🤖 Gemini CLI Integration**: Google Gemini assistant capabilities
- **🧪 Sandbox Environment**: Safe experimentation workspace
- **🌐 Web Content Extraction**: URL to markdown conversion with batch processing

## 📦 Components

### 🔧 uCORE/ - Core System [10-00-00]
**System files, protected from user modification**
- `code/` - Main uDOS scripts and logic [10-20-00]
- `launcher/` - Cross-platform launching system [10-10-00]  
- `extensions/` - Extension system and modules [10-30-00]
  - `registry.json` - Extension registry and metadata
  - `extensions.sh` - Extension manager and loader
  - `development/` - Extension development environment
    - `deployment-manager.sh` - Multi-platform deployment system
    - `smart-input-enhanced.sh` - Advanced input and form system
- `templates/` - Core template library [10-40-00]

### 💾 uMEMORY/ - User Data [20-00-00]
**Your personal data and customizations**
- `configs/` - User configuration and identity [20-10-00]
- `templates/` - Your custom templates [20-20-00]
- `scripts/` - Your custom scripts [20-30-00]
- `datasets/` - Your personal datasets [20-40-00]
- `projects/` - Your project files [20-50-00]
- `forms/` - Generated forms and responses [20-60-00]
- `deployments/` - Deployment configurations and logs [20-70-00]

### 📚 uKNOWLEDGE/ - Knowledge Bank [30-00-00]
**Shared public knowledge (Wizard managed)**
- Read-only in production mode
- Editable in development mode
- Contains shared intelligence and reference materials

### 🧪 sandbox/ - User Workspace [40-00-00]
**Your experimentation and draft area**
- `user.md` - Your personal notes and workspace [40-10-00]
- `scripts/` - Experimental scripts [40-20-00]
- `drafts/` - Work-in-progress files [40-30-00]
- `experiments/` - Testing and prototyping area [40-40-00]
- `test-deployment/` - Deployment testing environment [40-50-00]
- `datagets/` - Web content and extracted data [40-60-00]

### 🧙‍♂️ wizard/ - Development Environment [50-00-00]
**Advanced development and workflow system (renamed from uDEV)**
*See also:* `wizard/README.md` for setup, workflows, and usage.
- `logs/` - Development session logs and activity tracking [50-10-00]
- `workflows/` - Automated workflow definitions [50-20-00]
- `tools/` - Development and maintenance tools [50-30-00]
- `vscode/` - VS Code integration and workspace files [50-40-00]
- `reports/` - Generated reports and summaries [50-50-00]

## 🚀 Quick Start

### Easy Launch (All Platforms)
```bash
# Universal installer
./uCORE/launcher/install-launcher.sh

# Then use platform-specific launcher:
# • macOS: Double-click uDOS.command
# • Windows: Double-click uDOS.bat  
# • Linux: Use desktop launcher or run uDOS.sh
```

### Development Mode
```bash
# Start with VS Code integration
./uCORE/launcher/universal/start-dev.sh

# Or force terminal development mode
./uCORE/launcher/universal/start-udos.sh --dev
```

### Wizard Environment
Start the focused developer environment (see wizard/README.md for details).
```bash
# Start Wizard workflows and developer tools
./uCORE/launcher/universal/start-dev.sh --wizard
# Or open the VS Code workspace directly
code wizard/vscode/uDOS.code-workspace
```

### Manual Launch
```bash
# Start uDOS main interface
./uCORE/code/ucode.sh

# Start Gemini assistant (ASSIST mode)
./uCORE/code/ucode.sh assist

# Check system health
./uCORE/code/check.sh all

# Generate live dashboard
./uCORE/code/dash.sh live

# Convert web page to markdown
udos-url2md https://example.com

# Batch convert URLs from file
udos-url2md-batch urls.txt
```

## 🤖 Gemini Integration

### ASSIST Mode
```bash
./uCORE/scripts/assist
```
Development assistance with project context using Google Gemini

### COMMAND Mode  
```bash
./uCORE/scripts/command
```
Natural language system commands

### Direct Gemini Access
```bash
./uCORE/extensions/gemini/uc-gemini.sh
```
Direct access to Gemini CLI integration

## 🎯 User Roles

- **🧙‍♂️ Wizard**: Full system access and Gemini management
- **🔮 Sorcerer**: Extension development and advanced features  
- **👨‍🎓 Apprentice**: Learning-focused interface with guidance
- **📚 Scholar**: Research tools and knowledge management

## � Documentation & Standards

### 📋 Core Documentation [10-50-00]
- **[Markdown Standard v1.2](uCORE/docs/uDOS-Markdown-Standard.md)** [10-50-01] - Documentation formatting standards
- **[Location Map](uCORE/docs/uDOS-Location-Map.md)** [10-50-04] - Complete system mapping with location codes
- **[Development Guide](uCORE/docs/Development-Guide.md)** [10-50-02] - Developer workflow and best practices
- **[User Manual](uCORE/docs/User-Manual.md)** [10-50-03] - Complete user documentation

### � Implementation Summaries
- **[Cross-Platform Launcher](CROSS_PLATFORM_LAUNCHER_SUMMARY.md)** [00-21-00] - Launcher system implementation
- **[Documentation Standards](DOCUMENTATION_STANDARDS_SUMMARY.md)** [00-22-00] - Standards implementation details

## [ ] Documentation System

```
┌──────────────────────────────┐
│ uDOS Documentation Library   │
│ Practical Guides & Standards │
└──────────────────────────────┘
```

- **[ARCHITECTURE Guide](docs/technical/ARCHITECTURE.md)** [10-50-00] – System architecture explained  
- **[Core Concepts](docs/technical/Core-Concepts.md)** [10-50-01] – Foundations and philosophy  
- **[User Guide](docs/user-guides/USER-GUIDE.md)** [10-50-03] – Practical user manual  
- **[uCode Developer Guide](docs/development/uCode-Developer-Guide.md)** [10-50-02] – Writing and extending uCode  
- **[VS Code Dev Mode Guide](docs/development/VS-Code-Dev-Mode-Guide.md)** [10-10-05] – Editor integration  
- **[Smart Input System](docs/technical/Smart-Input-System.md)** [10-30-00] – Input/output design  
- **[Template Standard](docs/reference/Template-Standard.md)** [10-40-00] – Templates and consistency  
- **[Markdown Spec](docs/reference/Markdown-Spec.md)** [10-50-01] – Documentation format  
- **[Filename Convention](docs/reference/Filename-Convention.md)** [10-50-04] – Naming standards  
- **[Style Guide](docs/reference/Style-Guide.md)** [10-50-02] – Coding and writing style  

## 🔧 Development Environment

### VS Code Integration [10-10-05]
```bash
# Setup development environment
./uCORE/launcher/vscode/setup-vscode.sh

# Open workspace
code uDOS.code-workspace
```

### Location Code Navigation
```bash
# Quick component location reference
[10-10-00] Launcher system
[10-20-01] Main ucode.sh script  
[20-10-01] User identity.md
[10-50-01] Documentation standards
```

## 🆘 Support & Contributing

- **📚 Documentation**: [uCORE/docs/](uCORE/docs/) [10-50-00]
- **🐛 Issues**: Use location codes for precise component references
- **💡 Feature Requests**: Follow development guide standards [10-50-02]
- **🤝 Contributing**: See development documentation and standards

## ⚡ Architecture Benefits

- **Clear Separation**: System vs User vs Knowledge vs Workspace
- **Cross-Platform**: Native launchers for macOS, Windows, Linux
- **Standardized**: Consistent documentation and location coding
- **Scalable**: Easy to backup user data separately  
- **Maintainable**: Logical organization with precise component addressing
- **Developer-Friendly**: Full VS Code integration with debugging support

---

**uDOS v1.3** - *Where Data Meets Intelligence* ✨

**Features**: Extension System | Deployment Manager | Smart Input Enhanced | Wizard Development Environment | Web Content Extraction  
**Updated**: August 17, 2025 | **Architecture**: Modern Modular Design with Plugin Architecture

---
*For the full manual experience, see docs/user-guides/USER-GUIDE.md, written in the spirit of the Acorn 1981 User Manual.*
