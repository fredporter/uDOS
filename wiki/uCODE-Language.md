# uCODE User Manual
## uDOS v1.0.0 Command Language Reference

### Overview
uCODE is the internal command language for uDOS. It provides a structured syntax for file operations, AI integration, multi-panel management, system control, and map navigation.

### Command Contexts

#### **CLI Context (Terminal/Interactive)**
Direct commands - case insensitive input, themed output:
```
HELP                          ~ Show general help
CATALOG                       ~ List files in current directory
LOAD "README.MD"              ~ Load file into main panel
ASK "What is uDOS?"           ~ Query AI (online) or offline engine
MAP STATUS                    ~ Show current map position
```

#### **Script Context (uSCRIPT Files)**
uCODE format with brackets for automation:
```
[FILE|LIST*.*main]            ~ List files to main panel
[FILE|LOAD*README.MD*docs]    ~ Load file to docs panel
[AI|ASK*Explain this*main]    ~ Ask AI with context from panel
[MAP|MOVE*5*3]                ~ Move on map grid
[SYSTEM|REBOOT]               ~ Restart system
```

#### **Conditional Context (Setup Scripts)**
uCODE with IF/THEN/ELSE logic:
```
IF USER.NAME IS_EMPTY THEN
  PROMPT "Enter your name" INTO USER.NAME
ENDIF

IF FILE_EXISTS "config.json" THEN
  LOAD_JSON "config.json" INTO CONFIG
ELSE
  ERROR "Configuration file not found"
ENDIF
```

### Command Syntax Rules

**CLI Format (Terminal):**
```
COMMAND [PARAMETER] [OPTION] [VALUE]
```

**uCODE Format (Scripts):**
```
[MODULE|COMMAND*PARAMETER_1*PARAMETER_2*...]
```

**Conditional Format (Setup Scripts):**
```
IF CONDITION THEN
  COMMANDS
ELSE
  COMMANDS
ENDIF
```

**Components:**
- MODULE : System module (FILE, AI, GRID, SYSTEM, MAP)
- COMMAND : Primary operation (required)
- PARAMETER : Command arguments (separated by *)
- OPTION : Modifiers (TO, FROM, etc.)

**Examples:**
```
# CLI Context
CATALOG "data"                ~ List data directory
LOAD "file.txt" TO "notes"    ~ Load to specific panel
ASK "Summarize" FROM "main"   ~ AI query with context
MOVE 5 3                      ~ Move on map

# uCODE Context
[FILE|LIST*data*main]         ~ List data to main panel
[FILE|LOAD*file.txt*notes]    ~ Load to notes panel
[AI|ASK*Summarize*main]       ~ AI query from main panel
[MAP|MOVE*5*3]                ~ Move on map grid
```

---

## Core Commands

