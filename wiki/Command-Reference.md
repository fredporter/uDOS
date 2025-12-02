# Command Reference

**Version:** v1.1.16 (Archive System Infrastructure)
**Format:** uPY (Python-like syntax)
**Last Updated:** December 3, 2025

Complete reference for all uDOS commands with uPY syntax examples.

> **💡 Quick Help**: Type `HELP` in uDOS for command list, or `HELP <command>` for specific help.

---

## 📋 Command Categories

- [System Commands](#system-commands) - Core system operations
- [File Operations](#file-operations) - File management
- [Content Generation](#content-generation) - AI-powered creation
- [Knowledge & Guides](#knowledge--guides) - Knowledge bank access
- [Missions & Workflows](#missions--workflows) - Task management
- [Graphics & Diagrams](#graphics--diagrams) - Visual content
- [Scripts & Adventures](#scripts--adventures) - Interactive content
- [Variables & Data](#variables--data) - Data management
- [Extensions](#extensions) - Extension system

---

## System Commands

### HELP
Show command help and documentation.

**Syntax:**
```
HELP                    # List all commands
HELP <command>          # Command-specific help
HELP DETAILED           # Full documentation
```

**Examples:**
```upy
HELP
HELP GENERATE
HELP MISSION
```

### STATUS
Display system status and active processes.

**Syntax:**
```
STATUS                  # Overall system status
STATUS VERBOSE          # Detailed status
```

### VERSION
Show uDOS version information.

**Syntax:**
```
VERSION                 # Current version
```

### REBOOT
Restart the uDOS system.

**Syntax:**
```
REBOOT                  # Restart system
```

**⚠️ Warning:** Saves all state before restarting.

### CLEAR
Clear the terminal screen.

**Syntax:**
```
CLEAR                   # Clear screen
```

### CONFIG
View or modify system configuration.

**Syntax:**
```
CONFIG                  # Show all settings
CONFIG <key>            # Show specific setting
CONFIG <key> <value>    # Update setting
```

**Examples:**
```upy
CONFIG                      # View all
CONFIG theme galaxy         # Set theme
CONFIG username "Fred"      # Set username
```

### SETTINGS
Alias for CONFIG command.

---

## File Operations

### LIST
List directory contents.

**Syntax:**
```
LIST [path]             # List directory
LS [path]               # Alias
```

**Examples:**
```upy
LIST                    # Current directory
LIST knowledge/water    # Specific path
LS memory/missions      # Using alias
```

### SHOW
Display file contents.

**Syntax:**
```
SHOW <file>             # Display file
CAT <file>              # Alias
VIEW <file>             # Alias
```

**Examples:**
```upy
SHOW knowledge/water/boiling.md
CAT memory/missions/water-setup.json
```

### EDIT
Open file in micro editor.

**Syntax:**
```
EDIT <file>             # Edit file
EDIT <file> <line>      # Edit at line number
```

**Examples:**
```upy
EDIT README.md
EDIT core/config.py 45
```

### NEW
Create new file.

**Syntax:**
```
NEW <file>              # Create empty file
NEW <file> <content>    # Create with content
```

**Examples:**
```upy
NEW memory/notes.md
NEW test.upy "PRINT('Hello world')"
```

### DELETE
Delete file or directory.

**Syntax:**
```
DELETE <path>           # Delete file/directory
RM <path>               # Alias
```

**⚠️ Warning:** Permanent deletion, use carefully.

### COPY
Copy file or directory.

**Syntax:**
```
COPY <source> <dest>    # Copy file
CP <source> <dest>      # Alias
```

### MOVE
Move or rename file/directory.

**Syntax:**
```
MOVE <source> <dest>    # Move/rename
MV <source> <dest>      # Alias
```

### RUN
Execute uPY script file.

**Syntax:**
```
RUN <script.upy>        # Execute script
```

**Examples:**
```upy
RUN memory/tests/shakedown.upy
RUN workflows/water-purification.upy
```

**Note:** Use `.upy` extension (Python-like format), not `.uscript`

---

## Content Generation

### GENERATE
Unified AI content generation system (Nano Banana pipeline).

**Syntax:**
```
GENERATE SVG <description>                          # Generate PNG→SVG diagram
GENERATE SVG --survival <category>/<prompt> [opts]  # Use survival templates
GENERATE ASCII <type> <content> [width] [height]    # Generate ASCII art
GENERATE --survival-help                            # Show survival prompts
```

**SVG Options:**
- `--pro` - Professional style (clean, technical)
- `--strict` - Strict compliance mode
- `--refined` - Refined aesthetic

**SVG Examples:**
```upy
# General SVG generation
GENERATE SVG water purification flowchart
GENERATE SVG shelter building sequence

# Survival templates (optimized prompts)
GENERATE SVG --survival water/purification_flow --pro
GENERATE SVG --survival fire/methods_comparison --strict
GENERATE SVG --survival shelter/types_hierarchy --refined

# List available survival prompts
GENERATE --survival-help
```

**ASCII Types:**
- `box` - Box with title
- `panel` - Info panel
- `table` - Data table
- `flowchart` - Simple flowchart
- `progress` - Progress bar
- `list` - Bulleted list
- `banner` - Large banner text
- `tree` - Tree structure

**ASCII Examples:**
```upy
GENERATE ASCII box "Water Sources" 40 5
GENERATE ASCII table "Method,Time,Difficulty" "Friction,10min,Hard;Flint,2min,Easy"
GENERATE ASCII progress "Purification" 75 30
```

**Output:**
- SVG: `memory/drafts/svg/`
- ASCII: Terminal + save option

### MERMAID
Create Mermaid.js diagrams (flowcharts, sequence, gantt, etc.).

**Syntax:**
```
MERMAID CREATE <type>               # Interactive creation
MERMAID RENDER <file.mmd>           # Render diagram
MERMAID LIST                        # Show supported types
MERMAID EXAMPLES                    # Show examples
```

**Supported Types:**
- `flowchart` - Flowchart diagrams
- `sequence` - Sequence diagrams
- `gantt` - Gantt charts
- `class` - Class diagrams
- `state` - State machines
- `pie` - Pie charts
- `gitgraph` - Git graphs
- `mindmap` - Mind maps
- `timeline` - Timelines
- `quadrant` - Quadrant charts

**Examples:**
```upy
MERMAID CREATE flowchart
MERMAID RENDER memory/diagrams/process.mmd
MERMAID LIST
```

### GEOJSON / GEODIAGRAM
Create geographic maps (GeoJSON format for GitHub).

**Syntax:**
```
GEOJSON CREATE <type>               # Create map
GEOJSON POINT <name> <lat> <lon>    # Add point
GEOJSON LINE <name> <coords>        # Add line
GEOJSON POLY <name> <coords>        # Add polygon
```

**Examples:**
```upy
GEOJSON CREATE point "Water Source" -33.87 151.21
GEOJSON CREATE line "Trail Route" "[[-33.87,151.21],[-33.88,151.22]]"
```

### STL
Create 3D models in ASCII STL format (for GitHub 3D viewer).

**Syntax:**
```
STL CREATE <type>                   # Create 3D model
STL EXAMPLES                        # Show examples
```

### TYPORA
Enhanced diagram support for Typora editor (13 diagram types).

**Syntax:**
```
TYPORA LIST                         # Show supported types
TYPORA CREATE <type>                # Create diagram
TYPORA HELP                         # Integration guide
```

---

## Knowledge & Guides

### GUIDE
Interactive knowledge guide system with progress tracking.

**Syntax:**
```
GUIDE LIST [category]               # List guides
GUIDE SHOW <guide>                  # Display guide
GUIDE START <guide>                 # Interactive mode
GUIDE PROGRESS                      # Show progress
GUIDE SEARCH <query>                # Search guides
```

**Categories:**
- `water` - Water purification & storage
- `fire` - Fire starting & management
- `shelter` - Shelter building
- `food` - Food & foraging
- `navigation` - Navigation & wayfinding
- `medical` - First aid & health

**Examples:**
```upy
GUIDE LIST water
GUIDE SHOW water/boiling
GUIDE START water/purification
GUIDE SEARCH "emergency"
```

### DIAGRAM
Browse ASCII diagram library.

**Syntax:**
```
DIAGRAM LIST [type]                 # List diagrams
DIAGRAM SEARCH <query>              # Search diagrams
DIAGRAM SHOW <name>                 # Display diagram
DIAGRAM TYPES                       # Show categories
DIAGRAM EXPORT <name> <file>        # Save to file
```

**Examples:**
```upy
DIAGRAM LIST
DIAGRAM SEARCH water
DIAGRAM SHOW water_filter
DIAGRAM TYPES
```

### CHECKLIST
Task checklist management.

**Syntax:**
```
CHECKLIST LIST                      # List all checklists
CHECKLIST LOAD <id>                 # Load checklist
CHECKLIST SHOW                      # Show current
CHECKLIST COMPLETE <item>           # Mark complete
CHECKLIST PROGRESS                  # Show stats
CHECKLIST RESET                     # Reset progress
```

**Examples:**
```upy
CHECKLIST LIST
CHECKLIST LOAD emergency/72-hour-kit
CHECKLIST COMPLETE "Water bottles"
CHECKLIST PROGRESS
```

---

## Missions & Workflows

### MISSION
Mission management and execution.

**Syntax:**
```
MISSION CREATE <id> <title>         # Create mission
MISSION START <id>                  # Start mission
MISSION STATUS                      # Show status
MISSION COMPLETE <id>               # Mark complete
MISSION LIST                        # List missions
MISSION ABORT <id>                  # Abort mission
```

**Examples:**
```upy
MISSION CREATE water-purify "Water Purification Setup"
MISSION START water-purify
MISSION STATUS
MISSION COMPLETE water-purify
```

### WORKFLOW
Workflow automation (.upy scripts).

**Syntax:**
```
WORKFLOW RUN <script.upy>           # Execute workflow
WORKFLOW LIST                       # List workflows
WORKFLOW STATUS                     # Show execution state
```

**Examples:**
```upy
WORKFLOW RUN memory/workflows/missions/water-setup.upy
WORKFLOW STATUS
```

### ARCHIVE
Archive completed work.

**Syntax:**
```
ARCHIVE LIST [type]                 # List archived items
ARCHIVE mission <id>                # Archive mission
ARCHIVE checklist <id>              # Archive checklist
ARCHIVE workflow <id>               # Archive workflow
ARCHIVE restore <type> <id>         # Restore item
```

**Examples:**
```upy
ARCHIVE LIST mission
ARCHIVE mission water-purify
ARCHIVE restore mission water-purify
```

---

## Graphics & Diagrams

### DRAW
Generate ASCII/Teletext graphics (offline).

**Syntax:**
```
DRAW <type> <params>                # Generate graphic
```

**Examples:**
```upy
DRAW box "Title" 40 5
DRAW banner "WARNING"
```

### PANEL
Teletext-style UI panels.

**Syntax:**
```
PANEL <name>                        # Show panel
PANEL LIST                          # List panels
```

---

## Scripts & Adventures

### STORY
Interactive adventure system (uPY powered).

**Syntax:**
```
STORY START <adventure>             # Start adventure
STORY CONTINUE                      # Continue story
STORY CHOICE <number>               # Make choice
STORY STATUS                        # Check progress
STORY SAVE <name>                   # Save game
STORY LOAD <name>                   # Load game
```

**Examples:**
```upy
STORY START survival_intro
STORY CHOICE 1
STORY SAVE "day1"
```

---

## Variables & Data

### GET
Get system variable value.

**Syntax:**
```
GET <variable>                      # Get value
GET MISSION.<field>                 # Mission variables
GET CHECKLIST.<field>               # Checklist variables
GET WORKFLOW.<field>                # Workflow variables
```

**Mission Variables:**
- `MISSION.ID` - Current mission ID
- `MISSION.NAME` - Mission name
- `MISSION.STATUS` - Status (ACTIVE|PAUSED|COMPLETE)
- `MISSION.PROGRESS` - Progress metrics
- `MISSION.START_TIME` - Start timestamp

**Checklist Variables:**
- `CHECKLIST.ACTIVE` - Active checklist count
- `CHECKLIST.PROGRESS_PCT` - Completion percentage
- `CHECKLIST.COMPLETED` - Completed items
- `CHECKLIST.TOTAL` - Total items

**Workflow Variables:**
- `WORKFLOW.NAME` - Workflow name
- `WORKFLOW.PHASE` - Execution phase
- `WORKFLOW.ITERATION` - Loop iteration
- `WORKFLOW.ERRORS` - Error count
- `WORKFLOW.ELAPSED_TIME` - Runtime seconds

**Examples:**
```upy
GET MISSION.STATUS
GET CHECKLIST.PROGRESS_PCT
GET WORKFLOW.PHASE
```

### SET
Set system variable value.

**Syntax:**
```
SET <variable> <value>              # Set value
```

**Examples:**
```upy
SET theme galaxy
SET username "Fred"
```

---

## Extensions

### POKE
Extension and server management.

**Syntax:**
```
POKE LIST                           # List servers
POKE START <extension>              # Start server
POKE STOP <extension>               # Stop server
POKE STATUS                         # Show status
POKE RESTART <extension>            # Restart server
```

**Examples:**
```upy
POKE LIST
POKE START dashboard
POKE STOP teletext
POKE STATUS
```

### EXTENSION
Extension system management.

**Syntax:**
```
EXTENSION LIST                      # List extensions
EXTENSION INFO <name>               # Extension details
EXTENSION ENABLE <name>             # Enable extension
EXTENSION DISABLE <name>            # Disable extension
```

**Examples:**
```upy
EXTENSION LIST
EXTENSION INFO typora-diagrams
```

---

## Utility Commands

### TREE
Display directory structure.

**Syntax:**
```
TREE [path] [depth]                 # Show tree
```

**Examples:**
```upy
TREE                                # Current dir
TREE knowledge 2                    # 2 levels deep
```

### CLEAN
Clean workspace and manage archive system.

**Syntax:**
```
CLEAN                               # Clean workspace (review mode)
CLEAN --scan                        # Scan all .archive/ folders
CLEAN --purge [days]                # Purge old files (default: 30 days)
CLEAN --dry-run                     # Preview deletions
CLEAN --path <dir>                  # Target specific directory
```

**Examples:**
```upy
CLEAN                               # Review sandbox files
CLEAN --scan                        # Health check on archives
CLEAN --purge 7                     # Remove files older than 7 days
CLEAN --purge --dry-run             # Preview what would be deleted
```

**v1.1.16:** Enhanced with archive system health metrics and retention-based cleanup.

### TIDY
Organize workspace files.

**Syntax:**
```
TIDY                                # Tidy workspace
TIDY --report                       # Show report
```

### BACKUP
Create and manage file backups in .archive/ folders.

**Syntax:**
```
BACKUP <file>                       # Create timestamped backup
BACKUP <file> --to <path>           # Backup to specific archive
BACKUP LIST [file]                  # List backups
BACKUP RESTORE <backup>             # Restore backup
BACKUP RESTORE <backup> --to <path> # Restore to custom location
BACKUP CLEAN [days]                 # Purge old backups (default: 30)
BACKUP CLEAN --dry-run              # Preview cleanup
BACKUP HELP                         # Show help
```

**Examples:**
```upy
BACKUP config.json                  # Create backup
BACKUP LIST config.json             # List all config.json backups
BACKUP RESTORE 20251203_120000_config.json
BACKUP CLEAN 7                      # Remove backups older than 7 days
```

**v1.1.16:** New command for file backup lifecycle management.

### UNDO / REDO
Revert files to previous versions using version history.

**Syntax:**
```
UNDO <file>                         # Revert to previous version
UNDO --list <file>                  # List version history
UNDO --to-version <version> <file>  # Revert to specific version
REDO <file>                         # Re-apply undone changes
```

**Examples:**
```upy
UNDO config.json                    # Undo last change
UNDO --list config.json             # See all versions
UNDO --to-version 20251203_120000_config.json config.json
REDO config.json                    # Redo after undo
```

**v1.1.16:** New commands for file version history management. Versions stored in `.archive/versions/`.

### REPAIR
System maintenance and file recovery.

**Syntax:**
```
REPAIR                              # System health check
REPAIR auto                         # Auto-repair issues
REPAIR report                       # Detailed report
REPAIR recover [file]               # Recover deleted files
```

**Examples:**
```upy
REPAIR                              # Check system health
REPAIR recover                      # List recoverable files
REPAIR recover config.json          # Restore deleted file
```

**v1.1.16:** Added `RECOVER` subcommand for soft-delete recovery from `.archive/deleted/` (7-day window).

### LOGS
View system logs.

**Syntax:**
```
LOGS                                # Recent logs
LOGS --tail                         # Follow logs
LOGS --level ERROR                  # Filter level
```

---

## uPY Script Commands

Commands for use within .upy scripts:

### PRINT
Output text (with variable substitution and emoji).

**Syntax:**
```upy
PRINT("message")                    # Simple output
PRINT("Hello $name")                # Variable substitution
PRINT(":check: Done!")              # Emoji codes
```

### FUNCTION
Define reusable functions.

**Syntax:**
```upy
FUNCTION [@NAME($PARAMS)
    # Function body
    RETURN value
]
```

**Example:**
```upy
FUNCTION [@GREET($NAME)
    PRINT("Hello, $NAME!")
    RETURN ":wave:"
]

@GREET("Fred")                      # Call function
```

### IF
Conditional execution.

**Syntax:**
```upy
# Inline conditional
IF {condition | statement}

# Block conditional
IF condition THEN
    statements
ELSE
    statements
ENDIF
```

**Example:**
```upy
IF {$HP < 20 | PRINT(":warning: Low health!")}

IF $SCORE > 100 THEN
    PRINT(":trophy: You win!")
ELSE
    PRINT("Keep trying!")
ENDIF
```

### JSON
JSON data operations.

**Syntax:**
```upy
JSON.load("file.json")              # Load JSON
JSON.save("file.json")              # Save JSON
player.stats.health = 100           # Dot notation
player.inventory.append("sword")    # Array operations
```

---

## Deprecated Commands

These commands have been removed or replaced:

### ❌ DIAGRAM GENERATE
**Removed in:** v1.1.15
**Use instead:** `GENERATE SVG --survival <category>/<prompt>`

### ❌ SVG
**Removed in:** v1.1.5.3
**Use instead:** `GENERATE SVG <description>`

### ❌ KB
**Removed in:** v2.0.0
**Use instead:** `GUIDE` command

### ❌ GRID
**Removed in:** v1.0.32
**Use instead:** `TREE`, `PANEL`, file commands

### ❌ .uscript format
**Replaced by:** `.upy` format (Python-like syntax)
**Migration:** See [uPY Quick Start](Tutorial-uPY-Quick-Start)

---

## Quick Tips

**Finding Commands:**
```upy
HELP                                # All commands
GUIDE SEARCH <topic>                # Search knowledge
DIAGRAM SEARCH <query>              # Search diagrams
```

**Common Workflows:**
```upy
# Generate diagram
GENERATE SVG --survival water/purification_flow --pro

# Start mission
MISSION CREATE water "Water Setup"
MISSION START water

# Run workflow
WORKFLOW RUN memory/workflows/missions/water-setup.upy

# Check progress
GET MISSION.PROGRESS
GET CHECKLIST.PROGRESS_PCT
```

**File Management:**
```upy
LIST memory/missions                # Browse
SHOW mission.json                   # View
EDIT mission.json                   # Edit
RUN script.upy                      # Execute
```

---

## See Also

- [uPY Quick Start](Tutorial-uPY-Quick-Start) - Learn uPY syntax
- [uPY Cheat Sheet](uPY-Cheat-Sheet) - Quick reference
- [Getting Started](Getting-Started) - Complete beginner guide
- [Nano Banana Integration](Nano-Banana-Integration) - AI diagram generation
- [Graphics System](Graphics-System) - Visual content creation

---

**Last Updated:** December 3, 2025
**Version:** v1.1.15 (Graphics Infrastructure Complete)
