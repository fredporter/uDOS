# uDOS v1.3 User Guide - BBC Mode 7 Edition

---

**Foreword**

Welcome to uDOS v1.3 with authentic BBC Mode 7 interface. This manual is written in the tradition of classic home computer guides — direct, practical, and nostalgic. Following the design principles from [BBC BASIC for Windows Manual](https://www.bbcbasic.co.uk/bbcwin/manual/bbcwinh.html), uDOS now features an authentic Mode 7 teletext interface with chunky block graphics and dashboard integration.

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

**Edition**: v1.3 Production Guide - BBC Mode 7 Interface  
**Published**: August 2025  
**System**: Universal Data Operating System v1.3  
**Features**: BBC Mode 7 Interface, Chunky Block Graphics, Dashboard Integration, Authentic Teletext Styling

---

## BBC Mode 7 Interface

### What's New: Authentic Mode 7 Design

#### BBC Mode 7 Teletext Interface
uDOS v1.3 now features an **authentic BBC Mode 7 interface**:
- **640×500 pixel display** with 40×25 character grid
- **Authentic SAA5050 color palette** with BBC Micro teletext colors
- **Chunky block graphics** using █ characters for buttons
- **MODE7GX3 font** for authentic BBC Micro typography

#### Dashboard Integration
**Chunky block button system** for uDOS modules:
- **uCORE System**: Green block buttons for core functions
- **uSERVER Web**: Blue block buttons for web services  
- **uSCRIPT Auto**: Magenta block buttons for automation
- **uKNOWLEDGE**: Cyan block buttons for documentation
- **Template System**: Mode 7 integrated template access

#### Authentic Teletext Features
- **Double-height text**: BBC Mode 7 standard character sizing
- **Flashing text**: CSS animations for attention and authenticity
- **Background colors**: Text with colored backgrounds per Mode 7 standard
- **Block graphics**: Complete SAA5050 block character support

### Mode 7 Interface Layout

```ascii
┌─── BBC MODE 7 INTERFACE (640×500) ──────────────────┐
│                                                     │
│  ██ uDOS v1.3 ██  UNIVERSAL DATA OPERATING SYSTEM   │
│                                                     │
│  ▌█ uCORE █▐    ▌█ uSERVER █▐    ▌█ uSCRIPT █▐      │
│  SYSTEM CORE    WEB SERVICES     AUTOMATION         │
│                                                     │
│  ▌█ WIZARD █▐   ▌█ SORCERER █▐   ▌█ IMP █▐          │
│  DEVELOPMENT    ADMIN TOOLS      SCRIPTING          │
│                                                     │
│  ▌█ uKNOWLEDGE █▐ ▌█ TEMPLATES █▐ ▌█ TERMINAL █▐   │
│  DOCUMENTATION  GENERATORS       COMMAND LINE       │
│                                                     │
│  > [COMMAND INPUT]_                                 │
│                                                     │
│  Status: System Online | Time: 15:30 | Mode: Mode7 │
└─────────────────────────────────────────────────────┘
```

### BBC Mode 7 Color Palette
Following authentic SAA5050 teletext standard:
- **Black** (#000000) - Text and backgrounds
- **Red** (#ff0000) - Admin and critical functions  
- **Green** (#00ff00) - System and core functions
- **Yellow** (#ffff00) - Warnings and highlights
- **Blue** (#0000ff) - Information and web services
- **Magenta** (#ff00ff) - Special functions and automation
- **Cyan** (#00ffff) - Utilities and documentation
- **White** (#ffffff) - Primary text and interface

---

## Getting Started Quickly

### What's New in v1.3

#### Modular Architecture
uDOS v1.3 introduces a **complete architectural redesign**:
- **Clean Core System**: Essential shell commands only (247 lines)
- **uCode Script Library**: Complex functionality in Visual Basic-style scripts
- **Modular Design**: Perfect separation of concerns and expandability
- **Zero Empty Directories**: Streamlined, focused structure

#### Complete uCode Script Library
**9 comprehensive modules** written in Visual Basic syntax:
- **MEMORY.ucode**: Memory file management with search, create, stats
- **MISSION.ucode**: Mission creation, tracking, completion system
- **PACKAGE.ucode**: Package install, remove, search, update management
- **LOG.ucode**: Advanced logging, analysis, export, cleanup
- **DEV.ucode**: Development tools (testing, build, deploy, debug, profiling)
- **RENDER.ucode**: Visual rendering, ASCII art, charts, animations, UI
- **DASH.ucode**: Live dashboard and system monitoring
- **PANEL.ucode**: Interactive control panels
- **TREE.ucode**: Repository structure generation and visualization

#### Enhanced Command System
**Dual command interface** with intelligent routing:
```
[COMMAND|ACTION]     # Shortcode format for quick actions
COMMAND [args]       # Full command format for detailed control
```

#### Clean System Architecture
- **uCORE**: Cleaned up core system with empty directories removed
- **uSCRIPT**: Modular script library with Visual Basic-style uCode
- **Smart Routing**: Core shell intelligently routes to appropriate uCode scripts
- **Minimal Footprint**: Essential functionality only in core shell

---

## Getting Started

### * First Time Setup

When you start uDOS v1.3, the system automatically:

1. **Initializes modular architecture** with clean core shell
2. **Loads uCode script library** with Visual Basic-style modules
3. **Sets up intelligent command routing** between core and scripts
4. **Provides dual interface** for both shortcode and full commands

### [ ] Basic Commands

```ascii
┌─── CORE SYSTEM COMMANDS ───────────────────────────┐
│                                                     │
│  STATUS       [ ] System overview and health        │
│  HELP         [ ] Complete command reference        │
│  EXIT         [ ] Clean system shutdown             │
│  RESTART      [ ] Restart uDOS session              │
│  RESIZE       [ ] Terminal size optimizer           │
│                                                     │
└─────────────────────────────────────────────────────┘

┌─── uCODE SCRIPT COMMANDS ──────────────────────────┐
│                                                     │
│  [DASH|LIVE]      * Live dashboard system           │
│  [PANEL|DASH]     [ ] Interactive control panels    │
│  [TREE|GENERATE]  * Repository structure tools      │
│  [MEM|LIST]       * Memory file management          │
│  [MISSION|CREATE] * Mission tracking system         │
│  [PACK|LIST]      * Package management tools        │
│  [LOG|REPORT]     * Advanced logging system         │
│  [DEV|TEST]       * Development tools (wizard)      │
│  [RENDER|ART]     (Art) Visual rendering & ASCII art│
│                                                     │
└─────────────────────────────────────────────────────┘
```

### Modular Architecture

uDOS v1.3 features a revolutionary modular design:

#### Core Shell (`ucode-modular.sh`)
- **247 lines** of essential system functionality
- **Smart routing** to uCode scripts
- **Dual command interface** (shortcode + full commands)
- **Clean, minimal design** with zero bloat

#### uCode Script Library
Located in `/uSCRIPT/library/ucode/` with **Visual Basic syntax**:

| Script | Purpose | Key Features |
|--------|---------|--------------|
| `MEMORY.ucode` | Memory management | File operations, search, statistics |
| `MISSION.ucode` | Task tracking | Create, track, complete missions |
| `PACKAGE.ucode` | Package management | Install, remove, search, update |
| `LOG.ucode` | Logging system | Analysis, export, cleanup, reports |
| `DEV.ucode` | Development tools | Test, build, deploy, debug, profile |
| `RENDER.ucode` | Visual system | ASCII art, charts, animations, UI |
| `DASH.ucode` | Dashboard | Live monitoring, system status |
| `PANEL.ucode` | Control panels | Interactive system controls |
| `TREE.ucode` | Structure tools | Repository visualization |

#### Command Examples
```bash
# Shortcode format - quick actions
[MEM|LIST]           # List memory files
[MISSION|CREATE]     # Create new mission
[RENDER|ART]         # Show ASCII art gallery

# Full command format - detailed control
MEMORY search "keyword"          # Search memory files
MISSION track project-alpha      # Track specific mission
RENDER chart bar data.json       # Create bar chart from data
```

---

## System Architecture

### (M) Core Components

#### uCORE - Clean Core System
```
uCORE/
├── code/
│   ├── ucode-modular.sh     # Main system shell (247 lines)
│   ├── smart-input.sh       # Input processing
│   ├── setup.sh            # System initialization
│   └── destroy.sh          # Clean shutdown
├── datasets/               # JSON configuration data
├── templates/              # System templates
└── launcher/              # System launchers
```

#### uSCRIPT - Script Library
```
uSCRIPT/library/ucode/
├── MEMORY.ucode           # Memory file management
├── MISSION.ucode          # Mission tracking system
├── PACKAGE.ucode          # Package management
├── LOG.ucode             # Advanced logging
├── DEV.ucode             # Development tools
├── RENDER.ucode          # Visual rendering
├── DASH.ucode            # Live dashboard
├── PANEL.ucode           # Control panels
└── TREE.ucode            # Structure visualization
```

### * Command Flow

1. **User Input** → Core Shell (`ucode-modular.sh`)
2. **Command Parsing** → Identify core vs. script command
3. **Smart Routing** → Execute locally or route to uCode script
4. **Script Execution** → Visual Basic-style uCode interpreter
5. **Result Display** → Formatted output to user

### [ ] Visual Basic uCode Syntax

All uCode scripts use consistent Visual Basic syntax:

```vb
FUNCTION Main(args AS STRING) AS INTEGER
    DIM command AS STRING = "help"
    
    IF args <> "" THEN
        command = args
    END IF
    
    SELECT CASE LCASE(command)
        CASE "create"
            RETURN CreateMemoryFile()
        CASE "list"
            RETURN ListMemoryFiles()
        CASE ELSE
            PRINT "Unknown command"
            RETURN 1
    END SELECT
END FUNCTION
```

---

## Development System

### * DEV Command - Development Tools

The DEV command provides comprehensive development tools (Wizard installations only):

```bash
# Testing system
DEV test [suite]        # Run test suites (core, script, memory, etc.)
DEV test core          # Run core system tests

# Building system
DEV build [target]     # Build system components
DEV build all          # Complete system build

# Deployment
DEV deploy [env]       # Deploy to environment
DEV deploy staging     # Deploy to staging environment

# Debugging
DEV debug [component]  # Debug system components
DEV debug memory       # Debug memory system

# Performance
DEV profile [duration] # Performance profiling
DEV profile 120        # Profile for 2 minutes

# System validation
DEV validate [comp]    # Validate system integrity
DEV backup [type]      # Backup system data
DEV restore [backup]   # Restore from backup
```

### (Art) RENDER Command - Visual System

The RENDER command provides advanced visual capabilities:

```bash
# ASCII Art
RENDER art [name]           # Display ASCII art
RENDER gallery              # Browse art gallery

# Text Formatting
RENDER text "Hello" banner  # Create banner text
RENDER text "Info" box      # Text in decorative box

# Charts and Graphs
RENDER chart bar data.json  # Bar chart from data
RENDER chart line metrics   # Line graph
RENDER chart pie usage      # Pie chart

# User Interfaces
RENDER ui dashboard         # System dashboard
RENDER ui menu             # Interactive menu

# Animations
RENDER animation loading    # Play loading animation
RENDER progress 75 100     # 75% progress bar
```

---

## ASSIST Mode Enhancement

### (M) AI-Powered Task Management

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

### [ ] v1.3 Modular Dashboard

The dashboard now reflects the modular architecture:

```ascii
┌─── uDOS v1.3 MODULAR DASHBOARD ────────────────────┐
│                                                     │
│  *  Architecture: Modular    [ ] Date: 2025-08-17   │
│  (M) Core: 247 lines         [ ] Uptime: 2h 34m     │
│                                                     │
│  [ ] System Components        * uCode Scripts        │
│  ══════════════════           ═══════════════        │
│  Core Shell    [x]            MEMORY.ucode   [x]     │
│  uSCRIPT       [x]            MISSION.ucode  [x]     │
│  uMEMORY       [x]            PACKAGE.ucode  [x]     │
│  Routing       [x]            LOG.ucode      [x]     │
│                              DEV.ucode      [x]      │
│                              RENDER.ucode   [x]      │
│  [ ] Performance Stats        * Command Usage         │
│  ═══════════════════          ═══════════════         │
│  Core Efficiency: 98%         Shortcodes: 67%        │
│  Script Load: <1ms            Full Commands: 33%     │
│  Memory Usage: 12MB           Most Used: [MEM|LIST]  │
│                                                     │
└─────────────────────────────────────────────────────┘
```

### * Dashboard Commands
```bash
DASH                    # Main modular dashboard
DASH ARCHITECTURE       # Architecture overview
DASH PERFORMANCE        # Performance metrics
DASH SCRIPTS           # uCode script status
DASH USAGE             # Command usage statistics
```

---

## Memory & Mission Management

### (M) MEMORY Command System

The MEMORY command provides comprehensive file management:

```bash
# File Management
MEMORY create "filename" "description"    # Create memory file
MEMORY search "keyword"                   # Search memory files
MEMORY list [filter]                     # List files with optional filter
MEMORY stats                             # Show memory statistics

# Organization
MEMORY organize                          # Auto-organize files
MEMORY cleanup                           # Clean temporary files
MEMORY backup                            # Backup memory system
MEMORY restore "backup-name"             # Restore from backup

# Shortcode Examples
[MEM|LIST]              # Quick file listing
[MEM|SEARCH] keyword    # Quick search
[MEM|STATS]             # Quick statistics
```

### * MISSION Command System

The MISSION command handles task and project tracking:

```bash
# Mission Management
MISSION create "title" "description"     # Create new mission
MISSION list [status]                    # List missions by status
MISSION track "mission-id"               # Track mission progress
MISSION complete "mission-id"            # Mark mission complete

# Mission Operations
MISSION update "mission-id" "progress"   # Update mission progress
MISSION assign "mission-id" "assignee"   # Assign mission to user
MISSION archive "mission-id"             # Archive completed mission
MISSION report                           # Generate mission report

# Shortcode Examples
[MISSION|CREATE] "Task title"    # Quick mission creation
[MISSION|LIST]                   # Quick mission listing
[MISSION|TRACK] mission-123      # Quick mission tracking
```

---

## Command Reference

### * Core System Commands

| Command | Description | Example |
|---------|-------------|---------|
| `STATUS` | System overview and health | `STATUS` |
| `HELP` | Complete command reference | `HELP` |
| `EXIT` | Clean system shutdown | `EXIT` |
| `RESTART` | Restart uDOS session | `RESTART` |
| `RESIZE` | Terminal size optimizer | `RESIZE` |

### * uCode Script Commands

| Command | Script | Description | Example |
|---------|--------|-------------|---------|
| `MEMORY` | MEMORY.ucode | File management | `MEMORY search "keyword"` |
| `MISSION` | MISSION.ucode | Task tracking | `MISSION create "title"` |
| `PACKAGE` | PACKAGE.ucode | Package management | `PACKAGE install "name"` |
| `LOG` | LOG.ucode | Advanced logging | `LOG analyze today` |
| `DEV` | DEV.ucode | Development tools | `DEV test core` |
| `RENDER` | RENDER.ucode | Visual rendering | `RENDER art dragon` |
| `DASH` | DASH.ucode | Live dashboard | `DASH performance` |
| `PANEL` | PANEL.ucode | Control panels | `PANEL system` |
| `TREE` | TREE.ucode | Structure tools | `TREE generate` |

### [ ] Shortcode Commands

| Shortcode | Full Command | Description |
|-----------|--------------|-------------|
| `[MEM\|LIST]` | `MEMORY list` | List memory files |
| `[MISSION\|CREATE]` | `MISSION create` | Create new mission |
| `[PACK\|INSTALL]` | `PACKAGE install` | Install package |
| `[LOG\|REPORT]` | `LOG report` | Generate log report |
| `[DEV\|TEST]` | `DEV test` | Run development tests |
| `[RENDER\|ART]` | `RENDER art` | Display ASCII art |
| `[DASH\|LIVE]` | `DASH live` | Live dashboard |
| `[PANEL\|SYSTEM]` | `PANEL system` | System control panel |
| `[TREE\|GENERATE]` | `TREE generate` | Generate structure |

---

## Advanced Features

### * Development Tools (DEV Command)

#### Comprehensive Testing System
```bash
# Test Suites
DEV test core           # Core system tests
DEV test script         # uScript engine tests  
DEV test memory         # Memory system tests
DEV test security       # Security validation tests

# Build System
DEV build all           # Complete system build
DEV build core          # Core components only
DEV build scripts       # Script libraries
DEV build docs          # Documentation generation

# Deployment Pipeline
DEV deploy development  # Local development environment
DEV deploy staging      # Pre-production testing
DEV deploy production   # Live production system
```

#### Performance Analysis
```bash
# System Profiling
DEV profile 60          # Profile for 1 minute
DEV profile 300         # Profile for 5 minutes

# Validation & Health
DEV validate core       # Validate core system
DEV validate scripts    # Validate all uCode scripts
DEV backup system       # Backup entire system
DEV restore latest      # Restore from latest backup
```

### (Art) Visual Rendering System (RENDER Command)

#### ASCII Art & Graphics
```bash
# Art Gallery
RENDER gallery          # Browse available ASCII art
RENDER art dragon       # Display specific art piece
RENDER logo uDOS        # Show uDOS logo variants

# Text Formatting
RENDER text "Hello World" banner    # Banner-style text
RENDER text "Warning" box          # Text in decorative box
RENDER text "Info" center          # Centered text formatting
```

#### Charts & Data Visualization
```bash
# Chart Generation
RENDER chart bar sales.json        # Bar chart from data
RENDER chart line performance.csv  # Line graph
RENDER chart pie usage-stats       # Pie chart visualization
RENDER chart timeline project      # Project timeline

# Interactive Elements
RENDER ui dashboard                # System dashboard
RENDER ui menu navigation         # Navigation menu
RENDER progress 75 100            # Progress indicator
RENDER table system-status        # Data table display
```

### [ ] Monitoring & Analytics

#### System Health Monitoring
- **Modular Architecture**: Track core shell and uCode script performance
- **Command Usage**: Monitor shortcode vs. full command usage patterns
- **Script Performance**: Analyze uCode script execution times
- **Memory Efficiency**: Track system resource utilization

#### Development Analytics
- **Script Development**: Monitor uCode script creation and modification
- **Testing Metrics**: Track test suite execution and success rates
- **Deployment History**: Monitor system deployment frequency and success
- **Performance Trends**: Analyze system performance over time

---

## Troubleshooting

### * Common Issues v1.3

#### uCode Script Execution Problems
```
❌ uCode script execution failed
✅ Solution: Check script exists in /uSCRIPT/library/ucode/
✅ Solution: Verify Visual Basic syntax in script file
✅ Solution: Use DEV validate scripts command
```

#### Command Routing Issues
```
❌ Command not recognized by core shell
✅ Solution: Check if command should route to uCode script
✅ Solution: Use HELP command to see available commands
✅ Solution: Try shortcode format [COMMAND|ACTION]
```

#### Core System Performance
```
❌ System responding slowly
✅ Solution: Use DEV profile command to analyze performance
✅ Solution: Check core shell with STATUS command
✅ Solution: Restart system with RESTART command
```

#### Development Mode Access
```
❌ Cannot access DEV commands
✅ Solution: Ensure wizard user permissions are configured
✅ Solution: Verify DEV.ucode script exists and is executable
✅ Solution: Check system architecture with DASH architecture
```

### * Diagnostic Commands

```bash
STATUS                      # Core system overview
HELP                       # Complete command reference
DASH architecture          # Modular architecture status
DEV validate system        # Full system validation
RENDER art gallery         # Test visual rendering system
[MEM|STATS]               # Memory system diagnostics
[LOG|REPORT]              # System log analysis
```

---

## Best Practices

### * Modular Architecture
1. **Use shortcode commands** for quick daily tasks
2. **Use full commands** for detailed operations with specific parameters
3. **Leverage uCode scripts** for complex functionality instead of extending core shell
4. **Monitor system performance** with DEV profile and DASH commands

### * Memory & Mission Management
1. **Create descriptive missions** with clear objectives and timelines
2. **Use memory search** to quickly locate files and information
3. **Organize missions** by status and priority for better tracking
4. **Regular cleanup** of completed missions and temporary files

### (Art) Visual System Usage
1. **Use RENDER gallery** to explore available ASCII art
2. **Create custom charts** with your data for better visualization
3. **Use progress bars** for long-running operations
4. **Design interactive UIs** for complex system operations

### * Development Workflow
1. **Start with DEV validate** before making system changes
2. **Use comprehensive testing** with DEV test before deployment
3. **Profile performance** regularly with DEV profile
4. **Document changes** using LOG command for traceability

---

## uCode Script Library

### * Visual Basic Style Scripts

uDOS v1.3 features a complete library of Visual Basic-style uCode scripts:

#### Core Management Scripts
- **MEMORY.ucode**: Advanced memory file management with search, statistics, and organization
- **MISSION.ucode**: Comprehensive mission tracking with creation, progress monitoring, and completion
- **PACKAGE.ucode**: Full package management system with install, remove, search, and update capabilities
- **LOG.ucode**: Advanced logging system with analysis, export, cleanup, and reporting features

#### Development & Visualization Scripts  
- **DEV.ucode**: Complete development toolkit with testing, building, deployment, debugging, and profiling
- **RENDER.ucode**: Visual rendering system with ASCII art, charts, animations, and UI generation
- **DASH.ucode**: Live dashboard system with real-time monitoring and system status
- **PANEL.ucode**: Interactive control panels for system management
- **TREE.ucode**: Repository structure generation and visualization tools

### * Script Architecture

Each uCode script follows consistent Visual Basic syntax patterns:

```vb
' Standard uCode script structure
FUNCTION Main(args AS STRING) AS INTEGER
    ' Parse command arguments
    DIM command AS STRING = "help"
    
    IF args <> "" THEN
        command = ExtractCommand(args)
    END IF
    
    ' Execute command logic
    SELECT CASE LCASE(command)
        CASE "create"
            RETURN HandleCreate(args)
        CASE "list"
            RETURN HandleList(args)
        CASE "help"
            RETURN ShowHelp()
        CASE ELSE
            PRINT "* Unknown command: " + command
            RETURN 1
    END SELECT
END FUNCTION
```

### [ ] Script Execution Flow

1. **Core Shell** receives user command
2. **Command Parser** determines if command routes to uCode script
3. **Script Executor** loads appropriate `.ucode` file
4. **Visual Basic Interpreter** processes script logic
5. **Formatted Output** returns results to user

### * Script Development

Future uCode scripts can be easily added to the library:

```bash
# Create new uCode script
touch /uSCRIPT/library/ucode/NEWSCRIPT.ucode

# Add routing in core shell
# Edit ucode-modular.sh to include new script routing

# Test script execution
DEV test script NEWSCRIPT
```

---

## Support & Resources

### [ ] Documentation
- **Architecture Guide**: `/docs/ARCHITECTURE.md` - Complete system architecture
- **Modular Guide**: `/docs/uDOS-Concepts-v1.3.md` - v1.3 modular concepts
- **Style Guide**: `/docs/Style-Guide.md` - Coding and documentation standards
- **VS Code Guide**: `/docs/VS-Code-Dev-Mode-Guide.md` - Development environment setup

### * Core System Tools
- **Modular Shell**: `/uCORE/code/ucode-modular.sh` - Main system shell (247 lines)
- **Smart Input**: `/uCORE/code/smart-input.sh` - Input processing system
- **System Setup**: `/uCORE/code/setup.sh` - System initialization
- **Clean Shutdown**: `/uCORE/code/destroy.sh` - Safe system termination

### * uCode Script Library
- **MEMORY.ucode**: `/uSCRIPT/library/ucode/MEMORY.ucode` - Memory management
- **MISSION.ucode**: `/uSCRIPT/library/ucode/MISSION.ucode` - Task tracking
- **PACKAGE.ucode**: `/uSCRIPT/library/ucode/PACKAGE.ucode` - Package management
- **LOG.ucode**: `/uSCRIPT/library/ucode/LOG.ucode` - Advanced logging
- **DEV.ucode**: `/uSCRIPT/library/ucode/DEV.ucode` - Development tools
- **RENDER.ucode**: `/uSCRIPT/library/ucode/RENDER.ucode` - Visual rendering

### * Community
- **GitHub Repository**: uDOS project repository with modular architecture
- **Development Discussions**: Community development forum for v1.3
- **Issue Tracking**: Bug reports and feature requests for modular system
- **Knowledge Base**: Community-contributed documentation and scripts

### * Quick Reference Commands
```bash
# System Overview
STATUS                  # Complete system health check
HELP                   # Full command reference guide

# Architecture Information  
DASH architecture      # Modular architecture overview
DEV validate system    # Comprehensive system validation

# Script Information
[MEM|STATS]           # Memory system statistics
[LOG|REPORT]          # System activity report
RENDER gallery        # Visual capabilities showcase
```


---

**Notes**

This guide is designed to be read like the early home computer manuals — direct, practical, and a little nostalgic. Explore, make mistakes, and enjoy learning uDOS.

---

**Document Status**: Production Ready - Modular Architecture v1.3  
**Version**: v1.3 Modular  
**Last Updated**: August 17, 2025  
**Next Review**: September 17, 2025

---

*uDOS v1.3 User Guide - Universal Data Operating System*  
*Modular Architecture • Visual Basic uCode Scripts • Clean Core Design*
