# uDOS - Universal Device Operating System

**A modular, role-based system providing unified interface across CLI Terminal, Desktop Application, and Web Export modes.**

```
    ██╗   ██╗██████╗  ██████╗ ███████╗
    ██║   ██║██╔══██╗██╔═══██╗██╔════╝
    ██║   ██║██║  ██║██║   ██║███████╗
    ██║   ██║██║  ██║██║   ██║╚════██║
    ╚██████╔╝██████╔╝╚██████╔╝███████║
     ╚═════╝ ╚═════╝  ╚═════╝ ╚══════╝

    Universal Device Operating System
    ════════════ v1.0.4.1 ═════════════
```

## 🚀 **Current Development Stage**

### 🏗️ **Foundational System Design**
- **Data Separation** - Clean separation between system code (uCORE) and user data (uMEMORY)
- **Workspace Organization** - sandbox (active/flushable) vs uMEMORY (permanent archive)
- **Repository Health** - Clean foundational codebase without development bloat
- **Documentation Standards** - Comprehensive style guide and foundational approach

### 🌐 **Three-Mode Display System**
- **CLI Terminal** - Core system control and automation interface
- **Desktop Application** - Native app for Drone+ user roles
- **Web Export** - Share dashboards and terminals remotely
- **Role-Based Access** - Interface availability based on user permissions (8-role system)

### 🔧 **Protected DEV Environment**
- **Core Development Workspace** - `/dev/` for uDOS system development
- **Access Control** - Wizard + DEV mode only
- **Persistent Protection** - Never flushed, always preserved
- **Clean Distribution** - Proper separation of development tools vs user content

### 🚀 **Flushable Sandbox**
- **User Workspace** - `/sandbox/` for all user development and experimentation
- **Session Management** - Archive valuable data before flushing
- **Clean Reset** - Fresh workspace for each session

### 🧠 **Memory Archive System**
- **Persistent Storage** - `/uMEMORY/` for long-term data preservation
- **Role Isolation** - Separate memory spaces for each role
- **Session Archiving** - Automatic data preservation before sandbox flush

---

## 📚 Documentation System

*Comprehensive documentation library with flat structure for easy access*

```
┌──────────────────────────────┐
│ uDOS Documentation Library   │
│ v1.0.4.1 Foundational       │
└──────────────────────────────┘
```

- **[Documentation Library](docs/README.md)** [10-50-00] – Complete documentation index with role-based learning paths
- **[User Guide](docs/USER-GUIDE.md)** [10-50-03] – Practical user manual and getting started
- **[uCODE Manual](docs/uCODE-MANUAL.md)** [10-50-05] – Complete command reference and syntax
- **[Architecture Guide](docs/ARCHITECTURE.md)** [10-50-01] – System architecture explained
- **[uGRID Display System](docs/Grid-Display-Specs.md)** [10-50-06] – Tile-based display architecture
- **[Smart Input System](docs/Smart-Input-System.md)** [10-30-00] – Advanced input capabilities
- **[Style Guide](docs/STYLE-GUIDE.md)** [10-50-02] – Comprehensive v1.3.3 standards with uHEX, uCODE, Mode 7
- **[Template Standard](docs/Template-Standard.md)** [10-40-00] – Templates and consistency
- **[User Authentication](docs/User-Authentication-System.md)** [10-30-01] – Security and authentication
- **[User Role Capabilities](docs/User-Role-Capabilities.md)** [10-30-02] – Role-based access system

## 🏗️ Foundational System Features

### Core Architecture
- **Data Separation**: Clean separation between system (uCORE), workspace (sandbox), and archive (uMEMORY)
- **Role-Based Access**: 8-tier hierarchy from Ghost (10) to Wizard (100) with appropriate permissions
- **Three-Mode Display**: CLI Terminal, Desktop Application, Web Export based on role access
- **Extension System**: Modular components organized by access level (core/platform/user)

