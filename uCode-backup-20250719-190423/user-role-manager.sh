#!/bin/bash
# user-role-manager.sh - User Role Management System for uDOS
# Version: 2.0.0
# Description: Role-based permissions and access control system

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
UHOME="${UHOME:-$HOME/uDOS}"
ROLES_DATASET="$UHOME/uTemplate/datasets/user-roles.json"
USER_PROFILE="$UHOME/uMemory/user/profile.json"
IDENTITY_FILE="$UHOME/uMemory/user/identity.md"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
PURPLE='\033[0;35m'
CYAN='\033[0;36m'
BOLD='\033[1m'
NC='\033[0m' # No Color

# Logging functions
log() { echo -e "${BLUE}[$(date +'%H:%M:%S')]${NC} $1"; }
error() { echo -e "${RED}[ERROR]${NC} $1" >&2; }
success() { echo -e "${GREEN}[SUCCESS]${NC} $1"; }
warning() { echo -e "${YELLOW}[WARNING]${NC} $1"; }

# Initialize user profile if it doesn't exist
init_user_profile() {
    mkdir -p "$(dirname "$USER_PROFILE")"
    
    if [[ ! -f "$USER_PROFILE" ]]; then
        local username="${USER:-unknown}"
        local current_date=$(date '+%Y-%m-%d %H:%M:%S')
        
        cat > "$USER_PROFILE" << EOF
{
  "user_id": "$(uuidgen 2>/dev/null || echo "user-$(date +%s)")",
  "username": "$username",
  "role": "user",
  "role_id": "USR",
  "created": "$current_date",
  "last_login": "$current_date",
  "dev_mode": {
    "enabled": false,
    "activated": false
  },
  "permissions": {
    "cached": false,
    "last_updated": "$current_date"
  },
  "spawned_by": "system",
  "status": "active"
}
EOF
        success "User profile initialized for $username"
    fi
}

# Get current user role
get_current_role() {
    init_user_profile
    
    if [[ -f "$USER_PROFILE" ]] && command -v jq >/dev/null 2>&1; then
        jq -r '.role // "user"' "$USER_PROFILE" 2>/dev/null
    else
        echo "user"
    fi
}

# Get role information from dataset
get_role_info() {
    local role="$1"
    
    if [[ ! -f "$ROLES_DATASET" ]]; then
        error "User roles dataset not found: $ROLES_DATASET"
        return 1
    fi
    
    if command -v jq >/dev/null 2>&1; then
        jq ".[] | select(.role == \"$role\")" "$ROLES_DATASET" 2>/dev/null
    else
        error "jq not available - cannot process role information"
        return 1
    fi
}

# Check if user has permission for a specific action
check_permission() {
    local action="$1"
    local resource="${2:-}"
    local current_role=$(get_current_role)
    local role_info=$(get_role_info "$current_role")
    
    if [[ -z "$role_info" ]]; then
        error "Role information not found for: $current_role"
        return 1
    fi
    
    # Check specific permission
    case "$action" in
        "read"|"write"|"execute")
            local permissions=$(echo "$role_info" | jq -r ".permissions.$action[]" 2>/dev/null)
            if [[ "$permissions" == "*" ]] || echo "$permissions" | grep -q "$resource"; then
                return 0
            fi
            ;;
        "admin"|"dev_mode_available"|"spawn_users"|"system_folders")
            local has_permission=$(echo "$role_info" | jq -r ".permissions.$action" 2>/dev/null)
            if [[ "$has_permission" == "true" ]]; then
                return 0
            fi
            ;;
    esac
    
    return 1
}

# Check folder access level
check_folder_access() {
    local folder="$1"
    local current_role=$(get_current_role)
    local role_info=$(get_role_info "$current_role")
    
    if [[ -z "$role_info" ]]; then
        echo "none"
        return 1
    fi
    
    echo "$role_info" | jq -r ".folder_access.$folder // \"none\"" 2>/dev/null
}

