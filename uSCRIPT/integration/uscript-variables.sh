#!/bin/bash
# uSCRIPT Variable Integration
# Provides variable management capabilities within uSCRIPT container environment

set -euo pipefail

# Configuration
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
UDOS_ROOT="$(cd "$SCRIPT_DIR/../.." && pwd)"
VARIABLE_MANAGER="$UDOS_ROOT/uCORE/code/variable-manager.sh"

# Source the variable manager functions
source "$VARIABLE_MANAGER"

# uSCRIPT-specific variable operations
export_variables_to_environment() {
    local session_id="${1:-current}"
    local values_file="$USER_VARIABLE_DIR/values-${session_id}.json"

    if [[ -f "$values_file" ]]; then
        # Export all variable values as environment variables
        while IFS= read -r line; do
            local var_name
            var_name=$(echo "$line" | jq -r '.key')
            local var_value
            var_value=$(echo "$line" | jq -r '.value')

            # Export with UDOS_ prefix to avoid conflicts
            export "UDOS_${var_name}=${var_value}"

        done < <(jq -r '.values | to_entries[] | @json' "$values_file")

        log_success "Variables exported to environment for session: $session_id"
    fi
}

# Import variables from environment
import_variables_from_environment() {
    local session_id="${1:-current}"

    # Look for UDOS_ prefixed environment variables
    while IFS= read -r env_var; do
        if [[ "$env_var" =~ ^UDOS_(.+)=(.*)$ ]]; then
            local var_name="${BASH_REMATCH[1]}"
            local var_value="${BASH_REMATCH[2]}"

            set_variable "$var_name" "$var_value" "$session_id"
        fi
    done < <(env | grep "^UDOS_")

    log_success "Environment variables imported to session: $session_id"
}

# Generate variable substitution for script execution
substitute_variables() {
    local script_content="$1"
    local session_id="${2:-current}"

    local values_file="$USER_VARIABLE_DIR/values-${session_id}.json"

    if [[ -f "$values_file" ]]; then
        # Substitute all $VARIABLE references in script content
        while IFS= read -r line; do
            local var_name
            var_name=$(echo "$line" | jq -r '.key')
            local var_value
            var_value=$(echo "$line" | jq -r '.value')

            # Replace $VARIABLE with actual value
            script_content="${script_content//\$$var_name/$var_value}"

        done < <(jq -r '.values | to_entries[] | @json' "$values_file")
    fi

    echo "$script_content"
}

# Create a variable-aware script template
create_variable_script() {
    local script_name="$1"
    local script_type="${2:-bash}"
    local variables_list="${3:-}"

    local script_file="$UDOS_ROOT/uSCRIPT/active/${script_name}.${script_type}"

    # Create script header with variable declarations
    local script_header=""

    case "$script_type" in
        "bash"|"sh")
            script_header="#!/bin/bash
# Generated uSCRIPT with variable support
# Variables: $variables_list

set -euo pipefail

"
            ;;
        "python"|"py")
            script_header="#!/usr/bin/env python3
# Generated uSCRIPT with variable support
# Variables: $variables_list

import os
import sys

"
            ;;
        "js"|"javascript")
            script_header="#!/usr/bin/env node
// Generated uSCRIPT with variable support
// Variables: $variables_list

"
            ;;
    esac

    # Add variable loading section
    if [[ -n "$variables_list" ]]; then
        IFS=',' read -ra vars <<< "$variables_list"

        case "$script_type" in
            "bash"|"sh")
                script_header+="# Load variables from uDOS variable system
"
                for var in "${vars[@]}"; do
                    var=$(echo "$var" | tr -d ' ')
                    script_header+="$var=\$($VARIABLE_MANAGER GET $var)
"
                done
                script_header+="
"
                ;;
            "python"|"py")
                script_header+="# Load variables from uDOS variable system
import subprocess

def get_udos_variable(var_name):
    try:
        result = subprocess.run(['$VARIABLE_MANAGER', 'GET', var_name],
                              capture_output=True, text=True, check=True)
        return result.stdout.strip()
    except subprocess.CalledProcessError:
        return ''

"
                for var in "${vars[@]}"; do
                    var=$(echo "$var" | tr -d ' ')
                    script_header+="$var = get_udos_variable('$var')
