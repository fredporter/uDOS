# uDOS v1.3 Architecture Overview

**Last Updated:** August 17, 2025  
**Status:** Multi-Installation Architecture with Hex Filename Convention  
**Version:** v1.3 - Production Ready

## System Architecture

uDOS v1.3 follows a modular, extensible architecture designed for multi-installation role-based access with a clean hierarchical structure supporting 6 installation types and hex-based filename conventions.

### Core Components

#### 🏗️ **Directory Structure**

```
uDOS/
├── docs/                   # System Documentation (✅ Hex convention updated)
├── extension/              # VS Code extension development
├── install/                # Installation scripts for multi-role setup
├── installations/          # Multi-Installation Architecture (NEW v1.3)
│   ├── wizard/            # Level 100 - Full system access (symlink)
│   ├── sorcerer/          # Level 80 - Advanced management
│   ├── imp/               # Level 60 - Developer tools
│   ├── drone/             # Level 40 - Task automation
│   ├── tomb/              # Level 20 - Archive management
│   └── ghost/             # Level 10 - Demo installation
├── sandbox/                # User workspace and development area
├── shared/                 # Shared resources and permissions (NEW v1.3)
│   ├── configs/           # Cross-installation configurations
│   ├── permissions/       # Role-based permission files
│   └── resources/         # Common resources
├── uCORE/                  # Core system architecture and utilities
│   ├── code/              # Core utilities and uCODE shell
│   ├── datasets/          # System data and mappings
│   ├── extensions/        # Extension development framework
│   ├── launcher/          # Platform-specific launchers
│   └── templates/         # System templates (enhanced for hex)
├── uKNOWLEDGE/            # Knowledge base and documentation system
├── uMEMORY/               # User memory with hex filename support
│   ├── moves/            # Move files (uMOV-HEXCODE-*.md)
│   ├── missions/         # Mission files (uMIS-HEXCODE-*.md)
│   ├── memories/         # Memory files (uMEM-HEXCODE-*.md)
│   └── milestones/       # Milestone files (uMIL-HEXCODE-*.md)
├── uSCRIPT/               # Production script library & execution engine
│   ├── config/           # JSON configuration system
│   ├── library/          # Multi-language script storage
│   ├── registry/         # Script catalog and metadata
│   ├── runtime/          # Role-aware execution environment
│   └── templates/        # Script generation templates
└── wizard/                # Development environment (Level 100 only)
    ├── notes/            # Development logs (63+ hex-named files)
    ├── scripts/          # Development utilities
    ├── utilities/        # Hex conversion tools
    ├── vscode/           # VS Code integration
    └── workflows/        # Development workflows
```

#### 🔧 **Core Systems**

##### **Multi-Installation Architecture (installations/)**
- **6-tier role hierarchy**: Ghost(10) → Tomb(20) → Drone(40) → Imp(60) → Sorcerer(80) → Wizard(100)
- **Role-based permissions**: JSON-configured access controls per installation type
- **Cross-installation collaboration**: Secure sharing mechanisms between roles
- **Installation management**: Complete toolkit for role creation and management

##### **Hex Filename Convention System**
- **8-character hex encoding**: Date, time, timezone, and role/tile information
- **63+ files converted**: All uDOS generated files now use hex format
- **Temporal organization**: Chronological sorting with spatial context
- **Self-contained system**: No external timezone datasets required

##### **Production Script Management (uSCRIPT/)**
- **Multi-language execution engine**: Python, Shell, JavaScript, uCODE
- **Role-aware security**: Execution permissions based on installation type
- **Catalog-based organization**: Script registry with comprehensive metadata
- **Cross-installation sharing**: Template and script sharing with proper permissions

##### **Dev Mode Environment (wizard/)**
- **Special system development mode** available only to Wizard Installations
- **Enhanced workflow management** with roadmaps, versioning, and task tracking
- **Centralized log system** with flat file structure (uDEV-YYYYMMDD-HHMM-TTZ-TYPE.md format)
- **Advanced development tools** and utilities exclusive to Wizard users

##### **Extension Architecture (uCORE/extensions/)**
- **Modular plugin system** with registry-based management
- **VS Code integration** templates and syntax highlighting
- **AI service integrations** (Gemini CLI, development assistants)
- **Custom workflow automation** through wizard system

##### **Memory Management (uMEMORY/)**
- **User data persistence** with structured missions and milestones
- **State management** for system configurations
- **Personal workspace** isolation and privacy
- **Development history** tracking and recovery

##### **Knowledge Management (uKNOWLEDGE/)**
- **Knowledge base system** for documentation and learning
- **Information organization** and retrieval
- **Documentation standards** and best practices
- **Learning resource management**

##### **Core System (uCORE/)**
- **Unified template processing** with shortcodes and variables
- **Core utilities** and micro-syntax support
- **System datasets** and mapping configurations
- **Extension development framework**

#### 📊 **Data Flow**

1. **Development Workflow**
   ```
   User Request → wizard/ Tools → uCORE/ Scripts → Output/Logs
   ```

2. **Production Script Execution**
   ```
   Script Request → uSCRIPT/ → Security Check → Execution → Logging
   ```

3. **Extension System**
   ```
   Extension Registry → uCORE/extensions/ → VS Code → Development Tools
   ```

