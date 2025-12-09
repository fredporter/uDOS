# GitHub Copilot Instructions for uDOS

**uDOS** is an offline-first knowledge system for survival and sustainable living. Built as a terminal-based OS with dual interfaces (CLI + Web), custom scripting language (uPY v1.2), and extensive knowledge bank (230+ guides).

**Key Architecture**: Command Router → Handlers → Services → Extensions. Everything is handler-based delegation with minimal main loop.

## Critical First Steps

1. **Always activate virtual environment**: `source .venv/bin/activate`
2. **Entry point**: `core/uDOS_main.py` → loads `core/uDOS_commands.py` (command router)
3. **Command routing**: `core/uDOS_commands.py` delegates to `core/commands/*_handler.py`
4. **Configuration**: `core/config.py` (unified .env + user.json + runtime state)
5. **Test validation**: Run `./start_udos.sh memory/ucode/tests/shakedown.upy` (142/148 tests, 95.9%)

## Workspace Organization (v1.2.21)

**CRITICAL**: Development files in `/dev/` (git submodule). User workspace (gitignored) in `/memory/`.
**v1.1.16**: Universal `.archive/` folders in any directory for version history, backups, and file recovery.
**v1.2.12**: Standardized memory/ucode/ structure (scripts/tests/sandbox/stdlib/examples/adventures).
**v1.2.21**: OK Assistant integration + Dev Mode submodule separation (FINAL v1.2.x STABLE).
**uPY v1.2**: Three-format scripting syntax aligned with uDOS v1.2.x releases.

### Development Directory (`/dev/` - git submodule)

**NEW in v1.2.21:** Development tools moved to separate repository (uDOS-dev)

```
dev/                        # Git submodule → https://github.com/fredporter/uDOS-dev
├── tools/                  # Development utilities (migrate_upy.py, etc.)
├── roadmap/                # ROADMAP.md - streamlined planning
└── scripts/                # Development scripts

# For end users: dev/ folder is empty (lightweight clone)
# For contributors: Clone with --recurse-submodules flag
```

**Clone Options:**
- **Users:** `git clone https://github.com/fredporter/uDOS.git` (1,331 files)
- **Contributors:** `git clone --recurse-submodules https://github.com/fredporter/uDOS.git` (1,367 files)

### Memory Directory (`/memory/` - gitignored, unified user workspace)

```
memory/
├── ucode/                  # Core distributable .upy scripts + tests
│   ├── scripts/            # User .upy scripts (ignored)
│   ├── tests/              # Test suites (tracked - v1.2.12)
│   ├── sandbox/            # Experimental scripts (ignored)
│   ├── stdlib/             # Standard library (tracked)
│   ├── examples/           # Example scripts (tracked)
│   └── adventures/         # Adventure scripts (tracked)
├── workflows/              # Unified workflow system (v2.0 - flat structure)
│   ├── .archive/           # Workflow version history & completed work
│   ├── config.json         # Workflow system configuration
│   ├── README.md           # Workflow v2.0 documentation
│   ├── missions/           # All mission workflow scripts (.upy)
│   │   └── .archive/       # Archived missions
│   ├── checkpoints/        # Auto-saved state snapshots
│   │   └── .archive/       # Old checkpoint history
│   ├── state/              # Current execution state and control
│   └── extensions/         # Gameplay/XP/achievement integration
├── bank/                   # Banking/barter/user system (unified)
│   ├── user/               # User settings and persistent data
│   │   └── .archive/       # User config history (BACKUP command)
│   ├── system/             # System files (themes, resource-state)
│   │   └── .archive/       # System file backups & old configs
│   ├── private/            # Private transactions
│   └── barter/             # Barter transactions
├── shared/                 # Shared/community content
│   ├── groups/             # Community groups
│   ├── metadata/           # Shared metadata
│   ├── public/             # Public content
│   └── .submissions/       # Content submissions
├── docs/                   # User documentation
├── drafts/                 # Draft content
│   ├── ascii/              # ASCII art drafts
│   ├── svg/                # SVG drafts
│   └── teletext/           # Teletext drafts
└── logs/                   # System logs
    └── auto/               # Auto-generated logs
```

### Universal .archive/ System (v1.1.16)

**Purpose:** Every directory can have a hidden `.archive/` folder for:
- File version history (old/working versions)
- Backup files (automated and manual)
- Deleted files (recovery before permanent deletion)
- Archived work (completed missions, workflows, checklists)

