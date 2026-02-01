# TUI Stability Plan (Option B)

**Version:** 1.0  
**Date:** 2026-01-31  
**Priority:** High — Foundation for TypeScript Runtime  
**Duration:** 3-5 days

---

## 🎯 Objective

Polish TUI stability before TypeScript Markdown Runtime implementation, focusing on:
1. Ghost mode / non-interactive environment handling
2. Hot-reload watcher edge cases
3. Variable input handler consistency
4. Terminal interactivity detection

---

## 📋 Current Status

### ✅ Completed
- Health training system (`core/services/health_training.py`)
- System script runner (`core/services/system_script_runner.py`)
- Self-healer expanded diagnostics
- Hot reload basic implementation
- Story form handler with DateTimeApproval
- Fallback form handler (`SimpleFallbackFormHandler`)

### 🔍 Needs Verification
- Terminal interactivity checks across all input handlers
- Hot-reload watcher stability under file churn
- Variable input handlers during window resize
- Ghost mode / CI environment fallback paths

---

## 🔧 Components to Audit

### 1. Terminal Interactivity Checks

**Files with `isatty()` checks:**
- [core/ui/interactive_menu.py](core/ui/interactive_menu.py) — `tty.setraw(sys.stdin.fileno())`
- [core/input/smart_prompt.py](core/input/smart_prompt.py) — `sys.stdin.isatty()`
- [core/tui/advanced_form_handler.py](core/tui/advanced_form_handler.py) — `sys.stdout.isatty()`
- [core/tui/story_form_handler.py](core/tui/story_form_handler.py) — `sys.stdin.isatty()` and `sys.stdout.isatty()`
- [core/services/dependency_warning_monitor.py](core/services/dependency_warning_monitor.py) — `sys.stdin.isatty()`

**Common Pattern:**
```python
def _is_interactive(self) -> bool:
    """Check if running in interactive terminal."""
    return sys.stdin.isatty() and sys.stdout.isatty()
```

**Edge Cases to Test:**
1. Piped input: `echo "SETUP" | python -m core.cli`
2. Redirected output: `python -m core.cli > output.log`
3. Background process: `python -m core.cli &`
4. CI environment: `TERM=dumb python -m core.cli`
5. SSH without TTY: `ssh user@host "python -m core.cli"`

---

### 2. Input Handler Graceful Degradation

**Primary Handler:** `StoryFormHandler`
- Uses `termios.tcgetattr()` and `tty.setraw()`
- Has exception handling but needs comprehensive testing

**Fallback Handler:** `SimpleFallbackFormHandler`
- Uses basic `input()` calls
- Should activate when:
  - `isatty()` returns `False`
  - `termios` operations fail
  - Terminal resize interrupts input

**Enhancement Needed:**
```python
def _setup_terminal(self) -> None:
    """Setup terminal for raw input capture."""
    try:
        # Check if interactive FIRST
        if not self._is_interactive():
            logger.info("[LOCAL] Non-interactive mode detected, using fallback")
            raise EnvironmentError("Non-interactive environment")
        
        self.original_settings = termios.tcgetattr(sys.stdin)
        tty.setraw(sys.stdin.fileno())
    except Exception as e:
        logger.warning(f"[LOCAL] Could not setup terminal: {e}")
        # Signal to use SimpleFallbackFormHandler
        raise

def _is_interactive(self) -> bool:
    """Check if running in interactive terminal."""
    return sys.stdin.isatty() and sys.stdout.isatty()
```

---

### 3. Hot Reload Watcher

**File:** [core/services/hot_reload.py](core/services/hot_reload.py)

**Current Implementation:**
- Watches `core/commands/` directory
- Uses `watchdog` library
- Tracks reload count and failures

**Edge Cases to Test:**
1. **Rapid file changes** (save, save, save)
   - Should debounce or handle gracefully
2. **File being edited** (partial write)
   - Should wait for write completion
3. **Syntax errors in handler**
   - Should log error, not crash watcher
4. **Handler removal**
   - Should unregister command
5. **Watcher crash recovery**
   - Should log and continue without crashing TUI

**Enhancement Strategy:**
```python
def _should_reload_file(filepath: str, last_modified: Dict[str, float]) -> bool:
    """Check if file should be reloaded with debouncing."""
    now = time.time()
    last_mod = last_modified.get(filepath, 0)
    
    # Debounce: require 500ms between reloads
    if now - last_mod < 0.5:
        return False
    
    last_modified[filepath] = now
    return True
```

---

### 4. Variable Input Handlers

**Files:**
- [core/input/smart_prompt.py](core/input/smart_prompt.py) — SmartPrompt with autocomplete
- [core/input/enhanced_prompt.py](core/input/enhanced_prompt.py) — 2-line context display
- [core/input/command_prompt.py](core/input/command_prompt.py) — Command registry integration

**Requirements:**
- Emit predictions even during window resize
- Surface TUI command prompt reliably
- Graceful degradation when `prompt_toolkit` unavailable

**Current Fallback:**
```python
if not HAS_PROMPT_TOOLKIT:
    # Falls back to basic input()
    logger.warning("[LOCAL] prompt_toolkit not available, using basic input")
```

**Test Scenarios:**
1. Window resize mid-input
2. Prediction list overflow (> terminal height)
3. Command prediction with special characters
4. History navigation after resize

---

## 🧪 Test Plan

### Phase 1: Terminal Interactivity (Day 1)

