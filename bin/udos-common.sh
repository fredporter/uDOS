#!/bin/bash
# ╔═══════════════════════════════════════════════════════════════════════════╗
# ║                    uDOS Common Shell Helpers                              ║
# ║              Shared by all launcher scripts                               ║
# ╚═══════════════════════════════════════════════════════════════════════════╝
#
# Source this at the top of any launcher:
#   source "$(dirname "$0")/udos-common.sh"

# ═══════════════════════════════════════════════════════════════════════════
# Colors and Formatting
# ═══════════════════════════════════════════════════════════════════════════
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
CYAN='\033[0;36m'
MAGENTA='\033[0;35m'
WHITE='\033[1;37m'
DIM='\033[2m'
NC='\033[0m'
BOLD='\033[1m'

# Box drawing characters
H_LINE="━"
V_LINE="┃"
TL="┏"
TR="┓"
BL="┗"
BR="┛"

# ═══════════════════════════════════════════════════════════════════════════
# Path Detection (works regardless of where uDOS is installed)
# ═══════════════════════════════════════════════════════════════════════════
UDOS_BIN_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
UDOS_ROOT="$(dirname "$UDOS_BIN_DIR")"
UDOS_HOME_ROOT="${HOME}/uDOS"

_udos_realpath() {
    if command -v realpath >/dev/null 2>&1; then
        realpath "$1"
    else
        python3 - <<'PY' "$1"
import os, sys
print(os.path.realpath(sys.argv[1]))
PY
    fi
}

_udos_find_repo_root() {
    local start="$1"
    while [ -n "$start" ] && [ "$start" != "/" ]; do
        if [ -f "$start/uDOS.py" ]; then
            echo "$start"
            return 0
        fi
        start="$(dirname "$start")"
    done
    return 1
}

