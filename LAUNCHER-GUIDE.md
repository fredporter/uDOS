# uDOS Launcher Architecture Guide

**Version:** v1.0.0
**Status:** Unified System Complete
**Last Updated:** 2026-01-24

---

## Architecture Overview

All 14 uDOS launchers use a **unified dispatcher system** in `bin/udos-common.sh`. This eliminates 91% code duplication and makes maintenance trivial.

### Master Entry Point

Every launcher delegates to `launch_component()` in `bin/udos-common.sh`:

```bash
#!/bin/bash
set -e
SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
UDOS_ROOT="$(dirname "$SCRIPT_DIR")"
source "$SCRIPT_DIR/udos-common.sh"  # Load unified library
launch_component "component_name" "mode" "$@"
```

**All launchers follow this identical 8-10 line pattern.**

---

## Available Launchers

### Core Components

| Launcher          | Location                           | Type  | Purpose                           |
| ----------------- | ---------------------------------- | ----- | --------------------------------- |
| **Core TUI**      | `bin/start_udos.sh`                | CLI   | Offline-first command interface   |
| **Core TUI**      | `bin/Launch-uDOS-TUI.command`      | macOS | Double-click launcher             |
| **Wizard Server** | `bin/start-wizard-server.sh`       | CLI   | Production API server (port 8765) |
| **Wizard Server** | `bin/Launch-Wizard-Server.command` | macOS | Double-click launcher             |

### Development/Experimental

| Launcher       | Location                               | Type  | Purpose                             |
| -------------- | -------------------------------------- | ----- | ----------------------------------- |
| **Wizard TUI** | `bin/start-wizard-tui.sh`              | CLI   | Wizard text interface               |
| **App Dev**    | `app/bin/start-app-dev.sh`             | CLI   | Tauri app dev mode                  |
| **App Dev**    | `app/bin/Launch uMarkdown-dev.command` | macOS | Double-click launcher               |
| **Goblin Dev** | `dev/bin/start-goblin-dev.sh`          | CLI   | Experimental dev server (port 8767) |
| **Goblin Dev** | `dev/bin/Launch-Goblin-Dev.command`    | macOS | Double-click launcher               |
| **Empire Dev** | `dev/bin/start-empire-dev.sh`          | CLI   | CRM dev server                      |
| **Empire Dev** | `dev/bin/Launch-Empire-Server.command` | macOS | Double-click launcher               |

---

## Unified Launcher System

### What Happens When You Run a Launcher

Every launcher execution follows this flow:

```
User (CLI / Finder)
    ↓
Launcher Script (8-10 lines)
    ├─ cd to UDOS_ROOT
    └─ source bin/udos-common.sh
        ↓
    launch_component() dispatcher
        ├─ _setup_component_environment()
        │  ├─ Activate venv (.venv/bin/activate)
        │  ├─ Check Python deps
        │  ├─ Run self-healing (git, repair)
        │  └─ Detect port conflicts
        └─ Component-specific launcher
           ├─ launch_core_tui()          → python uDOS.py
           ├─ launch_wizard_server()     → python -m wizard.server
           ├─ launch_wizard_tui()        → wizard TUI mode
           ├─ launch_app_dev()           → npm run tauri:dev
           ├─ launch_goblin_dev()        → python dev/goblin/dev_server.py
           └─ launch_empire_dev()        → python dev/empire/server.py
```

### Shared Features (Automatic in All Launchers)

Every launcher gets these features automatically:

✅ **Environment Setup**

- Locate `.venv` and activate it
- Install missing Python packages
- Validate npm (if needed)

✅ **Self-Healing Diagnostics**

- Check Python version compatibility
- Git repo validation
- Submodule sync (dev folder)
- Auto-upgrade dependencies

✅ **Port Management**

- Auto-detect port conflicts
- Find next available port
- Update config files automatically
- Fall back to alternative modes

✅ **UI Polish**

- Consistent color codes (red, green, yellow, blue)
- Spinning progress indicator
- Clear status messages
- Error recovery suggestions

---

## Component-Specific Launchers

### launch_core_tui()

```bash
# In bin/udos-common.sh
launch_core_tui() {
    log_info "Starting uDOS Core TUI..."
    cd "$UDOS_ROOT"
    python uDOS.py "$@"
}
```

**Starter Script:**

