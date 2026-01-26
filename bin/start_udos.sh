#!/bin/bash
# Main uDOS TUI Launcher
# Entry point: delegates to unified core launcher

set -e
SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
UDOS_ROOT="$(dirname "$SCRIPT_DIR")"
source "$SCRIPT_DIR/udos-common.sh"
launch_component "core" "tui" "$@"
