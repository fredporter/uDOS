#!/bin/bash
# uDOS v1.0 - User Setup and Installation Detection
# 🔐 init-user.sh — First-time setup and user validation

set -euo pipefail

UHOME="${HOME}/uDOS"
UMEM="${UHOME}/uMemory"
USER_IDENTITY="${UMEM}/user/identity.md"
USER_SETUP_TEMPLATE="${UHOME}/uTemplate/input-user-setup.md"

# Color output helpers
red() { echo -e "\033[0;31m$1\033[0m"; }
green() { echo -e "\033[0;32m$1\033[0m"; }
yellow() { echo -e "\033[0;33m$1\033[0m"; }
blue() { echo -e "\033[0;34m$1\033[0m"; }
bold() { echo -e "\033[1m$1\033[0m"; }

# Logging
log() {
    echo "[$(date '+%Y-%m-%d %H:%M:%S')] $1" | tee -a "${UMEM}/logs/setup.log" 2>/dev/null || echo "[$(date '+%Y-%m-%d %H:%M:%S')] $1"
}

# Enhanced first-time setup detection
is_first_time_setup() {
    # Check for user identity and proper uMemory structure
    if [[ ! -f "$USER_IDENTITY" ]] || ! check_umemory_structure; then
        return 0  # Is first-time setup
    fi
    
    # Check if user role profile exists
    local username
    username=$(grep "^\*\*Username\*\*:" "$USER_IDENTITY" 2>/dev/null | cut -d' ' -f2)
    if [[ -z "$username" ]] || [[ ! -f "${UMEM}/users/profiles/${username}.md" ]]; then
        return 0  # Is first-time setup
    fi
    
    return 1  # Not first-time setup
}

# Check if required uMemory structure exists
check_umemory_structure() {
    local required_dirs=(
        "user"
        "logs"
        "state" 
        "moves"
        "missions"
        "milestones"
        "sandbox"
        "templates"
    )
    
    for dir in "${required_dirs[@]}"; do
        if [[ ! -d "${UMEM}/${dir}" ]]; then
            log "❌ Missing required directory: uMemory/${dir}"
            return 1
        fi
    done
    return 0
}

# Create uMemory structure if missing
create_umemory_structure() {
    log "🏗️  Creating uMemory directory structure..."
    
    mkdir -p "${UMEM}"/{user,logs,state,moves,missions,milestones,sandbox,templates}
    mkdir -p "${UMEM}/logs"/{moves,missions,milestones,system}
    mkdir -p "${UMEM}/users"/{profiles,roles,permissions,sessions}
    
    # Create initial log files
    touch "${UMEM}/logs/setup.log"
    touch "${UMEM}/logs/system/startup.log"
    
    green "✅ uMemory structure created"
}

# Validate installation integrity  
validate_installation() {
    log "🔍 Validating uDOS installation..."
    
    local required_paths=(
        "uCode/ucode.sh"
        "uTemplate/uc-template.md"
        "uKnowledge/ARCHITECTURE.md"
        "uScript/README.md"
    )
    
    for path in "${required_paths[@]}"; do
        if [[ ! -f "${UHOME}/${path}" ]]; then
            red "❌ Critical file missing: ${path}"
            log "ERROR: Missing critical file: ${path}"
            return 1
        fi
    done
    
    green "✅ Installation integrity validated"
    return 0
}

# Interactive user setup
setup_user_identity() {
    bold "🎭 uDOS User Identity Setup"
    echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
    echo
    
    # Core identity information
    read -p "👤 Enter your username: " username
    read -p "📧 Enter your email (optional): " email
    read -p "🌍 Enter your location code (optional): " location
    read -p "⏰ Enter your timezone (optional): " timezone
    read -p "📝 Enter your full name (optional): " full_name
    
    echo
    bold "⚙️  Preferences Setup"
    echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
    
    read -p "🎨 Theme preference (default/dark/light) [default]: " theme
    theme=${theme:-default}
    
    read -p "🐛 Enable debug mode? (y/N): " debug_mode
    debug_mode=$([ "$debug_mode" = "y" ] && echo "true" || echo "false")
    
    read -p "💾 Enable auto backup? (Y/n): " auto_backup  
    auto_backup=$([ "$debug_mode" = "n" ] && echo "false" || echo "true")
    
    # Create user identity file
    cat > "$USER_IDENTITY" << EOF
# uDOS User Identity

**Username**: ${username}
$([ -n "$location" ] && echo "**Location**: ${location}")
**Created**: $(date '+%Y-%m-%d')
$([ -n "$timezone" ] && echo "**Timezone**: ${timezone}")
**Version**: v1.0.0
**Architecture**: Single-User Installation

## Profile
- **Role**: Primary User
- **Setup**: Complete
$([ -n "$full_name" ] && echo "- **Full Name**: ${full_name}")
$([ -n "$email" ] && echo "- **Email**: ${email}")

## Preferences
- **Theme**: ${theme}
- **Debug Mode**: ${debug_mode}
- **Auto Backup**: ${auto_backup}

## System
- **uDOS Path**: ~/uDOS
- **Identity Location**: uMemory/user/identity.md
- **Installation Date**: $(date '+%Y-%m-%d %H:%M:%S')
- **Privacy Mode**: Local-Only

## Privacy Settings
- **Data Sharing**: Disabled
- **External Access**: None
- **Backup Location**: Local uMemory only
- **Session Tracking**: Local only

EOF

    # Set up user role using the role management system
    create_user_role_profile "$username"
    
    green "✅ User identity created successfully"
    log "User identity created for: $username"
}

