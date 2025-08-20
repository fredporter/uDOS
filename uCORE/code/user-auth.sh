#!/bin/bash

# uDOS User Authentication System v1.3
# Manages user.md file in sandbox for authentication and user data
# Missing user.md triggers destroy and reboot for security
# Includes timezone, location, and role management

set -euo pipefail

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
PURPLE='\033[0;35m'
CYAN='\033[0;36m'
NC='\033[0m' # No Color

# Get the uDOS root directory
UDOS_ROOT="${UDOS_ROOT:-$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)}"
SANDBOX_DIR="$UDOS_ROOT/sandbox"
USER_FILE="$SANDBOX_DIR/user.md"
USCRIPT_DIR="$UDOS_ROOT/uSCRIPT/library/ucode"

# Log functions
log_info() { echo -e "${CYAN}ℹ️  $1${NC}"; }
log_success() { echo -e "${GREEN}✅ $1${NC}"; }
log_warning() { echo -e "${YELLOW}⚠️  $1${NC}"; }
log_error() { echo -e "${RED}❌ $1${NC}"; }

# Check if user.md exists and is valid
check_user_file() {
    if [[ ! -f "$USER_FILE" ]]; then
        log_error "User authentication file missing: $USER_FILE"
        log_warning "This triggers system destroy and reboot for security"
        return 1
    fi
    
    # Validate file structure
    if ! grep -q "^# 🎭 uDOS User Identity" "$USER_FILE"; then
        log_error "Invalid user file format"
        return 1
    fi
    
    return 0
}

# Extract value from user.md file
get_user_value() {
    local key="$1"
    local default_value="${2:-}"
    
    if [[ ! -f "$USER_FILE" ]]; then
        echo "$default_value"
        return
    fi
    
    local value=$(grep "^\*\*${key}\*\*:" "$USER_FILE" 2>/dev/null | sed "s/^\*\*${key}\*\*: *//" | sed 's/^`//;s/`$//')
    echo "${value:-$default_value}"
}

# Update value in user.md file
set_user_value() {
    local key="$1"
    local value="$2"
    
    if [[ ! -f "$USER_FILE" ]]; then
        log_error "User file does not exist"
        return 1
    fi
    
    # Create backup
    cp "$USER_FILE" "$USER_FILE.backup"
    
    # Update the value
    if grep -q "^\*\*${key}\*\*:" "$USER_FILE"; then
        sed -i'' -e "s/^\*\*${key}\*\*: .*/\*\*${key}\*\*: $value/" "$USER_FILE"
    else
        log_error "Key not found in user file: $key"
        return 1
    fi
    
    # Update last modified timestamp
    local current_date=$(date "+%Y-%m-%d %H:%M:%S")
    sed -i'' -e "s/\*\*Last Modified\*\*: .*/\*\*Last Modified\*\*: $current_date/" "$USER_FILE"
    
    # Remove backup if successful
    rm -f "$USER_FILE.backup"
}

# Hash password using SHA-256
hash_password() {
    local password="$1"
    echo -n "$password" | shasum -a 256 | cut -d' ' -f1
}

