# Repository Cleanup - v1.4.0 Restructuring

## Overview

As part of v1.4.0 beta preparation, system files and scripts have been reorganized into `/core` subdirectories to maintain a clean, professional root directory structure.

## Changes Made

### Files Moved

| Original Location | New Location | Purpose |
|------------------|--------------|---------|
| `pytest.ini` | `core/tests/pytest.ini` | Test framework configuration |
| `test_cli.sh` | `core/scripts/test_cli.sh` | Quick CLI testing script |
| `web.sh` | `core/scripts/web.sh` | Web interface launcher |
| `structure.txt` | `dev/docs/structure.txt` | Repository structure documentation |

### Code Updates

Updated references to moved files:

1. **core/commands/system_handler.py**
   - Changed TREE command output from `structure.txt` to `dev/docs/structure.txt`

2. **core/utils/tree.py**
   - Updated default output path in `save_to_file()` and `generate_repository_tree()`

3. **core/uDOS_main.py**
   - Updated startup messages to reflect new structure.txt location

4. **knowledge/system/commands.json**
   - Updated TREE command description with new output path

5. **MANIFEST.in**
   - Removed pytest.ini from package distribution (developer-only file)

### New Directories Created

- **`core/scripts/`** - Utility scripts (testing, launching, convenience)
- **`core/setup/`** - Reserved for setup and installation utilities
- **`dev/docs/`** - Developer documentation and generated files

### Documentation Added

- `core/scripts/README.md` - Script directory overview and usage
- `core/setup/README.md` - Setup directory purpose and roadmap
- `dev/docs/` - Created for developer-generated documentation

## Root Directory Philosophy

### Keep in Root

Files that users and build tools expect to find in the repository root:

- **Documentation**: README.MD, ROADMAP.MD, CHANGELOG.md, CODE_OF_CONDUCT.md, CONTRIBUTING.md, etc.
- **Licenses**: LICENSE.txt, CREDITS.md
- **Entry Points**: uDOS.py, start_udos.sh
- **Build Config**: setup.py, requirements.txt, MANIFEST.in
- **IDE Config**: uDOS.code-workspace, .gitignore
- **Environment**: .env (ignored), .venv/ (ignored)

### Move to /core

System files and utilities used by developers:

- **Test Configuration**: pytest.ini → `core/tests/`
- **Utility Scripts**: test_cli.sh, web.sh → `core/scripts/`
- **Generated Docs**: structure.txt → `dev/docs/`
- **Setup Utilities**: Future additions → `core/setup/`

## Testing Impact

### pytest Configuration

- **Location**: `core/tests/pytest.ini`
- **Invocation**: pytest automatically finds config in subdirectories
- **Cache**: Still configured to use `memory/sandbox/.pytest_cache`
- **Test Paths**: Still points to `memory/tests` (unchanged)

**Testing Commands (still work):**
```bash
# From repository root
pytest

# Explicit config (if needed)
pytest -c core/tests/pytest.ini

# Via task runner
./start_udos.sh
```

### Script Execution

Updated paths for convenience scripts:

```bash
# Test CLI
./core/scripts/test_cli.sh

# Launch web interface
./core/scripts/web.sh

# Main entry point (unchanged)
./start_udos.sh
```

## Build Impact

### Package Distribution

- **setup.py**: Unchanged (standard location)
- **MANIFEST.in**: Updated to exclude pytest.ini (developer-only)
- **requirements.txt**: Unchanged

**Installation Commands (still work):**
```bash
pip install -e .
python setup.py develop
```

## Migration Guide

### For Developers

If you have existing scripts or workflows referencing old paths:

**Before:**
```bash
pytest -c pytest.ini
./test_cli.sh
./web.sh
cat structure.txt
```

**After:**
```bash
pytest -c core/tests/pytest.ini  # or just: pytest
./core/scripts/test_cli.sh
./core/scripts/web.sh
cat dev/docs/structure.txt
```

### For CI/CD Pipelines

Update any GitHub Actions or CI scripts that reference:
- `pytest.ini` → `core/tests/pytest.ini` (or remove -c flag)
- `test_cli.sh` → `core/scripts/test_cli.sh`
- `web.sh` → `core/scripts/web.sh`

## Future Improvements

Potential additions to maintain clean structure:

1. **core/scripts/**
   - Add install_dependencies.sh
   - Add validate_environment.sh
   - Add generate_assets.sh

2. **core/setup/**
   - Add automated setup wizard script
   - Add migration tools for version upgrades
   - Add extension installation helpers

3. **dev/docs/**
   - Move all auto-generated documentation here
   - Add architecture diagrams
   - Add API reference materials

## References

- **ROADMAP.MD**: Updated to reflect 90% completion of Phase 5.2
- **wiki/Architecture-Contributor-Guide.md**: Should be updated with new structure
- **wiki/Quick-Reference.md**: Update with new script paths
- **.github/**: No impact (templates reference general concepts)

## Checklist

- [x] Move pytest.ini to core/tests/
- [x] Move test_cli.sh to core/scripts/
- [x] Move web.sh to core/scripts/
- [x] Move structure.txt to dev/docs/
- [x] Update system_handler.py (TREE command)
- [x] Update tree.py (default paths)
- [x] Update uDOS_main.py (startup messages)
- [x] Update commands.json (TREE description)
- [x] Update MANIFEST.in (remove pytest.ini)
- [x] Create core/scripts/README.md
- [x] Create core/setup/README.md
- [x] Create dev/docs/ directory
- [x] Update ROADMAP.MD (Phase 5.2 complete)
- [x] Verify pytest still works
- [x] Document changes in this file

---

**Version**: v1.4.0 (Phase 5.2 - Repository Cleanup)
**Date**: 2025-01-24
**Author**: uDOS Development Team
