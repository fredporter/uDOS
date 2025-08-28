#!/bin/bash
# uDOS Variable Manager
# Central system for managing $VARIABLE definitions and user-defined variables
# Supports STORY-based input collection for variable population

set -euo pipefail

# Configuration
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
UDOS_ROOT="$(cd "$SCRIPT_DIR/../.." && pwd)"
VARIABLE_DIR="$UDOS_ROOT/uMEMORY/system/variables"
USER_VARIABLE_DIR="$UDOS_ROOT/uMEMORY/user/variables"
STORY_DIR="$UDOS_ROOT/uMEMORY/system/stories"

# Create required directories
mkdir -p "$VARIABLE_DIR" "$USER_VARIABLE_DIR" "$STORY_DIR"

# Source logging functions
source "$SCRIPT_DIR/logging.sh" 2>/dev/null || {
    log_info() { echo -e "\033[0;36m[INFO]\033[0m $1"; }
    log_success() { echo -e "\033[0;32m[SUCCESS]\033[0m $1"; }
    log_warning() { echo -e "\033[0;33m[WARNING]\033[0m $1"; }
    log_error() { echo -e "\033[0;31m[ERROR]\033[0m $1"; }
}

# Initialize system variables registry
init_system_variables() {
    local system_vars_file="$VARIABLE_DIR/system-variables.json"

    if [[ ! -f "$system_vars_file" ]]; then
        cat > "$system_vars_file" << 'EOF'
{
    "metadata": {
        "name": "uDOS System Variables",
        "version": "1.0.4.1",
        "type": "system",
        "created": "2025-08-26T00:00:00Z"
    },
    "variables": {
        "USER-ROLE": {
            "type": "string",
            "default": "GHOST",
            "values": ["GHOST", "TOMB", "CRYPT", "DRONE", "KNIGHT", "IMP", "SORCERER", "WIZARD"],
            "description": "Current user role level (10-100)",
            "scope": "system",
            "required": true
        },
        "DISPLAY-MODE": {
            "type": "string",
            "default": "CLI",
            "values": ["CLI", "DESKTOP", "WEB"],
            "description": "Display system mode",
            "scope": "system",
            "required": true
        },
        "MAX-RESOLUTION": {
            "type": "string",
            "default": "1280x720",
            "pattern": "^[0-9]+x[0-9]+$",
            "description": "Maximum display resolution",
            "scope": "display",
            "required": false
        },
        "GRID-SIZE": {
            "type": "string",
            "default": "80x30",
            "pattern": "^[0-9]+x[0-9]+$",
            "description": "Grid dimensions for display",
            "scope": "display",
            "required": false
        },
        "DETAIL-LEVEL": {
            "type": "string",
            "default": "STANDARD",
            "values": ["MINIMAL", "STANDARD", "DETAILED", "VERBOSE"],
            "description": "Information detail level",
            "scope": "display",
            "required": false
        },
        "TILE-CODE": {
            "type": "string",
            "default": "00AA00",
            "pattern": "^[0-9A-F]{6}$",
            "description": "Geographic tile location code",
            "scope": "geo",
            "required": false
        },
        "PROJECT-NAME": {
            "type": "string",
            "default": "",
            "description": "Current project identifier",
            "scope": "project",
            "required": false
        },
        "SESSION-ID": {
            "type": "string",
            "default": "",
            "pattern": "^[A-F0-9]{8}$",
            "description": "Current session identifier",
            "scope": "session",
            "required": false
        }
    }
}
EOF
        log_success "System variables registry initialized"
    fi
}

# Initialize user variables registry
init_user_variables() {
    local user_vars_file="$USER_VARIABLE_DIR/user-variables.json"

    if [[ ! -f "$user_vars_file" ]]; then
        cat > "$user_vars_file" << 'EOF'
{
    "metadata": {
        "name": "User Defined Variables",
        "version": "1.0.0",
        "type": "user",
        "created": "2025-08-26T00:00:00Z"
    },
    "variables": {}
}
EOF
        log_success "User variables registry initialized"
    fi
}

