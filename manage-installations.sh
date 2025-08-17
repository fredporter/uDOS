#!/bin/bash

# uDOS v1.3 Multi-Installation Management Script
# Manages role-specific installations and permissions

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
PURPLE='\033[0;35m'
CYAN='\033[0;36m'
NC='\033[0m' # No Color

# Installation directory
INSTALL_DIR="/Users/agentdigital/uDOS/installations"
SHARED_DIR="/Users/agentdigital/uDOS/shared"
UCORE_DIR="/Users/agentdigital/uDOS/uCORE"

# Available roles and their levels (using arrays for compatibility)
ROLE_NAMES=(ghost tomb drone imp sorcerer wizard)
ROLE_LEVELS=(10 20 40 60 80 100)
ROLE_EMOJIS=("👻" "⚰️" "🤖" "👹" "🔮" "🧙‍♂️")

# Function to get role level
get_role_level() {
    local role="$1"
    for i in "${!ROLE_NAMES[@]}"; do
        if [ "${ROLE_NAMES[$i]}" = "$role" ]; then
            echo "${ROLE_LEVELS[$i]}"
            return
        fi
    done
    echo ""
}

# Function to get role emoji
get_role_emoji() {
    local role="$1"
    for i in "${!ROLE_NAMES[@]}"; do
        if [ "${ROLE_NAMES[$i]}" = "$role" ]; then
            echo "${ROLE_EMOJIS[$i]}"
            return
        fi
    done
    echo ""
}

# Function to display header
show_header() {
    echo -e "${PURPLE}┌─────────────────────────────────────────────┐${NC}"
    echo -e "${PURPLE}│     🏗️  uDOS v1.3 Installation Manager     │${NC}"
    echo -e "${PURPLE}│        Multi-Role Architecture v2.0        │${NC}"
    echo -e "${PURPLE}└─────────────────────────────────────────────┘${NC}"
    echo
}

# Function to list available installations
list_installations() {
    echo -e "${CYAN}📂 Available Installations:${NC}"
    echo
    
    for role in "${ROLE_NAMES[@]}"; do
        local level=$(get_role_level "$role")
        local emoji=$(get_role_emoji "$role")
        local dir_path="$INSTALL_DIR/$role"
        
        if [ -d "$dir_path" ] || [ -L "$dir_path" ]; then
            local status="${GREEN}✅ Installed${NC}"
            if [ -L "$dir_path" ]; then
                status="${BLUE}🔗 Symlink${NC}"
            fi
        else
            local status="${RED}❌ Not Found${NC}"
        fi
        
        printf "  %s %-10s (Level %3s) - %s\n" "$emoji" "$role" "$level" "$status"
    done
    echo
}

# Function to show installation details
show_installation_details() {
    local role="$1"
    
    if [ -z "$role" ]; then
        echo -e "${RED}❌ Error: No role specified${NC}"
        return 1
    fi
    
    local level=$(get_role_level "$role")
    if [ -z "$level" ]; then
        echo -e "${RED}❌ Error: Invalid role '$role'${NC}"
        return 1
    fi
    
    local emoji=$(get_role_emoji "$role")
    local dir_path="$INSTALL_DIR/$role"
    
    echo -e "${CYAN}$emoji $role Installation Details (Level $level):${NC}"
    echo
    
    if [ -d "$dir_path" ] || [ -L "$dir_path" ]; then
        echo -e "${GREEN}✅ Status: Installed${NC}"
        echo -e "📁 Location: $dir_path"
        
        if [ -L "$dir_path" ]; then
            local target=$(readlink "$dir_path")
            echo -e "🔗 Symlink Target: $target"
        fi
        
        echo
        echo -e "${BLUE}📊 Directory Contents:${NC}"
        ls -la "$dir_path" 2>/dev/null | head -10
        
        if [ -f "$dir_path/README.md" ]; then
            echo
            echo -e "${YELLOW}📖 README Available: $dir_path/README.md${NC}"
        fi
    else
        echo -e "${RED}❌ Status: Not Installed${NC}"
        echo -e "📁 Expected Location: $dir_path"
    fi
    echo
}

