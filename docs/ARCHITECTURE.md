# uDOS Architecture v1.0.5.1
System design and modular architecture for the Universal Device Operating System

## Overview
uDOS provides a clean, **modular architecture** with complete separation between core utilities and feature modules:
- **uCORE**: Pure bash core system (100% bash-only, 1.4M, 77 scripts)
- **uSCRIPT/modules**: Feature modules (6,431 lines moved from uCORE)
- **sandbox**: Active workspace and user data
- **uMEMORY**: Permanent system configuration and templates
- **8-Role System**: Progressive capabilities from GHOST to WIZARD

## 🎯 Major Architecture Changes in v1.0.5.1

### Modular Refactoring Complete
- **6,431 lines moved** from uCORE to uSCRIPT modules
- **uCORE reduced by 23%** - now lean and focused
- **Zero Python dependencies** in uCORE (moved to uSCRIPT/legacy-python)
- **Module loader system** for clean core-to-module interface

### File Organization Improvements
- **installation.id**: `root/` → `uMEMORY/` (proper location)
- **Trash system**: `uCORE/trash/` → `sandbox/trash/` (proper scope)
- **Root launchers**: scattered → `launchers/` directory
- **Empty folders eliminated**: `/core` merged with `/code`

## Core Components

### uCORE (Pure Bash Core) - 100% Clean
```
uCORE/
├── code/              # Essential bash scripts only
│   ├── command-router.sh       # Central command processing (1,958 lines)
│   ├── module-loader.sh        # Interface to uSCRIPT modules (130 lines)
│   ├── variable-manager.sh     # Variable system (581 lines)
│   ├── template-engine.sh      # Template processing (497 lines)
│   └── utilities/              # Core utilities
├── bin/               # Essential binaries and tools
├── launcher/          # Platform-specific launchers
├── system/            # System utilities (bash only)
├── geo/               # Geographic engines
├── distribution/      # Role-based distributions
└── completion/        # Command completion
```
**Total: 1.4M, 77 shell scripts, 0 Python files**

### uSCRIPT/modules (Feature Modules) - Organized by Function
```
uSCRIPT/
├── modules/
│   ├── session/
│   │   └── session-manager.sh     # Session management (902 lines)
│   ├── workflow/
│   │   └── workflow-manager.sh    # User journey automation (1,073 lines)
│   ├── stories/
│   │   └── story-manager.sh       # Interactive variable collection (799 lines)
│   ├── backup/
│   │   └── backup-restore.sh      # Backup system (837 lines)
│   ├── input/
│   │   ├── smart-input.sh         # Advanced input processing
│   │   ├── smart-input-enhanced.sh
│   │   └── smart-input-*.sh       # Input variants
│   └── notifications/             # Future: Toast manager
├── legacy-python/     # Python files moved from uCORE
└── active/            # Development workspace
```
**Total: 6,431 lines moved to modular structure**

### sandbox (Active Workspace)
```
sandbox/
├── user.md           # User profile (key=value format)
├── sessions/         # Session data and state
├── logs/            # All system logging
├── trash/           # System trash (moved from uCORE)
└── temp/            # Temporary files
```

### uMEMORY (Permanent Storage & Configuration)
```
uMEMORY/
├── installation.id   # Installation identifier (moved from root)
├── installation.md   # Installation metadata
├── system/          # System configuration
├── templates/       # Data templates
└── user/            # User data archives
```

## Modular Integration System

### Module Loader Architecture
```bash
# Command flow in v1.0.5.1
User Command → uCORE/command-router.sh → module-loader.sh → uSCRIPT/modules/

# Example: Session management
./uCORE/code/command-router.sh "[SESSION|STATUS]"
  ↓
module-loader.sh exec session session-manager "status"
  ↓
uSCRIPT/modules/session/session-manager.sh status
```

### Available Modules
| Module | Location | Purpose | Lines | Status |
|--------|----------|---------|-------|--------|
| Session | `modules/session/` | Persistent state tracking | 902 | ✅ |
| Workflow | `modules/workflow/` | User journey automation | 1,073 | ✅ |
| Stories | `modules/stories/` | Interactive data collection | 799 | ✅ |
| Backup | `modules/backup/` | Backup/restore system | 837 | ✅ |
| Input | `modules/input/` | Advanced input processing | 656+ | ✅ |