# Define a new variable (system or user)
define_variable() {
    local var_name="$1"
    local var_type="$2"
    local var_default="${3:-}"
    local var_scope="${4:-user}"
    local var_description="${5:-User defined variable}"
    local var_values="${6:-}"
    local var_pattern="${7:-}"

    # Determine target file
    local target_file
    if [[ "$var_scope" == "system" ]]; then
        target_file="$VARIABLE_DIR/system-variables.json"
    else
        target_file="$USER_VARIABLE_DIR/user-variables.json"
    fi

    # Build variable definition
    local var_def="{\"type\": \"$var_type\", \"default\": \"$var_default\", \"description\": \"$var_description\", \"scope\": \"$var_scope\", \"required\": false"

    if [[ -n "$var_values" ]]; then
        var_def+=", \"values\": $(echo "$var_values" | jq -R 'split(",")')"
    fi

    if [[ -n "$var_pattern" ]]; then
        var_def+=", \"pattern\": \"$var_pattern\""
    fi

    var_def+="}"

    # Update variables file
    local updated_vars
    updated_vars=$(jq --arg name "$var_name" --argjson def "$var_def" \
        '.variables[$name] = $def' "$target_file")
    echo "$updated_vars" > "$target_file"

    log_success "Variable \$$var_name defined in $var_scope scope"
}

# Get variable definition
get_variable() {
    local var_name="$1"
    local scope="${2:-auto}"

    # Check system variables first
    local system_vars_file="$VARIABLE_DIR/system-variables.json"
    if [[ -f "$system_vars_file" ]]; then
        local system_var
        system_var=$(jq -r ".variables[\"$var_name\"] // empty" "$system_vars_file")
        if [[ -n "$system_var" && "$system_var" != "null" ]]; then
            echo "$system_var"
            return 0
        fi
    fi

    # Check user variables
    local user_vars_file="$USER_VARIABLE_DIR/user-variables.json"
    if [[ -f "$user_vars_file" ]]; then
        local user_var
        user_var=$(jq -r ".variables[\"$var_name\"] // empty" "$user_vars_file")
        if [[ -n "$user_var" && "$user_var" != "null" ]]; then
            echo "$user_var"
            return 0
        fi
    fi

    log_error "Variable \$$var_name not found"
    return 1
}

# Set variable value
set_variable() {
    local var_name="$1"
    local var_value="$2"
    local session_id="${3:-current}"

    # Create session-specific values file
    local values_file="$USER_VARIABLE_DIR/values-${session_id}.json"

    if [[ ! -f "$values_file" ]]; then
        echo '{"values": {}}' > "$values_file"
    fi

    # Update value
    local updated_values
    updated_values=$(jq --arg name "$var_name" --arg value "$var_value" \
        '.values[$name] = $value' "$values_file")
    echo "$updated_values" > "$values_file"

    # Export to environment if variable is configured for export
    export_variable_to_environment "$var_name" "$var_value"

    log_success "Variable \$$var_name set to: $var_value"
}

# Export variable to environment based on system configuration
export_variable_to_environment() {
    local var_name="$1"
    local var_value="$2"

    # Check if this variable should be exported
    local var_def
    var_def=$(get_variable "$var_name" 2>/dev/null)
    if [[ $? -eq 0 ]]; then
        local should_export
        should_export=$(echo "$var_def" | jq -r '.export_to_env // false')

        if [[ "$should_export" == "true" ]]; then
            local env_name
            env_name=$(echo "$var_def" | jq -r '.env_name // ""')

            if [[ -n "$env_name" ]]; then
                export "$env_name"="$var_value"
                log_info "Exported to environment: $env_name=$var_value"
            fi
        fi
    fi
}

# Get variable value
get_variable_value() {
    local var_name="$1"
    local session_id="${2:-current}"

    # Check session values first
    local values_file="$USER_VARIABLE_DIR/values-${session_id}.json"
    if [[ -f "$values_file" ]]; then
        local session_value
        session_value=$(jq -r ".values[\"$var_name\"] // empty" "$values_file")
        if [[ -n "$session_value" && "$session_value" != "null" ]]; then
            echo "$session_value"
            return 0
        fi
    fi

    # Fall back to default value from definition
    local var_def
    var_def=$(get_variable "$var_name")
    if [[ $? -eq 0 ]]; then
        local default_value
        default_value=$(echo "$var_def" | jq -r '.default // ""')
        echo "$default_value"
        return 0
    fi

    log_error "Variable \$$var_name has no value"
    return 1
}

