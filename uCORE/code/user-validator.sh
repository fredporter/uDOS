#!/bin/bash

# uDOS User Validation System
# Validates sandbox/user.md format and triggers setup if needed

set -euo pipefail

# Get script directory and uDOS root
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
UDOS_ROOT="$(cd "$SCRIPT_DIR/../.." && pwd)"

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

# User file path
USER_FILE="$UDOS_ROOT/sandbox/user.md"

# Validate user.md format
validate_user_file() {
    local file="$1"
    
    if [[ ! -f "$file" ]]; then
        echo -e "${RED}❌ User file missing: $file${NC}"
        return 1
    fi
    
    # Check required fields in key=value format
    local required_fields=("USERNAME" "PASSWORD" "ROLE" "TIMEZONE" "LOCATION")
    local missing_fields=()
    
    for field in "${required_fields[@]}"; do
        if ! grep -q "^${field}=" "$file"; then
            missing_fields+=("$field")
        fi
    done
    
    if [[ ${#missing_fields[@]} -gt 0 ]]; then
        echo -e "${RED}❌ Missing required fields: ${missing_fields[*]}${NC}"
        return 1
    fi
    
    echo -e "${GREEN}✅ User file format valid${NC}"
    return 0
}

# Extract user data
get_user_data() {
    local file="$1"
    local field="$2"
    
    grep "^${field}=" "$file" 2>/dev/null | cut -d'=' -f2 || echo ""
}

# Check password authentication
check_password() {
    local user_file="$1"
    local password
    password=$(get_user_data "$user_file" "PASSWORD")
    
    # If password is empty, skip authentication
    if [[ -z "$password" || "$password" == "(blank)" ]]; then
        echo -e "${YELLOW}⚠️  Authentication skipped (no password set)${NC}"
        return 0
    fi
    
    # In interactive mode, prompt for password
    if [[ -t 0 ]]; then
        echo -n "🔐 Enter password: "
        read -s input_password
        echo
        
        if [[ "$input_password" == "$password" ]]; then
            echo -e "${GREEN}✅ Authentication successful${NC}"
            return 0
        else
            echo -e "${RED}❌ Authentication failed${NC}"
            return 1
        fi
    else
        # Non-interactive mode - skip password check
        echo -e "${YELLOW}⚠️  Non-interactive mode - password check skipped${NC}"
        return 0
    fi
}

# Trigger user setup story
trigger_user_setup() {
    echo -e "${BLUE}🚀 Triggering user setup story...${NC}"
    
    # Check if command router exists
    local router="$UDOS_ROOT/uCORE/code/command-router.sh"
    if [[ -f "$router" && -x "$router" ]]; then
        "$router" "[STORY|RUN*user-setup]"
    else
        echo -e "${YELLOW}⚠️  Command router not available - manual setup required${NC}"
        show_manual_setup
    fi
}

# Show manual setup instructions
show_manual_setup() {
    echo ""
    echo "📝 Manual User Setup Required"
    echo "════════════════════════════════════════════════════════════"
    echo ""
    echo "Create/edit: $USER_FILE"
    echo ""
    echo "Required format:"
    echo "USERNAME=your-username"
    echo "PASSWORD=your-password-or-blank"  
    echo "ROLE=KNIGHT"
    echo "TIMEZONE=America/New_York"
    echo "LOCATION=your-unique-location-name"
    echo ""
    echo "Available Roles:"
    echo "  GHOST (10), TOMB (20), CRYPT (30), DRONE (40)"
    echo "  KNIGHT (50), IMP (60), SORCERER (80), WIZARD (100)"
    echo ""
}

# Show user info
show_user_info() {
    local file="$1"
    
    echo "👤 uDOS User Information"
    echo "════════════════════════════════════════════════════════════"
    echo "Username:  $(get_user_data "$file" "USERNAME")"
    echo "Role:      $(get_user_data "$file" "ROLE")"
    echo "Timezone:  $(get_user_data "$file" "TIMEZONE")"
    echo "Location:  $(get_user_data "$file" "LOCATION")"
    
    local password
    password=$(get_user_data "$file" "PASSWORD")
    if [[ -n "$password" && "$password" != "(blank)" ]]; then
        echo "Password:  *** (set)"
    else
        echo "Password:  (not set)"
    fi
    echo ""
}

# Main function
main() {
    local action="${1:-validate}"
    
    case "$action" in
        "validate")
            echo "🔍 Validating user configuration..."
            if validate_user_file "$USER_FILE"; then
                show_user_info "$USER_FILE"
                return 0
            else
                echo ""
                echo "🚨 User configuration invalid or missing"
                trigger_user_setup
                return 1
            fi
            ;;
        "auth")
            echo "🔐 Checking authentication..."
            if validate_user_file "$USER_FILE"; then
                check_password "$USER_FILE"
            else
                echo "❌ Cannot authenticate - user file invalid"
                return 1
            fi
            ;;
        "setup")
            trigger_user_setup
            ;;
        "info")
            if validate_user_file "$USER_FILE"; then
                show_user_info "$USER_FILE"
            else
                echo "❌ User file invalid or missing"
                return 1
            fi
            ;;
        "help")
            echo "uDOS User Validation System"
            echo ""
            echo "Usage: $0 [action]"
            echo ""
            echo "Actions:"
            echo "  validate  - Validate user.md format (default)"
            echo "  auth      - Check password authentication"
            echo "  setup     - Trigger user setup story"
            echo "  info      - Show user information"
            echo "  help      - Show this help"
            ;;
        *)
            echo "❌ Unknown action: $action"
            echo "Use '$0 help' for available actions"
            return 1
            ;;
    esac
}

# Run main function
main "$@"
