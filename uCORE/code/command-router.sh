#!/bin/bash
# uDOS Command Router v1.0.4.1
# Central command processing system for uCODE syntax [COMMAND|ACTION*params]
# Phase 2 Implementation - Enhanced Role-Based Access Control

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
    # Use role manager for consistent role handling
    if [[ -f "$SCRIPT_DIR/role-manager.sh" ]]; then
        "$SCRIPT_DIR/role-manager.sh" get 2>/dev/null | grep "Role:" | cut -d' ' -f2 | tr -d ' \n\r' || echo "GHOST"
    else
        # Fallback to direct file reading
        local role_file="$UDOS_ROOT/uMEMORY/role/current.txt"
        if [[ -f "$role_file" ]]; then
            cat "$role_file" 2>/dev/null | tr -d ' \n\r' | tr '[:lower:]' '[:upper:]' || echo "GHOST"
        else
            echo "GHOST"
        fi
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

# Enhanced permission checking with detailed feedback
check_permission() {
    local command="$1"
    local action="$2"
    local current_role=$(get_current_role)
    local required_level=10  # Default minimum level
    local required_role=""

    # Command-specific permission requirements with enhanced granularity
    case "$command" in
        "ASSIST")
            case "$action" in
                "ENTER"|"EXIT"|"NEXT")
                    required_level=40
                    required_role="DRONE"
                    ;;
                "FINALIZE"|"ROADMAP")
                    required_level=60
                    required_role="IMP"
                    ;;
                "STATUS"|"HELP")
                    required_level=10
                    required_role="GHOST"
                    ;;
            esac
            ;;
        "SYSTEM")
            case "$action" in
                "STATUS"|"HELP"|"INFO")
                    required_level=10
                    required_role="GHOST"
                    ;;
                "CONFIGURE"|"SETTINGS")
                    required_level=80
                    required_role="SORCERER"
                    ;;
                "MODIFY"|"CORE")
                    required_level=100
                    required_role="WIZARD"
                    ;;
                "RESTART"|"MAINTENANCE")
                    required_level=60
                    required_role="IMP"
                    ;;
            esac
            ;;
        "GET"|"SET")
            case "$action" in
                "SYSTEM"|"CORE")
                    required_level=80
                    required_role="SORCERER"
                    ;;
                *)
                    required_level=20
                    required_role="TOMB"
                    ;;
            esac
            ;;
        "ROLE")
            case "$action" in
                "GET"|"STATUS")
                    required_level=10
                    required_role="GHOST"
                    ;;
                "SET"|"CHANGE")
                    required_level=50
                    required_role="KNIGHT"
                    ;;
                "FORCE"|"ADMIN")
                    required_level=80
                    required_role="SORCERER"
                    ;;
            esac
            ;;
        "DEV"|"DEVELOPMENT")
            required_level=100
            required_role="WIZARD"
            ;;
        "BACKUP"|"RESTORE")
            case "$action" in
                "CREATE"|"LIST")
                    required_level=30
                    required_role="CRYPT"
                    ;;
                "RESTORE"|"MANAGE")
                    required_level=50
                    required_role="KNIGHT"
                    ;;
            esac
            ;;
        "HELP"|"STATUS"|"INFO")
            required_level=10
            required_role="GHOST"
            ;;
        *)
            required_level=10
            required_role="GHOST"
            ;;
    esac

    local current_level=$(get_role_level "$current_role")

    if (( current_level >= required_level )); then
        return 0
    else
        # Enhanced error messaging
        log_error "Access denied: Insufficient permissions"
        echo "┌─ Permission Details ─────────────────────"
        echo "│ Command: $command${action:+|$action}"
        echo "│ Required: $required_role (Level $required_level+)"
        echo "│ Current: $current_role (Level $current_level)"
        echo "│ Action: Use [ROLE|SET*$required_role] to upgrade"
        echo "└─────────────────────────────────────────"
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

