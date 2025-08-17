# uDOS Architecture Overview

## System Architecture

uDOS follows a predominently flat, modular, user-centric architecture designed for simplicity and extensibility.

### Core Components

# uDOS v1.3 Architecture Overview

## System Architecture

uDOS v1.3 follows a modular, extensible architecture designed for development productivity and system maintainability.

### Core Components

#### 🏗️ **Directory Structure**

```
uDOS/
├── docs/           # Documentation and architecture guides
├── extension/      # VS Code extension development
├── install/        # Installation scripts and setup
├── sandbox/        # User workspace and development area
├── uCode/          # Core development utilities
├── uCORE/          # Core system architecture
│   ├── code/       # Core utilities and micro-syntax
│   ├── datasets/   # System data and mappings
│   ├── extensions/ # Extension development framework
│   ├── launcher/   # Platform-specific launchers
│   ├── scripts/    # Core maintenance scripts
│   └── templates/  # System templates and configurations
├── uExtensions/    # Extension registry and AI integrations
├── uInstall/       # Installation configurations
├── uMEMORY/        # User memory and data management
├── uTemplate/      # Global template system
└── wizard/         # Development workflow tools
    ├── tools/      # Development utilities
    ├── workflows/  # Automated workflows
    └── vscode/     # VS Code integration
```

#### 🔧 **Core Systems**

##### **Extension Architecture**
- **Modular plugin system** with registry-based management
- **VS Code integration** templates and syntax highlighting
- **AI service integrations** (Gemini CLI, development assistants)
- **Custom workflow automation** through wizard system

##### **Memory Management (uMEMORY/)**
- **User data persistence** with structured missions and milestones
- **State management** for system configurations
- **Personal workspace** isolation and privacy
- **Development history** tracking and recovery

##### **Template System (uTemplate/ & uCORE/templates/)**
- **Unified template processing** with shortcodes and variables
- **Form generation** for user interactions
- **Configuration templates** for system setup
- **Project scaffolding** and boilerplate generation

##### **Development Environment (wizard/)**
- **Workflow orchestration** for development tasks
- **Script execution** with logging and error handling
- **Development session** tracking and reporting
- **Tool integration** for modern development practices

#### 📊 **Data Flow**

1. **Development Workflow**
   ```
   User Request → wizard/ Tools → uCORE/ Scripts → Output/Logs
   ```

2. **Extension System**
   ```
   Extension Registry → uExtensions/ → VS Code → Development Tools
   ```

3. **Memory Management**
   ```
   User Actions → uMEMORY/ → State Persistence → Mission Tracking
   ```

4. **Template Processing**
   ```
   Template Request → uTemplate/ → Processing → Generated Output
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

- **Architecture Version**: v1.3
- **Extension System**: v1.0 with modular plugin architecture
- **Memory System**: v1.3 with enhanced state management
- **Development Environment**: v1.3 with wizard workflow system
- **Template System**: v2.1 with advanced shortcode support
- **Logging System**: v1.3 with structured development tracking
- **Filename Convention**: v1.3 with CAPS-NUMERIC-DASH standards

### Security Model

#### **Public Repository Content**
- ✅ Core system architecture (`uCORE/`)
- ✅ Documentation and guides (`docs/`)
- ✅ Extension framework (`uExtensions/`)
- ✅ Installation tools (`install/`, `uInstall/`)
- ✅ Development utilities (`wizard/tools/`, `uCode/`)
- ✅ Template system (`uTemplate/`)

#### **Private/Local Only (.gitignored)**
- 🔒 User memory and personal data (`uMEMORY/`)
- 🔒 Development session logs (`wizard/logs/`)
- 🔒 Personal workspace files (`sandbox/user.md`)
- 🔒 Editor configurations (`.vscode/`)
- 🔒 Authentication tokens and local configs

---

*This architecture document is part of the uDOS v1.3 knowledge base and is automatically updated with system evolution.*  
*Last Updated: Generated by TREE command - see `repo_structure.txt` for complete structure*

---
*This architecture document is part of the uDOS knowledge base and should be updated as the system evolves.*
