#!/bin/bash

# uCORE Extension Manager v1.0
# Loads and manages extensions for the uDOS system

set -euo pipefail

readonly SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
readonly UCORE_DIR="$(dirname "$SCRIPT_DIR")"
readonly EXTENSIONS_DIR="$SCRIPT_DIR"
readonly REGISTRY_FILE="$EXTENSIONS_DIR/registry.json"

# Colors
readonly GREEN='\033[0;32m'
readonly YELLOW='\033[1;33m'
readonly BLUE='\033[0;34m'
readonly CYAN='\033[0;36m'
readonly BOLD='\033[1m'
readonly NC='\033[0m'

# Load extension registry
load_registry() {
    if [[ -f "$REGISTRY_FILE" ]]; then
        cat "$REGISTRY_FILE"
    else
        echo '{"extensions": {}}'
    fi
}

# List available extensions
list_extensions() {
    echo -e "${BOLD}🔌 uCORE Extensions${NC}"
    echo ""
    
    local registry
    registry=$(load_registry)
    
    if command -v jq >/dev/null 2>&1; then
        echo "$registry" | jq -r '.extensions | to_entries[] | "\(.key): \(.value.name) v\(.value.version) - \(.value.description)"'
    else
        echo "Registry file: $REGISTRY_FILE"
        echo "Development extensions in: $EXTENSIONS_DIR/development/"
        ls -la "$EXTENSIONS_DIR/development/" 2>/dev/null || echo "No development extensions found"
    fi
    echo ""
}

# Run an extension
run_extension() {
    local extension_id="$1"
    shift
    
    local extension_script="$EXTENSIONS_DIR/development/${extension_id}.sh"
    
    if [[ -f "$extension_script" && -x "$extension_script" ]]; then
        echo -e "${BLUE}🔌 Running extension: $extension_id${NC}"
        exec "$extension_script" "$@"
    else
        echo -e "${YELLOW}⚠️ Extension not found or not executable: $extension_id${NC}"
        echo "Looking for: $extension_script"
        return 1
    fi
}

# Main dispatcher
case "${1:-LIST}" in
    "LIST")
        list_extensions
        ;;
    "RUN")
        [[ $# -lt 2 ]] && { echo "Usage: extensions.sh RUN <extension_id> [args...]" >&2; exit 1; }
        run_extension "$2" "${@:3}"
        ;;
    *)
        echo "Extension Manager Commands:"
        echo "  LIST - Show available extensions"
        echo "  RUN <id> [args] - Run an extension"
        echo ""
        echo "Available Extensions:"
        echo "  deployment-manager - Comprehensive deployment system"
        echo "  smart-input-enhanced - Advanced input collection system"
        ;;
esac
