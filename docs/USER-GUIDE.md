# uDOS v1.3 User Guide

```
    ██╗   ██╗██████╗  ██████╗ ███████╗
    ██║   ██║██╔══██╗██╔═══██╗██╔════╝
    ██║   ██║██║  ██║██║   ██║███████╗
    ██║   ██║██║  ██║██║   ██║╚════██║
    ╚██████╔╝██████╔╝╚██████╔╝███████║
     ╚═════╝ ╚═════╝  ╚═════╝ ╚══════╝

    Universal Data Operating System
    ═══════════════ v1.3 ═══════════════
```

**Edition**: v1.3 Production Guide  
**Published**: August 2025  
**System**: Universal Data Operating System v1.3  
**Features**: Timezone Integration, Wizard Mode, ASSIST Enhancement, uSCRIPT Production Library

---

## Quick Start Guide

### 🚀 What's New in v1.3

#### Enhanced Naming Convention
All files now follow the **CAPS-NUMERIC-DASH** standard:
```
uTYPE-YYYYMMDD-HHMM-TTZ-MMLLNN.md

Example: uLOG-20250816-1640-28-00SY43.md
```

#### Timezone Integration
- **38 timezone codes** mapped from existing city dataset
- **Automatic detection** of your current timezone
- **Global compatibility** with standard timezone formats

#### Dev Mode (Wizard Installations)
- **Special system development mode** available only to Wizard Installations
- **Advanced development tools** housed in the wizard folder
- **uLOG Management**: Centralized logging with flat file structure
- **Workflow Management**: Enhanced roadmap, versioning, and task tracking

#### uSCRIPT Production Script Library
- **Multi-language execution engine**: Python, Shell, JavaScript, uCODE
- **Security-first architecture**: Sandbox execution with configurable security levels
- **Catalog-based organization**: Script registry with comprehensive metadata
- **Production vs Development**: Clear separation from Dev Mode development scripts

#### Enhanced ASSIST Mode
- **Sandbox task management** for AI-enhanced workflows
- **Natural language processing** for task creation
- **Automated documentation** generation
- **Context-aware assistance** with development integration

---

## Getting Started

### 🎯 First Time Setup

When you start uDOS v1.3, the system automatically:

1. **Detects your timezone** and maps it to a 2-digit code
2. **Sets up your development environment** (if wizard user)
3. **Migrates existing files** to v1.3 naming convention
4. **Initializes task management** system

### 📋 Basic Commands

```ascii
┌─── ESSENTIAL COMMANDS ──────────────────────────────┐
│                                                     │
│  STATUS       📊 System overview with v1.3 info    │
│  HELP         📖 Comprehensive help system          │
│  DASH         🎛️  Enhanced dashboard with timezone  │
│  ASSIST       🤖 AI-powered task assistance         │
│  DEV          🛠️  Enter Dev Mode (Wizard only)       │
│                                                     │
└─────────────────────────────────────────────────────┘
```

### 🌍 Timezone System

uDOS v1.3 automatically detects and uses your timezone:

| Timezone Code | Region | UTC Offset | Example Location |
|---------------|--------|------------|------------------|
| 28 | AEDT/AEST | +10/+11 | Sydney, Australia |
| 02 | EST/EDT | -5/-4 | New York, USA |
| 08 | CET/CEST | +1/+2 | Berlin, Germany |
| 23 | JST | +9 | Tokyo, Japan |
| 09 | GMT | ±0 | London, UK |

---

## File Management

### 📁 v1.3 Naming Convention

All files follow the enhanced naming standard:

#### File Types
- **uLOG**: Activity logs and session records
- **uSCRIPT**: Executable scripts and automation
- **uDOC**: Documentation and guides
- **uTASK**: Task definitions and missions
- **uDATA**: Datasets and information files

#### Location Codes
- **MMLLNN**: Map(00-99) + Location + Number
- **00**: System template (Planet Earth)
- **01-99**: Custom user maps

#### Examples
```
uLOG-20250816-1640-28-00SY43.md    # Log file, Sydney timezone
uSCRIPT-20250816-0930-02-00NY12.sh # Script, New York timezone
uTASK-20250816-1500-08-00BE01.md   # Task, Berlin timezone
```

### 🔄 File Migration

Existing files are automatically migrated to v1.3 format:

```bash
# Check migration status
./uCORE/scripts/migrate-to-v13.sh . --dry-run

# Perform migration
./uCORE/scripts/migrate-to-v13.sh ./uMEMORY
```

---

## Dev Mode (Wizard Installations Only)

### 🧙‍♂️ Entering Dev Mode

For Wizard Installation users with special development access:

```bash
# Enter development environment
cd wizard

# Start development session
./tools/dev-session-logger.sh start "Session Title" "Objectives"

# Launch VS Code workspace
code vscode/
```

### 📊 Development Features

#### Automated Logging
All development activities are automatically logged:
```
uLOG-20250816-1500-28-00SS0816.md  # Session log
```

