# uDOS Architecture

Understanding the internal structure of uDOS v1.0.0

---

## System Design Philosophy

uDOS is built on three core principles:

1. **Separation of Concerns**: User interface, parsing, and execution are distinct
2. **Human-Readable First**: Commands read like natural language
3. **Educational Transparency**: Code is clear and well-documented

---

## High-Level Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                         USER INPUT                          │
│              "LOAD 'README.MD' TO 'docs'"                   │
└──────────────────────┬──────────────────────────────────────┘
                       │
                       ▼
┌─────────────────────────────────────────────────────────────┐
│                    PARSER (uDOS_parser.py)                  │
│  • Command decomposition                                    │
│  • Lexicon theming                                          │
│  • uCODE generation                                         │
└──────────────────────┬──────────────────────────────────────┘
                       │
                       ▼
                 [FILE|LOAD*README.MD*docs]
                       │
                       ▼
┌─────────────────────────────────────────────────────────────┐
│               COMMAND HANDLER (uDOS_commands.py)            │
│  • Module routing (FILE, AI, GRID, SYSTEM, MAP)            │
│  • Parameter validation                                     │
│  • Execution logic                                          │
└──────────────────────┬──────────────────────────────────────┘
                       │
        ┌──────────────┼──────────────┬──────────────┐
        │              │               │              │
        ▼              ▼               ▼              ▼
┌──────────┐  ┌──────────────┐  ┌──────────┐  ┌──────────┐
│   FILE   │  │     GRID     │  │    AI    │  │   MAP    │
│  SYSTEM  │  │   SYSTEM     │  │  ENGINE  │  │  ENGINE  │
└──────────┘  └──────────────┘  └──────────┘  └──────────┘
```

---

## Data Structure

uDOS v1.0.0 uses a JSON-based data architecture with clear separation between system files, user data, and runtime memory.

### Directory Organization

```
data/
├── system/           # System configuration (read-only)
│   ├── commands.json       # Command definitions
│   ├── palette.json        # Color schemes
│   ├── fonts.json          # ASCII art fonts
│   ├── worldmap.json       # City database
│   ├── extensions.json     # Extension registry
│   └── credits.json        # Attribution
│
├── themes/           # Visual themes (read-only)
│   ├── _index.json         # Theme registry
│   ├── dungeon.json        # Dungeon Crawler theme
│   ├── galaxy.json         # Galactic Voyager theme
│   ├── foundation.json     # Foundation theme
│   ├── science.json        # Science theme
│   └── project.json        # Project theme
│
└── templates/        # User data templates
    ├── user.template.json  # Profile template
    ├── story.template.json # Story template
    └── setup.uscript       # First-time setup script

knowledge/
└── system/
    └── faq.json            # Help system & AI prompts

memory/
├── user.json               # Active user profile
├── story.json              # Current story state
├── config/
│   └── active-theme.json   # Current theme selection
└── logs/
    └── sessions/           # Session logs