# Create user role profile using the role management system
create_user_role_profile() {
    local username="$1"
    
    log "🔐 Setting up user role profile for $username..."
    
    # Use the role management system to create wizard role
    if [[ -f "${UHOME}/uCode/user-roles.sh" ]]; then
        "${UHOME}/uCode/user-roles.sh" create "$username" wizard
        log "User role profile created via role management system"
    else
        yellow "⚠️  Role management system not found - creating basic profile"
        # Fallback: create basic profile directly
        mkdir -p "${UMEM}/users/profiles"
        cat > "${UMEM}/users/profiles/${username}.md" << EOF
# User Profile: ${username}

**Role**: wizard
**Permission Level**: Owner  
**Created**: $(date '+%Y-%m-%d %H:%M:%S')
**Status**: Active
**Description**: Primary user with full system access

## Installation Binding
- **Device ID**: $(system_profiler SPHardwareDataType 2>/dev/null | grep "Hardware UUID" | awk '{print $3}' || echo "unknown")
- **Installation Path**: ${UHOME}
- **Privacy Level**: Maximum
EOF
    fi
    
    green "✅ User role profile configured"
}

# Show welcome message
show_welcome() {
    clear
    blue "   ┌─────────────────────────────────────────────────────────────┐"
    blue "   │                                                             │"
    blue "   │    🌟 Welcome to uDOS v1.0 — Your Personal OS! 🌟         │"  
    blue "   │                                                             │"
    blue "   │    One Installation • One User • Maximum Privacy           │"
    blue "   │                                                             │"
    blue "   └─────────────────────────────────────────────────────────────┘"
    echo
    echo "This appears to be your first time running uDOS."
    echo "Let's set up your personal computing environment..."
    echo
}

# Post-setup summary
show_setup_summary() {
    echo
    green "🎉 uDOS User Setup Complete!"
    echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
    echo
    echo "📁 Your uMemory structure is ready"
    echo "🔐 Privacy settings configured (local-only)"
    echo "👤 User identity established"  
    echo "🛡️  Permissions configured"
    echo
    echo "Next steps:"
    echo "  1. Run: ./uCode/ucode.sh"
    echo "  2. Create your first mission"
    echo "  3. Explore the uDOS interface"
    echo
    blue "Remember: This uDOS installation is bound to YOU and this device."
    blue "For additional users, they need their own uDOS installation."
    echo
}

# Main execution
main() {
    # First check if uDOS is properly installed
    if ! validate_installation; then
        red "❌ uDOS installation appears incomplete or corrupted"
        exit 1
    fi
    
    # Create uMemory structure if missing
    if ! check_umemory_structure; then
        create_umemory_structure
    fi
    
    # Check if first-time setup needed
    if is_first_time_setup; then
        bold "🎉 Welcome to uDOS v1.0!"
        echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
        echo "🔐 This installation follows uDOS core ethos:"
        echo "   • One installation per user for maximum privacy"
        echo "   • Local-first data sovereignty" 
        echo "   • Device-bound secure installation"
        echo
        show_welcome
        setup_user_identity
        
        # Validate single-user installation principle
        if [[ -f "${UHOME}/uCode/user-roles.sh" ]]; then
            "${UHOME}/uCode/user-roles.sh" validate
        fi
        
        show_setup_summary
    else
        # Existing user - validate their identity and installation
        if [[ -f "$USER_IDENTITY" ]]; then
            username=$(grep "^\*\*Username\*\*:" "$USER_IDENTITY" | cut -d' ' -f2)
            green "✅ Welcome back, $username!"
            log "User session started: $username"
            
            # Quick installation validation
            if [[ -f "${UHOME}/uCode/user-roles.sh" ]]; then
                "${UHOME}/uCode/user-roles.sh" validate
            fi
        else
            yellow "⚠️  User identity file missing - run setup again"
            exit 1
        fi
    fi
}

# Run if called directly
if [[ "${BASH_SOURCE[0]}" == "${0}" ]]; then
    main "$@"
fi
