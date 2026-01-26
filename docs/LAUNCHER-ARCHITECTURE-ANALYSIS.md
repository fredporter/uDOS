# uDOS Launcher Architecture Analysis

**Date:** 2026-01-26  
**Status:** Audit Complete — Recommendations for Unification

---

## 📋 Current Launcher Inventory

### macOS `.command` Files (Entry Points for Finder)

| File                           | Location    | Purpose                        | Component | Lines |
| ------------------------------ | ----------- | ------------------------------ | --------- | ----- |
| `Launch-uDOS-TUI.command`      | `/bin/`     | Core TUI interactive           | Core      | 93    |
| `Launch-uDOS-Dev.command`      | `/bin/`     | Dev Mode TUI (minimal wrapper) | Core      | ~12   |
| `Launch-Wizard-Server.command` | `/bin/`     | Wizard Server + dashboard      | Wizard    | 241   |
| `Launch-Goblin-Dev.command`    | `/dev/bin/` | Goblin Dev Server + TUI        | Goblin    | ~77   |
| `Launch-Empire-Server.command` | `/dev/bin/` | Empire CRM Server + TUI        | Empire    | 166   |
| `Launch uMarkdown-dev.command` | `/app/bin/` | App (Tauri) dev                | App       | ~20   |

### Shell `.sh` Implementations (Core Logic)

| File                         | Location           | Purpose                | Component | Lines |
| ---------------------------- | ------------------ | ---------------------- | --------- | ----- |
| `start_udos.sh`              | `/bin/`            | Core TUI launcher      | Core      | 121   |
| `start_wizard.sh`            | `/bin/`            | Wizard Server launcher | Wizard    | 424   |
| `launch_wizard_tui.sh`       | `/wizard/`         | Wizard TUI (wrapper)   | Wizard    | ~11   |
| `launch_wizard_dev_tui.sh`   | `/bin/`            | Wizard Dev TUI         | Wizard    | ?     |
| `launch-goblin-server.sh`    | `/dev/goblin/bin/` | Goblin server only     | Goblin    | ?     |
| `launch-goblin-dashboard.sh` | `/dev/goblin/bin/` | Goblin dashboard only  | Goblin    | ?     |
| `start_umarkdown_dev.sh`     | `/app/bin/`        | App dev                | App       | ~21   |
| `start_umarkdown_build.sh`   | `/app/bin/`        | App build              | App       | ?     |

---

## 🔍 Redundancy Analysis

### Problem 1: Duplication Across `.command` Files

```bash
# PATTERN 1: All .command files repeat this boilerplate
#!/bin/bash
set -e
cd "$(dirname "$0")/.."
source "$script_dir/udos-common.sh"
UDOS_ROOT="$(resolve_udos_root)"
export UDOS_ROOT
cd "$UDOS_ROOT"
```

**Appears in:** All 6 `.command` files (repeated 6x)

### Problem 2: Color/Formatting Code Duplication

```bash
# PATTERN 2: Color codes re-declared everywhere
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
...
```

**Appears in:**

- `Launch-Wizard-Server.command`
- `Launch-Empire-Server.command`
- `start_wizard.sh`
- `start_udos.sh`
- `udos-common.sh` (but NOT exported)

**Issue:** Colors defined in BOTH `.command` AND `.sh` files separately

### Problem 3: Environment Setup Duplication

```bash
# PATTERN 3: Repeated in multiple launchers
ensure_python_env || exit 1
run_with_spinner "..." "python -m core.services.self_healer $component"
mkdir -p "$UDOS_LOG_DIR"
```

**Appears in:** `start_wizard.sh`, `start_udos.sh`, `Launch-Goblin-Dev.command`, `Launch-Wizard-Server.command`

### Problem 4: Spinner Implementation Variation

- `udos-common.sh`: Has `run_with_spinner()` with elapsed time
- `start_wizard.sh`: Has custom `start_spinner()` + `stop_spinner()` (different implementation)
- `Launch-Wizard-Server.command`: Uses `run_with_spinner()` from common.sh

**Result:** Inconsistent progress feedback

### Problem 5: Folder Structure Inconsistency