### Module Commands
```bash
# Module management
./uCORE/code/module-loader.sh status          # Check all modules
./uCORE/code/module-loader.sh list           # List available modules
./uCORE/code/module-loader.sh exec <module> <script> <args>

# Integrated commands (through command router)
[SESSION|CREATE]     # Create new session
[SESSION|STATUS]     # Show session status  
[WORKFLOW|START]     # Start workflow
[BACKUP|CREATE]      # Create backup
[STORY|RUN*name]     # Execute story
```

## Role-Based System (Unchanged but Enhanced)

### 8-Role Hierarchy
Progressive capability model from basic to advanced:

1. **GHOST (Level 10)** - Demo installation, read-only access
2. **TOMB (Level 20)** - Archive access, data archaeology  
3. **CRYPT (Level 30)** - Encryption, security protocols
4. **DRONE (Level 40)** - Automation, maintenance tasks
5. **KNIGHT (Level 50)** - Security functions, standard operations
6. **IMP (Level 60)** - Development tools, automation
7. **SORCERER (Level 80)** - Advanced administration, debugging
8. **WIZARD (Level 100)** - Full system access, core development

### Enhanced Role Integration with Modules
All modular features respect the role-based access system:

#### GHOST (Demo) - Level 10
- Basic module status checking
- Read-only session viewing
- Module help and documentation

**Module Commands**: `[SESSION|STATUS]`, `[WORKFLOW|HELP]`, Module loader status

#### DRONE (Automation) - Level 40
- Session creation and management
- Workflow automation
- Basic backup operations
- Story execution

**Module Commands**: `[SESSION|CREATE]`, `[WORKFLOW|START]`, `[BACKUP|AUTO]`, `[STORY|RUN*name]`

#### WIZARD (Full Access) - Level 100
- Complete module access
- Module development and debugging
- Core system modification
- `/dev` folder access for module development

**Module Commands**: All module commands, module debugging, core development

### Access Matrix (Updated for Modular Architecture)
| Component | GHOST | TOMB | CRYPT | DRONE | KNIGHT | IMP | SORCERER | WIZARD |
|-----------|-------|------|-------|-------|--------|-----|----------|--------|
| uCORE commands | basic | basic | standard | standard | enhanced | enhanced | admin | full |
| Session modules | view | view | basic | full | full | full | full | full |
| Workflow modules | help | help | basic | full | full | full | full | full |
| Backup modules | none | view | basic | auto | manual | full | admin | full |
| Story modules | none | view | basic | run | create | develop | admin | full |
| Module development | none | none | none | none | none | basic | advanced | full |

## Data Flow (Enhanced for Modules)

### System Startup
1. Load authentication from `uMEMORY/installation.id` and `sandbox/user.md`
2. Initialize role configuration and permissions
3. Load module loader system
4. Initialize role-appropriate interface with module access

### Module Command Processing
```
[MODULE|ACTION*PARAMS] → Command Router → Role Check → Module Loader → Module Execution
```

### Variable System (Enhanced)
- System variables: `$USER-ROLE`, `$DISPLAY-MODE`
- Module variables: Cross-module variable sharing
- User variables: Custom definitions with validation
- Story collection: Interactive data gathering through story module
- Template processing: `{VARIABLE}` substitution with module integration

## Development Environment (Updated)

### /dev Folder (Wizard + DEV Mode Only)
```
dev/
├── active/       # Current development (local only)
├── templates/    # Development templates (synced)
├── docs/         # Architecture docs (updated for v1.0.5.1)
├── copilot/      # AI assistant context (updated)
└── scripts/      # Development scripts
```

### Module Development
- **Module Creation**: Template-based module scaffolding
- **Module Testing**: Isolated testing environment
- **Module Integration**: Clean interface through module loader
- **Legacy Migration**: Tools for moving features to modules

## Design Principles (Enhanced for v1.0.5.1)

