#!/bin/bash
# uCORE GET Utility - Simple Data Retrieval
# Handles data retrieval operations for uCORE compatibility

set -euo pipefail

# Get script directory
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
UDOS_ROOT="$(cd "$SCRIPT_DIR/../../.." && pwd)"

# Logging functions
log_info() { echo -e "\033[0;36m[INFO]\033[0m $1"; }
log_success() { echo -e "\033[0;32m[SUCCESS]\033[0m $1"; }
log_warning() { echo -e "\033[0;33m[WARNING]\033[0m $1"; }
log_error() { echo -e "\033[0;31m[ERROR]\033[0m $1"; }

# Get data from various sources
get_data() {
    local source="$1"
    local key="${2:-}"

    case "$source" in
        user)
            get_user_data "$key"
            ;;
        system)
            get_system_data "$key"
            ;;
        template)
            get_template_data "$key"
            ;;
        role)
            get_role_data "$key"
            ;;
        location)
            get_location_data "$key"
            ;;
        timezone)
            get_timezone_data "$key"
            ;;
        *)
            log_error "Unknown data source: $source"
            return 1
            ;;
    esac
}

# Get user data from sandbox
get_user_data() {
    local key="$1"
    local user_file="$UDOS_ROOT/sandbox/user.md"

    if [ ! -f "$user_file" ]; then
        log_warning "User file not found: $user_file"
        return 1
    fi

    # Extract value from markdown format
    grep "^$key:" "$user_file" 2>/dev/null | sed "s/^$key: *//" || echo ""
}

# Get system data from uMEMORY
get_system_data() {
    local key="$1"
    local system_file="$UDOS_ROOT/uMEMORY/system/system.json"

    if [ -f "$system_file" ] && command -v jq >/dev/null 2>&1; then
        jq -r ".$key // empty" "$system_file" 2>/dev/null || echo ""
    else
        log_warning "System data not available"
        echo ""
    fi
}

# Get template data
get_template_data() {
    local template="$1"
    local template_file="$UDOS_ROOT/uMEMORY/system/templates/$template"

    if [ -f "$template_file" ]; then
        cat "$template_file"
    else
        log_warning "Template not found: $template"
        return 1
    fi
}

# Get role data
get_role_data() {
    local key="$1"
    local current_role="${UDOS_ROLE:-Tomb}"
    local role_file="$UDOS_ROOT/uMEMORY/role/$current_role/config.json"

    if [ -f "$role_file" ] && command -v jq >/dev/null 2>&1; then
        jq -r ".$key // empty" "$role_file" 2>/dev/null || echo ""
    else
        echo ""
    fi
}

# Get location data from geographic system
get_location_data() {
    local query="$1"
    local geo_engine="$UDOS_ROOT/uCORE/geo/engines/geo-core-engine.sh"

    if [ -x "$geo_engine" ]; then
        "$geo_engine" location "$query" 2>/dev/null || echo ""
    else
        echo ""
    fi
}

# Get timezone data
get_timezone_data() {
    local location="$1"
    local timezone_data="$UDOS_ROOT/uCORE/geo/data/timezone-map.json"

    if [ -f "$timezone_data" ] && command -v jq >/dev/null 2>&1; then
        jq -r ".\"$location\" // empty" "$timezone_data" 2>/dev/null || echo ""
    else
        echo ""
    fi
}

# Show usage
show_usage() {
    echo "Usage: get <source> [key]"
    echo ""
    echo "Sources:"
    echo "  user        User data from sandbox"
    echo "  system      System configuration"
    echo "  template    Template files"
    echo "  role        Current role data"
    echo "  location    Geographic location data"
    echo "  timezone    Timezone information"
    echo ""
    echo "Examples:"
    echo "  get user name"
    echo "  get system version"
    echo "  get template uDOT-mission-brief.md"
    echo "  get role capabilities"
    echo "  get location 'Los Angeles'"
    echo "  get timezone America/Los_Angeles"
}

# Main execution
main() {
    if [ $# -eq 0 ]; then
        show_usage
        return 1
    fi

    case "$1" in
        help|--help|-h)
            show_usage
            ;;
        *)
            get_data "$@"
            ;;
    esac
}

# Run if executed directly
if [ "${BASH_SOURCE[0]}" == "${0}" ]; then
    main "$@"
fi
