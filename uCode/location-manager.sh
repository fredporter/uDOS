#!/bin/bash
# location-manager.sh - Location and Grid Context Management
# Manages location, timezone, and grid position while logging to uMemory
# Version: 2.0.0

set -euo pipefail

# Environment Setup
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
UHOME="${UHOME:-$HOME/uDOS}"
UMEM="${UHOME}/uMemory"
SANDBOX="${UHOME}/sandbox"

# Location system files
LOCATION_CONFIG="${UMEM}/system/location-config.json"
GRID_STATE="${UMEM}/state/grid-position.json"
TIMEZONE_CONFIG="${UMEM}/system/timezone-config.json"
USER_LOCATION_PREFS="${SANDBOX}/user-data/location-preferences.json"

# Load display configuration if available
DISPLAY_VARS="${UMEM}/config/display-vars.sh"
[[ -f "$DISPLAY_VARS" ]] && source "$DISPLAY_VARS" 2>/dev/null || true

# Color helpers
red() { echo -e "\033[0;31m$1\033[0m"; }
green() { echo -e "\033[0;32m$1\033[0m"; }
yellow() { echo -e "\033[0;33m$1\033[0m"; }
blue() { echo -e "\033[0;34m$1\033[0m"; }
cyan() { echo -e "\033[0;36m$1\033[0m"; }
bold() { echo -e "\033[1m$1\033[0m"; }

# Initialize location manager
init_location_manager() {
    bold "🗺️ Location Manager v2.0.0"
    echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
    echo
    
    # Create required directories
    mkdir -p "${UMEM}/system" "${UMEM}/state" "${SANDBOX}/user-data"
    
    # Initialize configuration files
    setup_location_config
    setup_grid_system
    setup_timezone_config
    
    # Load current state
    load_current_state
    
    green "✅ Location manager initialized"
    show_location_status
}

# Setup location configuration
setup_location_config() {
    cyan "📍 Setting up location configuration..."
    
    cat > "$LOCATION_CONFIG" << 'EOF'
{
  "location_system": {
    "version": "2.0.0",
    "default_location": "Unknown",
    "location_format": "city_country",
    "coordinate_system": "grid",
    "timezone_auto_detect": true
  },
  "supported_locations": [
    {
      "name": "Sydney",
      "country": "Australia",
      "timezone": "Australia/Sydney",
      "grid_region": "A1:Z99",
      "coordinates": {"lat": -33.8688, "lng": 151.2093}
    },
    {
      "name": "Melbourne",
      "country": "Australia", 
      "timezone": "Australia/Melbourne",
      "grid_region": "A1:Z99",
      "coordinates": {"lat": -37.8136, "lng": 144.9631}
    },
    {
      "name": "Brisbane",
      "country": "Australia",
      "timezone": "Australia/Brisbane", 
      "grid_region": "A1:Z99",
      "coordinates": {"lat": -27.4698, "lng": 153.0251}
    },
    {
      "name": "Perth",
      "country": "Australia",
      "timezone": "Australia/Perth",
      "grid_region": "A1:Z99", 
      "coordinates": {"lat": -31.9505, "lng": 115.8605}
    },
    {
      "name": "Auckland",
      "country": "New Zealand",
      "timezone": "Pacific/Auckland",
      "grid_region": "A1:Z99",
      "coordinates": {"lat": -36.8485, "lng": 174.7633}
    }
  ],
  "grid_mapping": {
    "cell_size_meters": 1000,
    "origin_point": "city_center",
    "coordinate_format": "alphanumeric"
  }
}
EOF
    
    echo "  📍 Location configuration created"
}

# Setup grid system
setup_grid_system() {
    cyan "🎯 Setting up grid system..."
    
    # Get grid configuration from display system
    local grid_mode="${UDOS_GRID_MODE:-standard}"
    local grid_cols="${UDOS_GRID_COLS_MAX:-26}"
    local grid_rows="${UDOS_GRID_ROWS_MAX:-99}"
    
    cat > "$GRID_STATE" << EOF
{
  "grid_system": {
    "version": "2.0.0",
    "mode": "$grid_mode",
    "max_columns": $grid_cols,
    "max_rows": $grid_rows,
    "current_position": "A1",
    "last_updated": "$(date -Iseconds)"
  },
  "position_history": [
    {
      "position": "A1",
      "timestamp": "$(date -Iseconds)",
      "action": "initialization"
    }
  ],
  "grid_preferences": {
    "auto_move": false,
    "highlight_current": true,
    "show_coordinates": true
  }
}
EOF
    
    echo "  🎯 Grid system configured ($grid_mode mode: ${grid_cols}x${grid_rows})"
}