4. **Memory Management**
   ```
   User Actions → uMEMORY/ → State Persistence → Mission Tracking
   ```

5. **Knowledge Processing**
   ```
   Knowledge Request → uKNOWLEDGE/ → Processing → Documentation Output
   ```

### Design Principles

#### **Modular Architecture**
- **Separation of concerns** with clear component boundaries
- **Extension-first design** for easy customization and growth
- **Tool integration** through standardized interfaces

#### **Developer Experience**
- **Modern development workflows** with automation
- **VS Code integration** for seamless development
- **Comprehensive logging** and debugging support
- **Git-friendly** structure with proper .gitignore

#### **Security & Privacy**
- **User data isolation** in uMEMORY/ (gitignored)
- **Public/private separation** with security model
- **Local-only sensitive data** never committed to repository
- **Extension sandboxing** for safe third-party integrations
- **uSCRIPT security levels**: Multi-tier security (safe, elevated, admin)
- **Sandbox execution environment** for script isolation

#### **Script Management Architecture**
- **Development vs Production**: Clear separation between wizard/ and uSCRIPT/
- **Multi-language support**: Python, Shell, JavaScript, uCODE execution
- **Catalog-based organization**: JSON metadata system for script management
- **Security-first execution**: Sandboxed environments with permission levels

#### **Maintainability**
- **Consistent naming conventions** across all components
- **Comprehensive documentation** with living architecture
- **Automated structure generation** with tree command
- **Version-controlled standards** for ongoing consistency

### File Naming Conventions

#### **Scripts & Utilities**
- **Shell scripts**: `kebab-case.sh` (e.g., `cleanup-filenames.sh`)
- **Configuration files**: `kebab-case.json` (e.g., `template-system-config.json`)
- **Data files**: `camelCase.json` (e.g., `locationMap.json`, `timezoneMap.json`)

#### **Log Files**
- **Format**: `uLOG-YYYYMMDD-HHMM-TZ-TYPE.md`
- **Example**: `uLOG-20250817-1045-28-00SY01.md`
- **Components**:
  - `YYYYMMDD-HHMM`: Timestamp
  - `TZ`: Timezone code (28 = UTC+8)
  - `TYPE`: Operation type code

#### **Documentation**
- **Guides**: `TITLE-Guide.md` (e.g., `USER-GUIDE.md`)
- **Standards**: `TITLE-Standard.md` (e.g., `Template-Standard.md`)
- **Architecture**: `ARCHITECTURE.md`, `ROADMAP.md`

### Version Information

- **Architecture Version**: v1.3 - Multi-Installation with Hex Filename Convention
- **Multi-Installation System**: v1.3 with 6-tier role hierarchy (Ghost→Tomb→Drone→Imp→Sorcerer→Wizard)
- **Hex Filename Convention**: v3.0 with 8-character encoding (63+ files converted)
- **Extension System**: v1.0 with modular plugin architecture and hex integration
- **Memory System**: v1.3 with hex-based file organization and spatial context
- **Development Environment**: v1.3 with wizard workflow system (Level 100 access)
- **Production Script System**: uSCRIPT v1.3 with role-aware execution engine
- **Knowledge Management**: uKNOWLEDGE v1.3 with documentation system
- **Core System**: uCORE v1.3 with template processing and hex utilities
- **Logging System**: v1.3 with hex-based temporal tracking
- **Security Model**: v1.3 with JSON-configured role-based permissions
- **Repository Structure**: 170+ directories with multi-installation architecture

### Security Model

#### **Multi-Installation Security Architecture**
- 🔐 **Role-based access control**: 6-tier permission system (10-100 levels)
- 🔐 **JSON permission files**: `shared/permissions/` with role-specific configurations
- 🔐 **Cross-installation collaboration**: Secure sharing mechanisms between roles
- 🔐 **Installation isolation**: Separate execution environments per role type

#### **Public Repository Content**
- ✅ Core system architecture (`uCORE/`)
- ✅ Documentation and guides (`docs/`)
- ✅ Multi-installation framework (`installations/`)
- ✅ Shared resources and configs (`shared/`)
- ✅ Extension framework (`extension/`)
- ✅ Installation tools (`install/`)
- ✅ Development utilities (`wizard/tools/`)
- ✅ Template system (`uCORE/templates/`)

#### **Private/Local Only (.gitignored)**
- 🔒 User memory and personal data (`uMEMORY/user/`)
- 🔒 Development session logs (`wizard/notes/` - 63+ hex files)
- 🔒 Personal workspace files (`sandbox/user.md`)
- 🔒 Role-specific user data in installations
- 🔒 Editor configurations (`.vscode/`)
- 🔒 Authentication tokens and local configs

#### **Hex Filename Security**
- 🔐 **Temporal encoding**: Prevents filename conflicts across installations
- 🔐 **Role identification**: Embedded role/tile information for access control
- 🔐 **Timezone awareness**: Geographic context for security auditing
- 🔐 **Self-contained**: No external dependencies for filename generation

---

*This architecture document is part of the uDOS v1.3 knowledge base and is automatically updated with system evolution.*  
*Last Updated: August 17, 2025 - Updated for Multi-Installation Architecture and Hex Filename Convention v3.0*  
*Repository Structure: 170+ directories documented in `docs/uDOS-Repository-Structure.md`*