# Set user role (requires wizard permissions)
set_user_role() {
    local target_user="$1"
    local new_role="$2"
    local current_role=$(get_current_role)
    
    # Check if current user can spawn users
    if ! check_permission "spawn_users"; then
        error "Permission denied: Only Wizard role can set user roles"
        return 1
    fi
    
    # Validate new role exists
    local role_info=$(get_role_info "$new_role")
    if [[ -z "$role_info" ]]; then
        error "Invalid role: $new_role"
        echo "Available roles:"
        list_available_roles
        return 1
    fi
    
    # Update user profile
    local target_profile="$UHOME/uMemory/users/$target_user/profile.json"
    
    if [[ -f "$target_profile" ]]; then
        local role_id=$(echo "$role_info" | jq -r '.role_id')
        local current_date=$(date '+%Y-%m-%d %H:%M:%S')
        
        if command -v jq >/dev/null 2>&1; then
            jq ".role = \"$new_role\" | .role_id = \"$role_id\" | .permissions.last_updated = \"$current_date\"" "$target_profile" > "${target_profile}.tmp"
            mv "${target_profile}.tmp" "$target_profile"
            success "Role updated for user $target_user: $new_role"
        else
            error "jq not available - cannot update user profile"
            return 1
        fi
    else
        error "User profile not found: $target_user"
        return 1
    fi
}

# Toggle dev mode (wizard only)
toggle_dev_mode() {
    local mode="${1:-toggle}"
    local current_role=$(get_current_role)
    
    # Check if dev mode is available for current role
    if ! check_permission "dev_mode_available"; then
        error "Dev mode not available for role: $current_role"
        return 1
    fi
    
    local current_dev_mode="false"
    if [[ -f "$USER_PROFILE" ]] && command -v jq >/dev/null 2>&1; then
        current_dev_mode=$(jq -r '.dev_mode.enabled // false' "$USER_PROFILE" 2>/dev/null)
    fi
    
    local new_mode
    case "$mode" in
        "on"|"enable"|"true")
            new_mode="true"
            ;;
        "off"|"disable"|"false")
            new_mode="false"
            ;;
        "toggle"|"")
            new_mode=$([[ "$current_dev_mode" == "true" ]] && echo "false" || echo "true")
            ;;
        *)
            error "Invalid dev mode option: $mode (use: on/off/toggle)"
            return 1
            ;;
    esac
    
    # Update profile
    if command -v jq >/dev/null 2>&1; then
        local current_date=$(date '+%Y-%m-%d %H:%M:%S')
        jq ".dev_mode.enabled = $new_mode | .dev_mode.activated = \"$current_date\"" "$USER_PROFILE" > "${USER_PROFILE}.tmp"
        mv "${USER_PROFILE}.tmp" "$USER_PROFILE"
        
        if [[ "$new_mode" == "true" ]]; then
            warning "🔓 DEV MODE ENABLED - System folders now writable!"
            warning "This grants write access to uTemplate, uCode, and uScript folders"
        else
            success "🔒 Dev mode disabled - System protection restored"
        fi
    else
        error "jq not available - cannot update dev mode"
        return 1
    fi
}