# Validate password length (1-16 characters)
validate_password() {
    local password="$1"
    local length=${#password}
    
    if [[ $length -gt 16 ]]; then
        log_error "Password too long (maximum 16 characters)"
        return 1
    fi
    
    return 0
}

# Create new user.md file
create_user_file() {
    local username="${1:-$USER}"
    local password="$2"
    
    # Ensure sandbox directory exists
    mkdir -p "$SANDBOX_DIR"
    
    # Generate user ID (timestamp + random)
    local user_id="$(date +%Y%m%d)$(printf "%04d" $((RANDOM % 10000)))"
    local creation_date="$(date "+%Y-%m-%d %H:%M:%S")"
    
    # Handle password
    local password_status="NONE"
    local password_hash="BLANK"
    
    if [[ -n "$password" ]]; then
        if ! validate_password "$password"; then
            return 1
        fi
        password_status="SET"
        password_hash=$(hash_password "$password")
    fi
    
    # Get timezone information
    local timezone=$(get_system_timezone)
    local city=$(get_timezone_city "$timezone")
    local current_time=$(date "+%Y-%m-%d %H:%M:%S %Z")
    
    # Create user.md from template
    cat > "$USER_FILE" << EOF
# 🎭 uDOS User Identity
**System**: uDOS v1.3  
**Created**: $creation_date  
**Last Modified**: $creation_date  

## 🔐 Authentication
**Username**: $username  
**Password**: $password_status  
**Password Hash**: $password_hash

## 🎯 User Settings
**User ID**: $user_id  
**Role**: ghost  
**Role Description**: Public Interface & Demo Access - Basic level
**Theme**: default  
**Debug Mode**: false

## 🌍 Location Profile
**Timezone**: $timezone  
**Location Name**: $city  
**Last Timezone Check**: $current_time

## 📁 Workspace Preferences
**Auto Backup**: true  
**Companion Enabled**: true  
**Default Editor**: nano

---
*This file contains your personal user data and authentication credentials.*  
*It should only exist in the sandbox folder and is never tracked by git.*  
*Missing this file will trigger system destroy and reboot for security.*
EOF

    # Set secure permissions
    chmod 600 "$USER_FILE"
    
    log_success "User file created: $USER_FILE"
    log_info "Username: $username"
    log_info "User ID: $user_id"
    log_info "Role: ghost (default)"
    log_info "Location: $city"
    log_info "Timezone: $timezone"
    if [[ -n "$password" ]]; then
        log_info "Password: SET (${#password} characters)"
    else
        log_info "Password: NONE (authentication disabled)"
    fi
}

# Get system timezone (helper function)
get_system_timezone() {
    if [[ -f /etc/timezone ]]; then
        cat /etc/timezone
    elif [[ -L /etc/localtime ]]; then
        readlink /etc/localtime | sed 's|.*/zoneinfo/||'
    elif command -v timedatectl >/dev/null 2>&1; then
        timedatectl | grep "Time zone" | awk '{print $3}'
    else
        date +%Z
    fi
}

# Get timezone city name (helper function)
get_timezone_city() {
    local tz="$1"
    if [[ -n "$tz" && "$tz" =~ / ]]; then
        echo "$tz" | cut -d'/' -f2 | tr '_' ' '
    else
        echo "Unknown"
    fi
}

# Interactive user setup
interactive_setup() {
    echo -e "${BLUE}🎭 uDOS User Setup${NC}"
    echo ""
    
    # Get username
    local default_username="$USER"
    echo -ne "${CYAN}👤 Enter username [$default_username]: ${NC}"
    read -r username
    username="${username:-$default_username}"
    
    # Get password
    echo -ne "${CYAN}🔐 Enter password (1-16 chars, blank for none): ${NC}"
    read -s password
    echo ""
    
    if [[ -n "$password" ]]; then
        if ! validate_password "$password"; then
            return 1
        fi
        
        # Confirm password
        echo -ne "${CYAN}🔐 Confirm password: ${NC}"
        read -s password_confirm
        echo ""
        
        if [[ "$password" != "$password_confirm" ]]; then
            log_error "Passwords do not match"
            return 1
        fi
    fi
    
    # Create user file
    create_user_file "$username" "$password"
}

# Authenticate user
authenticate() {
    if [[ "${UDOS_DEV_MODE:-false}" == "true" ]]; then
        log_info "Skipping authentication (development mode)"
        return 0
    fi
    
    if ! check_user_file; then
        trigger_destroy_reboot
        return 1
    fi
    
    local stored_hash=$(get_user_value "Password Hash")
    local username=$(get_user_value "Username")
    
    # Skip if no password set
    if [[ "$stored_hash" == "BLANK" ]]; then
        log_info "Welcome back, $username! (no password required)"
        return 0
    fi
    
    # Prompt for password
    echo -ne "${CYAN}🔐 Enter password for $username: ${NC}"
    read -s password
    echo ""
    
    # Validate password
    local input_hash=$(hash_password "$password")
    
    if [[ "$input_hash" != "$stored_hash" ]]; then
        log_error "Authentication failed for user: $username"
        sleep 2  # Delay for security
        return 1
    fi
    
    log_success "Welcome back, $username!"
    return 0
}

# Change password
change_password() {
    if ! check_user_file; then
        trigger_destroy_reboot
        return 1
    fi
    
    local username=$(get_user_value "Username")
    
    echo -ne "${CYAN}🔐 Enter new password (1-16 chars, blank for none): ${NC}"
    read -s password
    echo ""
    
    if [[ -n "$password" ]]; then
        if ! validate_password "$password"; then
            return 1
        fi
        
        # Confirm password
        echo -ne "${CYAN}🔐 Confirm new password: ${NC}"
        read -s password_confirm
        echo ""
        
        if [[ "$password" != "$password_confirm" ]]; then
            log_error "Passwords do not match"
            return 1
        fi
        
        local password_hash=$(hash_password "$password")
        set_user_value "Password" "SET"
        set_user_value "Password Hash" "$password_hash"
        log_success "Password updated for $username"
    else
        set_user_value "Password" "NONE"
        set_user_value "Password Hash" "BLANK"
        log_success "Password disabled for $username"
    fi
}

# Show user information
show_user_info() {
    if ! check_user_file; then
        trigger_destroy_reboot
        return 1
    fi
    
    echo -e "${BLUE}🎭 uDOS User Information${NC}"
    echo ""
    echo -e "${CYAN}Username:${NC} $(get_user_value "Username")"
    echo -e "${CYAN}User ID:${NC} $(get_user_value "User ID")"
    echo -e "${CYAN}Password:${NC} $(get_user_value "Password")"
    echo -e "${CYAN}Role:${NC} $(get_user_value "Role")"
    echo -e "${CYAN}Theme:${NC} $(get_user_value "Theme")"
    echo -e "${CYAN}Created:${NC} $(get_user_value "Created")"
    echo -e "${CYAN}Last Modified:${NC} $(get_user_value "Last Modified")"
    echo ""
    echo -e "${CYAN}Location:${NC}"
    echo -e "  Timezone: $(get_user_value "Timezone")"
    echo -e "  City: $(get_user_value "City")"
    echo -e "  Country: $(get_user_value "Country")"
    echo ""
    echo -e "${CYAN}Preferences:${NC}"
    echo -e "  Auto Backup: $(get_user_value "Auto Backup")"
    echo -e "  Companion: $(get_user_value "Companion Enabled")"
    echo -e "  Editor: $(get_user_value "Default Editor")"
}

# Trigger destroy and reboot when user.md is missing
trigger_destroy_reboot() {
    log_error "SECURITY ALERT: User authentication file missing!"
    log_warning "System integrity compromised - triggering destroy and reboot"
    echo ""
    echo -e "${RED}╔════════════════════════════════════════╗${NC}"
    echo -e "${RED}║  🚨 SECURITY BREACH DETECTED 🚨       ║${NC}"
    echo -e "${RED}║                                        ║${NC}"
    echo -e "${RED}║  User authentication file missing     ║${NC}"
    echo -e "${RED}║  Initiating security protocol         ║${NC}"
    echo -e "${RED}║                                        ║${NC}"
    echo -e "${RED}║  → Destroy sandbox                    ║${NC}"
    echo -e "${RED}║  → Reboot system                      ║${NC}"
    echo -e "${RED}╚════════════════════════════════════════╝${NC}"
    echo ""
    
    sleep 3
    
    # Create session log for security destroy
    local session_logger="$UDOS_ROOT/uCORE/code/session-logger.sh"
    if [[ -x "$session_logger" ]]; then
        "$session_logger" destroy >/dev/null 2>&1
    fi
    
    # Execute destroy script
    local destroy_script="$UDOS_ROOT/uCORE/code/destroy.sh"
    if [[ -x "$destroy_script" ]]; then
        log_info "Executing security destroy protocol..."
        export UCODE_HEADLESS=true
        "$destroy_script" <<< "B"  # Fresh start option
    else
        # Manual cleanup
        log_info "Manual security cleanup..."
        rm -rf "$SANDBOX_DIR" 2>/dev/null || true
        rm -rf "$UDOS_ROOT/uMEMORY/user" 2>/dev/null || true
    fi
    
    # Restart system
    log_info "Restarting uDOS for security..."
    sleep 2
    clear
    exec "$UDOS_ROOT/uCORE/code/startup.sh"
}

# Main function
main() {
    case "${1:-help}" in
        "check")
            check_user_file
            ;;
        "create")
            if [[ -f "$USER_FILE" ]]; then
                log_error "User file already exists: $USER_FILE"
                log_info "Use 'reset' to recreate or 'info' to view current user"
                return 1
            fi
            interactive_setup
            ;;
        "setup"|"interactive")
            interactive_setup
            ;;
        "auth"|"authenticate")
            authenticate
            ;;
        "password"|"passwd")
            change_password
            ;;
        "info"|"show")
            show_user_info
            ;;
        "reset")
            if [[ -f "$USER_FILE" ]]; then
                log_warning "This will delete the current user file!"
                read -p "Continue? (y/N): " -n 1 -r
                echo
                if [[ $REPLY =~ ^[Yy]$ ]]; then
                    rm -f "$USER_FILE"
                    log_success "User file deleted"
                    interactive_setup
                else
                    log_info "Reset cancelled"
                fi
            else
                log_info "No user file exists, creating new one"
                interactive_setup
            fi
            ;;
        "destroy")
            trigger_destroy_reboot
            ;;
        "help"|"-h"|"--help"|*)
            echo -e "${BLUE}🎭 uDOS User Authentication System${NC}"
            echo ""
            echo "Usage: $0 <command>"
            echo ""
            echo "Commands:"
            echo "  check       - Check if user.md exists and is valid"
            echo "  create      - Create new user.md file (interactive)"
            echo "  setup       - Same as create"
            echo "  auth        - Authenticate current user"
            echo "  password    - Change user password"
            echo "  info        - Show user information"
            echo "  reset       - Delete and recreate user.md"
            echo "  destroy     - Trigger security destroy and reboot"
            echo "  help        - Show this help"
            echo ""
            echo "Security Features:"
            echo "  • User data stored only in sandbox/user.md"
            echo "  • Password hashing with SHA-256"
            echo "  • 1-16 character password limit"
            echo "  • Missing user.md triggers destroy/reboot"
            echo "  • Development mode bypasses authentication"
            ;;
    esac
}

# Run main function
main "$@"
