#!/bin/bash
# list-command.sh - Role-based LIST command for uDOS
# Version: 2.0.0
# Description: Shows folders based on user role permissions

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
UHOME="${UHOME:-$HOME/uDOS}"
ROLE_MANAGER="$SCRIPT_DIR/user-role-manager.sh"

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

# Get current user role
get_user_role() {
    if [[ -f "$ROLE_MANAGER" ]]; then
        bash "$ROLE_MANAGER" status 2>/dev/null | grep "Role:" | awk '{print $2}' | sed 's/(.*//'
    else
        echo "user"
    fi
}

# Check if user has access to folder
check_folder_access() {
    local folder="$1"
    
    if [[ -f "$ROLE_MANAGER" ]]; then
        bash "$ROLE_MANAGER" check "$folder" read >/dev/null 2>&1
        return $?
    else
        # Fallback - assume basic access
        case "$folder" in
            "sandbox") return 0 ;;
            "uMemory"|"uKnowledge") return 1 ;;
            *) return 1 ;;
        esac
    fi
}

# Get folder access level description
get_access_description() {
    local folder="$1"
    local role="$2"
    
    if [[ -f "$ROLE_MANAGER" ]] && [[ -f "$UHOME/uTemplate/datasets/user-roles.json" ]] && command -v jq >/dev/null 2>&1; then
        jq -r ".[] | select(.role == \"$role\") | .folder_access.$folder // \"none\"" "$UHOME/uTemplate/datasets/user-roles.json" 2>/dev/null
    else
        echo "unknown"
    fi
}

# Show folder with role-based information
show_folder_info() {
    local folder="$1"
    local path="$UHOME/$folder"
    local current_role=$(get_user_role)
    local access_level=$(get_access_description "$folder" "$current_role")
    
    # Check if folder exists
    if [[ -d "$path" ]]; then
        local item_count=$(find "$path" -maxdepth 1 -type f | wc -l | tr -d ' ')
        local dir_count=$(find "$path" -maxdepth 1 -type d | wc -l | tr -d ' ')
        ((dir_count--))  # Subtract the directory itself
        
        # Access level indicators and colors
        case "$access_level" in
            "full")
                echo -e "  🟢 ${GREEN}${BOLD}$folder${NC} ${GREEN}(full access)${NC}"
                echo -e "      📁 $dir_count directories, 📄 $item_count files"
                ;;
            "read_only")
                echo -e "  🔵 ${BLUE}${BOLD}$folder${NC} ${BLUE}(read only)${NC}"
                echo -e "      📁 $dir_count directories, 📄 $item_count files"
                ;;
            "read_write_limited"|"read_write_user")
                echo -e "  🟡 ${YELLOW}${BOLD}$folder${NC} ${YELLOW}(limited access)${NC}"
                echo -e "      📁 $dir_count directories, 📄 $item_count files"
                ;;
            "conditional_dev")
                local dev_status="disabled"
                if [[ -f "$ROLE_MANAGER" ]]; then
                    local status_output=$(bash "$ROLE_MANAGER" status 2>/dev/null | tr -d '\r' || echo "")
                    if echo "$status_output" | grep -i "dev mode.*enabled" >/dev/null 2>&1; then
                        dev_status="enabled"
                    fi
                fi
                
                if [[ "$dev_status" == "enabled" ]]; then
                    echo -e "  🟠 ${YELLOW}${BOLD}$folder${NC} ${YELLOW}(dev mode - write access)${NC}"
                else
                    echo -e "  🔵 ${BLUE}${BOLD}$folder${NC} ${BLUE}(dev mode disabled - read only)${NC}"
                fi
                echo -e "      📁 $dir_count directories, 📄 $item_count files"
                ;;
            "personal_only")
                echo -e "  🟣 ${PURPLE}${BOLD}$folder${NC} ${PURPLE}(personal workspace)${NC}"
                echo -e "      📁 $dir_count directories, 📄 $item_count files"
                ;;
            "demo_only")
                echo -e "  🟣 ${PURPLE}${BOLD}$folder${NC} ${PURPLE}(demo access)${NC}"
                echo -e "      📁 $dir_count directories, 📄 $item_count files"
                ;;
            "none")
                echo -e "  🔴 ${RED}${BOLD}$folder${NC} ${RED}(no access)${NC}"
                echo -e "      🚫 Access denied"
                return 0
                ;;
            *)
                echo -e "  ⚪ ${CYAN}${BOLD}$folder${NC} ${CYAN}($access_level)${NC}"
                echo -e "      📁 $dir_count directories, 📄 $item_count files"
                ;;
        esac
        
        # Show path
        echo -e "      📍 $path"
        
        # Show recent activity if accessible
        if check_folder_access "$folder"; then
            local recent_file=$(find "$path" -type f -name "*.md" -o -name "*.json" -o -name "*.txt" 2>/dev/null | head -1)
            if [[ -n "$recent_file" ]]; then
                local file_date=$(stat -f "%Sm" -t "%Y-%m-%d %H:%M" "$recent_file" 2>/dev/null || echo "unknown")
                echo -e "      🕒 Recent activity: $(basename "$recent_file") ($file_date)"
            fi
        fi
        
    else
        echo -e "  ❌ ${RED}${BOLD}$folder${NC} ${RED}(not found)${NC}"
        echo -e "      📍 Expected at: $path"
    fi
}