**Location Pattern:**
```
any-folder/
├── .archive/              # Hidden archive folder
│   ├── 20251203_143022_   # Timestamped backups
│   ├── old_versions/      # Version history
│   └── deleted/           # Soft-deleted files
├── active_file.txt        # Active files
└── working_data.json
```

**Commands Integration:**
- `CLEAN` - Scans and purges old `.archive/` files across workspace
- `BACKUP` - Creates timestamped copies in `.archive/`
- `REPAIR` - Can access `.archive/` for recovery
- `ARCHIVE` - Moves completed work to `.archive/`
- `UNDO/REDO` - Uses `.archive/` for version rollback
- `STATUS --health` - Reports `.archive/` usage across all folders

**Example Paths:**
```
memory/workflows/.archive/        # Workflow backups
memory/missions/.archive/         # Mission archives
memory/system/user/.archive/      # Config backups
wiki/.archive/                    # Old wiki versions
core/data/.archive/               # System file backups
memory/logs/.archive/             # Log rotation
.archive/                         # Root-level deprecated folders
```

**Auto-Management:**
- Old backups (>30 days): Flagged by CLEAN command
- Version history: Keep last 5 versions per file
- Deleted files: 7-day recovery window
- Archive size: Tracked in system health metrics

### File Placement Rules

**✅ Use `/dev/` for (tracked in git):**
- Development session logs → `dev/sessions/`
- Project roadmap → `dev/roadmap/ROADMAP.md`
- Development tools → `dev/tools/`
- Development scripts → `dev/scripts/`

**✅ Use `/memory/` for (gitignored, except ucode/):**
- Mission workflows → `memory/workflows/missions/` (all .upy scripts)
  - Archived missions → `memory/workflows/missions/.archive/`
- Workflow checkpoints → `memory/workflows/checkpoints/` (auto-saved state)
  - Old checkpoints → `memory/workflows/checkpoints/.archive/`
- Workflow state → `memory/workflows/state/` (current execution state)
- Workflow extensions → `memory/workflows/extensions/` (gameplay integration)
- User data → `memory/bank/user/`
  - Config backups → `memory/bank/user/.archive/`
- System files → `memory/bank/system/` (themes, resource-state.json)
  - System backups → `memory/bank/system/.archive/`
- Core tests/utilities → `memory/ucode/` (tracked in git)

**✅ Use `.archive/` folders for (auto-managed, ALL directories):**
- File version history (old/working versions)
- Backup snapshots (timestamped)
- Soft-deleted files (7-day recovery)
- Completed/archived work
- Log rotation (memory/logs/.archive/)
- Deprecated folders at root level (.archive/deprecated-root/)

**❌ Never commit to git:**
- Entire `memory/` directory (except `memory/ucode/`)
- `.env` file (contains secrets)
- User data, logs, active work

## Core Architecture

### Command Flow (Critical Understanding)

```
User Input → SmartPrompt → Parser → CommandHandler → Specialized Handler → Service/Extension
                 ↓
            TUIController (keypad, predictor, pager)
```

**Router Pattern** (`core/uDOS_commands.py`):
```python
# Thin routing layer - delegates everything
self.assistant_handler = AssistantCommandHandler(**handler_kwargs)
self.file_handler = FileCommandHandler(**handler_kwargs)
self.system_handler = SystemCommandHandler(**handler_kwargs)
# ... 40+ handlers

def execute(self, cmd_parts):
    cmd = cmd_parts[0].upper()
    if cmd in ['ASK', 'ANALYZE']: return self.assistant_handler.handle_command(cmd_parts)
    elif cmd in ['NEW', 'DELETE']: return self.file_handler.handle_command(cmd_parts)
    # Command routing lookup - see full map in uDOS_commands.py
```

**Handler Pattern** (`core/commands/*_handler.py`):
- All handlers inherit from `BaseCommandHandler`
- Each handles 3-10 related commands
- Examples: `assistant_handler.py` (ASK/ANALYZE), `file_handler.py` (NEW/DELETE/COPY/MOVE), `system_handler.py` (STATUS/REPAIR/REBOOT)

