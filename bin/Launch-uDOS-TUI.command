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

# ═══════════════════════════════════════════════════════════════════════════
# Helper: Find uDOS root
# ═══════════════════════════════════════════════════════════════════════════
find_repo_root() {
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

# ═══════════════════════════════════════════════════════════════════════════
# Resolve uDOS root
# ═══════════════════════════════════════════════════════════════════════════
resolve_udos_root() {
    if [ -n "$UDOS_ROOT" ] && [ -f "$UDOS_ROOT/uDOS.py" ]; then
        echo "$UDOS_ROOT"
        return 0
    fi

    local script_dir
    script_dir="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
    local found
    found="$(find_repo_root "$script_dir")" && { echo "$found"; return 0; }

    found="$(find_repo_root "$(pwd)")" && { echo "$found"; return 0; }

    return 1
}

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
    ensure_python_env || echo -e "${YELLOW}[WARN]${NC} Python env setup skipped"
else
    # Minimal venv activation fallback
    if [ ! -f "$UDOS_ROOT/.venv/bin/activate" ]; then
        echo -e "${YELLOW}[SETUP]${NC} Virtual environment not found"
        echo "Creating .venv..."
        python3 -m venv "$UDOS_ROOT/.venv"
    fi
    source "$UDOS_ROOT/.venv/bin/activate"
fi

# ═══════════════════════════════════════════════════════════════════════════
# Launch TUI
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
