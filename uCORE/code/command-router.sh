#!/bin/bash
# uDOS Command Router v1.0.4.1
# Central command processing system for uCODE syntax [COMMAND|ACTION*params]
# Phase 1 Implementation - Core Router with Role-Based Access

set -euo pipefail

# Configuration
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
UDOS_ROOT="$(cd "$SCRIPT_DIR/../.." && pwd)"

# Source dependencies
source "$SCRIPT_DIR/logging.sh" 2>/dev/null || {
    log_info() { echo -e "\033[0;36m[INFO]\033[0m $1"; }
    log_success() { echo -e "\033[0;32m[SUCCESS]\033[0m $1"; }
    log_warning() { echo -e "\033[0;33m[WARNING]\033[0m $1"; }
    log_error() { echo -e "\033[0;31m[ERROR]\033[0m $1"; }
}

# ════════════════════════════════════════════════════════════════
# 🎯 CORE COMMAND PARSING
# ════════════════════════════════════════════════════════════════

# Parse uCODE command syntax: [COMMAND|ACTION*params]
parse_ucode_command() {
    local input="$1"

    # Remove brackets and extract content
    if [[ "$input" =~ ^\[([^\]]+)\]$ ]]; then
        local content="${BASH_REMATCH[1]}"

        # Split on | for COMMAND|ACTION
        if [[ "$content" =~ ^([^|]+)\|(.+)$ ]]; then
            local command="${BASH_REMATCH[1]}"
            local action_params="${BASH_REMATCH[2]}"

            # Split on * for ACTION*params
            local action=""
            local params=""
            if [[ "$action_params" =~ ^([^*]+)\*(.*)$ ]]; then
                action="${BASH_REMATCH[1]}"
                params="${BASH_REMATCH[2]}"
            else
                action="$action_params"
            fi

            echo "COMMAND=$command"
            echo "ACTION=$action"
            echo "PARAMS=$params"
        else
            # Single command without action
            echo "COMMAND=$content"
            echo "ACTION="
            echo "PARAMS="
        fi
    else
        log_error "Invalid uCODE syntax. Expected format: [COMMAND|ACTION*params]"
        return 1
    fi
}

# ════════════════════════════════════════════════════════════════
# 🔐 ROLE-BASED ACCESS CONTROL
# ════════════════════════════════════════════════════════════════

# Load current user role
get_current_role() {
    local role_file="$UDOS_ROOT/sandbox/current-role.conf"

    if [[ -f "$role_file" ]]; then
        grep "^ROLE=" "$role_file" 2>/dev/null | cut -d'=' -f2 | tr -d '"' || echo "GHOST"
    else
        echo "GHOST"
    fi
}

# Get role permission level (10-100)
get_role_level() {
    local role="$1"

    case "$role" in
        "GHOST") echo "10" ;;
        "TOMB") echo "20" ;;
        "CRYPT") echo "30" ;;
        "DRONE") echo "40" ;;
        "KNIGHT") echo "50" ;;
        "IMP") echo "60" ;;
        "SORCERER") echo "80" ;;
        "WIZARD") echo "100" ;;
        *) echo "0" ;;
    esac
}

# Check if role has permission for command
check_permission() {
    local command="$1"
    local action="$2"
    local current_role=$(get_current_role)
    local required_level=10  # Default minimum level

    # Command-specific permission requirements
    case "$command" in
        "ASSIST")
            case "$action" in
                "ENTER"|"EXIT"|"NEXT") required_level=40 ;;  # DRONE+
                "FINALIZE"|"ROADMAP") required_level=60 ;;   # IMP+
            esac
            ;;
        "SYSTEM")
            case "$action" in
                "STATUS"|"HELP") required_level=10 ;;        # GHOST+
                "CONFIGURE") required_level=80 ;;            # SORCERER+
                "MODIFY") required_level=100 ;;              # WIZARD only
            esac
            ;;
        "GET"|"SET")
            required_level=20 ;;  # TOMB+ for variable operations
            ;;
        "ROLE")
            required_level=50 ;;  # KNIGHT+ for role management
            ;;
        *)
            required_level=10 ;;  # Default access for most commands
            ;;
    esac

    local current_level=$(get_role_level "$current_role")

    if (( current_level >= required_level )); then
        return 0
    else
        log_error "Insufficient permissions. Required: level $required_level, Current: $current_role (level $current_level)"
        return 1
    fi
}

# ════════════════════════════════════════════════════════════════
# 🎯 COMMAND ROUTING
# ════════════════════════════════════════════════════════════════

