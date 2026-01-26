#!/bin/bash
#
# Launch Wizard TUI with Integrated Server Management
# Starts Wizard Server with terminal UI for development
#

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
UDOS_ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"

# shellcheck source=/dev/null
source "$UDOS_ROOT/bin/udos-common.sh"

cd "$SCRIPT_DIR"

if [ -f "$UDOS_ROOT/.venv/bin/activate" ]; then
    echo "Activating virtual environment..."
    # shellcheck source=/dev/null
    source "$UDOS_ROOT/.venv/bin/activate"
else
    echo "❌ Virtual environment not found"
    echo "Run: python3 -m venv .venv && source .venv/bin/activate && pip install -r requirements.txt"
    exit 1
fi

# Launch Wizard Server + TUI (integrated mode)
python launch_wizard_dev.py
