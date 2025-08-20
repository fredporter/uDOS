#!/bin/bash

# uDOS Startup Script v1.3
# Handles uDOS initialization, uMEMORY backup, system startup, and timezone checks

set -euo pipefail

# Colors for output
GREEN='\033[0;32m'
BLUE='\033[0;34m'
CYAN='\033[0;36m'
YELLOW='\033[1;33m'
NC='\033[0m'

# Get the uDOS root directory
UDOS_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
USCRIPT_DIR="$UDOS_ROOT/uSCRIPT/library/ucode"

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

# Run smart backup on startup
run_startup_backup() {
    log_info "Running automatic smart backup on startup..."
    
    local smart_backup_script="$UDOS_ROOT/uCORE/code/smart-backup.sh"
    
    if [[ -x "$smart_backup_script" ]]; then
        # Run smart backup silently in background
        "$smart_backup_script" >/dev/null 2>&1 &
        local backup_pid=$!
        
        # Wait a moment to ensure backup starts
        sleep 1
        
        if kill -0 "$backup_pid" 2>/dev/null; then
            log_success "Smart backup initiated (running in background)"
        else
            log_success "Smart backup completed"
        fi
    else
        log_warning "Smart backup script not found or not executable"
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

# Check user authentication file on startup
check_user_authentication() {
    log_info "Checking user authentication..."
    
    local user_file="$UDOS_ROOT/sandbox/user.md"
    local user_auth_script="$UDOS_ROOT/uCORE/code/user-auth.sh"
    
    # Check if user.md exists
    if [[ ! -f "$user_file" ]]; then
        log_warning "User authentication file missing!"
        log_warning "This triggers security destroy and reboot protocol"
        
        # Give user a moment to see the warning
        sleep 2
        
        # Execute security protocol
        if [[ -x "$user_auth_script" ]]; then
            log_info "Executing security protocol..."
            exec "$user_auth_script" destroy
        else
            # Fallback manual cleanup
            log_error "Security system compromised - manual cleanup"
            rm -rf "$UDOS_ROOT/sandbox" 2>/dev/null || true
            rm -rf "$UDOS_ROOT/uMEMORY/user" 2>/dev/null || true
            log_info "System cleaned, restarting..."
            sleep 2
            clear
            exec "$0"
        fi
        return 1
    fi
    
    # Validate user file format
    if ! grep -q "^# 🎭 uDOS User Identity" "$user_file"; then
        log_warning "Invalid user authentication file format"
        log_warning "Triggering security reset..."
        
        if [[ -x "$user_auth_script" ]]; then
            exec "$user_auth_script" destroy
        fi
        return 1
    fi
    
    log_success "User authentication file validated"
}

# Check timezone setup
check_timezone_setup() {
    log_info "Checking timezone and location setup..."
    
    # Set USCRIPT_DIR if not already set
    if [[ -z "$USCRIPT_DIR" ]]; then
        export USCRIPT_DIR="$UDOS_ROOT/uSCRIPT"
    fi
    
    # Run timezone startup check using uSCRIPT
    if [[ -f "$USCRIPT_DIR/uscript.sh" ]]; then
        "$USCRIPT_DIR/uscript.sh" "library/ucode/timezone.sh" "startup_timezone_check" >/dev/null 2>&1
        if [[ $? -eq 0 ]]; then
            log_success "Timezone and location verified"
        else
            log_warning "Timezone setup may need attention"
        fi
    else
        log_warning "uSCRIPT not available for timezone check"
    fi
}

# Main startup sequence
main() {
    show_startup_banner
    
    log_info "Initializing uDOS system..."
    echo "  📁 Root: $UDOS_ROOT"
    echo "  🗄️  Smart Backup: Role-based with encryption & retention"
    echo "  🔄 Restart behavior: exit/quit commands restart uDOS"
    echo ""
    
    check_system_integrity
    check_user_authentication
    check_timezone_setup
    run_startup_backup
    
    echo ""
    log_success "uDOS startup sequence completed!"
    
    # Create session log
    log_info "Creating session log..."
    local session_logger="$UDOS_ROOT/uCORE/code/session-logger.sh"
    if [[ -x "$session_logger" ]]; then
        "$session_logger" startup >/dev/null 2>&1
        log_success "Session log created"
    else
        log_warning "Session logger not found"
    fi
    
    log_info "Launching main uDOS interface..."
    echo ""
    
    # Launch main uDOS interface
    exec "$UDOS_ROOT/uCORE/code/ucode.sh"
}

# Run startup sequence
main "$@"