# Route command to appropriate handler
route_command() {
    local command="$1"
    local action="$2"
    local params="$3"

    case "$command" in
        "ASSIST")
            handle_assist_command "$action" "$params"
            ;;
        "GET"|"SET")
            handle_variable_command "$command" "$action" "$params"
            ;;
        "SYSTEM")
            handle_system_command "$action" "$params"
            ;;
        "ROLE")
            handle_role_command "$action" "$params"
            ;;
        "HELP")
            handle_help_command "$action" "$params"
            ;;
        *)
            log_error "Unknown command: $command"
            echo "Use [HELP] to see available commands"
            return 1
            ;;
    esac
}

# ════════════════════════════════════════════════════════════════
# 📋 COMMAND HANDLERS
# ════════════════════════════════════════════════════════════════

# Handle ASSIST mode commands
handle_assist_command() {
    local action="$1"
    local params="$2"

    case "$action" in
        "ENTER")
            set_assist_mode "enabled"
            log_success "ASSIST mode activated"
            ;;
        "EXIT")
            set_assist_mode "disabled"
            log_success "ASSIST mode deactivated"
            ;;
        "FINALIZE")
            log_info "🚀 Session finalization would execute here"
            log_info "Features: Auto-commit, session logging, git push"
            ;;
        "NEXT")
            log_info "🎯 Next task recommendation would appear here"
            log_info "Based on: Current roadmap progress and system state"
            ;;
        "ROADMAP")
            log_info "📋 Roadmap update would execute here"
            log_info "Features: Progress tracking, milestone updates"
            ;;
        *)
            log_error "Unknown ASSIST action: $action"
            echo "Available: ENTER, EXIT, FINALIZE, NEXT, ROADMAP"
            return 1
            ;;
    esac
}

# Handle variable commands (GET/SET)
handle_variable_command() {
    local command="$1"
    local action="$2"
    local params="$3"

    if [[ -f "$SCRIPT_DIR/variable-manager.sh" ]]; then
        case "$command" in
            "GET")
                log_info "Getting variable: $action"
                "$SCRIPT_DIR/variable-manager.sh" get "$action" 2>/dev/null || echo "Variable $action not found"
                ;;
            "SET")
                log_info "Setting variable: $action = $params"
                "$SCRIPT_DIR/variable-manager.sh" set "$action" "$params" 2>/dev/null || log_error "Failed to set variable"
                ;;
        esac
    else
        log_warning "Variable manager not found - feature will be available in Phase 4"
        echo "Command would execute: $command $action $params"
    fi
}

# Handle system commands
handle_system_command() {
    local action="$1"
    local params="$2"

    case "$action" in
        "STATUS")
            show_system_status
            ;;
        "HELP")
            show_system_help
            ;;
        "")
            show_system_status  # Default to status if no action
            ;;
        *)
            log_error "Unknown SYSTEM action: $action"
            echo "Available: STATUS, HELP"
            return 1
            ;;
    esac
}

# Handle role commands
handle_role_command() {
    local action="$1"
    local params="$2"
    local current_role=$(get_current_role)

    case "$action" in
        "GET"|"")
            echo "Current role: $current_role (Level $(get_role_level "$current_role"))"
            ;;
        "SET")
            if [[ -n "$params" ]]; then
                log_info "Role change requested: $current_role → $params"
                log_warning "Role SET functionality coming in Phase 2"
            else
                log_error "Role SET requires parameter"
                echo "Usage: [ROLE|SET*WIZARD]"
                return 1
            fi
            ;;
        *)
            log_error "Unknown ROLE action: $action"
            echo "Available: GET, SET"
            return 1
            ;;
    esac
}

# Handle help commands
handle_help_command() {
    local action="$1"
    local params="$2"

    if [[ -n "$action" ]]; then
        show_command_help "$action"
    else
        show_general_help
    fi
}

# ════════════════════════════════════════════════════════════════
# 🛠️ UTILITY FUNCTIONS
# ════════════════════════════════════════════════════════════════

# Get ASSIST mode status
get_assist_mode() {
    local assist_file="$UDOS_ROOT/sandbox/assist-mode.conf"
    if [[ -f "$assist_file" ]]; then
        grep "ASSIST_MODE=" "$assist_file" 2>/dev/null | cut -d'=' -f2 | tr -d '"' || echo "disabled"
    else
        echo "disabled"
    fi
}

# Set ASSIST mode status
set_assist_mode() {
    local mode="$1"
    local assist_file="$UDOS_ROOT/sandbox/assist-mode.conf"
    mkdir -p "$(dirname "$assist_file")"
    echo "ASSIST_MODE=\"$mode\"" > "$assist_file"
    echo "TIMESTAMP=\"$(date '+%Y-%m-%d %H:%M:%S %Z')\"" >> "$assist_file"
}

