# GitHub Copilot Instructions for uDOS

## Project Context

uDOS is an **offline-first operating system** for survival knowledge, mapping, and text-based computing. It prioritizes minimal design, offline functionality, and human-centric interfaces.

## Development Workspace: `/sandbox/`

**CRITICAL**: All development work, testing, and scratch files belong in `/sandbox/`. This is the primary development workspace.

### Sandbox Directory Structure

```
sandbox/
├── dev/                    # Development notes, planning, session logs
├── docs/                   # Draft documentation before wiki promotion
├── drafts/                 # Work-in-progress content
├── logs/                   # Runtime logs, dev logs, test output
├── scripts/                # Development scripts, utilities, generators
├── tests/                  # Pytest test suite (primary test location)
├── ucode/                  # Test scripts and example .uscript files
├── trash/                  # Temporary files (auto-cleaned)
├── user/                   # User data (planets.json, USER.UDT)
└── workflow/               # uCODE workflow automation scripts
```

### File Placement Rules

**✅ Use `/sandbox/` for:**
- Development notes and session logs → `sandbox/dev/`
- Test files → `sandbox/tests/`
- Scratch scripts → `sandbox/scripts/`
- Draft documentation → `sandbox/docs/`
- Experimental code → `sandbox/drafts/`
- Generated content (testing) → `sandbox/drafts/`
- Runtime logs → `sandbox/logs/`

**❌ Never commit to git:**
- `sandbox/logs/` (logs)
- `sandbox/trash/` (temp files)
- `sandbox/.pytest_cache/` (test cache)
- `sandbox/user/` (user data)
- `sandbox/.server_state.json` (runtime state)

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
# Place ALL tests in sandbox/tests/
# File: sandbox/tests/test_feature_name.py

import pytest
from core.services.knowledge_manager import KnowledgeManager

def test_load_water_guide():
    """Test loading water purification guide."""
    km = KnowledgeManager()
    guide = km.load_guide("water/purification")
    assert guide is not None
    assert "boiling" in guide['content'].lower()
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

## Version 2.0.0 Changes (Current)

### Data Consolidation

**COMPLETED** (Nov 2025):
- `knowledge/system/` → `core/data/` (60+ files)
- `knowledge/geography/` → `extensions/assets/data/` (8 files)
- `extensions/ai/` → `extensions/assistant/`
- Removed `dev/` directory (all dev work → `sandbox/dev/`)

### Grid System (TILE Codes)

- **Format**: Strict 2-letter columns (AA-RL for 0-479)
- **No coordinates**: Use TILE codes only (e.g., `OC-AU-SYD`)
- **Layers**: 100 (world), 200 (region), 300 (city), 400 (district), 500 (block)

```python
# ✅ Good: Use TILE codes
location = "OC-AU-SYD"  # Sydney, Australia
grid_cell = "AA340"     # Grid position

# ❌ Bad: Don't use lat/long (removed in v2.0.0)
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
- **Draft docs** → `sandbox/docs/` (before wiki promotion)

### Wiki Structure

- `wiki/Home.md` - Main landing page
- `wiki/Getting-Started.md` - User onboarding
- `wiki/Developers-Guide.md` - Complete dev reference
- `wiki/Command-Reference.md` - All commands
- `wiki/Knowledge-System.md` - Knowledge bank docs

## Helpful Commands

```bash
# Run tests
pytest sandbox/tests/ -v

# Run shakedown test
./start_udos.sh sandbox/ucode/shakedown.uscript

# Generate SVG diagram (requires Gemini API key)
python sandbox/scripts/generate_svg_diagram.py "water filter" water

# Clean sandbox
# In uDOS: CLEAN

# Tidy sandbox (organize files)
# In uDOS: TIDY --report
```

## VS Code Tasks

Available via `Ctrl+Shift+P` → "Run Task":

- **Run uDOS Interactive** - Launch main application
- **Run Shakedown Test** - Core functionality test
- **Run Pytest** - Full test suite
- **Logs: Tail Dev** - Monitor dev logs
- **CLEAN Sandbox** - Remove trash/temp files
- **TIDY Sandbox** - Organize sandbox files

## Anti-Patterns to Avoid

❌ **Don't:**
- Create files outside `/sandbox/` for development/testing
- Use `dev/` directory (removed in v2.0.0)
- Store sensitive data in git (use `.env`)
- Hardcode paths (use Config or constants)
- Mix user data with system files
- Create JSON files in `knowledge/` (use `core/data/` or `extensions/assets/data/`)
- Use lat/long coordinates (TILE codes only)

✅ **Do:**
- Use `/sandbox/` for all development work
- Follow directory structure conventions
- Document all public APIs
- Write tests for new features
- Use type hints in Python
- Keep knowledge bank read-only (guides are curated)

## Current Focus (v2.0.0)

**Stabilization & Documentation**:
- Core data minimization complete
- Grid system standardized (2-letter format)
- TILE code system (no coordinates)
- Wiki consolidation (comprehensive guides)
- Sandbox as primary dev workspace

**Next Steps**:
- Extension system improvements
- Web interface enhancements
- Knowledge bank expansion
- Mobile/PWA support (future)

---

**Remember**: `/sandbox/` is your development workspace. Use it freely for experiments, tests, and drafts. Keep `core/` and `knowledge/` stable and production-ready.
