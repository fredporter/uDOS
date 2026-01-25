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

# ═══════════════════════════════════════════════════════════════════════════
# Spinner Function
# ═══════════════════════════════════════════════════════════════════════════
run_with_spinner() {
    local message="$1"
    shift
    local cmd="$@"
    local spin_chars='⠋⠙⠹⠸⠼⠴⠦⠧⠇⠏'
    local i=0

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
    printf "\r"
    return $exit_code
}

# ═══════════════════════════════════════════════════════════════════════════
# Python Environment Setup
# ═══════════════════════════════════════════════════════════════════════════
ensure_python_env() {
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

    # Set environment
    export PYTHONPATH="$UDOS_ROOT:$PYTHONPATH"
    export UDOS_DEV_MODE=1

    # Create log directory
    mkdir -p "$UDOS_ROOT/memory/logs"
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
rebuild_core_runtime() {
    local core_dir="$UDOS_ROOT/core"
    local core_src="$core_dir"
    local core_dist="$core_dir/dist"

    if [ -f "$core_dir/package.json" ]; then
        echo -e "${CYAN}🔧 Core Runtime: checking build...${NC}"
        maybe_npm_install "$core_dir" || return 1
        run_npm_build_if_needed "$core_dir" "$core_dist" "npm run build" || return 1
        echo -e "${GREEN}✅ Core Runtime ready${NC}"
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
