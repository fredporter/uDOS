#!/bin/bash
# Core TUI Launcher (Unified)
# Delegates to launch_component() system

set -e
SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
UDOS_ROOT="$(dirname "$SCRIPT_DIR")"
source "$SCRIPT_DIR/udos-common.sh"
launch_component "core" "tui" "$@"
