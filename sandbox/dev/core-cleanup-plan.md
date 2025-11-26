# Core Directory Cleanup Plan

## Current Problem
**20 files in `/core` root** - Too cluttered, unclear organization

## Proposed Structure (8 core files + packages)

### Keep in Root (8 files):
```
core/
├── __init__.py          ✅ Package API
├── config.py            ✅ NEW - Unified config (Phase 2)
├── main.py              🔄 Rename from uDOS_main.py
├── router.py            🔄 Rename from uDOS_commands.py
├── parser.py            🔄 Rename from uDOS_parser.py
├── grid.py              🔄 Rename from uDOS_grid.py
├── logger.py            🔄 Rename from uDOS_logger.py
└── startup.py           🔄 Rename from uDOS_startup.py
```

### Move to Packages (organized by function):

**1. Input Package** (`core/input/`):
- `uDOS_interactive.py` → `core/input/interactive.py`
- `uDOS_prompt.py` → `core/input/prompt.py` (or delete if unused)
- Services: `standardized_input.py`, `input_manager.py`

**2. Output Package** (`core/output/`):
- `uDOS_graphics.py` → `core/output/graphics.py`
- `uDOS_splash.py` → `core/output/splash.py`
- Services: `output_formatter.py`, `teletext_renderer.py`

**3. Interpreters Package** (`core/interpreters/`):
- `uDOS_ucode.py` → `core/interpreters/ucode.py` (64K - largest file!)
- `uDOS_offline.py` → `core/interpreters/offline.py`

**4. Network Package** (`core/network/`):
- `uDOS_server.py` → `core/network/server.py` (26K)
- `uDOS_gemini.py` → `core/network/gemini.py` (or delete, likely superseded)

**5. Utils Package** (already exists, consolidate):
- `uDOS_tree.py` → `core/utils/tree.py`
- `uDOS_files.py` → `core/utils/files.py`
- `uDOS_settings.py` → `core/utils/settings.py`

**6. Delete or Consolidate**:
- `uDOS_env.py` → ❌ DELETE (replaced by config.py)
- `uDOS_prompt.py` → ❌ DELETE (replaced by services/smart_prompt.py)
- `uDOS_gemini.py` → ❌ CHECK if used, likely superseded

## Impact
- **Before**: 20 files in /core root
- **After**: 8 files in /core root + organized packages
- **Reduction**: 60% fewer root files
- **Clarity**: Clear functional organization

## Quick Wins (No Breaking Changes)

### Phase 4A: Rename Files (preserves imports via __init__.py)
```bash
# Just rename, update imports in __init__.py
mv core/uDOS_main.py core/main.py
mv core/uDOS_commands.py core/router.py
mv core/uDOS_parser.py core/parser.py
mv core/uDOS_grid.py core/grid.py
mv core/uDOS_logger.py core/logger.py
mv core/uDOS_startup.py core/startup.py
```

### Phase 4B: Create Packages & Move
```bash
# Input package
mkdir -p core/input
mv core/uDOS_interactive.py core/input/interactive.py

# Output package
mkdir -p core/output
mv core/uDOS_graphics.py core/output/graphics.py
mv core/uDOS_splash.py core/output/splash.py

# Interpreters package
mkdir -p core/interpreters
mv core/uDOS_ucode.py core/interpreters/ucode.py
mv core/uDOS_offline.py core/interpreters/offline.py

# Network package
mkdir -p core/network
mv core/uDOS_server.py core/network/server.py
```

### Phase 4C: Delete Obsolete
```bash
rm core/uDOS_env.py          # Replaced by config.py
rm core/uDOS_prompt.py       # Replaced by services/smart_prompt.py
```

## Next Steps
1. Verify which files are actually imported/used
2. Start with simple renames (Phase 4A)
3. Create packages and move files (Phase 4B)
4. Update all imports
5. Delete obsolete files (Phase 4C)
6. Test everything still works

**Ready to proceed?**