# Setup timezone configuration
setup_timezone_config() {
    cyan "🕐 Setting up timezone configuration..."
    
    cat > "$TIMEZONE_CONFIG" << 'EOF'
{
  "timezone_system": {
    "version": "2.0.0",
    "current_timezone": "UTC",
    "auto_detect": true,
    "format": "ISO8601"
  },
  "supported_timezones": [
    "Australia/Sydney",
    "Australia/Melbourne", 
    "Australia/Brisbane",
    "Australia/Perth",
    "Australia/Adelaide",
    "Australia/Darwin",
    "Pacific/Auckland",
    "UTC",
    "America/New_York",
    "America/Los_Angeles",
    "Europe/London",
    "Europe/Paris",
    "Asia/Tokyo",
    "Asia/Shanghai"
  ],
  "timezone_mapping": {
    "AEDT": "Australia/Sydney",
    "AEST": "Australia/Brisbane", 
    "AWST": "Australia/Perth",
    "NZDT": "Pacific/Auckland",
    "UTC": "UTC",
    "GMT": "UTC"
  }
}
EOF
    
    echo "  🕐 Timezone configuration created"
}

# Load current state
load_current_state() {
    cyan "📊 Loading current state..."
    
    # Try to detect current timezone
    local current_tz="UTC"
    if command -v timedatectl >/dev/null 2>&1; then
        current_tz=$(timedatectl show --property=Timezone --value 2>/dev/null || echo "UTC")
    elif [[ -f /etc/timezone ]]; then
        current_tz=$(cat /etc/timezone)
    fi
    
    # Update timezone in config
    if command -v jq >/dev/null 2>&1; then
        jq ".timezone_system.current_timezone = \"$current_tz\"" "$TIMEZONE_CONFIG" > "${TIMEZONE_CONFIG}.tmp" && mv "${TIMEZONE_CONFIG}.tmp" "$TIMEZONE_CONFIG"
    fi
    
    echo "  🕐 Current timezone: $current_tz"
    echo "  🎯 Current grid position: $(get_current_grid_position)"
    echo "  📍 Current location: $(get_current_location)"
}

# Get current grid position
get_current_grid_position() {
    if [[ -f "$GRID_STATE" ]] && command -v jq >/dev/null 2>&1; then
        jq -r '.grid_system.current_position' "$GRID_STATE" 2>/dev/null || echo "A1"
    else
        echo "A1"
    fi
}

# Get current location
get_current_location() {
    if [[ -f "$LOCATION_CONFIG" ]] && command -v jq >/dev/null 2>&1; then
        jq -r '.location_system.default_location' "$LOCATION_CONFIG" 2>/dev/null || echo "Unknown"
    else
        echo "Unknown"
    fi
}

# Set location
set_location() {
    local new_location="$1"
    local update_timezone="${2:-true}"
    
    cyan "📍 Setting location to: $new_location"
    
    # Validate location
    local timezone=""
    if command -v jq >/dev/null 2>&1 && [[ -f "$LOCATION_CONFIG" ]]; then
        timezone=$(jq -r ".supported_locations[] | select(.name==\"$new_location\") | .timezone" "$LOCATION_CONFIG" 2>/dev/null || echo "")
    fi
    
    if [[ -z "$timezone" ]]; then
        yellow "⚠️ Location '$new_location' not in supported list, using as custom location"
        timezone="UTC"
    fi
    
    # Update location configuration
    if command -v jq >/dev/null 2>&1; then
        jq ".location_system.default_location = \"$new_location\"" "$LOCATION_CONFIG" > "${LOCATION_CONFIG}.tmp" && mv "${LOCATION_CONFIG}.tmp" "$LOCATION_CONFIG"
    fi
    
    # Update timezone if requested
    if [[ "$update_timezone" == "true" && -n "$timezone" ]]; then
        set_timezone "$timezone" false
    fi
    
    # Log to uMemory
    log_location_change "$new_location" "$timezone"
    
    echo "  📍 Location set to: $new_location"
    if [[ -n "$timezone" ]]; then
        echo "  🕐 Timezone: $timezone"
    fi
}

