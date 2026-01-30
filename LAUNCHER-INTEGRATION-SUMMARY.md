# Launcher Self-Healing & Logging Integration - Summary

## ✅ Completed Changes

### 1. **Fixed Launcher Crash** (`core/tui/ucode.py`)
- Added missing `_cmd_fkeys()` handler method to prevent `AttributeError` on startup
- Provides F-key help and dispatch functionality
- Integrates with `FKeyHandler` for UI shortcuts

### 2. **Memory/Logs Root Resolution** (`bin/udos-common.sh`)
- Added `resolve_memory_root()` function to detect user memory location:
  - Priority 1: `~/memory` (user convenience link)
  - Priority 2: `~/.udos/memory` (installed location)
  - Priority 3: `<repo>/memory` (development location)
- Added `ensure_home_memory_link()` to safely create `~/memory` symlink
- Exports `UDOS_MEMORY_ROOT` and `UDOS_LOG_DIR` before self-heal runs
- Logs now centralize to **unified location** (default: `<memory_root>/logs/`)

### 3. **Story File Resolution** (`core/commands/story_handler.py`)
- Updated `_resolve_path()` to support fallback loading:
  - Primary: `memory/story/` (user stories)
  - Secondary: `wizard/templates/` (built-in stories)
  - This allows `STORY wizard-setup` to work automatically

### 4. **Story Template Creation** (`memory/story/wizard-setup-story.md`)
- Created canonical wizard-setup story in `memory/story/`
- Proper Markdown structure with multiple sections:
  - User Identity (username, DOB, role)
  - Time & Place (timezone, location)
  - Installation (ID, OS, lifespan)
  - Capabilities & Permissions

### 5. **Installation Integration** (`bin/install.sh`)
- Added symlink creation: `~/memory` → `~/.udos/memory`
- Ensures logs and workspace paths are consistent across installs
- Improves discoverability for users

### 6. **Launcher Integration** (`bin/udos`)
- Now sources `udos-common.sh` for environment setup
- Calls `_setup_component_environment` before Python execution
- Inherits memory/logs setup from unified launcher system

---

## 🔄 Data Flow

```
Launch-uCODE.command (or ./bin/udos)
    ↓
sources bin/udos-common.sh
    ↓
_setup_component_environment():
    ├── ensure_python_env()          # Activate venv + deps
    ├── resolve_memory_root()        # Detect ~/memory or ~/.udos/memory
    ├── ensure_home_memory_link()    # Create ~/memory symlink
    ├── export UDOS_MEMORY_ROOT      # Set for Python
    ├── export UDOS_LOG_DIR          # Set for Python
    └── run self-healing diagnostics (writes to UDOS_LOG_DIR)
    ↓
python uDOS.py
    ↓
logging_manager reads UDOS_LOG_DIR
    ↓
All logs → <memory_root>/logs/ (flat structure with category-YYYY-MM-DD.log)
```

---

## 📁 Memory Directory Structure

```
~/memory/                           (symlink OR direct dir)
├── logs/                           (Unified logging directory)
│   ├── core-YYYY-MM-DD.log         (Core TUI logs)
│   ├── self-healer-YYYY-MM-DD.log  (Self-heal diagnostics)
│   ├── story-YYYY-MM-DD.log        (Story execution)
│   └── ...
├── story/                          (User & built-in stories)
│   └── wizard-setup-story.md       (Setup wizard)
├── sandbox/                        (User workspace)
├── bank/                           (Saved data)
├── knowledge/                      (Knowledge base)
├── wizard/                         (Wizard data)
├── .cache/                         (Temp cache)
└── ...
```

---

## 🧪 Testing Verification

### Story Resolution:
```bash
STORY wizard-setup  # Now works without errors
```

### Logging:
```bash
tail -f ~/memory/logs/core-*.log  # Watch real-time logs
ls -la ~/memory/logs/             # View log files
```

### Self-Healing:
```bash
./bin/Launch-uCODE.command        # Runs diagnostics automatically
./bin/udos-self-heal.sh core      # Manual self-heal
```

---

## 🔍 Key Files Modified

| File | Change | Purpose |
|------|--------|---------|
| `core/tui/ucode.py` | Added `_cmd_fkeys()` | Fix launcher crash |
| `bin/udos-common.sh` | Added memory/logs functions | Unified logging resolution |
| `core/commands/story_handler.py` | Updated path resolution | Fallback to templates |
| `memory/story/wizard-setup-story.md` | Created new file | Built-in setup story |
| `bin/install.sh` | Added symlink creation | ~/memory convenience |
| `bin/udos` | Added common.sh sourcing | Integrated environment |

---

## 📊 Installation Modes

### Development (in-repo):
```bash
./bin/Launch-uCODE.command        # Logs → /Users/fredbook/Code/uDOS/memory/logs/
```

### Installed (user home):
```bash
udos                              # Logs → ~/.udos/memory/logs/ OR ~/memory/logs (if symlink)
```

### Symlink Preference:
If `~/memory` symlink exists → All paths default to `~/memory`
Otherwise → Fall back to `~/.udos/memory` or repo memory

---

## 🛠️ Self-Healing Integration

Self-healer now has proper logging path:

```python
from core.services.logging_manager import get_logging_manager

logger_mgr = get_logging_manager()  # Uses UDOS_LOG_DIR
logger = logger_mgr.get_logger("self-healer")
logger.info("System is healthy")   # → ~/memory/logs/self-healer-2026-01-30.log
```

All diagnostics write to unified log location automatically.

---

## ✨ Benefits

✅ **Unified Logging** — All components write to same location
✅ **Self-Healing** — Diagnostics run automatically on startup
✅ **Cross-Platform** — Works on macOS, Linux, Alpine, Windows
✅ **User-Friendly** — `~/memory` symlink for easy access
✅ **Story Support** — Built-in wizard-setup story with fallback
✅ **Backward Compatible** — Old code still works, new integration optional

---

**Status:** ✅ All Integration Complete
**Date:** 2026-01-30
**Testing:** Manual verification complete
