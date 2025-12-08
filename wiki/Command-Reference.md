# Command Reference

**Version:** v1.2.20 (Workflow Management System)
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

### OK - AI Assistant (v1.2.21) ✨

**NEW in v1.2.21** - AI-powered workflow generation, code assistance, and content creation with context awareness.

**Access**: Press **O** key to open interactive panel, or use commands directly.

**Commands:**
```
OK MAKE WORKFLOW <description>      # Generate uPY workflow script
OK MAKE SVG <description>           # Generate SVG graphics with AI
OK MAKE DOC <file|topic>            # Generate documentation (markdown)
OK MAKE TEST <file|function>        # Generate unit tests (pytest)
OK MAKE MISSION <description>       # Generate mission script
OK ASK <question>                   # Ask AI assistant anything
OK CLEAR                            # Clear conversation history
OK STATUS                           # Show usage statistics and config
```

**Features**:
- **Context-Aware**: Tracks workspace state, TILE location, recent commands, git status
- **Quick Prompts**: O-key panel with 8 instant access options
- **Conversation History**: Last 10 AI interactions with timestamps
- **Smart Output**: Auto-saves to appropriate directories (workflows/, drafts/svg/, docs/, tests/)
- **Code Extraction**: Automatically extracts code blocks from AI responses
- **Usage Tracking**: Cost estimates, token counts, request statistics

**Examples:**
```upy
# Workflow generation
OK MAKE WORKFLOW "backup system files to archive"
OK MAKE WORKFLOW "scan knowledge base for missing files"

# SVG graphics
OK MAKE SVG "water filtration system diagram"
OK MAKE SVG "shelter building steps flowchart"

# Documentation
OK MAKE DOC core/commands/ok_handler.py
OK MAKE DOC "grid system architecture"

# Unit tests
OK MAKE TEST core/services/ok_context_manager.py
OK MAKE TEST "test_load_knowledge function"

# Mission scripts
OK MAKE MISSION "establish camp and secure water source"

# General questions
OK ASK "how do I optimize this function for performance?"
OK ASK "explain the difference between TILE codes and coordinates"
OK ASK "what's the best way to structure a workflow script?"

# Management
OK STATUS     # Show usage stats, config, history count
OK CLEAR      # Clear conversation history
```

**Configuration**: Access via CONFIG panel → [OK] tab:
- `ok_model` - AI model (gemini-2.0-flash-exp, gemini-1.5-pro, gemini-1.5-flash, gemini-1.0-pro)
- `ok_temperature` - Creativity (0.0-2.0, default 0.7)
- `ok_max_tokens` - Response length (100-100000, default 2048)
- `ok_cost_tracking` - Enable/disable cost tracking
- `ok_context_length` - Command history (1-20, default 5)

**Output Directories**:
- Workflows → `memory/workflows/missions/`
- SVG → `memory/drafts/svg/`
- Documentation → `memory/docs/`
- Tests → `memory/ucode/tests/`
- Missions → `memory/missions/`

**State Files**:
- Config: `memory/system/user/ok_config.json`
- History: `memory/system/user/ok_history.json`

**Requirements**: GEMINI_API_KEY in `.env` file (gracefully degrades if missing)

**Panel Navigation** (O-key):
- 8/2 - Navigate prompts or history
- 5 - Select and execute
- P - Switch to prompts view
- H - Switch to history view
- C - Clear conversation history
- ESC - Close panel

---

### GENERATE
**v1.2.0** - Unified AI generation system with offline-first architecture.
**v1.2.15** - Graphics commands (SVG, ASCII, TELETEXT) deprecated, use `MAKE --format` instead.

**Commands:**
```
GENERATE DO <query>                                 # Offline-first Q&A (90%+ free!)
GENERATE REDO [modifications]                       # Retry last generation
GENERATE GUIDE <category> <topic>                   # Generate knowledge guide
GENERATE SVG <description>                          # [DEPRECATED] Use MAKE --format svg
GENERATE ASCII <type> <content> [width] [height]    # [DEPRECATED] Use MAKE --format ascii
GENERATE TELETEXT <content>                         # [DEPRECATED] Use MAKE --format teletext
GENERATE STATUS                                     # Show usage statistics
GENERATE CLEAR                                      # Clear generation history
```

**Migration to v1.2.15:**
```bash
# Old (deprecated)
GENERATE SVG water filter
GENERATE ASCII flowchart "Process"
GENERATE TELETEXT welcome_screen

# New (v1.2.15+)
MAKE --format svg --style technical --source "water filter"
MAKE --format ascii --template flowchart
MAKE --format teletext --palette classic --source "welcome screen"
```

**Architecture (3-tier intelligence):**
1. **Offline Engine** (90%+ queries, zero cost)
   - FAQ database (70% confidence)
   - Knowledge bank synthesis (30% confidence)
   - Instant responses, no API calls
2. **Gemini Extension** (fallback, <10% queries)
   - Activated when offline confidence < 50%
   - Optional (requires GEMINI_API_KEY)
   - Cost tracking and rate limiting
3. **Graphics System** (v1.2.15+)
   - 5-format unified system (MAKE command)
   - Node.js rendering service
   - Template library with offline-first operation

