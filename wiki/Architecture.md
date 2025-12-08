# uDOS Architecture

**Version:** v1.2.21 (December 2025)

Internal structure of uDOS - survival knowledge, mapping, and workflow automation.

---

## System Design Philosophy

uDOS is built on five core principles:

1. **Offline-First**: Full functionality without internet/API keys
2. **Human-Readable**: Commands read like natural language
3. **Separation of Concerns**: UI, parsing, execution are distinct
4. **Modular**: Core system + optional extensions
5. **Educational**: Clear code, well-documented

---

## Core vs Extensions Architecture *(v1.2.12+)*

### Design Principle

**Core CLI**: Minimal, stable, fully-functional command-line interface
**Extensions**: Optional features that enhance but are not required

### Directory Structure (v1.2.12)

```
uDOS/
├── core/                    # Core CLI - Required
│   ├── uDOS_main.py         # Main loop
│   ├── uDOS_commands.py     # Command routing
│   ├── commands/            # Command handlers (49 handlers)
│   ├── data/                # System configuration, themes, templates
│   ├── docs/                # Core system documentation
│   ├── interpreters/        # uCODE, offline mode interpreters
│   ├── runtime/             # uPY runtime (v1.2.x)
│   ├── services/            # Core services (config, knowledge, etc)
│   ├── ui/                  # UI components (file picker, etc)
│   └── utils/               # Core utilities
│
├── extensions/              # Optional Extensions
│   ├── assistant/           # AI assistant (Gemini integration)
│   ├── assets/              # Shared assets (fonts, icons, data)
│   ├── core/                # Core extensions (extension manager, server)
│   ├── play/                # Gameplay extensions (map engine, XP)
│   └── web/                 # Web interfaces (teletext, dashboard)
│
├── knowledge/               # Public knowledge bank (read-only)
│   ├── water/               # Water guides (26 files)
│   ├── fire/                # Fire guides (20 files)
│   ├── shelter/             # Shelter guides (20 files)
│   ├── food/                # Food guides (23 files)
│   ├── navigation/          # Navigation guides (20 files)
│   └── medical/             # Medical guides (27 files)
│
├── memory/                  # User workspace (gitignored except ucode/)
│   ├── ucode/               # Core distributable .upy scripts (tracked)
│   │   ├── scripts/         # User .upy scripts (ignored)
│   │   ├── tests/           # Test suites (tracked - v1.2.12)
│   │   ├── sandbox/         # Experimental scripts (ignored)
│   │   ├── stdlib/          # Standard library (tracked)
│   │   ├── examples/        # Example scripts (tracked)
│   │   └── adventures/      # Adventure scripts (tracked)
│   ├── workflows/           # Workflow automation (v1.2.20)
│   │   ├── missions/        # All mission scripts (.upy)
│   │   ├── checkpoints/     # Auto-saved state snapshots
│   │   ├── state/           # Current execution state and control
│   │   └── extensions/      # Gameplay/XP/achievement integration
│   ├── system/              # System files
│   │   ├── user/            # User settings (USER.UDT, profiles)
│   │   └── themes/          # Custom themes
│   ├── bank/                # Banking/barter system
│   ├── shared/              # Shared/community content
│   ├── docs/                # User documentation
│   └── drafts/              # Draft content (ascii, svg, teletext)
│
├── dev/                     # Development workspace (tracked)
│   ├── roadmap/             # ROADMAP.md (streamlined planning)
│   ├── sessions/            # Development session logs
│   ├── tools/               # Development utilities
│   └── scripts/             # Development scripts
│
└── wiki/                    # GitHub wiki documentation (tracked)
```

### Core Requirements (Minimal)

- Python 3.8+
- prompt_toolkit (interactive prompts)
- python-dotenv (environment config)
- psutil (system monitoring)
- requests (HTTP client)

### Extension Requirements (Optional)

- **Teletext Web GUI**: Flask, Flask-CORS, Flask-SocketIO
- **Dashboard**: No additional requirements (uses base server)
- **Future Extensions**: Per-extension dependencies