### Development Workflow
- **Protected DEV Environment**: Core development workspace with Wizard + DEV mode access control
- **Flushable Sandbox**: User workspace for experimentation with session archiving
- **Documentation Standards**: Comprehensive style guide with ASCII art and naming conventions
- **VS Code Integration**: Complete task system and development environment setup

### Data Management
- **uDATA Format**: JSON-based configuration with structured data templates
- **Memory Archive System**: Persistent storage with role isolation and session archiving
- **Backup System**: Centralized storage with encryption and retention policies
- **Smart Input System**: Interactive command processing with context-aware suggestions

## �️ System Architecture

### Core Structure
```
uDOS/
├── uCORE/                     # System code (protected)
│   ├── code/                  # Core scripts and utilities
│   ├── launcher/              # Cross-platform launching
│   └── system/                # System components
├── sandbox/                   # Active workspace (flushable)
│   ├── data/                  # Working data files
│   └── logs/                  # Session logging
├── uMEMORY/                   # Permanent archive
│   ├── role/                  # Role-based data
│   └── system/                # System configurations
├── uNETWORK/                  # Display and networking
│   ├── server/                # Web server components
│   └── display/               # Display management
├── extensions/                # Extension system
│   ├── core/                  # Essential extensions
│   └── user/                  # User extensions
└── dev/                       # Development workspace (Wizard only)
    ├── active/                # Core development
    └── templates/             # Development templates
```

### Role-Based Access
- **Ghost (10)**: Read-only access, demo installation
- **Tomb (20)**: Basic storage operations
- **Crypt (30)**: Secure storage, standard operations
- **Drone (40)**: Automation and maintenance tasks
- **Knight (50)**: Security functions and operations
- **Imp (60)**: Development tools and script automation
- **Sorcerer (80)**: System administration and debugging
- **Wizard (100)**: Core development access + DEV mode

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

## � Quick Start

### Installation
```bash
# Clone repository
git clone https://github.com/fredporter/uDOS.git
cd uDOS

# Launch system
./uCORE/code/ucode.sh
```

### First Steps
1. **Check system status**: `[SYS] <STATUS>`
2. **View available commands**: `[HELP]`
3. **Set up your role**: `[ROLE] <ACTIVATE> {ROLE-NAME}`
4. **Explore documentation**: Check `docs/` folder

### Development Setup
1. **Enter DEV mode** (Wizard role required)
2. **Run development task**: `🚀 Start uDOS Development`
3. **Open VS Code workspace** with integrated tasks
4. **Use copilot instructions** at `.github/copilot-instructions.md`
## 🤝 Contributing

### Development Guidelines
- **Follow foundational approach**: Simple, lean, fast
- **Use proper documentation**: Reference style guide and templates
- **Test thoroughly**: Use available test tasks
- **Maintain role hierarchy**: Respect 8-tier access control

### Repository Structure
- **Core development**: Use `dev/` workspace (Wizard + DEV mode only)
- **User contributions**: Follow extension system patterns
- **Documentation updates**: Maintain version consistency at v1.0.4.1
- **Code standards**: Follow copilot instructions and style guide

---

## 📄 License

MIT License - See LICENSE file for details.

---

```
╔══════════════════════════════════════════════════════════════════════════════╗
║                                                                              ║
║     🌟 uDOS v1.0.4.1 - Universal Device Operating System 🌟                 ║
║                                                                              ║
║   Foundational system design with clean architecture and role-based access  ║
║   Three-mode display • Data separation • Extension system • Dev workflow    ║
║   Simple, lean, fast - everything needed for sustainable development        ║
║                                                                              ║
║          🚀 Build once, run everywhere - The universal way 🚀                ║
║                                                                              ║
╚══════════════════════════════════════════════════════════════════════════════╝
```

*uDOS v1.0.4.1 - Foundational System Design*
*August 26, 2025*