# Function to validate role permissions
validate_permissions() {
    local role="$1"
    
    echo -e "${CYAN}🔐 Validating Permissions for $role:${NC}"
    echo
    
    # Check shared resources access
    echo -e "${BLUE}Shared Resources:${NC}"
    
    local permissions_file="$SHARED_DIR/permissions/${role}-permissions.json"
    if [ -f "$permissions_file" ]; then
        echo -e "  ✅ Permissions file: $permissions_file"
    else
        echo -e "  ❌ Missing permissions file: $permissions_file"
    fi
    
    # Check uCORE access based on role level
    local level=$(get_role_level "$role")
    echo -e "${BLUE}uCORE Access (Level $level):${NC}"
    
    case "$role" in
        "wizard")
            echo -e "  ✅ Full system access"
            echo -e "  ✅ Development environment"
            echo -e "  ✅ Git integration"
            ;;
        "sorcerer")
            echo -e "  ✅ Advanced user features"
            echo -e "  ✅ Project management"
            echo -e "  ❌ System administration"
            ;;
        "imp")
            echo -e "  ✅ Development tools"
            echo -e "  ✅ Script editing"
            echo -e "  ❌ User management"
            ;;
        "drone")
            echo -e "  ✅ Task automation"
            echo -e "  ✅ Monitoring tools"
            echo -e "  ❌ Development access"
            ;;
        "tomb")
            echo -e "  ✅ Archive access"
            echo -e "  ✅ Backup management"
            echo -e "  ❌ Live data modification"
            ;;
        "ghost")
            echo -e "  ✅ Demo interface"
            echo -e "  ✅ Public documentation"
            echo -e "  ❌ System access"
            ;;
    esac
    echo
}

# Function to create missing installation
create_installation() {
    local role="$1"
    
    local level=$(get_role_level "$role")
    if [ -z "$level" ]; then
        echo -e "${RED}❌ Error: Invalid role '$role'${NC}"
        return 1
    fi
    
    local emoji=$(get_role_emoji "$role")
    local dir_path="$INSTALL_DIR/$role"
    
    echo -e "${YELLOW}🔧 Creating $emoji $role installation...${NC}"
    
    # Create role-specific directories based on role type
    case "$role" in
        "wizard")
            echo -e "🔗 Creating symlink to existing wizard folder..."
            ln -sf "../wizard" "$dir_path"
            ;;
        "sorcerer")
            mkdir -p "$dir_path"/{project-manager,user-admin,advanced-tools}
            ;;
        "imp")
            mkdir -p "$dir_path"/{script-editor,template-manager,user-projects}
            ;;
        "drone")
            mkdir -p "$dir_path"/{task-automation,scheduler,operation-logs}
            ;;
        "tomb")
            mkdir -p "$dir_path"/{archive-browser,backup-manager,historical-data}
            ;;
        "ghost")
            mkdir -p "$dir_path"/{demo-interface,public-docs,temp-sandbox}
            ;;
    esac
    
    # Create role-specific README if it doesn't exist
    if [ ! -f "$dir_path/README.md" ] && [ "$role" != "wizard" ]; then
        echo "# $emoji $role Installation" > "$dir_path/README.md"
        echo "Role Level: $level/100" >> "$dir_path/README.md"
        echo "Created: $(date)" >> "$dir_path/README.md"
    fi
    
    # Create permissions file
    local permissions_file="$SHARED_DIR/permissions/${role}-permissions.json"
    if [ ! -f "$permissions_file" ]; then
        mkdir -p "$SHARED_DIR/permissions"
        cat > "$permissions_file" << EOF
{
    "role": "$role",
    "level": $level,
    "permissions": {
        "uCORE": "role-based",
        "uMEMORY": "role-based",
        "uKNOWLEDGE": "role-based",
        "sandbox": "role-based",
        "installation": "full"
    },
    "created": "$(date -Iseconds)",
    "version": "1.3"
}
EOF
    fi
    
    echo -e "${GREEN}✅ $emoji $role installation created successfully${NC}"
    echo
}

