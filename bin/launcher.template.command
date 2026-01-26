#!/bin/bash
# ╔═══════════════════════════════════════════════════════════════════════════╗
# ║                    Universal uDOS Launcher Template                       ║
# ║              macOS .command wrapper for component launchers               ║
# ║                  Delegates to unified launch_component()                  ║
# ╚═══════════════════════════════════════════════════════════════════════════╝
#
# This template is called by individual .command files which set COMPONENT and MODE
# Example .command file:
#   #!/bin/bash
#   exec "$(cd "$(dirname "$0")" && pwd)/launcher.template.command" "core" "tui" "$@"

set -e

COMPONENT="${1:-core}"
MODE="${2:-tui}"
shift 2 || shift

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
UDOS_ROOT="$(dirname "$SCRIPT_DIR")"

# Source unified launcher functions
source "$SCRIPT_DIR/udos-common.sh"

# Dispatch to component launcher
launch_component "$COMPONENT" "$MODE" "$@"
