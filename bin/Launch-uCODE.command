#!/bin/bash
# ╔═══════════════════════════════════════════════════════════════════════════╗
# ║                    uCODE - Unified Terminal TUI                          ║
# ║                     macOS .command entry point                            ║
# ╚═══════════════════════════════════════════════════════════════════════════╝
# Usage: Open in Finder or run: open Launch-uCODE.command

set -e

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
UDOS_ROOT="$(dirname "$SCRIPT_DIR")"

# Source unified launcher
source "$SCRIPT_DIR/udos-common.sh"

# Delegate to unified component launcher
launch_component "core" "tui" "$@"