---

#### GENERATE DO (Offline-First Q&A)

**NEW in v1.2.0** - Ask questions with intelligent offline-first answering.

**Syntax:**
```
GENERATE DO <query>                 # Ask any question
GENERATE DO --mode offline <query>  # Force offline only
GENERATE DO --mode online <query>   # Force Gemini (if available)
```

**Examples:**
```upy
GENERATE DO how do I purify water?
GENERATE DO what's the best fire starting method in wet conditions?
GENERATE DO explain grid system
GENERATE DO --mode offline water sources

# With workflow variables
SET GENERATE.MODE offline
GENERATE DO shelter building basics
```

**How It Works:**
1. Searches 166+ survival guides in knowledge bank
2. Checks FAQ database (40+ common questions)
3. If confidence ≥ 50%: Returns offline answer (FREE)
4. If confidence < 50%: Falls back to Gemini (if configured)
5. Tracks costs, rate limits, and statistics

**Output:**
```
✅ Knowledge Bank (Offline - No API Cost)
Confidence: 85%

[Answer content with sources]

📚 Sources (3):
  • knowledge/water/purification.md
  • knowledge/water/boiling.md
  • knowledge/water/filtration.md

💡 Related:
  • water filtration methods
  • emergency water sources
```

---

#### GENERATE REDO (Retry Generation)

**Syntax:**
```
GENERATE REDO                       # Retry exact same query
GENERATE REDO [modifications]       # Retry with changes
```

**Examples:**
```upy
# First query
GENERATE DO fire starting methods

# Retry with modification
GENERATE REDO in wet conditions
GENERATE REDO without matches
```

**Use Cases:**
- Refine answer with additional constraints
- Try online fallback if offline answer insufficient
- Regenerate with different prompt variables

---

#### GENERATE GUIDE (Create Knowledge Guides)

**Requires Gemini** - Generate complete knowledge bank guides.

**Syntax:**
```
GENERATE GUIDE <category> <topic>   # Create new guide
```

**Examples:**
```upy
GENERATE GUIDE water "solar distillation"
GENERATE GUIDE fire "char cloth making"
GENERATE GUIDE shelter "emergency bivouac"
```

**Output:**
- File: `knowledge/<category>/<topic>.md`
- Includes: Steps, safety, materials, common mistakes
- Metadata: Difficulty, time, complexity level

---

#### GENERATE SVG/ASCII/TELETEXT (Graphics)

**SVG Diagrams (Nano Banana pipeline):**
```
GENERATE SVG <description>                          # General diagram
GENERATE SVG --survival <category>/<prompt> [opts]  # Survival templates
```

**SVG Options:**
- `--pro` - Professional style (clean, technical)
- `--strict` - Strict compliance mode
- `--refined` - Refined aesthetic

**SVG Examples:**
```upy
GENERATE SVG water purification flowchart
GENERATE SVG --survival water/purification_flow --pro
GENERATE SVG --survival fire/methods_comparison --strict
```

**ASCII Art:**
```
GENERATE ASCII <type> <content> [width] [height]
```

**ASCII Types:** box, panel, table, flowchart, progress, list, banner, tree

**ASCII Examples:**
```upy
GENERATE ASCII box "Water Sources" 40 5
GENERATE ASCII table "Method,Time,Difficulty" "Friction,10min,Hard;Flint,2min,Easy"
GENERATE ASCII progress "Purification" 75 30
```

**Teletext Graphics:**
```upy
GENERATE TELETEXT "Welcome to uDOS"
```

**Output Locations:**
- SVG: `memory/drafts/svg/`
- ASCII: Terminal display + optional save
- Teletext: `memory/drafts/teletext/`

---

#### GENERATE STATUS (Monitor Usage)

**Show generation statistics and API monitoring.**

**Syntax:**
```
GENERATE STATUS                     # Full status report
```

**Output:**
```
📊 GENERATE System Status

Services:
  Offline Engine: ✅ Active
  Gemini Extension: ✅ Active

Usage Statistics:
  Total Requests: 47
  Offline Requests: 42 (89%)
  Online Requests: 5 (11%)
  Total Cost: $0.0012
  Avg Cost/Request: $0.0000

History:
  Generation History: 47 items

API Monitoring:
  Rate Limit: 2.0 req/sec (1 remaining)
  Budget: $0.0012 / $1.00 daily (0%)
  Requests Today: 5

🚨 Active Alerts:
  [None]
```

---

#### GENERATE CLEAR (Clear History)

**Clear generation history (keeps statistics).**

**Syntax:**
```
GENERATE CLEAR                      # Clear all history
```

---

### Migration from ASSISTANT

**⚠️ DEPRECATED**: `ASSISTANT` and `OK ASK` commands replaced by `GENERATE DO`.

**Old Syntax → New Syntax:**
```upy
# OLD (deprecated)
ASSISTANT ASK how do I purify water?
OK ASK what's the best fire method?

# NEW (recommended)
GENERATE DO how do I purify water?
GENERATE DO what's the best fire method?
```