#### Task Integration
Connect development work with ASSIST mode tasks:
```
sandbox/tasks/assist-mode/    # AI-enhanced tasks
sandbox/tasks/in-progress/    # Active development
sandbox/tasks/completed/      # Finished work
```

#### Session Management
```bash
# Log development activity
./tools/dev-session-logger.sh log "CODE_CHANGE" "Updated timezone mapper"

# End development session
./tools/dev-session-logger.sh end "Session complete"
```

---

## ASSIST Mode Enhancement

### 🤖 AI-Powered Task Management

ASSIST mode now integrates with the sandbox task system:

#### Task Creation
```bash
# Create ASSIST mode task
ASSIST CREATE TASK "Implement new feature"

# Natural language task creation
ASSIST "I need help organizing my development workflow"
```

#### Task Management
Tasks are stored in the sandbox with v1.3 naming:
```
sandbox/tasks/assist-mode/uTASK-20250816-1600-28-00AI01.md
```

#### ASSIST Integration Points
- **Development Sessions**: AI assists with coding workflows
- **Documentation**: Automated documentation generation
- **Code Review**: AI-enhanced code analysis
- **Task Automation**: Intelligent task scheduling

---

## Enhanced Dashboard

### 📈 v1.3 Dashboard Features

The dashboard now includes timezone-aware information:

```ascii
┌─── uDOS v1.3 DASHBOARD ─────────────────────────────┐
│                                                     │
│  🌍 Timezone: AEDT (28)    📅 Date: 2025-08-16     │
│  🕐 Local: 16:40:23        🌐 UTC: 05:40:23         │
│                                                     │
│  📊 System Status          🧠 Memory v1.3           │
│  ══════════════            ═══════════════          │
│  Online    ✅              Files: 42 (v1.3)        │
│  Mode: Production          Naming: CAPS-NUM-DASH    │
│  Layout: Enhanced          Migration: Complete      │
│                                                     │
│  🎯 Active Tasks          📈 Development Activity   │
│  ═════════════            ══════════════════════   │
│  ASSIST: 3                Sessions: 5 today        │
│  DEV: 2                   Last: 30min ago          │
│  COMPLETE: 8              Status: Active           │
│                                                     │
└─────────────────────────────────────────────────────┘
```

### 🎛️ Dashboard Commands
```bash
DASH                 # Main dashboard
DASH TIMEZONE        # Timezone information
DASH DEV             # Development activity
DASH ASSIST          # ASSIST mode status
DASH MIGRATION       # v1.3 migration status
```

---

## Task Management System

### 📋 Sandbox Task Structure

```
sandbox/tasks/
├── assist-mode/     # AI-enhanced tasks
├── in-progress/     # Current work
├── completed/       # Finished tasks
└── templates/       # Task templates
```

### 🎯 Task Workflow

#### 1. Task Creation
Use templates to create consistent tasks:
```bash
# Copy template
cp sandbox/tasks/templates/task-template.md sandbox/tasks/in-progress/

# Rename with v1.3 convention
mv task-template.md uTASK-20250816-1600-28-00PR01.md
```

#### 2. ASSIST Integration
ASSIST mode can automatically create and manage tasks:
```bash
ASSIST CREATE "Optimize timezone mapping performance"
```

#### 3. Development Integration
Link tasks with development sessions:
```bash
# Start session with task reference
./wizard/tools/dev-session-logger.sh start "Task Implementation" "Working on uTASK-20250816-1600-28-00PR01"
```

#### 4. Completion
Move completed tasks to archive:
```bash
mv sandbox/tasks/in-progress/uTASK-* sandbox/tasks/completed/
```

---

## Command Reference

### 🔧 Core Commands v1.3

| Command | Description | Example |
|---------|-------------|---------|
| `STATUS` | System overview with v1.3 info | `STATUS` |
| `DASH` | Enhanced dashboard | `DASH TIMEZONE` |
| `ASSIST` | AI-powered assistance | `ASSIST CREATE TASK "title"` |
| `DEV` | Dev Mode | `DEV START SESSION` |
| `MIGRATE` | v1.3 file migration | `MIGRATE --dry-run` |

### 📁 File Commands

| Command | Description | Example |
|---------|-------------|---------|
| `GENERATE FILENAME` | Create v1.3 filename | `GENERATE FILENAME SCRIPT "description"` |
| `VALIDATE NAMING` | Check v1.3 compliance | `VALIDATE NAMING filename.md` |
| `MAP TIMEZONE` | Convert timezone codes | `MAP TIMEZONE AEDT` |

### 🤖 ASSIST Commands

| Command | Description | Example |
|---------|-------------|---------|
| `ASSIST CREATE TASK` | Create new task | `ASSIST CREATE TASK "title"` |
| `ASSIST STATUS` | Show ASSIST activity | `ASSIST STATUS` |
| `ASSIST HELP` | ASSIST mode help | `ASSIST HELP TASKS` |

---

## Advanced Features

### 🔧 Development Tools

#### Filename Generator
```bash
# Generate v1.3 compliant filename
./uCORE/scripts/generate-filename-v3.sh SCRIPT "Build automation"
# Output: uSCRIPT-20250816-1640-28-00SY43.sh
```

