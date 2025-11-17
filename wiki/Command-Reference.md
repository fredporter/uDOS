# Command Reference

Complete guide to all uDOS commands

> **💡 Quick Tip**: Use `HELP` in uDOS for built-in command help, or `HELP DETAILED` for comprehensive documentation.

---

## 🚀 Quick Reference Card

### Essential Commands (Most Common)
```bash
# Getting Help
HELP                      # Show all commands
HELP <command>            # Show specific command help
HELP DETAILED             # Complete documentation

# File Operations
LIST [path]               # List directory contents
LOAD <file>               # Load file into memory
SAVE <file>               # Save current content
EDIT <file>               # Edit file

# System
STATUS                    # System status
CLEAR                     # Clear screen
REBOOT                    # Restart uDOS
```

### By Category
| Category | Common Commands |
|----------|----------------|
| **Files** | `LIST`, `LOAD`, `SAVE`, `EDIT` |
| **Grid** | `GRID`, `NEW GRID`, `GRID LIST` |
| **Navigation** | `MAP`, `GOTO`, `MOVE` |
| **System** | `STATUS`, `VIEWPORT`, `REPAIR` |
| **Automation** | `RUN <script>` |
| **AI Assistant** | `OK <task>`, `READ <content>` |
| **Utilities** | `HELP`, `CLEAR`, `SETUP` |

---

## Command Index