"
                done
                script_header+="
"
                ;;
            "js"|"javascript")
                script_header+="// Load variables from uDOS variable system
const { execSync } = require('child_process');

function getUdosVariable(varName) {
    try {
        return execSync(\`$VARIABLE_MANAGER GET \${varName}\`, {encoding: 'utf8'}).trim();
    } catch (error) {
        return '';
    }
}

"
                for var in "${vars[@]}"; do
                    var=$(echo "$var" | tr -d ' ')
                    script_header+="const $var = getUdosVariable('$var');
"
                done
                script_header+="
"
                ;;
        esac
    fi

    # Add placeholder for user code
    script_header+="# === USER CODE BELOW ===

# Your script code here...
# Variables are available as defined above
"

    echo "$script_header" > "$script_file"
    chmod +x "$script_file"

    log_success "Variable-aware script created: $script_file"
    echo "$script_file"
}

# Execute script with variable substitution
execute_with_variables() {
    local script_file="$1"
    local session_id="${2:-current}"

    if [[ ! -f "$script_file" ]]; then
        log_error "Script file not found: $script_file"
        return 1
    fi

    # Read script content
    local script_content
    script_content=$(cat "$script_file")

    # Substitute variables
    local processed_content
    processed_content=$(substitute_variables "$script_content" "$session_id")

    # Create temporary processed script
    local temp_script="/tmp/udos-script-$$.tmp"
    echo "$processed_content" > "$temp_script"
    chmod +x "$temp_script"

    # Export variables to environment
    export_variables_to_environment "$session_id"

    # Execute processed script
    log_info "Executing script with variable substitution: $script_file"
    "$temp_script"
    local exit_code=$?

    # Clean up
    rm -f "$temp_script"

    if [[ $exit_code -eq 0 ]]; then
        log_success "Script executed successfully"
    else
        log_error "Script execution failed with exit code: $exit_code"
    fi

    return $exit_code
}

# Create a VAR template (enhanced GET template for variable collection)
create_var_template() {
    local template_name="$1"
    local template_title="$2"
    local variables_list="$3"

    # Use the STORY system from variable-manager
    create_story "$template_name" "$template_title" "$variables_list"
}

# Execute VAR template to populate variables
execute_var_template() {
    local template_name="$1"
    local session_id="${2:-current}"

    local story_file="$STORY_DIR/${template_name}.json"
    execute_story "$story_file" "$session_id"
}

# uSCRIPT command integration
uscript_variable_command() {
    local action="$1"
    shift

    case "$action" in
        "LOAD")
            # Load variables into current session
            local session_id="${1:-current}"
            export_variables_to_environment "$session_id"
            ;;
        "SAVE")
            # Save current environment variables to session
            local session_id="${1:-current}"
            import_variables_from_environment "$session_id"
            ;;
        "EXEC")
            # Execute script with variable substitution
            local script_file="$1"
            local session_id="${2:-current}"
            execute_with_variables "$script_file" "$session_id"
            ;;
        "TEMPLATE")
            # Create variable-aware script template
            local script_name="$1"
            local script_type="${2:-bash}"
            local variables_list="${3:-}"
            create_variable_script "$script_name" "$script_type" "$variables_list"
            ;;
        "STORY")
            # Work with STORY templates
            local story_action="$1"
            shift
            case "$story_action" in
                "CREATE")
                    create_var_template "$@"
                    ;;
                "EXECUTE")
                    execute_var_template "$@"
                    ;;
                *)
                    log_error "Unknown STORY action: $story_action"
                    echo "STORY actions: CREATE, EXECUTE"
                    ;;
            esac
            ;;
        *)
            log_error "Unknown variable action: $action"
            echo "Variable actions: LOAD, SAVE, EXEC, TEMPLATE, STORY"
            ;;
    esac
}

# Main entry point for uSCRIPT integration
main() {
    if [[ "${1:-}" == "VAR" ]]; then
        shift
        uscript_variable_command "$@"
    else
        # Pass through to variable manager
        "$VARIABLE_MANAGER" "$@"
    fi
}

# Execute if called directly
if [[ "${BASH_SOURCE[0]}" == "${0}" ]]; then
    main "$@"
fi
