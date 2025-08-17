# uDOS v1.3 Architecture Overview

## System Architecture

uDOS v1.3 follows a modular, extensible architecture designed for development productivity and system maintainability with a clean 11-folder structure.

### Core Components

#### 🏗️ **Directory Structure**

```
uDOS/
├── docs/           # Documentation and architecture guides
├── extension/      # VS Code extension development
├── install/        # Installation scripts and setup
├── sandbox/        # User workspace and development area
├── uCORE/          # Core system architecture and utilities
│   ├── code/       # Core utilities and micro-syntax
│   ├── datasets/   # System data and mappings
│   ├── extensions/ # Extension development framework
│   ├── launcher/   # Platform-specific launchers
│   ├── scripts/    # Core maintenance scripts
│   └── templates/  # System templates and configurations
├── uKNOWLEDGE/     # Knowledge base and documentation system
├── uMEMORY/        # User memory and data management
├── uSCRIPT/        # Production script library & execution engine
│   ├── config/     # JSON configuration system
│   ├── library/    # Multi-language script storage
│   ├── registry/   # Script catalog and metadata
│   ├── runtime/    # Execution environment
│   └── executed/   # Execution archives
└── wizard/         # Development workflow tools and environment
    ├── logs/       # Development session logs
    ├── reports/    # Workflow analysis and metrics
    ├── scripts/    # Development utilities
    ├── summaries/  # Session summaries
    ├── tools/      # Development utilities
    ├── vscode/     # VS Code integration
    └── workflows/  # Automated workflows
```

#### 🔧 **Core Systems**

##### **Production Script Management (uSCRIPT/)**
- **Multi-language execution engine**: Python, Shell, JavaScript, uCODE
- **Security-first architecture**: Sandbox execution with configurable security levels
- **Catalog-based organization**: Script registry with comprehensive metadata
- **Production-ready management**: Finalized, tested scripts vs development scripts

##### **Dev Mode Environment (wizard/)**
- **Special system development mode** available only to Wizard Installations
- **Enhanced workflow management** with roadmaps, versioning, and task tracking
- **Centralized uLOG system** with flat file structure for all logs, reports, summaries
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

- **Architecture Version**: v1.3
- **Extension System**: v1.0 with modular plugin architecture
- **Memory System**: v1.3 with enhanced state management
- **Development Environment**: v1.3 with wizard workflow system
- **Production Script System**: uSCRIPT v1.3 with multi-language execution engine
- **Knowledge Management**: uKNOWLEDGE v1.3 with documentation system
- **Core System**: uCORE v1.3 with template processing and utilities
- **Logging System**: v1.3 with structured development tracking
- **Filename Convention**: v1.3 with CAPS-NUMERIC-DASH standards
- **Repository Structure**: 11-folder clean architecture (reduced from scattered structure)

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