**Service Layer** (`core/services/`):
- `knowledge_manager.py` - 230+ survival guides (water, fire, shelter, medical, etc.)
- `asset_manager.py` - Fonts, patterns, themes
- `session_logger.py` - Command history and replay
- `connection_manager.py` - Network monitoring

### Directory Organization (v1.2.21)

```
core/                       # Core system (required, stable)
├── commands/               # Command handlers
├── data/                   # System configuration, themes, templates
├── docs/                   # Core system documentation
├── interpreters/           # uCODE, offline mode interpreters
├── services/               # Core services (config, knowledge, etc.)
├── ui/                     # UI components (file picker, etc.)
└── utils/                  # Utilities (path validation, etc.)

extensions/                 # Extension system
├── assistant/              # AI assistant (Gemini integration, OK system)
├── assets/                 # Shared assets (fonts, icons, data)
├── cloned/                 # Third-party cloned repos (gitignored, local-only)
│   ├── meshcore/           # MeshCore integration (v1.2.14+, optional)
│   └── README.md           # Installation guide for cloned extensions
├── core/                   # Core extensions (extension manager, server)
├── play/                   # Gameplay extensions (map engine, XP, MeshCore)
└── web/                    # Web interfaces (teletext, dashboard)

knowledge/                  # Public knowledge bank (read-only)
├── water/                  # Water guides (26 files)
├── fire/                   # Fire guides (20 files)
├── shelter/                # Shelter guides (20 files)
├── food/                   # Food guides (23 files)
├── navigation/             # Navigation guides (20 files)
└── medical/                # Medical guides (27 files)

memory/                     # User workspace (unified in v1.1.13)
├── ucode/                  # Core distributable .upy scripts + tests
├── missions/               # Mission management
├── workflows/              # Workflow automation
├── checklists/             # Checklist tracking
└── user/                   # User settings and data

wiki/                       # GitHub wiki (documentation)
```

### Key Design Principles

1. **Minimal Design**: No bloat, essential features only
2. **Offline-First**: Full functionality without internet/API keys
3. **Human-Centric**: Clear language, practical focus
4. **Text-First**: Terminal-based, ASCII graphics, teletext rendering
5. **Modular**: Clean separation (core → services → extensions)

## Coding Standards

### Python Style

```python
# ✅ Good: Clear, documented, type hints
def load_knowledge(category: str, complexity: str = "detailed") -> dict:
    """Load knowledge guide from knowledge bank.

    Args:
        category: Knowledge category (water, fire, shelter, etc.)
        complexity: simple | detailed | technical

    Returns:
        Dictionary with guide content and metadata
    """
    path = f"knowledge/{category}/guide.md"
    return load_file(path)

# ❌ Bad: No docs, no types, unclear
def lk(c, x="d"):
    return load_file(f"knowledge/{c}/guide.md")
```

### File Path Conventions

```python
# ✅ Good: Use absolute paths from project root
from core.config import Config
config = Config()
data = load_json("core/data/themes/galaxy.json")

# ❌ Bad: Relative paths (breaks from different contexts)
data = load_json("../data/themes/galaxy.json")
```

### Testing (v1.2.12)

```python
# Core tests go in memory/ucode/tests/
# File: memory/ucode/tests/test_feature_name.py

import pytest
from core.services.knowledge_manager import KnowledgeManager

def test_load_water_guide():
    """Test loading water purification guide."""
    km = KnowledgeManager()
    guide = km.load_guide("water/purification")
    assert guide is not None
## uPY Scripting Language (v1.2)

uDOS uses the **uPY scripting language** (.upy files) for automation, workflows, and mission scripts. As of v1.2.21, uPY uses **v1.2 syntax** with three-format system.

### uPY File Organization

```
memory/ucode/
├── scripts/            # User .upy scripts (ignored in git)
├── tests/              # Test suites for uPY features (tracked)
│   └── shakedown.upy   # Core functionality validation (142/148 tests, 95.9%)
├── sandbox/            # Experimental/working scripts (ignored)
├── stdlib/             # Standard library functions (tracked)
├── examples/           # Example scripts for learning (tracked)
└── adventures/         # Adventure/story scripts (tracked)
```

### uPY Runtime Architecture (v1.2)

**Critical Files**:
- `core/runtime/upy_runtime.py` - Main interpreter (1,179 lines)
- `core/interpreters/validator.py` - Syntax validation
- Test runner: `./start_udos.sh <script.upy>`

**Execution Flow**:
```python
# In uDOS_main.py:run_script()
from core.runtime.upy_runtime import UPYRuntime
runtime = UPYRuntime(command_handler=command_handler, grid=grid, parser=parser)
output = runtime.execute_file(script_file)  # Interprets .upy directly - no conversion
```

**Key Components**:
- **Variables**: `{$VARIABLE}` with dot notation `{$MISSION.STATUS}`
- **Commands**: `(COMMAND|param1|param2)` - delegates to CommandHandler
- **Conditionals**: Three formats (short/medium/long) parsed by regex patterns
- **Functions**: Stored in `self.functions` dict, executed inline
- **System vars**: Read-only (MISSION.*, WORKFLOW.*, SPRITE.*)

### uPY Syntax (v1.2)

**Three Bracket Types:**
- `{$variable}` - Variables (assignment, interpolation, system)
- `(command|params)` - Commands and functions
- `[condition]` - Short-form conditionals

**Three Complexity Levels:**
```upy
# SHORT FORM (1-2 actions)
[IF {$hp} < 30: HP (+20) | PRINT ('Healed!')]
@greet({$name}): PRINT ('Hello {$name}!')

