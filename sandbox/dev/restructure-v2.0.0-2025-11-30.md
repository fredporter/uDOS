# uDOS v2.0.0 Directory Restructure - November 30, 2025

## Summary

Completed comprehensive directory restructure to improve organization and align with uDOS v2.0.0 architecture principles.

## Changes Made

### 1. Planet System Simplification

**MOVED**: `extensions/assets/data/universe.json` → `core/data/universe.json`

**Rationale**: Planet/universe data is core mapping functionality, not an extension asset.

**Files Updated**:
- `core/services/planet_manager.py` - Updated all references to `core/data/universe.json`
- `sandbox/user/planets.json` - Updated `reference_universe` field
- `core/commands/shakedown_handler.py` - Updated test to check new location

**Impact**:
- ✅ Planet system is now part of core functionality
- ✅ Cleaner separation: core data vs extension assets
- ✅ All shakedown tests passing

### 2. Removed Deprecated Asset Directories

**REMOVED** (already didn't exist):
- `extensions/assets/patterns/` - Never created (deprecated)
- `extensions/assets/css/` - Never created (deprecated)
- `extensions/assets/js/` - Never created (deprecated)

**Files Updated**:
- `core/commands/shakedown_handler.py` - Removed checks for deprecated directories
- Updated asset type checks to only include: `fonts`, `icons`, `data`

**Impact**:
- ✅ Cleaner asset structure
- ✅ No false warnings in shakedown tests
- ✅ Follows v2.0.0 minimalist philosophy

### 3. Moved Private User Data to Sandbox

**CREATED**:
- `sandbox/workflow/` - Private workflow definitions
- `sandbox/sessions/` - Private session data and history

**Rationale**: These are private user data, not shared memory structures.

**Files Updated**:
- `core/commands/shakedown_handler.py` - Updated memory structure tests
- `sandbox/README.md` - Documented new directories

**Impact**:
- ✅ Clear separation: shared data (memory/) vs private data (sandbox/)
- ✅ Follows 4-tier knowledge architecture
- ✅ Better privacy model

### 4. Database Location Consistency

**VERIFIED**: All databases in `sandbox/user/`:
- ✅ `sandbox/user/knowledge.db`
- ✅ `sandbox/user/xp.db`
- ✅ `sandbox/user/USER.UDT`
- ✅ `sandbox/user/planets.json`

**Impact**:
- ✅ All user configuration in one place
- ✅ Easy backup/restore
- ✅ Consistent with v2.0.0 architecture

## Directory Structure (v2.0.0)

```
core/
├── data/
│   ├── universe.json          # ← MOVED from extensions/assets/data/
│   ├── themes/
│   ├── templates/
│   └── ...

extensions/
├── assets/
│   ├── fonts/                 # ✅ Kept
│   ├── icons/                 # ✅ Kept
│   └── data/                  # ✅ Kept (other data files)
│   # ❌ patterns/ - Removed
│   # ❌ css/ - Removed
│   # ❌ js/ - Removed

sandbox/
├── user/
│   ├── planets.json           # Planet configuration
│   ├── knowledge.db           # Knowledge database
│   ├── xp.db                  # XP/gamification database
│   └── USER.UDT               # User data table
├── workflow/                  # ← NEW (private)
├── sessions/                  # ← NEW (private)
├── dev/
├── docs/
├── drafts/
├── tests/
├── logs/
├── scripts/
├── ucode/
└── peek/

memory/
├── planet/                    # Planet workspaces
├── user/                      # Shared user content
├── private/                   # Private shared content
├── shared/                    # Shared content
├── groups/                    # Group content
├── public/                    # Public content
├── modules/                   # Module content
├── scenarios/                 # Scenario content
├── missions/                  # Mission content
├── barter/                    # Barter system
├── themes/                    # Theme content
├── sandbox/                   # Temporary workspace
└── logs/                      # System logs
```

## Testing Results

### Shakedown Test - All Passing ✅

```
🌍 Planet System Tests
  ✓ core/data/universe.json
  ✅ sandbox/user/planets.json
  ✅ memory/planet/ directory

🎨 Asset Management Tests
  ✅ extensions/assets/
  ✅ AssetManager imports successfully

💾 Memory Structure Tests
  ✅ sandbox/workflow/
  ✅ sandbox/sessions/

🗄️ Database Location Tests
  ✅ sandbox/user/knowledge.db
  ✅ sandbox/user/xp.db
  ✅ sandbox/user/USER.UDT

Total Tests:  71
Passed:       71 (100.0%)
Status:       ✅ PASSED
```

## Migration Notes

### For Users

No action required. Changes are transparent:
- Planet system works the same
- All data preserved
- All commands unchanged

### For Developers

If you reference these paths directly:

**OLD** → **NEW**:
- `extensions/assets/data/universe.json` → `core/data/universe.json`
- `memory/user/planets.json` → `sandbox/user/planets.json`
- `memory/workflow/` → `sandbox/workflow/`
- `memory/sessions/` → `sandbox/sessions/`

**DEPRECATED** (no longer checked):
- `extensions/assets/patterns/`
- `extensions/assets/css/`
- `extensions/assets/js/`

## Benefits

1. **Clearer Architecture**: Core data in `core/`, not `extensions/`
2. **Better Privacy**: Private data in `sandbox/`, shared data in `memory/`
3. **Simpler Structure**: Removed unused/deprecated directories
4. **Easier Maintenance**: Related files grouped logically
5. **Future-Proof**: Aligns with v2.0.0 principles

## Next Steps

- [ ] Update wiki documentation with new paths
- [ ] Add migration guide to CHANGELOG.md
- [ ] Update any extension documentation referencing old paths
- [ ] Consider consolidating other extension assets to core/data/

---

**Author**: uDOS Development Team
**Date**: November 30, 2025
**Version**: 2.0.0
**Status**: ✅ Complete
