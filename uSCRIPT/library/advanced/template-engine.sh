#!/bin/bash
# uDOS Template Engine
# Enhanced template processing with uCODE syntax support

set -euo pipefail

# Check bash version for associative array support
if ((BASH_VERSINFO[0] < 4)); then
    echo "Error: Bash 4.0 or higher required for associative arrays" >&2
    exit 1
fi

# Template Engine Configuration
TEMPLATE_ENGINE_VERSION="current"
TEMPLATE_CACHE_DIR="${UDOS_CACHE:-${HOME}/.udos/cache}/templates"
TEMPLATE_SYSTEM_DIR="${UDOS_ROOT:-$(pwd)}/uMEMORY/system/templates"
TEMPLATE_USER_DIR="${UDOS_ROOT:-$(pwd)}/uMEMORY/system/templates"

# Export UDOS_ROOT for sub-scripts
export UDOS_ROOT="${UDOS_ROOT:-$(pwd)}"

# Create cache directory if it doesn't exist
mkdir -p "$TEMPLATE_CACHE_DIR"

# uCODE Command Registry
declare -A UCODE_COMMANDS=()

# Initialize command registry
UCODE_COMMANDS["GET-RETRIEVE"]="get_retrieve_data"
UCODE_COMMANDS["POST-CREATE"]="post_create_data"
UCODE_COMMANDS["POST-SUBMIT"]="post_submit_data"
UCODE_COMMANDS["TEMPLATE-RENDER"]="template_render"
UCODE_COMMANDS["TEMPLATE-VALIDATE"]="template_validate"
UCODE_COMMANDS["COMPONENT-LOAD"]="component_load"
UCODE_COMMANDS["COMPONENT-RENDER"]="component_render"
UCODE_COMMANDS["CACHE-SET"]="cache_set"
UCODE_COMMANDS["CACHE-GET"]="cache_get"
UCODE_COMMANDS["SYSTEM-VERSION"]="system_version"

# uCODE Function Registry
declare -A UCODE_FUNCTIONS=()

# Initialize function registry
UCODE_FUNCTIONS["FORMAT-TIMESTAMP"]="format_timestamp"
UCODE_FUNCTIONS["FORMAT-TIMEZONE-FULL"]="format_timezone_full"
UCODE_FUNCTIONS["RESOLVE-LOCATION"]="resolve_location"
UCODE_FUNCTIONS["HUMANIZE-KEY"]="humanize_key"
UCODE_FUNCTIONS["FORMAT-PREFERENCE"]="format_preference"
UCODE_FUNCTIONS["SLUGIFY"]="slugify"
UCODE_FUNCTIONS["VALIDATE-EMAIL"]="validate_email"
UCODE_FUNCTIONS["SANITIZE-HTML"]="sanitize_html"
UCODE_FUNCTIONS["GET-SYSTEM-VERSION"]="get_system_version"

# Logging function
log_template() {
    echo "[$(date '+%Y-%m-%d %H:%M:%S')] [TEMPLATE-ENGINE] $*" >&2
}

# Error handling
template_error() {
    log_template "ERROR: $*"
    exit 1
}

# Parse uCODE command syntax
parse_ucode_command() {
    local input="$1"
    local command_type=""
    local command=""
    local params=""

    # Parse [COMMAND] {PARAMS}
    if [[ "$input" =~ ^\[([A-Z0-9-]+)\]\ *\{([^}]+)\}$ ]]; then
        command_type="command"
        command="${BASH_REMATCH[1]}"
        params="${BASH_REMATCH[2]}"
    # Parse <FUNCTION>
    elif [[ "$input" =~ ^\<([A-Z0-9-]+)\>$ ]]; then
        command_type="function"
        command="${BASH_REMATCH[1]}"
    else
        return 1
    fi

    echo "$command_type|$command|$params"
}

# Execute uCODE command
execute_ucode_command() {
    local command_type="$1"
    local command="$2"
    local params="${3:-}"

    case "$command_type" in
        "command")
            if [[ -n "${UCODE_COMMANDS[$command]:-}" ]]; then
                "${UCODE_COMMANDS[$command]}" "$params"
            else
                log_template "WARNING: Unknown command [$command]"
                echo "<!-- Unknown command: [$command] -->"
            fi
            ;;
        "function")
            if [[ -n "${UCODE_FUNCTIONS[$command]:-}" ]]; then
                "${UCODE_FUNCTIONS[$command]}"
            else
                log_template "WARNING: Unknown function <$command>"
                echo "<!-- Unknown function: <$command> -->"
            fi
            ;;
    esac
}

# uCODE Command Implementations
get_retrieve_data() {
    local params="$1"
    local data_source=""
    local query_params=""

    # Parse DATA-SOURCE | QUERY-PARAMS
    if [[ "$params" =~ ^([^|]+)\ *\|\ *(.+)$ ]]; then
        data_source="${BASH_REMATCH[1]}"
        query_params="${BASH_REMATCH[2]}"
    else
        data_source="$params"
    fi

    log_template "GET-RETRIEVE: $data_source with params: $query_params"

    # Implementation would connect to uMEMORY/system/get/
    case "$data_source" in
        "SETUP-STATUS")
            get_setup_status "$query_params"
            ;;
        "SYSTEM-VERSION")
            get_system_version
            ;;
        "USER-DATA")
            get_user_data "$query_params"
            ;;
        *)
            echo "<!-- GET-RETRIEVE: $data_source not implemented -->"
            ;;
    esac
}

