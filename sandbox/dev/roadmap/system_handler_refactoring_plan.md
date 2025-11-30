# System Handler Refactoring Plan
**Version**: v1.1.5.1 (Phase 1 Task 2)
**Timeline**: 5-6 days
**Status**: PLANNING
**Date**: 2025-11-30

---

## OVERVIEW

Refactor `core/commands/system_handler.py` (3,663 lines) into 4 focused handlers:

1. **ConfigurationHandler** (enhanced) - 1,300 lines
2. **SessionHandler** (new) - 900 lines
3. **DisplayHandler** (new) - 800 lines
4. **DebugHandler** (new) - 800 lines

**Result**: SystemCommandHandler becomes slim router (~300 lines, 90% reduction)

---

## INCREMENTAL MIGRATION STRATEGY

### Phase A: Create New Handlers (Day 1-2)

#### Task A1: Create SessionHandler (2-3 hours)
**File**: `core/commands/session_handler.py`
**Extract**: Lines 342-1150 + 2052-2180

**Methods**:
- `handle_session` (952-1150)
- `handle_history` (342-470)
- `handle_undo` (2052-2075)
- `handle_redo` (2077-2100)
- `handle_restore` (2102-2180)
- 9 session helpers (952-1150)
- 5 history helpers (342-470)

**Commands**: SESSION, HISTORY, UNDO, REDO, RESTORE

**Template**:
```python
"""
uDOS Session & History Handler

Manages session lifecycle, command history, and state restoration.
"""

from .base_handler import BaseCommandHandler

class SessionHandler(BaseCommandHandler):
    """Handles session management and command history."""

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self._session_manager = None
        self._usage_tracker = None

    @property
    def session_manager(self):
        if self._session_manager is None:
            from core.services.session_manager import SessionManager
            self._session_manager = SessionManager()
        return self._session_manager

    @property
    def usage_tracker(self):
        if self._usage_tracker is None:
            from core.utils.usage_tracker import UsageTracker
            self._usage_tracker = UsageTracker()
        return self._usage_tracker

    def handle(self, command, params, grid, parser):
        """Route session commands."""
        handlers = {
            'SESSION': self.handle_session,
            'HISTORY': self.handle_history,
            'UNDO': self.handle_undo,
            'REDO': self.handle_redo,
            'RESTORE': self.handle_restore
        }

        handler = handlers.get(command)
        if handler:
            return handler(params, grid, parser)

        return False

    # [COPY METHODS FROM system_handler.py]
```

**Verification**:
```python
# Test: sandbox/tests/test_session_handler.py
def test_session_save():
    handler = SessionHandler()
    result = handler.handle('SESSION', ['--save', 'test'], None, None)
    assert result is True

def test_history_search():
    handler = SessionHandler()
    result = handler.handle('HISTORY', ['--search', 'KNOW'], None, None)
    assert result is True
```

---

#### Task A2: Create DisplayHandler (2-3 hours)
**File**: `core/commands/display_handler.py`
**Extract**: Lines 195-260, 682-950, 1152-1380, 1692-1740, 262-340

**Methods**:
- `handle_blank` (195-260)
- `handle_layout` (1152-1380)
- `handle_splash` (1692-1740)
- `handle_help` (262-340)
- `handle_progress` (682-950)
- 8 layout helpers
- 7 progress helpers

**Commands**: LAYOUT, BLANK, SPLASH, HELP, PROGRESS

**Template**:
```python
"""
uDOS Display & Layout Handler

Manages adaptive UI, screen formatting, and progress indicators.
"""

from .base_handler import BaseCommandHandler

class DisplayHandler(BaseCommandHandler):
    """Handles display, layout, and UI management."""

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self._layout_manager = None
        self._screen_manager = None
        self._help_manager = None
        self._progress_manager = None

    # [LAZY LOADERS]

    def handle(self, command, params, grid, parser):
        """Route display commands."""
        handlers = {
            'BLANK': self.handle_blank,
            'LAYOUT': self.handle_layout,
            'SPLASH': self.handle_splash,
            'HELP': self.handle_help,
            'PROGRESS': self.handle_progress
        }

        handler = handlers.get(command)
        if handler:
            return handler(params, grid, parser)

        return False

    # [COPY METHODS FROM system_handler.py]
```

