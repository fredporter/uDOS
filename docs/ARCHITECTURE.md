# uDOS Architecture
System design and role capabilities for v1.0.4

## Overview
uDOS provides a clean, modular architecture with data separation and role-based access:
- **uCORE**: System code and core functionality
- **sandbox**: Active workspace and temporary files
- **uMEMORY**: Permanent user data and configuration
- **8-Role System**: Progressive capabilities from GHOST to WIZARD

## Core Components

### uCORE (System Code)
```
uCORE/
├── code/          # Core scripts (setup.sh, startup.sh, variable-manager.sh)
├── launcher/      # Platform-specific launchers
├── templates/     # System templates
└── system/        # System utilities
```

### sandbox (Active Workspace)
```
sandbox/
├── user.md           # User profile
├── current-role.conf # Role configuration
├── logs/            # All system logging
├── scripts/         # Temporary scripts
└── sessions/        # Current session data
```

### uMEMORY (Permanent Storage)
```
uMEMORY/
├── user/            # User data (installation.md)
├── system/          # System configuration (uDATA files)
└── templates/       # Data templates
```

## Role-Based System

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

### Role Capabilities

#### GHOST (Demo)
- Read-only access
- Basic tutorials
- Sandbox experimentation
- Demo interface

**Commands**: `[SYS|STATUS]`, `[ROLE|CURRENT]`, `[ASSIST|ENTER]`

#### DRONE (Automation)
- Task automation
- Maintenance operations
- Script execution
- Workflow management

**Commands**: `[TASK|CREATE]`, `[SCRIPT|RUN]`, `[MAINTAIN|SYSTEM]`

#### WIZARD (Full Access)
- Complete system control
- Core development access
- All functionality available
- `/dev` folder access

**Commands**: All commands, `[DEV|ACCESS]`, `[SYSTEM|MODIFY]`

### Access Matrix
| Role | sandbox | uMEMORY | uCORE | /dev |
|------|---------|---------|-------|------|
| GHOST | demo | none | none | none |
| DRONE | read/write | read | limited | none |
| WIZARD | full | full | full | full |

## Data Flow

### System Startup
1. Load role configuration (`sandbox/current-role.conf`)
2. Check user profile (`sandbox/user.md`)
3. Load system variables
4. Initialize role-appropriate interface

### Variable System
- System variables: `$USER-ROLE`, `$DISPLAY-MODE`
- User variables: Custom definitions with validation
- STORY collection: Interactive data gathering
- Template processing: `{VARIABLE}` substitution

### Command Processing
```
[COMMAND|ACTION*PARAMETER] → Router → Role Check → Execute
```

## Development Environment

### /dev Folder (Wizard + DEV Mode Only)
```
dev/
├── active/       # Current development (local only)
├── templates/    # Development templates (synced)
├── docs/         # Architecture docs (synced)
└── scripts/      # Development scripts
```

### Extension System
```
extensions/
├── core/         # System extensions
├── platform/     # Platform-specific
└── user/         # User extensions
```

## Multi-Mode Display

### Interface Modes
- **CLI**: Terminal interface (all roles)
- **DESKTOP**: Native application (Crypt+ roles)
- **WEB**: Browser interface (Crypt+ roles)

### Grid System (uGRID)
- 16×16 pixel cells (uCELL)
- Coordinate-based positioning (uMAP)
- Scalable from wearable to wallboard
- ASCII-based rendering

## File Organization

### Configuration
- System config: `/uMEMORY/system/uDATA-*.json`
- User settings: `/sandbox/user.md`
- Role config: `/sandbox/current-role.conf`

### Templates
- System: `/uMEMORY/templates/*.template.md`
- User: `/sandbox/templates/*.template.md`

### Scripts
- Core: `/uCORE/code/*.sh`
- User: `/sandbox/scripts/*.sh`

## Integration Points

### Variable Integration
- Command variables: `[SET $USER-ROLE|WIZARD]`
- Template variables: `{DEVELOPER-NAME}`
- System variables: Loaded on startup

### Command Integration
- Router: `/uCORE/code/command-router.sh`
- Variables: `/uCORE/code/variable-manager.sh`
- Setup: `/uCORE/code/setup.sh`

### Platform Integration
- Launchers: `/uCORE/launcher/`
- Scripts: `/uSCRIPT/`
- Network: `/uNETWORK/`

## Design Principles

### Simplicity
- Clean file structure
- Minimal dependencies
- Basic functionality first

### Modularity
- Separate concerns
- Clear interfaces
- Independent components

### Compatibility
- Cross-platform support
- Multiple interface modes
- Backward compatibility

### Security
- Role-based access
- Data separation
- Secure defaults

---
*uDOS v1.0.4 - Simple, lean, fast*

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