# Show system status
show_system_status() {
    local current_role=$(get_current_role)
    local assist_mode=$(get_assist_mode)

    echo "═══════════════════════════════════════"
    echo "🎯 uDOS System Status"
    echo "═══════════════════════════════════════"
    echo "Version: 1.0.4.1"
    echo "Role: $current_role (Level $(get_role_level "$current_role"))"
    echo "ASSIST Mode: $assist_mode"
    echo "Command Router: Phase 1 Active"
    echo "uCODE Syntax: Operational"
    echo "═══════════════════════════════════════"
}

# Show general help
show_general_help() {
    echo "🚀 uDOS Command Router - uCODE Syntax v1.0.4.1"
    echo "Format: [COMMAND|ACTION*params]"
    echo ""
    echo "📋 Available Commands:"
    echo "  [ASSIST|ENTER]       - Activate ASSIST mode (DRONE+)"
    echo "  [ASSIST|EXIT]        - Deactivate ASSIST mode (DRONE+)"
    echo "  [ASSIST|FINALIZE]    - Auto-commit session (IMP+)"
    echo "  [ASSIST|NEXT]        - Get next task recommendation (DRONE+)"
    echo "  [ASSIST|ROADMAP]     - Update roadmap progress (IMP+)"
    echo "  [SYSTEM|STATUS]      - Show system status (GHOST+)"
    echo "  [SYSTEM|HELP]        - Show system help (GHOST+)"
    echo "  [ROLE|GET]           - Show current role (KNIGHT+)"
    echo "  [ROLE|SET*WIZARD]    - Set role (KNIGHT+)"
    echo "  [GET|variable]       - Get variable value (TOMB+)"
    echo "  [SET|variable*value] - Set variable value (TOMB+)"
    echo "  [HELP]               - Show this help (GHOST+)"
    echo ""
    echo "📖 Examples:"
    echo "  ./command-router.sh \"[SYSTEM|STATUS]\""
    echo "  ./command-router.sh \"[ASSIST|ENTER]\""
    echo "  ./command-router.sh \"[SET|USER-NAME*John]\""
}

# Show system help
show_system_help() {
    echo "🔧 uDOS System Commands"
    echo "Available SYSTEM actions:"
    echo "  STATUS - Show current system status"
    echo "  HELP   - Show system command help"
}

# Show command-specific help
show_command_help() {
    local command="$1"

    case "$command" in
        "ASSIST")
            echo "🧠 ASSIST Mode Commands"
            echo "  ENTER    - Activate ASSIST mode"
            echo "  EXIT     - Deactivate ASSIST mode"
            echo "  FINALIZE - Auto-commit and finalize session"
            echo "  NEXT     - Get next development task recommendation"
            echo "  ROADMAP  - Update roadmap progress"
            ;;
        "SYSTEM")
            show_system_help
            ;;
        "ROLE")
            echo "👤 Role Management Commands"
            echo "  GET      - Show current role and level"
            echo "  SET*role - Change to specified role"
            ;;
        *)
            log_warning "No specific help available for: $command"
            echo "Use [HELP] for general command list"
            ;;
    esac
}

# ════════════════════════════════════════════════════════════════
# 🚀 MAIN EXECUTION
# ════════════════════════════════════════════════════════════════

main() {
    # Check if command provided
    if [[ $# -eq 0 ]]; then
        log_error "No command provided"
        show_general_help
        exit 1
    fi

    local input="$1"

    # Parse command
    local parse_result
    if ! parse_result=$(parse_ucode_command "$input"); then
        exit 1
    fi

    # Extract parsed components
    local command=$(echo "$parse_result" | grep "COMMAND=" | cut -d'=' -f2)
    local action=$(echo "$parse_result" | grep "ACTION=" | cut -d'=' -f2)
    local params=$(echo "$parse_result" | grep "PARAMS=" | cut -d'=' -f2)

    # Validate command format
    if [[ -z "$command" ]]; then
        log_error "Command cannot be empty"
        exit 1
    fi

    # Check permissions
    if ! check_permission "$command" "$action"; then
        exit 1
    fi

    # Route and execute command
    if route_command "$command" "$action" "$params"; then
        log_success "Command executed successfully: [$command|$action${params:+*$params}]"
    else
        log_error "Command execution failed"
        exit 1
    fi
}

# Execute main function if script is run directly
if [[ "${BASH_SOURCE[0]}" == "${0}" ]]; then
    main "$@"
fi
