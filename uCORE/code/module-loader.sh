#!/bin/bash
# uDOS Module Loader - Interface to uSCRIPT modules
# Provides clean access to modular components from uCORE

set -euo pipefail

# Get script directory and uDOS root
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
UDOS_ROOT="$(cd "$SCRIPT_DIR/../.." && pwd)"
MODULES_DIR="$UDOS_ROOT/uSCRIPT/modules"

# Colors for status output
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m'

# Module loader functions
load_module() {
    local module_name="$1"
    local script_name="${2:-$module_name}"
    local module_path="$MODULES_DIR/$module_name/$script_name.sh"
    
    if [[ -f "$module_path" ]]; then
        source "$module_path"
        return 0
    else
        echo -e "${RED}[ERROR]${NC} Module not found: $module_path" >&2
        return 1
    fi
}

# Execute module function
exec_module() {
    local module_name="$1"
    local script_name="${2:-$module_name}"
    local module_path="$MODULES_DIR/$module_name/$script_name.sh"
    
    if [[ -f "$module_path" ]]; then
        bash "$module_path" "${@:3}"
        return $?
    else
        echo -e "${RED}[ERROR]${NC} Module not found: $module_path" >&2
        return 1
    fi
}

# Check if module exists
module_exists() {
    local module_name="$1"
    local script_name="${2:-$module_name}"
    local module_path="$MODULES_DIR/$module_name/$script_name.sh"
    
    [[ -f "$module_path" ]]
}

# List available modules
list_modules() {
    echo -e "${GREEN}Available uSCRIPT Modules:${NC}"
    echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
    
    if [[ -d "$MODULES_DIR" ]]; then
        find "$MODULES_DIR" -name "*.sh" -type f | while read -r module; do
            local rel_path="${module#$MODULES_DIR/}"
            echo "  📦 $rel_path"
        done
    else
        echo -e "${YELLOW}[WARNING]${NC} Modules directory not found: $MODULES_DIR"
    fi
}

# Module status check
module_status() {
    local modules=("session/session-manager" "workflow/workflow-manager" "stories/story-manager" 
                   "backup/backup-restore" "input/smart-input/smart-input")
    
    echo -e "${GREEN}Module Status Check:${NC}"
    echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
    
    for module in "${modules[@]}"; do
        local module_dir="${module%/*}"
        local script_name="${module##*/}"
        
        if module_exists "$module_dir" "$script_name"; then
            echo -e "  ✅ $module"
        else
            echo -e "  ❌ $module"
        fi
    done
}

# Main command router
case "${1:-}" in
    "load")
        shift
        load_module "$@"
        ;;
    "exec")
        shift
        exec_module "$@"
        ;;
    "exists")
        shift
        module_exists "$@"
        ;;
    "list")
        list_modules
        ;;
    "status")
        module_status
        ;;
    *)
        echo "uDOS Module Loader v1.0.5.1"
        echo ""
        echo "Usage: $0 <command> [options]"
        echo ""
        echo "Commands:"
        echo "  load <module> [script]    - Source a module into current shell"
        echo "  exec <module> [script]    - Execute a module script"
        echo "  exists <module> [script]  - Check if module exists"
        echo "  list                      - List all available modules"
        echo "  status                    - Check status of core modules"
        echo ""
        echo "Examples:"
        echo "  $0 exec session session-manager start"
        echo "  $0 load workflow workflow-manager"
        echo "  $0 status"
        ;;
esac
