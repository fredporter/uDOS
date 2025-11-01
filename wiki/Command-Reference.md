# Command Reference

Complete guide to all uDOS commands

---

## Command Index

| Category | Commands |
|:---------|:---------|
| **File Operations** | [CATALOG](#catalog), [LOAD](#load), [SAVE](#save), [EDIT](#edit) |
| **Grid Management** | [GRID PANEL CREATE](#grid-panel-create), [GRID PANELS LIST](#grid-panels-list), [SHOW](#show) |
| **AI & Analysis** | [ASK](#ask), [ANALYZE](#analyze) |
| **Automation** | [RUN](#run) |
| **System** | [REBOOT](#reboot), [STATUS](#status), [VIEWPORT](#viewport), [PALETTE](#palette), [REPAIR](#repair) |
| **History** | [UNDO](#undo), [REDO](#redo), [RESTORE](#restore) |
| **Navigation** | [MAP](#map), [GOTO](#goto), [MOVE](#move), [LAYER](#layer), [DESCEND](#descend), [ASCEND](#ascend) |
| **Utilities** | [HELP](#help), [CLS](#cls), [SETUP](#setup) |

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
🔮 > RUN "examples/demo.uscript"
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