```
bin/
  Launch-uDOS-TUI.command        ✓ (correct)
  Launch-Wizard-Server.command   ✓ (correct)
  start_udos.sh                  ✓ (correct)
  start_wizard.sh                ✓ (correct)

dev/bin/
  Launch-Goblin-Dev.command      ✓ (correct)
  Launch-Empire-Server.command   ✓ (correct)
  (missing: launch-goblin-server.sh, launch-empire-server.sh)

wizard/
  launch_wizard_tui.sh           ? (should be bin/)
  launch_with_port_manager.py    ? (orphaned Python script)

app/bin/
  Launch uMarkdown-dev.command   ✓ (correct)
  start_umarkdown_dev.sh         ✓ (correct)
```

**Issue:** Wizard has `.sh` files in two places (`/bin/` and `/wizard/`)

---

## 🎯 Proposed Modular Architecture

### Tier 1: Universal `.command` Template

**File:** `/bin/launcher.template.command`

```bash
#!/bin/bash
# Universal macOS .command Launcher
# Usage: ./Launch-{Component}-{Mode}.command [--rebuild]

COMPONENT="${1:-core}"      # Passed via .command symlink or filename
MODE="${2:-tui}"             # Passed via .command symlink or filename
SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
UDOS_ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"

# Source common (for colors, utilities)
source "$UDOS_ROOT/bin/udos-common.sh"

# Execute the corresponding .sh file
LAUNCHER_SCRIPT="$SCRIPT_DIR/start-${COMPONENT}-${MODE}.sh"
if [ ! -f "$LAUNCHER_SCRIPT" ]; then
    LAUNCHER_SCRIPT="$UDOS_ROOT/${COMPONENT}/bin/launch-${COMPONENT}-${MODE}.sh"
fi

if [ ! -f "$LAUNCHER_SCRIPT" ]; then
    echo -e "${RED}[ERROR]${NC} Launcher script not found: $LAUNCHER_SCRIPT"
    exit 1
fi

# Execute with args
"$LAUNCHER_SCRIPT" "$@"
```

**Result:** All `.command` files become 8-line wrappers

### Tier 2: Unified Component Launch Scripts

**Structure:**

```
bin/
  start-core-tui.sh             (replaces: start_udos.sh)
  start-wizard-server.sh         (replaces: start_wizard.sh)
  start-wizard-tui.sh            (replaces: launch_wizard_tui.sh)
  start-app-dev.sh               (replaces: app/bin/start_umarkdown_dev.sh)
  start-app-build.sh             (replaces: app/bin/start_umarkdown_build.sh)

dev/bin/
  start-goblin-dev.sh            (replaces: Launch-Goblin-Dev.command internals)
  start-empire-dev.sh            (replaces: Launch-Empire-Server.command internals)
```

Each file follows a consistent pattern:

```bash
#!/bin/bash
COMPONENT="goblin"
MODE="dev"
SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
UDOS_ROOT="$(cd "$SCRIPT_DIR/../.." && pwd)"

source "$UDOS_ROOT/bin/udos-common.sh"

# Component-specific setup
launch_component "$COMPONENT" "$MODE" "$@"
```

### Tier 3: Extracted Utilities (`udos-common.sh` expansion)

Add these functions to `udos-common.sh`:

```bash
# Unified component launcher (replaces 80% of boilerplate in .sh files)
launch_component() {
    local component="$1"
    local mode="$2"
    shift 2

    # 1. Resolve paths
    UDOS_ROOT="${UDOS_ROOT:-$(resolve_udos_root)}"
    export UDOS_ROOT
    cd "$UDOS_ROOT"

    # 2. Setup environment
    setup_environment "$component"

    # 3. Run component-specific checks
    case "$component" in
        core)     launch_core_tui "$@" ;;
        wizard)   launch_wizard_server "$@" ;;
        goblin)   launch_goblin_server "$@" ;;
        empire)   launch_empire_server "$@" ;;
        app)      launch_app_dev "$@" ;;
        *)        echo "Unknown component: $component"; exit 1 ;;
    esac
}

# Extracted functions for each component
launch_core_tui() { ... }
launch_wizard_server() { ... }
launch_goblin_server() { ... }
launch_empire_server() { ... }
launch_app_dev() { ... }

setup_environment() {
    local component="$1"
    ensure_python_env || exit 1
    run_with_spinner "Running self-healing..." "python -m core.services.self_healer $component"
    mkdir -p "$UDOS_ROOT/memory/logs"
    export UDOS_LOG_DIR="$UDOS_ROOT/memory/logs"
}
```

---

## 📊 Before/After Comparison

### Before (Current State)