**Why Switch?**
- ✅ 90%+ queries answered offline (FREE)
- ✅ Cost tracking and rate limiting
- ✅ Better knowledge bank integration
- ✅ Confidence-based fallback
- ✅ Generation history (REDO support)

**See:** [Migration Guide](Migration-Guide-ASSISTANT-to-GENERATE.md)

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
**[DEPRECATED in v1.2.15]** Use `MAKE --format ascii --list` to browse templates.

Browse ASCII diagram library.

**Syntax:**
```
DIAGRAM LIST [type]                 # List diagrams [DEPRECATED]
DIAGRAM SEARCH <query>              # Search diagrams [DEPRECATED]
DIAGRAM SHOW <name>                 # Display diagram [DEPRECATED]
DIAGRAM TYPES                       # Show categories [DEPRECATED]
DIAGRAM EXPORT <name> <file>        # Save to file [DEPRECATED]
```

**Migration:**
```bash
# Old (deprecated)
DIAGRAM LIST
DIAGRAM SHOW water_filter

# New (v1.2.15+)
MAKE --list ascii
MAKE --format ascii --template system_architecture
```

**Examples:**
```upy
DIAGRAM LIST                        # [DEPRECATED]
DIAGRAM SEARCH water                # [DEPRECATED]
DIAGRAM SHOW water_filter           # [DEPRECATED]
DIAGRAM TYPES                       # [DEPRECATED]

# Use MAKE command instead:
MAKE --list ascii                   # List templates
MAKE --format ascii --template flowchart  # Generate diagram
```

**See Also:** `MAKE --help ascii` for complete ASCII graphics documentation.

---

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

### MAKE
**[v1.2.15]** Unified graphics generation system with 5 formats.

**Syntax:**
```bash
MAKE --format <type> [options]      # Generate graphic
MAKE --list [format]                # List templates/palettes/styles
MAKE --status                       # Session statistics
MAKE --help [format]                # Help (general or format-specific)
```

**Formats:**
- `ascii` - Terminal diagrams (25 templates)
- `teletext` - ANSI color pages (4 palettes)
- `svg` - Vector graphics (3 styles, AI-assisted)
- `sequence` - Sequence diagrams (5 templates, js-sequence)
- `flow` - Flowcharts (5 templates, flowchart.js)

**Common Options:**
```bash
--format <type>      # ascii | teletext | svg | sequence | flow
--output <file>      # Custom output filename
--list               # List available templates/palettes/styles
--status             # Show session statistics
--help [format]      # General or format-specific help
```

**Format-Specific Options:**

**ASCII**:
```bash
--template <name>    # Template: flowchart, system_architecture, etc.
--width <number>     # Diagram width (default: 80)
--border <style>     # Border: none | single | double | rounded
```

**Teletext**:
```bash
--palette <name>     # Palette: classic | earth | terminal | amber
--source <text>      # Page content (use {0-7} for colors)
```

**SVG**:
```bash
--style <name>       # Style: technical | simple | detailed
--ai-assisted        # Use AI for complex diagrams (requires API key)
--source <text>      # Description or diagram content
```

**Sequence**:
```bash
--template <name>    # Template: message_flow, api_request, etc.
--source <text>      # Sequence diagram syntax (js-sequence)
```

**Flow**:
```bash
--template <name>    # Template: decision_flow, login_process, etc.
--source <text>      # Flowchart syntax (flowchart.js)
```

**Examples:**
```bash
# List all ASCII templates
MAKE --list ascii

# Create ASCII flowchart
MAKE --format ascii --template flowchart --width 80 --border double

# Teletext welcome screen with colors
MAKE --format teletext --palette classic --source "Welcome to {1}uDOS{/}"

# AI-assisted SVG diagram
MAKE --format svg --style detailed --ai-assisted --source "water filter system"

# Sequence diagram for login flow
MAKE --format sequence --source "User->API: Login
API->Database: Validate
Database-->API: Success
API-->User: Token"

# Flowchart for error handling
MAKE --format flow --source "start=>start: Request
error=>condition: Error?
retry=>operation: Retry
success=>end: Complete
start->error
error(yes)->retry->error
error(no)->success"

# Get format-specific help
MAKE --help ascii
MAKE --help sequence

# View session stats
MAKE --status
```

**Output Locations:**
- ASCII: `memory/drafts/ascii/<filename>.txt`
- Teletext: `memory/drafts/teletext/<filename>.ans`
- SVG: `memory/drafts/svg/<filename>.svg`
- Sequence: `memory/drafts/sequence/<filename>.svg`
- Flow: `memory/drafts/flow/<filename>.svg`

**Requirements:**
- Node.js renderer service on port 5555 (auto-started if available)
- AI-assisted SVG requires `GEMINI_API_KEY` in `.env`
- Full offline functionality with template library

**See Also:** [Graphics System](Graphics-System.md), `DRAW` (deprecated), `DIAGRAM` (deprecated)

---

### DRAW
**[DEPRECATED in v1.2.15]** Use `MAKE --format ascii` instead.

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

**Migration:**
```bash
# Old (deprecated)
DRAW flow "Start → Process → End"

# New (v1.2.15+)
MAKE --format ascii --template flowchart
```

---

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
