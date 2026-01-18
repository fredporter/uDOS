#!/bin/bash
#
# Launch Wizard TUI with Integrated Server Management
# Starts Wizard Server with terminal UI for development
#

cd "$(dirname "$0")"

# Activate venv
if [ -f "../.venv/bin/activate" ]; then
    source ../.venv/bin/activate
elif [ -f ".venv/bin/activate" ]; then
    source .venv/bin/activate
else
    echo "❌ Virtual environment not found"
    echo "Run: python3 -m venv .venv && source .venv/bin/activate && pip install -r requirements.txt"
    exit 1
fi

# Launch Wizard Server + TUI (integrated mode)
python launch_wizard_dev.py
