#!/bin/bash
# uDOS User Roles & Access Module v1.3
# Manages user roles, permissions, and system access levels

# Get uDOS paths
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
UDOS_ROOT="$(cd "$SCRIPT_DIR/../../.." && pwd)"
SANDBOX="$UDOS_ROOT/sandbox"

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
CYAN='\033[0;36m'
PURPLE='\033[0;35m'
NC='\033[0m'

# Role definitions with hierarchy
declare -A ROLE_LEVELS=(
    ["tomb"]=100
    ["sorcerer"]=90
    ["wizard"]=80
    ["imp"]=70
    ["drone"]=60
    ["ghost"]=50
)

# Role descriptions
declare -A ROLE_DESCRIPTIONS=(
    ["tomb"]="Archive & Backup Management - Highest security access"
    ["sorcerer"]="Advanced Tools & Project Management" 
    ["wizard"]="Development Tools & System Administration"
    ["imp"]="Script Management & Template Creation"
    ["drone"]="Task Automation & Scheduling"
    ["ghost"]="Public Interface & Demo Access - Basic level"
)

# Role permissions
declare -A ROLE_PERMISSIONS=(
    ["tomb"]="all areas + backup/restore + historical data + system archives"
    ["sorcerer"]="all areas except tomb + advanced tools + project management"
    ["wizard"]="all areas except tomb/sorcerer + development + utilities + error handling"
    ["imp"]="script editing + template management + user projects"
    ["drone"]="task automation + scheduling + operation logs"
    ["ghost"]="demo interface + public docs + temp sandbox"
)

# Get user role from user.md
get_user_role() {
    local user_file="$SANDBOX/user.md"
    
    if [[ -f "$user_file" ]]; then
        grep "^Role:" "$user_file" 2>/dev/null | cut -d':' -f2 | tr -d ' '
    else
        echo "ghost"  # Default role
    fi
}

# Set user role
set_user_role() {
    local role="$1"
    local user_file="$SANDBOX/user.md"
    
    # Validate role
    if [[ -z "${ROLE_LEVELS[$role]}" ]]; then
        echo -e "${RED}❌ Invalid role: $role${NC}"
        echo "Valid roles: ${!ROLE_LEVELS[*]}"
        return 1
    fi
    
    if [[ ! -f "$user_file" ]]; then
        echo -e "${RED}❌ User file not found${NC}"
        return 1
    fi
    
    # Update or add role
    if grep -q "^Role:" "$user_file"; then
        sed -i.bak "s/^Role:.*/Role: $role/" "$user_file"
    else
        # Add role after username if it exists
        if grep -q "^Username:" "$user_file"; then
            sed -i.bak "/^Username:/a\\
Role: $role" "$user_file"
        else
            echo "Role: $role" >> "$user_file"
        fi
    fi
    
    # Add role description
    local description="${ROLE_DESCRIPTIONS[$role]}"
    if grep -q "^Role Description:" "$user_file"; then
        sed -i.bak "s/^Role Description:.*/Role Description: $description/" "$user_file"
    else
        echo "Role Description: $description" >> "$user_file"
    fi
    
    rm -f "$user_file.bak" 2>/dev/null
    echo -e "${GREEN}✅ User role set to: $role${NC}"
    echo "Description: $description"
}

# Check access permission for area
check_access() {
    local target_area="$1"
    local user_role=$(get_user_role)
    local user_level=${ROLE_LEVELS[$user_role]}
    local target_level=${ROLE_LEVELS[$target_area]}
    
    # If target area is not a role area, default to accessible
    if [[ -z "$target_level" ]]; then
        return 0
    fi
    
    # User can access their level and all lower levels
    if [[ $user_level -ge $target_level ]]; then
        return 0
    else
        return 1
    fi
}

# Show accessible areas for user
show_accessible_areas() {
    local user_role=$(get_user_role)
    local user_level=${ROLE_LEVELS[$user_role]}
    
    echo -e "${BLUE}🔐 Access Control for Role: $user_role${NC}"
    echo ""
    echo -e "${CYAN}Your access level: ${user_level}${NC}"
    echo -e "${CYAN}Description: ${ROLE_DESCRIPTIONS[$user_role]}${NC}"
    echo ""
    
    echo -e "${GREEN}✅ Accessible Areas:${NC}"
    for area in "${!ROLE_LEVELS[@]}"; do
        local area_level=${ROLE_LEVELS[$area]}
        if [[ $user_level -ge $area_level ]]; then
            echo -e "  • ${GREEN}$area${NC} (level $area_level) - ${ROLE_DESCRIPTIONS[$area]}"
        fi
    done
    
    echo ""
    echo -e "${RED}❌ Restricted Areas:${NC}"
    for area in "${!ROLE_LEVELS[@]}"; do
        local area_level=${ROLE_LEVELS[$area]}
        if [[ $user_level -lt $area_level ]]; then
            echo -e "  • ${RED}$area${NC} (level $area_level) - ${ROLE_DESCRIPTIONS[$area]}"
        fi
    done
}

