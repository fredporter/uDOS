#!/bin/bash
# uDOS Template Engine (Compatible Version)
# Enhanced template processing with uCODE syntax support
# Compatible with bash 3.2+

set -euo pipefail

# Template Engine Configuration
TEMPLATE_ENGINE_VERSION="current"
TEMPLATE_CACHE_DIR="${UDOS_CACHE:-${HOME}/.udos/cache}/templates"
TEMPLATE_SYSTEM_DIR="${UDOS_ROOT:-$(pwd)}/uMEMORY/system/templates"
TEMPLATE_USER_DIR="${UDOS_ROOT:-$(pwd)}/uMEMORY/system/templates"

# Export UDOS_ROOT for sub-scripts
export UDOS_ROOT="${UDOS_ROOT:-$(pwd)}"

# Create cache directory if it doesn't exist
mkdir -p "$TEMPLATE_CACHE_DIR"

# Logging function
log_template() {
    echo "[$(date '+%Y-%m-%d %H:%M:%S')] [TEMPLATE-ENGINE] $*" >&2
}

# Error handling
template_error() {
    log_template "ERROR: $*"
    exit 1
}

# uCODE Command Handler (bash 3.2 compatible)
handle_ucode_command() {
    local command="$1"
    local params="${2:-}"

    case "$command" in
        "GET-RETRIEVE")
            if [[ -n "$params" ]]; then
                # Parse DATA-SOURCE | QUERY-PARAMS
                if echo "$params" | grep -q '|'; then
                    local data_source=$(echo "$params" | cut -d'|' -f1 | tr -d ' ')
                    local query_params=$(echo "$params" | cut -d'|' -f2 | tr -d ' ')
                    "${UDOS_ROOT}/uCORE/core/get-handler.sh" "$data_source" "$query_params"
                else
                    "${UDOS_ROOT}/uCORE/core/get-handler.sh" "$params"
                fi
            else
                log_template "ERROR: GET-RETRIEVE requires parameters"
                echo "<!-- ERROR: GET-RETRIEVE requires parameters -->"
            fi
            ;;
        "POST-CREATE"|"POST-SUBMIT")
            "${UDOS_ROOT}/uCORE/core/post-handler.sh" "$command" "$params"
            ;;
        "TEMPLATE-RENDER")
            template_render "$params"
            ;;
        "SYSTEM-VERSION")
            echo "current"
            ;;
        *)
            log_template "WARNING: Unknown command [$command]"
            echo "<!-- Unknown command: [$command] -->"
            ;;
    esac
}

# uCODE Function Handler (bash 3.2 compatible)
handle_ucode_function() {
    local function_name="$1"
    local input="${2:-}"

    case "$function_name" in
        "FORMAT-TIMESTAMP")
            date '+%Y-%m-%d %H:%M:%S UTC'
            ;;
        "FORMAT-TIMEZONE-FULL")
            echo "$input (UTC$(date +%z))"
            ;;
        "RESOLVE-LOCATION")
            echo "$input (Resolved)"
            ;;
        "HUMANIZE-KEY")
            echo "$input" | sed 's/[-_]/ /g' | sed 's/\b\w/\U&/g'
            ;;
        "FORMAT-PREFERENCE")
            echo "$input"
            ;;
        "SLUGIFY")
            echo "$input" | tr '[:upper:]' '[:lower:]' | sed 's/[^a-z0-9]/-/g' | sed 's/--*/-/g' | sed 's/^-\|-$//g'
            ;;
        "GET-SYSTEM-VERSION")
            echo "current"
            ;;
        *)
            log_template "WARNING: Unknown function <$function_name>"
            echo "<!-- Unknown function: <$function_name> -->"
            ;;
    esac
}