```

### System Files (`data/system/`)

**Purpose**: Core configuration that defines uDOS behavior

- **`commands.json`** - All available commands with syntax, parameters, and uCODE templates
- **`palette.json`** - ANSI color codes and named color schemes
- **`fonts.json`** - ASCII art font definitions for FIGLET command
- **`worldmap.json`** - Global city database with coordinates and timezones
- **`extensions.json`** - Registry of installed extensions (native/web)
- **`credits.json`** - Attribution and acknowledgments

**Validation**: Health checks verify JSON structure at startup

### Theme Files (`data/themes/`)

**Purpose**: Visual theming with custom terminology and aesthetics

Each theme includes:
- **Lexicon**: Command aliases (e.g., "SUMMON" → "LOAD" in Dungeon Crawler)
- **Color Palette**: Theme-specific color schemes
- **Prompts**: Themed prompt templates
- **Splash**: ASCII art welcome screen

**Theme Index** (`_index.json`):
```json
{
  "themes": [
    {"id": "dungeon", "name": "Dungeon Crawler", "file": "dungeon.json"},
    {"id": "galaxy", "name": "Galactic Voyager", "file": "galaxy.json"},
    ...
  ]
}
```

### Template Files (`data/templates/`)

**Purpose**: Default structures for user data initialization

- **`user.template.json`** - Default user profile structure (copied to `memory/user.json` on first run)
- **`story.template.json`** - Default story structure for narrative mode
- **`setup.uscript`** - Interactive uCODE script for profile configuration

**First-Time Setup Flow**:
1. Health check detects missing `memory/user.json`
2. Copy `user.template.json` → `memory/user.json`
3. Optionally run `setup.uscript` for interactive configuration
4. Save personalized data to `memory/` directory

### Knowledge Base (`knowledge/system/`)

**Purpose**: Context for AI and help systems

- **`faq.json`** - Merged FAQ entries and AI prompt templates
  - Structured Q&A for HELP command
  - Context prompts for Gemini AI integration
  - Troubleshooting guides

**Structure**:
```json
{
  "faq": [
    {
      "question": "How do I load a file?",
      "answer": "Use: LOAD \"filename.txt\"",
      "category": "files"
    }
  ],
  "prompts": {
    "system": "You are uDOS assistant...",
    "creative": "Help the user with..."
  }
}
```

### Runtime Memory (`memory/`)

**Purpose**: Active user data and session state

- **`user.json`** - Current user profile (name, location, preferences)
- **`story.json`** - Active story data (if in narrative mode)
- **`config/active-theme.json`** - Selected theme ID
- **`logs/sessions/`** - Timestamped session logs

**User Profile Structure**:
```json
{
  "USER_PROFILE": {
    "NAME": "fredbook",
    "TIMEZONE": "America/New_York",
    "THEME": "DUNGEON_CRAWLER"
  },
  "WORLD_LOCATION": {
    "CITY": "New York",
    "LATITUDE": 40.7128,
    "LONGITUDE": -74.0060
  }
}
```

### Migration from v0.x (.UDO Format)

**Old Structure** (deprecated):
```
data/
├── COMMANDS.UDO    → data/system/commands.json
├── THEMES.UDO      → data/themes/*.json (split into 5 files)
├── FAQ.UDO         → knowledge/system/faq.json
├── PROMPTS.UDO     → (merged into faq.json)
├── USER.UDT        → data/templates/user.template.json
└── SETUP.USC       → data/templates/setup.uscript

sandbox/
└── USER.UDO        → memory/user.json
```

**Benefits of JSON Migration**:
- ✅ Standard format with validation tools
- ✅ Better IDE support (syntax highlighting, autocomplete)
- ✅ Easier parsing and error detection
- ✅ Clear separation: system vs. user vs. runtime data
- ✅ Modular themes (load only what's needed)

---

## Core Components

### 1. Main Loop (`uDOS_main.py`)

**Purpose**: Application entry point and run loop

**Responsibilities**:
- Initialize all subsystems
- Detect execution mode (interactive vs. script)
- Handle REBOOT requests
- Manage session lifecycle

**Key Functions**:
- `main()` - Entry point
- `run_interactive_mode()` - REPL loop with smart completion
- `run_script_mode()` - Batch execution
- `initialize_systems()` - Boot sequence

---

### 2. Parser (`uDOS_parser.py`)

**Purpose**: Translate human-readable commands to uCODE

**Process**:
1. **Tokenize** - Split input into words/strings
2. **Match Command** - Look up in COMMANDS.UDO
3. **Apply Theme** - Translate themed terms (LEXICON.UDO)
4. **Generate uCODE** - Build structured internal format
5. **Validate** - Check parameter count and types

**Example**:
```python
Input:  'LOAD "README.MD" TO "docs"'
Tokens: ['LOAD', 'README.MD', 'TO', 'docs']
Match:  LOAD command template
uCODE:  [FILE|LOAD*README.MD*docs]
```

**Key Classes**:
- `Parser` - Main parser logic
- `CommandMatcher` - Pattern matching
- `ThemingEngine` - Lexicon application

---

### 3. Command Handler (`uDOS_commands.py`)

**Purpose**: Execute uCODE instructions

**Module Routing**:
- `[FILE|...]` → `handle_file_command()`
- `[GRID|...]` → `handle_grid_command()`
- `[AI|...]` → `handle_ai_command()`
- `[SYSTEM|...]` → `handle_system_command()`
- `[MAP|...]` → `handle_map_command()`

**Execution Flow**:
```python
def handle_command(ucode, grid, parser):
    # 1. Parse uCODE
    module, command, params = parse_ucode(ucode)

    # 2. Route to handler
    if module == "FILE":
        return handle_file_command(command, params, grid)
    elif module == "AI":
        return handle_ai_command(command, params, grid)
    # ... etc
```

**Key Classes**:
- `CommandHandler` - Main execution engine
- `ModuleRouter` - Dispatch logic

---

### 4. Grid System (`uDOS_grid.py`)

**Purpose**: Multi-panel text buffer management

**Concept**: Named text panels for organizing data

**Operations**:
- `create_panel(name)` - Create new panel
- `set_panel_content(name, text)` - Update panel
- `get_panel_content(name)` - Retrieve text
- `list_panels()` - Show all panels
- `delete_panel(name)` - Remove panel

**Use Cases**:
- Load multiple files simultaneously
- Organize different data types
- Compare content side-by-side
- Temporary working buffers

---

### 5. AI Integration (`uDOS_commands.py`)

**Purpose**: Gemini API interaction with offline fallback

**Online Mode** (Gemini API):
```python
def handle_ai_command(command, params, grid):
    if connection.is_online():
        response = gemini.generate_content(prompt)
        return response.text
    else:
        return offline_engine.generate_response(prompt)
```

**Offline Mode** (Pattern Matching):
- Uses `uDOS_offline.py` for local logic
- Editable prompts in `data/PROMPTS.UDO`
- Pattern-based responses

---

### 6. Connection Awareness (`uDOS_connection.py`)

**Purpose**: Detect and adapt to network status

**Modes**:
- **ONLINE** - Full internet access, Gemini API available
- **OFFLINE** - No internet, uses local logic engine
- **LIMITED** - Partial connectivity (e.g., LAN only)

**Detection Methods**:
```python
def check_connectivity():
    # 1. Check internet access (Google DNS)
    # 2. Check Gemini API reachability
    # 3. Check local network
    # 4. Determine mode
```

---

### 7. Viewport System (`uDOS_viewport.py`)

**Purpose**: Terminal size detection and adaptation

**Device Classification**:
| Width | Height | Type |
|:------|:-------|:-----|
| 120+ | 40+ | DESKTOP |
| 80-119 | 30-39 | TABLET |
| <80 | <30 | MOBILE |

**Grid Calculation**:
```python
grid_width = (terminal_width - 4) // 16
grid_height = (terminal_height - 6) // 16
```

**Use Cases**:
- Adapt display density
- Optimize panel layouts
- Responsive ASCII art

---

### 8. Mapping System (`uDOS_map.py`)

**Purpose**: NetHack-inspired multi-layer navigation

**Layers** (8 levels):
```
SATELLITE  (+100)  ← Space view
CLOUD      (+50)   ← Aerial
SURFACE    (0)     ← Ground level (default)
DUNGEON-1  (-10)   ← First underground
DUNGEON-2  (-20)   ← Deeper
DUNGEON-3  (-30)   ← Even deeper
MINES      (-50)   ← Mining level
CORE       (-100)  ← Bottom
```

**Navigation**:
- `MOVE dx dy` - Horizontal movement
- `DESCEND` - Go down one layer
- `ASCEND` - Go up one layer
- `GOTO x y` - Teleport to coordinates

**Integration**:
- Real-world location (lat/lon → grid coordinates)
- City database (WORLDMAP.UDO)
- Timezone-aware positioning

---

### 9. Session Logging (`uDOS_logger.py`)

**Purpose**: Complete interaction history

**Log Format**:
```
[2025-10-30 20:53:28] INPUT: LOAD "README.MD"
[2025-10-30 20:53:28] OUTPUT: ✅ File loaded into 'main'
[2025-10-30 20:53:35] INPUT: SHOW "main"
[2025-10-30 20:53:35] OUTPUT: [file contents...]
```

**Location**: `sandbox/logs/session_YYYYMMDD_HHMMSS.log`

**Features**:
- Timestamped entries
- Input/output pairs
- Error tracking
- Session restoration

---

### 10. History Management (`uDOS_history.py`)

**Purpose**: UNDO/REDO capability

**Stack Structure**:
```python
undo_stack = [
    {'action': 'panel_create', 'data': {'name': 'test'}},
    {'action': 'panel_modify', 'data': {'name': 'main', 'old': '...'}},
    # ...
]
redo_stack = []  # Populated on UNDO
```

**Reversible Actions**:
- Panel creation/deletion
- Panel content modification
- File operations
- Grid state changes

---

### 11. User Profile (`uDOS_user.py`)

**Purpose**: Personal configuration and preferences

**Profile Structure** (`sandbox/USER.UDO`):
```json
{
  "USER_PROFILE": {
    "NAME": "fredbook",
    "TIMEZONE": "America/New_York",
    "THEME": "DUNGEON_CRAWLER",
    "LIFESPAN": "Infinite"
  },
  "WORLD_LOCATION": {
    "CITY": "New York",
    "LATITUDE": 40.7128,
    "LONGITUDE": -74.0060
  },
  "LOCATION_DATA": {
    "MAP_POSITION": {"X": 0, "Y": 0, "LAYER": "SURFACE"}
  }
}
```

---

### 12. System Health (`uDOS_health.py`)

**Purpose**: Dependency and integrity checks

**Checks**:
- ✅ Python version (3.9+)
- ✅ Required packages installed
- ✅ File structure intact
- ✅ Configuration files valid

**REPAIR Command**:
- Auto-install missing dependencies
- Recreate missing directories
- Restore template files
- Validate JSON configurations

---

## Data Flow Examples

### Example 1: Loading a File

```
User Input: LOAD "README.MD" TO "docs"
    ↓
Parser: Tokenize → Match command → Generate uCODE
    ↓
uCODE: [FILE|LOAD*README.MD*docs]
    ↓
CommandHandler: Route to handle_file_command()
    ↓
FileHandler: Read file → Store in grid
    ↓
Grid: Set panel "docs" content
    ↓
Logger: Record action
    ↓
History: Add to undo stack
    ↓
Output: "✅ File loaded into 'docs'"
```

### Example 2: AI Query (Online)

```
User Input: ASK "Explain Python decorators"
    ↓
Parser: [AI|ASK*Explain Python decorators*null]
    ↓
CommandHandler: Route to handle_ai_command()
    ↓
Connection: Check if online → Yes
    ↓
Gemini API: Send request
    ↓
Response: Receive AI-generated explanation
    ↓
Logger: Record I/O
    ↓
Output: [AI response text]
```

### Example 3: Map Navigation

```
User Input: MOVE 5 3
    ↓
Parser: [MAP|MOVE*5*3]
    ↓
CommandHandler: Route to handle_map_command()
    ↓
MapEngine: Update position (x+5, y+3)
    ↓
UserProfile: Save new position
    ↓
MapEngine: Generate ASCII map view
    ↓
Output: [Map display with new position marked]
```

---

## Configuration Files

### Commands Definition (`data/COMMANDS.UDO`)

Maps user commands to uCODE templates:

```json
{
  "NAME": "LOAD",
  "SYNTAX": "LOAD \"<file>\" [TO \"<panel>\"]",
  "DESCRIPTION": "Loads a file's content into a panel.",
  "UCODE_TEMPLATE": "[FILE|LOAD*$1*$2]",
  "DEFAULT_PARAMS": {
    "$2": "main"
  }
}
```

### Lexicon (`data/LEXICON.UDO`)

Themed terminology and messages:

```json
{
  "TERMINOLOGY": {
    "SUCCESS_LOAD": "✅ SUCCESS: Scroll unfurled into '{panel}'",
    "ERROR_FILE_NOT_FOUND": "❌ ERROR: No such scroll exists: '{file}'"
  }
}
```

### Palette (`data/PALETTE.UDO`)

Color system configuration:

```json
{
  "COLORS": {
    "red": {"tput": 196, "hex": "#FF1744"},
    "green": {"tput": 46, "hex": "#00E676"}
  }
}
```

---

## Design Patterns

### 1. Command Pattern
Each uCODE instruction is a command object executed by handlers.

### 2. Strategy Pattern
Connection mode determines AI execution strategy (online vs. offline).

### 3. Observer Pattern
Logger observes all I/O for recording.

### 4. Template Method
Parser uses command templates for uCODE generation.

### 5. Facade Pattern
CommandHandler provides simple interface to complex subsystems.

---

## Extension Points

### Add New Commands
1. Define in `data/COMMANDS.UDO`
2. Add handler in `uDOS_commands.py`
3. Update lexicon if themed

### Add New Module
1. Create `uDOS_mymodule.py`
2. Add routing in `CommandHandler`
3. Define uCODE format `[MYMODULE|...]`

### Custom Themes
1. Edit `data/LEXICON.UDO`
2. Define new terminology
3. Apply with user profile

---

## Performance Characteristics

| Operation | Time Complexity | Notes |
|:----------|:----------------|:------|
| Parse command | O(n) | n = command length |
| Execute uCODE | O(1) | Constant routing |
| Panel access | O(1) | Dictionary lookup |
| File load | O(f) | f = file size |
| AI query | O(network) | Depends on API |
| Map navigation | O(1) | Position update |

**Memory Usage**:
- Base system: ~10 MB
- Per panel: ~size of content
- Logs: Grows with session

---

## Next Steps

- [uCODE Language](uCODE-Language) - Deep dive into internal format
- [Parser Internals](Parser-Internals) - How parsing works
- [Extension Development](Extensions) - Build custom features
- [API Documentation](API-Documentation) - Complete API reference

---

*Understanding the architecture empowers you to extend and customize uDOS!* 🔮