# MEDIUM FORM (inline branching)
[IF {$gold} >= 100 THEN: ITEM (sword) ELSE: PRINT ('Need gold')]
[{$hp} < 30 ? HP (+20) : PRINT ('OK')]  # Ternary

# LONG FORM (complex logic, no indents required)
IF {$hp} < 30
  HP (+50)
  PRINT ('Emergency!')
  FLAG (critical)
ELSE IF {$hp} < 60
  HP (+20)
ELSE
  PRINT ('Healthy')
END IF
```

### uPY Version References

When documenting or referencing uPY features:
- Use **v1.2** for syntax version (aligned with uDOS v1.2.x)
- uPY versions match uDOS major.minor (v1.2.21 uses uPY v1.2)
- Runtime files: `core/runtime/upy_runtime.py` (interpreter)
- Validator: `core/interpreters/validator.py` (syntax checking)
- Test runner: Run with `./start_udos.sh <script.upy>`

### SHAKEDOWN Test (v1.2.12+)

**Core validation script:** `memory/ucode/tests/shakedown.upy`
- **Coverage:** 142/148 tests passing (95.9%)
- **Purpose:** Validates 16 required v1.2.x folders, core commands, system health
- **Usage:** `./start_udos.sh memory/ucode/tests/shakedown.upy`
- **Commands tested:** TREE, CONFIG CHECK/FIX, CLEAN, BACKUP, GUIDE, etc.
- Use **v1.2.x** for version references (aligned with uDOS)
- Runtime files: `core/runtime/upy_runtime.py` (internal implementation)
- Interpreter: `core/interpreters/validator.py` (syntax validation)

## System Variables (v2.0)

### Workflow Variables
```python
# Mission context
$MISSION.ID              # Current mission ID
$MISSION.NAME            # Mission name
$MISSION.STATUS          # DRAFT | ACTIVE | PAUSED | COMPLETED | FAILED
$MISSION.PROGRESS        # Progress (e.g., "45/55" or "82%")
$MISSION.START_TIME      # ISO timestamp
$MISSION.OBJECTIVE       # Mission goal

# Workflow execution context
$WORKFLOW.NAME           # Current workflow script name
$WORKFLOW.PHASE          # INIT | SETUP | EXECUTE | MONITOR | COMPLETE
$WORKFLOW.ITERATION      # Current loop iteration
$WORKFLOW.ERRORS         # Error count
$WORKFLOW.ELAPSED_TIME   # Seconds since start

# Checkpoint context
$CHECKPOINT.ID           # Unique checkpoint identifier
$CHECKPOINT.TIMESTAMP    # When checkpoint was saved
$CHECKPOINT.DATA         # Serialized state data
$CHECKPOINT.PREVIOUS     # Previous checkpoint (linked list)
$CHECKPOINT.NEXT         # Next checkpoint
```

## Common Patterns

### Configuration Access

```python
from core.config import Config

config = Config()
api_key = config.get_env('GEMINI_API_KEY')  # Environment variable
theme = config.get('theme', 'foundation')    # User setting
config.set('last_location', 'AU-BNE')        # Update setting
config.save()                                 # Persist to disk
```

### Knowledge Bank Access

```python
from core.services.knowledge_manager import KnowledgeManager

