#!/bin/bash
# uDOS Timezone & Location Module v1.3
# Manages timezone, location settings, and user preferences

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
NC='\033[0m'

# Get system timezone
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

# Get timezone city name
get_timezone_city() {
    local tz="$1"
    if [[ -n "$tz" && "$tz" =~ / ]]; then
        echo "$tz" | cut -d'/' -f2 | tr '_' ' '
    else
        echo "Unknown"
    fi
}

# Detect user location and timezone
detect_location() {
    echo -e "${BLUE}🌍 Detecting Location and Timezone${NC}"
    echo ""
    
    local timezone=$(get_system_timezone)
    local city=$(get_timezone_city "$timezone")
    local current_time=$(date "+%Y-%m-%d %H:%M:%S %Z")
    
    echo "System Timezone: $timezone"
    echo "Default City: $city"
    echo "Current Time: $current_time"
    
    # Return values for use in setup
    echo "DETECTED_TIMEZONE=$timezone"
    echo "DETECTED_CITY=$city"
    echo "CURRENT_TIME=$current_time"
}

# Set custom location name
set_custom_location() {
    local location_name="$1"
    local user_file="$SANDBOX/user.md"
    
    if [[ -z "$location_name" ]]; then
        echo -e "${RED}❌ Location name cannot be blank${NC}"
        return 1
    fi
    
    if [[ ! -f "$user_file" ]]; then
        echo -e "${RED}❌ User file not found${NC}"
        return 1
    fi
    
    # Update or add location in user.md
    if grep -q "^Location Name:" "$user_file"; then
        sed -i.bak "s/^Location Name:.*/Location Name: $location_name/" "$user_file"
    else
        # Add location after the user profile section
        if grep -q "## User Profile" "$user_file"; then
            sed -i.bak "/## User Profile/a\\
Location Name: $location_name" "$user_file"
        else
            echo "Location Name: $location_name" >> "$user_file"
        fi
    fi
    
    rm -f "$user_file.bak" 2>/dev/null
    echo -e "${GREEN}✅ Location set to: $location_name${NC}"
}

# Update timezone information in user.md
update_user_timezone() {
    local user_file="$SANDBOX/user.md"
    local timezone=$(get_system_timezone)
    local city=$(get_timezone_city "$timezone")
    local current_time=$(date "+%Y-%m-%d %H:%M:%S %Z")
    
    if [[ ! -f "$user_file" ]]; then
        echo -e "${RED}❌ User file not found${NC}"
        return 1
    fi
    
    # Update timezone information
    if grep -q "^Timezone:" "$user_file"; then
        sed -i.bak "s/^Timezone:.*/Timezone: $timezone/" "$user_file"
    else
        echo "Timezone: $timezone" >> "$user_file"
    fi
    
    # Set default location if not already set
    if ! grep -q "^Location Name:" "$user_file"; then
        set_custom_location "$city"
    fi
    
    # Update last timezone check
    if grep -q "^Last Timezone Check:" "$user_file"; then
        sed -i.bak "s/^Last Timezone Check:.*/Last Timezone Check: $current_time/" "$user_file"
    else
        echo "Last Timezone Check: $current_time" >> "$user_file"
    fi
    
    rm -f "$user_file.bak" 2>/dev/null
    echo -e "${GREEN}✅ Timezone information updated${NC}"
}

# Interactive location setup
interactive_location_setup() {
    local user_file="$SANDBOX/user.md"
    local timezone=$(get_system_timezone)
    local default_city=$(get_timezone_city "$timezone")
    
    echo -e "${BLUE}📍 Location Setup${NC}"
    echo ""
    echo "Detected timezone: $timezone"
    echo "Default city: $default_city"
    echo ""
    
    echo -e "${YELLOW}Enter your custom location name${NC}"
    echo -e "${CYAN}(Press Enter to use '$default_city'):${NC} "
    read -r custom_location
    
    if [[ -z "$custom_location" ]]; then
        custom_location="$default_city"
    fi
    
    set_custom_location "$custom_location"
    update_user_timezone
    
    echo ""
    echo -e "${GREEN}✅ Location setup complete!${NC}"
    echo "Location: $custom_location"
    echo "Timezone: $timezone"
}

# Show current location and timezone info
show_location_info() {
    local user_file="$SANDBOX/user.md"
    
    echo -e "${BLUE}📍 Location & Timezone Information${NC}"
    echo ""
    
    # System information
    local timezone=$(get_system_timezone)
    local current_time=$(date "+%Y-%m-%d %H:%M:%S %Z")
    
    echo -e "${CYAN}System Information:${NC}"
    echo "Current Time: $current_time"
    echo "System Timezone: $timezone"
    echo ""
    
    # User settings
    if [[ -f "$user_file" ]]; then
        echo -e "${CYAN}User Settings:${NC}"
        
        local user_location=$(grep "^Location Name:" "$user_file" 2>/dev/null | cut -d':' -f2- | sed 's/^ *//')
        local user_timezone=$(grep "^Timezone:" "$user_file" 2>/dev/null | cut -d':' -f2- | sed 's/^ *//')
        local last_check=$(grep "^Last Timezone Check:" "$user_file" 2>/dev/null | cut -d':' -f2- | sed 's/^ *//')
        
        echo "Location Name: ${user_location:-'Not set'}"
        echo "Saved Timezone: ${user_timezone:-'Not set'}"
        echo "Last Check: ${last_check:-'Never'}"
    else
        echo -e "${YELLOW}No user location settings found${NC}"
    fi
}

# Check if timezone has changed since last check
check_timezone_changes() {
    local user_file="$SANDBOX/user.md"
    local current_timezone=$(get_system_timezone)
    
    if [[ -f "$user_file" ]]; then
        local saved_timezone=$(grep "^Timezone:" "$user_file" 2>/dev/null | cut -d':' -f2- | sed 's/^ *//')
        
        if [[ -n "$saved_timezone" && "$saved_timezone" != "$current_timezone" ]]; then
            echo -e "${YELLOW}⚠️ Timezone change detected!${NC}"
            echo "Previous: $saved_timezone"
            echo "Current: $current_timezone"
            echo ""
            echo "Updating timezone information..."
            update_user_timezone
            return 1
        fi
    fi
    
    return 0
}

# Startup timezone check (called during system startup)
startup_timezone_check() {
    echo -e "${BLUE}🕐 Startup Timezone Check${NC}"
    
    # Always update timezone on startup
    update_user_timezone
    
    # Check for changes
    if ! check_timezone_changes; then
        echo -e "${GREEN}✅ Timezone updated for system startup${NC}"
    else
        echo -e "${GREEN}✅ Timezone verified${NC}"
    fi
}

# Main timezone function
timezone_main() {
    local action="${1:-info}"
    local param="${2:-}"
    
    case "$action" in
        "info"|"show")
            show_location_info
            ;;
        "detect")
            detect_location
            ;;
        "setup")
            interactive_location_setup
            ;;
        "set")
            if [[ -n "$param" ]]; then
                set_custom_location "$param"
            else
                echo -e "${RED}Usage: timezone set <location_name>${NC}"
            fi
            ;;
        "update")
            update_user_timezone
            ;;
        "check")
            check_timezone_changes && echo -e "${GREEN}✅ No timezone changes${NC}"
            ;;
        "startup")
            startup_timezone_check
            ;;
        *)
            echo "Timezone module - Available actions: info, detect, setup, set <name>, update, check, startup"
            ;;
    esac
}

# Export main function
if [[ "${BASH_SOURCE[0]}" == "${0}" ]]; then
    timezone_main "$@"
fi
