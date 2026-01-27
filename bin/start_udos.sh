#!/bin/bash
# Main uDOS TUI Launcher
# Directly launches the Python TUI (called by launch_core_tui)

set -e
SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
UDOS_ROOT="$(dirname "$SCRIPT_DIR")"

cd "$UDOS_ROOT"

# Ensure venv is activated
if [ -f "$UDOS_ROOT/.venv/bin/activate" ]; then
    source "$UDOS_ROOT/.venv/bin/activate"
fi

# Launch TUI
exec python uDOS.py "$@"
