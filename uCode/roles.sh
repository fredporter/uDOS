#!/bin/bash
# uDOS v1.0 - User Role and Permission Management
# 👑 user-roles.sh — Implement NetHack-inspired role system with privacy enforcement

set -euo pipefail

UHOME="${HOME}/uDOS"
UMEM="${UHOME}/uMemory"
USERS_DIR="${UMEM}/users"

# Role definitions based on NetHack archetypes but adapted for uDOS
get_role_description() {
    case "$1" in
        "wizard") echo "Primary user with full system access and OK companion management" ;;
        "sorcerer") echo "Advanced user with scripting and automation privileges" ;;
        "ghost") echo "Limited user with read-only access to most systems" ;;
        "imp") echo "Restricted user for testing and sandboxed operations" ;;
        *) echo "Unknown role" ;;
    esac
}

# Valid roles list
get_valid_roles() {
    echo "wizard sorcerer ghost imp"
}

# Get permission for role and system
get_permission() {
    local role="$1"
    local system="$2"
    
    case "${role}:${system}" in
        "wizard:umemory") echo "full" ;;
        "wizard:ucode") echo "execute" ;;
        "wizard:utemplates") echo "create" ;;
        "wizard:uknoweledge") echo "read" ;;
        "wizard:uscript") echo "create" ;;
        "wizard:system") echo "configure" ;;
        "wizard:companions") echo "manage" ;;
        
        "sorcerer:umemory") echo "full" ;;
        "sorcerer:ucode") echo "execute" ;;
        "sorcerer:utemplates") echo "create" ;;
        "sorcerer:uknoweledge") echo "read" ;;
        "sorcerer:uscript") echo "create" ;;
        "sorcerer:system") echo "view" ;;
        "sorcerer:companions") echo "interact" ;;
        
        "ghost:umemory") echo "read" ;;
        "ghost:ucode") echo "view" ;;
        "ghost:utemplates") echo "use" ;;
        "ghost:uknoweledge") echo "read" ;;
        "ghost:uscript") echo "view" ;;
        "ghost:system") echo "none" ;;
        "ghost:companions") echo "view" ;;
        
        "imp:umemory") echo "sandbox" ;;
        "imp:ucode") echo "none" ;;
        "imp:utemplates") echo "use" ;;
        "imp:uknoweledge") echo "read" ;;
        "imp:uscript") echo "none" ;;
        "imp:system") echo "none" ;;
        "imp:companions") echo "none" ;;
        
        *) echo "none" ;;
    esac
}

# Color helpers
red() { echo -e "\033[0;31m$1\033[0m"; }
green() { echo -e "\033[0;32m$1\033[0m"; }
yellow() { echo -e "\033[0;33m$1\033[0m"; }
blue() { echo -e "\033[0;34m$1\033[0m"; }
purple() { echo -e "\033[0;35m$1\033[0m"; }
bold() { echo -e "\033[1m$1\033[0m"; }

# Logging
log_role_event() {
    echo "[$(date '+%Y-%m-%d %H:%M:%S')] ROLES: $1" >> "${UMEM}/logs/system/roles.log"
}

# Get current user info
get_current_user() {
    if [[ -f "${UMEM}/user/identity.md" ]]; then
        grep "^\*\*Username\*\*:" "${UMEM}/user/identity.md" | cut -d' ' -f2
    else
        echo "unknown"
    fi
}

# Get user role
get_user_role() {
    local username="$1"
    local role_file="${USERS_DIR}/profiles/${username}.md"
    
    if [[ -f "$role_file" ]]; then
        grep "^\*\*Role\*\*:" "$role_file" | cut -d' ' -f2- | tr '[:upper:]' '[:lower:]' | sed 's/primary user/wizard/'
    else
        echo "unknown"
    fi
}

# Check permission for user and system
check_permission() {
    local username="$1"
    local system="$2"
    local user_role
    user_role=$(get_user_role "$username")
    
    get_permission "$user_role" "$system"
}