km = KnowledgeManager()

# Search knowledge
results = km.search("water purification", category="water")

# Load specific guide
guide = km.load_guide("water/boiling.md")

# List category
guides = km.list_category("medical")
```

### Asset Management

```python
from core.services.asset_manager import get_asset_manager

mgr = get_asset_manager()

# Load font
font = mgr.load_font('mallard', format='woff2')

# Load pattern
pattern = mgr.load_pattern('teletext-single')
data = pattern.load()  # Returns dict with pattern data
```

## Common Development Workflows

### Adding a New Command

1. **Create handler** in `core/commands/my_handler.py`:
   ```python
   from core.commands.base_handler import BaseCommandHandler
   
   class MyHandler(BaseCommandHandler):
       def handle_command(self, params):
           # params[0] is command name
           if params[0].upper() == 'MYCOMMAND':
               return self._do_something(params[1:])
   ```

2. **Register in router** (`core/uDOS_commands.py`):
   ```python
   from core.commands.my_handler import MyHandler
   self.my_handler = MyHandler(**handler_kwargs)
   
   # In execute():
   elif cmd in ['MYCOMMAND']: return self.my_handler.handle_command(cmd_parts)
   ```

3. **Add to commands.json** (`core/data/commands.json`):
   ```json
   "MYCOMMAND": {
     "syntax": "MYCOMMAND <arg>",
     "description": "Does something useful",
     "category": "utility"
   }
   ```

### Creating a uPY Script

```upy
# memory/ucode/scripts/example.upy
# SHORT FORM - Quick checks
[IF {$hp} < 30: HP (+20) | PRINT ('Healed!')]

# MEDIUM FORM - Inline branching
[IF {$gold} >= 100 THEN: ITEM (sword) ELSE: PRINT ('Need 100 gold')]

# LONG FORM - Complex logic
IF {$level} >= 10
  UNLOCK (advanced_feature)
  PRINT ('Feature unlocked!')
  XP (+500)
ELSE IF {$level} >= 5
  PRINT ('Level 10 required')
ELSE
  PRINT ('Keep playing!')
END IF

# FUNCTIONS - Reusable logic
FUNCTION check_status()
  GET (hp) → {$current_hp}
  [IF {$current_hp} < 50: PRINT ('Warning: Low health')]
  RETURN {$current_hp}
END FUNCTION

# Call function
@check_status()
```

### Testing Changes

```bash
# 1. Activate environment
source .venv/bin/activate

# 2. Run SHAKEDOWN test (validates core system)
./start_udos.sh memory/ucode/tests/shakedown.upy

# 3. Test specific command in interactive mode
./start_udos.sh
uDOS> MYCOMMAND test

# 4. Run pytest for unit tests
pytest memory/ucode/tests/ -v

# 5. Check errors
uDOS> STATUS --health
```

### Accessing Configuration

```python
from core.config import Config

config = Config()
api_key = config.get_env('GEMINI_API_KEY')  # .env variable
theme = config.get('theme', 'foundation')    # user.json setting
config.set('last_location', 'AA340')         # Update setting
config.save()                                # Persist to disk
```

## Version 1.2.21 (Current)

### Recent Major Features ✅

**v1.2.21 - OK Assistant** (FINAL STABLE v1.2.x release)
- O-key command panel with 8 AI prompts (MAKE WORKFLOW/SVG/DOC/TEST/MISSION)
- Context-aware assistance (workspace tracking, git status, error capture)
- Commands: `OK MAKE <type> "task"`, `OK ASK "question"`, `OK STATUS`

**v1.2.15 - TUI System**
- Keypad navigation (8↑ 2↓ 4← 6→, 5=select, 7/9=undo/redo)
- Command predictor with syntax highlighting
- Enhanced pager, file browser
- Enable: `TUI ENABLE KEYPAD`

**v1.2.14 - Grid-First** (4,807 lines)
- Multi-layer mapping (100-899 layers)
- MeshCore mesh networking integration

**v1.2.12 - Folder Structure**
- Standardized memory/ucode/ layout (scripts/tests/sandbox/stdlib/examples/adventures)
- SHAKEDOWN validation (142/148 tests, 95.9%)
- TREE, CONFIG CHECK/FIX commands

**v1.1.16 - Archive System**
- Universal .archive/ folders (versions, backups, deleted, completed)
- BACKUP/UNDO/REDO commands
- Soft-delete recovery (7-day window)
- CLEAN with archive scanning

### Grid System (TILE Codes)

- **Format**: Strict 2-letter columns (AA-RL for 0-479) + row number (0-269)
- **Layer suffix**: Optional -XXX suffix for layer (e.g., AA340-100 for world layer)
- **No coordinates**: Use TILE codes only
- **Layers**: 100 (world ~83km/cell), 200 (region ~2.78km), 300 (city ~93m), 400 (district ~3m), 500 (block ~10cm)

```python
# ✅ Good: Use TILE codes
grid_cell = "AA340"        # Sydney (grid position only)
tile_code = "AA340-100"    # Sydney at world layer
city_grid = "JF57"         # London (grid position)
full_tile = "JF57-100"     # London at world layer

