#!/bin/bash
# uCODE lightweight launcher (core|wizard|goblin)

set -e

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
source "$SCRIPT_DIR/udos-common.sh"

component="${1:-core}"
mode="${2:-}"

case "$component" in
    core|wizard|goblin) ;;
    *)
        echo "Usage: ./Launch-uCODE.command [core|wizard|goblin] [mode]" >&2
        exit 1
        ;;
esac

if [ -z "$mode" ]; then
    case "$component" in
        core) mode="tui" ;;
        wizard) mode="server" ;;
        goblin) mode="dev" ;;
    esac
fi

shift 2 2>/dev/null || true
launch_component "$component" "$mode" "$@"
