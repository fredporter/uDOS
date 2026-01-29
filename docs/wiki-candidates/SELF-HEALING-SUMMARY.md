---
uid: udos-wiki-candidate-self-healing-summary-20260128160000-UTC-L300AB54
title: Self-Healing System Summary
tags: [wiki, candidate]
status: living
updated: 2026-01-30
spec: wiki_spec_obsidian.md
authoring-rules:
- Wiki candidate for future integration
- Pending review for promotion
- Obsidian-compatible
---

> **Moved:** See [wiki/SELF-HEALING-SUMMARY.md](../../wiki/SELF-HEALING-SUMMARY.md)

# Self-Healing System Summary

**Date:** 2026-01-26  
**Impact:** Ecosystem-wide  
**Status:** ✅ Complete

---

## Quick Reference

### Run Self-Healing Check

```bash
# Check all components
./bin/udos-self-heal.sh

# Check specific component
./bin/udos-self-heal.sh wizard
./bin/udos-self-heal.sh goblin
./bin/udos-self-heal.sh core

# Dry-run (no repairs)
./bin/udos-self-heal.sh --no-repair
```

### Python API

```python
from core.services.self_healer import run_self_heal

result = run_self_heal("wizard", auto_repair=True)
print("\n".join(result.messages))
```

---

## What Was Fixed

### 1. ✅ Goblin Deprecation Warning

**Before:**

```
DeprecationWarning: on_event is deprecated, use lifespan event handlers instead.
```

**After:**

```python
@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info("Starting...")
    yield
    logger.info("Shutting down...")

app = FastAPI(lifespan=lifespan)
```

### 2. ✅ Port Conflict Auto-Resolution

```bash
$ python -m core.services.self_healer goblin
✅ Repaired 1 issue(s)
  - Port 8767 is already in use
```

### 3. ✅ Launcher Integration

All launchers now include pre-flight self-healing checks:

- `Launch-Goblin-Dev.command`
- `Launch-Wizard-Server.command`
- `Launch-uDOS-TUI.command`

---

## Files Created

1. `/core/services/self_healer.py` (500+ lines)
   - Issue detection framework
   - Auto-repair logic
   - Python API

2. `/bin/udos-self-heal.sh` (130 lines)
   - CLI wrapper
   - Multi-component support
   - Pretty output

3. `/docs/SELF-HEALING-GUIDE.md`
   - Usage examples
   - API reference
   - Troubleshooting

4. `/docs/devlog/2026-01-26-self-healing-system.md`
   - Implementation details
   - Test results

---

## Files Modified

1. `/dev/goblin/goblin_server.py`
   - Migrated to lifespan pattern
   - Removed deprecated on_event

2. `/dev/bin/Launch-Goblin-Dev.command`
   - Added self-healing check

3. `/bin/Launch-Wizard-Server.command`
   - Added self-healing check

4. `/bin/Launch-uDOS-TUI.command`
   - Added self-healing check

---

## Issue Types

| Type                 | Auto-Fix  | Example               |
| -------------------- | --------- | --------------------- |
| `MISSING_DEPENDENCY` | ✅        | `pip install fastapi` |
| `PORT_CONFLICT`      | ✅        | Kill process on port  |
| `FILE_PERMISSION`    | ✅        | `chmod +x script.sh`  |
| `DEPRECATED_CODE`    | ⚠️ Manual | Flag for review       |
| `VERSION_MISMATCH`   | ✅        | Upgrade package       |
| `CONFIG_ERROR`       | ⚠️ Manual | Report issue          |

---

## Test Results

### Goblin Server

**Deprecation Warning:** ✅ Fixed  
**Port Conflict:** ✅ Auto-resolved  
**Startup:** ✅ Clean (no warnings)

### Wizard Server

**Dependencies:** ✅ Validated  
**Port Check:** ✅ Working  
**Self-heal Integration:** ✅ Active

### Core/TUI

**Environment:** ✅ Healthy  
**Scripts:** ✅ Executable  
**Self-heal Integration:** ✅ Active

---

## Usage Examples

### Before Launch

```bash
# Check system health
./bin/udos-self-heal.sh all

# If OK, launch server
./bin/Launch-Wizard-Server.command
```

### During Development

```bash
# Check specific component
python -m core.services.self_healer goblin

# Dry-run
python -m core.services.self_healer wizard --no-repair
```

### In Python Code

```python
from core.services.self_healer import SelfHealer

healer = SelfHealer("wizard", auto_repair=True)
result = healer.diagnose_and_repair()

if result.success:
    start_server()
else:
    log_issues(result.issues_remaining)
```

---

## Next Steps

### Roll Out to Remaining Launchers

- [ ] `/dev/bin/Launch-Empire-Server.command`
- [ ] `/app/bin/Launch uMarkdown-dev.command`
- [ ] Any custom launcher scripts

### Future Enhancements

- [ ] Database health checks
- [ ] Network diagnostics
- [ ] Disk space monitoring
- [ ] Memory leak detection

---

**Full Documentation:** [Self-Healing Guide](SELF-HEALING-GUIDE.md)

---

_Last Updated: 2026-01-26 20:45 PST_