# Show default sandbox structure
show_sandbox_default() {
    local sandbox_path="$UHOME/sandbox"
    local current_role=$(get_user_role)
    
    echo -e "${BOLD}${CYAN}📦 Default Sandbox Structure${NC}"
    echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
    echo ""
    
    if [[ -d "$sandbox_path" ]]; then
        echo -e "📍 ${GREEN}Sandbox Location:${NC} $sandbox_path"
        echo -e "👤 ${BLUE}Your Role:${NC} $current_role"
        echo ""
        
        # Show sandbox contents with role-based access indicators
        if check_folder_access "sandbox"; then
            echo -e "${PURPLE}📂 Sandbox Contents:${NC}"
            
            # Create default structure if it doesn't exist
            mkdir -p "$sandbox_path"/{today,sessions,drafts,research,temp}
            
            local folders=("today" "sessions" "drafts" "research" "temp")
            for folder in "${folders[@]}"; do
                local folder_path="$sandbox_path/$folder"
                if [[ -d "$folder_path" ]]; then
                    local count=$(find "$folder_path" -maxdepth 1 -type f | wc -l | tr -d ' ')
                    echo -e "  📁 ${GREEN}$folder${NC} ($count files)"
                else
                    echo -e "  📁 ${YELLOW}$folder${NC} (will be created)"
                fi
            done
            
            # Show today's workspace
            local today_dir="$sandbox_path/today/$(date +%Y-%m-%d)"
            if [[ -d "$today_dir" ]]; then
                local today_files=$(find "$today_dir" -type f | wc -l | tr -d ' ')
                echo ""
                echo -e "📅 ${CYAN}Today's Workspace:${NC} $(date +%Y-%m-%d)"
                echo -e "   📂 $today_files files in today's workspace"
            else
                echo ""
                echo -e "📅 ${YELLOW}Today's Workspace:${NC} Not yet created"
                echo -e "   💡 Use: [TODAY:notes] or CREATE command to start"
            fi
            
        else
            echo -e "${RED}🚫 Access denied to sandbox${NC}"
        fi
    else
        echo -e "${RED}❌ Sandbox not found: $sandbox_path${NC}"
        echo -e "💡 Initialize with: ucode SETUP or [SANDBOX:init]"
    fi
}

# Show advanced folder listing
show_advanced_listing() {
    local current_role=$(get_user_role)
    
    echo -e "${BOLD}${PURPLE}📋 uDOS Folder Structure (Role: $current_role)${NC}"
    echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
    echo ""
    
    # Core folders that all roles see
    local core_folders=("sandbox")
    echo -e "${CYAN}🏠 Core Workspace:${NC}"
    for folder in "${core_folders[@]}"; do
        show_folder_info "$folder"
        echo ""
    done
    
    # Role-dependent folders
    local system_folders=("uMemory" "uKnowledge")
    echo -e "${CYAN}🧠 Memory & Knowledge:${NC}"
    for folder in "${system_folders[@]}"; do
        if check_folder_access "$folder" || [[ "$current_role" == "wizard" ]] || [[ "$current_role" == "admin" ]]; then
            show_folder_info "$folder"
        else
            echo -e "  🔴 ${RED}${BOLD}$folder${NC} ${RED}(no access for role: $current_role)${NC}"
        fi
        echo ""
    done
    
    # System folders (wizard/dev only)
    if [[ "$current_role" == "wizard" ]] || [[ "$current_role" == "admin" ]] || [[ "$current_role" == "developer" ]]; then
        local dev_folders=("uTemplate" "uCode" "uScript")
        echo -e "${CYAN}⚙️ System & Development:${NC}"
        for folder in "${dev_folders[@]}"; do
            show_folder_info "$folder"
            echo ""
        done
    fi
    
    # Additional folders
    local misc_folders=("docs" "package" "extension")
    echo -e "${CYAN}📚 Documentation & Extensions:${NC}"
    for folder in "${misc_folders[@]}"; do
        if [[ -d "$UHOME/$folder" ]]; then
            if [[ "$current_role" == "wizard" ]] || check_folder_access "$folder"; then
                show_folder_info "$folder"
            else
                echo -e "  🔴 ${RED}${BOLD}$folder${NC} ${RED}(no access)${NC}"
                echo -e "      🚫 Access denied"
            fi
            echo ""
        fi
    done
    
    # Role summary
    echo -e "${PURPLE}📊 Access Summary:${NC}"
    if [[ -f "$ROLE_MANAGER" ]]; then
        local accessible_count=0
        local total_folders=("sandbox" "uMemory" "uKnowledge" "uTemplate" "uCode" "uScript" "docs" "package" "extension")
        
        for folder in "${total_folders[@]}"; do
            if check_folder_access "$folder" || ([[ "$current_role" == "wizard" ]] && [[ "$folder" == "package" || "$folder" == "extension" ]]); then
                ((accessible_count++))
            fi
        done
        
        echo -e "  🟢 Accessible folders: $accessible_count/${#total_folders[@]}"
        echo -e "  👤 Current role: $current_role"
        
        # Dev mode status for wizard
        if [[ "$current_role" == "wizard" ]]; then
            local dev_status=$(bash "$ROLE_MANAGER" status 2>/dev/null | grep "Dev Mode:" | awk '{print $3}')
            echo -e "  🔧 Dev mode: $dev_status"
        fi
    fi
}