# Show current user status
show_user_status() {
    local current_role=$(get_current_role)
    local role_info=$(get_role_info "$current_role")
    
    echo -e "${BOLD}${PURPLE}👤 User Role Status${NC}"
    echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
    
    if [[ -f "$USER_PROFILE" ]] && command -v jq >/dev/null 2>&1; then
        local username=$(jq -r '.username // "unknown"' "$USER_PROFILE" 2>/dev/null)
        local user_id=$(jq -r '.user_id // "unknown"' "$USER_PROFILE" 2>/dev/null)
        local role_id=$(jq -r '.role_id // "USR"' "$USER_PROFILE" 2>/dev/null)
        local created=$(jq -r '.created // "unknown"' "$USER_PROFILE" 2>/dev/null)
        local dev_mode=$(jq -r '.dev_mode.enabled // false' "$USER_PROFILE" 2>/dev/null)
        
        echo -e "${CYAN}Username:${NC} $username"
        echo -e "${CYAN}User ID:${NC} $user_id"
        echo -e "${CYAN}Role:${NC} $current_role ($role_id)"
        echo -e "${CYAN}Created:${NC} $created"
        echo -e "${CYAN}Dev Mode:${NC} $([[ "$dev_mode" == "true" ]] && echo "${RED}ENABLED${NC}" || echo "${GREEN}disabled${NC}")"
        echo ""
        
        if [[ -n "$role_info" ]]; then
            local description=$(echo "$role_info" | jq -r '.description')
            local level=$(echo "$role_info" | jq -r '.level')
            
            echo -e "${BLUE}Role Description:${NC} $description"
            echo -e "${BLUE}Permission Level:${NC} $level/100"
            echo ""
            
            echo -e "${PURPLE}📁 Folder Access Permissions:${NC}"
            echo "$role_info" | jq -r '.folder_access | to_entries[] | "  • \(.key): \(.value)"' | while read -r line; do
                echo -e "${GREEN}$line${NC}"
            done
            echo ""
            
            echo -e "${PURPLE}⚡ System Permissions:${NC}"
            echo "$role_info" | jq -r '.permissions | to_entries[] | select(.value == true) | "  • \(.key): enabled"' | while read -r line; do
                echo -e "${GREEN}$line${NC}"
            done
        fi
    else
        echo -e "${YELLOW}⚠️ User profile not found or jq not available${NC}"
    fi
}

# List available roles
list_available_roles() {
    echo -e "${PURPLE}📋 Available User Roles${NC}"
    echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
    
    if [[ ! -f "$ROLES_DATASET" ]]; then
        error "Roles dataset not found"
        return 1
    fi
    
    if command -v jq >/dev/null 2>&1; then
        jq -r '.[] | "🏷️  \(.role) (\(.role_id)) - Level \(.level)/100\n   \(.description)\n"' "$ROLES_DATASET"
    else
        error "jq not available - cannot display roles"
        return 1
    fi
}

# Show folder structure based on user permissions
show_accessible_folders() {
    local current_role=$(get_current_role)
    local role_info=$(get_role_info "$current_role")
    
    echo -e "${BOLD}${CYAN}📁 Accessible Folders for Role: $current_role${NC}"
    echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
    
    if [[ -z "$role_info" ]]; then
        error "Role information not available"
        return 1
    fi
    
    # Show folder access with visual indicators
    echo "$role_info" | jq -r '.folder_access | to_entries[]' | while read -r entry; do
        local folder=$(echo "$entry" | jq -r '.key')
        local access=$(echo "$entry" | jq -r '.value')
        local folder_path="$UHOME/$folder"
        
        case "$access" in
            "full")
                echo -e "  🟢 ${GREEN}$folder${NC} - Full access (read/write)"
                ;;
            "read_only")
                echo -e "  🔵 ${BLUE}$folder${NC} - Read only"
                ;;
            "read_write_limited"|"read_write_user")
                echo -e "  🟡 ${YELLOW}$folder${NC} - Limited read/write"
                ;;
            "conditional_dev")
                local dev_enabled=$(check_dev_mode_status)
                if [[ "$dev_enabled" == "true" ]]; then
                    echo -e "  🟠 ${YELLOW}$folder${NC} - Dev mode access (write enabled)"
                else
                    echo -e "  🔵 ${BLUE}$folder${NC} - Read only (dev mode disabled)"
                fi
                ;;
            "personal_only"|"demo_only")
                echo -e "  🟣 ${PURPLE}$folder${NC} - Personal/Demo access only"
                ;;
            "none")
                echo -e "  🔴 ${RED}$folder${NC} - No access"
                ;;
            *)
                echo -e "  ⚪ ${CYAN}$folder${NC} - $access"
                ;;
        esac
        
        # Show if folder exists
        if [[ -d "$folder_path" ]]; then
            echo -e "    📍 Path: $folder_path"
        else
            echo -e "    ❌ Path not found: $folder_path"
        fi
    done
}

