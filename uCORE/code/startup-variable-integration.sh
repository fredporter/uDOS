#!/bin/bash
# Startup Variable Integration - Connects variables with startup stories
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
UDOS_ROOT="$(cd "$SCRIPT_DIR/../.." && pwd)"

# Load variable values and apply them to startup stories
integrate_startup_variables() {
    local role="$1"
    local session_id="${2:-startup-$(date +%s)}"

    # Get role-specific variables
    local role_lower=$(echo "$role" | tr '[:upper:]' '[:lower:]')
    local role_config="$UDOS_ROOT/uMEMORY/system/role-configs/${role_lower}-variables.json"

    if [[ -f "$role_config" ]]; then
        echo "🔧 Applying $role role-specific variable configurations..."

        # Apply each variable from role config as a system default
        jq -r '.variables | to_entries[] | "\(.key)=\(.value.default)"' "$role_config" | while IFS='=' read -r var_name var_value; do
            if [[ -n "$var_name" && -n "$var_value" ]]; then
                "$UDOS_ROOT/uCORE/code/variable-manager.sh" SET "$var_name" "$var_value" "$session_id"
            fi
        done

        echo "✅ Role-specific variables applied for $role"
    fi

    # Apply install-time variables
    local install_config="$UDOS_ROOT/uMEMORY/system/install-configs/install-system-variables.json"
    if [[ -f "$install_config" ]]; then
        echo "🔧 Applying install-time variable configurations..."

        jq -r '.variables | to_entries[] | "\(.key)=\(.value.default)"' "$install_config" | while IFS='=' read -r var_name var_value; do
            if [[ -n "$var_name" && -n "$var_value" ]]; then
                "$UDOS_ROOT/uCORE/code/variable-manager.sh" SET "$var_name" "$var_value" "$session_id"
            fi
        done

        echo "✅ Install-time variables applied"
    fi
}

# Check if startup story should run automatically
should_run_startup_story() {
    local role="$1"

    # Get STARTUP-STORY-AUTO setting
    local auto_setting=$("$UDOS_ROOT/uCORE/code/variable-manager.sh" GET "STARTUP-STORY-AUTO" 2>/dev/null || echo "first-run-only")

    case "$auto_setting" in
        "always")
            return 0
            ;;
        "first-run-only")
            # Check if this is first run for this role
            local role_lower=$(echo "$role" | tr '[:upper:]' '[:lower:]')
            local role_marker="$UDOS_ROOT/sandbox/.${role_lower}-startup-complete"
            [[ ! -f "$role_marker" ]]
            ;;
        "role-change")
            # Check if role has changed since last startup
            local last_startup_role=$(cat "$UDOS_ROOT/sandbox/.last-startup-role" 2>/dev/null || echo "")
            [[ "$role" != "$last_startup_role" ]]
            ;;
        "manual"|"disabled")
            return 1
            ;;
        *)
            return 1
            ;;
    esac
}

# Mark startup story as complete for role
mark_startup_complete() {
    local role="$1"
    local role_lower=$(echo "$role" | tr '[:upper:]' '[:lower:]')
    local role_marker="$UDOS_ROOT/sandbox/.${role_lower}-startup-complete"

    echo "$(date '+%Y-%m-%d %H:%M:%S')" > "$role_marker"
    echo "$role" > "$UDOS_ROOT/sandbox/.last-startup-role"
}

# Main integration function
main() {
    local command="${1:-integrate}"
    local role="${2:-$(cat "$UDOS_ROOT/sandbox/current-role.conf" | grep "^ROLE=" | cut -d'=' -f2 | tr -d '"' || echo "GHOST")}"

    case "$command" in
        "integrate")
            integrate_startup_variables "$role"
            ;;
        "should-run")
            should_run_startup_story "$role"
            ;;
        "mark-complete")
            mark_startup_complete "$role"
            ;;
        *)
            echo "Usage: $0 {integrate|should-run|mark-complete} [ROLE]"
            exit 1
            ;;
    esac
}

main "$@"