| Category | Commands |
|:---------|:---------|
| **File Operations** | [LIST](#list), [LOAD](#load), [SAVE](#save), [EDIT](#edit) |
| **Grid Management** | [GRID](#grid), [NEW GRID](#new-grid), [GRID LIST](#grid-list), [SHOW GRID](#show-grid) |
| **Assisted Task** | [OK ASK](#ok-ask), [OK DEV](#ok-dev), [READ](#read) |
| **Automation** | [RUN](#run) |
| **Knowledge Bank (v1.0.20)** | [MEMORY](#memory), [PRIVATE](#private), [SHARED](#shared), [COMMUNITY](#community), [KB](#kb) |
| **Geographic Data (v1.0.20b)** | [TILE](#tile-commands) |
| **Display System (v1.0.21)** | [PANEL](#panel-commands) |
| **Debugging** | [DEBUG](#debug), [BREAK](#break), [STEP](#step), [CONTINUE](#continue), [INSPECT](#inspect), [WATCH](#watch), [STACK](#stack), [MODIFY](#modify), [PROFILE](#profile), [HISTORY](#history) |
| **System** | [REBOOT](#reboot), [STATUS](#status), [VIEWPORT](#viewport), [PALETTE](#palette), [REPAIR](#repair) |
| **History** | [UNDO](#undo), [REDO](#redo), [RESTORE](#restore) |
| **Navigation** | [MAP](#map), [GOTO](#goto), [MOVE](#move), [LEVEL](#level), [GODOWN](#godown), [GOUP](#goup) |
| **Utilities** | [HELP](#help), [CLEAR](#clear), [SETUP](#setup) |

---

## Command Evolution by Version

uDOS commands have been developed systematically, focusing on core functionality:

### 🧪 v1.0.1 - System Commands Foundation
**SYSTEM category commands** - Core infrastructure and diagnostics
- **HELP**: Interactive command search and categorization
- **STATUS**: System state and resource monitoring
- **REPAIR**: Diagnostic modes with auto-fix capabilities
- **VIEWPORT**: Terminal size and display management
- **PALETTE**: Visual color tests and grayscale gradients
- **REBOOT**: System restart and state reset

### 📁 v1.0.2 - File Operations
**File management** - Core data handling operations
- **LIST**: Directory contents and file browsing
- **LOAD**: File loading into memory/grids
- **SAVE**: File persistence and export
- **EDIT**: File editing and modification

### � v1.0.3 - Grid System
**Workspace organization** - Flexible data visualization
- **GRID**: Grid creation and management
- **NEW GRID**: Initialize new grid workspaces
- **GRID LIST**: List all active grids
- **SHOW GRID**: Display grid contents

### �️ v1.0.4 - Navigation System
**Spatial movement** - Intuitive positioning and traversal
- **MAP**: Display current location and surroundings
- **GOTO**: Jump to specific coordinates or locations
- **MOVE**: Relative position changes
- **LEVEL**: Current level/depth display
- **GODOWN**: Descend one level
- **GOUP**: Ascend one level

### 🐛 v1.0.17 - Interactive Debugger
**Developer tools** - Full debugging environment for uCODE scripts
- **DEBUG**: Start/stop debugging sessions with breakpoints
- **BREAK**: Breakpoint management (set, clear, enable, disable, conditional)
- **STEP**: Step execution (over, into, out)
- **CONTINUE**: Resume execution until next breakpoint
- **INSPECT**: Variable inspection (specific or all variables)
- **WATCH**: Watch expression management
- **STACK**: Call stack display
- **MODIFY**: Runtime variable modification
- **PROFILE**: Performance profiling and analysis
- **HISTORY**: Variable change history tracking

---

## File Operations

### CATALOG

**Purpose**: List directory contents

**Syntax**:
```
CATALOG ["<path>"] [TO "<panel>"]
```

**Parameters**:
- `path` (optional) - Directory to list (default: current directory)
- `panel` (optional) - Panel to output results (default: `main`)

**Examples**:
```
🔮 > CATALOG
🔮 > CATALOG "data"
🔮 > CATALOG "./" TO "files"
```

**Output**:
```
📁 ./data
  ├── COMMANDS.UDO (15.2 KB)
  ├── LEXICON.UDO (8.4 KB)
  ├── PALETTE.UDO (7.1 KB)
  └── WORLDMAP.UDO (12.3 KB)
```

**uCODE**: `[FILE|LIST*<path>*<panel>]`

---

### LOAD

**Purpose**: Load file content into a panel

**Syntax**:
```
LOAD "<file>" [TO "<panel>"]
```

**Parameters**:
- `file` (required) - Path to file
- `panel` (optional) - Target panel (default: `main`)

**Examples**:
```
🔮 > LOAD "README.MD"
🔮 > LOAD "data/COMMANDS.UDO" TO "config"
🔮 > LOAD "script.uscript" TO "code"
```

**Output**:
```
✅ SUCCESS: File loaded into 'main' (361 lines)
💡 Try: SHOW "main"
```

**Tab Completion**: File paths auto-complete

**uCODE**: `[FILE|LOAD*<file>*<panel>]`

---

### SAVE

**Purpose**: Save panel content to a file

**Syntax**:
```
SAVE "<panel>" TO "<file>"
```

**Parameters**:
- `panel` (required) - Source panel name
- `file` (required) - Target file path

**Examples**:
```
🔮 > SAVE "main" TO "output.txt"
🔮 > SAVE "notes" TO "sandbox/mynotes.md"
🔮 > SAVE "config" TO "data/settings.json"
```

**Output**:
```
✅ SUCCESS: Panel 'main' saved to 'output.txt'
```

**Notes**:
- Creates directories if needed
- Overwrites existing files
- Adds to UNDO stack

**uCODE**: `[FILE|SAVE*<panel>*<file>]`

---

### EDIT

**Purpose**: Open file in default text editor

**Syntax**:
```
EDIT "<file>"
```

**Parameters**:
- `file` (required) - Path to file

**Examples**:
```
🔮 > EDIT "README.MD"
🔮 > EDIT "data/SETUP.USC"
```

**Output**:
```
📝 Opening 'README.MD' in typora...
💡 File will be opened in your default editor
```

**Notes**:
- Uses system default editor
- Auto-installs typo editor if available
- Returns to uDOS after closing

**uCODE**: `[SYSTEM|EDIT*<file>]`

---

### FILE PICK

**Purpose**: Interactive file picker with fuzzy search

**Syntax**:
```
FILE PICK [pattern]
```

**Parameters**:
- `pattern` (optional) - Search pattern for filtering files

**Examples**:
```
🔮 > FILE PICK
🔮 > FILE PICK readme
🔮 > FILE PICK .py
```

**Output**:
```
📁 File Picker - Found 15 files (relevance 0.8+)
1. README.MD (1.0) - 5.2KB, modified 2h ago ✓
2. readme.txt (0.9) - 1.1KB, modified 1d ago
3. READBOOK.md (0.8) - 3.4KB, modified 3d ago
Select file (1-15): 1
✅ Selected: README.MD
```

**Features**:
- Fuzzy search with relevance scoring
- Git status integration (✓ = tracked)
- File type classification and size display
- Automatic access tracking for recent files

**uCODE**: `[FILE|PICK*<pattern>]`

---

### FILE RECENT

**Purpose**: Display recently accessed files

**Syntax**:
```
FILE RECENT [count] [workspace]
```

**Parameters**:
- `count` (optional) - Number of files to show (default: 20)
- `workspace` (optional) - Filter by workspace

**Examples**:
```
🔮 > FILE RECENT
🔮 > FILE RECENT 10
🔮 > FILE RECENT sandbox 5
```

**Output**:
```
📊 Recent Files (last 20)
1. README.MD (accessed 3 times, last: 15m ago)
2. config.json (accessed 7 times, last: 1h ago)
3. script.py (accessed 2 times, last: 3h ago)
```

**Features**:
- SQLite persistence for access history
- Access frequency counting
- Workspace filtering available
- File existence verification

**uCODE**: `[FILE|RECENT*<count>*<workspace>]`

---

### FILE BATCH

**Purpose**: Batch operations on multiple files

**Syntax**:
```
FILE BATCH [DELETE|COPY|MOVE] <pattern> [destination]
```

**Parameters**:
- `operation` (required) - DELETE, COPY, or MOVE
- `pattern` (required) - File pattern or search term
- `destination` (optional) - Target directory for COPY/MOVE

**Examples**:
```
🔮 > FILE BATCH DELETE *.tmp
🔮 > FILE BATCH COPY *.md backup/
🔮 > FILE BATCH MOVE test* archive/
```

**Output**:
```
🔍 Found 5 files matching '*.tmp'
⚠️  DELETE operation will permanently remove files
Continue? (y/N): y
✅ Deleted 5 files successfully
```

**Features**:
- Pattern matching with fuzzy search
- Safety confirmations for destructive operations
- Progress tracking for large operations
- Detailed error reporting

**uCODE**: `[FILE|BATCH*<operation>*<pattern>*<destination>]`

---

### FILE BOOKMARKS

**Purpose**: Manage persistent file bookmarks

**Syntax**:
```
FILE BOOKMARKS [ADD|REMOVE] [filename]
```

**Parameters**:
- `action` (optional) - ADD or REMOVE bookmark
- `filename` (optional) - File to bookmark/unbookmark

**Examples**:
```
🔮 > FILE BOOKMARKS
🔮 > FILE BOOKMARKS ADD README.MD
🔮 > FILE BOOKMARKS REMOVE config
```

**Output**:
```
📚 File Bookmarks (3 total)
1. 🔖 README.MD - Project documentation
2. 🔖 config.json - System configuration
3. 🔖 startup.sh - Launch script
```

**Features**:
- SQLite persistence for bookmarks
- Custom bookmark names and tags
- File existence verification
- Interactive add/remove operations

**uCODE**: `[FILE|BOOKMARKS*<action>*<filename>]`

---

### FILE PREVIEW

**Purpose**: Preview file content with metadata

**Syntax**:
```
FILE PREVIEW <filename>
```

**Parameters**:
- `filename` (required) - File to preview

**Examples**:
```
🔮 > FILE PREVIEW README.MD
🔮 > FILE PREVIEW config.json
```

**Output**:
```
📄 README.MD (5.2KB, modified 2h ago) ✓
─────────────────────────────────────
# uDOS Project

This is the main documentation for...
[Content preview - first 20 lines]
─────────────────────────────────────
📊 361 lines, 15,432 chars, 2,847 words
```

**Features**:
- Content preview for text files (first 20 lines)
- File metadata and git status integration
- Text statistics for text files
- Binary file detection and safe handling

**uCODE**: `[FILE|PREVIEW*<filename>]`

---

### FILE INFO

**Purpose**: Comprehensive file information and statistics

**Syntax**:
```
FILE INFO <filename>
```

**Parameters**:
- `filename` (required) - File to analyze

**Examples**:
```
🔮 > FILE INFO README.MD
🔮 > FILE INFO script.py
```

**Output**:
```
📋 File Information: README.MD
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
📂 Location: /Users/user/project/README.MD
📏 Size: 5.2KB (5,247 bytes)
📅 Created: Nov 1, 2025 14:23:45
📝 Modified: Nov 2, 2025 09:15:32
👁️  Accessed: Nov 2, 2025 11:30:22
📊 Content: 361 lines, 15,432 chars, 2,847 words
🔖 Bookmarked: Yes (added 2d ago)
📈 Access History: 8 times (last: 15m ago)
💡 Suggested: EDIT, LOAD TO panel, BOOKMARKS
```

**Features**:
- Complete file metadata and timestamps
- Text analysis for readable files
- Access history from tracking database
- Bookmark status and git integration
- Contextual command suggestions

**uCODE**: `[FILE|INFO*<filename>]`

---

## Knowledge Base

### KNOWLEDGE SEARCH

**Purpose**: Full-text search of knowledge base

**Syntax**:
```
KNOWLEDGE SEARCH <query> [category] [limit]
```

**Parameters**:
- `query` (required) - Search terms
- `category` (optional) - Limit to specific category
- `limit` (optional) - Maximum results (default: 10)

**Examples**:
```
🔮 > KNOWLEDGE SEARCH "ASK command"
🔮 > KNOWLEDGE SEARCH mapping commands 5
🔮 > KNOWLEDGE SEARCH python concepts
```

**Output**:
```
🔍 Knowledge Search: "ASK command" (3 results)
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
1. ASK Command Reference (commands) - Score: 0.95
   📄 Complete guide to ASK command with AI integration
   🏷️  #command #AI #help #assistant

2. Command Architecture (concepts) - Score: 0.82
   📄 Handler patterns and command routing
   🏷️  #architecture #development #patterns

3. FAQ: Common Questions (faq) - Score: 0.71
   📄 Frequently asked questions about commands
   🏷️  #help #troubleshooting #guide
```

**Features**:
- BM25 relevance scoring with SQLite FTS5
- Category filtering for focused searches
- Tag-based content organization
- Fuzzy matching for typos and partial terms

**uCODE**: `[KNOWLEDGE|SEARCH*<query>*<category>*<limit>]`

---

### KNOWLEDGE LIST

**Purpose**: Browse knowledge by categories and topics

**Syntax**:
```
KNOWLEDGE LIST [category]
```

**Parameters**:
- `category` (optional) - Specific category to list

**Examples**:
```
🔮 > KNOWLEDGE LIST
🔮 > KNOWLEDGE LIST commands
🔮 > KNOWLEDGE LIST concepts
```

**Output**:
```
📚 Knowledge Categories (3 total, 2,847 words)
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
📂 commands (3 items, 1,234 words)
   • ASK Command Reference - AI assistance guide
   • MAP Command Reference - Navigation and mapping
   • SYSTEM Command Reference - System management

📂 concepts (1 item, 987 words)
   • Command Architecture - Handler patterns and design

📂 faq (2 items, 626 words)
   • Common Questions - Troubleshooting guide
   • Getting Started - Quick start tutorial
```

**Features**:
- Hierarchical category organization
- Word count statistics per category
- Auto-organization by folder structure
- Quick navigation to content

**uCODE**: `[KNOWLEDGE|LIST*<category>]`

---

### KNOWLEDGE SHOW

**Purpose**: Display full knowledge content

**Syntax**:
```
KNOWLEDGE SHOW <title|path>
```

**Parameters**:
- `title|path` (required) - Knowledge item title or file path

**Examples**:
```
🔮 > KNOWLEDGE SHOW "ASK Command Reference"
🔮 > KNOWLEDGE SHOW commands/MAP.md
```

**Output**:
```
📖 ASK Command Reference (commands)
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
[Full content displayed in panel]

# ASK Command Reference

The ASK command provides AI-powered assistance...
[Complete document content]
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
📊 1,234 words | 🏷️  #command #AI #help #assistant
💡 Try: KNOWLEDGE SEARCH related topics
```

**Features**:
- Full content display with panel integration
- Rich formatting preservation
- Metadata and tag display
- Related content suggestions

**uCODE**: `[KNOWLEDGE|SHOW*<title>]`

---

### KNOWLEDGE INDEX

**Purpose**: Reindex knowledge base with change detection

**Syntax**:
```
KNOWLEDGE INDEX [--force]
```

**Parameters**:
- `--force` (optional) - Force complete reindexing

**Examples**:
```
🔮 > KNOWLEDGE INDEX
🔮 > KNOWLEDGE INDEX --force
```

**Output**:
```
🔄 Indexing Knowledge Base...
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
📂 Scanning knowledge/ directory...
✅ commands/ASK.md - Updated (checksum changed)
✅ commands/MAP.md - No changes
✅ concepts/command-architecture.md - New file
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
📊 Indexing complete: 6 files, 2,847 words total
⚡ Full-text search ready (SQLite FTS5)
```

**Features**:
- Automatic change detection with checksums
- Incremental updates for efficiency
- Force reindex option for complete refresh
- Progress reporting with file status

**uCODE**: `[KNOWLEDGE|INDEX*<force>]`

---

### KNOWLEDGE STATS

**Purpose**: Knowledge base metrics and analytics

**Syntax**:
```
KNOWLEDGE STATS
```

**Examples**:
```
🔮 > KNOWLEDGE STATS
```

**Output**:
```
📊 Knowledge Base Statistics
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
📚 Content Overview
   • Total Items: 6 files
   • Total Words: 2,847 words
   • Total Size: 47.3KB
   • Last Updated: 2h ago

📂 Category Breakdown
   • commands: 3 items (43.4%) - 1,234 words
   • concepts: 1 item (16.7%) - 987 words
   • faq: 2 items (33.3%) - 626 words

🔍 Search Performance
   • Database Size: 234KB
   • FTS Index: Optimized
   • Average Query Time: <10ms
   • Total Searches: 47 queries
```

**Features**:
- Comprehensive content metrics
- Category distribution analysis
- Search performance statistics
- Visual percentage breakdowns

**uCODE**: `[KNOWLEDGE|STATS]`

---

### KNOWLEDGE CATEGORIES

**Purpose**: Category management and overview

**Syntax**:
```
KNOWLEDGE CATEGORIES
```

**Examples**:
```
🔮 > KNOWLEDGE CATEGORIES
```

**Output**:
```
📂 Knowledge Categories Overview
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
1. commands (3 items) ████████████░░░░ 43.4%
   📖 Command references and usage guides
   🔍 Most Recent: ASK Command Reference (updated 2h ago)

2. concepts (1 item) ██████░░░░░░░░░░ 16.7%
   📖 System architecture and design patterns
   🔍 Most Recent: Command Architecture (updated 1d ago)

3. faq (2 items) ████████░░░░░░░░ 33.3%
   📖 Frequently asked questions and troubleshooting
   🔍 Most Recent: Common Questions (updated 3d ago)

💡 Try: KNOWLEDGE LIST <category> to browse content
```

**Features**:
- Visual category distribution with progress bars
- Recent activity tracking per category
- Category descriptions and purposes
- Navigation suggestions for browsing

**uCODE**: `[KNOWLEDGE|CATEGORIES]`

---

## Grid Management

### GRID PANEL CREATE

**Purpose**: Create a new named panel

**Syntax**:
```
GRID PANEL CREATE "<name>"
```

**Parameters**:
- `name` (required) - Panel name (unique)

**Examples**:
```
🔮 > GRID PANEL CREATE "notes"
🔮 > GRID PANEL CREATE "temp"
🔮 > GRID PANEL CREATE "analysis-results"
```

**Output**:
```
✅ Panel 'notes' created
💡 Try: LOAD "file.txt" TO "notes"
```

**uCODE**: `[GRID|PANEL*CREATE*<name>]`

---

### GRID PANELS LIST

**Purpose**: Show all panels and their status

**Syntax**:
```
GRID PANELS LIST
```

**Examples**:
```
🔮 > GRID PANELS LIST
```

**Output**:
```
📋 Active Panels:
  • main (3,421 bytes) - Last modified: 2025-10-30 20:53:28
  • notes (0 bytes) - Empty
  • config (15,234 bytes) - Last modified: 2025-10-30 19:15:42

Total: 3 panels
```

**uCODE**: `[GRID|PANELS*LIST]`

---

### SHOW

**Purpose**: Display panel contents

**Syntax**:
```
SHOW "<panel>"
```

**Parameters**:
- `panel` (required) - Panel name

**Examples**:
```
🔮 > SHOW "main"
🔮 > SHOW "notes"
```

**Output**:
```
═══════════════════════════════════════
Panel: main (361 lines)
═══════════════════════════════════════
[panel contents displayed...]
═══════════════════════════════════════
```

**Tab Completion**: Panel names auto-complete

**uCODE**: `[GRID|SHOW*<panel>]`

---

## AI & Analysis

### ASK

**Purpose**: Query Gemini AI (or offline engine)

**Syntax**:
```
ASK "<question>" [FROM "<panel>"]
```

**Parameters**:
- `question` (required) - Your question
- `panel` (optional) - Panel to use as context

**Examples**:
```
🔮 > ASK "What is uDOS?"
🔮 > ASK "Explain this code" FROM "main"
🔮 > ASK "Summarize the file"
```

**Online Output**:
```
🤖 Gemini AI:
uDOS is a human-readable CLI framework that combines natural
language commands with AI integration. It features...
```

**Offline Output**:
```
🔌 OFFLINE MODE - Using local logic engine
Based on the patterns I recognize, this appears to be...
```

**uCODE**: `[AI|ASK*<question>*<panel>]`

---

### ANALYZE

**Purpose**: Offline content analysis

**Syntax**:
```
ANALYZE "<panel>"
```

**Parameters**:
- `panel` (required) - Panel to analyze

**Examples**:
```
🔮 > ANALYZE "main"
🔮 > ANALYZE "code"
```

**Output**:
```
📊 Analysis Results for 'main':
  • Lines: 361
  • Words: 2,147
  • Characters: 15,234
  • Code blocks: 12
  • Links: 8
  • Sentiment: Informative
```

**uCODE**: `[AI|ANALYZE*<panel>]`

---

## Automation

### RUN

**Purpose**: Execute a script file

**Syntax**:
```
RUN "<script>"
```

**Parameters**:
- `script` (required) - Path to `.uscript` file

**Examples**:
```
🔮 > RUN "shakedown.uscript"
🔮 > RUN "data/SETUP.USC"
🔮 > RUN "knowledge/demos/demo.uscript"
```

**Output**:
```
🚀 Executing script: shakedown.uscript
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
[script execution output...]
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
✅ Script completed
```

**Script Format**: uCODE or regular commands

**uCODE**: `[SYSTEM|RUN*<script>]`

---

## System Commands

### REBOOT

**Purpose**: Restart uDOS and re-detect system

**Syntax**:
```
REBOOT
RESTART  # Alias
```

**Examples**:
```
🔮 > REBOOT
```

**Pre-Flight Checks**:
- ✅ USER.UDO validation
- ✅ System health
- ✅ File structure
- ✅ Viewport detection
- ✅ Color capability test

**Output**:
```
🔄 REBOOT PRE-FLIGHT CHECK
============================================================
✅ User profile OK (fredbook)
✅ Python version OK
✅ All dependencies available
✅ Viewport detected

🔄 VIEWPORT & COLOR TEST
[Full splash screen with ASCII art and color tests...]

🔄 Restarting uDOS...
```

**uCODE**: `[SYSTEM|REBOOT]`

---

### STATUS

**Purpose**: Show comprehensive system status

**Syntax**:
```
STATUS
```

**Examples**:
```
🔮 > STATUS
```

**Output**:
```
============================================================
📊 uDOS SYSTEM STATUS
============================================================

🌐 Connection: ONLINE (Gemini API reachable)
📐 Display: 120×40 (DESKTOP), Grid: 7×2
👤 User: fredbook (America/New_York)
🗺️  Location: New York (40.71°N, 74.01°W)
📜 History: 5 actions in undo stack
🎯 Map: SURFACE layer at (0, 0)
🏥 System Health: All OK

🎨 Quick Test: R:██  G:██  Y:██  B:██  P:██  C:██ | ██████
```

**uCODE**: `[SYSTEM|STATUS]`

---

### VIEWPORT

**Purpose**: Display terminal dimensions and grid

**Syntax**:
```
VIEWPORT
```

**Examples**:
```
🔮 > VIEWPORT
```

**Output**:
```
📐 Viewport Specifications:
  Terminal: 120×40 characters
  Device Type: DESKTOP
  Grid: 7×2 cells (16×16 per cell)
  Total Cells: 14

[ASCII grid visualization...]
```

**uCODE**: `[SYSTEM|VIEWPORT]`

---

### PALETTE

**Purpose**: Display color palette with visual tests

**Syntax**:
```
PALETTE
```

**Examples**:
```
🔮 > PALETTE
```

**Output**:
```
🎨 POLAROID COLOR PALETTE
============================================================
Name: Polaroid
Version: 1.0
Description: High-contrast photo-inspired color system

[Full color visualization with blocks, gradients, ASCII art...]

📋 COLOR REFERENCE:
PRIMARY:
  ███ Polaroid Red     (tput:196) #FF1744 - Errors, alerts
  ███ Polaroid Green   (tput:46)  #00E676 - Success
  [... etc ...]
```

**uCODE**: `[SYSTEM|PALETTE]`

---

### REPAIR

**Purpose**: Fix system issues automatically

**Syntax**:
```
REPAIR [<component>]
```

**Parameters**:
- `component` (optional) - Specific component (default: ALL)

**Examples**:
```
🔮 > REPAIR
🔮 > REPAIR DEPENDENCIES
🔮 > REPAIR FILES
```

**Output**:
```
🔧 System Repair Initiated
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
✅ Checking dependencies... OK
✅ Validating file structure... OK
✅ Verifying configurations... OK
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
✅ System health restored
```

**uCODE**: `[SYSTEM|REPAIR*<component>]`

---

## History Commands

### UNDO

**Purpose**: Undo last reversible action

**Syntax**:
```
UNDO
```

**Examples**:
```
🔮 > UNDO
```

**Output**:
```
⏪ Undone: panel_modify (main)
💡 Use REDO to reapply
```

**Reversible Actions**:
- Panel creation/deletion
- Panel modifications
- File operations

**uCODE**: `[SYSTEM|UNDO]`

---

### REDO

**Purpose**: Redo last undone action

**Syntax**:
```
REDO
```

**Examples**:
```
🔮 > REDO
```

**Output**:
```
⏩ Redone: panel_modify (main)
```

**uCODE**: `[SYSTEM|REDO]`

---

### RESTORE

**Purpose**: Restore to previous session

**Syntax**:
```
RESTORE [<session_number>]
```

**Parameters**:
- `session_number` (optional) - Session to restore (default: previous)

**Examples**:
```
🔮 > RESTORE
🔮 > RESTORE 25
```

**Output**:
```
🔄 Restoring session #25...
✅ Session restored (12 actions undone)
```

**uCODE**: `[SYSTEM|RESTORE*<session>]`

---

## Navigation & Mapping Commands

### MAP STATUS

**Purpose**: Show current location and system status

**Syntax**:
```
MAP STATUS
```

**Examples**:
```
🔮 > MAP STATUS
```

**Output**:
```
🗺️  Map Status
==============================
Current Location: Melbourne, Australia
TIZO Code: MEL
Cell Reference: JN196
Coordinates: -37.81°, 144.96°
Timezone: AEST (+10:00)
Accessible Layers: SURFACE, CLOUD-OC, SATELLITE-OC, DUNGEON-1

Use 'MAP VIEW' to see the area around you.
```

**uCODE**: `[MAP|STATUS]`

---

### MAP VIEW

**Purpose**: Generate ASCII map of current area

**Syntax**:
```
MAP VIEW [width] [height]
```

**Parameters**:
- `width` (optional) - Map width in characters (default: 40)
- `height` (optional) - Map height in characters (default: 20)

**Examples**:
```
🔮 > MAP VIEW
🔮 > MAP VIEW 60 30
🔮 > MAP VIEW 25 12
```

**Output**:
```
ASCII Map View - Center: JN196
========================================
~..~..~..~..~..~..~..~..~..~..~..~..~..~
.                                       .
~                                       ~
.                                       .
~                                       ~
.                                       .
~                     ◉                 ~
.                                       .
~                                       ~
.                                       .
~..~..~..~..~..~..~..~..~..~..~..~..~..~

Legend: ◉ Your Position, ~ Water, . Land
```

**uCODE**: `[MAP|VIEW*<width>*<height>]`

---

### MAP CITIES

**Purpose**: List cities globally or in a region

**Syntax**:
```
MAP CITIES [cell] [radius]
```

**Parameters**:
- `cell` (optional) - Center cell for regional search
- `radius` (optional) - Search radius in cells (default: global)

**Examples**:
```
🔮 > MAP CITIES
🔮 > MAP CITIES JN196 5
🔮 > MAP CITIES LON 10
```

**Output**:
```
🏙️  TIZO Cities (20 total):
AKL: Auckland, New Zealand (LB194)
BER: Berlin, Germany (CT52)
BJS: Beijing, China (IB72)
BOM: Mumbai, India (FV105)
MEL: Melbourne, Australia (JN196)
SYD: Sydney, Australia (JV189)
...
```

**uCODE**: `[MAP|CITIES*<cell>*<radius>]`

---

### MAP CELL

**Purpose**: Get detailed information about a specific cell

**Syntax**:
```
MAP CELL <cell_reference>
```

**Parameters**:
- `cell_reference` (required) - Cell in A1-RL270 format

**Examples**:
```
🔮 > MAP CELL JN196
🔮 > MAP CELL CB54
🔮 > MAP CELL PD68
```

**Output**:
```
📍 Cell Information: JN196
==============================
Center Coordinates: -38.09°, 145.12°
Bounds: -38.41° to -37.78° (lat)
        144.75° to 145.50° (lon)

🏙️  City in this cell:
Name: Melbourne, Australia
TIZO Code: MEL
Timezone: AEST (+10:00)
Population: MAJOR
Connection Quality: {'oceania': 'NATIVE', 'asia': 'FAST'}
```

**uCODE**: `[MAP|CELL*<cell>]`

---

### MAP NAVIGATE

**Purpose**: Calculate navigation between locations

**Syntax**:
```
MAP NAVIGATE <from> <to>
```

**Parameters**:
- `from` (required) - Starting location (TIZO code or cell reference)
- `to` (required) - Destination location (TIZO code or cell reference)

**Examples**:
```
🔮 > MAP NAVIGATE MEL SYD
🔮 > MAP NAVIGATE JN196 JV189
🔮 > MAP NAVIGATE LON NYC
```

**Output**:
```
🧭 Navigation: Melbourne (MEL) → Sydney (SYD)
========================================
From Cell: JN196
To Cell: JV189
Distance: 729.3 km
Cell Distance: 8 cells
Bearing: 49.6° (NE)
```

**uCODE**: `[MAP|NAVIGATE*<from>*<to>]`

---

### MAP LOCATE

**Purpose**: Set location to a TIZO city

**Syntax**:
```
MAP LOCATE <tizo_code>
```

**Parameters**:
- `tizo_code` (required) - 3-letter TIZO city code

**Examples**:
```
🔮 > MAP LOCATE MEL
🔮 > MAP LOCATE LON
🔮 > MAP LOCATE NYC
```

**Output**:
```
📍 Location set to Melbourne, Australia (MEL)
Cell: JN196
```

**Available TIZO Codes**: MEL, SYD, AKL, LON, BER, FRA, MOS, NYC, LA, SFO, TOR, VAN, TYO, BJS, HKG, SIN, BOM, DEL, DXB, JNB

**uCODE**: `[MAP|LOCATE*<tizo>]`

---

### MAP GOTO

**Purpose**: Move to specific coordinates or cell

**Syntax**:
```
MAP GOTO <cell_reference>
MAP GOTO <lat> <lon>
```

**Parameters**:
- `cell_reference` (required) - Cell in A1-RL270 format
- `lat` `lon` (required) - Latitude and longitude coordinates

**Examples**:
```
🔮 > MAP GOTO JN196
🔮 > MAP GOTO -37.81 144.96
🔮 > MAP GOTO CB54
```

**Output**:
```
🎯 Moving to cell JN196
Coordinates: -38.09°, 145.12°
Location: Melbourne, Australia (MEL)
```

**uCODE**: `[MAP|GOTO*<location>]`

---

### MAP LAYERS

**Purpose**: Show accessible layers from current location

**Syntax**:
```
MAP LAYERS
```

**Examples**:
```
🔮 > MAP LAYERS
```

**Output**:
```
🌍 Accessible Layers from MEL:
  SURFACE
  CLOUD-OC
  SATELLITE-OC
  DUNGEON-1

🌐 Connection Quality:
  Oceania: NATIVE
  Asia: FAST
  Americas: STANDARD
  Europe: SLOW
```

**uCODE**: `[MAP|LAYERS]`

---

### MAP TELETEXT

**Purpose**: Generate teletext-style map with mosaic block art

**Syntax**:
```
MAP TELETEXT [width] [height]
```

**Parameters**:
- `width` (optional) - Map width in characters (default: 40)
- `height` (optional) - Map height in characters (default: 20)

**Examples**:
```
🔮 > MAP TELETEXT
🔮 > MAP TELETEXT 60 30
🔮 > MAP TELETEXT 25 12
```

**Output**:
```
🖥️  Teletext Map Generated
===================================
Location: Melbourne, Australia
Cell: JN196
Size: 40×20 characters
Style: Mosaic block art

� File saved: output/teletext/udos_teletext_map_20251102_032408.html
🌐 Open in web browser to view
💡 Use MAP WEB to start local server
```

**uCODE**: `[MAP|TELETEXT*<width>*<height>]`

---

### MAP WEB

**Purpose**: Open teletext maps in browser or start web server

**Syntax**:
```
MAP WEB [server]
```

**Parameters**:
- `server` (optional) - Start HTTP server instead of opening file

**Examples**:
```
🔮 > MAP WEB
🔮 > MAP WEB SERVER
```

**Output**:
```
🌐 Teletext Map Opened
=========================
File: udos_teletext_map_20251102_032408.html
URL: file:///path/to/map.html

💡 Map should open in your default browser
�️  Use MAP WEB SERVER for local HTTP server
```

**Server Mode**:
```
🚀 Teletext Web Server Started
==============================
Server URL: http://localhost:8080
Port: 8080

🌐 Browser should open automatically
📁 All teletext maps available at server root
🛑 Press Ctrl+C in terminal to stop server
```

**uCODE**: `[MAP|WEB*<mode>]`

**uCODE**: `[MAP|MOVE*<dx>*<dy>]`

---

### LAYER

**Purpose**: Show available layers

**Syntax**:
```
LAYER
```

**Examples**:
```
🔮 > LAYER
```

**Output**:
```
🏔️  Available Layers:
  SATELLITE  (+100)  Space view
  CLOUD      (+50)   Aerial
→ SURFACE    (0)     Ground level  ← You are here
  DUNGEON-1  (-10)   First underground
  DUNGEON-2  (-20)   Deeper
  DUNGEON-3  (-30)   Even deeper
  MINES      (-50)   Mining level
  CORE       (-100)  Bottom
```

**uCODE**: `[MAP|LAYER]`

---

### DESCEND

**Purpose**: Go down one layer

**Syntax**:
```
DESCEND
```

**Examples**:
```
🔮 > DESCEND
```

**Output**:
```
⬇️  Descended to DUNGEON-1 (depth: -10)
[Map display for new layer...]
```

**uCODE**: `[MAP|DESCEND]`

---

### ASCEND

**Purpose**: Go up one layer

**Syntax**:
```
ASCEND
```

**Examples**:
```
🔮 > ASCEND
```

**Output**:
```
⬆️  Ascended to SURFACE (depth: 0)
[Map display for new layer...]
```

**uCODE**: `[MAP|ASCEND]`

---

## CLI Features (v1.0.6+)

### HISTORY

**Purpose**: Enhanced command history management with SQLite persistence and intelligent search

**Syntax**:
```
HISTORY LIST [count]
HISTORY SEARCH <term>
HISTORY STATS
HISTORY CLEAR
HISTORY EXPORT <file>
```

**Parameters**:
- `count` (optional) - Number of recent commands to show (default: 10)
- `term` - Search term for fuzzy matching
- `file` - Export filename (JSON format)

**Examples**:
```
🔮 > HISTORY LIST
🔮 > HISTORY LIST 20
🔮 > HISTORY SEARCH file
🔮 > HISTORY SEARCH map
🔮 > HISTORY STATS
🔮 > HISTORY CLEAR
🔮 > HISTORY EXPORT backup.json
```

**Features**:
- **SQLite persistence** - Commands survive restarts
- **Fuzzy search** with relevance scoring
- **Usage statistics** and frequency tracking
- **Smart deduplication** - No repeated commands within 5 minutes
- **JSON export** for backup and sharing

**Output Examples**:
```
📜 Command History (Last 10):
  1. MAP GOTO TOKYO
  2. THEME SET cyberpunk
  3. LOAD "data.txt"
  4. HISTORY SEARCH file

🔍 Search results for "file":
  1. FILE SEARCH *.py
  2. LOAD "myfile.txt"
  3. SAVE "output.json"

📊 Usage Statistics:
  Total commands: 147
  Unique commands: 89
  Most used: MAP (23 times)
```

---

### THEME

**Purpose**: Dynamic color theme management with accessibility support

**Syntax**:
```
THEME LIST
THEME SET <name>
THEME INFO
THEME ACCESSIBILITY ON|OFF
THEME CONTRAST ON|OFF
THEME COLORBLIND <type>
THEME CREATE <name>
```

**Parameters**:
- `name` - Theme name (classic, cyberpunk, accessibility, monochrome)
- `type` - Colorblind type (deuteranopia, protanopia, tritanopia)

**Examples**:
```
🔮 > THEME LIST
🔮 > THEME SET cyberpunk
🔮 > THEME SET accessibility
🔮 > THEME INFO
🔮 > THEME ACCESSIBILITY ON
🔮 > THEME CONTRAST ON
🔮 > THEME COLORBLIND deuteranopia
🔮 > THEME CREATE mytheme
```

**Available Themes**:
- **classic** - Traditional terminal colors
- **cyberpunk** - Neon-inspired futuristic theme
- **accessibility** - High contrast, accessible colors
- **monochrome** - Black and white for maximum compatibility

**Accessibility Features**:
- **High contrast mode** for enhanced visibility
- **Colorblind support** for deuteranopia, protanopia, tritanopia
- **Screen reader optimization** with accessible formatting
- **Custom theme creation** for personal preferences

**Output Examples**:
```
🎨 Available Themes:
  • classic (active)
  • cyberpunk
  • accessibility
  • monochrome

🎨 Current Theme: cyberpunk
  Primary: #00ff41
  Secondary: #ff00ff
  Accent: #ffff00
  Background: #000000
  Accessibility: OFF
```

---

### SESSION

**Purpose**: Workspace state persistence with save/restore functionality

**Syntax**:
```
SESSION LIST
SESSION SAVE [name] [description]
SESSION LOAD <id>
SESSION DELETE <id>
SESSION CURRENT
SESSION AUTO ON|OFF
SESSION CHECKPOINT [description]
SESSION EXPORT <id> <file>
SESSION IMPORT <file> [name]
```

**Parameters**:
- `name` - Session name (optional)
- `description` - Session description (optional)
- `id` - Session ID number
- `file` - Import/export filename

**Examples**:
```
🔮 > SESSION LIST
🔮 > SESSION SAVE dev_work "Development session"
🔮 > SESSION SAVE
🔮 > SESSION LOAD 1
🔮 > SESSION DELETE 2
🔮 > SESSION CURRENT
🔮 > SESSION AUTO ON
🔮 > SESSION CHECKPOINT "Before refactor"
🔮 > SESSION EXPORT 1 backup.json
🔮 > SESSION IMPORT backup.json restored_session
```

**Session Types**:
- **Manual** - User-created sessions
- **Automatic** - Auto-saved at intervals
- **Checkpoint** - Milestone markers
- **Backup** - Safety snapshots

**What's Saved**:
- Command history
- Current working directory
- Active files and bookmarks
- Theme and layout settings
- Environment variables

**Output Examples**:
```
💾 Available Sessions:
  1. dev_work (2024-11-02 13:45) - Development session
  2. auto_save_001 (2024-11-02 14:12) - Automatic save
  3. checkpoint_001 (2024-11-02 14:30) - Before refactor

💾 Current Session: dev_work
  Created: 2024-11-02 13:45:23
  Commands: 47
  Files: 3 active
  Auto-save: ON
```

---

### PROGRESS

**Purpose**: Real-time progress indicators for long-running operations

**Syntax**:
```
PROGRESS TEST
PROGRESS TEST MULTI
PROGRESS TEST SEARCH
PROGRESS LIST
PROGRESS CANCEL [id]
PROGRESS DEMO
```

**Parameters**:
- `id` (optional) - Progress indicator ID to cancel

**Examples**:
```
🔮 > PROGRESS TEST
🔮 > PROGRESS TEST MULTI
🔮 > PROGRESS TEST SEARCH
🔮 > PROGRESS LIST
🔮 > PROGRESS CANCEL 1
🔮 > PROGRESS DEMO
```

**Progress Types**:
- **Determinate** - Known progress (0-100%)
- **Indeterminate** - Unknown duration spinner
- **Multi-stage** - Multiple phases
- **Parallel** - Multiple simultaneous operations

**Features**:
- **Real-time updates** with animated indicators
- **Time estimation** and speed calculation
- **Cancellation support** with Ctrl+C
- **Background processing** with status updates
- **Integration** with FILE SEARCH and other operations

**Output Examples**:
```
⏳ Processing files... ████████████████████ 100% (47/47) [2.3s]

⚙️  Multi-stage operation:
  Stage 1: Scanning files    ████████████████████ 100%
  Stage 2: Processing data   ██████████░░░░░░░░░░  50%
  Stage 3: Generating output ░░░░░░░░░░░░░░░░░░░░   0%

📊 Active Progress Indicators:
  1. File search (87% complete, ~15s remaining)
  2. Data export (45% complete, ~30s remaining)
```

---

### LAYOUT

**Purpose**: Responsive terminal layouts that adapt to screen size

**Syntax**:
```
LAYOUT INFO
LAYOUT MODE <mode>
LAYOUT RESIZE
LAYOUT AUTO ON|OFF
LAYOUT CONFIG <setting> <value>
LAYOUT TEST
LAYOUT DEMO
LAYOUT SPLIT <content1> <content2>
```

**Parameters**:
- `mode` - Layout mode (compact, standard, expanded, split, dashboard)
- `setting` - Configuration setting name
- `value` - Configuration value
- `content1`, `content2` - Content for split layout

**Examples**:
```
🔮 > LAYOUT INFO
🔮 > LAYOUT MODE compact
🔮 > LAYOUT MODE expanded
🔮 > LAYOUT RESIZE
🔮 > LAYOUT AUTO ON
🔮 > LAYOUT CONFIG margin 2
🔮 > LAYOUT TEST
🔮 > LAYOUT DEMO
🔮 > LAYOUT SPLIT "File list" "Content view"
```

**Layout Modes**:
- **compact** - Mobile/small screen optimized
- **standard** - Default balanced layout
- **expanded** - Wide screen with extra details
- **split** - Two-panel layout for large screens
- **dashboard** - Information-dense overview

**Features**:
- **Automatic resize detection** with background monitoring
- **Mobile-friendly** responsive design for small screens
- **Wide-screen enhancements** for large displays
- **Split-pane support** for multi-tasking
- **Configurable margins** and spacing

**Output Examples**:
```
📐 Layout Information:
  Current mode: standard
  Screen size: 120×30
  Auto-resize: ON
  Margin: 2
  Split mode: OFF

📱 Compact Mode (Mobile Optimized):
┌─────────────────────┐
│ uDOS v1.0.6         │
│ =================== │
│ > COMMAND           │
│ Result here...      │
└─────────────────────┘

🖥️  Expanded Mode (Wide Screen):
┌─────────────────────────────────────────────────────────────┐
│ uDOS v1.0.6                    Session: dev_work    14:30   │
│ =========================================================== │
│ > COMMAND                                Status: ✅ Ready   │
│ Detailed result with extra information...                   │
│ Additional context and metadata displayed here.             │
└─────────────────────────────────────────────────────────────┘
```

---

## Utility Commands

### HELP

**Purpose**: Show command help

**Syntax**:
```
HELP [<command>]
```

**Parameters**:
- `command` (optional) - Specific command (default: ALL)

**Examples**:
```
🔮 > HELP
🔮 > HELP LOAD
🔮 > HELP MAP
```

**Output**:
```
📖 HELP: LOAD
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Syntax: LOAD "<file>" [TO "<panel>"]
Description: Loads a file's content into a panel.

Examples:
  LOAD "README.MD"
  LOAD "data/config.json" TO "settings"
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
```

**uCODE**: `[SYSTEM|HELP*<command>]`

---

### CLS

**Purpose**: Clear terminal screen

**Syntax**:
```
CLS
CLEAR  # Alias
```

**Examples**:
```
🔮 > CLS
```

**Output**: (Screen cleared)

**uCODE**: `[SYSTEM|CLS]`

---

### SETUP

**Purpose**: Run interactive setup wizard

**Syntax**:
```
SETUP
```

**Examples**:
```
🔮 > SETUP
```

**Output**:
```
🔧 USER PROFILE SETUP
============================================================
Running setup script: data/SETUP.USC
[Interactive prompts for user data...]
✅ User profile configured
```

**uCODE**: `[SYSTEM|SETUP]`

---

## Debugging Commands

### DEBUG

**Purpose**: Start, stop, or check status of debugging sessions

**Syntax**:
```
DEBUG <script>          # Start debugging a script
DEBUG STATUS            # Show debugger status
DEBUG STOP              # Stop current debugging session
```

**Parameters**:
- `script` - Path to .uscript file to debug
- `STATUS` - Show current debugger state
- `STOP` - Terminate active debugging

**Examples**:
```
🔮 > DEBUG "memory/tests/debug_test.uscript"
🐛 Debugger started for: memory/tests/debug_test.uscript
💡 Use BREAK <line> to set breakpoints, CONTINUE to run

🔮 > DEBUG STATUS
🐛 Debugger Status:
   State: PAUSED
   Script: debug_test.uscript
   Line: 15
   Breakpoints: 3 active

🔮 > DEBUG STOP
✅ Debugging session stopped
```

**Output**:
```
🐛 Debugger started for: script.uscript
💡 Use BREAK <line> to set breakpoints
💡 Use CONTINUE to start execution
```

**uCODE**: `[SYSTEM|DEBUG*<script>]`

---

### BREAK

**Purpose**: Manage breakpoints (set, clear, list, enable, disable, conditional)

**Syntax**:
```
BREAK <line>                # Set breakpoint at line number
BREAK <line> IF <condition> # Set conditional breakpoint
BREAK LIST                  # List all breakpoints
BREAK CLEAR <line>          # Clear specific breakpoint
BREAK CLEAR ALL             # Clear all breakpoints
BREAK DISABLE <line>        # Disable breakpoint (keep it)
BREAK ENABLE <line>         # Re-enable disabled breakpoint
```

**Parameters**:
- `line` - Line number (1-based)
- `condition` - Boolean expression (e.g., `x > 10`, `name == "test"`)

**Examples**:
```
🔮 > BREAK 15
✅ Breakpoint set at line 15

🔮 > BREAK 25 IF count > 100
✅ Conditional breakpoint set at line 25: count > 100

🔮 > BREAK LIST
🐛 Active Breakpoints:
   Line 15 (enabled)
   Line 25 (enabled, condition: count > 100)
   Line 42 (disabled)

🔮 > BREAK DISABLE 15
✅ Breakpoint at line 15 disabled

🔮 > BREAK CLEAR ALL
✅ All breakpoints cleared
```

**Notes**:
- Conditional breakpoints evaluated at runtime
- Disabled breakpoints kept but not triggered
- Line numbers are 1-based (first line = 1)

**uCODE**: `[SYSTEM|BREAK*<line>*<condition>]`

---

### STEP

**Purpose**: Step through code execution (over, into, out)

**Syntax**:
```
STEP                    # Step over (execute next line)
STEP INTO               # Step into function call
STEP OUT                # Step out of current function
```

**Examples**:
```
🔮 > STEP
🐛 Stepped to line 16
   x = 42

🔮 > STEP INTO
🐛 Stepped into function 'calculate' at line 8
   params: [5, 10]

🔮 > STEP OUT
🐛 Stepped out to line 17
   result = 50
```

**Output**:
```
🐛 Stepped to line 16
   Current values:
   x = 42
   y = "test"
```

**uCODE**: `[SYSTEM|STEP*<mode>]`

---

### CONTINUE

**Purpose**: Resume execution until next breakpoint or script end

**Syntax**:
```
CONTINUE                # Continue execution
```

**Examples**:
```
🔮 > CONTINUE
🐛 Execution paused at breakpoint (line 25)
   count = 150

🔮 > CONTINUE
✅ Script execution completed
```

**Output**:
```
🐛 Running...
🐛 Breakpoint hit at line 25
```

**uCODE**: `[SYSTEM|CONTINUE]`

---

### INSPECT

**Purpose**: Inspect variable values during debugging

**Syntax**:
```
INSPECT <variable>      # Inspect specific variable
INSPECT ALL             # Show all variables in current scope
```

**Parameters**:
- `variable` - Variable name to inspect
- `ALL` - Show all variables

**Examples**:
```
🔮 > INSPECT count
🐛 Variable: count
   Type: int
   Value: 150
   Last changed: line 23

🔮 > INSPECT ALL
🐛 Current Variables:
   count = 150 (int)
   name = "test" (str)
   items = [1, 2, 3] (list)
   active = true (bool)
```

**Output**:
```
🐛 Variable: x
   Type: int
   Value: 42
   Last changed: line 15
```

**uCODE**: `[SYSTEM|INSPECT*<variable>]`

---

### WATCH

**Purpose**: Watch variable values across execution

**Syntax**:
```
WATCH <variable>        # Add variable to watch list
WATCH LIST              # Show all watched variables
WATCH CLEAR <variable>  # Remove from watch list
WATCH CLEAR ALL         # Clear all watches
```

**Parameters**:
- `variable` - Variable name to watch

**Examples**:
```
🔮 > WATCH count
✅ Watching variable: count

🔮 > WATCH x
✅ Watching variable: x

🔮 > WATCH LIST
🐛 Watched Variables:
   count = 150
   x = 42

🔮 > WATCH CLEAR count
✅ Stopped watching: count
```

**Notes**:
- Watches persist across breakpoints
- Shows current value at each step
- Useful for tracking state changes

**uCODE**: `[SYSTEM|WATCH*<variable>]`

---

### STACK

**Purpose**: Display call stack during debugging

**Syntax**:
```
STACK                   # Show full call stack
```

**Examples**:
```
🔮 > STACK
🐛 Call Stack:
   #0 calculate() at line 15
   #1 process_data() at line 28
   #2 main() at line 42
   #3 <script> at line 1
```

**Output**:
```
🐛 Call Stack (3 frames):
   #0 inner_function() at line 8
   #1 outer_function() at line 15
   #2 <main> at line 1
```

**uCODE**: `[SYSTEM|STACK]`

---

### MODIFY

**Purpose**: Modify variable values during debugging

**Syntax**:
```
MODIFY <variable> = <value>
```

**Parameters**:
- `variable` - Variable name to modify
- `value` - New value to assign

**Examples**:
```
🔮 > MODIFY count = 200
✅ Variable 'count' modified: 150 → 200

🔮 > MODIFY name = "debug"
✅ Variable 'name' modified: "test" → "debug"

🔮 > MODIFY active = false
✅ Variable 'active' modified: true → false
```

**Notes**:
- Changes take effect immediately
- Type coercion applied automatically
- Useful for testing edge cases

**uCODE**: `[SYSTEM|MODIFY*<variable>*<value>]`

---

### PROFILE

**Purpose**: Performance profiling and analysis

**Syntax**:
```
PROFILE                 # Show full performance profile
PROFILE TOP <n>         # Show top N slowest lines
PROFILE CLEAR           # Clear profiling data
PROFILE AUTO ON         # Enable automatic profiling
PROFILE AUTO OFF        # Disable automatic profiling
```

**Parameters**:
- `n` - Number of top results to show (default: 10)

**Examples**:
```
🔮 > PROFILE
🐛 Performance Profile:
   Line 15: 0.0023s (150 executions)
   Line 28: 0.0156s (1 execution)
   Line 42: 0.0001s (300 executions)
   Total: 0.0180s

🔮 > PROFILE TOP 3
🐛 Top 3 Slowest Lines:
   1. Line 28: 0.0156s
   2. Line 15: 0.0023s
   3. Line 42: 0.0001s

🔮 > PROFILE AUTO ON
✅ Auto-profiling enabled
```

**Notes**:
- Tracks execution time per line
- Shows execution count
- Auto-profiling runs in background

**uCODE**: `[SYSTEM|PROFILE*<mode>]`

---

### HISTORY

**Purpose**: View variable change history

**Syntax**:
```
HISTORY <variable>      # Show change history for variable
HISTORY ALL             # Show all variable histories
```

**Parameters**:
- `variable` - Variable name to track

**Examples**:
```
🔮 > HISTORY count
🐛 Change History: count
   Line 5: undefined → 0
   Line 12: 0 → 50
   Line 23: 50 → 150
   Line 35: 150 → 200

🔮 > HISTORY ALL
🐛 Variable Change History:
   count: 4 changes
   name: 2 changes
   active: 1 change
```

**Output**:
```
🐛 History: count
   Line 12: 0 → 50
   Line 23: 50 → 150
```

**uCODE**: `[SYSTEM|HISTORY*<variable>]`

---

## 🧠 Knowledge Bank Commands (v1.0.20)

### MEMORY

**Purpose**: Cross-tier memory search and operations

**Syntax**:
```
MEMORY STATUS           # Show all tiers status
MEMORY SEARCH <query>   # Search across all accessible tiers
MEMORY STATS            # Statistics across tiers
```

**Examples**:
```
🔮 > MEMORY STATUS
🧠 Memory System Status
   PRIVATE: 12 items (encrypted)
   SHARED: 8 items (3 shared with you)
   COMMUNITY: 5 groups
   PUBLIC: 245 knowledge items

🔮 > MEMORY SEARCH "water purification"
Found in PRIVATE: 2 results
Found in SHARED: 1 result
Found in PUBLIC: 8 results
```

**uCODE**: `[MEMORY|COMMAND*PARAMS]`

---

### PRIVATE

**Purpose**: Encrypted personal data storage (Tier 1)

**Syntax**:
```
PRIVATE ADD <key> <data>    # Store encrypted data
PRIVATE GET <key>           # Retrieve data
PRIVATE LIST                # List all keys
PRIVATE DELETE <key>        # Remove entry
PRIVATE SEARCH <query>      # Search private data
```

**Security**:
- AES-256 encryption
- Password-protected
- Auto-lock after inactivity

**Examples**:
```
🔮 > PRIVATE ADD password "mySecretPass123"
🔒 Data encrypted and stored in PRIVATE tier

🔮 > PRIVATE GET password
🔓 Decrypted: mySecretPass123

🔮 > PRIVATE SEARCH "password"
Found 3 encrypted entries matching "password"
```

**uCODE**: `[PRIVATE|COMMAND*PARAMS]`

---

### SHARED

**Purpose**: Explicit permission-based sharing (Tier 2)

**Syntax**:
```
SHARED ADD <key> <data>         # Add shareable data
SHARED SHARE <key> <user>       # Grant access
SHARED REVOKE <key> <user>      # Remove access
SHARED LIST                     # Show shared items
SHARED PERMISSIONS <key>        # View who has access
```

**Examples**:
```
🔮 > SHARED ADD recipe "Family pasta recipe: ..."
✅ Added to SHARED tier

🔮 > SHARED SHARE recipe alice
✅ Granted alice access to "recipe"

🔮 > SHARED PERMISSIONS recipe
👥 Shared with: alice, bob
```

**uCODE**: `[SHARED|COMMAND*PARAMS]`

---

### COMMUNITY

**Purpose**: Group collaboration with access control (Tier 3)

**Syntax**:
```
COMMUNITY CREATE <group>        # Create group
COMMUNITY JOIN <group>          # Join existing group
COMMUNITY POST <group> <data>   # Post to group
COMMUNITY LIST                  # List your groups
COMMUNITY MEMBERS <group>       # Show group members
```

**Examples**:
```
🔮 > COMMUNITY CREATE survivors
✅ Created group: survivors

🔮 > COMMUNITY POST survivors "Found clean water source at 34.5N, 118.2W"
✅ Posted to survivors group

🔮 > COMMUNITY MEMBERS survivors
👥 Members (5): alice, bob, charlie, dana, eve
```

**uCODE**: `[COMMUNITY|COMMAND*PARAMS]`

---

### KB (Knowledge Bank)

**Purpose**: Public knowledge base with full-text search (Tier 4)

**Syntax**:
```
KB SEARCH <query>       # Full-text search
KB ADD <topic> <data>   # Contribute knowledge
KB GET <topic>          # Retrieve topic
KB LIST <category>      # Browse by category
KB STATS                # Database statistics
```

**Examples**:
```
🔮 > KB SEARCH "first aid"
📚 Found 23 results:
   1. Basic First Aid Kit Contents
   2. CPR Procedure Steps
   3. Treating Burns and Wounds
   ...

🔮 > KB GET "water purification"
💧 Water Purification Methods:
   1. Boiling (most reliable)
   2. Chemical tablets (portable)
   3. UV light (solar)
   ...
```

**uCODE**: `[KB|COMMAND*PARAMS]`

---

## 🗺️ TILE Commands (v1.0.20b)

### TILE INFO

**Purpose**: Get comprehensive location information

**Syntax**:
```
TILE INFO <location>    # City or country info
```

**Examples**:
```
🔮 > TILE INFO Tokyo
🏙️  Tokyo, JP
📍 Location:
   Coordinates: 35.6762°, 139.6503°
   TIZO Code: T001
   Elevation: 40 meters

🌍 Demographics:
   Population: 37,400,000
   Region: Asia-Pacific

🌡️  Climate: subtropical
🕐 Time: Asia/Tokyo
```

**uCODE**: `[TILE|INFO*<location>]`

---

### TILE SEARCH

**Purpose**: Search cities and countries

**Syntax**:
```
TILE SEARCH <query>     # Search by name
```

**Examples**:
```
🔮 > TILE SEARCH Paris
🔍 Search Results (3):
🏙️  Paris, FR (TIZO: T023)
🏙️  Paris, US (TIZO: T145)
🌏 Paraguay (PY)
```

**uCODE**: `[TILE|SEARCH*<query>]`

---

### TILE NEARBY

**Purpose**: Find nearby cities within radius

**Syntax**:
```
TILE NEARBY <location> [radius_km]
```

**Examples**:
```
🔮 > TILE NEARBY London 500
🗺️  Cities near London (within 500km):
  109.2km - Birmingham, GB
  212.5km - Amsterdam, NL
  344.0km - Paris, FR
  491.3km - Brussels, BE
```

**uCODE**: `[TILE|NEARBY*<location>*<radius>]`

---

### TILE WEATHER

**Purpose**: Get climate information

**Syntax**:
```
TILE WEATHER <location>
```

**Examples**:
```
🔮 > TILE WEATHER Sydney
🌡️  Climate: Sydney, AU
🌍 Climate Type: Temperate (Cfb)

🌡️  Temperature Range: 8°C to 26°C
🌧️  Annual Rainfall: 1200-1500mm

📝 Description: Mild temperatures year-round
🌿 Vegetation: Temperate forests
📅 Seasons: 4
```

**uCODE**: `[TILE|WEATHER*<location>]`

---

### TILE TIMEZONE

**Purpose**: Detailed timezone information

**Syntax**:
```
TILE TIMEZONE <location>
```

**Examples**:
```
🔮 > TILE TIMEZONE New_York
🕐 America/New_York

⏰ Time Offsets:
   Standard: UTC-05:00
   DST: UTC-04:00
   Zone: EST/EDT

🌍 DST Information:
   Active: Yes
   Starts: 2nd Sunday March 2:00 AM
   Ends: 1st Sunday November 2:00 AM

🏙️  Major Cities: New York, Washington DC, Miami
```

**uCODE**: `[TILE|TIMEZONE*<location>]`

---

### TILE TERRAIN

**Purpose**: Terrain type information

**Syntax**:
```
TILE TERRAIN [type]     # Show terrain info or list all
```

**Examples**:
```
🔮 > TILE TERRAIN ocean
🗺️  Ocean Terrain

🎨 Visuals:
   ASCII: ≈
   Symbol: ~
   Color: blue

📐 Elevation Range: -11000m to 0m
🚶 Traversable: No
💧 Water Source: Yes

📝 Description: Deep ocean waters
```

**uCODE**: `[TILE|TERRAIN*<type>]`

---

### TILE ROUTE

**Purpose**: Route planning between locations

**Syntax**:
```
TILE ROUTE <from> <to>
```

**Examples**:
```
🔮 > TILE ROUTE Tokyo London
🧭 Route: Tokyo → London

📍 From: Tokyo, JP
   TIZO: T001
   Timezone: Asia/Tokyo
   Climate: subtropical

📍 To: London, GB
   TIZO: T045
   Timezone: Europe/London
   Climate: temperate

📏 Distance: 9584.5 km (5954.7 miles)
🧭 Bearing: 312.4° (NW)
```

**uCODE**: `[TILE|ROUTE*<from>*<to>]`

---

### TILE CONVERT

**Purpose**: Unit conversions

**Syntax**:
```
TILE CONVERT <value> <from> <to>
```

**Supported Units**:
- Temperature: C, F, K
- Distance: km, mi, m, ft
- Mass: kg, lb

**Examples**:
```
🔮 > TILE CONVERT 100 km mi
100 km = 62.14 miles

🔮 > TILE CONVERT 32 C F
32°C = 89.60°F

🔮 > TILE CONVERT 5 kg lb
5 kg = 11.02 lbs
```

**uCODE**: `[TILE|CONVERT*<value>*<from>*<to>]`

---

## 📺 PANEL Commands (v1.0.21)

The PANEL command provides a teletext-style character display system inspired by C64 screen memory. Create character-based panels, manipulate individual characters with POKE, and embed displays in markdown files.

### PANEL CREATE

**Purpose**: Create a new character panel with specified dimensions

**Syntax**:
```
PANEL CREATE <name> <width> <height> <tier>
```

**Parameters**:
- `name`: Panel identifier (alphanumeric, no spaces)
- `width`: Width in characters (1-320)
- `height`: Height in characters (1-160)
- `tier`: Screen tier 0-14 (validates max dimensions)

**Examples**:
```
🔮 > PANEL CREATE main 80 45 7
✅ Panel 'main' created: 80×45 chars (Tier 7: Notebook)

🔮 > PANEL CREATE dashboard 120 67 9
✅ Panel 'dashboard' created: 120×67 chars (Tier 9: Large Desktop)
```

**uCODE**: `[PANEL|CREATE*main*80*45*7]`

---

### PANEL SHOW

**Purpose**: Display panel contents with optional C64-style border

**Syntax**:
```
PANEL SHOW <name>         # Display without border
PANEL SHOW <name> border  # Display with C64-style border
```

**Examples**:
```
🔮 > PANEL SHOW main
[Panel contents displayed]

🔮 > PANEL SHOW main border
▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓
▓                   ▓
▓  Panel contents   ▓
▓                   ▓
▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓
```

**uCODE**: `[PANEL|SHOW*main]` or `[PANEL|SHOW*main*border]`

---

### PANEL POKE

**Purpose**: Write a single character at x,y coordinates (C64-style)

**Syntax**:
```
PANEL POKE <name> <x> <y> <char>
```

**Parameters**:
- `x`: Column position (0-based, left to right)
- `y`: Row position (0-based, top to bottom)
- `char`: Single character (supports Unicode)

**Examples**:
```
🔮 > PANEL POKE main 0 0 █
✅ Character written at (0,0)

🔮 > PANEL POKE main 10 5 ☀
✅ Character written at (10,5)
```

**Origin**: Top-left is (0,0), x increases right, y increases down

**uCODE**: `[PANEL|POKE*main*0*0*█]`

---

### PANEL WRITE

**Purpose**: Write a text string at x,y position

**Syntax**:
```
PANEL WRITE <name> <x> <y> <text>
```

**Examples**:
```
🔮 > PANEL WRITE main 10 5 Hello World!
✅ Text written at (10,5)

🔮 > PANEL WRITE main 10 6 Temperature: 24°C ☀
✅ Text written at (10,6)
```

**uCODE**: `[PANEL|WRITE*main*10*5*Hello World!]`

---

### PANEL EMBED

**Purpose**: Export panel to markdown file as code block

**Syntax**:
```
PANEL EMBED <name> <filepath.md>
```

**Examples**:
```
🔮 > PANEL EMBED diagram knowledge/systems/memory.md
✅ Panel embedded in knowledge/systems/memory.md
```

Embedded content appears as:
````markdown
## Diagram
```
[Panel content here as ASCII art]
```
````

**uCODE**: `[PANEL|EMBED*diagram*knowledge/systems/memory.md]`

---

### PANEL SIZE

**Purpose**: Display screen tier information

**Syntax**:
```
PANEL SIZE
```

**Output**:
```
Screen Tiers:
  0: Watch (20×10 chars) - Wearable displays
  1: Phone Small (30×20 chars) - Compact smartphone
  ...
  7: Notebook (80×45 chars) - Standard laptop ⭐
  ...
  14: 8K (320×160 chars) - Maximum resolution
```

⭐ **Tier 7 (Notebook 80×45)** is the most common target.

**uCODE**: `[PANEL|SIZE]`

---

### PANEL INFO

**Purpose**: Display panel statistics and metadata

**Syntax**:
```
PANEL INFO <name>
```

**Output**:
```
Panel: main
Size: 80×45 characters (3600 total)
Tier: 7 (Notebook - 80×45)
Characters: 450 (12.5% filled)
Created: 2025-01-16 14:30:00
```

**uCODE**: `[PANEL|INFO*main]`

---

### PANEL LIST

**Purpose**: Display all active panels with statistics

**Syntax**:
```
PANEL LIST
```

**Output**:
```
Active Panels:
  main: 80×45 chars (Tier 7) - 450/3600 chars (12.5%)
  dashboard: 120×67 chars (Tier 9) - 1200/8040 chars (15%)
```

**uCODE**: `[PANEL|LIST]`

---

### PANEL CLEAR

**Purpose**: Reset panel buffer to spaces (blank panel)

**Syntax**:
```
PANEL CLEAR <name>
```

**uCODE**: `[PANEL|CLEAR*main]`

---

### PANEL DELETE

**Purpose**: Remove panel from memory

**Syntax**:
```
PANEL DELETE <name>
```

**uCODE**: `[PANEL|DELETE*main]`

---

### Teletext Graphics Reference

The PANEL system supports full Unicode characters:

**Block Characters**:
```
█ ▓ ▒ ░  (Full, dark, medium, light blocks)
▀ ▄ ▌ ▐  (Half blocks - top, bottom, left, right)
```

**Box Drawing**:
```
┌ ┬ ┐  (Top corners and T-junction)
├ ┼ ┤  (Side T-junctions and cross)
└ ┴ ┘  (Bottom corners and T-junction)
─ │    (Horizontal and vertical lines)
```

**Double Lines**:
```
╔ ╦ ╗  (Double top)
╠ ╬ ╣  (Double sides)
╚ ╩ ╝  (Double bottom)
═ ║    (Double horizontal and vertical)
```

**Emoji**:
```
☀ ☁ 🌧 ❄  (Weather)
✓ ✗ ⚠ ℹ  (Status)
← → ↑ ↓  (Arrows)
```

---

### Example 1: Progress Bar

```
🔮 > PANEL CREATE progress 60 5 7
🔮 > PANEL WRITE progress 5 2 [████████████████████░░░░░░░░] 75%
🔮 > PANEL SHOW progress
```

Output:
```
[████████████████████░░░░░░░░] 75%
```

---

### Example 2: Weather Display

```
🔮 > PANEL CREATE weather 50 10 7
🔮 > PANEL POKE weather 5 2 ☀
🔮 > PANEL WRITE weather 8 2 Sydney: 24°C Clear
🔮 > PANEL POKE weather 5 4 ☁
🔮 > PANEL WRITE weather 8 4 London: 12°C Cloudy
🔮 > PANEL SHOW weather border
🔮 > PANEL EMBED weather data/weather/current.md
```

---

### Integration

**With Markdown Viewer**:
1. Create panel: `PANEL CREATE diagram 60 20 7`
2. Draw content: `PANEL WRITE diagram 10 5 System Architecture`
3. Embed: `PANEL EMBED diagram knowledge/systems/architecture.md`
4. View: Start markdown viewer at `http://localhost:9000`

**With uSCRIPT**:
See `knowledge/demos/panel_demo.uscript` for comprehensive examples.

**Full Documentation**: `docs/commands/PANEL.md`

---

## Command Aliases

Many commands have shorter or themed aliases:

| Standard | Alias | Theme |
|:---------|:------|:------|
| CATALOG | LIST | ZAP (Dungeon) |
| LOAD | - | CAST |
| SAVE | - | SCRIBE |
| ASK | - | CONSULT |
| REBOOT | RESTART | - |
| CLS | CLEAR | - |

---

## Tab Completion

uDOS provides smart context-aware completion:

| After Typing | Press Tab | Result |
|:-------------|:----------|:-------|
| `LO` | Tab | `LOAD` |
| `LOAD "` | Tab | List of files |
| `SHOW "` | Tab | List of panels |
| `RUN "` | Tab | List of .uscript files |
| `[` | - | Command menu appears |

---

## Next Steps

- [uCODE Language](uCODE-Language) - Internal command format
- [Script Automation](Script-Automation) - Batch operations
- [Tutorials](Tutorials) - Step-by-step guides

---

*Master these commands to wield the full power of uDOS!* 🔮