# Create a STORY template for variable collection
create_story() {
    local story_name="$1"
    local story_title="$2"
    local variables_list="$3"  # Comma-separated list of variable names

    local story_file="$STORY_DIR/${story_name}.json"

    # Convert variables list to array
    IFS=',' read -ra vars <<< "$variables_list"

    # Build story structure
    local story_json='{
        "metadata": {
            "name": "'$story_name'",
            "title": "'$story_title'",
            "type": "story",
            "created": "'$(date -u +%Y-%m-%dT%H:%M:%SZ)'"
        },
        "story": {
            "introduction": "",
            "context": "",
            "purpose": ""
        },
        "variables": [],
        "flow": {
            "sequential": true,
            "allow_skip": false,
            "validate_each": true
        }
    }'

    # Add variables to story
    for var in "${vars[@]}"; do
        var=$(echo "$var" | tr -d ' ')  # Remove spaces
        local var_def
        var_def=$(get_variable "$var" 2>/dev/null || echo '{"type": "string", "description": "User variable"}')

        local story_var
        story_var=$(echo "$var_def" | jq --arg name "$var" '{
            name: $name,
            type: .type,
            description: .description,
            required: (.required // false),
            values: (.values // []),
            pattern: (.pattern // ""),
            prompt: "",
            help: ""
        }')

        story_json=$(echo "$story_json" | jq --argjson var "$story_var" '.variables += [$var]')
    done

    echo "$story_json" > "$story_file"
    log_success "STORY template created: $story_file"
    echo "$story_file"
}

# Execute a STORY to collect variable values
execute_story() {
    local story_file="$1"
    local session_id="${2:-current}"

    if [[ ! -f "$story_file" ]]; then
        log_error "STORY file not found: $story_file"
        return 1
    fi

    # Read story metadata
    local story_title
    story_title=$(jq -r '.metadata.title' "$story_file")

    local story_intro
    story_intro=$(jq -r '.story.introduction // ""' "$story_file")

    local story_context
    story_context=$(jq -r '.story.context // ""' "$story_file")

    # Display story introduction
    echo ""
    echo "📖 STORY: $story_title"
    echo "════════════════════════════════════════"

    if [[ -n "$story_intro" && "$story_intro" != "null" ]]; then
        echo "$story_intro"
        echo ""
    fi

    if [[ -n "$story_context" && "$story_context" != "null" ]]; then
        echo "Context: $story_context"
        echo ""
    fi

    # Process each variable in the story
    local var_count
    var_count=$(jq '.variables | length' "$story_file")

    for ((i=0; i<var_count; i++)); do
        local var_info
        var_info=$(jq ".variables[$i]" "$story_file")

        local var_name
        var_name=$(echo "$var_info" | jq -r '.name')

        local var_prompt
        var_prompt=$(echo "$var_info" | jq -r '.prompt // .description')

        local var_type
        var_type=$(echo "$var_info" | jq -r '.type')

        local var_values
        var_values=$(echo "$var_info" | jq -r '.values // [] | join("|")')

        local var_required
        var_required=$(echo "$var_info" | jq -r '.required // false')

        local var_help
        var_help=$(echo "$var_info" | jq -r '.help // ""')

        # Collect variable value using enhanced CLI smart input
        local var_value=""
        local smart_input_cli="$SCRIPT_DIR/smart-input/smart-input-simple.sh"

        if [[ -x "$smart_input_cli" ]]; then
            if [[ -n "$var_values" && "$var_values" != "" ]]; then
                # Use enhanced CLI for selection with predefined values
                var_value=$("$smart_input_cli" collect "$var_name" "$var_type" "$var_prompt" "$var_help" "$var_values")
            else
                # Use enhanced CLI for free text input
                var_value=$("$smart_input_cli" collect "$var_name" "$var_type" "$var_prompt" "$var_help" "")
            fi
        else
            # Fallback to basic prompt
            echo "$var_prompt"
            if [[ -n "$var_help" ]]; then
                echo "💡 $var_help"
            fi
            echo -n "❯ "
            read -r var_value
        fi

        # Set variable value if collected successfully
        if [[ -n "$var_value" ]]; then
            set_variable "$var_name" "$var_value" "$session_id"
        fi

        echo ""
    done

    echo "✅ STORY completed: All variables collected"
    log_success "STORY executed: $story_title -> session $session_id"
}

# List all defined variables
list_variables() {
    local scope="${1:-all}"

    echo ""
    echo "📊 Variable Registry"
    echo "══════════════════════"

    if [[ "$scope" == "all" || "$scope" == "system" ]]; then
        echo ""
        echo "🔧 SYSTEM VARIABLES:"
        if [[ -f "$VARIABLE_DIR/system-variables.json" ]]; then
            jq -r '.variables | to_entries[] | "  $" + .key + " (" + .value.type + ") - " + .value.description' \
                "$VARIABLE_DIR/system-variables.json"
        fi
    fi

    if [[ "$scope" == "all" || "$scope" == "user" ]]; then
        echo ""
        echo "👤 USER VARIABLES:"
        if [[ -f "$USER_VARIABLE_DIR/user-variables.json" ]]; then
            local user_count
            user_count=$(jq '.variables | length' "$USER_VARIABLE_DIR/user-variables.json")
            if [[ $user_count -gt 0 ]]; then
                jq -r '.variables | to_entries[] | "  $" + .key + " (" + .value.type + ") - " + .value.description' \
                    "$USER_VARIABLE_DIR/user-variables.json"
            else
                echo "  (No user variables defined)"
            fi
        fi
    fi
    echo ""
}

# Validate variable value against definition
validate_variable() {
    local var_name="$1"
    local var_value="$2"

    local var_def
    var_def=$(get_variable "$var_name")
    if [[ $? -ne 0 ]]; then
        return 1
    fi

    local var_type
    var_type=$(echo "$var_def" | jq -r '.type')

    local var_pattern
    var_pattern=$(echo "$var_def" | jq -r '.pattern // ""')

    local var_values
    var_values=$(echo "$var_def" | jq -r '.values // []')

    # Type validation
    case "$var_type" in
        "number")
            if ! [[ "$var_value" =~ ^[0-9]+$ ]]; then
                log_error "Variable \$$var_name must be a number"
                return 1
            fi
            ;;
        "string")
            # Basic string validation
            ;;
    esac

    # Pattern validation
    if [[ -n "$var_pattern" && "$var_pattern" != "null" ]]; then
        if ! [[ "$var_value" =~ $var_pattern ]]; then
            log_error "Variable \$$var_name does not match pattern: $var_pattern"
            return 1
        fi
    fi

    # Values validation
    if [[ "$var_values" != "null" && "$var_values" != "[]" ]]; then
        local valid_values
        valid_values=$(echo "$var_values" | jq -r '.[]' | tr '\n' '|' | sed 's/|$//')
        if [[ "$valid_values" =~ $var_value ]]; then
            return 0
        else
            log_error "Variable \$$var_name must be one of: $valid_values"
            return 1
        fi
    fi

    return 0
}