# Enforce uDOS core ethos: one installation per user
validate_single_user_installation() {
    echo "🔐 Validating single-user installation..."
    
    local current_user
    current_user=$(get_current_user)
    
    if [[ "$current_user" == "unknown" ]]; then
        red "❌ No user identity found - run user setup first"
        return 1
    fi
    
    # Count user profiles
    local user_count
    user_count=$(find "${USERS_DIR}/profiles" -name "*.md" 2>/dev/null | wc -l)
    
    if [[ $user_count -gt 1 ]]; then
        yellow "⚠️  Multiple user profiles detected"
        echo "   uDOS ethos: One installation per user"
        echo "   Consider separate installations for additional users"
        log_role_event "WARNING: Multiple user profiles detected (count: $user_count)"
    else
        green "✅ Single-user installation confirmed"
        log_role_event "Single-user installation validated for: $current_user"
    fi
}

# Create role profile
create_role_profile() {
    local username="$1"
    local role="$2"
    local description
    description=$(get_role_description "$role")
    
    echo "👑 Creating role profile for $username as $role..."
    
    # Ensure directories exist
    mkdir -p "${USERS_DIR}"/{profiles,roles,permissions,sessions}
    
    # Get role capabilities
    local capabilities
    case "$role" in
        "wizard")
            capabilities="- 🧙‍♂️ Full system access and configuration
- 🤖 OK companion management (Chester, etc.)
- 📝 Template creation and modification
- 🔧 System script execution and development
- 🛡️ Privacy and security configuration"
            ;;
        "sorcerer")
            capabilities="- 🔮 Advanced scripting and automation
- 📝 Template creation
- 🤖 OK companion interaction
- 📊 Full uMemory access
- 👁️ System monitoring (read-only)"
            ;;
        "ghost")
            capabilities="- 👻 Read-only access to most systems
- 📖 Knowledge base access
- 📝 Template usage
- 📁 uMemory read access
- 👁️ Companion viewing only"
            ;;
        "imp")
            capabilities="- 😈 Sandbox environment access
- 📖 Knowledge base reading
- 📝 Template usage only
- 🚫 No system or script access
- 🔒 Restricted to sandbox operations"
            ;;
    esac
    
    # Get device ID
    local device_id
    device_id=$(system_profiler SPHardwareDataType 2>/dev/null | grep "Hardware UUID" | awk '{print $3}' || echo "unknown")
    
    # Create profile
    cat > "${USERS_DIR}/profiles/${username}.md" << EOF
# User Profile: ${username}

**Role**: ${role}
**Permission Level**: $([ "$role" = "wizard" ] && echo "Owner" || echo "User")
**Created**: $(date '+%Y-%m-%d %H:%M:%S')
**Status**: Active
**Description**: ${description}

## Role Capabilities
${capabilities}

## Installation Binding
- **Device ID**: ${device_id}
- **Installation Path**: ${UHOME}
- **Privacy Level**: Maximum
- **Single User**: Enforced

## Permission Matrix
$(for system in umemory ucode utemplates uknoweledge uscript system companions; do
    perm=$(get_permission "$role" "$system")
    echo "- **${system}**: ${perm}"
done)

EOF

    # Create JSON permissions file
    cat > "${USERS_DIR}/permissions/${username}.json" << EOF
{
  "username": "${username}",
  "role": "${role}",
  "permissions": {
$(for system in umemory ucode utemplates uknoweledge uscript system companions; do
    perm=$(check_permission "$username" "$system")
    echo "    \"${system}\": \"${perm}\","
done | sed '$ s/,$//')
  },
  "installation_bound": true,
  "device_id": "$(system_profiler SPHardwareDataType 2>/dev/null | grep "Hardware UUID" | awk '{print $3}' || echo "unknown")",
  "created": "$(date -u +%Y-%m-%dT%H:%M:%SZ)",
  "privacy_level": "maximum",
  "single_user_enforced": true
}
EOF

    green "✅ Role profile created for $username as $role"
    log_role_event "Role profile created: $username -> $role"
}