### Modularity (Primary Focus)
- **Separation of Concerns**: Core utilities vs feature modules
- **Clean Interfaces**: Module loader provides consistent API
- **Independent Components**: Modules can be developed/tested separately
- **Backward Compatibility**: Legacy functionality preserved in modules

### Simplicity
- **Pure Bash Core**: uCORE eliminated Python dependencies
- **Clean File Structure**: Logical organization by function
- **Minimal Dependencies**: Core works on any bash-capable system
- **Basic Functionality First**: Essential features in core, advanced in modules

### Compatibility
- **Cross-platform Support**: Pure bash ensures universal compatibility
- **Multiple Interface Modes**: CLI/Desktop/Web interfaces maintained
- **Graceful Degradation**: System adapts to available resources
- **Legacy Support**: Old installations can upgrade cleanly

### Security
- **Role-based Module Access**: Modules respect permission system
- **Data Separation**: Clear boundaries between core and modules
- **Secure File Locations**: Proper placement of sensitive files
- **Secure Defaults**: Conservative permissions and access

---

## Migration from v1.0.4 to v1.0.5.1

### Automatic Migrations
- **installation.id**: Automatically moved to uMEMORY
- **user.md**: Updated to support key=value format
- **Command routing**: Transparently routes to modules
- **Module integration**: Existing commands work through module loader

### Breaking Changes
- **Python scripts in uCORE**: Moved to uSCRIPT/legacy-python
- **Direct module calls**: Should use module loader interface
- **Trash location**: Now in sandbox/trash instead of uCORE/trash

### New Features
- **Module system**: `./uCORE/code/module-loader.sh`
- **Enhanced session management**: Persistent state tracking
- **Workflow automation**: User journey management  
- **Story system**: Interactive variable collection
- **Comprehensive backup**: Full backup/restore functionality

---

## Command Examples (v1.0.5.1)

### Core Commands (uCORE)
```bash
# Role and system management
./uCORE/code/command-router.sh "[ROLE]"              # Show current role
./uCORE/code/command-router.sh "[SYSTEM|STATUS]"    # System status
./uCORE/code/command-router.sh "[HELP]"             # Show help

# Variable management
./uCORE/code/command-router.sh "[SET|VAR*value]"    # Set variable
./uCORE/code/command-router.sh "[GET|VAR]"          # Get variable
```

### Module Commands (via Command Router)
```bash
# Session management (through modules)
./uCORE/code/command-router.sh "[SESSION|CREATE]"   # Create session
./uCORE/code/command-router.sh "[SESSION|STATUS]"   # Session status
./uCORE/code/command-router.sh "[SESSION|LIST]"     # List sessions

# Workflow management
./uCORE/code/command-router.sh "[WORKFLOW|START]"   # Start workflow
./uCORE/code/command-router.sh "[WORKFLOW|STATUS]"  # Workflow status

# Backup operations
./uCORE/code/command-router.sh "[BACKUP|CREATE]"    # Create backup
./uCORE/code/command-router.sh "[BACKUP|RESTORE]"   # Restore backup

# Story system
./uCORE/code/command-router.sh "[STORY|LIST]"       # List stories
./uCORE/code/command-router.sh "[STORY|RUN*name]"   # Run story
```

### Direct Module Access
```bash
# Module management
./uCORE/code/module-loader.sh status                # Check all modules
./uCORE/code/module-loader.sh list                  # List modules
./uCORE/code/module-loader.sh exec session session-manager help

# Direct module execution
./uSCRIPT/modules/session/session-manager.sh create myproject
./uSCRIPT/modules/workflow/workflow-manager.sh start
./uSCRIPT/modules/backup/backup-restore.sh create manual
```

---

*uDOS v1.0.5.1 - Modular, Clean, Efficient*

### Architecture Summary

**Clean Separation Achieved:**
- **uCORE**: 100% bash-only core utilities (1.4M, 77 scripts)
- **uSCRIPT/modules**: Feature modules (6,431 lines organized by function)  
- **Module Loader**: Clean interface between core and modules
- **File Organization**: Proper location for all system files