# Parse uCODE Block syntax
parse_ucode_block() {
    local input="$1"

    # Parse [TERM] {VARIABLE | FUNCTION}
    if echo "$input" | grep -q '^\[TERM\].*{.*}'; then
        local variable=$(echo "$input" | sed 's/.*{\([^}]*\)}.*/\1/')
        echo "variable|$variable"
        return 0
    fi

    # Parse [COMMAND] {PARAMS}
    if echo "$input" | grep -q '^\[[A-Z-]*\].*{.*}'; then
        local command=$(echo "$input" | sed 's/^\[\([^]]*\)\].*/\1/')
        local params=$(echo "$input" | sed 's/.*{\([^}]*\)}.*/\1/')
        echo "command|$command|$params"
        return 0
    fi

    # Parse [IF] {CONDITION}
    if echo "$input" | grep -q '^\[IF\].*{.*}'; then
        local condition=$(echo "$input" | sed 's/.*{\([^}]*\)}.*/\1/')
        echo "if|$condition"
        return 0
    fi

    # Parse [/IF], [ELSE], [/EACH], [/WITH]
    if echo "$input" | grep -q '^\[/\?[A-Z]*\]$'; then
        local block=$(echo "$input" | sed 's/^\[\(/\?\)\([^]]*\)\].*/\2/')
        local closing=$(echo "$input" | sed 's/^\[\(/\?\)[^]]*\].*/\1/')
        echo "block|$closing$block"
        return 0
    fi

    # Parse [EACH] {COLLECTION}
    if echo "$input" | grep -q '^\[EACH\].*{.*}'; then
        local collection=$(echo "$input" | sed 's/.*{\([^}]*\)}.*/\1/')
        echo "each|$collection"
        return 0
    fi

    # Parse [WITH] DATA
    if echo "$input" | grep -q '^\[WITH\]'; then
        local data=$(echo "$input" | sed 's/^\[WITH\] *//')
        echo "with|$data"
        return 0
    fi

    return 1
}

# Process uCODE Block syntax
process_ucode_block() {
    local block_type="$1"
    local content="$2"
    local params="${3:-}"

    case "$block_type" in
        "variable")
            # Handle [TERM] {VARIABLE | FUNCTION}
            if echo "$content" | grep -q '|'; then
                local var=$(echo "$content" | cut -d'|' -f1 | tr -d ' ')
                local func=$(echo "$content" | cut -d'|' -f2 | tr -d ' ')
                local value="<!-- TERM: $var -->"
                if [[ "$func" =~ ^\<.*\>$ ]]; then
                    local func_name=$(echo "$func" | sed 's/^<\([^>]*\)>.*/\1/')
                    handle_ucode_function "$func_name" "$value"
                else
                    echo "$value"
                fi
            else
                echo "<!-- TERM: $content -->"
            fi
            ;;
        "if")
            echo "<!-- IF: $content -->"
            ;;
        "each")
            echo "<!-- EACH: $content -->"
            ;;
        "with")
            echo "<!-- WITH: $content -->"
            ;;
        "block")
            case "$content" in
                "/IF"|"ELSE"|"/EACH"|"/WITH")
                    echo "<!-- $content -->"
                    ;;
                *)
                    echo "<!-- BLOCK: $content -->"
                    ;;
            esac
            ;;
        "command")
            handle_ucode_command "$content" "$params"
            ;;
    esac
}

# uCODE Command Handler (bash 3.2 compatible)
handle_ucode_command() {
    local command="$1"
    local params="${2:-}"

    case "$command" in
        "GET-RETRIEVE")
            if [[ -n "$params" ]]; then
                # Parse DATA-SOURCE | QUERY-PARAMS
                if echo "$params" | grep -q '|'; then
                    local data_source=$(echo "$params" | cut -d'|' -f1 | tr -d ' ')
                    local query_params=$(echo "$params" | cut -d'|' -f2 | tr -d ' ')
                    "${UDOS_ROOT}/uCORE/core/get-handler.sh" "$data_source" "$query_params"
                else
                    "${UDOS_ROOT}/uCORE/core/get-handler.sh" "$params"
                fi
            else
                log_template "ERROR: GET-RETRIEVE requires parameters"
                echo "<!-- ERROR: GET-RETRIEVE requires parameters -->"
            fi
            ;;
        "POST-CREATE"|"POST-SUBMIT")
            "${UDOS_ROOT}/uCORE/core/post-handler.sh" "$command" "$params"
            ;;
        "TEMPLATE-RENDER")
            template_render "$params"
            ;;
        "SYSTEM-VERSION")
            echo "current"
            ;;
        *)
            log_template "WARNING: Unknown command [$command]"
            echo "<!-- Unknown command: [$command] -->"
            ;;
    esac
}

