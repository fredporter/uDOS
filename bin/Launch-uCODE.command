#!/bin/bash
# uCODE lightweight launcher (core|wizard|goblin)

set -e

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
source "$SCRIPT_DIR/udos-common.sh"

parse_common_flags "$@"

component="${1:-core}"
mode="${2:-}"

# Preserve TTY for prompt_toolkit (bottom toolbar + live hints)
if [ -z "$UDOS_TTY" ]; then
    export UDOS_TTY=1
fi

# Check for --rebuild flag in any position
for arg in "$@"; do
    if [ "$arg" = "--rebuild" ]; then
        export UDOS_REBUILD=1
        echo "🔄 Rebuild mode: Clearing Python cache..."
    fi
done

case "$component" in
    core|wizard|goblin) ;;
    --rebuild)
        # If --rebuild is first arg, default to core
        component="core"
        ;;
    *)
        echo "Usage: ./Launch-uCODE.command [core|wizard|goblin] [mode] [--rebuild] [--quiet] [--tty] [--no-log]" >&2
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

# Strip --rebuild from args before passing to launch
args=()
for arg in "$@"; do
    if [ "$arg" != "--rebuild" ] && [ "$arg" != "$component" ] && [ "$arg" != "$mode" ]; then
        args+=("$arg")
    fi
done

launch_component "$component" "$mode" "${args[@]}"
