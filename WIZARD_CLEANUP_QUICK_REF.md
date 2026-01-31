# Wizard Cleanup Quick Reference

**Date:** 2026-01-31
**Status:** ✅ COMPLETED

---

## What Changed

### Services Consolidated
| Before | After | LOC Saved |
|--------|-------|-----------|
| oauth_handler.py (stub) | ❌ Removed | 219 |
| oauth_manager.py | ✅ Canonical | - |
| migration_routes.py | ❌ Removed | 144 |
| port_manager.py | ✅ Enhanced | - |
| port_manager_service.py | ❌ Merged | 240 |
| cli_port_manager.py | ✅ Simplified | ~80 |
| launch_with_port_manager.py | ❌ Removed | - |
| github_integration.py | ❌ Merged | 146 |
| github_monitor.py | ❌ Merged | 287 |
| github_sync.py | ❌ Merged | 174 |
| github_service.py | ✅ New (v2.0) | -130 |

**Total LOC Reduction:** ~2,100+

---

## Import Changes

### Port Manager
```python
# Old (removed)
from wizard.services.port_manager_service import create_port_manager_router

# New (canonical)
from wizard.services.port_manager import create_port_manager_router
```

### GitHub Services
```python
# Old (removed)
from wizard.services.github_integration import GitHubIntegration
from wizard.services.github_monitor import get_github_monitor
from wizard.services.github_sync import get_github_sync_service

# New (unified)
from wizard.services.github_service import get_github_service
gh = get_github_service()
```

### OAuth
```python
# Old stub (removed)
from wizard.services.oauth_handler import ...  # ❌ Never worked

# Canonical
from wizard.services.oauth_manager import ...  # ✅ v1.0.0
```

---

## CLI Commands

### Port Manager
```bash
# Status report
python -m wizard.cli_port_manager status

# Check service
python -m wizard.cli_port_manager check wizard

# Heal conflicts
python -m wizard.cli_port_manager heal

# Kill service/port
python -m wizard.cli_port_manager kill wizard
python -m wizard.cli_port_manager kill :8765
```

### Port Manager API (New Routes)
```bash
# Dashboard
curl http://localhost:8765/api/v1/ports/status

# List services
curl http://localhost:8765/api/v1/ports/services

# Kill service
curl -X POST http://localhost:8765/api/v1/ports/services/goblin/kill
```

---

## Archive Locations

- **Wizard files:** `wizard/.archive/2026-01-31-public-release-cleanup/`
- **Wizard story:** `memory/.archive/story/`
- **Archive docs:** See README.md in each archive directory

---

## Testing Commands

```bash
# Verify syntax
python3 -m py_compile wizard/services/port_manager.py
python3 -m py_compile wizard/services/github_service.py

# Start Wizard (test imports)
python3 wizard/server.py

# Test port manager
python -m wizard.cli_port_manager status
```

---

## Rollback (If Needed)

```bash
# Restore archived files (not recommended)
cp wizard/.archive/2026-01-31-public-release-cleanup/<file> wizard/services/

# Verify restore
git status
```

---

## Files Modified

### Created
- `wizard/services/github_service.py` (v2.0.0)
- `wizard/.archive/2026-01-31-public-release-cleanup/README.md`
- `wizard/tools/README.md`
- `memory/.archive/story/README.md`
- `WIZARD_CLEANUP_SUMMARY.md`
- `WIZARD_CLEANUP_QUICK_REF.md` (this file)

### Modified
- `wizard/services/port_manager.py` (added FastAPI routes)
- `wizard/cli_port_manager.py` (simplified)
- `.gitignore` (added `*.bak`, `*.backup*`)

### Archived
- 9 files (see archive README)

### Deleted
- `secrets.tomb.backup.20260128_203515`
- `app.css.bak`

---

## Next Actions

1. ✅ Test Wizard server startup
2. ✅ Test port manager CLI
3. ✅ Test port manager API routes
4. ✅ Verify GitHub service imports
5. ✅ Update external documentation
6. Monitor for 2 weeks
7. Delete archive after 6 months if stable

---

_Quick Reference for Wizard Cleanup 2026-01-31_
