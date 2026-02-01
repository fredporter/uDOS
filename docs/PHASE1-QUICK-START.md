# Phase 1 Quick-Start Checklist
**UDOS_ROOT Bootstrap Implementation**  
**Duration:** 4 hours  
**Status:** Ready to Execute

---

## Pre-Implementation Checklist (15 min)

- [ ] Reviewed `CONTAINERIZATION-READINESS-ASSESSMENT.md` (overview section)
- [ ] Reviewed `PHASE1-UDOS-ROOT-IMPLEMENTATION.md` (tasks 1-5)
- [ ] Have access to ~/uDOS/ directory
- [ ] Python venv is activated
- [ ] Can run tests: `pytest memory/`
- [ ] Git is ready: `git status` works
- [ ] Text editor is ready (edit `.py` and `.md` files)

---

## Implementation Checklist (3.5 hours)

### Task 1: Update `.env.example` (15 min)
**File:** `.env.example`

- [ ] Open `.env.example` in editor
- [ ] Add new section after existing fields:
```bash
# System Root Path (auto-detected at setup, containerization support)
UDOS_ROOT=/Users/fredbook/Code/uDOS
```
- [ ] Save file
- [ ] Verify section added: `grep UDOS_ROOT .env.example`
- [ ] ✅ **TASK 1 COMPLETE**

**Expected Output:**
```
UDOS_ROOT=/Users/fredbook/Code/uDOS
```

---

### Task 2: Add UDOS_ROOT Detection to setup_handler.py (30 min)
**File:** `core/commands/setup_handler.py`

- [ ] Open `core/commands/setup_handler.py`
- [ ] Find the imports section at top
- [ ] Add this helper function after imports (before other functions):

```python
def _detect_udos_root() -> Path:
    """
    Auto-detect uDOS repository root for UDOS_ROOT .env variable.
    
    Tries in order:
    1. UDOS_ROOT environment variable (container override)
    2. Relative path from this file (local development)
    3. Raise error if not found
    
    Returns:
        Path: Absolute path to uDOS repository root
    
    Raises:
        RuntimeError: If root cannot be detected
    """
    # Try environment first (containers will set this)
    env_root = os.getenv("UDOS_ROOT")
    if env_root:
        env_path = Path(env_root).expanduser()
        marker = env_path / "uDOS.py"
        if marker.exists():
            logger.info(f"[LOCAL] UDOS_ROOT detected from environment: {env_path}")
            return env_path
        else:
            logger.warning(f"[LOCAL] UDOS_ROOT env var set but uDOS.py not found at {env_path}")
    
    # Fall back to relative path discovery
    try:
        current_file = Path(__file__).resolve()
        # setup_handler.py → core/commands → core → root
        candidate = current_file.parent.parent.parent
        marker = candidate / "uDOS.py"
        
        if marker.exists():
            logger.info(f"[LOCAL] UDOS_ROOT auto-detected: {candidate}")
            return candidate
    except Exception as e:
        logger.warning(f"[LOCAL] Relative path detection failed: {e}")
    
    raise RuntimeError(
        "Cannot auto-detect uDOS root. Please:\n"
        "1. Ensure uDOS.py exists at repository root\n"
        "2. Or set UDOS_ROOT environment variable\n"
        "3. Or run setup from repository root directory"
    )
```

- [ ] Find the main setup function (`handle_setup_interactive`)
- [ ] Add UDOS_ROOT detection (add before existing .env write logic):

```python
    # Auto-detect and save UDOS_ROOT
    try:
        udos_root = _detect_udos_root()
        story_vars["UDOS_ROOT"] = str(udos_root)
        logger.info(f"[LOCAL] UDOS_ROOT will be saved: {udos_root}")
    except RuntimeError as e:
        logger.warning(f"[LOCAL] UDOS_ROOT detection failed: {e}")
```

- [ ] Save file
- [ ] Verify syntax: `python -m py_compile core/commands/setup_handler.py`
- [ ] ✅ **TASK 2 COMPLETE**

**Expected Output:**
```
# No syntax errors
```

