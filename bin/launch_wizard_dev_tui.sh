#!/bin/bash
# Wizard Dev TUI Launcher

set -e

# Resolve uDOS root by locating uDOS.py
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
    echo "[launch_wizard_dev_tui] Could not locate uDOS repo root (missing uDOS.py)." >&2
    exit 1
}

UDOS_ROOT="$(resolve_udos_root)"
export UDOS_ROOT
cd "$UDOS_ROOT"

# Source common helpers and parse rebuild flag
if [ -f "$UDOS_ROOT/bin/udos-common.sh" ]; then
    # shellcheck source=/dev/null
    source "$UDOS_ROOT/bin/udos-common.sh"
    parse_rebuild_flag "$@"
else
    UDOS_FORCE_REBUILD=0
fi

if declare -f mark_dev_mode_used >/dev/null 2>&1; then
    mark_dev_mode_used
fi

# Activate venv if present
if [ -f "$UDOS_ROOT/.venv/bin/activate" ]; then
    source "$UDOS_ROOT/.venv/bin/activate"
fi

python3 -m wizard.dev_tui "$@"

# After Dev TUI session, optionally rebuild core and wizard assets
if declare -f rebuild_after_dev >/dev/null 2>&1; then
    echo ""
    echo "Running post-Dev rebuild checks..."
    rebuild_after_dev || echo "Post-Dev rebuild skipped or failed (non-fatal)"
fi

if declare -f mark_dev_mode_used >/dev/null 2>&1; then
    mark_dev_mode_used
fi