**Verification**:
```python
# Test: sandbox/tests/test_display_handler.py
def test_blank():
    handler = DisplayHandler()
    result = handler.handle('BLANK', [], None, None)
    assert result is True

def test_layout_info():
    handler = DisplayHandler()
    result = handler.handle('LAYOUT', ['--info'], None, None)
    assert result is True
```

---

#### Task A3: Create DebugHandler (3-4 hours)
**File**: `core/commands/debug_handler.py`
**Extract**: Lines 2182-2960

**Methods**:
- `handle_debug` (2182-2290)
- `handle_breakpoint` (2292-2420)
- `handle_step` (2422-2465)
- `handle_continue` (2467-2490)
- `handle_inspect` (2492-2560)
- `handle_watch` (2562-2650)
- `handle_stack` (2652-2690)
- `handle_modify` (2692-2750)
- `handle_profile` (2752-2880)
- `handle_history` (debugger) (2882-2960)

**Commands**: DEBUG, BREAK, STEP, CONTINUE, INSPECT, WATCH, STACK, MODIFY, PROFILE

**Template**:
```python
"""
uDOS Debugger Handler

Complete debugging system for uCODE scripts.
"""

from .base_handler import BaseCommandHandler

class DebugHandler(BaseCommandHandler):
    """Handles uCODE debugging operations."""

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

    def handle(self, command, params, grid, parser):
        """Route debug commands."""
        handlers = {
            'DEBUG': self.handle_debug,
            'BREAK': self.handle_breakpoint,
            'STEP': self.handle_step,
            'CONTINUE': self.handle_continue,
            'INSPECT': self.handle_inspect,
            'WATCH': self.handle_watch,
            'STACK': self.handle_stack,
            'MODIFY': self.handle_modify,
            'PROFILE': self.handle_profile
        }

        handler = handlers.get(command)
        if handler:
            return handler(params, grid, parser)

        return False

    # [COPY METHODS FROM system_handler.py]
```

**Verification**:
```python
# Test: sandbox/tests/test_debug_handler.py
def test_debug_enable():
    handler = DebugHandler()
    # Requires parser with uCODE debugger
    # Integration test with actual .uscript file
```

---

#### Task A4: Enhance ConfigurationHandler (2-3 hours)
**File**: `core/commands/configuration_handler.py`
**Extract**: Lines 472-680, 1802-1860

**Add Methods**:
- `handle_theme` (472-680)
- `handle_wizard` (1802-1860)
- 7 theme helpers

**New Commands**: THEME, WIZARD (to existing CONFIG, SETTINGS)

**Changes**:
```python
# In configuration_handler.py, add to handle():
handlers = {
    'CONFIG': self.handle_config,
    'SETTINGS': self.handle_settings,
    'THEME': self.handle_theme,      # NEW
    'WIZARD': self.handle_wizard      # NEW
}
```

**Verification**:
```python
# Test: sandbox/tests/test_configuration_handler.py
def test_theme_switch():
    handler = ConfigurationHandler()
    result = handler.handle('THEME', ['galaxy'], None, None)
    assert result is True

def test_wizard_launch():
    handler = ConfigurationHandler()
    result = handler.handle('WIZARD', [], None, None)
    assert result is True
```

---

### Phase B: Update SystemHandler Router (Day 3)

#### Task B1: Add Handler Delegation (1 hour)
**File**: `core/commands/system_handler.py`

**Add Lazy Loaders**:
```python
@property
def session_handler(self):
    """Lazy load session handler."""
    if self._session_handler is None:
        from .session_handler import SessionHandler
        self._session_handler = SessionHandler(**self.get_handler_kwargs())
    return self._session_handler

@property
def display_handler(self):
    """Lazy load display handler."""
    if self._display_handler is None:
        from .display_handler import DisplayHandler
        self._display_handler = DisplayHandler(**self.get_handler_kwargs())
    return self._display_handler

@property
def debug_handler(self):
    """Lazy load debug handler."""
    if self._debug_handler is None:
        from .debug_handler import DebugHandler
        self._debug_handler = DebugHandler(**self.get_handler_kwargs())
    return self._debug_handler
```

