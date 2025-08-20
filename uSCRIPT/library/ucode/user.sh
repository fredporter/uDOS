#!/bin/bash
# uDOS User Module v1.3
# User management interface for authentication system

# Get uDOS paths
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
UDOS_ROOT="$(cd "$SCRIPT_DIR/../../.." && pwd)"
UCORE="$UDOS_ROOT/uCORE"
SANDBOX="$UDOS_ROOT/sandbox"

# Colors
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

# Source the authentication module
AUTH_MODULE="$UCORE/code/user-auth.sh"
if [[ -f "$AUTH_MODULE" ]]; then
    source "$AUTH_MODULE"
else
    echo -e "${RED}Error: Authentication module not found at: $AUTH_MODULE${NC}"
    echo "Expected location: $UCORE/code/user-auth.sh"
    exit 1
fi

show_user_info() {
    echo -e "${BLUE}👤 User Information${NC}"
    echo ""
    
    if [[ -f "$SANDBOX/user.md" ]]; then
        echo -e "${GREEN}User data found${NC}"
        echo ""
        
        # Extract and display user information (excluding sensitive data)
        local username=$(grep "^Username:" "$SANDBOX/user.md" 2>/dev/null | cut -d' ' -f2-)
        local email=$(grep "^Email:" "$SANDBOX/user.md" 2>/dev/null | cut -d' ' -f2-)
        local created=$(grep "^Account Created:" "$SANDBOX/user.md" 2>/dev/null | cut -d' ' -f3-)
        local last_login=$(grep "^Last Login:" "$SANDBOX/user.md" 2>/dev/null | cut -d' ' -f3-)
        
        echo "Username: ${username:-'Not set'}"
        echo "Email: ${email:-'Not set'}"
        echo "Account Created: ${created:-'Unknown'}"
        echo "Last Login: ${last_login:-'Never'}"
        
        # Show profile information if available
        if grep -q "## User Profile" "$SANDBOX/user.md" 2>/dev/null; then
            echo ""
            echo -e "${BLUE}Profile Information:${NC}"
            sed -n '/## User Profile/,/## /p' "$SANDBOX/user.md" | head -n -1 | tail -n +2
        fi
    else
        echo -e "${RED}No user data found${NC}"
        echo "Run 'user setup' to create a user account"
    fi
}

show_user_profile() {
    echo -e "${BLUE}👤 User Profile${NC}"
    echo ""
    
    if [[ -f "$SANDBOX/user.md" ]]; then
        # Show full profile section
        if grep -q "## User Profile" "$SANDBOX/user.md" 2>/dev/null; then
            sed -n '/## User Profile/,/## /p' "$SANDBOX/user.md" | head -n -1 | tail -n +1
        else
            echo "No profile information available"
        fi
        
        # Show adventurer profile if available
        if grep -q "## Adventurer Profile" "$SANDBOX/user.md" 2>/dev/null; then
            echo ""
            sed -n '/## Adventurer Profile/,/## /p' "$SANDBOX/user.md" | head -n -1 | tail -n +1
        fi
    else
        echo -e "${RED}No user data found${NC}"
    fi
}

handle_user_login() {
    echo -e "${BLUE}🔐 User Authentication${NC}"
    echo ""
    
    if authenticate; then
        echo -e "${GREEN}Authentication successful!${NC}"
        
        # Update last login time
        if [[ -f "$SANDBOX/user.md" ]]; then
            local current_time=$(date "+%Y-%m-%d %H:%M:%S")
            if grep -q "^Last Login:" "$SANDBOX/user.md"; then
                sed -i.bak "s/^Last Login:.*/Last Login: $current_time/" "$SANDBOX/user.md"
            else
                echo "Last Login: $current_time" >> "$SANDBOX/user.md"
            fi
            rm -f "$SANDBOX/user.md.bak" 2>/dev/null
        fi
    else
        echo -e "${RED}Authentication failed${NC}"
        return 1
    fi
}

handle_user_setup() {
    echo -e "${BLUE}⚙️ User Setup${NC}"
    echo ""
    
    if [[ -f "$SANDBOX/user.md" ]]; then
        echo -e "${YELLOW}User data already exists${NC}"
        echo "Use 'user change-password' to update password"
        echo "Use 'user info' to view current information"
        return 0
    fi
    
    echo "Setting up new user account..."
    echo ""
    
    # Use the authentication module's create_user_file function
    if create_user_file; then
        echo ""
        echo -e "${GREEN}User setup completed successfully!${NC}"
        echo "Your account has been created and secured."
    else
        echo ""
        echo -e "${RED}User setup failed${NC}"
        return 1
    fi
}

handle_change_password() {
    echo -e "${BLUE}🔑 Change Password${NC}"
    echo ""
    
    if [[ ! -f "$SANDBOX/user.md" ]]; then
        echo -e "${RED}No user account found${NC}"
        echo "Run 'user setup' first"
        return 1
    fi
    
    # Use the authentication module's change_password function
    if change_password; then
        echo -e "${GREEN}Password changed successfully!${NC}"
    else
        echo -e "${RED}Password change failed${NC}"
        return 1
    fi
}

show_security_status() {
    echo -e "${BLUE}🔒 Security Status${NC}"
    echo ""
    
    if [[ -f "$SANDBOX/user.md" ]]; then
        echo -e "${GREEN}✓ User account exists${NC}"
        
        # Check for password hash
        if grep -q "^Password Hash:" "$SANDBOX/user.md" 2>/dev/null; then
            echo -e "${GREEN}✓ Password protection enabled${NC}"
        else
            echo -e "${RED}✗ No password protection${NC}"
        fi
        
        # Check file permissions
        local perms=$(ls -la "$SANDBOX/user.md" | awk '{print $1}')
        echo "File permissions: $perms"
        
        # Check for recent activity
        local last_modified=$(stat -f "%Sm" -t "%Y-%m-%d %H:%M:%S" "$SANDBOX/user.md" 2>/dev/null)
        echo "Last modified: $last_modified"
    else
        echo -e "${RED}✗ No user account${NC}"
        echo "Security status: Unprotected"
    fi
}

# Main function
user_main() {
    local action="${1:-info}"
    
    case "$action" in
        "info")
            show_user_info
            ;;
        "profile")
            show_user_profile
            ;;
        "login")
            handle_user_login
            ;;
        "setup")
            handle_user_setup
            ;;
        "change-password")
            handle_change_password
            ;;
        "security")
            show_security_status
            ;;
        *)
            echo "User module - Available actions: info, profile, login, setup, change-password, security"
            ;;
    esac
}

# Export main function
if [[ "${BASH_SOURCE[0]}" == "${0}" ]]; then
    user_main "$@"
fi
