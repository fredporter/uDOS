#!/bin/bash
# uDOS Variable Environment Export System
# Exports system variables to environment for uSCRIPT access

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
SYSTEM_VARS_FILE="$SCRIPT_DIR/system-variables.json"

# Export all system variables to environment
export_system_variables() {
    if [[ ! -f "$SYSTEM_VARS_FILE" ]]; then
        echo "System variables file not found: $SYSTEM_VARS_FILE" >&2
        return 1
    fi

    # Get current variable values
    local values_file="$SCRIPT_DIR/../user/variables/values-current.json"

    # Process each variable that should be exported
    while IFS= read -r var_line; do
        local var_name=$(echo "$var_line" | jq -r '.name')
        local env_name=$(echo "$var_line" | jq -r '.env_name')
        local default_value=$(echo "$var_line" | jq -r '.default')
        local should_export=$(echo "$var_line" | jq -r '.export_to_env // false')

        if [[ "$should_export" == "true" ]]; then
            # Get current value or use default
            local current_value="$default_value"
            if [[ -f "$values_file" ]]; then
                local session_value=$(jq -r ".values[\"$var_name\"] // empty" "$values_file" 2>/dev/null)
                if [[ -n "$session_value" && "$session_value" != "null" ]]; then
                    current_value="$session_value"
                fi
            fi

            # Export to environment
            export "$env_name"="$current_value"
            echo "Exported: $env_name=$current_value"
        fi
    done < <(jq -r '.variables | to_entries[] | {name: .key, env_name: .value.env_name, default: .value.default, export_to_env: .value.export_to_env}' "$SYSTEM_VARS_FILE")
}

# Export variables for uSCRIPT environment
export_for_uscript() {
    # Export all system variables
    export_system_variables

    # Set uDOS-specific environment variables
    export UDOS_ROOT="$(cd "$SCRIPT_DIR/../../.." && pwd)"
    export UDOS_SYSTEM_VARS="$SYSTEM_VARS_FILE"
    export UDOS_USER_VARS="$SCRIPT_DIR/../user/variables"
    export UDOS_INITIALIZED="true"

    echo "uDOS environment variables exported for uSCRIPT access"
}

# Main execution
if [[ "${BASH_SOURCE[0]}" == "${0}" ]]; then
    case "${1:-export}" in
        "export"|"all")
            export_system_variables
            ;;
        "uscript")
            export_for_uscript
            ;;
        *)
            echo "Usage: $0 [export|uscript]"
            exit 1
            ;;
    esac
fi
