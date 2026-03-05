#!/bin/bash
# uDOS v1.5 macOS installer launcher
# Double-click this file on macOS to run the stable installer

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

export UDOS_AUTO_LAUNCH_VIBE=1
"$SCRIPT_DIR/install-udos.sh" "$@"
status=$?

echo
read -r -p "Installation finished. Press Enter to close this window..." _
exit "$status"