post_create_data() {
    local params="$1"
    log_template "POST-CREATE: $params"
    # Implementation would connect to uMEMORY/system/post/
    echo "<!-- POST-CREATE: $params -->"
}

template_render() {
    local params="$1"
    log_template "TEMPLATE-RENDER: $params"
    echo "<!-- TEMPLATE-RENDER: $params -->"
}

# uCODE Function Implementations
format_timestamp() {
    date '+%Y-%m-%d %H:%M:%S UTC'
}

format_timezone_full() {
    # Input from pipe
    local timezone="${1:-$(cat)}"
    # Format timezone with full name and offset
    echo "$timezone (UTC$(date +%z))"
}

resolve_location() {
    local location="${1:-$(cat)}"
    # Mock implementation - would connect to location service
    echo "$location (Resolved)"
}

humanize_key() {
    local key="${1:-$(cat)}"
    # Convert KEBAB-CASE or snake_case to Title Case
    echo "$key" | sed 's/[-_]/ /g' | sed 's/\b\w/\U&/g'
}

format_preference() {
    local pref="${1:-$(cat)}"
    # Format preference value for display
    echo "$pref"
}

slugify() {
    local input="${1:-$(cat)}"
    echo "$input" | tr '[:upper:]' '[:lower:]' | sed 's/[^a-z0-9]/-/g' | sed 's/--*/-/g' | sed 's/^-\|-$//g'
}

get_system_version() {
    echo "current"
}

get_setup_status() {
    local username="$1"
    # Mock implementation - would read from uMEMORY/system/get/setup-status/
    cat << EOF
{
    "IDENTITY-CONFIGURED": true,
    "LOCATION-SET": false,
    "TIMEZONE-CONFIGURED": true,
    "PREFERENCES-SET": false,
    "FIRST-MISSION-CREATED": false,
    "TEMPLATE-SYSTEM-VALIDATED": true
}
EOF
}

get_user_data() {
    local username="$1"
    # Mock implementation - would read from uMEMORY/system/get/user-data/
    cat << EOF
{
    "FULL-NAME": "Test User",
    "EMAIL": "test@example.com",
    "LOCATION": "San Francisco, CA",
    "TIMEZONE": "America/Los_Angeles"
}
EOF
}

# Process template with uCODE syntax
process_template() {
    local template_file="$1"
    local output_file="${2:-}"

    if [[ ! -f "$template_file" ]]; then
        template_error "Template file not found: $template_file"
    fi

    log_template "Processing template: $template_file"

    # Read template content
    local content
    content=$(cat "$template_file")

    # Process uCODE commands and functions
    # This is a simplified implementation - would need full parser for production
    while IFS= read -r line; do
        # Process {{#IF}} blocks, {{#EACH}} blocks, etc.
        # Process [COMMAND] {PARAMS} patterns
        # Process <FUNCTION> patterns
        # Process variable substitutions
        echo "$line"
    done <<< "$content"
}

# Main template engine entry point
main() {
    local action="${1:-help}"
    local template_file="${2:-}"
    local output_file="${3:-}"

    case "$action" in
        "render")
            if [[ -z "$template_file" ]]; then
                template_error "Template file required for render action"
            fi
            process_template "$template_file" "$output_file"
            ;;
        "validate")
            if [[ -z "$template_file" ]]; then
                template_error "Template file required for validate action"
            fi
            validate_template "$template_file"
            ;;
        "version")
            echo "uDOS Template Engine v$TEMPLATE_ENGINE_VERSION"
            ;;
        "help"|*)
            cat << EOF
uDOS Template Engine v$TEMPLATE_ENGINE_VERSION

Usage: $0 <action> [options]

Actions:
  render <template_file> [output_file]  - Render template with uCODE processing
  validate <template_file>              - Validate template syntax
  version                               - Show engine version
  help                                  - Show this help

Examples:
  $0 render /path/to/template.md
  $0 validate /path/to/template.md
EOF
            ;;
    esac
}

# Validate template syntax
validate_template() {
    local template_file="$1"
    log_template "Validating template: $template_file"

    # Check for valid uCODE syntax
    local errors=0

    # Check for proper bracket matching
    if ! grep -q '{{.*}}' "$template_file"; then
        log_template "WARNING: No template variables found"
    fi

    # Check for proper uCODE command syntax
    while IFS= read -r line; do
        if [[ "$line" =~ \[([^]]+)\] ]]; then
            local cmd="${BASH_REMATCH[1]}"
            if [[ ! "$cmd" =~ ^[A-Z0-9-]+$ ]]; then
                log_template "ERROR: Invalid command syntax: [$cmd]"
                ((errors++))
            fi
        fi

        if [[ "$line" =~ \<([^>]+)\> ]]; then
            local func="${BASH_REMATCH[1]}"
            if [[ ! "$func" =~ ^[A-Z0-9-]+$ ]]; then
                log_template "ERROR: Invalid function syntax: <$func>"
                ((errors++))
            fi
        fi
    done < "$template_file"

    if [[ $errors -eq 0 ]]; then
        log_template "Template validation passed: $template_file"
        return 0
    else
        log_template "Template validation failed with $errors errors"
        return 1
    fi
}

# Run main function if script is executed directly
if [[ "${BASH_SOURCE[0]}" == "${0}" ]]; then
    main "$@"
fi
