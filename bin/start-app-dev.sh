#!/bin/bash
# ╔═══════════════════════════════════════════════════════════════════════════╗
# ║                    App Development Unified Launcher                       ║
# ║              uMarkdown Tauri app - Vite dev server                        ║
# ╚═══════════════════════════════════════════════════════════════════════════╝

set -e

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
UDOS_ROOT="$(cd "$SCRIPT_DIR/../.." && pwd)"

# Source shared functions
source "$UDOS_ROOT/bin/udos-common.sh"

# Delegate to unified component launcher
launch_app_dev "$@"