# ❌ Bad: Don't use lat/long (removed in v1.1.12)
# coords = [-33.87, 151.21]  # DEPRECATED

# ❌ Bad: Don't use old hierarchical format
# location = "OC-AU-SYD"  # DEPRECATED (v1.x format)
```
# coords = [-33.87, 151.21]  # DEPRECATED
```

## Extension Development

When creating extensions:

1. Use extension template structure
2. Place in `extensions/cloned/my-extension/`
3. Follow `extension.json` schema
4. Use core services (Config, KnowledgeManager, AssetManager)
5. Document in extension README.md

## Documentation

### Where to Document

- **Core features** → `core/docs/`
- **Extensions** → `extensions/*/README.md`
- **User guides** → `wiki/` (GitHub wiki)
- **API docs** → `wiki/Developers-Guide.md`
- **Draft docs** → `dev/sessions/` (development notes)

### Wiki Structure

- `wiki/Home.md` - Main landing page
- `wiki/Getting-Started.md` - User onboarding
- `wiki/Developers-Guide.md` - Complete dev reference
- `wiki/Command-Reference.md` - All commands
- `wiki/Knowledge-System.md` - Knowledge bank docs

## Helpful Commands

**CRITICAL: Always activate virtual environment first!**

```bash
# Activate virtual environment (REQUIRED for all Python commands)
source .venv/bin/activate

# Run tests
pytest memory/ucode/ -v

# Run shakedown test
./start_udos.sh memory/tests/shakedown.uscript

# Generate SVG diagram (requires Gemini API key)
python memory/ucode/generate_svg_diagram.py "water filter" water

# Clean memory workspace
# In uDOS: CLEAN

# Tidy memory workspace
# In uDOS: TIDY --report
```

## VS Code Tasks

Available via `Ctrl+Shift+P` → "Run Task":

- **Run uDOS Interactive** - Launch main application
- **Run Shakedown Test** - Core functionality test
- **Run Pytest** - Full test suite
- **Logs: Tail Dev** - Monitor dev logs
- **CLEAN Memory** - Remove trash/temp files
- **TIDY Memory** - Organize workspace files

## Anti-Patterns to Avoid

❌ **Don't:**
- Create files outside `/dev/` or `/memory/` for development/testing
- Store sensitive data in git (use `.env`)
- Hardcode paths (use Config or constants)
- Mix user data with system files
- Create JSON files in `knowledge/` (use `core/data/` or `extensions/play/data/`)
- Use lat/long coordinates (TILE codes only since v1.1.12)
- Manually manage `.archive/` folders (use CLEAN, BACKUP, ARCHIVE commands)
- Store permanent data in `.archive/` (use for versioning/recovery only)

✅ **Do:**
- Use `/dev/` for tracked development files (roadmap, tools, sessions)
- Use `/memory/` for user workspace (missions, workflows, checklists)
- Use `.archive/` folders for version history and backups (auto-managed)
- Follow directory structure conventions
- Document all public APIs
- Write tests for new features
- Use BACKUP command before major config changes
- Use CLEAN command to manage .archive/ space
- Root-level deprecated folders stored in .archive/deprecated-root/

## Command Handler Architecture (As of Dec 2025)

## Command Handler Architecture (As of Dec 2025)

