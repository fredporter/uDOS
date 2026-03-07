#!/bin/bash
# uDOS v1.5 macOS ucode TUI launcher
# Double-click this file on macOS to open the stable ucode TUI path

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

export UV_PROJECT_ENVIRONMENT="${UV_PROJECT_ENVIRONMENT:-.venv}"
"$SCRIPT_DIR/udos" ops "$@"
status=$?

echo
read -r -p "uCODE TUI exited. Press Enter to close this window..." _
exit "$status"
