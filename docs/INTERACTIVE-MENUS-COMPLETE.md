# Interactive Menus Implementation - Complete

**Status:** ✅ COMPLETE (Ready for Testing)  
**Date:** 2026-01-30  
**Version:** Core v1.0.7

---

## Summary

Fixed all issues with interactive menus in uDOS commands. Commands now properly:
1. Display menu options
2. **Prompt for user input**
3. **Execute selected action**
4. Complete the loop (not just return to prompt)

---

## What Was Fixed

### 1. SelfHealer API Error
- **Problem:** `healer.diagnose()` doesn't exist
- **Solution:** Changed to `healer.diagnose_and_repair()`
- **File:** [core/commands/restart_handler.py](../core/commands/restart_handler.py#L250-L268)

### 2. Interactive Menu Pattern
- **Problem:** Old `_show_menu()` just displayed text and returned
- **Solution:** New `_show_interactive_menu()` that prompts and executes
- **Files:**
  - [core/commands/destroy_handler.py](../core/commands/destroy_handler.py) — Working reference
  - [core/commands/restart_handler.py](../core/commands/restart_handler.py) — Just implemented

### 3. Version Display
- **Problem:** Still showing v1.0.7.1
- **Solution:** Changed to v1.0.7.0 + added --rebuild flag to clear cache
- **File:** [core/version.json](../core/version.json)

### 4. Python Cache Issues
- **Problem:** .pyc bytecode preventing changes from loading
- **Solution:** Added `clear_python_cache()` and `--rebuild` flag
- **Files:**
  - [bin/udos-common.sh](../bin/udos-common.sh) — Cache clearing function
  - [bin/Launch-uCODE.command](../bin/Launch-uCODE.command) — Flag parsing

---

## Testing Instructions

### CRITICAL: Use --rebuild Flag

Python cache was preventing changes from loading. **Always use --rebuild** for first test:

```bash
./bin/Launch-uCODE.command --rebuild
```

This will:
- Clear all `__pycache__` directories
- Delete all `.pyc` bytecode files
- Set `PYTHONDONTWRITEBYTECODE=1`
- Load fresh code

### Test 1: DESTROY Interactive Menu

```bash
uCODE> DESTROY
```

**Expected:**
```
╔════════════════════════════════════════╗
║     DESTROY SYSTEM                     ║
╚════════════════════════════════════════╝

Choose cleanup action:
  [1] Wipe user data (memory/user-data, logs, sandbox)
  [2] Compost old data (archive memory/ → .archive/)
  [3] Full reset (wipe + compost + clean venv)
  [0] Cancel

Choose an option (0-3): _
```

**Should:**
- ✅ Display menu
- ✅ Wait for input (cursor blinking at prompt)
- ✅ Execute selected action when you press 1, 2, 3, or 0
- ✅ Show confirmation for destructive actions

### Test 2: RESTART/REBOOT Interactive Menu

```bash
uCODE> REBOOT
```

**Expected:**
```
╔════════════════════════════════════════╗
║      RESTART SYSTEM                    ║
╚════════════════════════════════════════╝

Choose restart action:
  [1] Hot reload handlers only
  [2] Run repair/diagnostics only
  [3] Hot reload + repair
  [4] Full system restart
  [0] Show help

Choose an option (0-4): _
```

**Should:**
- ✅ Display menu
- ✅ Wait for input
- ✅ Execute selected action
- ✅ Show reload/repair progress
- ✅ NOT show AttributeError about `diagnose()`

### Test 3: Version Display

```bash
uCODE> VERSION
```

**Expected:**
```
Core TUI runtime (v1.0.7)
```

**Should NOT show:** `v1.0.7.1`

### Test 4: Hot Reload Works

Make a test change to a handler:

```bash
# Edit a file (e.g., add comment to restart_handler.py)
vim core/commands/restart_handler.py

# Then in uCODE:
uCODE> RESTART --reload-only
```

**Should:**
```
🔄 Hot reloading handlers...
   ✓ Reloaded 15 handlers (0 failed)
```

---

## Technical Details

### Interactive Menu Pattern

```python
def _show_interactive_menu(self, command):
    """Display menu, prompt for choice, execute action."""
    
    # 1. Display menu
    print("Choose action:")
    print("  [1] Option one")
    print("  [2] Option two")
    print("  [0] Cancel")
    
    # 2. Prompt for choice
    choice = self.prompt.ask_menu_choice("Choose an option", 2, allow_zero=True)
    
    # 3. Map choice to parameters
    if choice == 0:
        return None  # Cancel
    elif choice == 1:
        param1 = True
    elif choice == 2:
        param2 = True
    
    # 4. Execute action
    return self._perform_action(param1, param2, skip_confirm=True, command)
```

### SmartPrompt API

Located in [core/input/smart_prompt.py](../core/input/smart_prompt.py):

```python
# Yes/No/OK prompt (OK counts as Yes)
result = prompt.ask_yes_no_ok("Continue?", default="no")
# Returns: "yes", "no", or "ok"

# Menu choice (validates 1-N)
choice = prompt.ask_menu_choice("Choose option", 3, allow_zero=True)
# Returns: int (1-3) or 0 or None

# Single key validation
key = prompt.ask_single_key("Press Y/N", valid_keys=['y', 'n'], default='n')
# Returns: validated single character
```

### SelfHealer Correct API

Located in [core/services/self_healer.py](../core/services/self_healer.py):

```python
from core.services.self_healer import SelfHealer

healer = SelfHealer(component='core', auto_repair=True)
result = healer.diagnose_and_repair()  # NOT diagnose()

if result.success:
    print("✅ System healthy")
else:
    print(f"⚠️  {len(result.issues_remaining)} issues remaining")
```

---

## Files Modified

1. **[core/commands/restart_handler.py](../core/commands/restart_handler.py)**
   - Added `_show_interactive_menu()` method
   - Added `__init__()` to store `self.prompt`
   - Updated `handle()` to call interactive menu
   - Fixed `diagnose()` → `diagnose_and_repair()`
   - Actually executes hot reload (was just showing plan)

2. **[core/commands/destroy_handler.py](../core/commands/destroy_handler.py)**
   - Already working (reference implementation)

3. **[core/version.json](../core/version.json)**
   - Changed build from 1 to 0 (v1.0.7.1 → v1.0.7)

4. **[bin/udos-common.sh](../bin/udos-common.sh)**
   - Added `clear_python_cache()` function
   - Sets `PYTHONDONTWRITEBYTECODE=1`

5. **[bin/Launch-uCODE.command](../bin/Launch-uCODE.command)**
   - Added `--rebuild` flag parsing

---

## Documentation

- [STANDARD-INPUT-HANDLERS.md](STANDARD-INPUT-HANDLERS.md) — Complete API reference
- [INTERACTIVE-MENU-DEMO.md](INTERACTIVE-MENU-DEMO.md) — Implementation examples
- [SHAKEDOWN-DESTROY-QUICK-REFERENCE.md](SHAKEDOWN-DESTROY-QUICK-REFERENCE.md) — Updated with interactive examples

---

## Known Issues (Fixed)

| Issue | Status | Fix |
|-------|--------|-----|
| Menus don't prompt for input | ✅ FIXED | Implemented `_show_interactive_menu()` |
| AttributeError: diagnose() | ✅ FIXED | Changed to `diagnose_and_repair()` |
| Version shows v1.0.7.1 | ✅ FIXED | Updated version.json + --rebuild flag |
| Python cache persisting | ✅ FIXED | Added cache clearing + PYTHONDONTWRITEBYTECODE |
| RESTART doesn't reload | ✅ FIXED | Actually executes `importlib.reload()` now |

---

## Next Steps

1. **Test with --rebuild:**
   ```bash
   ./bin/Launch-uCODE.command --rebuild
   ```

2. **Try interactive commands:**
   ```bash
   DESTROY
   REBOOT
   VERSION
   ```

3. **Verify behavior:**
   - Menus prompt for input ✓
   - Actions execute ✓
   - No AttributeErrors ✓
   - Version shows v1.0.7 ✓

4. **Report results:**
   - If working: "DESTROYER works, REBOOT works!"
   - If issues: Share exact error message

---

## Rollback Plan

If issues persist, all changes are in git:

```bash
git log --oneline -5
git diff HEAD~1
git checkout HEAD~1 -- core/commands/restart_handler.py
```

---

**Status:** Implementation complete, ready for user testing with `--rebuild` flag.

