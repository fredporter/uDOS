#!/bin/bash
# ╔═══════════════════════════════════════════════════════════════════════════╗
# ║                      uDOS TUI Launcher (.command)                         ║
# ║                     Offline-first Terminal UI                             ║
# ╚═══════════════════════════════════════════════════════════════════════════╝
#
# macOS launcher for uDOS interactive TUI
# Keeps terminal window open for session
# Run from Finder or command line: open Launch-uDOS-TUI.command

set -e

# Parse args
UDOS_FORCE_REBUILD=0
ARGS=()
for arg in "$@"; do
    if [ "$arg" = "--rebuild" ]; then
        UDOS_FORCE_REBUILD=1
    else
        ARGS+=("$arg")
    fi
done
export UDOS_FORCE_REBUILD
set -- "${ARGS[@]}"

cd "$(dirname "$0")/.."


# ═══════════════════════════════════════════════════════════════════════════
# Colors, Formatting, and Spinner
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

# Spinner function
SPINNER_PID=""
spinner() {
    local msg="$1"
    local delay=0.12
    local spinstr='|/-\\'
    printf "  %s " "$msg"
    while :; do
        for i in $(seq 0 3); do
            printf "\b${spinstr:$i:1}"
            sleep $delay
        done
    done
}
start_spinner() {
    spinner "$1" &
    SPINNER_PID=$!
    disown $SPINNER_PID
}
stop_spinner() {
    if [ -n "$SPINNER_PID" ] && kill -0 "$SPINNER_PID" 2>/dev/null; then
        kill "$SPINNER_PID" 2>/dev/null
        wait "$SPINNER_PID" 2>/dev/null
        printf "\b\b\b  \n"
    fi
    SPINNER_PID=""
}
trap stop_spinner EXIT

# ═══════════════════════════════════════════════════════════════════════════
# Resolve uDOS root
# ═══════════════════════════════════════════════════════════════════════════
script_dir="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
# shellcheck source=/dev/null
source "$script_dir/udos-common.sh"

# ═══════════════════════════════════════════════════════════════════════════
# Main
# ═══════════════════════════════════════════════════════════════════════════
UDOS_ROOT="$(resolve_udos_root)" || {
    echo -e "${RED}[ERROR]${NC} Could not locate uDOS repo root"
    echo "Make sure uDOS.py exists in your repo directory"
    read -p "Press Enter to exit..."
    exit 1
}

export UDOS_ROOT
cd "$UDOS_ROOT"

# Source common helpers and parse rebuild flag
if [ -f "$UDOS_ROOT/bin/udos-common.sh" ]; then
    # shellcheck source=/dev/null
    source "$UDOS_ROOT/bin/udos-common.sh"
    parse_rebuild_flag "$@"
    start_spinner "Checking Python environment and build status..."
    ensure_python_env || echo -e "${YELLOW}[WARN]${NC} Python env setup skipped"
    stop_spinner
else
    # Minimal venv activation fallback
    if [ ! -f "$UDOS_ROOT/.venv/bin/activate" ]; then
        echo -e "${YELLOW}[SETUP]${NC} Virtual environment not found"
        start_spinner "Creating .venv (virtual environment)..."
        python3 -m venv "$UDOS_ROOT/.venv" >/dev/null 2>&1
        stop_spinner
        echo -e "${GREEN}[OK]${NC} .venv created"
    fi
    start_spinner "Activating Python environment..."
    source "$UDOS_ROOT/.venv/bin/activate"
    stop_spinner
fi


# ═══════════════════════════════════════════════════════════════════════════
# Launch TUI (with spinner)
# ═══════════════════════════════════════════════════════════════════════════
echo ""
echo -e "${CYAN}╔═══════════════════════════════════════════════════════════════╗${NC}"
echo -e "${CYAN}║${BOLD}               uDOS Interactive TUI${NC}${CYAN}                          ║${NC}"
echo -e "${CYAN}║${DIM}              Offline-first Terminal UI${NC}${CYAN}                      ║${NC}"
echo -e "${CYAN}╚═══════════════════════════════════════════════════════════════╝${NC}"
echo ""
echo -e "${GREEN}[BOOT]${NC} uDOS Root: $UDOS_ROOT"
echo -e "${GREEN}[BOOT]${NC} Python: $(python --version)"
echo ""

# Run the TUI (start_udos will trigger core rebuild if needed)
"$UDOS_ROOT/bin/start_udos.sh" "$@"

# Keep window open if script exits
echo ""
echo -e "${YELLOW}[EXIT]${NC} TUI session ended"
read -p "Press Enter to close this window..."
