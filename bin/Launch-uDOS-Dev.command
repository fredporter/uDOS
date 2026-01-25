#!/bin/bash
# ╔═══════════════════════════════════════════════════════════════════════════╗
# ║                 Wizard Dev TUI Launcher (.command)                        ║
# ╚═══════════════════════════════════════════════════════════════════════════╝
set -e

cd "$(dirname "$0")/.."

echo ""
echo "Launching Wizard Dev TUI..."
echo ""

"$(pwd)/bin/launch_wizard_dev_tui.sh" "$@"

echo ""
echo "Dev TUI session ended"
read -p "Press Enter to close this window..."