**Update handle() Method**:
```python
def handle(self, command, params, grid, parser):
    """Route system commands to specialized handlers."""

    # Session & History
    if command in ['SESSION', 'HISTORY', 'UNDO', 'REDO', 'RESTORE']:
        return self.session_handler.handle(command, params, grid, parser)

    # Display & Layout
    if command in ['BLANK', 'LAYOUT', 'SPLASH', 'HELP', 'PROGRESS']:
        return self.display_handler.handle(command, params, grid, parser)

    # Debug
    if command in ['DEBUG', 'BREAK', 'STEP', 'CONTINUE', 'INSPECT', 'WATCH', 'STACK', 'MODIFY', 'PROFILE']:
        return self.debug_handler.handle(command, params, grid, parser)

    # Configuration (enhanced)
    if command in ['THEME', 'WIZARD']:
        return self.configuration_handler.handle(command, params, grid, parser)

    # ... existing delegations ...

    # Remaining system ops (REBOOT, DESTROY, CLEAN, OUTPUT, DEV, etc.)
    # Keep inline for now (Phase 2)
```

---

#### Task B2: Remove Extracted Methods (1 hour)
**File**: `core/commands/system_handler.py`

**Delete Lines**:
- 195-260 (handle_blank + helpers)
- 262-340 (handle_help)
- 342-470 (handle_history + helpers)
- 472-680 (handle_theme + helpers)
- 682-950 (handle_progress + helpers)
- 952-1150 (handle_session + helpers)
- 1152-1380 (handle_layout + helpers)
- 1692-1740 (handle_splash)
- 1802-1860 (handle_wizard)
- 2052-2180 (handle_undo/redo/restore)
- 2182-2960 (all debug methods)

**Result**: ~2,500 lines removed, ~1,100 lines remain

---

### Phase C: Testing & Verification (Day 4)

#### Task C1: Create Handler Tests (2 hours)
**Files**:
- `sandbox/tests/test_session_handler.py`
- `sandbox/tests/test_display_handler.py`
- `sandbox/tests/test_debug_handler.py`
- `sandbox/tests/test_configuration_handler.py` (update)

**Test Coverage**:
- Each command handler method
- Parameter parsing
- Error handling
- Delegation chain
- Lazy loading

---

#### Task C2: Run Integration Tests (1 hour)
**Commands**:
```bash
# Shakedown test
./start_udos.sh sandbox/ucode/shakedown.uscript

# Pytest
pytest sandbox/tests/ -v

# Manual smoke tests
python uDOS.py
> SESSION --save test
> HISTORY --recent 10
> THEME galaxy
> LAYOUT --info
> BLANK
> DEBUG --enable
> HELP KNOW
```

---

#### Task C3: Update Documentation (1 hour)
**Files**:
- `core/commands/README.md` - Update handler list
- `wiki/Architecture.md` - Update command routing diagram
- `wiki/Developers-Guide.md` - Update handler creation guide

**Add**:
```markdown
### Handler Architecture (v1.1.5.1+)

SystemCommandHandler now delegates to specialized handlers:

- **SessionHandler**: SESSION, HISTORY, UNDO, REDO, RESTORE
- **DisplayHandler**: BLANK, LAYOUT, SPLASH, HELP, PROGRESS
- **DebugHandler**: DEBUG, BREAK, STEP, CONTINUE, INSPECT, WATCH, STACK, MODIFY, PROFILE
- **ConfigurationHandler**: CONFIG, SETTINGS, THEME, WIZARD (enhanced)
- **DashboardHandler**: STATUS, DASHBOARD, VIEWPORT, PALETTE
- **RepairHandler**: REPAIR
- **ShakedownHandler**: SHAKEDOWN

System handler retains: REBOOT, DESTROY, CLEAN, OUTPUT, DEV, WORKSPACE, GET, SET
```

---

### Phase D: Cleanup & Optimization (Day 5)

#### Task D1: Extract Shared Utilities (2 hours)
**File**: `core/commands/shared/system_utilities.py`