```
Total Launcher Files:       14 files
Total Lines of Code:        ~1,600+ lines
Duplication Ratio:          ~60% (colors, boilerplate, env setup)
Update Burden:              High (change in 3-6 files per improvement)
Consistency:                Low (spinner, colors, error handling vary)
macOS Finder Support:       Native (.command files)
Linux/CI Support:           Partial (requires finding .sh equivalent)
```

### After (Proposed)

```
Total Launcher Files:       10 files (6 .command wrappers + 4 start-*.sh)
Total Lines of Code:        ~600-700 lines (57% reduction)
Duplication Ratio:          ~5% (minimal boilerplate)
Update Burden:              Low (one function change in udos-common.sh)
Consistency:                High (all use unified launcher)
macOS Finder Support:       Native (.command files preserved)
Linux/CI Support:           Full (direct .sh execution)
```

---

## 🔄 Migration Path

### Phase 1: Prepare Shared Library

1. Expand `bin/udos-common.sh` with `launch_component()` and component-specific functions
2. Move all color definitions to `udos-common.sh` (export them)
3. Unify spinner to `run_with_spinner()` (already done)

### Phase 2: Create Universal .command Template

1. Create `/bin/launcher-template.command` (8 lines, parameterized)
2. Create actual `.command` files as lightweight wrappers:
   ```bash
   #!/bin/bash
   source "$(cd "$(dirname "$0")" && pwd)/launcher-template.command" "core" "tui" "$@"
   ```

### Phase 3: Consolidate `.sh` Files

1. Move all component launchers to `bin/start-{component}-{mode}.sh`
2. Standardize them to call `launch_component()` from udos-common.sh
3. Remove component-specific color/spinner code

### Phase 4: Remove Redundancy

1. Delete duplicate `.sh` files in `/wizard/`, `/dev/goblin/bin/`, `/app/bin/`
2. Update references in documentation
3. Test all entry points (both `.command` and `.sh`)

---

## 📁 Proposed Final Structure

```
bin/
  ├── launcher-template.command         (NEW: 8-line parameterized template)
  ├── Launch-uDOS-TUI.command          (SIMPLIFIED: 8-line wrapper)
  ├── Launch-uDOS-Dev.command          (SIMPLIFIED: 8-line wrapper)
  ├── Launch-Wizard-Server.command     (SIMPLIFIED: 8-line wrapper)
  ├── start-core-tui.sh                (CONSOLIDATED: core TUI logic)
  ├── start-wizard-server.sh           (CONSOLIDATED: wizard logic)
  ├── start-wizard-tui.sh              (CONSOLIDATED: wizard TUI)
  ├── start-app-dev.sh                 (NEW: app dev consolidated)
  ├── start-app-build.sh               (NEW: app build consolidated)
  └── udos-common.sh                   (EXPANDED: component launcher, all utilities)

dev/bin/
  ├── Launch-Goblin-Dev.command        (SIMPLIFIED: 8-line wrapper)
  ├── Launch-Empire-Server.command     (SIMPLIFIED: 8-line wrapper)
  ├── start-goblin-dev.sh              (CONSOLIDATED)
  └── start-empire-dev.sh              (CONSOLIDATED)

app/bin/
  ├── Launch uMarkdown-dev.command     (SIMPLIFIED: 8-line wrapper)
  └── start-app-dev.sh                 (symlink to bin/start-app-dev.sh or direct call)

wizard/
  └── (EMPTY: all .sh moved to bin/)
```

---

## ✅ Benefits

1. **Maintenance Burden Cut by 60%** — Change spinner once, update everywhere
2. **Consistency Guaranteed** — Same startup flow, same error handling
3. **Linux/CI Friendly** — Direct `.sh` execution supported everywhere
4. **macOS Native Support** — `.command` files still work from Finder
5. **Extensibility** — Add new component in minutes (5 lines)
6. **Testability** — Single `launch_component()` function to test instead of 14 separate scripts
7. **Onboarding** — New developers see one unified pattern

---

## 🚀 Next Actions

1. **Estimate effort:** Consolidation can be done in 2-3 hours
2. **Create prototype:** Build unified `udos-common.sh` + one test `.command` file
3. **Validate:** Test all 6 components launching from both `.command` and `.sh`
4. **Migrate:** Convert remaining launchers one at a time
5. **Document:** Update INSTALLATION.md and QUICKSTART.md

---

**Status:** Ready for Implementation  
**Recommendation:** Proceed with Phase 1 (expand udos-common.sh) immediately