# Main command dispatcher
main() {
    # Initialize system
    init_system_variables
    init_user_variables

    # Initialize environment exports if available
    local export_script="$VARIABLE_DIR/export-variables.sh"
    if [[ -f "$export_script" && -x "$export_script" ]]; then
        source "$export_script"
    fi

    case "${1:-LIST}" in
        "DEFINE")
            [[ $# -lt 3 ]] && { echo "Usage: variable-manager.sh DEFINE <name> <type> [default] [scope] [description] [values] [pattern]" >&2; exit 1; }
            define_variable "$2" "$3" "${4:-}" "${5:-user}" "${6:-User defined variable}" "${7:-}" "${8:-}"
            ;;
        "SET")
            [[ $# -lt 3 ]] && { echo "Usage: variable-manager.sh SET <name> <value> [session]" >&2; exit 1; }
            set_variable "$2" "$3" "${4:-current}"
            ;;
        "GET")
            [[ $# -lt 2 ]] && { echo "Usage: variable-manager.sh GET <name> [session]" >&2; exit 1; }
            get_variable_value "$2" "${3:-current}"
            ;;
        "DEF")
            [[ $# -lt 2 ]] && { echo "Usage: variable-manager.sh DEF <name>" >&2; exit 1; }
            get_variable "$2"
            ;;
        "STORY")
            case "${2:-}" in
                "CREATE")
                    [[ $# -lt 5 ]] && { echo "Usage: variable-manager.sh STORY CREATE <name> <title> <variables>" >&2; exit 1; }
                    create_story "$3" "$4" "$5"
                    ;;
                "EXECUTE")
                    [[ $# -lt 3 ]] && { echo "Usage: variable-manager.sh STORY EXECUTE <story_file> [session]" >&2; exit 1; }
                    execute_story "$3" "${4:-current}"
                    ;;
                *)
                    echo "STORY subcommands: CREATE, EXECUTE"
                    ;;
            esac
            ;;
        "VALIDATE")
            [[ $# -lt 3 ]] && { echo "Usage: variable-manager.sh VALIDATE <name> <value>" >&2; exit 1; }
            validate_variable "$2" "$3"
            ;;
        "LIST")
            list_variables "${2:-all}"
            ;;
        *)
            echo "Commands: DEFINE, SET, GET, DEF, STORY, VALIDATE, LIST"
            ;;
    esac
}

# Execute main with all arguments
main "$@"