---

### Task 3: Harden get_repo_root() in logging_service.py (30 min)
**File:** `core/services/logging_service.py` (lines 57-65)

- [ ] Open `core/services/logging_service.py`
- [ ] Find function `def get_repo_root() -> Path:` (around line 57)
- [ ] Replace entire function with:

```python
def get_repo_root() -> Path:
    """
    Get repository root, preferring UDOS_ROOT environment variable.
    
    Supports:
    - Container deployments (UDOS_ROOT set by container)
    - Local development (falls back to relative path)
    - Subprocess isolation (inherited UDOS_ROOT from parent)
    
    Returns:
        Path: Absolute path to uDOS repository root
        
    Raises:
        RuntimeError: If UDOS_ROOT is set but invalid
    """
    env_root = os.getenv("UDOS_ROOT")
    if env_root:
        env_path = Path(env_root).expanduser().resolve()
        marker = env_path / "uDOS.py"
        
        if marker.exists():
            # Container path: env var points to valid root
            return _enforce_home_root(env_path)
        else:
            # Invalid container setup
            raise RuntimeError(
                f"UDOS_ROOT={env_root} does not contain uDOS.py marker. "
                "Invalid container configuration or .env corruption."
            )
    
    # Local development fallback: Use relative path from this file
    try:
        current = Path(__file__).resolve()
        candidate = current.parent.parent.parent
        marker = candidate / "uDOS.py"
        
        if marker.exists():
            return _enforce_home_root(candidate)
        else:
            # This file is outside a valid uDOS repo
            raise RuntimeError(
                f"Cannot find uDOS.py at expected location: {candidate / 'uDOS.py'}. "
                "Set UDOS_ROOT environment variable or move repo to ~/uDOS."
            )
    except Exception as e:
        raise RuntimeError(
            f"Failed to detect repository root: {e}\n"
            "Set UDOS_ROOT environment variable or check repo structure."
        )
```

- [ ] Save file
- [ ] Verify syntax: `python -m py_compile core/services/logging_service.py`
- [ ] ✅ **TASK 3 COMPLETE**

---

### Task 4: Add Subprocess Environment Export (30 min)
**File:** `core/services/unified_logging.py`