### Startup Flow (v1.2.12)

```
1. Load core modules (/core)
   ├─ Config & Environment (.env, user settings)
   ├─ Command Router (uDOS_commands.py)
   ├─ Services (knowledge manager, asset manager)
   └─ Runtime (uPY v1.2 interpreter)

2. Initialize user environment (/memory)
   ├─ Load user profile (memory/system/user/USER.UDT)
   ├─ Check folder structure (16 required folders)
   ├─ Restore workflow state (memory/workflows/state/)
   └─ Load active missions (memory/workflows/missions/)

3. Load knowledge bank (/knowledge)
   ├─ Public guides (water, fire, shelter, food, nav, medical)
   ├─ System themes (core/data/themes/)
   └─ Configurations (core/data/)

4. [Optional] Load extensions (if enabled)
   ├─ Assistant (Gemini API integration)
   ├─ Play (map engine, XP system)
   ├─ Web (teletext, dashboard)
   └─ Check user settings (api_server_enabled, etc.)

5. Start CLI prompt
   └─ Fully functional regardless of extensions
```

### Extension Loading Pattern

```python
# In core/uDOS_main.py
try:
    if user_settings.get('api_server_enabled', False):
        from extensions.core.teletext.api_server_manager import APIServerManager
        # Start if available
except ImportError:
    pass  # Extension not installed - CLI still works
```

**Philosophy**: CLI should be simple, fast, and fully functional. Extensions add power for those who want it, but never at the expense of core simplicity.

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

## Data Structure (v1.2.12)

uDOS v1.2.12 uses a structured data architecture with clear separation between core system files (tracked), knowledge content (tracked, read-only), and user workspace (gitignored except distributable code).

### Directory Organization

```
core/data/                # Core system data (tracked)
├── themes/               # Visual themes
│   ├── _index.json       # Theme registry
│   ├── dungeon.json      # Dungeon Crawler theme
│   ├── galaxy.json       # Galactic Voyager theme
│   ├── foundation.json   # Foundation theme (default)
│   ├── science.json      # Science theme
│   └── project.json      # Project theme
├── templates/            # Data templates
│   ├── user.template.json
│   ├── story.template.json
│   └── setup.uscript
└── [system configs]      # Core configuration files

knowledge/                # Public knowledge bank (tracked, read-only)
├── water/                # Water purification, storage (26 guides)
├── fire/                 # Fire starting, management (20 guides)
├── shelter/              # Shelter building, insulation (20 guides)
├── food/                 # Foraging, preservation (23 guides)
├── navigation/           # Land/sea navigation (20 guides)
├── medical/              # First aid, trauma care (27 guides)
├── checklists/           # Survival checklists (JSON)
├── communication/        # Signaling, radio (guides)
├── making/               # Crafting, tools (guides)
└── [other categories]    # Skills, tech, reference

memory/                   # User workspace (gitignored except ucode/)
├── ucode/                # Distributable code (tracked)
│   ├── tests/            # Test suites (tracked)
│   ├── stdlib/           # Standard library (tracked)
│   ├── examples/         # Example scripts (tracked)
│   ├── adventures/       # Adventure scripts (tracked)
│   ├── scripts/          # User scripts (ignored)
│   └── sandbox/          # Experimental (ignored)
├── system/user/          # User data (ignored)
│   ├── USER.UDT          # User profile database
│   ├── profiles.json     # Multi-user profiles
│   └── settings.json     # User preferences
├── workflows/            # Workflow automation (ignored)
│   ├── missions/         # Mission scripts (.upy)
│   ├── checkpoints/      # State snapshots
│   └── state/            # Current execution state
├── bank/                 # Financial data (ignored)
├── shared/               # Community content (ignored)
├── docs/                 # User documentation (ignored)
├── drafts/               # Draft content (ignored)
└── logs/                 # Session logs (ignored)
```

### System Files (`core/data/`)

**Purpose**: Core configuration that defines uDOS behavior (tracked in git)