**Test Script:** `tests/test_terminal_interactivity.py`

```python
import subprocess
import sys

def test_piped_input():
    """Test with piped input."""
    result = subprocess.run(
        ["python", "-m", "core.cli", "SETUP"],
        input=b"Test User\ntest@example.com\n",
        capture_output=True
    )
    assert result.returncode == 0
    assert b"fallback" in result.stdout.lower()

def test_redirected_output():
    """Test with redirected output."""
    result = subprocess.run(
        ["python", "-m", "core.cli", "HELP"],
        capture_output=True
    )
    assert result.returncode == 0

def test_background_process():
    """Test as background process."""
    # Should detect non-interactive and use fallback
    pass

def test_ci_environment():
    """Test in CI-like environment."""
    env = {**os.environ, "TERM": "dumb", "CI": "true"}
    result = subprocess.run(
        ["python", "-m", "core.cli", "VERSION"],
        env=env,
        capture_output=True
    )
    assert result.returncode == 0
```

### Phase 2: Hot Reload Stability (Day 2)

**Test Script:** `tests/test_hot_reload_stability.py`

```python
import time
from core.services.hot_reload import HotReloadManager

def test_rapid_file_changes():
    """Test rapid consecutive saves."""
    # Modify file 10 times in 1 second
    # Should debounce and only reload once
    pass

def test_syntax_error_recovery():
    """Test reload with syntax error."""
    # Introduce syntax error
    # Should log error, continue watching
    pass

def test_handler_removal():
    """Test handler file deletion."""
    # Delete handler file
    # Should unregister command gracefully
    pass

def test_watcher_crash_recovery():
    """Test watcher recovery from crashes."""
    # Simulate watchdog observer crash
    # Should restart or fail gracefully
    pass
```

### Phase 3: Input Handler Edge Cases (Day 3)

**Test Script:** `tests/test_input_handlers.py`

```python
def test_window_resize_during_input():
    """Test terminal resize during input."""
    # Simulate SIGWINCH signal
    # Should preserve input buffer
    pass

def test_prediction_overflow():
    """Test prediction list longer than terminal."""
    # Generate 100+ predictions
    # Should paginate or truncate gracefully
    pass

def test_special_characters():
    """Test commands with special chars."""
    # Test: LOCATION "New York, NY"
    # Should handle quotes and commas
    pass
```

---

## 🔨 Implementation Tasks

### Task 1: Add `_is_interactive()` check to all input handlers
**Files:** story_form_handler.py, interactive_menu.py, advanced_form_handler.py  
**Estimate:** 2 hours

### Task 2: Enhance hot_reload with debouncing
**File:** [core/services/hot_reload.py](core/services/hot_reload.py)  
**Estimate:** 3 hours

### Task 3: Add fallback activation logging
**All input handlers**  
**Estimate:** 1 hour

### Task 4: Write comprehensive tests
**New files:** tests/test_terminal_interactivity.py, test_hot_reload_stability.py, test_input_handlers.py  
**Estimate:** 4 hours

### Task 5: Document fallback behavior
**File:** [docs/specs/STANDARD-INPUT-HANDLERS.md](docs/specs/STANDARD-INPUT-HANDLERS.md)  
**Estimate:** 2 hours

---

## 📝 Success Criteria

- [ ] All input handlers check `_is_interactive()` before raw mode
- [ ] `SimpleFallbackFormHandler` activates in all non-interactive scenarios
- [ ] Hot reload watcher survives file churn without crashes
- [ ] Variable input handlers maintain state during window resize
- [ ] All edge case tests pass
- [ ] Documentation updated with fallback behavior

---

## 🎯 Next Phase: TypeScript Runtime (Option C)

After TUI stability is confirmed, proceed to:

### Review & Plan Phase (2-3 days)
1. Review [typescript-markdown-runtime.md](specs/typescript-markdown-runtime.md) ✅ (Already reviewed)
2. Review [script-executor.ts](core/src/executors/script-executor.ts) ✅ (Basic implementation exists)
3. Check for STREAM1-ACTION-PLAN.md ❌ (Does not exist, needs creation)
4. Create detailed task breakdown for:
   - Phase 1A: State management (`$variables`)
   - Phase 1B: Runtime blocks (`state`, `set`, `form`, `if/else`, `nav`, `panel`, `map`)
   - Phase 1C: Variable interpolation
   - Phase 1D: SQLite DB binding
   - Phase 1E: Node runner

### Implementation Roadmap Reference
- [STREAM1-ACTION-PLAN.md](STREAM1-ACTION-PLAN.md) (To be created)
- [typescript-markdown-runtime.md](specs/typescript-markdown-runtime.md) (Reference spec)
- [core/src/executors/](core/src/executors/) (Executor implementations)

---

## 📊 Timeline

| Phase | Duration | Tasks |
|-------|----------|-------|
| **Day 1** | 8 hours | Terminal interactivity checks, fallback enhancement |
| **Day 2** | 8 hours | Hot reload debouncing, error recovery |
| **Day 3** | 8 hours | Input handler edge cases, window resize handling |
| **Day 4** | 6 hours | Comprehensive testing, bug fixes |
| **Day 5** | 4 hours | Documentation, validation |

**Total:** 34 hours (~3-5 days)

---

## 🚀 Ready to Begin?

**Start with:** Task 1 — Add `_is_interactive()` checks  
**First file:** [core/tui/story_form_handler.py](core/tui/story_form_handler.py)

Would you like me to begin implementation?
