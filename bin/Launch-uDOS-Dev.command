#!/bin/bash
# uDOS Development Mode Launcher
# Launches Goblin Dev Server (experimental features)

set -e
SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
UDOS_ROOT="$(dirname "$SCRIPT_DIR")"
source "$SCRIPT_DIR/udos-common.sh"
launch_component "goblin" "dev" "$@"
