#!/bin/bash

# uDOS Startup Script v1.3
# Handles uDOS initialization, uMEMORY backup, and system startup

set -euo pipefail

# Colors for output
GREEN='\033[0;32m'
BLUE='\033[0;34m'
CYAN='\033[0;36m'
YELLOW='\033[1;33m'
NC='\033[0m'

# Get the uDOS root directory
UDOS_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"

# Log functions
log_info() { echo -e "${CYAN}ℹ️  $1${NC}"; }
log_success() { echo -e "${GREEN}✅ $1${NC}"; }
log_warning() { echo -e "${YELLOW}⚠️  $1${NC}"; }

# Display startup banner
show_startup_banner() {
    echo -e "${BLUE}"
    echo "╔══════════════════════════════════════════════════════════════════════════════╗"
    echo "║                                                                              ║"
    echo "║                    🚀 uDOS System Startup v1.3                             ║"
    echo "║                                                                              ║"
    echo "╚══════════════════════════════════════════════════════════════════════════════╝"
    echo -e "${NC}"
}

# Run uMEMORY backup on startup
run_startup_backup() {
    log_info "Running automatic uMEMORY backup on startup..."
    
    local backup_script="$UDOS_ROOT/uCORE/code/backup-umemory.sh"
    
    if [[ -x "$backup_script" ]]; then
        # Run backup silently in background
        "$backup_script" >/dev/null 2>&1 &
        local backup_pid=$!
        
        # Wait a moment to ensure backup starts
        sleep 1
        
        if kill -0 "$backup_pid" 2>/dev/null; then
            log_success "uMEMORY backup initiated (running in background)"
        else
            log_warning "uMEMORY backup completed immediately"
        fi
    else
        log_warning "uMEMORY backup script not found or not executable"
    fi
}

# Check system integrity
check_system_integrity() {
    log_info "Checking uDOS system integrity..."
    
    local critical_dirs=("uCORE" "uMEMORY" "sandbox" "docs")
    local missing_dirs=()
    
    for dir in "${critical_dirs[@]}"; do
        if [[ ! -d "$UDOS_ROOT/$dir" ]]; then
            missing_dirs+=("$dir")
        fi
    done
    
    if [[ ${#missing_dirs[@]} -eq 0 ]]; then
        log_success "System integrity check passed"
    else
        log_warning "Missing directories: ${missing_dirs[*]}"
    fi
}

# Main startup sequence
main() {
    show_startup_banner
    
    log_info "Initializing uDOS system..."
    echo "  📁 Root: $UDOS_ROOT"
    echo "  🗄️  Auto-backup: uMEMORY → role/backup/ + sandbox/backup/"
    echo "  🔄 Restart behavior: exit/quit commands restart uDOS"
    echo ""
    
    check_system_integrity
    run_startup_backup
    
    echo ""
    log_success "uDOS startup sequence completed!"
    log_info "Launching main uDOS interface..."
    echo ""
    
    # Launch main uDOS interface
    exec "$UDOS_ROOT/uCORE/code/ucode.sh"
}

# Run startup sequence
main "$@"