# Set timezone
set_timezone() {
    local new_timezone="$1"
    local update_system="${2:-false}"
    
    cyan "🕐 Setting timezone to: $new_timezone"
    
    # Validate timezone
    if ! echo "$new_timezone" | grep -E "^[A-Za-z_/]+$" >/dev/null; then
        red "❌ Invalid timezone format: $new_timezone"
        return 1
    fi
    
    # Update timezone configuration
    if command -v jq >/dev/null 2>&1; then
        jq ".timezone_system.current_timezone = \"$new_timezone\"" "$TIMEZONE_CONFIG" > "${TIMEZONE_CONFIG}.tmp" && mv "${TIMEZONE_CONFIG}.tmp" "$TIMEZONE_CONFIG"
    fi
    
    # Update system timezone if requested (requires admin)
    if [[ "$update_system" == "true" ]]; then
        yellow "⚠️ System timezone update requires admin privileges"
        if command -v timedatectl >/dev/null 2>&1; then
            echo "  Run: sudo timedatectl set-timezone $new_timezone"
        fi
    fi
    
    # Log to uMemory
    log_timezone_change "$new_timezone"
    
    echo "  🕐 Timezone set to: $new_timezone"
}

# Set grid position
set_grid_position() {
    local new_position="$1"
    
    cyan "🎯 Setting grid position to: $new_position"
    
    # Validate grid position format
    if ! echo "$new_position" | grep -E "^[A-Z]{1,2}[0-9]{1,2}$" >/dev/null; then
        red "❌ Invalid grid position format: $new_position (use format like A1, B5, AA12)"
        return 1
    fi
    
    # Check if position is within grid bounds
    local grid_cols="${UDOS_GRID_COLS_MAX:-26}"
    local grid_rows="${UDOS_GRID_ROWS_MAX:-99}"
    
    # Extract column and row
    local col_part=$(echo "$new_position" | sed 's/[0-9]*$//')
    local row_part=$(echo "$new_position" | sed 's/^[A-Z]*//')
    
    # Validate bounds (simplified check)
    if [[ ${#row_part} -gt 2 ]] || [[ $row_part -gt $grid_rows ]]; then
        red "❌ Grid position out of bounds: $new_position"
        return 1
    fi
    
    # Update grid state
    if command -v jq >/dev/null 2>&1; then
        # Add to position history
        local timestamp=$(date -Iseconds)
        jq ".grid_system.current_position = \"$new_position\" | 
            .grid_system.last_updated = \"$timestamp\" |
            .position_history += [{\"position\": \"$new_position\", \"timestamp\": \"$timestamp\", \"action\": \"manual_set\"}]" \
            "$GRID_STATE" > "${GRID_STATE}.tmp" && mv "${GRID_STATE}.tmp" "$GRID_STATE"
    fi
    
    # Log to uMemory
    log_grid_position_change "$new_position"
    
    echo "  🎯 Grid position set to: $new_position"
}

# Logging functions
log_location_change() {
    local location="$1"
    local timezone="$2"
    local timestamp=$(date -Iseconds)
    
    local log_entry="{
        \"timestamp\": \"$timestamp\",
        \"action\": \"location_change\",
        \"location\": \"$location\",
        \"timezone\": \"$timezone\",
        \"user\": \"$(whoami)\",
        \"source\": \"location_manager\"
    }"
    
    local log_file="${UMEM}/logs/location-changes.jsonl"
    mkdir -p "$(dirname "$log_file")"
    echo "$log_entry" >> "$log_file"
}

log_timezone_change() {
    local timezone="$1"
    local timestamp=$(date -Iseconds)
    
    local log_entry="{
        \"timestamp\": \"$timestamp\",
        \"action\": \"timezone_change\",
        \"timezone\": \"$timezone\",
        \"user\": \"$(whoami)\",
        \"source\": \"location_manager\"
    }"
    
    local log_file="${UMEM}/logs/timezone-changes.jsonl"
    mkdir -p "$(dirname "$log_file")"
    echo "$log_entry" >> "$log_file"
}

log_grid_position_change() {
    local position="$1"
    local timestamp=$(date -Iseconds)
    
    local log_entry="{
        \"timestamp\": \"$timestamp\",
        \"action\": \"grid_position_change\",
        \"position\": \"$position\",
        \"user\": \"$(whoami)\",
        \"source\": \"location_manager\"
    }"
    
    local log_file="${UMEM}/logs/grid-changes.jsonl"
    mkdir -p "$(dirname "$log_file")"
    echo "$log_entry" >> "$log_file"
}

# Show location status
show_location_status() {
    echo
    bold "📊 Location & Grid Status"
    echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
    
    local current_location=$(get_current_location)
    local current_position=$(get_current_grid_position)
    local current_timezone="UTC"
    
    if command -v jq >/dev/null 2>&1 && [[ -f "$TIMEZONE_CONFIG" ]]; then
        current_timezone=$(jq -r '.timezone_system.current_timezone' "$TIMEZONE_CONFIG" 2>/dev/null || echo "UTC")
    fi
    
    local current_time=$(date -j -f "%Z" "$current_timezone" "+%Y-%m-%d %H:%M:%S %Z" 2>/dev/null || date "+%Y-%m-%d %H:%M:%S UTC")
    
    echo "📍 Location: $current_location"
    echo "🎯 Grid Position: $current_position"
    echo "🕐 Timezone: $current_timezone"
    echo "⏰ Current Time: $current_time"
    echo "🗺️ Grid Mode: ${UDOS_GRID_MODE:-standard}"
    echo "📏 Grid Size: ${UDOS_GRID_COLS_MAX:-26}×${UDOS_GRID_ROWS_MAX:-99}"
}

# List supported locations
list_locations() {
    bold "📍 Supported Locations"
    echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
    
    if command -v jq >/dev/null 2>&1 && [[ -f "$LOCATION_CONFIG" ]]; then
        jq -r '.supported_locations[] | "📍 \(.name), \(.country) - \(.timezone)"' "$LOCATION_CONFIG" 2>/dev/null || {
            echo "📍 Sydney, Australia - Australia/Sydney"
            echo "📍 Melbourne, Australia - Australia/Melbourne" 
            echo "📍 Brisbane, Australia - Australia/Brisbane"
            echo "📍 Perth, Australia - Australia/Perth"
            echo "📍 Auckland, New Zealand - Pacific/Auckland"
        }
    else
        echo "📍 Sydney, Australia - Australia/Sydney"
        echo "📍 Melbourne, Australia - Australia/Melbourne"
        echo "📍 Brisbane, Australia - Australia/Brisbane"
        echo "📍 Perth, Australia - Australia/Perth"
        echo "📍 Auckland, New Zealand - Pacific/Auckland"
    fi
}

# Show grid map
show_grid_map() {
    bold "🗺️ Grid Map"
    echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
    
    local current_position=$(get_current_grid_position)
    local grid_cols="${UDOS_GRID_COLS_MAX:-26}"
    local grid_rows="${UDOS_GRID_ROWS_MAX:-99}"
    
    echo "Current Position: $current_position"
    echo "Grid Size: ${grid_cols}×${grid_rows}"
    echo
    echo "Sample Grid (first 10x10):"
    echo "   A B C D E F G H I J"
    for i in {1..10}; do
        printf "%2d " $i
        for col in A B C D E F G H I J; do
            local pos="${col}${i}"
            if [[ "$pos" == "$current_position" ]]; then
                printf "X "
            else
                printf ". "
            fi
        done
        echo
    done
    echo
    echo "Legend: X = Current Position, . = Available Position"
}

# Main execution
case "${1:-help}" in
    "init"|"setup")
        init_location_manager
        ;;
    "set")
        if [[ $# -lt 2 ]]; then
            red "❌ Usage: $0 set <location>"
            exit 1
        fi
        set_location "$2"
        ;;
    "timezone"|"tz")
        if [[ $# -lt 2 ]]; then
            red "❌ Usage: $0 timezone <timezone>"
            exit 1
        fi
        set_timezone "$2"
        ;;
    "grid")
        if [[ $# -lt 2 ]]; then
            red "❌ Usage: $0 grid <position>"
            exit 1
        fi
        set_grid_position "$2"
        ;;
    "status"|"show")
        show_location_status
        ;;
    "list"|"locations")
        list_locations
        ;;
    "map")
        show_grid_map
        ;;
    "help"|"-h"|"--help")
        bold "🗺️ Location Manager v2.0.0"
        echo
        echo "Usage: $0 [command] [options]"
        echo
        echo "Commands:"
        echo "  init                    Initialize location manager"
        echo "  set <location>          Set current location"
        echo "  timezone <timezone>     Set timezone"
        echo "  grid <position>         Set grid position (e.g., A1, B5)"
        echo "  status                  Show current location and grid status"
        echo "  list                    List supported locations"
        echo "  map                     Show grid map"
        echo "  help                    Show this help"
        echo
        echo "Examples:"
        echo "  $0 set Sydney"
        echo "  $0 timezone Australia/Sydney"
        echo "  $0 grid B5"
        echo "  $0 status"
        echo
        ;;
    *)
        red "❌ Unknown command: $1"
        echo "Use '$0 help' for available commands"
        exit 1
        ;;
esac
