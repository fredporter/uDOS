#!/bin/bash
# uDOS DEV Command Integration
# Provides [DEV] command functionality within uCODE system

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
UDOS_ROOT="$(cd "$SCRIPT_DIR/../.." && pwd)"
DEV_STARTUP_SCRIPT="$UDOS_ROOT/dev/scripts/dev-mode-startup.sh"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

log_info() { echo -e "${BLUE}ℹ️  $1${NC}"; }
log_success() { echo -e "${GREEN}✅ $1${NC}"; }
log_warning() { echo -e "${YELLOW}⚠️  $1${NC}"; }
log_error() { echo -e "${RED}❌ $1${NC}"; }

# Execute dev mode startup
start_dev_mode() {
    log_info "Initializing uDOS Development Mode..."

    if [[ -x "$DEV_STARTUP_SCRIPT" ]]; then
        "$DEV_STARTUP_SCRIPT"
    else
        log_error "Development startup script not found or not executable"
        log_info "Expected location: $DEV_STARTUP_SCRIPT"
        return 1
    fi
}

# Check dev mode status
check_dev_status() {
    local dev_commands="$UDOS_ROOT/dev/scripts/dev-commands.sh"

    if [[ -x "$dev_commands" ]]; then
        "$dev_commands" status
    else
        log_warning "Development mode not initialized"
        echo "Run: [DEV|INIT] to initialize development environment"
    fi
}

# Quick dev commit
dev_commit() {
    local message="${1:-Development progress update}"
    local dev_commands="$UDOS_ROOT/dev/scripts/dev-commands.sh"

    if [[ -x "$dev_commands" ]]; then
        "$dev_commands" commit "$message"
    else
        log_error "Development mode not initialized"
        return 1
    fi
}

# Update repository structure
update_tree() {
    local dev_commands="$UDOS_ROOT/dev/scripts/dev-commands.sh"

    if [[ -x "$dev_commands" ]]; then
        "$dev_commands" tree
    else
        log_error "Development mode not initialized"
        return 1
    fi
}

# Migrate staged changes
migrate_changes() {
    local dev_commands="$UDOS_ROOT/dev/scripts/dev-commands.sh"

    if [[ -x "$dev_commands" ]]; then
        "$dev_commands" migrate
    else
        log_error "Development mode not initialized"
        return 1
    fi
}

# Main command dispatcher
main() {
    case "${1:-STATUS}" in
        "INIT"|"init")
            start_dev_mode
            ;;
        "STATUS"|"status")
            check_dev_status
            ;;
        "COMMIT"|"commit")
            dev_commit "${2:-Development progress update}"
            ;;
        "TREE"|"tree")
            update_tree
            ;;
        "MIGRATE"|"migrate")
            migrate_changes
            ;;
        *)
            echo "DEV Commands:"
            echo "  [DEV|INIT]                 - Initialize development mode"
            echo "  [DEV|STATUS]               - Check development status"
            echo "  [DEV|COMMIT*MESSAGE]       - Commit and push changes"
            echo "  [DEV|TREE]                 - Update repository structure"
            echo "  [DEV|MIGRATE]              - Migrate staged changes"
            ;;
    esac
}

# Execute main with all arguments
main "$@"
