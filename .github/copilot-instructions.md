# GitHub Copilot Instructions for uDOS

## Project Context

uDOS is an **offline-first operating system** for survival knowledge, mapping, and text-based computing. It prioritizes minimal design, offline functionality, and human-centric interfaces.

## Workspace Organization (v1.1.13)

**CRITICAL**: Development files (tracked) in `/dev/`. User workspace (gitignored) in `/memory/`.

### Development Directory (`/dev/` - tracked in git)

```
dev/
├── tools/                  # Development utilities (migrate_upy.py, etc.)
├── roadmap/                # ROADMAP.md - streamlined planning
├── sessions/               # Development session logs
└── scripts/                # Development scripts
```

### Memory Directory (`/memory/` - gitignored, unified user workspace)

```
memory/
├── ucode/                  # Core distributable .upy scripts + tests (tracked)
│   ├── adventures/         # Adventure scripts
│   ├── examples/           # Example scripts
│   └── stdlib/             # Standard library
├── workflows/              # Unified workflow system (v2.0 - flat structure)
│   ├── config.json         # Workflow system configuration
│   ├── README.md           # Workflow v2.0 documentation
│   ├── missions/           # All mission workflow scripts (.upy)
│   ├── checkpoints/        # Auto-saved state snapshots
│   ├── state/              # Current execution state and control
│   ├── extensions/         # Gameplay/XP/achievement integration
│   └── .archive/           # Legacy structure (v1.x)
├── system/                 # System files
│   ├── archived/           # Archived system files
│   ├── backup/             # Configuration backups
│   ├── themes/             # Custom themes
│   └── user/               # User settings and persistent data
├── bank/                   # Banking/barter system
│   ├── private/            # Private transactions
│   └── barter/             # Barter transactions
├── shared/                 # Shared/community content
│   ├── groups/             # Community groups
│   ├── metadata/           # Shared metadata
│   ├── public/             # Public content
│   └── .submissions/       # Content submissions
├── docs/                   # User documentation
└── drafts/                 # Draft content
    ├── ascii/              # ASCII art drafts
    ├── svg/                # SVG drafts
    └── teletext/           # Teletext drafts
```

### File Placement Rules

**✅ Use `/dev/` for (tracked in git):**
- Development session logs → `dev/sessions/`
- Project roadmap → `dev/roadmap/ROADMAP.md`
- Development tools → `dev/tools/`
- Development scripts → `dev/scripts/`

**✅ Use `/memory/` for (gitignored, except ucode/):**
- Mission workflows → `memory/workflows/missions/` (all .upy scripts)
- Workflow checkpoints → `memory/workflows/checkpoints/` (auto-saved state)
- Workflow state → `memory/workflows/state/` (current execution state)
- Workflow extensions → `memory/workflows/extensions/` (gameplay integration)
- User data → `memory/system/user/`
- System backups → `memory/system/backup/`
- System archives → `memory/system/archived/`
- Core tests/utilities → `memory/ucode/` (tracked in git)

**❌ Never commit to git:**
- Entire `memory/` directory (except `memory/ucode/`)
- `.env` file (contains secrets)
- User data, logs, active work

## Core Architecture

### Directory Organization

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
├── assistant/              # AI assistant (Gemini integration)
├── assets/                 # Shared assets (fonts, icons, data)
├── core/                   # Core extensions (extension manager, server)
├── play/                   # Gameplay extensions (map engine, XP)
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

### Testing

```python
# Core tests go in memory/ucode/
# File: memory/ucode/test_feature_name.py

import pytest
from core.services.knowledge_manager import KnowledgeManager

def test_load_water_guide():
    """Test loading water purification guide."""
    km = KnowledgeManager()
    guide = km.load_guide("water/purification")
    assert guide is not None
    assert "boiling" in guide['content'].lower()
```

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

## Version 1.1.12 Changes (Current)

### Recent Completions (December 2025)

**v1.1.5.1 - System Handler Refactoring** ✅
- Refactored `system_handler.py`: 1,342 → 674 lines (50% reduction)
- Created 3 specialized handlers:
  - `variable_handler.py` (294 lines) - GET/SET/HISTORY commands
  - `environment_handler.py` (233 lines) - SETTINGS/CLEAN/DEV MODE
  - `output_handler.py` (417 lines) - POKE/servers/extensions
- All 111 tests passing

**v1.1.5.2 - Dead Code Removal** ✅
- Removed 5 unused documentation handlers (1,604 lines):
  - `doc_handler.py`, `docs_unified_handler.py`, `manual_handler.py`
  - `handbook_handler.py`, `example_handler.py`
- None were routed in `uDOS_commands.py` (completely inactive)
- GUIDE handler provides all knowledge access (active, working)

**Data Consolidation** ✅
- `knowledge/system/` → `core/data/` (60+ files)
- `knowledge/geography/` → `extensions/assets/data/` (8 files)
- `extensions/ai/` → `extensions/assistant/`
- `sandbox/dev/` → `/dev/` (development workspace reorganization)

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

```bash
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
- Create JSON files in `knowledge/` (use `core/data/` or `extensions/assets/data/`)
- Use lat/long coordinates (TILE codes only since v1.1.12)

✅ **Do:**
- Use `/dev/` for tracked development files (roadmap, tools, sessions)
- Use `/memory/` for user workspace (missions, workflows, checklists)
- Follow directory structure conventions
- Document all public APIs
- Write tests for new features
- Use type hints in Python
- Keep knowledge bank read-only (guides are curated)

## Command Handler Architecture (As of Dec 2025)

**Active Handlers** (46 total in `core/commands/`):
- **Knowledge**: `guide_handler.py` (interactive guides with progress tracking)
- **System**: `system_handler.py` (routing), `variable_handler.py`, `environment_handler.py`, `output_handler.py`
- **Files**: `file_handler.py` (NEW/DELETE/COPY/MOVE/etc.)
- **Memory**: `memory_commands.py` (4-tier system), `private_commands.py`, `shared_commands.py`, `community_commands.py`
- **Graphics**: `diagram_handler.py`, `panel_handler.py`, `generate_handler.py`, `sprite_handler.py`
- **Assistant**: `assistant_handler.py` (Gemini integration)
- **Extensions**: `extension_handler.py`, `workflow_handler.py`
- See `core/uDOS_commands.py` for complete routing map

**Deprecated/Removed**:
- ❌ DOC, MANUAL, HANDBOOK, EXAMPLE handlers (removed v1.1.5.2)
- ❌ KB handler (redirects to GUIDE as of v2.0.0)
- ❌ .uscript format (use .upy only)

## Current Focus (v1.1.12)

**Recent Achievements**:
- ✅ System handler refactoring (50% reduction)
- ✅ Dead code removal (1,604 lines cleaned)
- ✅ Core data minimization complete
- ✅ Grid system standardized (2-letter TILE codes)
- ✅ Unified /memory workspace (v1.1.13)

**Next Priorities**:
- v1.1.5.3: Deprecated code removal & utilities refactoring
- v1.1.6: Nano Banana workflow integration
- Extension system improvements
- Knowledge bank expansion

---

**Remember**: `/dev/` is for tracked development files (roadmap, tools, sessions). `/memory/` is for user workspace (missions, workflows, checklists, user data). Keep `core/` and `knowledge/` stable and production-ready.