_udos_within_home_root() {
    local candidate="$1"
    if [ -d "$UDOS_HOME_ROOT" ]; then
        local resolved
        resolved="$(_udos_realpath "$candidate")"
        case "$resolved" in
            "$UDOS_HOME_ROOT"/*|"$UDOS_HOME_ROOT") return 0 ;;
            *) return 1 ;;
        esac
    fi
    return 0
}

resolve_udos_root() {
    local resolved=""

    if [ -n "$UDOS_ROOT" ] && [ -f "$UDOS_ROOT/uDOS.py" ]; then
        resolved="$UDOS_ROOT"
    else
        local script_dir
        script_dir="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
        resolved="$(_udos_find_repo_root "$script_dir")" || resolved=""
        if [ -z "$resolved" ]; then
            resolved="$(_udos_find_repo_root "$(pwd)")" || resolved=""
        fi
    fi

    if [ -z "$resolved" ]; then
        echo "[udos] Could not locate uDOS repo root (missing uDOS.py). Set UDOS_ROOT or run from inside the repo." >&2
        return 1
    fi

    if ! _udos_within_home_root "$resolved"; then
        echo "[udos] Refusing repo root outside ~/uDOS. Move the repo under ~/uDOS or set UDOS_HOME_ROOT_ALLOW_OUTSIDE=1 to bypass." >&2
        if [ "$UDOS_HOME_ROOT_ALLOW_OUTSIDE" != "1" ]; then
            return 1
        fi
    fi

    echo "$resolved"
}

resolve_memory_root() {
    if [ -n "$UDOS_MEMORY_ROOT" ]; then
        echo "$UDOS_MEMORY_ROOT"
        return 0
    fi

    local home_memory="$HOME/memory"
    local dot_memory="$HOME/.udos/memory"
    local repo_memory="$UDOS_ROOT/memory"

    if [ -d "$home_memory" ] || [ -L "$home_memory" ]; then
        echo "$home_memory"
        return 0
    fi

    if [ -d "$dot_memory" ]; then
        echo "$dot_memory"
        return 0
    fi

    if [ -d "$repo_memory" ]; then
        echo "$repo_memory"
        return 0
    fi

    echo "$repo_memory"
}

ensure_home_memory_link() {
    local target_root="$1"
    local home_memory="$HOME/memory"

    if [ -e "$home_memory" ]; then
        return 0
    fi

    if [ -n "$target_root" ] && [ -d "$target_root" ]; then
        ln -s "$target_root" "$home_memory" 2>/dev/null || true
    fi
}

# Shared flag parser for all launchers
parse_common_flags() {
    for arg in "$@"; do
        case "$arg" in
            --rebuild)
                export UDOS_REBUILD=1
                echo -e "${YELLOW}🔄 Rebuild mode: Clearing Python cache...${NC}"
                ;;
            --flag)
                export UDOS_FLAG_MODE=1
                echo -e "${CYAN}⚙️ Flag mode: enabling auto launcher hooks${NC}"
                ;;
        esac
    done
}

prompt_permission() {
    local prompt="$1"
    local choice
    echo -n "${prompt} [1-Yes|0-No|Enter-OK] "
    read -r choice
    if [ -z "$choice" ] || [ "$choice" = "1" ]; then
        return 0
    fi
    return 1
}

check_wizard_updates() {
    # Skip if not a git repo or git not available
    if [ -z "$UDOS_ROOT" ] || [ ! -d "$UDOS_ROOT/.git" ]; then
        return 0
    fi

    if ! command -v git >/dev/null 2>&1; then
        return 0
    fi

    local branch
    branch="$(git -C "$UDOS_ROOT" rev-parse --abbrev-ref HEAD 2>/dev/null)"
    if [ -z "$branch" ]; then
        branch="main"
    fi

    # Fetch quietly, ignore network errors
    if ! git -C "$UDOS_ROOT" fetch --quiet origin "$branch" 2>/dev/null; then
        # Silent fail - no network or repo issue
        return 0
    fi

    local behind
    behind="$(git -C "$UDOS_ROOT" rev-list --count HEAD..origin/$branch 2>/dev/null || echo 0)"

    if [ "$behind" -gt 0 ]; then
        echo -e "${YELLOW}⚠️  Wizard updates available (${behind} commits).${NC}"
        if prompt_permission "Update Wizard now?"; then
            # Pull with ff-only to prevent merge conflicts
            if git -C "$UDOS_ROOT" pull --ff-only origin "$branch" 2>/dev/null; then
                echo -e "${GREEN}✓${NC} Wizard updated successfully"
                export UDOS_FORCE_REBUILD=1
                if rebuild_wizard_dashboard; then
                    echo -e "${GREEN}✓${NC} Dashboard rebuilt"
                    return 0
                else
                    echo -e "${YELLOW}⚠️  Dashboard rebuild had issues${NC}"
                    return 0  # Still return success - server can start
                fi
            else
                echo -e "${RED}❌ Update failed (merge conflict or network error).${NC}"
                echo -e "${DIM}ℹ️  Run 'git pull origin ${branch}' manually to fix${NC}"
                return 0  # Don't block server startup
            fi
        else
            echo -e "${DIM}ℹ️  Skipping update.${NC}"
        fi
    fi

    return 0
}

# ═══════════════════════════════════════════════════════════════════════════
# Spinner Function
# ═══════════════════════════════════════════════════════════════════════════
run_with_spinner() {
    local message="$1"
    shift
    local cmd="$@"
    local spin_chars='⠋⠙⠹⠸⠼⠴⠦⠧⠇⠏'
    local i=0
    local start_time
    start_time=$(date +%s)

    eval "$cmd" &
    local pid=$!

    printf "  ${YELLOW}⠋${NC} %s" "$message"
    while kill -0 $pid 2>/dev/null; do
        i=$(( (i + 1) % 10 ))
        printf "\r  ${YELLOW}${spin_chars:$i:1}${NC} %s" "$message"
        sleep 0.1
    done

    wait $pid
    local exit_code=$?
    local end_time
    end_time=$(date +%s)
    local elapsed=$(( end_time - start_time ))

    printf "\r"
    if [ $exit_code -eq 0 ]; then
        printf "  ${GREEN}✓${NC} %s (${elapsed}s)\n" "$message"
    else
        printf "  ${RED}✗${NC} %s (${elapsed}s)\n" "$message"
    fi
    return $exit_code
}

# ═══════════════════════════════════════════════════════════════════════════
# Python Cache Management
# ═══════════════════════════════════════════════════════════════════════════
clear_python_cache() {
    echo -e "${YELLOW}🧹 Clearing Python cache...${NC}"

    # Remove __pycache__ directories
    find "$UDOS_ROOT" -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null || true

    # Remove .pyc files
    find "$UDOS_ROOT" -type f -name "*.pyc" -delete 2>/dev/null || true

    # Remove .pyo files
    find "$UDOS_ROOT" -type f -name "*.pyo" -delete 2>/dev/null || true

    echo -e "  ${GREEN}✓${NC} Python cache cleared"
}

# ═══════════════════════════════════════════════════════════════════════════
# Python Environment Setup
# ═══════════════════════════════════════════════════════════════════════════
ensure_python_env() {
    # Check for --rebuild flag
    if [ "$UDOS_REBUILD" = "1" ]; then
        clear_python_cache
    fi

    # Check venv - auto-create if missing
    if [ ! -d "$UDOS_ROOT/.venv" ]; then
        echo -e "${YELLOW}⚠️  Virtual environment not found - creating...${NC}"
        if run_with_spinner "Creating virtual environment..." "python3 -m venv $UDOS_ROOT/.venv"; then
            echo -e "  ${GREEN}✅ Virtual environment created${NC}"
        else
            echo -e "  ${RED}❌ Failed to create virtual environment${NC}"
            return 1
        fi
    fi

    # Activate venv
    source "$UDOS_ROOT/.venv/bin/activate"
    echo -e "${GREEN}✅ Python venv activated${NC}"

    # Check dependencies - auto-install if missing
    if ! python -c "import flask" 2>/dev/null; then
        echo -e "${YELLOW}⚠️  Dependencies missing - installing (first time setup)...${NC}"
        echo ""
        pip install --progress-bar on -r "$UDOS_ROOT/requirements.txt"
        if [ $? -eq 0 ]; then
            echo ""
            echo -e "  ${GREEN}✅ Dependencies installed${NC}"
        else
            echo ""
            echo -e "  ${RED}❌ Failed to install dependencies${NC}"
            return 1
        fi
    fi

    if ! python -c "import prompt_toolkit" 2>/dev/null; then
        echo -e "${YELLOW}⚠️  prompt_toolkit missing - installing advanced CLI helper...${NC}"
        if ! pip install --progress-bar on "prompt_toolkit>=3.0.0"; then
            echo -e "  ${RED}❌ Failed to install prompt_toolkit${NC}"
            return 1
        fi
    fi

    # Set environment
    export PYTHONPATH="$UDOS_ROOT:$PYTHONPATH"
    export UDOS_DEV_MODE=1

    # Prevent Python from writing .pyc files (helps with hot reload)
    export PYTHONDONTWRITEBYTECODE=1

    # Load .env file if it exists
    if [ -f "$UDOS_ROOT/.env" ]; then
        set -a  # Export all variables
        source "$UDOS_ROOT/.env"
        set +a
    fi

    # Create log directory
    mkdir -p "$UDOS_ROOT/memory/logs"
}

# ═══════════════════════════════════════════════════════════════════════════
# Dependency Preflight
# ═══════════════════════════════════════════════════════════════════════════
run_dependency_preflight() {
    local component="$1"
    local interactive="${2:-1}"
    local auto_repair="${3:-1}"

    if [ "$UDOS_SKIP_DEP_CHECK" = "1" ]; then
        return 0
    fi

    local py_bin="${UDOS_DEP_PYTHON_BIN:-python}"
    if ! command -v "$py_bin" >/dev/null 2>&1; then
        echo -e "${YELLOW}⚠️  Dependency preflight skipped (missing ${py_bin})${NC}"
        return 0
    fi

    "$py_bin" - "$component" "$interactive" "$auto_repair" <<'PY'
import sys

from core.services.dependency_warning_monitor import run_preflight_check

component = sys.argv[1]
interactive = bool(int(sys.argv[2]))
auto_repair = bool(int(sys.argv[3]))

try:
    code = run_preflight_check(
        component=component,
        prompt_if_interactive=interactive,
        auto_repair_if_headless=auto_repair,
    )
except Exception as exc:  # pragma: no cover
    print(f"Dependency preflight failed: {exc}")
    code = 5

sys.exit(code)
PY
    local status=$?
    if [ $status -ne 0 ]; then
        echo -e "${RED}[✗]${NC} Dependency verification failed"
    fi
    return $status
}

# ═══════════════════════════════════════════════════════════════════════════
# Header Display
# ═══════════════════════════════════════════════════════════════════════════
print_header() {
    local title="$1"
    local width=75
    local padding=$(( (width - ${#title} - 2) / 2 ))

    echo ""
    echo -e "${CYAN}${BOLD}╔═══════════════════════════════════════════════════════════════════════╗${NC}"
    printf "${CYAN}${BOLD}║%*s%s%*s║${NC}\n" $padding "" "$title" $((padding + (width - ${#title} - 2) % 2)) ""
    echo -e "${CYAN}${BOLD}╚═══════════════════════════════════════════════════════════════════════╝${NC}"
    echo ""
}

# ═══════════════════════════════════════════════════════════════════════════
# Port Management
# ═══════════════════════════════════════════════════════════════════════════
kill_port() {
    local port="$1"
    if lsof -Pi :$port -sTCP:LISTEN -t >/dev/null 2>&1; then
        echo -e "${YELLOW}⚠️  Port $port already in use, killing existing process...${NC}"
        "$UDOS_ROOT/bin/port-manager" kill :$port 2>/dev/null || lsof -ti:$port | xargs kill -9 2>/dev/null || true
        sleep 1
    fi
}

# ═══════════════════════════════════════════════════════════════════════════
# Service URL Display
# ═══════════════════════════════════════════════════════════════════════════
print_service_url() {
    local label="$1"
    local url="$2"
    printf "  ${DIM}%-14s${NC} ${GREEN}%s${NC}\n" "$label:" "$url"
}

# ═══════════════════════════════════════════════════════════════════════════
# Rebuild Helpers
# ═══════════════════════════════════════════════════════════════════════════
parse_rebuild_flag() {
    UDOS_FORCE_REBUILD=0
    UDOS_ARGS=()
    for arg in "$@"; do
        if [ "$arg" = "--rebuild" ]; then
            UDOS_FORCE_REBUILD=1
        else
            UDOS_ARGS+=("$arg")
        fi
    done
    export UDOS_FORCE_REBUILD
}

needs_rebuild() {
    local src_dir="$1"
    local marker_file="$2"

    if [ "$UDOS_FORCE_REBUILD" = "1" ]; then
        return 0
    fi
    if [ ! -f "$marker_file" ]; then
        return 0
    fi
    if find "$src_dir" -type f -newer "$marker_file" | head -n 1 | grep -q .; then
        return 0
    fi
    return 1
}

maybe_npm_install() {
    local dir="$1"
    if [ "$UDOS_FORCE_REBUILD" = "1" ] || [ ! -d "$dir/node_modules" ] || [ "$dir/package.json" -nt "$dir/package-lock.json" ]; then
        echo -e "${YELLOW}⚠️  Installing dependencies in ${dir}...${NC}"
        (cd "$dir" && npm install --no-fund --no-audit) || return 1
    fi
    return 0
}

# Build a Node project if sources changed or --rebuild is set
run_npm_build_if_needed() {
    local src_dir="$1"
    local dist_dir="$2"
    local build_cmd="$3"   # e.g. "npm run build"

    # If dist missing, always build
    if [ ! -d "$dist_dir" ]; then
        echo -e "${YELLOW}⚠️  Output not found, building...${NC}"
        (cd "$src_dir" && eval "$build_cmd") || return 1
        return 0
    fi

    # Force rebuild via flag
    if [ "$UDOS_FORCE_REBUILD" = "1" ]; then
        echo -e "${YELLOW}⚠️  --rebuild requested, building...${NC}"
        (cd "$src_dir" && eval "$build_cmd") || return 1
        return 0
    fi

    # Rebuild if any source file newer than dist
    local newest_src
    newest_src=$(find "$src_dir" -type f \( -name "*.ts" -o -name "*.tsx" -o -name "*.js" -o -name "*.svelte" -o -name "*.css" -o -name "*.json" -o -name "*.md" \) -print0 | xargs -0 -I{} stat -f "%m %N" {} 2>/dev/null | sort -nr | head -n1 | awk '{print $2}')
    local newest_dist
    newest_dist=$(find "$dist_dir" -type f -print0 | xargs -0 -I{} stat -f "%m %N" {} 2>/dev/null | sort -nr | head -n1 | awk '{print $2}')

    if [ -n "$newest_src" ] && [ -n "$newest_dist" ] && [ "$newest_src" -nt "$newest_dist" ]; then
        echo -e "${YELLOW}⚠️  Sources changed since last build, rebuilding...${NC}"
        (cd "$src_dir" && eval "$build_cmd") || return 1
    fi

    return 0
}

# ═══════════════════════════════════════════════════════════════════════════
# Rebuild After Dev Mode Operations
# ═══════════════════════════════════════════════════════════════════════════
dev_mode_marker_path() {
    echo "$UDOS_ROOT/memory/logs/dev-mode-used"
}

mark_dev_mode_used() {
    local marker
    marker="$(dev_mode_marker_path)"
    mkdir -p "$(dirname "$marker")"
    touch "$marker"
}

check_dev_mode_marker() {
    local marker
    marker="$(dev_mode_marker_path)"
    if [ -f "$marker" ]; then
        export UDOS_FORCE_REBUILD=1
        export UDOS_DEV_MODE_USED=1
        return 0
    fi
    return 1
}

clear_dev_mode_marker() {
    local marker
    marker="$(dev_mode_marker_path)"
    [ -f "$marker" ] && rm -f "$marker"
}

rebuild_core_runtime() {
    local core_dir="$UDOS_ROOT/core"
    local core_src="$core_dir"
    local core_dist="$core_dir/dist"

    if [ -f "$core_dir/package.json" ]; then
        if run_with_spinner "Core Runtime: checking build..." "maybe_npm_install '$core_dir' && run_npm_build_if_needed '$core_dir' '$core_dist' 'npm run build'"; then
            echo -e "  ${GREEN}✅ Core Runtime ready${NC}"
        else
            echo -e "  ${RED}❌ Core Runtime build failed${NC}"
            return 1
        fi
    else
        echo -e "${DIM}ℹ️  Core runtime package.json not found; skipping JS build${NC}"
    fi
}

rebuild_wizard_dashboard() {
    local dash_root="$UDOS_ROOT/wizard/dashboard"
    local dash_src="$dash_root"
    local dash_dist="$dash_root/dist"

    if [ -d "$dash_root" ] && [ -f "$dash_root/package.json" ]; then
        echo -e "${CYAN}🧙 Wizard Dashboard: checking build...${NC}"
        # Ensure npm available
        if ! command -v npm >/dev/null 2>&1; then
            echo -e "${YELLOW}⚠️  npm not found; skipping dashboard build (use Launch-Wizard-Server.command for guided install)${NC}"
            return 0
        fi
        maybe_npm_install "$dash_root" || return 1
        run_npm_build_if_needed "$dash_src" "$dash_dist" "npm run build" || return 1
        echo -e "${GREEN}✅ Wizard Dashboard ready${NC}"
    else
        echo -e "${DIM}ℹ️  Wizard dashboard sources not found; skipping${NC}"
    fi
}

rebuild_after_dev() {
    # Generic hook to rebuild JS parts after Dev Mode, or when --rebuild is passed
    rebuild_core_runtime || return 1
    rebuild_wizard_dashboard || return 1
    return 0
}

# ═══════════════════════════════════════════════════════════════════════════
# Unified Component Launcher
# ═══════════════════════════════════════════════════════════════════════════
# Central dispatcher for all component launchers (core, wizard, goblin, empire, app)
# Reduces launcher duplication across .command and .sh files
# ═════════════════════════════════════════════════════════════════════════════

_setup_component_environment() {
    if [ ! -t 0 ] || [ ! -t 1 ]; then
        echo -e "${YELLOW}⚠️  Launcher requires an interactive terminal (stdin and stdout must be TTYs).${NC}"
        return 1
    fi
    local component="$1"

    # Ensure venv and dependencies
    echo -e "${CYAN}[INFO]${NC} Checking Python environment and dependencies..."
    ensure_python_env || return 1

    # Setup memory/logs directory (prefer ~/memory/logs)
    local memory_root
    memory_root="$(resolve_memory_root)"
    mkdir -p "$memory_root/logs"
    ensure_home_memory_link "$memory_root"
    export UDOS_MEMORY_ROOT="$memory_root"
    export UDOS_LOG_DIR="$memory_root/logs"

    # Run self-healing diagnostics
    run_with_spinner "Running self-healing diagnostics for ${component}..." "python -m core.services.self_healer $component" || {
        echo -e "${YELLOW}[WARN]${NC} Some dependency issues detected (non-blocking)"
    }
}

launch_core_tui() {
    local title="uDOS Core TUI"
    print_header "$title"

    _setup_component_environment "core" || return 1

    echo -e "${CYAN}[BOOT]${NC} uDOS Root: $UDOS_ROOT"
    echo -e "${CYAN}[BOOT]${NC} Python: $(python --version)"
    echo ""

    # Launch the TUI
    python "$UDOS_ROOT/uDOS.py" "$@" || return 1
}

launch_wizard_server() {
    local title="Wizard Server - Always-On Services"
    print_header "$title"

    _setup_component_environment "wizard" || return 1
    check_wizard_updates || true  # Don't block startup on update failures

    echo -e "${CYAN}[INFO]${NC} Starting Wizard Server in background..."

    # Check if already running
    if curl -s --connect-timeout 2 http://127.0.0.1:8765/health >/dev/null 2>&1; then
        echo -e "${GREEN}✓${NC} Wizard already running on http://localhost:8765"
    else
        # Validate python module exists
        if ! python -c "import wizard.server" 2>/dev/null; then
            echo -e "${RED}❌ Wizard module not found${NC}"
            return 1
        fi

        # Start in background with proper I/O isolation
        mkdir -p "$UDOS_ROOT/memory/logs"
        nohup python -m wizard.server --no-interactive > "$UDOS_ROOT/memory/logs/wizard-server.log" 2>&1 &
        local wizard_pid=$!

        # Wait for server to be ready (max 10 seconds)
        local max_wait=10
        local waited=0
        while [ $waited -lt $max_wait ]; do
            if curl -s --connect-timeout 1 http://127.0.0.1:8765/health >/dev/null 2>&1; then
                echo -e "${GREEN}✓${NC} Wizard Server started (PID: $wizard_pid)"
                break
            fi
            sleep 0.5
            waited=$((waited + 1))
        done

        if [ $waited -ge $max_wait ]; then
            echo -e "${YELLOW}⚠${NC}  Wizard Server started but slow to respond (PID: $wizard_pid)"
            echo -e "${DIM}ℹ️  Check logs: tail -f $UDOS_ROOT/memory/logs/wizard-server.log${NC}"
        fi
    fi

    print_service_url "Server" "http://localhost:8765"
    print_service_url "Dashboard" "http://localhost:8765/dashboard"
    echo ""
    echo -e "${CYAN}[INFO]${NC} Launching uCODE TUI..."
    echo ""

    # Launch Core TUI with Wizard available
    python "$UDOS_ROOT/uDOS.py" "$@" || return 1
}

launch_wizard_tui() {
    local title="Wizard Dev TUI - Server + Interactive Console"
    print_header "$title"

    _setup_component_environment "wizard" || return 1
    check_wizard_updates || return 1

    # Delegate to wizard TUI launcher
    "$UDOS_ROOT/wizard/launch_wizard_tui.sh" "$@" || return 1
}

launch_goblin_dev() {
    local title="Goblin Dev Server - Experimental Features"
    print_header "$title"

    _setup_component_environment "goblin" || return 1

    print_service_url "Server" "http://localhost:8767"
    print_service_url "Dashboard" "http://localhost:5174"
    print_service_url "Swagger" "http://localhost:8767/docs"
    echo ""

    # Delegate to goblin launcher
    "$UDOS_ROOT/dev/bin/start-goblin-dev.sh" "$@" || return 1
}

launch_empire_dev() {
    local title="Empire Private Server - CRM & Business Intelligence"
    print_header "$title"

    _setup_component_environment "empire" || return 1

    print_service_url "Server" "http://localhost:8768"
    print_service_url "Dashboard" "http://localhost:8768/dashboard"
    echo ""

    # Delegate to empire launcher
    "$UDOS_ROOT/dev/bin/start-empire-dev.sh" "$@" || return 1
}

# Note: App (Tauri) launcher moved to dev/app/bin/
# /app is a private submodule for commercial release via Xcode/Mac App Store

launch_component() {
    local component="${1:-core}"
    local mode="${2:-tui}"
    shift 2 || shift

    # Resolve paths if not already set
    if [ -z "$UDOS_ROOT" ]; then
        UDOS_ROOT="$(resolve_udos_root)" || return 1
        export UDOS_ROOT
    fi

    cd "$UDOS_ROOT"

    # Dispatch to component-specific launcher
    case "$component:$mode" in
        core:tui)       launch_core_tui "$@" ;;
        wizard:server)  launch_wizard_server "$@" ;;
        wizard:tui)     launch_wizard_tui "$@" ;;
        goblin:dev)     launch_goblin_dev "$@" ;;
        empire:dev)     launch_empire_dev "$@" ;;
        *)
            echo -e "${RED}[ERROR]${NC} Unknown component:mode: $component:$mode"
            echo ""
            echo "Supported combinations:"
            echo "  core:tui        - Core TUI interactive"
            echo "  wizard:server   - Wizard Server + dashboard"
            echo "  wizard:tui      - Wizard TUI console"
            echo "  goblin:dev      - Goblin Dev Server"
            echo "  empire:dev      - Empire CRM Server"
            echo ""
            echo "Note: App (Tauri) launcher is in dev/app/bin/"
            return 1
            ;;
    esac
}