- [ ] Open `core/services/unified_logging.py` (or `logging_service.py` if unified doesn't exist)
- [ ] Add this helper function (near top, after imports):

```python
def get_subprocess_environment() -> Dict[str, str]:
    """
    Get environment dictionary for subprocess execution.
    
    Ensures UDOS_ROOT is propagated to child processes, preventing
    relative path fallback issues in subprocesses.
    
    Returns:
        dict: Updated environment with UDOS_ROOT set
    """
    env = os.environ.copy()
    
    # Always try to set UDOS_ROOT if not already set
    if "UDOS_ROOT" not in env:
        try:
            env["UDOS_ROOT"] = str(get_repo_root())
        except Exception as e:
            logger.warning(f"[LOCAL] Could not set UDOS_ROOT for subprocess: {e}")
    
    return env
```

- [ ] Save file
- [ ] Verify syntax
- [ ] ✅ **TASK 4 COMPLETE**

---

### Task 5: Update TUI Setup Story (15 min)
**File:** `core/tui/setup-story.md`

- [ ] Open `core/tui/setup-story.md`
- [ ] Find the "Identity" or first main section
- [ ] Add new section after it:

```markdown
## System Paths

The system has detected your uDOS installation at:

```
UDOS_ROOT: /Users/fredbook/Code/uDOS
```

This value will be saved to your `.env` file and used by:
- **Wizard Server** — Locate plugins and config
- **Extensions** — Find shared resources
- **Containers** — Mount repository at runtime

**Why:** uDOS is designed for containerized deployments. Setting UDOS_ROOT enables:
- Plugin/bolt-on system compatibility
- Docker and Kubernetes support
- Clean separation of code from data
- Subprocess isolation

**Advanced:** Set `UDOS_ROOT` environment variable before running uDOS to override auto-detection.

---
```

- [ ] Save file
- [ ] ✅ **TASK 5 COMPLETE**

---

### Task 6: Create Test Suite (30 min)
**File:** `memory/tests/test_udos_root.py` (NEW FILE)

- [ ] Create new file: `memory/tests/test_udos_root.py`
- [ ] Copy entire test code:

```python
#!/usr/bin/env python3
"""Test UDOS_ROOT environment variable propagation."""

import os
import subprocess
import sys
from pathlib import Path

def test_env_var_set():
    """Test that UDOS_ROOT is set in current process."""
    udos_root = os.getenv("UDOS_ROOT")
    assert udos_root is not None, "UDOS_ROOT not set in environment"
    assert Path(udos_root).exists(), f"UDOS_ROOT path does not exist: {udos_root}"
    print(f"✓ UDOS_ROOT is set: {udos_root}")

def test_get_repo_root():
    """Test that get_repo_root() respects UDOS_ROOT."""
    from core.services.logging_service import get_repo_root
    
    repo_root = get_repo_root()
    udos_root = os.getenv("UDOS_ROOT")
    
    assert str(repo_root) == udos_root, \
        f"Mismatch: get_repo_root()={repo_root} vs UDOS_ROOT={udos_root}"
    print(f"✓ get_repo_root() returns UDOS_ROOT: {repo_root}")

def test_subprocess_inheritance():
    """Test that subprocesses inherit UDOS_ROOT."""
    from core.services.unified_logging import get_subprocess_environment
    
    env = get_subprocess_environment()
    assert "UDOS_ROOT" in env, "UDOS_ROOT not in subprocess environment"
    
    # Test actual subprocess
    result = subprocess.run(
        [sys.executable, "-c", "import os; print(os.getenv('UDOS_ROOT'))"],
        env=env,
        capture_output=True,
        text=True
    )
    
    assert result.returncode == 0, f"Subprocess failed: {result.stderr}"
    assert result.stdout.strip() == env["UDOS_ROOT"], \
        f"Subprocess UDOS_ROOT mismatch: {result.stdout.strip()} vs {env['UDOS_ROOT']}"
    print(f"✓ Subprocess inherited UDOS_ROOT: {result.stdout.strip()}")

if __name__ == "__main__":
    try:
        test_env_var_set()
        test_get_repo_root()
        test_subprocess_inheritance()
        print("\n✅ All UDOS_ROOT tests passed!")
    except AssertionError as e:
        print(f"\n❌ Test failed: {e}")
        sys.exit(1)
```

- [ ] Save file
- [ ] Verify file created: `ls -la memory/tests/test_udos_root.py`
- [ ] ✅ **TASK 6 COMPLETE**

---

## Testing & Validation (30 min)

### Test 1: Local Setup
```bash
# Run this in terminal from ~/uDOS

# 1. Verify .env.example was updated
grep UDOS_ROOT .env.example
# Expected: UDOS_ROOT=/Users/fredbook/Code/uDOS

# 2. Verify setup_handler.py has no syntax errors
python -m py_compile core/commands/setup_handler.py
# Expected: No output (success)

# 3. Verify logging_service.py has no syntax errors
python -m py_compile core/services/logging_service.py
# Expected: No output (success)
```

- [ ] All 3 syntax checks passed

### Test 2: Run Test Suite
```bash
# Run new UDOS_ROOT tests
python -m pytest memory/tests/test_udos_root.py -v

# Expected output:
# test_env_var_set PASSED
# test_get_repo_root PASSED
# test_subprocess_inheritance PASSED
# ✅ All tests passed
```

- [ ] All tests passed

### Test 3: Run Setup Interactively
```bash
# Run setup and check UDOS_ROOT detection
python -m core.commands.setup --interactive

# Follow prompts, should see:
# ✅ UDOS_ROOT auto-detected: /Users/fredbook/Code/uDOS

# After setup completes, verify .env was created:
cat .env | grep UDOS_ROOT
# Expected: UDOS_ROOT=/Users/fredbook/Code/uDOS
```

- [ ] UDOS_ROOT detected and saved to .env

### Test 4: Start Wizard Server
```bash
# Start Wizard (in separate terminal)
python -m wizard.web.app

# In first terminal, check logs for UDOS_ROOT validation
tail -f memory/logs/*.log | grep UDOS_ROOT

# Expected to see:
# [WIZ] Using UDOS_ROOT=/Users/fredbook/Code/uDOS
```

- [ ] Wizard server started successfully

---

## Validation Checklist (30 min)

Before marking Phase 1 complete, verify:

- [ ] `.env.example` has UDOS_ROOT field
- [ ] `setup_handler.py` detects and saves UDOS_ROOT
- [ ] `get_repo_root()` validates UDOS_ROOT env var
- [ ] `get_subprocess_environment()` exports UDOS_ROOT
- [ ] TUI setup story shows UDOS_ROOT detection
- [ ] `test_udos_root.py` passes all tests
- [ ] Wizard server starts with UDOS_ROOT log
- [ ] No errors in test suite: `pytest memory/ tests/ -v`
- [ ] Documentation links work

---

## If Something Goes Wrong

### Syntax Error in Python File
```bash
# Check syntax
python -m py_compile <file.py>

# See detailed error
python <file.py>
```

### UDOS_ROOT Not Detected
```bash
# Verify uDOS.py exists
ls -la ~/uDOS/uDOS.py

# Verify UDOS_ROOT can be detected
python -c "from pathlib import Path; print(Path(__file__).parent.parent.parent / 'uDOS.py')"
```

### Tests Failing
```bash
# Run with verbose output
python -m pytest memory/tests/test_udos_root.py -vv -s

# Check imports
python -c "from core.services.logging_service import get_repo_root; print(get_repo_root())"
```

---

## Rollback (If Needed)

If issues occur and you need to rollback:

1. **Revert .env.example:**
   ```bash
   git checkout .env.example
   ```

2. **Revert setup_handler.py:**
   ```bash
   git checkout core/commands/setup_handler.py
   ```

3. **Revert logging_service.py:**
   ```bash
   git checkout core/services/logging_service.py
   ```

4. **Revert unified_logging.py:**
   ```bash
   git checkout core/services/unified_logging.py
   ```

5. **Revert setup-story.md:**
   ```bash
   git checkout core/tui/setup-story.md
   ```

6. **Remove test file:**
   ```bash
   rm memory/tests/test_udos_root.py
   ```

7. **Clear .env:**
   ```bash
   rm .env
   ```

---

## Success Indicators

✅ **Phase 1 Complete When:**

1. All .py files have valid syntax
2. All tests pass: `pytest memory/ tests/`
3. SETUP creates .env with UDOS_ROOT
4. Wizard logs show UDOS_ROOT validation
5. No errors in test suite
6. `get_repo_root()` returns UDOS_ROOT from env var

---

## Next Steps (After Phase 1)

Once Phase 1 is complete:

1. **Commit changes:**
   ```bash
   git add .
   git commit -m "Phase 1: Add UDOS_ROOT environment variable support"
   ```

2. **Create PR:** Push to branch and create pull request

3. **Review:** Get code review approval

4. **Merge:** Merge to main

5. **Plan Phase 2:** Begin Docker container hardening (next week)

---

## Documentation References

- **Full Implementation Guide:** `docs/PHASE1-UDOS-ROOT-IMPLEMENTATION.md`
- **Architecture Decision:** `docs/decisions/ADR-006-UDOS-ROOT-ENVIRONMENT-VARIABLE.md`
- **Assessment Results:** `docs/CONTAINERIZATION-READINESS-ASSESSMENT.md`
- **Overall Strategy:** `docs/CONTAINERIZATION-STRATEGY.md`

---

## Questions?

If you get stuck:

1. **Check test output** for specific error messages
2. **Review implementation guide** for code examples
3. **Read ADR-006** for architectural context
4. **Check AGENTS.md** for system boundaries

---

_Phase 1 Quick-Start Checklist_  
_Ready for Execution_  
_Estimated Duration: 4 hours_
