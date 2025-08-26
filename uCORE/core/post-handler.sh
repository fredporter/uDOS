#!/bin/bash
# uDOS POST Data Handler
# Handles POST data submission operations

set -euo pipefail

# Configuration
POST_DATA_DIR="${UDOS_ROOT:-$(pwd)}/uMEMORY/system/post"
POST_CACHE_DIR="${UDOS_CACHE:-${HOME}/.udos/cache}/post"
POST_HANDLER_VERSION="current"h
# uDOS POST Data Handler v1.0.4.1
# Handles POST data creation and submission operations

set -euo pipefail

# Configuration
POST_DATA_DIR="${UDOS_ROOT:-$(pwd)}/uMEMORY/system/post"
POST_CACHE_DIR="${UDOS_CACHE:-${HOME}/.udos/cache}/post"
POST_HANDLER_VERSION="1.3.3"

# Create directories
mkdir -p "$POST_DATA_DIR" "$POST_CACHE_DIR"

# Logging
log_post() {
    echo "[$(date '+%Y-%m-%d %H:%M:%S')] [POST-HANDLER] $*" >&2
}

# POST data creation functions
post_user_creation() {
    local username="$1"
    local user_data="$2"
    local user_file="$POST_DATA_DIR/user-creation/${username}.json"

    mkdir -p "$(dirname "$user_file")"

    # Validate and store user creation data
    echo "$user_data" > "$user_file"
    log_post "Created user data for: $username"

    # Update setup status
    update_setup_status "$username" "IDENTITY-CONFIGURED" "true"
}

post_form_submission() {
    local form_name="$1"
    local form_data="$2"
    local timestamp=$(date '+%Y%m%d-%H%M%S')
    local form_file="$POST_DATA_DIR/form-submissions/${form_name}-${timestamp}.json"

    mkdir -p "$(dirname "$form_file")"
    echo "$form_data" > "$form_file"
    log_post "Submitted form: $form_name"
}

post_preference_update() {
    local username="$1"
    local preferences="$2"
    local pref_file="$POST_DATA_DIR/preference-updates/${username}.json"

    mkdir -p "$(dirname "$pref_file")"
    echo "$preferences" > "$pref_file"
    log_post "Updated preferences for: $username"

    # Update setup status
    update_setup_status "$username" "PREFERENCES-SET" "true"
}

post_location_set() {
    local username="$1"
    local location_data="$2"
    local location_file="$POST_DATA_DIR/location-updates/${username}.json"

    mkdir -p "$(dirname "$location_file")"
    echo "$location_data" > "$location_file"
    log_post "Set location for: $username"

    # Update setup status
    update_setup_status "$username" "LOCATION-SET" "true"
}

# Update setup status helper
update_setup_status() {
    local username="$1"
    local field="$2"
    local value="$3"
    local get_dir="${UDOS_ROOT:-$(pwd)}/uMEMORY/system/get"
    local status_file="$get_dir/setup-status/${username}.json"

    mkdir -p "$(dirname "$status_file")"

    # Create or update status file
    if [[ -f "$status_file" ]]; then
        # Update existing status
        local temp_file=$(mktemp)
        jq --arg field "$field" --arg value "$value" '.[$field] = ($value == "true")' "$status_file" > "$temp_file"
        mv "$temp_file" "$status_file"
    else
        # Create new status file
        cat << EOF > "$status_file"
{
    "IDENTITY-CONFIGURED": false,
    "LOCATION-SET": false,
    "TIMEZONE-CONFIGURED": false,
    "PREFERENCES-SET": false,
    "FIRST-MISSION-CREATED": false,
    "TEMPLATE-SYSTEM-VALIDATED": false,
    "$field": $([ "$value" = "true" ] && echo "true" || echo "false")
}
EOF
    fi

    log_post "Updated setup status for $username: $field = $value"
}

# Validate JSON data
validate_json() {
    local data="$1"
    if echo "$data" | jq . >/dev/null 2>&1; then
        return 0
    else
        return 1
    fi
}

# Main POST handler
main() {
    local data_type="$1"
    local params="${2:-}"

    # Parse params (format: USERNAME|DATA or DATA)
    local username=""
    local data=""

    if [[ "$params" =~ ^([^|]+)\|(.+)$ ]]; then
        username="${BASH_REMATCH[1]}"
        data="${BASH_REMATCH[2]}"
    else
        data="$params"
    fi

    case "$data_type" in
        "USER-CREATION")
            if [[ -z "$username" ]]; then
                log_post "ERROR: Username required for user creation"
                exit 1
            fi
            post_user_creation "$username" "$data"
            ;;
        "FORM-SUBMISSION")
            local form_name="${username:-default}"
            post_form_submission "$form_name" "$data"
            ;;
        "PREFERENCE-UPDATE")
            if [[ -z "$username" ]]; then
                log_post "ERROR: Username required for preference update"
                exit 1
            fi
            post_preference_update "$username" "$data"
            ;;
        "LOCATION-SET")
            if [[ -z "$username" ]]; then
                log_post "ERROR: Username required for location update"
                exit 1
            fi
            post_location_set "$username" "$data"
            ;;
        *)
            log_post "ERROR: Unknown data type: $data_type"
            exit 1
            ;;
    esac
}

if [[ "${BASH_SOURCE[0]}" == "${0}" ]]; then
    main "$@"
fi