# Function to show role comparison
show_role_comparison() {
    echo -e "${CYAN}📊 Role Comparison Matrix:${NC}"
    echo
    
    printf "%-10s %-6s %-10s %-10s %-12s %-8s\n" "Role" "Level" "Sandbox" "uMemory" "uKnowledge" "System"
    printf "%-10s %-6s %-10s %-10s %-12s %-8s\n" "------" "-----" "-------" "--------" "----------" "------"
    
    for role in ghost tomb drone imp sorcerer wizard; do
        local emoji=$(get_role_emoji "$role")
        local level=$(get_role_level "$role")
        
        case "$role" in
            "wizard")
                printf "%s %-8s %-6s %-10s %-10s %-12s %-8s\n" "$emoji" "$role" "$level" "Full" "Full" "Full" "Dev"
                ;;
            "sorcerer")
                printf "%s %-8s %-6s %-10s %-10s %-12s %-8s\n" "$emoji" "$role" "$level" "Full" "Limited" "Read" "Read"
                ;;
            "imp")
                printf "%s %-8s %-6s %-10s %-10s %-12s %-8s\n" "$emoji" "$role" "$level" "Full" "User" "Read" "Read"
                ;;
            "drone")
                printf "%s %-8s %-6s %-10s %-10s %-12s %-8s\n" "$emoji" "$role" "$level" "Limited" "Read" "None" "Read"
                ;;
            "tomb")
                printf "%s %-8s %-6s %-10s %-10s %-12s %-8s\n" "$emoji" "$role" "$level" "Archive" "Archive" "Historical" "None"
                ;;
            "ghost")
                printf "%s %-8s %-6s %-10s %-10s %-12s %-8s\n" "$emoji" "$role" "$level" "Demo" "None" "None" "None"
                ;;
        esac
    done
    echo
}

# Function to check system status
check_system_status() {
    echo -e "${CYAN}🔍 System Status Check:${NC}"
    echo
    
    # Check core directories
    echo -e "${BLUE}Core Directories:${NC}"
    for dir in uCORE uMEMORY uKNOWLEDGE uSCRIPT sandbox; do
        if [ -d "/Users/agentdigital/uDOS/$dir" ]; then
            echo -e "  ✅ $dir"
        else
            echo -e "  ❌ $dir (missing)"
        fi
    done
    
    echo
    echo -e "${BLUE}Installation Structure:${NC}"
    if [ -d "$INSTALL_DIR" ]; then
        echo -e "  ✅ installations/ directory exists"
        local count=$(find "$INSTALL_DIR" -maxdepth 1 -type d -o -type l | wc -l)
        echo -e "  📊 Found $((count-1)) installations"
    else
        echo -e "  ❌ installations/ directory missing"
    fi
    
    echo
    echo -e "${BLUE}Shared Resources:${NC}"
    if [ -d "$SHARED_DIR" ]; then
        echo -e "  ✅ shared/ directory exists"
        for subdir in permissions configs resources; do
            if [ -d "$SHARED_DIR/$subdir" ]; then
                echo -e "  ✅ shared/$subdir"
            else
                echo -e "  ❌ shared/$subdir (missing)"
            fi
        done
    else
        echo -e "  ❌ shared/ directory missing"
    fi
    echo
}

# Main function
main() {
    show_header
    
    case "${1:-help}" in
        "list"|"ls")
            list_installations
            ;;
        "details"|"info")
            show_installation_details "$2"
            ;;
        "permissions"|"perms")
            if [ -n "$2" ]; then
                validate_permissions "$2"
            else
                echo -e "${YELLOW}Usage: $0 permissions <role>${NC}"
                echo -e "Available roles: ${ROLE_NAMES[*]}"
            fi
            ;;
        "create"|"install")
            if [ -n "$2" ]; then
                create_installation "$2"
            else
                echo -e "${YELLOW}Usage: $0 create <role>${NC}"
                echo -e "Available roles: ${ROLE_NAMES[*]}"
            fi
            ;;
        "compare"|"matrix")
            show_role_comparison
            ;;
        "status"|"check")
            check_system_status
            ;;
        "help"|"-h"|"--help")
            echo -e "${YELLOW}📖 Usage: $0 <command> [options]${NC}"
            echo
            echo -e "${CYAN}Commands:${NC}"
            echo -e "  list, ls              - List all installations"
            echo -e "  details <role>        - Show installation details"
            echo -e "  permissions <role>    - Validate role permissions"
            echo -e "  create <role>         - Create missing installation"
            echo -e "  compare, matrix       - Show role comparison matrix"
            echo -e "  status, check         - Check system status"
            echo -e "  help                  - Show this help message"
            echo
            echo -e "${CYAN}Available Roles:${NC}"
            for i in "${!ROLE_NAMES[@]}"; do
                local role="${ROLE_NAMES[$i]}"
                local emoji="${ROLE_EMOJIS[$i]}"
                local level="${ROLE_LEVELS[$i]}"
                echo -e "  $emoji $role (Level $level)"
            done
            echo
            ;;
        *)
            echo -e "${RED}❌ Unknown command: $1${NC}"
            echo -e "Run '$0 help' for usage information"
            exit 1
            ;;
    esac
}

# Run main function with all arguments
main "$@"