# Check dev mode status
check_dev_mode_status() {
    if [[ -f "$USER_PROFILE" ]] && command -v jq >/dev/null 2>&1; then
        jq -r '.dev_mode.enabled // false' "$USER_PROFILE" 2>/dev/null
    else
        echo "false"
    fi
}

# Validate access to specific folder
validate_folder_access() {
    local folder="$1"
    local operation="${2:-read}"
    local access_level=$(check_folder_access "$folder")
    local dev_mode=$(check_dev_mode_status)
    
    case "$access_level" in
        "full")
            return 0
            ;;
        "read_only")
            [[ "$operation" == "read" ]] && return 0
            ;;
        "read_write_limited"|"read_write_user")
            [[ "$operation" =~ ^(read|write)$ ]] && return 0
            ;;
        "conditional_dev")
            if [[ "$operation" == "read" ]]; then
                return 0
            elif [[ "$operation" == "write" && "$dev_mode" == "true" ]]; then
                return 0
            fi
            ;;
        "personal_only"|"demo_only")
            # Additional logic needed for personal/demo paths
            return 0
            ;;
        "none")
            return 1
            ;;
    esac
    
    return 1
}

# Main function
main() {
    case "${1:-status}" in
        "status"|"show")
            show_user_status
            ;;
        "roles"|"list-roles")
            list_available_roles
            ;;
        "folders"|"access")
            show_accessible_folders
            ;;
        "set-role")
            if [[ -n "${2:-}" && -n "${3:-}" ]]; then
                set_user_role "$2" "$3"
            else
                error "Usage: $0 set-role <username> <role>"
                echo "Available roles:"
                list_available_roles
            fi
            ;;
        "dev-mode"|"dev")
            toggle_dev_mode "${2:-toggle}"
            ;;
        "check")
            if [[ -n "${2:-}" && -n "${3:-}" ]]; then
                local folder="$2"
                local operation="${3:-read}"
                if validate_folder_access "$folder" "$operation"; then
                    success "Access granted: $operation on $folder"
                    exit 0
                else
                    error "Access denied: $operation on $folder"
                    exit 1
                fi
            else
                error "Usage: $0 check <folder> <operation>"
            fi
            ;;
        "init")
            init_user_profile
            ;;
        "validate")
            log "Validating user role system"
            local errors=0
            
            # Check dataset
            if [[ ! -f "$ROLES_DATASET" ]]; then
                error "User roles dataset not found"
                ((errors++))
            fi
            
            # Check jq availability
            if ! command -v jq >/dev/null 2>&1; then
                warning "jq not available - limited functionality"
            fi
            
            # Initialize profile if needed
            init_user_profile
            
            if [[ $errors -eq 0 ]]; then
                success "User role system validation passed"
            else
                error "Validation failed with $errors errors"
                exit 1
            fi
            ;;
        "help"|*)
            echo -e "${PURPLE}👤 User Role Manager v2.0${NC}"
            echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
            echo ""
            echo "Dataset-driven role-based access control for uDOS"
            echo ""
            echo "Usage: $0 <command> [options]"
            echo ""
            echo "Commands:"
            echo "  status              - Show current user role and permissions"
            echo "  roles              - List all available roles"
            echo "  folders            - Show accessible folders for current role"
            echo "  set-role <user> <role>  - Set role for user (wizard only)"
            echo "  dev-mode [on/off]  - Toggle dev mode (wizard only)"
            echo "  check <folder> <op> - Check folder access permission"
            echo "  init               - Initialize user profile"
            echo "  validate           - Validate role system"
            echo ""
            echo "Examples:"
            echo "  $0 status               # Show current user status"
            echo "  $0 set-role alice admin # Set alice to admin role"
            echo "  $0 dev-mode on          # Enable dev mode"
            echo "  $0 check uTemplate write # Check write access to uTemplate"
            ;;
    esac
}

# Initialize if called directly
if [[ "${BASH_SOURCE[0]}" == "${0}" ]]; then
    main "$@"
fi