# Interactive role setup
interactive_role_setup() {
    echo -e "${BLUE}👤 User Role Setup${NC}"
    echo ""
    echo "Available roles (from basic to advanced):"
    echo ""
    
    # Show roles in order from lowest to highest
    local sorted_roles=(ghost drone imp wizard sorcerer tomb)
    local i=1
    
    for role in "${sorted_roles[@]}"; do
        local level=${ROLE_LEVELS[$role]}
        local desc="${ROLE_DESCRIPTIONS[$role]}"
        echo -e "[$i] ${CYAN}$role${NC} (level $level)"
        echo "    $desc"
        echo ""
        ((i++))
    done
    
    echo -e "${YELLOW}Select a role (1-${#sorted_roles[@]}) or enter role name:${NC} "
    read -r choice
    
    local selected_role=""
    if [[ "$choice" =~ ^[0-9]+$ ]]; then
        local index=$((choice - 1))
        if [[ $index -ge 0 && $index -lt ${#sorted_roles[@]} ]]; then
            selected_role="${sorted_roles[$index]}"
        fi
    else
        # Check if it's a valid role name
        if [[ -n "${ROLE_LEVELS[$choice]}" ]]; then
            selected_role="$choice"
        fi
    fi
    
    if [[ -n "$selected_role" ]]; then
        set_user_role "$selected_role"
        echo ""
        show_accessible_areas
    else
        echo -e "${RED}❌ Invalid selection${NC}"
        return 1
    fi
}

# Validate access to directory
validate_directory_access() {
    local target_dir="$1"
    local user_role=$(get_user_role)
    
    # Extract area name from directory path
    local area_name=$(basename "$target_dir")
    
    if check_access "$area_name"; then
        echo -e "${GREEN}✅ Access granted to $area_name${NC}"
        return 0
    else
        echo -e "${RED}❌ Access denied to $area_name${NC}"
        echo "Your role '$user_role' does not have permission."
        echo "Required role: $area_name or higher"
        return 1
    fi
}

# Show role hierarchy
show_role_hierarchy() {
    echo -e "${BLUE}🏗️ uDOS Role Hierarchy${NC}"
    echo ""
    
    # Sort roles by level (highest to lowest)
    local sorted_roles=(tomb sorcerer wizard imp drone ghost)
    
    for role in "${sorted_roles[@]}"; do
        local level=${ROLE_LEVELS[$role]}
        local desc="${ROLE_DESCRIPTIONS[$role]}"
        local perms="${ROLE_PERMISSIONS[$role]}"
        
        case "$role" in
            "tomb") color="$PURPLE" ;;
            "sorcerer") color="$RED" ;;
            "wizard") color="$BLUE" ;;
            "imp") color="$YELLOW" ;;
            "drone") color="$CYAN" ;;
            "ghost") color="$NC" ;;
        esac
        
        echo -e "${color}┌─ $role (Level $level)${NC}"
        echo -e "${color}│  Description: $desc${NC}"
        echo -e "${color}│  Permissions: $perms${NC}"
        echo -e "${color}└─${NC}"
        echo ""
    done
}

# Check if user can access a specific command/area
can_access() {
    local target="$1"
    local user_role=$(get_user_role)
    
    # Special cases for system areas
    case "$target" in
        "tomb"|"tomb/"*)
            check_access "tomb"
            ;;
        "sorcerer"|"sorcerer/"*)
            check_access "sorcerer"
            ;;
        "wizard"|"wizard/"*)
            check_access "wizard"
            ;;
        "imp"|"imp/"*)
            check_access "imp"
            ;;
        "drone"|"drone/"*)
            check_access "drone"
            ;;
        "ghost"|"ghost/"*)
            check_access "ghost"
            ;;
        *)
            # Default areas are accessible to all
            return 0
            ;;
    esac
}

# Show current user role and permissions
show_user_role_info() {
    local user_role=$(get_user_role)
    local user_level=${ROLE_LEVELS[$user_role]}
    
    echo -e "${BLUE}👤 Current User Role Information${NC}"
    echo ""
    echo -e "${CYAN}Role:${NC} $user_role"
    echo -e "${CYAN}Level:${NC} $user_level"
    echo -e "${CYAN}Description:${NC} ${ROLE_DESCRIPTIONS[$user_role]}"
    echo -e "${CYAN}Permissions:${NC} ${ROLE_PERMISSIONS[$user_role]}"
    echo ""
    
    show_accessible_areas
}

# Main roles function
roles_main() {
    local action="${1:-info}"
    local param="${2:-}"
    
    case "$action" in
        "info"|"show")
            show_user_role_info
            ;;
        "setup")
            interactive_role_setup
            ;;
        "set")
            if [[ -n "$param" ]]; then
                set_user_role "$param"
            else
                echo -e "${RED}Usage: roles set <role_name>${NC}"
            fi
            ;;
        "hierarchy"|"list")
            show_role_hierarchy
            ;;
        "check")
            if [[ -n "$param" ]]; then
                can_access "$param" && echo -e "${GREEN}✅ Access granted${NC}" || echo -e "${RED}❌ Access denied${NC}"
            else
                echo -e "${RED}Usage: roles check <area_or_command>${NC}"
            fi
            ;;
        "accessible")
            show_accessible_areas
            ;;
        "validate")
            if [[ -n "$param" ]]; then
                validate_directory_access "$param"
            else
                echo -e "${RED}Usage: roles validate <directory_path>${NC}"
            fi
            ;;
        *)
            echo "Roles module - Available actions: info, setup, set <role>, hierarchy, check <area>, accessible, validate <dir>"
            ;;
    esac
}

# Export functions for use by other modules
export -f get_user_role check_access can_access

# Export main function
if [[ "${BASH_SOURCE[0]}" == "${0}" ]]; then
    roles_main "$@"
fi
