# System Handler Analysis & Refactoring Map
**File**: `core/commands/system_handler.py`
**Total Lines**: 3,664
**Handle Methods**: 41
**Helper Methods**: 54
**Analysis Date**: 2025-11-30

---

## EXECUTIVE SUMMARY

This monolithic handler contains **95 total methods** across 7 distinct functional areas. The file has grown organically from v1.0.0 through v1.5.3, accumulating features without proper modularization.

**Key Issues**:
- Mixed concerns (config, debug, session, layout, theme, etc.)
- Duplicate delegation patterns (some commands delegate, others don't)
- Inconsistent helper method organization
- Poor separation of UI vs business logic

**Recommendation**: Split into **4 focused handlers** + 1 base utility module.

---

## PART 1: METHOD INVENTORY

### Handle Methods (41 total)

| Method | Lines | Category | Complexity |
|--------|-------|----------|------------|
| `handle_blank` | 195-260 | Display | Medium |
| `handle_help` | 262-340 | Help | High |
| `handle_history` | 342-470 | Session | High |
| `handle_theme` | 472-680 | Configuration | High |
| `handle_progress` | 682-950 | Output | High |
| `handle_session` | 952-1150 | Session | High |
| `handle_layout` | 1152-1380 | Display | High |
| `handle_repair` | 1382-1400 | Delegated | Low |
| `handle_shakedown` | 1402-1420 | Delegated | Low |
| `handle_status` | 1422-1440 | Delegated | Low |
| `handle_dashboard` | 1442-1460 | Delegated | Low |
| `handle_viewport` | 1462-1480 | Delegated | Low |
| `handle_palette` | 1482-1500 | Delegated | Low |
| `handle_settings` | 1502-1525 | Delegated | Low |
| `handle_config` | 1527-1580 | Configuration | Medium |
| `handle_reboot` | 1582-1620 | System | Low |
| `handle_destroy` | 1622-1690 | System | Medium |
| `handle_splash` | 1692-1740 | Display | Low |
| `handle_clean` | 1742-1800 | System | Medium |
| `handle_wizard` | 1802-1860 | Configuration | Medium |
| `handle_workspace` | 1862-1865 | Stub | Low |
| `handle_output` | 1867-2050 | System | High |
| `handle_undo` | 2052-2075 | History | Low |
| `handle_redo` | 2077-2100 | History | Low |
| `handle_restore` | 2102-2180 | History | Medium |
| `handle_debug` | 2182-2290 | Debug | High |
| `handle_breakpoint` | 2292-2420 | Debug | High |
| `handle_step` | 2422-2465 | Debug | Medium |
| `handle_continue` | 2467-2490 | Debug | Low |
| `handle_inspect` | 2492-2560 | Debug | Medium |
| `handle_watch` | 2562-2650 | Debug | Medium |
| `handle_stack` | 2652-2690 | Debug | Low |
| `handle_modify` | 2692-2750 | Debug | Medium |
| `handle_profile` | 2752-2880 | Debug | High |
| `handle_history` (debugger) | 2882-2960 | Debug | Medium |
| `handle_get` | 2962-3080 | Data | High |
| `handle_set` | 3082-3200 | Data | High |
| `handle_config_planet` | 3202-3230 | Planet | Low |
| `handle_locate` | 3232-3260 | Planet | Low |
| `handle_dev_mode` | 3262-3450 | System | High |
| `handle_assets` | 3452-3485 | System | Low |

### Helper Methods (54 total)

| Category | Methods | Line Range | Count |
|----------|---------|------------|-------|
| History Helpers | `_show_recent_history`, `_search_history`, `_show_history_stats`, `_clear_history`, `_export_history` | 342-470 | 5 |
| Theme Helpers | `_show_theme_info`, `_list_themes`, `_set_theme`, `_toggle_accessibility`, `_toggle_contrast`, `_set_colorblind_support`, `_create_custom_theme` | 472-680 | 7 |
| Progress Helpers | `_show_active_progress`, `_test_basic_progress`, `_test_multi_stage_progress`, `_test_search_progress`, `_list_active_progress`, `_cancel_progress`, `_run_progress_demo` | 682-950 | 7 |
| Session Helpers | `_show_current_session`, `_list_sessions`, `_save_session`, `_load_session`, `_delete_session`, `_toggle_auto_save`, `_create_checkpoint`, `_export_session`, `_import_session` | 952-1150 | 9 |
| Layout Helpers | `_show_layout_info`, `_set_layout_mode`, `_force_resize_detection`, `_toggle_auto_resize`, `_update_layout_config`, `_test_adaptive_formatting`, `_layout_demo`, `_demo_split_layout` | 1152-1380 | 8 |
| Config Helpers | `_handle_config_role` | 1527-1580 | 1 |
| Output Helpers | `_handle_output_list`, `_handle_output_status`, `_handle_output_start`, `_handle_output_stop`, `_handle_output_health`, `_handle_output_restart`, `_handle_extension_discover`, `_handle_extension_info`, `_handle_extension_info_basic`, `_handle_extension_install`, `_handle_extension_uninstall`, `_handle_extension_marketplace` | 1867-2050 | 12 |
| DEV MODE Helpers | `_dev_mode_enable`, `_dev_mode_disable`, `_dev_mode_status`, `_dev_mode_help` | 3262-3450 | 4 |

---

## PART 2: FUNCTIONAL CATEGORIES

### Category 1: CONFIGURATION & SETTINGS
**Commands**: THEME, CONFIG, WIZARD, SETTINGS
**Lines**: 472-1580 (~1,108 lines)
**Complexity**: High

**Methods**:
- `handle_theme` (472-680) - 208 lines
- `handle_config` (1527-1580) - 53 lines
- `handle_wizard` (1802-1860) - 58 lines
- `handle_settings` (1502-1525) - 23 lines (delegated)
- Theme helpers: 7 methods (200+ lines)
- Config helpers: 1 method

**Dependencies**:
- `core.theme_manager.ThemeManager`
- `core.services.setup_wizard.SetupWizard`
- `core.commands.configuration_handler.ConfigurationHandler` (delegation target)
- `core.config_manager.ConfigManager`

**Notes**: Already partially delegated (CONFIG, SETTINGS) but THEME and WIZARD remain inline.

---

### Category 2: SESSION & HISTORY MANAGEMENT
**Commands**: SESSION, HISTORY, UNDO, REDO, RESTORE
**Lines**: 342-1150 (~808 lines)
**Complexity**: High

**Methods**:
- `handle_history` (342-470) - 128 lines
- `handle_session` (952-1150) - 198 lines
- `handle_undo` (2052-2075) - 23 lines
- `handle_redo` (2077-2100) - 23 lines
- `handle_restore` (2102-2180) - 78 lines
- History helpers: 5 methods (128 lines)
- Session helpers: 9 methods (198 lines)

**Dependencies**:
- `core.services.session_manager.SessionManager`
- `core.utils.usage_tracker.UsageTracker`
- Command history from base class
- History system from base class

**Notes**: Core functionality for workspace persistence, command tracking, and state restoration.

---

### Category 3: LAYOUT & DISPLAY
**Commands**: LAYOUT, VIEWPORT, PALETTE, BLANK, SPLASH, DASHBOARD
**Lines**: 195-1380 + delegated (~600 inline + 200 delegated)
**Complexity**: High

**Methods**:
- `handle_blank` (195-260) - 65 lines
- `handle_layout` (1152-1380) - 228 lines
- `handle_splash` (1692-1740) - 48 lines
- `handle_viewport` (1462-1480) - delegated
- `handle_palette` (1482-1500) - delegated
- `handle_dashboard` (1442-1460) - delegated
- Layout helpers: 8 methods (228 lines)

**Dependencies**:
- `core.output.layout_manager.LayoutManager`
- `core.output.screen_manager.ScreenManager`
- `core.output.splash` module
- `core.commands.dashboard_handler.DashboardHandler` (delegation target)

**Notes**: Mix of inline (LAYOUT, BLANK) and delegated (VIEWPORT, PALETTE, DASHBOARD) commands.

---

### Category 4: DEBUG & DEVELOPMENT
**Commands**: DEBUG, BREAK, STEP, CONTINUE, INSPECT, WATCH, STACK, MODIFY, PROFILE
**Lines**: 2182-2960 (~778 lines)
**Complexity**: Very High

**Methods**:
- `handle_debug` (2182-2290) - 108 lines
- `handle_breakpoint` (2292-2420) - 128 lines
- `handle_step` (2422-2465) - 43 lines
- `handle_continue` (2467-2490) - 23 lines
- `handle_inspect` (2492-2560) - 68 lines
- `handle_watch` (2562-2650) - 88 lines
- `handle_stack` (2652-2690) - 38 lines
- `handle_modify` (2692-2750) - 58 lines
- `handle_profile` (2752-2880) - 128 lines
- `handle_history` (debugger) (2882-2960) - 78 lines

**Dependencies**:
- `core.interpreters.ucode_debugger.UCodeDebugger` (accessed via parser.ucode.debugger)
- Parser instance for uCODE access
- No delegated handlers yet

**Notes**: Complete debugger implementation for v1.0.17. Self-contained but tightly coupled to uCODE interpreter.

---

### Category 5: SYSTEM OPERATIONS
**Commands**: REBOOT, DESTROY, CLEAN, OUTPUT, DEV, ASSETS
**Lines**: 1582-2050 + 3262-3485 (~500 lines)
**Complexity**: Medium-High

**Methods**:
- `handle_reboot` (1582-1620) - 38 lines
- `handle_destroy` (1622-1690) - 68 lines
- `handle_clean` (1742-1800) - 58 lines
- `handle_output` (1867-2050) - 183 lines
- `handle_dev_mode` (3262-3450) - 188 lines
- `handle_assets` (3452-3485) - 33 lines (delegated)
- Output helpers: 12 methods (183 lines)
- DEV MODE helpers: 4 methods (188 lines)

**Dependencies**:
- `extensions.server_manager.ServerManager`
- `extensions.core.extension_manager.ExtensionManager`
- `core.services.dev_mode_manager.DevModeManager`
- `core.commands.sandbox_handler.SandboxHandler` (for DESTROY)
- `core.commands.assets_handler` (delegation target for ASSETS)

**Notes**: Mix of critical system commands and extension management.

---

### Category 6: PROGRESS & OUTPUT MANAGEMENT
**Commands**: PROGRESS, HELP
**Lines**: 262-950 (~688 lines)
**Complexity**: High

**Methods**:
- `handle_help` (262-340) - 78 lines
- `handle_progress` (682-950) - 268 lines
- Progress helpers: 7 methods (268 lines)

**Dependencies**:
- `core.services.help_manager.HelpManager`
- `core.utils.progress_manager.ProgressManager`
- `core.utils.usage_tracker.UsageTracker`

**Notes**: HELP is used frequently; PROGRESS is for testing/demos.

---

### Category 7: DATA MANAGEMENT
**Commands**: GET, SET, CONFIG_PLANET, LOCATE
**Lines**: 2962-3260 (~298 lines)
**Complexity**: Medium

**Methods**:
- `handle_get` (2962-3080) - 118 lines
- `handle_set` (3082-3200) - 118 lines
- `handle_config_planet` (3202-3230) - 28 lines (delegated)
- `handle_locate` (3232-3260) - 28 lines (delegated)

**Dependencies**:
- Story manager (from base class)
- `core.commands.cmd_config_planet` (delegation target)
- `core.commands.cmd_locate` (delegation target)

**Notes**: GET/SET are smart accessors for story/config/system fields. Planet commands already delegated.

---

## PART 3: DELEGATION ANALYSIS

### Already Delegated (11 commands)
✅ **REPAIR** → `repair_handler.RepairHandler` (line 1382)
✅ **SHAKEDOWN** → `shakedown_handler.ShakedownHandler` (line 1402)
✅ **STATUS** → `dashboard_handler.DashboardHandler` (line 1422)
✅ **DASHBOARD** → `dashboard_handler.DashboardHandler` (line 1442)
✅ **VIEWPORT** → `dashboard_handler.DashboardHandler` (line 1462)
✅ **PALETTE** → `dashboard_handler.DashboardHandler` (line 1482)
✅ **SETTINGS** → `configuration_handler.ConfigurationHandler` (line 1502)
✅ **CONFIG** → `configuration_handler.ConfigurationHandler` (line 1527)
✅ **CONFIG_PLANET** → `cmd_config_planet` (line 3202)
✅ **LOCATE** → `cmd_locate` (line 3232)
✅ **ASSETS** → `assets_handler` (line 3452)

### Should Be Delegated (30 commands)
🔄 **THEME** (208 lines + 7 helpers) → ConfigurationHandler
🔄 **WIZARD** (58 lines) → ConfigurationHandler
🔄 **SESSION** (198 lines + 9 helpers) → SessionHandler
🔄 **HISTORY** (128 lines + 5 helpers) → SessionHandler
🔄 **UNDO/REDO/RESTORE** (124 lines) → SessionHandler
🔄 **LAYOUT** (228 lines + 8 helpers) → DisplayHandler
🔄 **BLANK** (65 lines) → DisplayHandler
🔄 **SPLASH** (48 lines) → DisplayHandler
🔄 **HELP** (78 lines) → DisplayHandler or HelpHandler
🔄 **PROGRESS** (268 lines + 7 helpers) → DisplayHandler
🔄 **DEBUG** (108 lines) → DebugHandler
🔄 **BREAK** (128 lines) → DebugHandler
🔄 **STEP/CONTINUE** (66 lines) → DebugHandler
🔄 **INSPECT/WATCH/STACK** (194 lines) → DebugHandler
🔄 **MODIFY/PROFILE** (186 lines) → DebugHandler
🔄 **GET/SET** (236 lines) → DataHandler
🔄 **OUTPUT** (183 lines + 12 helpers) → ExtensionHandler
🔄 **DEV** (188 lines + 4 helpers) → DevModeHandler
🔄 **REBOOT/DESTROY/CLEAN** (164 lines) → SystemOpsHandler

---

## PART 4: DEPENDENCY MAP

### External Dependencies by Category

**Configuration**:
- `core.theme_manager.ThemeManager`
- `core.services.setup_wizard.SetupWizard`
- `core.config_manager.ConfigManager`

**Session**:
- `core.services.session_manager.SessionManager`
- `core.utils.usage_tracker.UsageTracker`

**Display**:
- `core.output.layout_manager.LayoutManager`
- `core.output.screen_manager.ScreenManager`
- `core.output.splash`

**Debug**:
- `core.interpreters.ucode_debugger.UCodeDebugger`

**System**:
- `extensions.server_manager.ServerManager`
- `extensions.core.extension_manager.ExtensionManager`
- `core.services.dev_mode_manager.DevModeManager`
- `core.commands.sandbox_handler.SandboxHandler`

**Shared Services** (used across categories):
- `core.services.help_manager.HelpManager`
- `core.utils.progress_manager.ProgressManager`
- Story manager (base class)
- Config manager (base class)

---

## PART 5: SPLIT RECOMMENDATION

### Proposed Structure (4 New Handlers + 1 Utility)

```
core/commands/
├── system_handler.py          # Slim router (300 lines)
├── config_handler.py          # NEW: Configuration & Settings
├── session_handler.py         # NEW: Session & History
├── display_handler.py         # NEW: Layout & Display
├── debug_handler.py           # NEW: Debug & Development
├── system_ops_handler.py      # NEW: System Operations
└── shared/
    └── system_utilities.py    # Shared helper methods
```

---

### Handler 1: **ConfigurationHandler** (Enhanced)
**File**: `core/commands/config_handler.py`
**Commands**: THEME, CONFIG, WIZARD, SETTINGS
**Estimated Lines**: ~1,300

**Methods to Move**:
- `handle_theme` (208 lines)
- `handle_config` (53 lines) - merge with existing
- `handle_wizard` (58 lines)
- `handle_settings` (23 lines) - merge with existing
- Theme helpers (7 methods, ~200 lines)
- Config helpers (1 method)

**New Responsibilities**:
- Theme selection and customization
- Accessibility settings (contrast, colorblind)
- Setup wizard orchestration
- Configuration file management
- Settings validation

**Dependencies**:
- ThemeManager, SetupWizard, ConfigManager
- Merge with existing ConfigurationHandler

**Integration**:
- Extend existing `configuration_handler.py`
- Add theme management methods
- Add wizard methods

---

### Handler 2: **SessionHandler** (New)
**File**: `core/commands/session_handler.py`
**Commands**: SESSION, HISTORY, UNDO, REDO, RESTORE
**Estimated Lines**: ~900

**Methods to Move**:
- `handle_session` (198 lines)
- `handle_history` (128 lines)
- `handle_undo` (23 lines)
- `handle_redo` (23 lines)
- `handle_restore` (78 lines)
- Session helpers (9 methods, ~198 lines)
- History helpers (5 methods, ~128 lines)

**New Responsibilities**:
- Session lifecycle management
- Command history tracking and search
- State persistence and restoration
- Checkpoint creation
- Session import/export
- Bulk undo/redo operations

**Dependencies**:
- SessionManager, UsageTracker
- Command history system
- History system (from base)

**Integration**:
- Create new standalone handler
- Inherit from BaseCommandHandler
- Expose session API for other handlers

---

### Handler 3: **DisplayHandler** (New)
**File**: `core/commands/display_handler.py`
**Commands**: LAYOUT, BLANK, SPLASH, HELP, PROGRESS
**Estimated Lines**: ~800

**Methods to Move**:
- `handle_layout` (228 lines)
- `handle_blank` (65 lines)
- `handle_splash` (48 lines)
- `handle_help` (78 lines)
- `handle_progress` (268 lines)
- Layout helpers (8 methods, ~228 lines)
- Progress helpers (7 methods, ~268 lines)

**New Responsibilities**:
- Adaptive layout management
- Screen clearing and formatting
- Splash screen rendering
- Help system integration
- Progress indicator management
- Responsive UI adjustments

**Dependencies**:
- LayoutManager, ScreenManager
- HelpManager, ProgressManager
- Splash module

**Integration**:
- Create new standalone handler
- Coordinate with DashboardHandler for VIEWPORT/PALETTE
- Share layout utilities

---

### Handler 4: **DebugHandler** (New)
**File**: `core/commands/debug_handler.py`
**Commands**: DEBUG, BREAK, STEP, CONTINUE, INSPECT, WATCH, STACK, MODIFY, PROFILE
**Estimated Lines**: ~800

**Methods to Move**:
- `handle_debug` (108 lines)
- `handle_breakpoint` (128 lines)
- `handle_step` (43 lines)
- `handle_continue` (23 lines)
- `handle_inspect` (68 lines)
- `handle_watch` (88 lines)
- `handle_stack` (38 lines)
- `handle_modify` (58 lines)
- `handle_profile` (128 lines)
- `handle_history` (debugger) (78 lines)

**New Responsibilities**:
- uCODE script debugging
- Breakpoint management (conditional, hit count)
- Step execution (over, into, out)
- Variable inspection and modification
- Watch expression management
- Call stack visualization
- Performance profiling
- Variable history tracking

**Dependencies**:
- UCodeDebugger (via parser.ucode)
- Parser instance

**Integration**:
- Create new standalone handler
- Requires parser injection for uCODE access
- Could be split further into debugger_handler + profiler_handler

---

### Handler 5: **SystemOpsHandler** (New)
**File**: `core/commands/system_ops_handler.py`
**Commands**: REBOOT, DESTROY, CLEAN, OUTPUT, DEV, WORKSPACE
**Estimated Lines**: ~700

**Methods to Move**:
- `handle_reboot` (38 lines)
- `handle_destroy` (68 lines)
- `handle_clean` (58 lines)
- `handle_output` (183 lines)
- `handle_dev_mode` (188 lines)
- `handle_workspace` (stub)
- Output helpers (12 methods, ~183 lines)
- DEV MODE helpers (4 methods, ~188 lines)

**New Responsibilities**:
- System reboot/restart
- Destructive operations (with safety)
- Sandbox cleaning
- Extension/server management
- DEV MODE authentication and control
- Workspace management (future)

**Dependencies**:
- ServerManager, ExtensionManager
- DevModeManager
- SandboxHandler

**Integration**:
- Create new standalone handler
- Critical commands - require extra safety checks
- Extension management could be further split

---

### Shared Utilities Module
**File**: `core/commands/shared/system_utilities.py`
**Purpose**: Common helper methods used across handlers
**Estimated Lines**: ~200

**Contents**:
- Input validation utilities
- Output formatting helpers
- Common error messages
- Shared constants
- Utility decorators (e.g., @requires_dev_mode)

---

## PART 6: MIGRATION STRATEGY

### Phase 1: Prepare (Week 1)
1. Create new handler files with stubs
2. Set up imports and base class inheritance
3. Document current command routing in `system_handler.py`
4. Create comprehensive test suite for existing functionality

### Phase 2: Extract (Weeks 2-3)
**Priority Order**:
1. **DebugHandler** (most isolated, least dependencies)
2. **SessionHandler** (well-defined boundaries)
3. **DisplayHandler** (moderate dependencies)
4. **SystemOpsHandler** (careful - critical commands)
5. **ConfigHandler** (merge with existing)

**Per Handler**:
- Move handle methods
- Move helper methods
- Update imports
- Add delegation in system_handler
- Run tests
- Commit atomically

### Phase 3: Slim Router (Week 4)
**Reduce `system_handler.py` to**:
- Property definitions (lazy loading)
- Command routing table
- Delegation logic only
- **Target**: <300 lines

### Phase 4: Test & Validate (Week 5)
- Full integration testing
- Performance benchmarking
- Documentation updates
- Shakedown validation

### Phase 5: Optimize (Week 6)
- Extract shared utilities
- Remove code duplication
- Improve error handling
- Add type hints
- Update wiki documentation

---

## PART 7: LINE RANGE EXTRACTION MAP

### ConfigurationHandler
```python
# From system_handler.py lines 472-680 (THEME)
handle_theme()
_show_theme_info()
_list_themes()
_set_theme()
_toggle_accessibility()
_toggle_contrast()
_set_colorblind_support()
_create_custom_theme()

# From lines 1802-1860 (WIZARD)
handle_wizard()
```

### SessionHandler
```python
# From lines 342-470 (HISTORY)
handle_history()
_show_recent_history()
_search_history()
_show_history_stats()
_clear_history()
_export_history()

# From lines 952-1150 (SESSION)
handle_session()
_show_current_session()
_list_sessions()
_save_session()
_load_session()
_delete_session()
_toggle_auto_save()
_create_checkpoint()
_export_session()
_import_session()

# From lines 2052-2180 (UNDO/REDO/RESTORE)
handle_undo()
handle_redo()
handle_restore()
```

### DisplayHandler
```python
# From lines 195-260 (BLANK)
handle_blank()

# From lines 262-340 (HELP)
handle_help()

# From lines 682-950 (PROGRESS)
handle_progress()
_show_active_progress()
_test_basic_progress()
_test_multi_stage_progress()
_test_search_progress()
_list_active_progress()
_cancel_progress()
_run_progress_demo()

# From lines 1152-1380 (LAYOUT)
handle_layout()
_show_layout_info()
_set_layout_mode()
_force_resize_detection()
_toggle_auto_resize()
_update_layout_config()
_test_adaptive_formatting()
_layout_demo()
_demo_split_layout()

# From lines 1692-1740 (SPLASH)
handle_splash()
```

### DebugHandler
```python
# From lines 2182-2960 (ALL DEBUG COMMANDS)
handle_debug()            # 2182-2290
handle_breakpoint()       # 2292-2420
handle_step()             # 2422-2465
handle_continue()         # 2467-2490
handle_inspect()          # 2492-2560
handle_watch()            # 2562-2650
handle_stack()            # 2652-2690
handle_modify()           # 2692-2750
handle_profile()          # 2752-2880
handle_history()          # 2882-2960 (debugger version)
```

### SystemOpsHandler
```python
# From lines 1582-1690 (REBOOT/DESTROY)
handle_reboot()           # 1582-1620
handle_destroy()          # 1622-1690

# From lines 1742-1800 (CLEAN)
handle_clean()            # 1742-1800

# From lines 1862-2050 (OUTPUT/WORKSPACE)
handle_workspace()        # 1862-1865
handle_output()           # 1867-2050
_handle_output_list()
_handle_output_status()
_handle_output_start()
_handle_output_stop()
_handle_output_health()
_handle_output_restart()
_handle_extension_discover()
_handle_extension_info()
_handle_extension_info_basic()
_handle_extension_install()
_handle_extension_uninstall()
_handle_extension_marketplace()

# From lines 3262-3450 (DEV MODE)
handle_dev_mode()         # 3262-3450
_dev_mode_enable()
_dev_mode_disable()
_dev_mode_status()
_dev_mode_help()
```

### DataHandler (Optional - could merge with SessionHandler)
```python
# From lines 2962-3200 (GET/SET)
handle_get()              # 2962-3080
handle_set()              # 3082-3200
```

---

## PART 8: RISK ASSESSMENT

### High Risk Areas
1. **Debug Commands** - Tightly coupled to parser.ucode.debugger
2. **DEV MODE** - Security-critical authentication logic
3. **DESTROY** - Destructive operations with safety checks
4. **SESSION** - State persistence, risk of data loss

### Medium Risk
1. **THEME** - UI changes, accessibility features
2. **LAYOUT** - Responsive adjustments, terminal detection
3. **OUTPUT** - Server management, extension lifecycle

### Low Risk
1. **HELP** - Read-only, well-isolated
2. **PROGRESS** - Testing/demo, no state changes
3. **SPLASH** - Display only

### Mitigation Strategies
- Atomic commits per handler
- Comprehensive test coverage before extraction
- Feature flags for gradual rollout
- Parallel implementations during transition
- Extensive integration testing

---

## PART 9: SUCCESS METRICS

### Before Refactoring
- **system_handler.py**: 3,664 lines
- **Methods**: 95 (41 handle + 54 helper)
- **Cyclomatic Complexity**: High (many nested conditionals)
- **Test Coverage**: Unknown (likely low due to monolithic structure)

### After Refactoring (Target)
- **system_handler.py**: <300 lines (90% reduction)
- **New Handlers**: 5 files, avg 700-1,300 lines each
- **Cyclomatic Complexity**: Medium (simplified routing)
- **Test Coverage**: >80% per handler
- **Maintainability Index**: Increase from ~30 to >60
- **Code Duplication**: <5% (shared utilities)

### Measurable Improvements
- ✅ Single Responsibility Principle: Each handler = 1 domain
- ✅ Easier testing: Isolated unit tests per handler
- ✅ Faster onboarding: Clear command → handler mapping
- ✅ Reduced merge conflicts: Changes isolated to relevant handlers
- ✅ Better error handling: Domain-specific error messages

---

## PART 10: NEXT STEPS

### Immediate Actions
1. ✅ **This Analysis** - Complete categorization map
2. ⏳ **Create Test Suite** - Cover existing functionality
3. ⏳ **Stub New Handlers** - Create empty handler files
4. ⏳ **Extract DebugHandler** - Start with most isolated handler
5. ⏳ **Update Documentation** - Wiki + inline docs

### Decision Points
- **Should GET/SET be separate DataHandler or merge with SessionHandler?**
  - Recommendation: **Separate DataHandler** (clear domain: field access)

- **Should OUTPUT commands split into ExtensionHandler?**
  - Recommendation: **Keep in SystemOpsHandler** for now (only 12 methods)

- **Should HELP move to HelpHandler or DisplayHandler?**
  - Recommendation: **DisplayHandler** (related to layout/formatting)

### Questions for Review
1. Should we create a `DebugProfilerHandler` split from `DebugHandler`?
2. Should WORKSPACE have its own handler (currently stub)?
3. Should we extract progress management to separate `ProgressHandler`?
4. Should theme management stay in ConfigHandler or separate `ThemeHandler`?

---

## APPENDIX A: Full Method List

### Handle Methods (Alphabetical)
1. handle_assets
2. handle_blank
3. handle_breakpoint
4. handle_clean
5. handle_config
6. handle_config_planet
7. handle_continue
8. handle_dashboard
9. handle_debug
10. handle_destroy
11. handle_dev_mode
12. handle_get
13. handle_help
14. handle_history (2 versions: session + debugger)
15. handle_inspect
16. handle_layout
17. handle_locate
18. handle_modify
19. handle_output
20. handle_palette
21. handle_profile
22. handle_progress
23. handle_reboot
24. handle_redo
25. handle_repair
26. handle_restore
27. handle_session
28. handle_set
29. handle_settings
30. handle_shakedown
31. handle_splash
32. handle_stack
33. handle_status
34. handle_step
35. handle_theme
36. handle_undo
37. handle_viewport
38. handle_watch
39. handle_wizard
40. handle_workspace

### Helper Methods (by Category)
**Config**: `_handle_config_role`

**DEV MODE**: `_dev_mode_enable`, `_dev_mode_disable`, `_dev_mode_status`, `_dev_mode_help`

**History**: `_show_recent_history`, `_search_history`, `_show_history_stats`, `_clear_history`, `_export_history`

**Layout**: `_show_layout_info`, `_set_layout_mode`, `_force_resize_detection`, `_toggle_auto_resize`, `_update_layout_config`, `_test_adaptive_formatting`, `_layout_demo`, `_demo_split_layout`

**Output**: `_handle_output_list`, `_handle_output_status`, `_handle_output_start`, `_handle_output_stop`, `_handle_output_health`, `_handle_output_restart`, `_handle_extension_discover`, `_handle_extension_info`, `_handle_extension_info_basic`, `_handle_extension_install`, `_handle_extension_uninstall`, `_handle_extension_marketplace`

**Progress**: `_show_active_progress`, `_test_basic_progress`, `_test_multi_stage_progress`, `_test_search_progress`, `_list_active_progress`, `_cancel_progress`, `_run_progress_demo`

**Session**: `_show_current_session`, `_list_sessions`, `_save_session`, `_load_session`, `_delete_session`, `_toggle_auto_save`, `_create_checkpoint`, `_export_session`, `_import_session`

**Theme**: `_show_theme_info`, `_list_themes`, `_set_theme`, `_toggle_accessibility`, `_toggle_contrast`, `_set_colorblind_support`, `_create_custom_theme`

---

## APPENDIX B: Delegation Patterns

### Current Delegation (11 handlers)
```python
# Pattern: Create handler instance, call method
from .specialized_handler import SpecializedHandler

handler = SpecializedHandler(
    connection=self.connection,
    viewport=self.viewport,
    # ... context params
)
return handler.handle_command(params, grid, parser)
```

### Proposed Delegation (All commands)
```python
# Pattern: Lazy-loaded handler properties
@property
def session_handler(self):
    if self._session_handler is None:
        from .session_handler import SessionHandler
        self._session_handler = SessionHandler(**self.get_handler_context())
    return self._session_handler

# In handle() method
handlers = {
    'SESSION': self.session_handler.handle_session,
    'HISTORY': self.session_handler.handle_history,
    # ...
}
```

---

**END OF ANALYSIS**

Generated: 2025-11-30
Analyst: GitHub Copilot
File Version: v1.5.3+
Total Analysis Time: ~45 minutes
Confidence: High ✅
