# Phase 1: UDOS_ROOT Bootstrap Implementation
**Immediate Action Plan for Round 2**  
**Timeline:** 4 hours  
**Status:** Ready to execute

---

## Overview

This document provides a step-by-step implementation plan to add `UDOS_ROOT` environment variable support to uDOS, enabling containerization while maintaining local development compatibility.

**Outcome:** All uDOS processes will have access to `$UDOS_ROOT` environment variable pointing to the repository root, making the system container-ready.

---

## Task 1: Update `.env.example` (15 min)

### File: `.env.example`

Add new section after existing fields:

```bash
# System Root Path (auto-detected at setup, containerization support)
# Points to the uDOS repository root directory
# Used by Wizard, Core, and plugins to locate shared resources
UDOS_ROOT=/Users/fredbook/Code/uDOS
```

**Why:** Users and containers need this field in their .env file.

---

## Task 2: Implement UDOS_ROOT Discovery (1 hour)

### File: `core/commands/setup_handler.py`

Add this function near the top of the file (after imports):

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

### Update the setup handler's main save logic:

Find this section in `setup_handler.py` where .env is written and add UDOS_ROOT detection:

```python
def handle_setup_interactive(tui_instance=None, initial_story=None):
    """Run setup story and save to .env"""
    # ... existing code ...
    
    # Auto-detect and save UDOS_ROOT
    try:
        udos_root = _detect_udos_root()
        story_vars["UDOS_ROOT"] = str(udos_root)
        logger.info(f"[LOCAL] UDOS_ROOT will be saved: {udos_root}")
    except RuntimeError as e:
        logger.warning(f"[LOCAL] UDOS_ROOT detection failed: {e}")
        # Optionally prompt user here
    
    # ... rest of existing code ...
```

---

## Task 3: Harden get_repo_root() (1 hour)

### File: `core/services/logging_service.py`

Update the `get_repo_root()` function (lines 57-65) to this more robust version:

**Old Code:**
```python
def get_repo_root() -> Path:
    """Get repository root from current file location or UDOS_ROOT."""
    env_root = os.getenv("UDOS_ROOT")
    if env_root:
        env_path = Path(env_root).expanduser()
        if (env_path / "uDOS.py").exists():
            return _enforce_home_root(env_path)
    current = Path(__file__).resolve()
    return _enforce_home_root(current.parent.parent.parent)
```

**New Code:**
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

---

## Task 4: Export UDOS_ROOT to Subprocesses (1 hour)

### File: `core/services/unified_logging.py`

Add this helper function in the services module (or add to logging_service.py):

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
            from core.services.logging_service import get_repo_root
            env["UDOS_ROOT"] = str(get_repo_root())
        except Exception as e:
            logger.warning(f"[LOCAL] Could not set UDOS_ROOT for subprocess: {e}")
    
    return env