```bash
# bin/start-core-tui.sh
#!/bin/bash
set -e
SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
UDOS_ROOT="$(dirname "$SCRIPT_DIR")"
source "$SCRIPT_DIR/udos-common.sh"
launch_component "core" "tui" "$@"
```

---

### launch_wizard_server()

```bash
# In bin/udos-common.sh
launch_wizard_server() {
    log_info "Starting Wizard Server..."
    cd "$UDOS_ROOT"
    # Auto-build Svelte dashboard if npm available
    [[ -f wizard/dashboard/package.json ]] && npm --prefix wizard/dashboard install
    python -m wizard.server --port "$WIZARD_PORT"
}
```

**Starter Script:**

```bash
# bin/start-wizard-server.sh
#!/bin/bash
set -e
SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
UDOS_ROOT="$(dirname "$SCRIPT_DIR")"
source "$SCRIPT_DIR/udos-common.sh"
launch_component "wizard" "server" "$@"
```

---

### launch_app_dev()

```bash
# In bin/udos-common.sh
launch_app_dev() {
    log_info "Starting Tauri App Dev..."
    cd "$UDOS_ROOT/app"
    npm install --legacy-peer-deps 2>/dev/null || true
    npm run tauri:dev
}
```

---

### launch_goblin_dev()

```bash
# In bin/udos-common.sh
launch_goblin_dev() {
    log_info "Starting Goblin Dev Server..."
    cd "$UDOS_ROOT/dev/goblin"
    python dev_server.py --port 8767
}
```

---

## Creating New Launchers

### For a New Component

1. **Create starter script** in `component/bin/start-component.sh`:

   ```bash
   #!/bin/bash
   set -e
   SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
   UDOS_ROOT="$(cd "$SCRIPT_DIR/../../.." && pwd)"  # Adjust path as needed
   source "$UDOS_ROOT/bin/udos-common.sh"
   launch_component "component_name" "mode" "$@"
   ```

2. **Add launcher function** to `bin/udos-common.sh`:

   ```bash
   launch_my_component() {
       log_info "Starting My Component..."
       cd "$UDOS_ROOT/my-component"
       python server.py --port $PORT
   }
   ```

3. **Register in launch_component()** dispatcher:

   ```bash
   launch_component() {
       local component="$1"
       local mode="$2"
       _setup_component_environment "$component"

       case "$component" in
           my-component) launch_my_component "$@" ;;
           # ... other cases
       esac
   }
   ```

4. **Create .command file** for macOS (optional):
   ```bash
   # component/bin/Launch-My-Component.command
   #!/bin/bash
   set -e
   SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
   UDOS_ROOT="$(cd "$SCRIPT_DIR/../../.." && pwd)"
   source "$UDOS_ROOT/bin/udos-common.sh"
   launch_component "component_name" "mode" "$@"
   ```

---

## Code Reduction Metrics

### Before Unification (Phase 0)

| Launcher Type  | Count  | Total Lines | Avg Lines/File |
| -------------- | ------ | ----------- | -------------- |
| .command files | 6      | 600         | 100            |
| .sh files      | 8      | 1,000       | 125            |
| **Total**      | **14** | **1,600**   | **114**        |

### After Unification (Phase 4)

| Component          | Count  | Total Lines | Pattern         |
| ------------------ | ------ | ----------- | --------------- |
| bin/udos-common.sh | 1      | 561         | Unified library |
| .command files     | 6      | 53          | 8-10 lines each |
| .sh files          | 7      | 45          | 9 lines each    |
| **Total**          | **14** | **659**     | **47 avg**      |

### Code Reduction

- **Global:** 1,600 → 659 lines (-59%)
- **.command files:** 600 → 53 lines (-91%)
- **.sh files:** 1,000 → 45 lines (-95%)
- **Duplication:** 60% → 3% eliminated
- **Maintenance burden:** 6-10x reduction

---

## Wizard Production Server (Port 8765)

**Status:** PRODUCTION v1.1.0.0 (stable, frozen)

**Services:**

- AI Gateway (Ollama local-first, optional cloud burst)
- Device Authentication + Sessions
- Plugin Repository & Distribution
- Notion Sync (Webhooks + Queue)
- Task Scheduler (Organic cron)
- Binder Compiler (PDF/JSON/Markdown)
- GitHub Integration (Monitor + Sync)
- WebSocket support

**Endpoints:**

- Web Dashboard: `http://localhost:8765`
- REST API: `http://localhost:8765/api/v1/*`
- API Docs: `http://localhost:8765/docs`
- ReDoc: `http://localhost:8765/redoc`