- **`themes/*.json`** - Visual themes with color schemes, emoji sets, prompts
- **`templates/*.json`** - Data structure templates for user profiles, stories
- **System configs** - Core system configuration (commands, palettes, etc.)
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

### Template Files (`core/data/templates/`)

**Purpose**: Default structures for user data initialization

- **`user.template.json`** - Default user profile structure (copied to `sandbox/user.json` on first run)
- **`story.template.json`** - Default story structure for narrative mode
- **`setup.uscript`** - Interactive uCODE script for profile configuration

**First-Time Setup Flow**:
1. Health check detects missing `sandbox/user/USER.UDT`
2. Copy `user.template.json` → `sandbox/user/USER.UDT`
3. Optionally run `setup.uscript` for interactive configuration
4. Save personalized data to `sandbox/user/` directory

### Core System Data (`core/data/`)

**Purpose**: Essential configuration for minimal TUI operation

**Essential Files:**
- `commands.json` - Command registry and syntax
- `viewport.json` - TUI dimensions and grid settings
- `font-system.json` - Typography and color palette
- `locations.json` - Timezone→City + TILE code mappings
- `extensions.json` - Extension registry
- `faq.json` - FAQ content for HELP command
- `ucode_variables.json` - uCODE interpreter config
- `font-profile-template.json` - User font templates

**Directories:**
- `help_templates/` - Command help templates
- `themes/` - UI color schemes
- `templates/` - Setup and user templates (setup.uscript, user.template.json, usage_tracker.json)
- `graphics/` - ASCII art assets

**Design**: Minimal file set for core functionality. Educational/reference content moved to `/knowledge`.

### Knowledge Base (`knowledge/`)

**Purpose**: Curated reference library and educational content

**Contents:**
- `survival/`, `tech/`, `skills/` - Skill documentation
- `universe.json` - Solar system reference
- `credits.json` - Attribution data
- `geography/`, `reference/` - Geographic and reference data
- Community-contributed knowledge articles

**Usage**: Content for HELP system, educational lookups, reference materials

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

**Structure**:
```
memory/
├── user/                    # User data files
│   ├── USER.UDT             # User aliases
│   ├── planets.json         # Planet configurations
│   ├── knowledge.db         # Search index (SQLite)
│   └── xp.db                # XP/progression (SQLite)
├── planet/                  # Planet workspaces
│   ├── earth/               # Earth workspace
│   └── mars/                # Mars workspace
├── sandbox/                 # Drafts & development
├── workflow/                # uCODE scripts & missions
├── logs/                    # All system logs (flat)
├── sessions/                # Session history
├── private/                 # Tier 1: Encrypted (user-only)
├── shared/                  # Tier 2: Encrypted (team)
├── groups/                  # Tier 3: Community
└── public/                  # Tier 4: Public knowledge
```

**User Profile** (.env + sandbox/user/):
- Simple values in `.env` (current planet, theme, role)
- Complex data in `sandbox/user/planets.json`
- Current planet synced between both sources

**Planet Structure** (sandbox/user/planets.json):
```json
{
  "current_planet": "Earth",
  "user_planets": {
    "Earth": {
      "workspace_path": "memory/planet/earth",
      "location": { "city": "New York", "lat": 40.7128, "lon": -74.0060 }
    },
    "Mars": {
      "workspace_path": "memory/planet/mars",
      "location": { "settlement": "Olympus Base", "lat": 18.65, "lon": -133.8 }
    }
  },
  "reference_universe": "knowledge/universe.json"
}
```

### Migration from v0.x (.UDO Format)

**Old Structure** (deprecated):
```
data/
├── COMMANDS.UDO    → data/system/commands.json
├── THEMES.UDO      → data/themes/*.json (split into 5 files)
├── FAQ.UDO         → core/data/faq.json
├── PROMPTS.UDO     → (merged into faq.json)
├── USER.UDT        → core/data/templates/user.template.json
└── SETUP.USC       → core/data/templates/setup.uscript

sandbox/
└── USER.UDO        → sandbox/user.json
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

### 5. OK Assist Integration (`uDOS_commands.py`)

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