**Active Handlers** (49 total in `core/commands/`):
- **Knowledge**: `guide_handler.py` (interactive guides with progress tracking)
- **System**: `system_handler.py` (routing), `variable_handler.py`, `environment_handler.py`, `output_handler.py`
- **Files**: `file_handler.py` (NEW/DELETE/COPY/MOVE/etc., soft-delete v1.1.16)
- **Archive**: `archive_handler.py` (completed work), `backup_handler.py` (v1.1.16), `undo_handler.py` (v1.1.16)
- **Repair**: `repair_handler.py` (with RECOVER for soft-delete, v1.1.16)
- **Memory**: `memory_commands.py` (4-tier system), `private_commands.py`, `shared_commands.py`, `community_commands.py`
- **Graphics**: `diagram_handler.py`, `panel_handler.py`, `generate_handler.py`, `sprite_handler.py`
- **Assistant**: `assistant_handler.py` (Gemini integration)
- **Extensions**: `extension_handler.py`, `workflow_handler.py`
- See `core/uDOS_commands.py` for complete routing map

**Deprecated/Removed**:
- ❌ DOC, MANUAL, HANDBOOK, EXAMPLE handlers (removed v1.1.5.2)
- ❌ KB handler (redirects to GUIDE as of v2.0.0)
- ❌ .uscript format (use .upy only)

## TUI System (v1.2.15) ✅ **COMPLETE**

**Terminal Interface Components** - Fully integrated and functional numpad navigation system.

### Core Components (Fully Integrated)
- **Keypad Navigator** (`core/ui/keypad_navigator.py` - 379 lines) ✅ INTEGRATED
  - Numpad controls: 8↑ 2↓ 4← 6→ (movement), 5 (select), 7/9 (undo/redo), 1/3 (history), 0 (menu)
  - Config: `TUI ENABLE KEYPAD` command
  - Mode-aware design: command, menu, browser, pager
  - **Status:** Wired to main loop, fully functional
  
- **Command Predictor** (`core/ui/command_predictor.py`) ✅ INTEGRATED
  - Syntax-aware autocomplete from commands.json
  - Real-time token highlighting (green=valid, yellow=unknown, cyan=flags, magenta=paths)
  - Learning from command frequency
  - Fuzzy matching for typo tolerance
  - **Status:** Used in SmartPrompt autocomplete
  
- **Enhanced Pager** (`core/ui/pager.py`) ✅ INTEGRATED
  - Scroll-while-prompting: Navigate output without losing command input
  - Visual indicators: ▲ (more above), ▼ (more below)
  - Preserve scroll position across commands
  - **Status:** Active in output display
  
- **File Browser** (`core/ui/file_browser.py`) ✅ AVAILABLE
  - 5 workspaces: knowledge/, memory/docs/, memory/drafts/, memory/ucode/sandbox/, memory/ucode/scripts/
  - Filtered views (.upy, .md, .json only)
  - Breadcrumb navigation
  - Press 0 to switch workspaces
  - **Status:** Component ready, launcher planned for future

- **TUI Controller** (`core/ui/tui_controller.py` - 208 lines) ✅ INTEGRATED
  - Master integration layer for all TUI components
  - Key routing: keypad → pager → predictor
  - State persistence to memory/system/user/
  - **Status:** Initialized in uDOS_main.py, connected to SmartPrompt

### Integration Complete (v1.2.15)

**Main Loop:** `core/uDOS_main.py` uses TUI controller
- TUI controller initialized and connected to SmartPrompt
- Keypad input interception via key bindings
- Hints display when keypad enabled
- TUI instance passed to command handler
## Current Focus (v1.2.21 - FINAL STABLE v1.2.x)

**Latest Release (December 8, 2025):**
- ✅ **v1.2.21 COMPLETE** - OK Assistant Integration (760 lines, 11 files, FINAL v1.2.x)
  - OK Command Panel (310 lines) - O-key TUI integration, 8 quick prompts
  - Context-Aware Assistance (200 lines) - Workspace tracking, git status
  - OK Configuration (100 lines) - CONFIG panel [OK] tab
  - OK Workflows (150 lines) - MAKE commands (WORKFLOW/SVG/DOC/TEST/MISSION)
  - Gemini AI integration with graceful fallback
  - 6 bug fixes during testing

