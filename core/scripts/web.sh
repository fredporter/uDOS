#!/bin/bash
# uDOS Web Launcher - Quick Access Script
# Place in uDOS root for easy access: ./web.sh [command]

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

# Activate venv if exists
if [ -f "$SCRIPT_DIR/.venv/bin/activate" ]; then
    source "$SCRIPT_DIR/.venv/bin/activate"
fi

# Forward all arguments to the Python launcher
python3 "$SCRIPT_DIR/extensions/web/launch_web.py" "$@"