# Show quick summary
show_quick_summary() {
    local current_role=$(get_user_role)
    
    echo -e "${BOLD}${CYAN}📋 Quick Folder Summary${NC}"
    echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
    echo -e "👤 Role: ${GREEN}$current_role${NC}"
    echo ""
    
    # Show accessible folders in compact format
    local folders=("sandbox" "uMemory" "uKnowledge" "uTemplate" "uCode" "uScript")
    for folder in "${folders[@]}"; do
        if check_folder_access "$folder"; then
            local access_level=$(get_access_description "$folder" "$current_role")
            case "$access_level" in
                "full") echo -e "🟢 $folder (full)" ;;
                "read_only") echo -e "🔵 $folder (read)" ;;
                "conditional_dev") echo -e "🟠 $folder (dev)" ;;
                *) echo -e "🟡 $folder ($access_level)" ;;
            esac
        fi
    done
}

# Main function
main() {
    case "${1:-default}" in
        "sandbox"|"default")
            show_sandbox_default
            ;;
        "all"|"full"|"advanced")
            show_advanced_listing
            ;;
        "quick"|"summary")
            show_quick_summary
            ;;
        "permissions"|"access")
            if [[ -f "$ROLE_MANAGER" ]]; then
                bash "$ROLE_MANAGER" folders
            else
                error "Role manager not available"
            fi
            ;;
        "role")
            if [[ -f "$ROLE_MANAGER" ]]; then
                bash "$ROLE_MANAGER" status
            else
                error "Role manager not available"
            fi
            ;;
        "validate")
            log "Validating folder access and permissions"
            local current_role=$(get_user_role)
            echo "Current role: $current_role"
            
            local test_folders=("sandbox" "uMemory" "uKnowledge")
            for folder in "${test_folders[@]}"; do
                if check_folder_access "$folder"; then
                    success "Access granted to $folder"
                else
                    warning "Access denied to $folder"
                fi
            done
            ;;
        "help"|*)
            echo -e "${PURPLE}📋 LIST Command v2.0${NC}"
            echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
            echo ""
            echo "Role-based folder listing for uDOS"
            echo ""
            echo "Usage: $0 [command]"
            echo ""
            echo "Commands:"
            echo "  default/sandbox    - Show default sandbox structure"
            echo "  all/full/advanced  - Show complete folder structure (role-based)"
            echo "  quick/summary      - Show compact folder summary"
            echo "  permissions/access - Show detailed access permissions"
            echo "  role              - Show current user role and status"
            echo "  validate          - Validate folder access"
            echo ""
            echo "Examples:"
            echo "  $0                    # Show sandbox (default)"
            echo "  $0 all                # Show all accessible folders"
            echo "  $0 permissions        # Show role-based permissions"
            echo ""
            echo "Role Integration:"
            echo "  • Folders shown based on your current role"
            echo "  • Access levels indicated with color coding"
            echo "  • Dev mode status affects system folder access"
            ;;
    esac
}

# Initialize if called directly
if [[ "${BASH_SOURCE[0]}" == "${0}" ]]; then
    main "$@"
fi
