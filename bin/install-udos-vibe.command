#!/bin/bash
# uDOS v1.5 macOS Installer Launcher
# Double-click this file on macOS to run the installer

# Get the directory where this script lives
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

# Run the canonical launcher install flow
export UDOS_AUTO_LAUNCH_VIBE=1
"$SCRIPT_DIR/udos" install "$@"
status=$?

echo
read -r -p "Installation finished. Press Enter to close this window..." _
exit "$status"