**OK Assistant Commands (v1.2.21):**
```upy
OK MAKE WORKFLOW "backup system files"    # Generate .upy workflow
OK MAKE SVG "water filter diagram"        # Generate SVG with AI
OK MAKE DOC core/commands/ok_handler.py   # Generate documentation
OK MAKE TEST "test_load_knowledge"        # Generate unit tests
OK MAKE MISSION "establish camp"          # Generate mission script
OK ASK "how do I optimize this?"          # Ask AI assistant
OK STATUS                                  # Show usage statistics
OK CLEAR                                   # Clear conversation history
```

**Access:** Press **O-key** to open interactive panel, or use commands directly.

**Previous Major Releases:**
- ✅ v1.2.15 - TUI Integration (keypad, predictor, pager, file browser)
- ✅ v1.2.14 - Grid-First Development (4,807+ lines, MeshCore integration)
- ✅ v1.2.13 - Mapping System (100-899 layer architecture)
- ✅ v1.2.12 - Folder Structure Refactoring (SHAKEDOWN validation)
- ✅ v1.1.16 - Archive System Infrastructure (.archive/ folders)

**v1.2.x Feature Summary:**
- Complete TUI system with numpad navigation
- OK Assistant with AI-powered content generation
- Multi-layer mapping system (100-899 layers)
- MeshCore mesh networking integration
- Universal .archive/ backup system
- SHAKEDOWN test suite (142/148 tests, 95.9%)
- uPY v1.2 three-format syntax

**Next Priorities (v1.3.0+):**
- Community features & content sharing
- Enhanced extension system
- Knowledge bank expansion
- Advanced mapping features

---

## Testing & Validation

### SHAKEDOWN Test Suite
**File:** `memory/ucode/tests/shakedown.upy`
**Run:** `./start_udos.sh memory/ucode/tests/shakedown.upy`
**Coverage:** 142/148 tests passing (95.9%)

**Tests Include:**
- 16 required folder structure validation
- Core commands (TREE, CONFIG, CLEAN, BACKUP)
- Archive system functionality
- Knowledge bank integrity
- TUI component status
- Extension availability

### Running Tests
```bash
# Activate virtual environment first
source .venv/bin/activate

# Run SHAKEDOWN test
./start_udos.sh memory/ucode/tests/shakedown.upy

# Run pytest suite
pytest memory/ucode/tests/ -v

# Quick smoke test
echo -e "STATUS\nTREE\nEXIT" | python uDOS.py
```

---

## Testing & Validation

### SHAKEDOWN Test Suite
**File:** `memory/ucode/tests/shakedown.upy`
**Run:** `./start_udos.sh memory/ucode/tests/shakedown.upy`
**Coverage:** 142/148 tests passing (95.9%)

**Tests Include:**
- 16 required folder structure validation
- Core commands (TREE, CONFIG, CLEAN, BACKUP)
- Archive system functionality
- Knowledge bank integrity
- TUI component status
- Extension availability

### Running Tests
```bash
# Activate virtual environment first
source .venv/bin/activate

# Run SHAKEDOWN test
./start_udos.sh memory/ucode/tests/shakedown.upy

# Run pytest suite
pytest memory/ucode/tests/ -v

# Quick smoke test
echo -e "STATUS\nTREE\nEXIT" | python uDOS.py
```

---

## Extensions Management (v1.2.21)

### Cloned Extensions (Optional Dependencies)

**Location:** `extensions/cloned/` (gitignored, local-only)

**MeshCore Integration (v1.2.14+):**
```bash
# Install MeshCore for mesh networking features
cd extensions/cloned/
git clone https://github.com/meshcore-dev/MeshCore.git meshcore
```

**Used For:**
- Grid rendering with device overlays
- Mesh network simulation (extensions/play/meshcore_integration.py)
- Signal propagation analysis (extensions/play/meshcore_signal_calculator.py)
- Device management (extensions/play/meshcore_device_manager.py)

**Other Optional Extensions:**
- coreui (icons), micro (editor), typo (typography)
- See `extensions/cloned/README.md` for installation

---

**Remember**: `/dev/` is for tracked development files (roadmap, tools, sessions). `/memory/` is for user workspace (missions, workflows, checklists, user data). `/memory/ucode/` has standardized structure (scripts/tests/sandbox/stdlib/examples/adventures). `.archive/` folders are auto-managed (BACKUP, UNDO, CLEAN commands). `extensions/cloned/` contains optional third-party repos (gitignored). Keep `core/` and `knowledge/` stable and production-ready.
