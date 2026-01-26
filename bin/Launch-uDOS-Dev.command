#!/bin/bash
# uDOS Development Mode Launcher
# Delegates to unified launch_component() system

set -e
SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
UDOS_ROOT="$(dirname "$SCRIPT_DIR")"
source "$SCRIPT_DIR/udos-common.sh"
launch_component "core" "dev" "$@"
