#!/usr/bin/env bash
#
# uDOS Reboot Script
# Performs graceful system reboot with optional cleanup
#
# Usage:
#   ./reboot.sh                 - Normal reboot (restart all services)
#   ./reboot.sh --clean         - Reboot with cleanup (rebuild caches, indexes)
#   ./reboot.sh --hard          - Hard reboot (CAUTION: clears sessions, temp files)
#   ./reboot.sh --wipe-session  - Remove session data (forces re-login)
#

set -e

# Determine uDOS home directory
UDOS_HOME="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
export UDOS_HOME

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

log_info() { echo -e "${BLUE}ℹ️  $*${NC}"; }
log_success() { echo -e "${GREEN}✅ $*${NC}"; }
log_warning() { echo -e "${YELLOW}⚠️  $*${NC}"; }
log_error() { echo -e "${RED}❌ $*${NC}"; }

# Parse command-line options
REBOOT_TYPE="normal"
for arg in "$@"; do
    case "$arg" in
        --clean) REBOOT_TYPE="clean" ;;
        --hard) REBOOT_TYPE="hard" ;;
        --wipe-session) REBOOT_TYPE="wipe-session" ;;
        --help) show_usage; exit 0 ;;
        *) log_error "Unknown option: $arg"; show_usage; exit 1 ;;
    esac
done

show_usage() {
    cat << EOF
uDOS Reboot Script

Usage:
    ./reboot.sh                 Normal reboot (restart all services)
    ./reboot.sh --clean         Reboot with cleanup (rebuild caches, indexes)
    ./reboot.sh --hard          Hard reboot (clears sessions, temp files)
    ./reboot.sh --wipe-session  Remove session data (forces re-login)
    ./reboot.sh --help          Show this help message

Details:
    normal      - Restart Wizard Server and Core TUI
    clean       - Clear caches, rebuild search indexes, restart services
    hard        - Remove all temporary data, session files, restart services
    wipe-session- Remove user session, force re-login on next start
EOF
}

# Stop services
stop_services() {
    log_info "Stopping services..."

    # Try to stop Wizard server gracefully
    if command -v ./bin/start_wizard.sh &> /dev/null; then
        log_info "Stopping Wizard Server..."
        pkill -f "wizard" || true
        sleep 1
    fi

    log_success "Services stopped"
}

# Clean up files based on reboot type
cleanup() {
    case "$REBOOT_TYPE" in
        clean)
            log_info "Cleaning caches and temporary files..."
            rm -rf "$UDOS_HOME/memory"/.cache/* 2>/dev/null || true
            rm -rf "$UDOS_HOME/.pytest_cache" 2>/dev/null || true
            rm -rf "$UDOS_HOME/__pycache__" 2>/dev/null || true
            find "$UDOS_HOME" -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null || true
            log_success "Caches cleaned"
            ;;
        hard)
            log_warning "Performing hard reboot (clearing session and temp data)..."
            rm -rf "$UDOS_HOME/memory"/{.cache,session,temp} 2>/dev/null || true
            rm -rf "$UDOS_HOME/.pytest_cache" 2>/dev/null || true
            rm -f "$UDOS_HOME/memory"/logs/*.log
            log_success "Temporary data cleared"
            ;;
        wipe-session)
            log_warning "Wiping session data..."
            rm -f "$UDOS_HOME/memory"/private/session_token* 2>/dev/null || true
            rm -f "$UDOS_HOME/memory"/user/session* 2>/dev/null || true
            log_success "Session data cleared"
            ;;
    esac
}

# Restart system
restart_system() {
    log_info "Restarting system..."

    # Check Python
    PYTHON="python3"
    if [ -f "$UDOS_HOME/.venv/bin/python3" ]; then
        PYTHON="$UDOS_HOME/.venv/bin/python3"
    fi

    log_success "System ready. Launching uDOS..."
    echo ""

    # Launch uDOS
    exec "$PYTHON" "$UDOS_HOME/uDOS.py"
}

# Main sequence
main() {
    echo ""
    echo "╔════════════════════════════════════════════════════════════╗"
    echo "║              uDOS Reboot Script v1.0.0                     ║"
    echo "║               Reboot Type: $REBOOT_TYPE"
    echo "╚════════════════════════════════════════════════════════════╝"
    echo ""

    stop_services
    cleanup
    restart_system
}

main "$@"
