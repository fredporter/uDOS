# uDOS v1.3.3 Architecture Guide

---
**Foreword**

This Architecture Guide explains how uDOS v1.3.3 is organised. Written in the style of early home computer manu**Notes**

This guide is presented in a clear and practical style, inspired by the Acorn 1981 User Manual. It is meant to be studied alongside the User Guide and uCODE Modular Command Reference Manual, giving you both a quick start and a deeper understanding of the system's design.

For detailed command syntax and examples, refer to the uCODE Modular Command Reference Manual which documents the complete CAPITALS-DASH-NUMBER syntax and PIPE | option system introduced in v1.3.3., it avoids jargon and gives you a clear picture of how the system fits together.

---

## System Overview

uDOS v1.3.3 uses a modular design with enhanced workflow integration. The clean core shell handles only essential tasks.
Complex features live in *uCODE scripts*. Extensions and role-based modules expand the system.

```
User Input
    |
    v
+----------+     +-----------+     +-------------+
|  uCORE   | --> |  uSCRIPT  | --> |  WORKFLOW   |
+----------+     +-----------+     +-------------+
    |                |                     |
    v                v                     v
+--------------------+     +------------------------+
| Extensions / Roles |     |   Enhanced Features    |
| DRONE, GHOST, etc. |     | Briefings, Roadmaps,  |
+--------------------+     | Assist Mode, Cleanup  |
                           +------------------------+
    |
    v
 Output to User
```

---

## Core Components

- **uCORE/** → The clean system shell, enhanced for v1.3.3. Handles routing, setup, and workflow integration.
- **uSCRIPT/** → Script library using modern uCODE syntax (CAPITALS-DASH-NUMBER naming).
- **uMEMORY/** → Workspace for missions, notes, personal files, and encrypted data storage.
- **uKNOWLEDGE/** → Shared documentation and references with enhanced search capabilities.
- **dev/** → Development environment with briefings, roadmaps, and workflow management.
- **uNETWORK/** → Network operations and API integrations.

---

## uCODE Language (v1.3.3)

The native programming language for uSCRIPT operations:

```ucode
~ Modern uCODE syntax examples
[SYS] <STATUS|BRIEF>           ~ System status with pipe options
[ROLE] <ACTIVATE|FORCE> {DRONE}  ~ Force role activation
[MEM] <STORE|ENCRYPT> {KEY} {VALUE}  ~ Encrypted data storage
DEF {PROJECT-NAME} = {USER-INPUT}    ~ Variable definitions

<FUNCTION> {DAILY-MAINTENANCE}
    [LOG] <INFO|TIMESTAMP> {Starting maintenance...}
    [WORKFLOW] <CLEANUP|FORCE> {ALL}
<END-FUNCTION>
```

**Key Features:**
- CAPITALS-DASH-NUMBER naming convention for all identifiers
- PIPE | syntax for command options and modifiers
- ~ comments (avoiding unnecessary quotes)
- Enhanced data control with [GET]/[POST] operations
- Integrated workflow management commands

---

## Modules and Scripts

Each uCODE module provides a set of commands using modern syntax:

- **MEMORY.ucode** → File management, search, statistics with encryption support.
- **MISSION.ucode** → Create and track tasks with workflow integration.
- **PACKAGE.ucode** → Install, remove, search, update packages with retry mechanisms.
- **LOG.ucode** → Enhanced logging with timestamp and stack trace options.
- **DEV.ucode** → Development, testing, profiling with assist mode.
- **RENDER.ucode** → ASCII graphics, charts, simple UIs with detailed options.
- **DASH.ucode** → System dashboard with real-time monitoring.
- **PANEL.ucode** → Control panels with secure access controls.
- **TREE.ucode** → Repository visualisation with recursive listing.
- **WORKFLOW.ucode** → Briefings, roadmaps, cleanup, and assist mode management.

### Enhanced Command Examples:
```ucode
~ Modern uCODE module commands
[MEMORY] <SEARCH|FUZZY> {QUERY}
[MISSION] <CREATE|PRIORITY> {TASK-ID} {DESCRIPTION}
[LOG] <ERROR|STACK> {MESSAGE} {CRITICAL}
[WORKFLOW] <BRIEFINGS|SYNC> {UPDATE}
```

---

## Extensions

Extensions add new capabilities with enhanced integration:

- **Enhanced Workflow System** → Briefings, roadmaps, assist mode, context analysis.
- **Data Control Extensions** → HTTP [GET]/[POST] operations, JSON processing, API integrations.
- **Security Extensions** → Encrypted storage, secure authentication, backup systems.
- **Role Modules**:
  - *DRONE/* → Automation, scheduling, and maintenance tasks
  - *GHOST/* → Demos, public documentation, and presentation mode
  - *IMP/* → Project editing, scripts, and development tools
  - *SORCERER/* → Advanced tools, system administration, and debugging
  - *WIZARD/* → Setup, configuration, and user guidance

### Role Command Examples:
```ucode
~ Enhanced role-based commands
[ROLE] <ACTIVATE|PRESERVE> {DRONE}     ~ Preserve session context
[ROLE] <SWITCH|FORCE> {SORCERER}       ~ Force switch for admin tasks
[ROLE] <PERMISSIONS|FULL> {IMP}        ~ Detailed permission analysis
```

---

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

## Version 1.3.3 Enhancements

**New Features:**
- Modern uCODE syntax with CAPITALS-DASH-NUMBER naming convention
- PIPE | options for enhanced command expressiveness
- Integrated workflow management with briefings and roadmaps
- Enhanced data control with [GET]/[POST] operations
- Encrypted storage and secure authentication systems
- Context-aware assist mode for complex operations
- Improved error handling with stack traces and detailed reporting

**Architecture Improvements:**
- Cleaner separation between core shell and extensions
- Enhanced modularity with role-based access controls
- Improved performance through optimized script execution
- Better integration between workflow and role management systems

---

**Notes**

This guide is presented in a clear and practical style, inspired by the Acorn 1981 User Manual. It is meant to be studied alongside the User Guide, giving you both a quick start and a deeper understanding of the system’s design.