**Configuration:** `wizard/config/wizard.json` (committed, versioned)

---

## Boot Sequence & Output

```text

╔═══════════════════════════════════════════════════════════════╗
║ 🧙 Wizard Server v1.1.0.0 ║
║ Production • Always-On • Frozen API ║
╚═══════════════════════════════════════════════════════════════╝

[BOOT] Checking environment...
[BOOT] uDOS Root: ~/uDOS
[BOOT] Python: Python 3.9.6
[BOOT] Features: AI Gateway, Plugin Repository, Device Auth, GitHub Integration

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
🧙 Wizard Server v1.1.0.0
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
[✓] Virtual environment activated
[✓] Dependencies installed and ready
[BOOT] Starting Wizard Server on port 8765...

```

---

---

## Development Workflow

### Typical Development Stack

```bash
# Terminal 1: Core TUI (primary interface)
./bin/start_udos.sh

# Terminal 2: Wizard Server (background service)
./bin/start-wizard-server.sh &

# Terminal 3: Optional App Development
cd app && npm run tauri:dev
```

### macOS Workflow

```bash
# Double-click launchers in Finder
open bin/Launch-uDOS-TUI.command
open bin/Launch-Wizard-Server.command
open app/bin/Launch\ uMarkdown-dev.command
```

---

## File Structure

```text
/bin/
├── udos-common.sh                 # Unified launcher library (561 lines)
├── start_udos.sh                  # Core TUI launcher (9 lines)
├── start-core-tui.sh              # Alternative Core entry (9 lines)
├── start-wizard-server.sh         # Wizard launcher (9 lines)
├── start-wizard-tui.sh            # Wizard TUI (9 lines)
├── start-app-dev.sh               # App dev launcher (9 lines)
├── Launch-uDOS-TUI.command        # macOS Finder: Core (8 lines)
├── Launch-uDOS-Dev.command        # macOS Finder: Dev mode (9 lines)
├── Launch-Wizard-Server.command   # macOS Finder: Wizard (9 lines)
└── launcher.template.command      # Template for new launchers (16 lines)

/dev/bin/
├── start-goblin-dev.sh            # Goblin dev server (10 lines)
├── start-empire-dev.sh            # Empire dev server (10 lines)
├── Launch-Goblin-Dev.command      # macOS Finder: Goblin (9 lines)
└── Launch-Empire-Server.command   # macOS Finder: Empire (8 lines)

/app/bin/
├── start-app-dev.sh               # Tauri app dev (9 lines)
└── Launch\ uMarkdown-dev.command  # macOS Finder: App (9 lines)
```

---

## Key Principles

1. **Single Source of Truth:** All launcher logic lives in `bin/udos-common.sh`
2. **Minimal Starters:** Launcher scripts are just 8-10 line shells
3. **Automatic Everything:** Environment setup, deps, self-healing, port detection
4. **Consistent UX:** Same color codes, spinners, error messages everywhere
5. **Easy Extension:** Adding a new launcher = 1 function + 1 starter script
6. **Zero Duplication:** 60% → 3% (eliminated 1,000+ lines of redundant code)

---

## Component Versions

```bash
# Check all component versions
python -m core.version check

# View version dashboard
python -m core.version show

# Bump a component version
python -m core.version bump wizard patch
```

| Component | Version  | Status             |
| --------- | -------- | ------------------ |
| Core      | v1.1.1.1 | Development        |
| Wizard    | v1.1.0.2 | Production (Alpha) |
| API       | v1.0.1.0 | Alpha              |
| App       | v1.0.6.1 | Alpha              |
| Transport | v1.0.1.0 | Alpha              |
| Goblin    | v0.2.0.0 | Experimental       |

---

## References

- [INSTALLATION.md](INSTALLATION.md) — Setup and installation
- [QUICKSTART.md](QUICKSTART.md) — First-time launch guide
- [bin/udos-common.sh](bin/udos-common.sh) — Unified launcher library (source)
- [wizard/README.md](wizard/README.md) — Wizard Server documentation
- [core/README.md](core/README.md) — Core TUI documentation
- [AGENTS.md](AGENTS.md) — Development rules and architecture

---

**Status:** ✅ Unified Launcher System Complete
**Last Updated:** 2026-01-24
**Total Code Reduction:** 1,600 → 659 lines (-59%)
**Maintenance Burden:** 6-10x reduction