#### Timezone Mapper
```bash
# Convert timezone codes
./uCORE/scripts/timezone-mapper-v13.sh map AEDT
# Output: 28

# Show current timezone
./uCORE/scripts/timezone-mapper-v13.sh current
# Output: Current timezone: AEDT, 2-digit code: 28
```

#### Validation Tools
```bash
# Validate file naming
./uCORE/scripts/validate-naming-v3.sh filename.md

# Check system compliance
./uCORE/scripts/validate-naming-v3.sh . --check-all
```

### 📊 Monitoring & Analytics

#### Development Session Analytics
- **Session Duration**: Track development session lengths
- **Activity Patterns**: Identify peak development times
- **Task Completion**: Monitor task completion rates
- **ASSIST Usage**: Track AI assistance effectiveness

#### System Health Monitoring
- **Naming Compliance**: v1.3 convention adherence
- **Timezone Accuracy**: Automatic timezone detection success
- **Migration Status**: Track file migration progress
- **Performance Metrics**: System responsiveness tracking

---

## Troubleshooting

### 🚨 Common Issues v1.3

#### Timezone Detection Problems
```
❌ Timezone detection failed
✅ Solution: Manually set timezone using MAP TIMEZONE command
```

#### Naming Convention Errors
```
❌ File doesn't follow v1.3 convention
✅ Solution: Use GENERATE FILENAME or VALIDATE NAMING commands
```

#### Dev Mode Access
```
❌ Cannot enter wizard mode
✅ Solution: Ensure wizard user permissions are configured
```

#### Migration Issues
```
❌ Migration failed for some files
✅ Solution: Run migration with --dry-run first, check permissions
```

### 🛠️ Diagnostic Commands

```bash
STATUS                    # System overview
VALIDATE SYSTEM          # Full system check
DASH MIGRATION           # Migration status
DEV STATUS               # Dev Mode status
ASSIST DIAGNOSTICS       # ASSIST mode health check
```

---

## Best Practices

### 📝 File Management
1. **Use v1.3 naming** for all new files
2. **Migrate existing files** gradually using migration tools
3. **Validate naming** regularly with validation scripts
4. **Organize by type** using proper uTYPE prefixes

### 🧙‍♂️ Development Workflow
1. **Start sessions** with clear objectives
2. **Log activities** regularly during development
3. **Link tasks** to development sessions
4. **Use ASSIST mode** for complex workflow automation

### 🤖 ASSIST Integration
1. **Create tasks** with clear descriptions
2. **Use natural language** for task requests
3. **Review AI suggestions** before implementation
4. **Archive completed tasks** for future reference

### 🌍 Timezone Management
1. **Verify timezone detection** on system startup
2. **Use consistent timezone codes** across files
3. **Update location codes** when traveling
4. **Validate timezone mapping** for accuracy

---

## uSCRIPT Production Script Library

### 🚀 Script Management

uSCRIPT v1.3 provides a production script library and execution engine:

```bash
# Navigate to uSCRIPT
cd uSCRIPT

# Initialize the system
./uscript.sh init

# List available scripts
./uscript.sh list

# Get script information
./uscript.sh info <script-name>

# Execute a script
./uscript.sh run <script-name> [arguments...]
```

### 🔧 Supported Languages

- **Python** (.py): Full Python 3 support with package management
- **Shell** (.sh): Bash scripts with timeout and security controls
- **JavaScript** (.js): Node.js execution environment
- **uCODE** (.ucode.md): Native uDOS script format

### 🛡️ Security Levels

- **safe**: Read-only scripts, sandboxed execution
- **elevated**: File modification allowed, requires confirmation
- **admin**: Full system access, requires admin privileges

### 📁 Directory Structure

```
uSCRIPT/
├── library/     # Multi-language script storage
├── config/      # JSON configuration system
├── registry/    # Script catalog and metadata
├── runtime/     # Execution environment
└── executed/    # Execution archives
```

---

## Support & Resources

### 📚 Documentation
- **Architecture Guide**: `/docs/ARCHITECTURE.md`
- **Style Guide**: `/docs/Style-Guide.md`
- **Development Guide**: `/wizard/README.md`
- **Task Templates**: `/sandbox/tasks/templates/`

### 🛠️ Tools & Utilities
- **Migration Script**: `/uCORE/scripts/migrate-to-v13.sh`
- **Filename Generator**: `/uCORE/scripts/generate-filename-v3.sh`
- **Timezone Mapper**: `/uCORE/scripts/timezone-mapper-v13.sh`
- **Development Logger**: `/wizard/tools/dev-session-logger.sh`

### 🤝 Community
- **GitHub Repository**: uDOS project repository
- **Development Discussions**: Community development forum
- **Issue Tracking**: Bug reports and feature requests
- **Knowledge Base**: Community-contributed documentation

---

**Document Status**: Production Ready  
**Version**: v1.3  
**Last Updated**: August 16, 2025  
**Next Review**: September 16, 2025

---

*uDOS v1.3 User Guide - Universal Data Operating System*  
*Precision Through Standardization*