# Handle role commands with enhanced validation
handle_role_command() {
    local action="$1"
    local params="$2"
    local current_role=$(get_current_role)

    case "$action" in
        "GET"|"STATUS"|"")
            # Show comprehensive role status
            if [[ -f "$SCRIPT_DIR/role-manager.sh" ]]; then
                "$SCRIPT_DIR/role-manager.sh" status
            else
                echo "Current role: $current_role (Level $(get_role_level "$current_role"))"
                log_warning "Role manager not found - limited information available"
            fi
            ;;
        "SET"|"CHANGE")
            if [[ -z "$params" ]]; then
                log_error "Role SET requires target role parameter"
                echo "Usage: [ROLE|SET*WIZARD] or [ROLE|SET*DRONE]"
                if [[ -f "$SCRIPT_DIR/role-manager.sh" ]]; then
                    "$SCRIPT_DIR/role-manager.sh" list
                fi
                return 1
            fi

            # Validate and set role using role manager
            if [[ -f "$SCRIPT_DIR/role-manager.sh" ]]; then
                log_info "Processing role change request: $current_role → $params"

                # Check if this is a force operation
                local force_flag=""
                if [[ "$params" == *"|FORCE" ]]; then
                    local target_role="${params%|FORCE}"
                    force_flag="--force"
                    log_warning "Force flag detected - bypassing normal role transition checks"
                else
                    local target_role="$params"
                fi

                if "$SCRIPT_DIR/role-manager.sh" set "$target_role" $force_flag; then
                    log_success "Role successfully changed to $target_role"
                    # Refresh role in current session
                    export UDOS_CURRENT_ROLE="$target_role"
                else
                    log_error "Role change failed"
                    return 1
                fi
            else
                log_warning "Role manager not available - using legacy method"
                log_info "Legacy role change: $current_role → $params"

                # Create simple role file for backward compatibility
                mkdir -p "$UDOS_ROOT/sandbox"
                echo "ROLE=\"$params\"" > "$UDOS_ROOT/sandbox/current-role.conf"
                echo "TIMESTAMP=\"$(date '+%Y-%m-%d %H:%M:%S %Z')\"" >> "$UDOS_ROOT/sandbox/current-role.conf"

                log_success "Role set to $params (legacy mode)"
            fi
            ;;
        "LIST"|"AVAILABLE")
            # Show available roles
            if [[ -f "$SCRIPT_DIR/role-manager.sh" ]]; then
                "$SCRIPT_DIR/role-manager.sh" list
            else
                echo "📋 Available Roles:"
                echo "  GHOST (10) - Demo installation, read-only access"
                echo "  TOMB (20) - Basic storage and simple operations"
                echo "  CRYPT (30) - Secure storage and standard operations"
                echo "  DRONE (40) - Automation tasks and maintenance"
                echo "  KNIGHT (50) - Security functions and standard operations"
                echo "  IMP (60) - Development tools and automation"
                echo "  SORCERER (80) - Advanced administration and debugging"
                echo "  WIZARD (100) - Full development access and core system control"
            fi
            ;;
        "CAPABILITIES"|"PERMS")
            # Show role capabilities
            local target_role="${params:-$current_role}"
            if [[ -f "$SCRIPT_DIR/role-manager.sh" ]]; then
                "$SCRIPT_DIR/role-manager.sh" capabilities "$target_role"
            else
                echo "Role capabilities for $target_role (Level $(get_role_level "$target_role")):"
                log_warning "Role manager not found - limited capability information"
            fi
            ;;
        "VALIDATE"|"CHECK")
            # Validate role
            local target_role="${params:-$current_role}"
            if [[ -f "$SCRIPT_DIR/role-manager.sh" ]]; then
                "$SCRIPT_DIR/role-manager.sh" validate "$target_role"
            else
                local level=$(get_role_level "$target_role")
                if [[ $level -gt 0 ]]; then
                    log_success "Role '$target_role' is valid (Level $level)"
                else
                    log_error "Role '$target_role' is invalid"
                    return 1
                fi
            fi
            ;;
        *)
            log_error "Unknown ROLE action: $action"
            echo "Available actions:"
            echo "  GET/STATUS - Show current role information"
            echo "  SET*ROLE - Change to specified role"
            echo "  LIST - Show all available roles"
            echo "  CAPABILITIES*ROLE - Show role capabilities"
            echo "  VALIDATE*ROLE - Validate role name"
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

