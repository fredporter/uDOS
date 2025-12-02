# System Handler Refactoring Plan
**Created:** December 2, 2025
**Current Size:** 1,534 lines (down from 3,664)
**Target:** Modular handlers (~800 lines router + specialized handlers)

## Current Method Inventory (25 methods)

### Already Delegated (Working) ✅
1. `handle_repair` → RepairHandler
2. `handle_shakedown` → ShakedownHandler
3. `handle_status` → DashboardHandler
4. `handle_dashboard` → DashboardHandler
5. `handle_viewport` → DashboardHandler
6. `handle_palette` → DashboardHandler
7. `handle_config` → ConfigurationHandler
8. `handle_config_planet` → cmd_config_planet
9. `handle_locate` → cmd_locate
10. `handle_assets` → AssetsHandler

### Core System Commands (Keep in SystemHandler) ✅
11. `handle_reboot` - Core system restart
12. `handle_destroy` - Destructive operation
13. `handle_wizard` - Setup wizard
14. `handle_help` - Help system

### Display Commands → DisplayHandler
15. `handle_blank` - Clear screen
16. `handle_splash` - Show splash screen
17. `handle_layout` - Layout management
18. `handle_progress` - Progress display
19. `handle_output` - Output management (626 lines!)

### Environment Commands → EnvironmentHandler
20. `handle_settings` - Settings management
21. `handle_clean` - Cleanup operations
22. `handle_dev_mode` - DEV MODE management

### Variable Commands → VariableHandler
23. `handle_get` - Get variable values
24. `handle_set` - Set variable values
25. `handle_history` - Command history

## Refactoring Strategy

### Phase 1: Extract Display Commands
**Target:** `core/commands/display_handler.py` (already exists!)
- Move: blank, splash, layout, progress, output
- Estimated: 800 lines
- Impact: High (output is 626 lines alone)

### Phase 2: Extract Environment Commands
**Target:** `core/commands/environment_handler.py` (new)
- Move: settings, clean, dev_mode
- Estimated: 300 lines
- Impact: Medium

### Phase 3: Extract Variable Commands
**Target:** `core/commands/variable_handler.py` (new)
- Move: get, set, history
- Estimated: 400 lines
- Impact: Medium

### Phase 4: Clean Router
**Target:** Keep in `system_handler.py`
- Core: reboot, destroy, wizard, help
- Delegation routing
- Estimated: 200 lines
- Impact: Low (mostly routing)

## Analysis: display_handler.py Already Exists!

✅ **FOUND:** `core/commands/display_handler.py` (907 lines)

**Already Extracted:**
- handle_blank ✅
- handle_help ✅
- handle_layout ✅
- handle_splash ✅
- handle_progress ✅

**Problem:** system_handler.py has DUPLICATE methods (lines 108-162)!
- These 5 methods exist in BOTH files
- system_handler.py should DELEGATE, not duplicate

**Solution:** Remove duplicates from system_handler.py, keep only delegation routing.

## Duplication Found

Lines 108-162 in system_handler.py are duplicates of DisplayHandler methods.
Must remove and replace with delegation calls.

## Method Size Analysis (ACTUAL)

Top bloat methods in system_handler.py:
1. handle_get (117 lines) - Variable getter
2. handle_set (96 lines) - Variable setter
3. handle_history (74 lines) - Command history
4. handle_destroy (61 lines) - Core (keep)
5. handle_clean (61 lines) - Cleanup

**Total removable:** 117 + 96 + 74 = 287 lines (variable commands)

## Refactoring Strategy (FINAL)

### Phase 1: Extract Variable Commands ✅ PRIORITY
**Target:** Create `core/commands/variable_handler.py`
- Move: handle_get (117 lines), handle_set (96 lines), handle_history (74 lines)
- Total: 287 lines
- Expected: system_handler.py 1,534 → 1,247 lines

### Phase 2: Extract Environment Commands
**Target:** Create `core/commands/environment_handler.py`
- Move: handle_clean (61 lines), handle_settings, handle_dev_mode
- Total: ~150 lines
- Expected: system_handler.py 1,247 → 1,097 lines

### Phase 3: Consolidate POKE/Output
**Target:** Move to `extensions/core/server_manager_handler.py`
- Move: handle_output and helper methods
- Total: ~200 lines
- Expected: system_handler.py 1,097 → 897 lines

## Implementation Plan

**Step 1:** Create variable_handler.py with GET, SET, HISTORY commands
**Step 2:** Update system_handler.py to delegate to VariableHandler
**Step 3:** Update uDOS_commands.py routing
**Step 4:** Test all variable commands work
**Step 5:** Commit "Core: Extract variable commands to VariableHandler"

**Next:** Repeat for environment commands, then POKE commands## Implementation Status

### ✅ Phase 1 Complete: Variable Commands Extracted (Dec 2, 2025)

**Created:** `core/commands/variable_handler.py` (294 lines)
**Modified:** `core/commands/system_handler.py` (1,276 lines, down from 1,342)

**Changes:**
- Moved handle_get (117 lines) → VariableHandler
- Moved handle_set (96 lines) → VariableHandler
- Moved handle_history (74 lines) → VariableHandler
- Total extracted: 287 lines
- Actual reduction: 1,342 → 1,276 = 66 lines (delegation wrappers remain)

**Delegation pattern:**
```python
@property
def variable_handler(self):
    if not hasattr(self, '_variable_handler') or self._variable_handler is None:
        from .variable_handler import VariableHandler
        self._variable_handler = VariableHandler(**self.__dict__)
    return self._variable_handler

def handle_get(self, params, grid, parser):
    """GET field value - delegates to VariableHandler."""
    return self.variable_handler.handle_get(params, grid, parser)
```

**Testing:** All 111 tests passing ✅

**Commit:** Ready to commit

### ⏳ Phase 2 Pending: Environment Commands
**Target:** Create `core/commands/environment_handler.py`
- Extract: handle_clean (61 lines), handle_settings, handle_dev_mode
- Estimated: ~150 lines
- Expected: system_handler.py 1,276 → ~1,126 lines

### ⏳ Phase 3 Pending: POKE/Output Commands
**Target:** Consolidate to extensions handler
- Extract: handle_output and helpers
- Estimated: ~200 lines
- Expected: system_handler.py 1,126 → ~926 lines

## Next Steps

1. ✅ Create variable_handler.py with GET, SET, HISTORY commands
2. ✅ Update system_handler.py to delegate to VariableHandler
3. ✅ Test all variable commands work (111/111 tests pass)
4. ⏳ Commit "Core: Extract variable commands to VariableHandler"
5. Create environment_handler.py
6. Extract environment commands
7. Test and commit
8. Extract POKE/output commands
9. Final testing
10. Update documentation