```

### Update subprocess calls throughout codebase:

Find instances of `subprocess.run()` or similar calls and update them:

**Old Pattern:**
```python
result = subprocess.run(["python", "script.py"], cwd=some_path)
```

**New Pattern:**
```python
result = subprocess.run(
    ["python", "script.py"],
    cwd=some_path,
    env=get_subprocess_environment()  # Pass UDOS_ROOT
)
```

**Files to check for subprocess calls:**
- `core/services/system_script_runner.py`
- `core/services/hot_reload.py`
- `extensions/api/services/executor.py`
- `wizard/services/*`

---

## Task 5: Update TUI Setup Story (30 min)

### File: `core/tui/setup-story.md`

Add new section after the "Identity" section:

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

---

## Task 6: Testing & Validation (1 hour)

### Test 1: Local Setup (.env creation)

```bash
# Run setup interactively
cd ~/uDOS
python -m core.commands.setup --interactive

# Verify .env was created
cat .env | grep UDOS_ROOT

# Expected output:
# UDOS_ROOT=/Users/fredbook/Code/uDOS
```

### Test 2: Environment Variable Propagation

Create test file: `memory/tests/test_udos_root.py`

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

### Test 3: Wizard Server Startup

```bash
# Start wizard server
cd ~/uDOS
python -m wizard.web.app

# In another terminal, check logs
tail -f memory/logs/*.log | grep UDOS_ROOT

# Should see:
# [WIZ] Using UDOS_ROOT=/Users/fredbook/Code/uDOS
```

### Test 4: Container Simulation

```bash
# Simulate container by unsetting UDOS_ROOT and setting it again
unset UDOS_ROOT
export UDOS_ROOT=/tmp/test-udos-root

# Create marker file
mkdir -p /tmp/test-udos-root
touch /tmp/test-udos-root/uDOS.py

# Test that get_repo_root() uses env var
cd ~/uDOS
python -c "from core.services.logging_service import get_repo_root; print(get_repo_root())"

# Expected output:
# /tmp/test-udos-root
```

---

## Task 7: Documentation Updates (30 min)

### Update `docs/AGENTS.md` containerization section

Add to "Critical Rules" section:

```markdown
7. **UDOS_ROOT Environment** — All processes use $UDOS_ROOT
   - Local: Auto-detected at setup, saved to .env
   - Container: Set by Docker/Kubernetes at runtime
   - Subprocesses: Inherited from parent process environment
```

### Create `docs/ENV-VARIABLES.md` (NEW)

```markdown
# Environment Variables Reference

## System Paths

### UDOS_ROOT (Required)
- **Purpose:** Repository root directory
- **Set by:** setup-story.md (auto-detected)
- **Used by:** All services, plugins, Wizard
- **Container:** Set by Docker volume mount + startup
- **Example:** `UDOS_ROOT=/Users/fredbook/Code/uDOS`

## Service Variables

### Wizard Server
- `WIZARD_PORT` (default: 8765)
- `WIZARD_KEY` (secret key for admin operations)
- `WIZARD_ENV` (development/production)

### Core TUI
- `UDOS_ROOT` (required)
- `CORE_LOG_LEVEL` (debug/info/warning)

## See Also
- `.env.example` — Template with all fields
- `docs/CONTAINERIZATION-READINESS-ASSESSMENT.md` — Container setup
```

---

## Implementation Sequence

Execute in this order:

1. ✅ **Update `.env.example`** (5 min)
2. ✅ **Add UDOS_ROOT detection to setup_handler.py** (30 min)
3. ✅ **Harden get_repo_root()** (30 min)
4. ✅ **Export UDOS_ROOT to subprocesses** (30 min)
5. ✅ **Update TUI setup story** (15 min)
6. ✅ **Create test suite** (30 min)
7. ✅ **Run all tests** (30 min)
8. ✅ **Update documentation** (30 min)

**Total Time:** ~3.5 hours (with 30 min buffer = 4 hours)

---

## Validation Checklist

Before merging, verify:

- [ ] `.env.example` has UDOS_ROOT field
- [ ] `setup_handler.py` detects and saves UDOS_ROOT
- [ ] `get_repo_root()` validates UDOS_ROOT env var first
- [ ] `get_subprocess_environment()` exports UDOS_ROOT
- [ ] TUI setup story shows UDOS_ROOT detection
- [ ] `test_udos_root.py` passes all tests
- [ ] Wizard server starts with UDOS_ROOT log message
- [ ] Container simulation test passes
- [ ] Documentation is updated
- [ ] No regression in existing tests

---

## Rollback Plan

If issues occur:

1. Revert changes to `.env.example`
2. Revert changes to `setup_handler.py`
3. Revert changes to `logging_service.py` (restore original `get_repo_root()`)
4. Revert changes to `unified_logging.py`
5. Clear `.env` files and re-run setup with old code

---

## Next Phase (Week 2)

Once Phase 1 is complete and tested:
1. Create Dockerfile for core and wizard
2. Create docker-compose.yml with UDOS_ROOT mounts
3. Test Wizard in container with plugin loading
4. Document container setup in DOCKER-SETUP.md

---

_Implementation Plan Ready_  
_Estimated Duration: 4 hours_  
_Status: Ready to execute_