# Show enhanced system status
show_system_status() {
    local current_role=$(get_current_role)
    local assist_mode=$(get_assist_mode)
    local role_level=$(get_role_level "$current_role")

    echo "═══════════════════════════════════════"
    echo "🎯 uDOS System Status"
    echo "═══════════════════════════════════════"
    echo "Version: 1.0.4.1"
    echo "Command Router: Phase 2 Active"
    echo "uCODE Syntax: Enhanced"
    echo ""
    echo "👤 Session Information:"
    echo "  Role: $current_role (Level $role_level)"
    echo "  ASSIST Mode: $assist_mode"
    echo "  Role Manager: $([ -f "$SCRIPT_DIR/role-manager.sh" ] && echo "Available" || echo "Legacy Mode")"
    echo ""
    echo "🔑 Access Summary:"

    # Show quick capability overview based on current role
    case "$current_role" in
        "GHOST")
            echo "  ✅ Basic commands (HELP, STATUS)"
            echo "  ❌ Variable operations (requires TOMB+)"
            echo "  ❌ ASSIST mode (requires DRONE+)"
            echo "  ❌ Role management (requires KNIGHT+)"
            ;;
        "TOMB")
            echo "  ✅ Basic commands, Variable operations"
            echo "  ❌ ASSIST mode (requires DRONE+)"
            echo "  ❌ Role management (requires KNIGHT+)"
            ;;
        "CRYPT")
            echo "  ✅ Basic commands, Variable operations"
            echo "  ✅ Backup operations"
            echo "  ❌ ASSIST mode (requires DRONE+)"
            echo "  ❌ Role management (requires KNIGHT+)"
            ;;
        "DRONE")
            echo "  ✅ Basic commands, Variable operations"
            echo "  ✅ ASSIST basic (ENTER, EXIT, NEXT)"
            echo "  ❌ Role management (requires KNIGHT+)"
            echo "  ❌ ASSIST advanced (requires IMP+)"
            ;;
        "KNIGHT")
            echo "  ✅ Basic commands, Variable operations"
            echo "  ✅ ASSIST basic, Role management"
            echo "  ❌ ASSIST advanced (requires IMP+)"
            echo "  ❌ System configuration (requires SORCERER+)"
            ;;
        "IMP")
            echo "  ✅ All basic operations"
            echo "  ✅ ASSIST advanced (FINALIZE, ROADMAP)"
            echo "  ❌ System configuration (requires SORCERER+)"
            echo "  ❌ Core modification (requires WIZARD)"
            ;;
        "SORCERER")
            echo "  ✅ All standard operations"
            echo "  ✅ System configuration"
            echo "  ❌ Core modification (requires WIZARD)"
            ;;
        "WIZARD")
            echo "  ✅ Full system access"
            echo "  ✅ All operations available"
            echo "  ✅ Core system modification"
            echo "  ✅ Development environment access"
            ;;
    esac

    echo ""
    echo "🚀 Phase 2 Features:"
    echo "  ✅ Enhanced role validation"
    echo "  ✅ Detailed permission feedback"
    echo "  ✅ Role transition management"
    echo "  ✅ Comprehensive help system"
    echo "  ✅ Role capability analysis"
    echo "═══════════════════════════════════════"
}