# uCODE Function Handler (bash 3.2 compatible)
handle_ucode_function() {
    local function_name="$1"
    local input="${2:-}"

    case "$function_name" in
        "FORMAT-TIMESTAMP")
            date '+%Y-%m-%d %H:%M:%S UTC'
            ;;
        "FORMAT-TIMEZONE-FULL")
            echo "$input (UTC$(date +%z))"
            ;;
        "RESOLVE-LOCATION")
            echo "$input (Resolved)"
            ;;
        "HUMANIZE-KEY")
            echo "$input" | sed 's/[-_]/ /g' | sed 's/\b\w/\U&/g'
            ;;
        "FORMAT-PREFERENCE")
            echo "$input"
            ;;
        "SLUGIFY")
            echo "$input" | tr '[:upper:]' '[:lower:]' | sed 's/[^a-z0-9]/-/g' | sed 's/--*/-/g' | sed 's/^-\|-$//g'
            ;;
        "GET-SYSTEM-VERSION")
            echo "current"
            ;;
        *)
            log_template "WARNING: Unknown function <$function_name>"
            echo "<!-- Unknown function: <$function_name> -->"
            ;;
    esac
}

# Simple template processing
process_template() {
    local template_file="$1"
    local output_file="${2:-}"

    if [[ ! -f "$template_file" ]]; then
        template_error "Template file not found: $template_file"
    fi

    log_template "Processing template: $template_file"

    # For now, just validate the template and show its contents
    # Full processing would require a complete parser
    cat "$template_file"
}

template_render() {
    local params="$1"
    log_template "TEMPLATE-RENDER: $params"
    echo "<!-- TEMPLATE-RENDER: $params -->"
}

# Validate template syntax
validate_template() {
    local template_file="$1"
    log_template "Validating template: $template_file"

    if [[ ! -f "$template_file" ]]; then
        log_template "ERROR: Template file not found: $template_file"
        return 1
    fi

    # Check for valid uCODE syntax
    local errors=0

    # Check for uCODE Block syntax patterns
    if ! grep -q '\[VAR\]\||\[IF\]\|\[EACH\]\|\[WITH\]\|\[GET-RETRIEVE\]' "$template_file"; then
        log_template "WARNING: No uCODE Block syntax found"
    fi

    # Check for proper uCODE Block syntax
    while IFS= read -r line; do
        # Check [TERM] {VARIABLE} syntax
        if echo "$line" | grep -q '\[TERM\].*{.*}'; then
            local var_syntax=$(echo "$line" | grep -o '\[TERM\][^}]*}')
            # Allow variables with pipes and functions
            if ! echo "$var_syntax" | grep -q '\[TERM\] *{[A-Z0-9_|<> -]*}'; then
                log_template "ERROR: Invalid TERM syntax: $var_syntax"
                ((errors++))
            fi
        fi

        # Check [COMMAND] syntax
        if echo "$line" | grep -q '\[[A-Z-]*\]' && ! echo "$line" | grep -q '\[TERM\]\|\[/\?\(IF\|EACH\|WITH\|ELSE\)\]'; then
            local cmd=$(echo "$line" | sed 's/.*\[\([^]]*\)\].*/\1/')
            if [[ ! "$cmd" =~ ^[A-Z0-9-]+$ ]]; then
                log_template "ERROR: Invalid command syntax: [$cmd]"
                ((errors++))
            fi
        fi

        # Check <FUNCTION> syntax
        if echo "$line" | grep -q '<.*>'; then
            local func=$(echo "$line" | sed 's/.*<\([^>]*\)>.*/\1/')
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
            echo "uDOS Template Engine v$TEMPLATE_ENGINE_VERSION (Compatible)"
            ;;
        "help"|*)
            cat << EOF
uDOS Template Engine v$TEMPLATE_ENGINE_VERSION (Compatible)

Usage: $0 <action> [options]

Actions:
  render <template_file> [output_file]  - Render template with uCODE processing
  validate <template_file>              - Validate template syntax
  version                               - Show engine version
  help                                  - Show this help

Examples:
  $0 render /path/to/template.md
  $0 validate /path/to/template.md

Note: This is the bash 3.2+ compatible version
EOF
            ;;
    esac
}

# Run main function if script is executed directly
if [[ "${BASH_SOURCE[0]}" == "${0}" ]]; then
    main "$@"
fi