**Extract Common Patterns**:
```python
"""
Shared utilities for system command handlers.
"""

def format_command_list(commands, columns=3):
    """Format command list in columns."""
    # Extract from multiple handlers

def validate_session_name(name):
    """Validate session name format."""
    # Extract from SessionHandler

def parse_time_param(value):
    """Parse time parameter (1h, 30m, etc.)."""
    # Extract from multiple handlers

def format_table(data, headers):
    """Format data as ASCII table."""
    # Extract from multiple handlers
```

**Update Handlers**:
```python
# In session_handler.py
from .shared.system_utilities import validate_session_name, format_table

def _save_session(self, session_manager, name, description):
    if not validate_session_name(name):
        self.error("Invalid session name format")
        return False
    # ...
```

---

#### Task D2: Profile Performance (1 hour)
**Test**:
```bash
# Before refactoring
time python -c "from core.commands.system_handler import SystemCommandHandler; h = SystemCommandHandler()"

# After refactoring
time python -c "from core.commands.system_handler import SystemCommandHandler; h = SystemCommandHandler()"
```

**Measure**:
- Import time
- Memory footprint
- Lazy loading effectiveness

---

#### Task D3: Update Command Registry (1 hour)
**File**: `core/uDOS_commands.py`

**Update Command Map**:
```python
# Ensure all refactored commands route correctly
COMMAND_HANDLERS = {
    # Session & History (SessionHandler)
    'SESSION': 'system',
    'HISTORY': 'system',
    'UNDO': 'system',
    'REDO': 'system',
    'RESTORE': 'system',

    # Display & Layout (DisplayHandler)
    'BLANK': 'system',
    'LAYOUT': 'system',
    'SPLASH': 'system',
    'HELP': 'system',
    'PROGRESS': 'system',

    # Debug (DebugHandler)
    'DEBUG': 'system',
    'BREAK': 'system',
    'STEP': 'system',
    # ...
}
```

---

## ROLLBACK PLAN

If issues arise, revert in order:

1. **Day 4**: Revert `system_handler.py` from git
2. **Day 3**: Delete new handler files
3. **Day 2**: Restore original `configuration_handler.py`
4. **Day 1**: No changes to revert (only new files created)

**Git Strategy**:
```bash
# Checkpoint before each phase
git add -A
git commit -m "v1.1.5.1 Phase A: Created new handlers"
git commit -m "v1.1.5.1 Phase B: Updated SystemHandler router"
git commit -m "v1.1.5.1 Phase C: Testing & verification complete"
git commit -m "v1.1.5.1 Phase D: Cleanup & optimization complete"
```

---

## SUCCESS METRICS

✅ **Code Quality**:
- SystemHandler reduced from 3,663 → <300 lines (>90%)
- Each handler <1,000 lines (focused responsibility)
- No circular dependencies
- All tests passing

✅ **Performance**:
- Import time unchanged or improved (lazy loading)
- Memory footprint stable
- No regression in command execution speed

✅ **Maintainability**:
- Clear handler responsibilities
- Easy to locate command implementations
- Simplified testing (isolated handlers)

✅ **Documentation**:
- Updated architecture docs
- Updated developer guide
- Handler README complete

---

## TIMELINE SUMMARY

| Day | Phase | Tasks | Hours |
|-----|-------|-------|-------|
| 1 | A1-A2 | Create Session + Display handlers | 5-6 |
| 2 | A3-A4 | Create Debug handler + Enhance Config | 5-7 |
| 3 | B1-B2 | Update SystemHandler router + Delete old | 2 |
| 4 | C1-C3 | Testing, integration, documentation | 4 |
| 5 | D1-D3 | Extract utilities, optimize, registry | 4 |

**Total**: 20-23 hours over 5 days (4-5 hours/day)

---

## NEXT STEPS

1. **Today (Day 1)**: Start Phase A1 - Create SessionHandler
2. **Review**: Present analysis to user for approval
3. **Execute**: Follow incremental plan with git checkpoints
4. **Verify**: Test after each phase
5. **Document**: Update wiki as changes are made

**Ready to proceed?**