# Show general help with Phase 2 enhancements
show_general_help() {
    local current_role=$(get_current_role)
    local current_level=$(get_role_level "$current_role")

    echo "🚀 uDOS Command Router - uCODE Syntax v1.0.4.1 (Phase 2)"
    echo "Format: [COMMAND|ACTION*params]"
    echo ""
    echo "� Current Session: $current_role (Level $current_level)"
    echo ""
    echo "�📋 Available Commands (Role Requirements):"

    # Basic commands (all roles)
    echo "┌─ Basic Commands (GHOST+) ─────────────────"
    echo "│ [HELP]               - Show this help"
    echo "│ [SYSTEM|STATUS]      - Show system status"
    echo "│ [SYSTEM|HELP]        - Show system help"
    echo "│ [ROLE|GET]           - Show current role"
    echo "└─────────────────────────────────────────"

    # Variable operations (TOMB+)
    if [[ $current_level -ge 20 ]]; then
        echo "┌─ Variable Operations (TOMB+) ─────────────"
        echo "│ [GET|variable]       - Get variable value"
        echo "│ [SET|variable*value] - Set variable value"
        echo "└─────────────────────────────────────────"
    else
        echo "┌─ Variable Operations (TOMB+ required) ────"
        echo "│ [GET|variable]       - ❌ Requires TOMB+"
        echo "│ [SET|variable*value] - ❌ Requires TOMB+"
        echo "└─────────────────────────────────────────"
    fi

    # ASSIST basic (DRONE+)
    if [[ $current_level -ge 40 ]]; then
        echo "┌─ ASSIST Basic (DRONE+) ───────────────────"
        echo "│ [ASSIST|ENTER]       - Activate ASSIST mode"
        echo "│ [ASSIST|EXIT]        - Deactivate ASSIST mode"
        echo "│ [ASSIST|NEXT]        - Get next task recommendation"
        echo "└─────────────────────────────────────────"
    else
        echo "┌─ ASSIST Basic (DRONE+ required) ──────────"
        echo "│ [ASSIST|ENTER]       - ❌ Requires DRONE+"
        echo "│ [ASSIST|EXIT]        - ❌ Requires DRONE+"
        echo "│ [ASSIST|NEXT]        - ❌ Requires DRONE+"
        echo "└─────────────────────────────────────────"
    fi

    # Role management (KNIGHT+)
    if [[ $current_level -ge 50 ]]; then
        echo "┌─ Role Management (KNIGHT+) ───────────────"
        echo "│ [ROLE|SET*WIZARD]    - Change to specified role"
        echo "│ [ROLE|LIST]          - List all available roles"
        echo "│ [ROLE|CAPABILITIES]  - Show role capabilities"
        echo "└─────────────────────────────────────────"
    else
        echo "┌─ Role Management (KNIGHT+ required) ──────"
        echo "│ [ROLE|SET*WIZARD]    - ❌ Requires KNIGHT+"
        echo "│ [ROLE|LIST]          - ❌ Requires KNIGHT+"
        echo "│ [ROLE|CAPABILITIES]  - ❌ Requires KNIGHT+"
        echo "└─────────────────────────────────────────"
    fi

    # ASSIST advanced (IMP+)
    if [[ $current_level -ge 60 ]]; then
        echo "┌─ ASSIST Advanced (IMP+) ──────────────────"
        echo "│ [ASSIST|FINALIZE]    - Auto-commit session"
        echo "│ [ASSIST|ROADMAP]     - Update roadmap progress"
        echo "└─────────────────────────────────────────"
    else
        echo "┌─ ASSIST Advanced (IMP+ required) ─────────"
        echo "│ [ASSIST|FINALIZE]    - ❌ Requires IMP+"
        echo "│ [ASSIST|ROADMAP]     - ❌ Requires IMP+"
        echo "└─────────────────────────────────────────"
    fi

    # System configuration (SORCERER+)
    if [[ $current_level -ge 80 ]]; then
        echo "┌─ System Configuration (SORCERER+) ────────"
        echo "│ [SYSTEM|CONFIGURE]   - Configure system settings"
        echo "│ [GET|SYSTEM*setting] - Get system variables"
        echo "│ [SET|SYSTEM*value]   - Set system variables"
        echo "└─────────────────────────────────────────"
    else
        echo "┌─ System Configuration (SORCERER+ req'd) ──"
        echo "│ [SYSTEM|CONFIGURE]   - ❌ Requires SORCERER+"
        echo "│ [GET|SYSTEM*setting] - ❌ Requires SORCERER+"
        echo "│ [SET|SYSTEM*value]   - ❌ Requires SORCERER+"
        echo "└─────────────────────────────────────────"
    fi

    # Core system modification (WIZARD only)
    if [[ $current_level -ge 100 ]]; then
        echo "┌─ Core System Modification (WIZARD) ───────"
        echo "│ [SYSTEM|MODIFY]      - Modify core system"
        echo "│ [DEV|ACCESS]         - Access dev environment"
        echo "└─────────────────────────────────────────"
    else
        echo "┌─ Core System Modification (WIZARD req'd) ─"
        echo "│ [SYSTEM|MODIFY]      - ❌ Requires WIZARD"
        echo "│ [DEV|ACCESS]         - ❌ Requires WIZARD"
        echo "└─────────────────────────────────────────"
    fi

    echo ""
    echo "📖 Usage Examples:"
    echo "  ./command-router.sh \"[SYSTEM|STATUS]\""
    echo "  ./command-router.sh \"[ROLE|SET*WIZARD]\""
    echo "  ./command-router.sh \"[ASSIST|ENTER]\""
    echo "  ./command-router.sh \"[SET|USER-NAME*John]\""
    echo ""
    echo "🔑 Role Upgrade: Use [ROLE|SET*HIGHER_ROLE] to access more commands"
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