**Benefits of Modular Architecture:**
- **Faster Core**: Essential operations execute immediately
- **Easier Development**: Features can be developed independently
- **Better Testing**: Modules can be tested in isolation
- **Cleaner Maintenance**: Clear separation of concerns
- **Enhanced Compatibility**: Core works on any bash system

**Future-Ready Design:**
- **Extension Points**: Easy to add new modules
- **Legacy Support**: Old features preserved in modules
- **Migration Path**: Clear upgrade strategy for existing installations
- **Development Framework**: Structured approach for new features

### uCORE - System Foundation
The heart of uDOS containing all system code and essential functionality:
- **core/**: Essential components (sandbox.sh, workflow-manager.sh)
- **launcher/**: Platform-specific launchers and startup scripts
- **code/**: Core system scripts and utilities
- **config/**: System-wide configuration management

### sandbox - Active Workspace
Dynamic workspace for all active development and logging:
- **logs/**: Centralized logging for all system and user activities
- **sessions/**: Current session data and temporary state
- **scripts/**: User scripts and temporary automation
- **experiments/**: Development workspace and testing
- **tasks/**: Task management and workflow data

### uMEMORY - Permanent Archive
Persistent storage for user data and configurations:
- **user/**: User-specific permanent data
- **role/**: Role-based configurations and settings
- **templates/**: Data templates and user configurations
- **system/**: System logs archive and metadata

### dev - Core Development Environment
Wizard role + DEV mode exclusive development workspace:
- **active/**: Local-only core development (not synced)
- **templates/**: Development templates (synced for collaboration)
- **docs/**: Architecture documentation (synced)
- **copilot/**: AI assistant context and instructions (synced)
- **vscode/**: VS Code development configurations (synced)

### Extension System
Modular components organized by access level:
- **core/**: Essential system extensions
- **platform/**: OS-specific implementations
- **user/**: User-installed extensions and tools

### uNETWORK - Communication Hub
Cross-platform connectivity and display management:
- **server/**: Flask/SocketIO server for web interface
- **display/**: Three-mode display system coordination
- **wizard/**: Network administration tools

---

## Role-Based Access System

uDOS implements a comprehensive 8-role system with specific capabilities and access levels:

### Role Hierarchy (Level 10-100)
```
Wizard (100)   → Full system access + Core development (/dev)
Sorcerer (80)  → Advanced administration and platform management
Imp (60)       → Development tools and script automation
Knight (50)    → Security functions and enhanced operations
Drone (40)     → Automation tasks and maintenance
Crypt (30)     → Secure storage and standard operations
Tomb (20)      → Basic storage and simple operations
Ghost (10)     → Demo installation, read-only access
```

### Access Control Matrix
| Feature                    | Ghost | Tomb | Crypt | Drone | Knight | Imp | Sorcerer | Wizard |
|---------------------------|-------|------|-------|-------|--------|-----|----------|--------|
| CLI Terminal Mode         | ✓     | ✓    | ✓     | ✓     | ✓      | ✓   | ✓        | ✓      |
| Desktop/Web Display       | ✗     | ✗    | ✓     | ✓     | ✓      | ✓   | ✓        | ✓      |
| Extension Installation    | ✗     | ✗    | ✗     | ✓     | ✓      | ✓   | ✓        | ✓      |
| Script Development        | ✗     | ✗    | ✗     | ✗     | ✗      | ✓   | ✓        | ✓      |
| System Administration     | ✗     | ✗    | ✗     | ✗     | ✗      | ✗   | ✓        | ✓      |
| Core Development (/dev)   | ✗     | ✗    | ✗     | ✗     | ✗      | ✗   | ✗        | ✓      |

### Development Environment Access
- **Core Development**: Requires Wizard role + DEV mode activation
- **User Development**: Available to Imp+ roles in /sandbox
- **Extension Development**: Available to Drone+ roles with templates
- **System Modification**: Wizard role exclusive for /uCORE changes

### User Authentication System

uDOS implements a foundational authentication system integrated with the role-based access control:

#### Authentication Storage
```
sandbox/
├── user/                   # User authentication data
│   ├── identity.md         # User identity and role settings
│   └── auth.json          # Authentication configuration (uDATA format)
└── sessions/               # Current session authentication state
```

#### Authentication Integration
- **Role Assignment**: Users assigned one of 8 roles (Ghost → Wizard)
- **uDATA Format**: Authentication uses standard JSON configuration format
- **Data Separation**: User auth data stored in sandbox, role definitions in uMEMORY
- **Development Mode**: Authentication bypass available for development workflows

#### Basic Authentication Commands
```ucode
[USER|CREATE]               # Create new user account
[USER|AUTH]                 # Authenticate current user
[USER|INFO]                 # Display user information and role
[USER|ROLE*wizard]          # Change user role (admin operation)
```

---

## Three-Mode Display System

uDOS provides a unified interface that adapts to three distinct display modes based on user role and environment, while maintaining the clean uCORE → uSCRIPT → uNETWORK separation for older machine compatibility:

### Mode Descriptions
- **CLI Terminal Mode**: Universal access for all roles, optimized for command-line interaction and older machines
- **Desktop Application Mode**: Enhanced GUI for Crypt+ roles with rich visual interface
- **Web Export Mode**: Browser-based interface for Crypt+ roles with cross-platform compatibility

### Compatibility Architecture
```
┌─────────────────────────────────────────────────────────────┐
│                    uDOS Interface Layer                     │
├─────────────────┬─────────────────┬─────────────────────────┤
│ CLI Terminal    │ Desktop App     │ Web Export              │
│ • All Roles     │ • Crypt+        │ • Crypt+                │
│ • Older Machines│ • Modern GUI    │ • Cross-platform        │
│ • uCORE Direct  │ • uSCRIPT Layer │ • uNETWORK Layer        │
│ • Fast Response │ • Interactive   │ • Remote Access         │
└─────────────────┴─────────────────┴─────────────────────────┘
         │                 │                       │
         ▼                 ▼                       ▼
    uCORE Shell ────► uSCRIPT Engine ────► uNETWORK Server
    (Essential)      (Enhanced Features)   (Network/Web)
```

### Implementation Components
- **uCORE/**: Core system ensuring essential functionality on any machine
- **uSCRIPT/**: Enhanced features that gracefully degrade on older systems
- **uNETWORK/server/**: Modern server stack for capable machines
- **Graceful Degradation**: System adapts based on available resources and role permissions

---

## uCODE Language

The native programming language for uSCRIPT operations:

```ucode
~ uCODE syntax examples
[SYS] <STATUS|BRIEF>                    ~ System status with pipe options
[ROLE] <ACTIVATE|FORCE> {WIZARD}        ~ Force role activation
[DATA] <SAVE|ENCRYPT> {KEY} {VALUE}     ~ Encrypted data storage
[SANDBOX] <INIT|WORKSPACE> {PROJECT}    ~ Initialize sandbox workspace
DEF {PROJECT-NAME} = {USER-INPUT}       ~ Variable definitions

<FUNCTION> {DAILY-MAINTENANCE}
    [LOG] <INFO|TIMESTAMP> {Starting maintenance...}
    [WORKFLOW] <CLEANUP|FORCE> {ALL}
    [SANDBOX] <BACKUP|AUTO> {SESSION}
<END-FUNCTION>
```

**Key Features:**
- CAPITALS-DASH-NUMBER naming convention for all identifiers
- PIPE | syntax for command options and modifiers
- ~ comments (avoiding unnecessary quotes)
- Clean data control with sandbox/uMEMORY separation
- Three-mode display integration commands
- Role-based access control enforcement
- Core development environment commands

---

## uSCRIPT Modules

Each uCODE module provides commands with clean data separation:

### Core System Modules
- **SANDBOX.ucode** → Active workspace management, session control, temporary data
- **MEMORY.ucode** → Permanent storage, user data archives, configuration management
- **ROLE.ucode** → Role-based access control, permission management, user authentication
- **DISPLAY.ucode** → Three-mode display coordination, interface switching

### Development Modules
- **DEV.ucode** → Core development environment, wizard-only operations
- **EXTENSION.ucode** → Extension management, installation, configuration
- **WORKFLOW.ucode** → Project management, briefings, roadmaps, assist mode

### Utility Modules
- **LOG.ucode** → Centralized logging to sandbox/logs/
- **NETWORK.ucode** → Server operations, cross-platform connectivity
- **BACKUP.ucode** → Data backup between sandbox and uMEMORY

### Command Examples:
```ucode
~ Module commands with data separation
[SANDBOX] <INIT|WORKSPACE> {PROJECT-NAME}
[MEMORY] <ARCHIVE|COMPRESS> {SANDBOX-DATA}
[ROLE] <CHECK|PERMISSIONS> {DEV-ACCESS}
[DISPLAY] <SWITCH|MODE> {WEB-EXPORT}
[DEV] <BUILD|CORE> {EXTENSION-NAME}
[LOG] <WRITE|SANDBOX> {MESSAGE} {TIMESTAMP}
```---

## Command Flow

1. User enters a command in the shell.
2. uCORE parses input using enhanced syntax recognition (CAPITALS-DASH-NUMBER format).
3. uSCRIPT executes the requested `.ucode` file with modern uCODE interpreter.
4. Workflow system handles briefings, roadmaps, and assist mode if needed.
5. Extensions, role-modules, or data control operations are called as required.
6. Results are processed through enhanced formatting and security filters.
7. Output displayed in clear Markdown with timestamp and context information.

### Enhanced Flow Example:
```ucode
~ Command flow with workflow integration
[WORKFLOW] <ASSIST> {ENTER}              ~ Enter assist mode
[ROLE] <ACTIVATE|FORCE> {DRONE}          ~ Activate role with force option
[MEMORY] <SEARCH|FUZZY> {PROJECT-FILES}  ~ Fuzzy search with pipe option
[WORKFLOW] <BRIEFINGS> {UPDATE}          ~ Update session briefings
[WORKFLOW] <ASSIST> {EXIT}               ~ Exit assist mode
```

---

## Command Flow

1. User enters command through chosen display mode (CLI/Desktop/Web)
2. uCORE validates user role and checks permissions
3. Command routing based on data separation (sandbox vs uMEMORY operations)
4. uSCRIPT processes commands with clean syntax
5. Extensions execute with role-based access control validation
6. Logging written to centralized sandbox/logs/ directory
7. Output formatted and delivered through appropriate display mode

### Command Examples:
```bash
# Role-based development access
./dev/workflow.sh assist enter                    # Wizard role + DEV mode
./sandbox/scripts/user-script.sh                 # Imp+ roles sandbox development

# Data separation commands
./uCORE/core/sandbox.sh init project-name        # Initialize sandbox workspace
./uCORE/core/workflow-manager.sh move "dev"      # Log move to sandbox/logs/

# Display mode switching
./uNETWORK/server/server.py --mode web          # Start web export mode
./uCORE/launcher/universal/start.sh --cli       # Force CLI terminal mode
```

---

## System Foundation

**Core Architecture:**
- **Data Separation**: Clear boundaries between uCORE (system), sandbox (active), uMEMORY (archive)
- **Three-Mode Display**: Unified interface supporting CLI Terminal, Desktop App, and Web Export
- **Development Environment**: Dedicated /dev folder for wizard role + DEV mode core development
- **Role-Based Access**: Comprehensive 8-role system with granular permissions
- **AI Assistant Integration**: Development context and instructions

**Essential Components:**
- **/dev folder**: Core development environment with templates, docs, and AI context
- **sandbox/logs/**: Centralized logging system for all activities
- **Three-mode display**: Adaptive interface based on user role and platform
- **Extension system**: Role-aware extension installation and management
- **Selective git sync**: Strategic synchronization for collaborative development

**Development Principles:**
- **Wizard-only core development**: Secure /dev environment for system modifications
- **AI-assisted development**: Integrated copilot instructions and development context
- **Clean repository structure**: Organized data separation with proper .gitignore
- **VS Code integration**: Development tasks, settings, and workspace configuration---
