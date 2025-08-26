#!/bin/bash
# uDOS GET Data Handler
# Handles GET data retrieval operations

set -euo pipefail

# Configuration
GET_DATA_DIR="${UDOS_ROOT:-$(pwd)}/uMEMORY/system/get"
GET_CACHE_DIR="${UDOS_CACHE:-${HOME}/.udos/cache}/get"
GET_HANDLER_VERSION="current"

# Create directories
mkdir -p "$GET_DATA_DIR" "$GET_CACHE_DIR"

# Logging
log_get() {
    echo "[$(date '+%Y-%m-%d %H:%M:%S')] [GET-HANDLER] $*" >&2
}

# GET data retrieval functions
get_setup_status() {
    local username="$1"
    local status_file="$GET_DATA_DIR/setup-status/${username}.json"

    if [[ -f "$status_file" ]]; then
        cat "$status_file"
    else
        # Default setup status
        cat << EOF
{
    "IDENTITY-CONFIGURED": false,
    "LOCATION-SET": false,
    "TIMEZONE-CONFIGURED": false,
    "PREFERENCES-SET": false,
    "FIRST-MISSION-CREATED": false,
    "TEMPLATE-SYSTEM-VALIDATED": false
}
EOF
    fi
}

get_user_data() {
    local username="$1"
    local user_file="$GET_DATA_DIR/user-data/${username}.json"

    if [[ -f "$user_file" ]]; then
        cat "$user_file"
    else
        echo "{}"
    fi
}

get_system_version() {
    echo "current"
}

get_location_data() {
    local location_query="$1"
    local location_file="$GET_DATA_DIR/location/${location_query}.json"

    if [[ -f "$location_file" ]]; then
        cat "$location_file"
    else
        # Mock location data
        cat << EOF
{
    "query": "$location_query",
    "city": "Unknown",
    "country": "Unknown",
    "timezone": "UTC"
}
EOF
    fi
}

get_timezone_data() {
    local timezone="$1"
    local tz_file="$GET_DATA_DIR/timezone/${timezone}.json"

    if [[ -f "$tz_file" ]]; then
        cat "$tz_file"
    else
        # Default timezone data
        cat << EOF
{
    "timezone": "$timezone",
    "offset": "+00:00",
    "name": "Coordinated Universal Time"
}
EOF
    fi
}

# Main GET handler
main() {
    local data_source="$1"
    local params="${2:-}"

    case "$data_source" in
        "SETUP-STATUS")
            get_setup_status "$params"
            ;;
        "USER-DATA")
            get_user_data "$params"
            ;;
        "SYSTEM-VERSION")
            get_system_version
            ;;
        "LOCATION")
            get_location_data "$params"
            ;;
        "TIMEZONE")
            get_timezone_data "$params"
            ;;
        *)
            log_get "ERROR: Unknown data source: $data_source"
            echo "{\"error\": \"Unknown data source: $data_source\"}"
            exit 1
            ;;
    esac
}

if [[ "${BASH_SOURCE[0]}" == "${0}" ]]; then
    main "$@"
fi
