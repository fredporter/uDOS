#!/bin/bash
# Wizard Dev TUI Launcher

set -e

script_dir="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
# shellcheck source=/dev/null
source "$script_dir/udos-common.sh"

UDOS_ROOT="$(resolve_udos_root)"
export UDOS_ROOT
cd "$UDOS_ROOT"

parse_rebuild_flag "$@"

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