# Show role information
show_role_info() {
    local username="$1"
    local role
    role=$(get_user_role "$username")
    
    echo "👑 Role Information for $username"
    echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
    echo
    
    case "$role" in
        "wizard")
            purple "🧙‍♂️ Wizard - Master of uDOS"
            echo "You have full access to all uDOS systems and can manage OK companions."
            ;;
        "sorcerer") 
            blue "🔮 Sorcerer - Advanced User"
            echo "You can create scripts, templates, and interact with OK companions."
            ;;
        "ghost")
            yellow "👻 Ghost - Observer"
            echo "You have read-only access to explore uDOS safely."
            ;;
        "imp")
            red "😈 Imp - Sandbox User"  
            echo "You're restricted to sandbox operations for testing."
            ;;
        *)
            red "❓ Unknown Role"
            echo "Role not recognized - may need to recreate user profile."
            ;;
    esac
    
    echo
    echo "Permissions:"
    for system in umemory ucode utemplates uknoweledge uscript system companions; do
        local perm
        perm=$(check_permission "$username" "$system")
        local icon
        case "$perm" in
            "full") icon="🟢" ;;
            "create"|"execute"|"manage"|"configure") icon="🔵" ;;
            "read"|"view"|"interact"|"use") icon="🟡" ;;
            "sandbox") icon="🟠" ;;
            "none") icon="🔴" ;;
            *) icon="❓" ;;
        esac
        printf "  %s %-12s: %s\n" "$icon" "$system" "$perm"
    done
}

# List all users (for single-user validation)
list_users() {
    echo "👥 uDOS User Analysis"
    echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
    echo
    
    if [[ ! -d "${USERS_DIR}/profiles" ]]; then
        yellow "⚠️  No user profiles directory found"
        return 1
    fi
    
    local user_count=0
    for profile in "${USERS_DIR}/profiles"/*.md; do
        if [[ -f "$profile" ]]; then
            local username
            username=$(basename "$profile" .md)
            local role
            role=$(get_user_role "$username")
            
            printf "👤 %-15s | Role: %-10s | Status: Active\n" "$username" "$role"
            ((user_count++))
        fi
    done
    
    echo
    if [[ $user_count -eq 0 ]]; then
        red "❌ No users found - run user setup first"
    elif [[ $user_count -eq 1 ]]; then
        green "✅ Single user installation (uDOS ethos compliant)"
    else
        yellow "⚠️  Multiple users detected - consider separate installations"
        echo "   uDOS Core Ethos: One installation per user for maximum privacy"
    fi
    
    echo "   Total users: $user_count"
}

# Main role management
main() {
    local command="${1:-info}"
    local username
    username=$(get_current_user)
    
    # Ensure log directory exists
    mkdir -p "${UMEM}/logs/system"
    touch "${UMEM}/logs/system/roles.log"
    
    case "$command" in
        "info"|"show")
            if [[ "$username" == "unknown" ]]; then
                red "❌ No user identity found - run: ./uCode/init-user.sh"
                exit 1
            fi
            show_role_info "$username"
            ;;
        
        "create")
            local new_username="${2:-$username}"
            local role="${3:-wizard}"
            
            # Check if role is valid
            local valid_roles
            valid_roles=$(get_valid_roles)
            if ! echo "$valid_roles" | grep -q -w "$role"; then
                red "❌ Invalid role: $role"
                echo "Available roles: $valid_roles"
                exit 1
            fi
            
            create_role_profile "$new_username" "$role"
            ;;
            
        "list"|"users")
            list_users
            ;;
            
        "validate"|"check")
            validate_single_user_installation
            ;;
            
        "permission"|"perm")
            local system="${2:-umemory}"
            local perm
            perm=$(check_permission "$username" "$system")
            echo "User $username has '$perm' permission for $system"
            ;;
            
        *)
            echo "uDOS User Role Management v1.0"
            echo
            echo "Usage: $0 {command} [options]"
            echo
            echo "Commands:"
            echo "  info                    - Show current user role and permissions"
            echo "  create [user] [role]    - Create role profile (roles: $(get_valid_roles))"
            echo "  list                    - List all users (single-user validation)"
            echo "  validate                - Check single-user installation compliance"
            echo "  permission [system]     - Check permission for specific system"
            echo
            echo "uDOS Core Ethos: One installation per user for maximum privacy"
            ;;
    esac
}

# Run if called directly
if [[ "${BASH_SOURCE[0]}" == "${0}" ]]; then
    main "$@"
fi