### File Operations (FILE Module)
| CLI Command | uCODE | Description | Parameters |
|-------------|-------|-------------|------------|
| CATALOG | [FILE\|LIST*./*main] | List directory contents | path, panel |
| CATALOG "path" | [FILE\|LIST*path*main] | List specific directory | path, panel |
| CATALOG "path" TO "panel" | [FILE\|LIST*path*panel] | List to specific panel | path, panel |
| LOAD "file" | [FILE\|LOAD*file*main] | Load file to main panel | file, panel |
| LOAD "file" TO "panel" | [FILE\|LOAD*file*panel] | Load file to panel | file, panel |
| SAVE "panel" TO "file" | [FILE\|SAVE*panel*file] | Save panel to file | panel, file |
| EDIT "file" | [SYSTEM\|EDIT*file] | Open file in editor | file |

**File Operation Examples:**
```bash
# CLI Context
CATALOG                       ~ List current directory
CATALOG "data"                ~ List data directory
CATALOG "." TO "files"        ~ List to files panel
LOAD "README.MD"              ~ Load to main panel
LOAD "config.json" TO "cfg"   ~ Load to cfg panel
SAVE "notes" TO "output.txt"  ~ Save notes panel
EDIT "script.uscript"         ~ Edit script file

# uCODE Context
[FILE|LIST*.*main]            ~ List current to main
[FILE|LIST*data*main]         ~ List data to main
[FILE|LIST*.*files]           ~ List to files panel
[FILE|LOAD*README.MD*main]    ~ Load to main
[FILE|LOAD*config.json*cfg]   ~ Load to cfg panel
[FILE|SAVE*notes*output.txt]  ~ Save notes
[SYSTEM|EDIT*script.uscript]  ~ Edit script
```

### Grid Management (GRID Module)
| CLI Command | uCODE | Description | Parameters |
|-------------|-------|-------------|------------|
| GRID PANEL CREATE "name" | [GRID\|PANEL*CREATE*name] | Create new panel | name |
| GRID PANELS LIST | [GRID\|PANELS*LIST] | List all panels | none |
| SHOW "panel" | [GRID\|SHOW*panel] | Display panel contents | panel |
| GRID PANEL DELETE "name" | [GRID\|PANEL*DELETE*name] | Delete panel | name |

**Grid Examples:**
```bash
# CLI Context
GRID PANEL CREATE "notes"    ~ Create notes panel
GRID PANEL CREATE "temp"     ~ Create temp panel
GRID PANELS LIST             ~ List all panels
SHOW "main"                  ~ Show main panel
SHOW "notes"                 ~ Show notes panel
GRID PANEL DELETE "temp"     ~ Delete temp panel

# uCODE Context
[GRID|PANEL*CREATE*notes]    ~ Create notes panel
[GRID|PANEL*CREATE*temp]     ~ Create temp panel
[GRID|PANELS*LIST]           ~ List all panels
[GRID|SHOW*main]             ~ Show main panel
[GRID|SHOW*notes]            ~ Show notes panel
[GRID|PANEL*DELETE*temp]     ~ Delete temp panel
```

### AI Integration (AI Module)
| CLI Command | uCODE | Description | Parameters |
|-------------|-------|-------------|------------|
| ASK "question" | [AI\|ASK*question*null] | Query AI/offline engine | question, panel |
| ASK "question" FROM "panel" | [AI\|ASK*question*panel] | Query with context | question, panel |
| ANALYZE "panel" | [AI\|ANALYZE*panel] | Offline content analysis | panel |

**AI Examples:**
```bash
# CLI Context
ASK "What is uDOS?"          ~ Simple AI query
ASK "Explain this code" FROM "main" ~ Query with context
ASK "Summarize the file"     ~ File summary
ANALYZE "main"               ~ Offline analysis

# uCODE Context
[AI|ASK*What is uDOS?*null]  ~ Simple AI query
[AI|ASK*Explain this code*main] ~ Query with context
[AI|ASK*Summarize the file*null] ~ File summary
[AI|ANALYZE*main]            ~ Offline analysis
```

**Online vs Offline:**
- **ONLINE**: Uses Gemini API (requires API key)
- **OFFLINE**: Uses pattern-matching engine (no API needed)
- **LIMITED**: Partial connectivity (some features available)

### System Commands (SYSTEM Module)
| CLI Command | uCODE | Description | Parameters |
|-------------|-------|-------------|------------|
| REBOOT | [SYSTEM\|REBOOT] | Restart uDOS with checks | none |
| RESTART | [SYSTEM\|REBOOT] | Alias for REBOOT | none |
| STATUS | [SYSTEM\|STATUS] | System status report | none |
| VIEWPORT | [SYSTEM\|VIEWPORT] | Display viewport info | none |
| PALETTE | [SYSTEM\|PALETTE] | Show color palette | none |
| REPAIR | [SYSTEM\|REPAIR*ALL] | Auto-repair system | component |
| REPAIR DEPENDENCIES | [SYSTEM\|REPAIR*DEPENDENCIES] | Fix dependencies | component |
| REPAIR FILES | [SYSTEM\|REPAIR*FILES] | Fix file structure | component |
| SETUP | [SYSTEM\|SETUP] | Run setup wizard | none |
| RUN "script" | [SYSTEM\|RUN*script] | Execute script file | script |
| HELP | [SYSTEM\|HELP*ALL] | Show help | command |
| HELP "command" | [SYSTEM\|HELP*command] | Command-specific help | command |
| CLS | [SYSTEM\|CLS] | Clear screen | none |
| CLEAR | [SYSTEM\|CLS] | Alias for CLS | none |

**System Examples:**
```bash
# CLI Context
REBOOT                       ~ Restart with pre-flight checks
STATUS                       ~ Show system status
VIEWPORT                     ~ Display terminal specs
PALETTE                      ~ Show color palette
REPAIR                       ~ Auto-repair system
REPAIR DEPENDENCIES          ~ Fix missing packages
SETUP                        ~ Run setup wizard
RUN "shakedown.uscript"      ~ Execute script
HELP                         ~ General help
HELP LOAD                    ~ Help for LOAD command
CLS                          ~ Clear screen

# uCODE Context
[SYSTEM|REBOOT]              ~ Restart system
[SYSTEM|STATUS]              ~ System status
[SYSTEM|VIEWPORT]            ~ Viewport info
[SYSTEM|PALETTE]             ~ Color palette
[SYSTEM|REPAIR*ALL]          ~ Auto-repair
[SYSTEM|REPAIR*DEPENDENCIES] ~ Fix deps
[SYSTEM|SETUP]               ~ Setup wizard
[SYSTEM|RUN*shakedown.uscript] ~ Run script
[SYSTEM|HELP*ALL]            ~ General help
[SYSTEM|HELP*LOAD]           ~ LOAD help
[SYSTEM|CLS]                 ~ Clear screen
```

### History & Recovery (SYSTEM Module)
| CLI Command | uCODE | Description | Parameters |
|-------------|-------|-------------|------------|
| UNDO | [SYSTEM\|UNDO] | Undo last action | none |
| REDO | [SYSTEM\|REDO] | Redo last undo | none |
| RESTORE | [SYSTEM\|RESTORE*null] | Restore previous session | session |
| RESTORE session_num | [SYSTEM\|RESTORE*session_num] | Restore specific session | session |

**History Examples:**
```bash
# CLI Context
UNDO                         ~ Undo last operation
REDO                         ~ Redo last undo
RESTORE                      ~ Restore previous session
RESTORE 25                   ~ Restore session #25

# uCODE Context
[SYSTEM|UNDO]                ~ Undo last operation
[SYSTEM|REDO]                ~ Redo last undo
[SYSTEM|RESTORE*null]        ~ Restore previous
[SYSTEM|RESTORE*25]          ~ Restore session 25
```

### Map Navigation (MAP Module)
| CLI Command | uCODE | Description | Parameters |
|-------------|-------|-------------|------------|
| MAP | [MAP\|STATUS] | Show map status | none |
| MAP STATUS | [MAP\|STATUS] | Show position/layer | none |
| MAP VIEW | [MAP\|VIEW] | Show ASCII map | none |
| GOTO x y | [MAP\|GOTO*x*y] | Teleport to coordinates | x, y |
| MOVE dx dy | [MAP\|MOVE*dx*dy] | Move relative | dx, dy |
| LAYER | [MAP\|LAYER] | List available layers | none |
| DESCEND | [MAP\|DESCEND] | Go down one layer | none |
| ASCEND | [MAP\|ASCEND] | Go up one layer | none |
| LOCATE | [MAP\|LOCATE] | Show real-world location | none |
| WHERE | [MAP\|WHERE] | Alias for LOCATE | none |

**Map Examples:**
```bash
# CLI Context
MAP                          ~ Show map status
MAP STATUS                   ~ Position and layer info
MAP VIEW                     ~ Display ASCII map
GOTO 10 5                    ~ Teleport to (10, 5)
MOVE 1 0                     ~ Move east
MOVE 0 -1                    ~ Move north
MOVE 5 3                     ~ Move 5 east, 3 south
LAYER                        ~ List layers
DESCEND                      ~ Go down (SURFACE → DUNGEON-1)
ASCEND                       ~ Go up (DUNGEON-1 → SURFACE)
LOCATE                       ~ Show real-world location
WHERE                        ~ Alias for LOCATE

# uCODE Context
[MAP|STATUS]                 ~ Map status
[MAP|STATUS]                 ~ Position/layer
[MAP|VIEW]                   ~ ASCII map
[MAP|GOTO*10*5]              ~ Teleport
[MAP|MOVE*1*0]               ~ Move east
[MAP|MOVE*0*-1]              ~ Move north
[MAP|MOVE*5*3]               ~ Move diagonal
[MAP|LAYER]                  ~ List layers
[MAP|DESCEND]                ~ Go down
[MAP|ASCEND]                 ~ Go up
[MAP|LOCATE]                 ~ Location
[MAP|WHERE]                  ~ Location alias
```

**Map Layers (8 levels):**
```
SATELLITE  (+100)  ~ Space view
CLOUD      (+50)   ~ Aerial view
SURFACE    (0)     ~ Ground level (default)
DUNGEON-1  (-10)   ~ First underground
DUNGEON-2  (-20)   ~ Deeper underground
DUNGEON-3  (-30)   ~ Even deeper
MINES      (-50)   ~ Mining level
CORE       (-100)  ~ Bottom level
```

---

## uCODE Scripting (Advanced)

### Conditional Logic
| Statement | Syntax | Description |
|-----------|--------|-------------|
| IF | IF condition THEN | Start conditional block |
| ELSE | ELSE | Alternative block |
| ENDIF | ENDIF | End conditional block |

**Conditional Operators:**
```
EMPTY              ~ Field is empty
NOT_EMPTY          ~ Field has value
EQUALS             ~ Field equals value
NOT_EQUALS         ~ Field not equal to value
FILE_EXISTS        ~ File exists
FILE_MISSING       ~ File doesn't exist
```

**Conditional Examples:**
```ucode
# Check if user name is set
IF USER.NAME IS_EMPTY THEN
  PROMPT "Enter your name" INTO USER.NAME
ENDIF

# Check file existence
IF FILE_EXISTS "config.json" THEN
  LOAD_JSON "config.json" INTO CONFIG
ELSE
  ERROR "Configuration missing"
  COPY "config.template" TO "config.json"
ENDIF

# Nested conditions
IF USER.THEME EQUALS "DUNGEON_CRAWLER" THEN
  IF USER.LOCATION IS_EMPTY THEN
    SET_VAR "LOCATION" "Unknown Realm"
  ENDIF
ELSE
  SET_VAR "LOCATION" "Digital Space"
ENDIF
```

### Variable Operations
| Command | Syntax | Description |
|---------|--------|-------------|
| SET_VAR | SET_VAR "name" "value" | Set variable |
| PROMPT | PROMPT "question" INTO VAR | Get user input |
| GET_FIELD | GET_FIELD "path" FROM JSON | Get JSON field |
| SET_FIELD | SET_FIELD "path" TO "value" IN JSON | Set JSON field |

**Variable Examples:**
```ucode
# Set variables
SET_VAR "THEME" "DUNGEON_CRAWLER"
SET_VAR "USERNAME" "adventurer"

# Get user input
PROMPT "Enter project name" INTO PROJECT_NAME
PROMPT "Choose theme" INTO THEME

# JSON operations
LOAD_JSON "USER.UDO" INTO USER
GET_FIELD "USER_PROFILE.NAME" FROM USER
SET_FIELD "USER_PROFILE.THEME" TO "CYBERPUNK" IN USER
SAVE_JSON USER TO "USER.UDO"

# Variable substitution
DISPLAY "Welcome {USERNAME}!"
DISPLAY "Theme: {THEME}"
LOG "User {USERNAME} logged in at {TIMESTAMP}"
```

### System Functions
| Function | Syntax | Description |
|----------|--------|-------------|
| DISPLAY | DISPLAY "message" | Show message to user |
| LOG | LOG "message" | Write to log |
| ERROR | ERROR "message" | Show error |
| WARNING | WARNING "message" | Show warning |
| TIMESTAMP | {TIMESTAMP} | Current timestamp |
| DETECT_TIMEZONE | DETECT_TIMEZONE | Get system timezone |
| CHECK_FILE | CHECK_FILE "path" | Check if file exists |
| EXIT | EXIT | Exit script |

**System Function Examples:**
```ucode
# Display messages
DISPLAY "Setup starting..."
LOG "Configuration initialized"
ERROR "Missing required field"
WARNING "Using default value"

# Timestamps
DISPLAY "Started at {TIMESTAMP}"
LOG "Session created: {TIMESTAMP}"

# Timezone detection
DETECT_TIMEZONE
SET_FIELD "USER_PROFILE.TIMEZONE" TO "{DETECTED_TIMEZONE}" IN USER

# File operations
CHECK_FILE "data/config.json"
IF FILE_EXISTS THEN
  DISPLAY "Configuration found"
ELSE
  DISPLAY "Creating default configuration"
  COPY "templates/config.json" TO "data/config.json"
ENDIF
```

### JSON Manipulation
| Command | Description | Example |
|---------|-------------|---------|
| LOAD_JSON | Load JSON file | LOAD_JSON "USER.UDO" INTO USER |
| SAVE_JSON | Save JSON file | SAVE_JSON USER TO "USER.UDO" |
| GET_FIELD | Get field value | GET_FIELD "PROFILE.NAME" FROM USER |
| SET_FIELD | Set field value | SET_FIELD "PROFILE.NAME" TO "Fred" IN USER |

**Dot Notation:**
```
USER_PROFILE.NAME              ~ Access nested field
USER_PROFILE.WORLD_LOCATION.CITY ~ Deep nesting
LOCATION_DATA.MAP_POSITION.X   ~ Multi-level access
```

**JSON Examples:**
```ucode
# Load user profile
LOAD_JSON "sandbox/USER.UDO" INTO USER

# Get fields
GET_FIELD "USER_PROFILE.NAME" FROM USER
GET_FIELD "USER_PROFILE.TIMEZONE" FROM USER
GET_FIELD "WORLD_LOCATION.CITY" FROM USER

# Set fields
SET_FIELD "USER_PROFILE.NAME" TO "fredbook" IN USER
SET_FIELD "USER_PROFILE.THEME" TO "CYBERPUNK" IN USER
SET_FIELD "WORLD_LOCATION.CITY" TO "New York" IN USER

# Save changes
SAVE_JSON USER TO "sandbox/USER.UDO"

# Nested operations
GET_FIELD "LOCATION_DATA.MAP_POSITION.X" FROM USER
SET_FIELD "LOCATION_DATA.MAP_POSITION.LAYER" TO "SURFACE" IN USER
```

### Field Validation Patterns
| Pattern | Description | Example |
|---------|-------------|---------|
| REQUIRED | Must be filled | USER_NAME is REQUIRED |
| DEFAULT | Auto-fill if empty | TIMEZONE default: UTC |
| OPTIONAL | Can be empty | DESCRIPTION is OPTIONAL |

**Validation Examples:**
```ucode
# REQUIRED field (must be entered)
IF USER.NAME IS_EMPTY THEN
  PROMPT "Enter your name (required)" INTO USER.NAME
  IF USER.NAME IS_EMPTY THEN
    ERROR "Name is required"
    EXIT
  ENDIF
ENDIF

# DEFAULT field (auto-fill)
IF USER.TIMEZONE IS_EMPTY THEN
  DETECT_TIMEZONE
  SET_FIELD "USER_PROFILE.TIMEZONE" TO "{DETECTED_TIMEZONE}" IN USER
  DISPLAY "Using detected timezone: {DETECTED_TIMEZONE}"
ENDIF

# OPTIONAL field (can skip)
IF USER.DESCRIPTION IS_EMPTY THEN
  PROMPT "Enter description (optional, press Enter to skip)" INTO DESCRIPTION
  IF DESCRIPTION NOT_EMPTY THEN
    SET_FIELD "PROJECT.DESCRIPTION" TO "{DESCRIPTION}" IN USER
  ENDIF
ENDIF
```

---

## Character Usage Rules

### uCODE Special Characters
```
~ Operators:
|  ~ Module separator: [MODULE|COMMAND]
*  ~ Parameter separator: [MODULE|COMMAND*PARAM1*PARAM2]
"  ~ String delimiter: LOAD "file.txt"
{} ~ Variable substitution: {USERNAME}

~ Comments:
# This is a comment                    ~ Full line comment
LOAD "file.txt"                        ~ End-of-line comment supported in docs

~ Paths and Strings:
"path/to/file"                         ~ Use quotes for paths
"text with spaces"                     ~ Use quotes for strings with spaces
```

### Character Avoidance Rules
```
~ Avoid in regular operations:
[]  ~ Reserved for uCODE brackets
<>  ~ Reserved for future use
$   ~ Reserved for shell variables
&   ~ Reserved for future operators
%   ~ Reserved for future operators

~ Preferred formats:
"Press ENTER to continue"              ~ Not: "Press [Enter]"
LOAD "README.MD"                       ~ Not: LOAD README.MD (without quotes)
{USERNAME}                             ~ Not: $USERNAME
```

### Formatting Rules
```
# Commands: UPPERCASE (case-insensitive input)
LOAD SAVE CATALOG ASK MAP REBOOT      ~ Commands in UPPERCASE
GRID PANEL CREATE                      ~ Multi-word commands
MOVE GOTO DESCEND ASCEND              ~ Map navigation commands

# Parameters: Quoted strings or bare words
LOAD "README.MD"                       ~ File paths in quotes
CATALOG "data"                         ~ Directory paths in quotes
GOTO 10 5                              ~ Numeric parameters bare
MOVE 5 3                               ~ Movement offsets bare

# Variables: {CAPS_WITH_UNDERSCORES}
{USERNAME}                             ~ Variable reference
{PROJECT_NAME}                         ~ Multi-word variable
{DETECTED_TIMEZONE}                    ~ System variable
{TIMESTAMP}                            ~ Built-in function

# Themed output: Varies by lexicon
✅ SUCCESS: File loaded                ~ Dungeon Crawler theme
📝 Scroll unfurled into 'main'        ~ Fantasy-themed success
```

---

## Quick Reference

### Most Common Commands
```bash
# CLI Context (Terminal)
HELP                         ~ Get help
CATALOG                      ~ List files
LOAD "file"                  ~ Load file
SHOW "panel"                 ~ Show panel
ASK "question"               ~ Query AI
MAP STATUS                   ~ Map position
STATUS                       ~ System status
REBOOT                       ~ Restart system

# uCODE Context (Scripts)
[SYSTEM|HELP*ALL]            ~ Get help
[FILE|LIST*.*main]           ~ List files
[FILE|LOAD*file*main]        ~ Load file
[GRID|SHOW*panel]            ~ Show panel
[AI|ASK*question*null]       ~ Query AI
[MAP|STATUS]                 ~ Map position
[SYSTEM|STATUS]              ~ System status
[SYSTEM|REBOOT]              ~ Restart system
```

### Module-Specific Commands
```bash
# FILE Module - CLI
CATALOG "data"               ~ List directory
LOAD "file.txt" TO "notes"   ~ Load to panel
SAVE "notes" TO "output.txt" ~ Save panel
EDIT "script.uscript"        ~ Edit file

# FILE Module - uCODE
[FILE|LIST*data*main]        ~ List directory
[FILE|LOAD*file.txt*notes]   ~ Load to panel
[FILE|SAVE*notes*output.txt] ~ Save panel
[SYSTEM|EDIT*script.uscript] ~ Edit file

# GRID Module - CLI
GRID PANEL CREATE "temp"     ~ Create panel
GRID PANELS LIST             ~ List panels
SHOW "main"                  ~ Display panel
GRID PANEL DELETE "temp"     ~ Delete panel

# GRID Module - uCODE
[GRID|PANEL*CREATE*temp]     ~ Create panel
[GRID|PANELS*LIST]           ~ List panels
[GRID|SHOW*main]             ~ Display panel
[GRID|PANEL*DELETE*temp]     ~ Delete panel

# AI Module - CLI
ASK "What is uDOS?"          ~ Simple query
ASK "Explain" FROM "main"    ~ Query with context
ANALYZE "main"               ~ Offline analysis

# AI Module - uCODE
[AI|ASK*What is uDOS?*null]  ~ Simple query
[AI|ASK*Explain*main]        ~ Query with context
[AI|ANALYZE*main]            ~ Offline analysis

# MAP Module - CLI
MAP STATUS                   ~ Position/layer
GOTO 10 5                    ~ Teleport
MOVE 5 3                     ~ Move relative
DESCEND                      ~ Go down layer
ASCEND                       ~ Go up layer

# MAP Module - uCODE
[MAP|STATUS]                 ~ Position/layer
[MAP|GOTO*10*5]              ~ Teleport
[MAP|MOVE*5*3]               ~ Move relative
[MAP|DESCEND]                ~ Go down
[MAP|ASCEND]                 ~ Go up
```

### Scripting Commands
```ucode
# Conditional Logic
IF USER.NAME IS_EMPTY THEN
  PROMPT "Enter name" INTO USER.NAME
ENDIF

IF FILE_EXISTS "config.json" THEN
  LOAD_JSON "config.json" INTO CONFIG
ELSE
  ERROR "Config missing"
ENDIF

# Variables
SET_VAR "THEME" "DUNGEON_CRAWLER"
PROMPT "Enter value" INTO MYVAR
DISPLAY "Hello {USERNAME}!"

# JSON Operations
LOAD_JSON "USER.UDO" INTO USER
GET_FIELD "PROFILE.NAME" FROM USER
SET_FIELD "PROFILE.THEME" TO "CYBERPUNK" IN USER
SAVE_JSON USER TO "USER.UDO"

# System Functions
DISPLAY "Message to user"
LOG "Log entry"
ERROR "Error message"
WARNING "Warning message"
DETECT_TIMEZONE
CHECK_FILE "path"
EXIT
```

### Emergency Commands
```bash
# CLI Context
REPAIR                       ~ Auto-fix problems
REPAIR DEPENDENCIES          ~ Fix packages
REPAIR FILES                 ~ Fix file structure
RESTORE                      ~ Restore session
UNDO                         ~ Undo last action
REBOOT                       ~ Restart with checks

# uCODE Context
[SYSTEM|REPAIR*ALL]          ~ Auto-fix
[SYSTEM|REPAIR*DEPENDENCIES] ~ Fix packages
[SYSTEM|REPAIR*FILES]        ~ Fix files
[SYSTEM|RESTORE*null]        ~ Restore session
[SYSTEM|UNDO]                ~ Undo action
[SYSTEM|REBOOT]              ~ Restart
```

---

## Connection Modes

### ONLINE Mode
- ✅ Full Gemini API access
- ✅ Advanced AI queries
- ✅ Internet connectivity
- ✅ Real-time responses

**Commands Available:**
```bash
ASK "Complex question"       ~ Full AI power
ASK "Analyze code" FROM "main" ~ Context-aware
```

### OFFLINE Mode
- ✅ Pattern-matching engine
- ✅ Local content analysis
- ✅ No internet required
- ✅ Instant responses

**Commands Available:**
```bash
ANALYZE "panel"              ~ Content analysis
ASK "Basic question"         ~ Pattern matching
```

### LIMITED Mode
- ⚠️ Partial connectivity
- ⚠️ Some features available
- ⚠️ Fallback to offline
- ⚠️ Reduced functionality

**Commands Available:**
```bash
STATUS                       ~ Check mode
CATALOG                      ~ File operations
LOAD/SAVE                    ~ Panel operations
```

---

## Themed Commands (Lexicon)

### Dungeon Crawler Theme
| Standard | Themed | Description |
|----------|--------|-------------|
| LOAD | CAST | Cast scroll spell |
| SAVE | SCRIBE | Scribe to scroll |
| CATALOG | ZAP | Zap to reveal |
| ASK | CONSULT | Consult oracle |
| MOVE | WALK | Walk in dungeon |

**Theme Examples:**
```bash
# Standard commands (always work)
LOAD "file.txt"
SAVE "panel" TO "output.txt"
CATALOG "data"

# Themed equivalents (Dungeon Crawler)
CAST "file.txt"              ~ Same as LOAD
SCRIBE "panel" TO "output.txt" ~ Same as SAVE
ZAP "data"                   ~ Same as CATALOG
```

### Cyberpunk Theme
| Standard | Themed | Description |
|----------|--------|-------------|
| LOAD | JACK | Jack into file |
| CATALOG | SCAN | Scan directory |
| MAP | TRACE | Trace grid |

**Theme Examples:**
```bash
JACK "data.txt"              ~ Load file (cyberpunk)
SCAN "directory"             ~ List directory
TRACE STATUS                 ~ Map status
```

---

## Tab Completion

### Smart Completion System
```bash
# Command completion
LO[Tab]                      → LOAD
CA[Tab]                      → CATALOG
MA[Tab]                      → MAP

# File path completion
LOAD "[Tab]                  → Shows available files
EDIT "[Tab]                  → Shows .uscript files
RUN "[Tab]                   → Shows script files

# Panel completion
SHOW "[Tab]                  → Shows panel names
SAVE "[Tab]                  → Shows panel names

# Trigger character
[                            → Opens command menu instantly
```

### Context-Aware Hints
```bash
# After LOAD
✅ File loaded into 'main'
💡 Try: SHOW "main"

# After MAP
👣 Moved to (5, 3)
💡 Try: MAP VIEW

# After panel create
✅ Panel 'notes' created
💡 Try: LOAD "file.txt" TO "notes"
```

---

## Best Practices

### Script Organization
```ucode
# Header with description
# Script: SETUP.USC
# Purpose: Initialize user profile
# Author: uDOS Team

# Validate required fields
IF USER.NAME IS_EMPTY THEN
  PROMPT "Enter your name" INTO USER.NAME
ENDIF

# Set defaults
IF USER.TIMEZONE IS_EMPTY THEN
  DETECT_TIMEZONE
  SET_FIELD "PROFILE.TIMEZONE" TO "{DETECTED_TIMEZONE}" IN USER
ENDIF

# Save configuration
SAVE_JSON USER TO "USER.UDO"
DISPLAY "Setup complete!"
```

### Error Handling
```ucode
# Check file existence
IF FILE_MISSING "config.json" THEN
  ERROR "Configuration file not found"
  DISPLAY "Creating default configuration..."
  COPY "templates/config.json" TO "config.json"
ENDIF

# Validate user input
PROMPT "Enter value" INTO VALUE
IF VALUE IS_EMPTY THEN
  WARNING "No value entered, using default"
  SET_VAR "VALUE" "default"
ENDIF
```

### Variable Naming
```ucode
# Good variable names (descriptive, CAPS)
{USERNAME}
{PROJECT_NAME}
{THEME_SELECTION}
{MAP_POSITION_X}

# Avoid (ambiguous, lowercase)
{user}
{name}
{x}
{temp}
```

---

## See Also

- [Command Reference](Command-Reference) - All commands with examples
- [Architecture](Architecture) - System design
- [Script Automation](Script-Automation) - Writing scripts
- [Tutorials](Tutorials) - Step-by-step guides
- [FAQ](FAQ) - Common questions

---

*uCODE Manual v1.0.0 | Last updated: November 2025* 🔮
