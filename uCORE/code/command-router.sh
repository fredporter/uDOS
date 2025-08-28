#!/bin/bash
# uDOS Command Router v1.0.4.3
# Central command processing system for uCODE syntax [COMMAND|ACTION*params]
# Enhanced with Advanced Template System Integration & Self-Healing

set -euo pipefail

# Configuration
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
UDOS_ROOT="$(cd "$SCRIPT_DIR/../.." && pwd)"

# Core integrations
TEMPLATE_ENGINE="$SCRIPT_DIR/template-engine.sh"
VARIABLE_MANAGER="$SCRIPT_DIR/variable-manager.sh"
SELF_HEALING="$SCRIPT_DIR/self-healing/dependency-healer.sh"

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
# � TEMPLATE RENDERING INTEGRATION
# ════════════════════════════════════════════════════════════════

# Render template with current session variables
render_template() {
    local template_name="$1"
    local output_type="${2:-text}"
    local template_dir="$UDOS_ROOT/uMEMORY/system/templates"
    local template_path="$template_dir/$template_name"
    
    if [[ ! -f "$template_path" ]]; then
        log_error "Template not found: $template_name"
        return 1
    fi
    
    log_info "Rendering template: $(basename "$template_name")"
    
    # Create temporary file for processing
    local temp_file=$(mktemp)
    cp "$template_path" "$temp_file"
    
    # Get current system values
    local user_role=$(get_current_role)
    local user_level=$("$VARIABLE_MANAGER" GET "USER-LEVEL" 2>/dev/null || echo "10")
    local session_id=$("$VARIABLE_MANAGER" GET "SESSION-ID" 2>/dev/null || echo "active-session")
    local display_mode=$("$VARIABLE_MANAGER" GET "DISPLAY-MODE" 2>/dev/null || echo "standard")
    local system_status=$("$VARIABLE_MANAGER" GET "SYSTEM-STATUS" 2>/dev/null || echo "healthy")
    local timestamp=$(date '+%Y-%m-%d %H:%M:%S')
    local dev_mode=$("$VARIABLE_MANAGER" GET "DEV-MODE" 2>/dev/null || echo "false")
    
    # Process template conditionals
    process_template_conditionals "$temp_file" "$user_level" "$dev_mode"
    
    # Perform variable substitution with type formatting
    process_template_variables "$temp_file" "$user_role" "$user_level" "$session_id" "$display_mode" "$system_status" "$timestamp" "$dev_mode"
    
    # Output the processed template
    cat "$temp_file"
    rm -f "$temp_file"
    
    return 0
}

# Process template conditionals like {#if} and {#extend}
process_template_conditionals() {
    local temp_file="$1"
    local user_level="$2"
    local dev_mode="$3"
    
    # Process {#if USER-LEVEL:number >= X} blocks
    while grep -q "{#if USER-LEVEL:number >=" "$temp_file"; do
        local line_num=$(grep -n "{#if USER-LEVEL:number >=" "$temp_file" | head -1 | cut -d: -f1)
        local condition=$(sed -n "${line_num}p" "$temp_file")
        local required_level=$(echo "$condition" | sed 's/.*USER-LEVEL:number >= \([0-9]*\).*/\1/')
        
        # Find the end of this conditional block
        local end_line=$(tail -n +$((line_num + 1)) "$temp_file" | grep -n "{/if" | head -1 | cut -d: -f1)
        end_line=$((line_num + end_line))
        
        if [[ "$user_level" -ge "$required_level" ]]; then
            # Keep the content, remove the conditional tags
            sed -i "${line_num}d" "$temp_file"
            sed -i "$((end_line - 1))d" "$temp_file"
        else
            # Remove the entire conditional block
            sed -i "${line_num},${end_line}d" "$temp_file"
        fi
    done
    
    # Process {#if DEV-MODE} blocks
    while grep -q "{#if DEV-MODE" "$temp_file"; do
        local line_num=$(grep -n "{#if DEV-MODE" "$temp_file" | head -1 | cut -d: -f1)
        local end_line=$(tail -n +$((line_num + 1)) "$temp_file" | grep -n "{/if" | head -1 | cut -d: -f1)
        end_line=$((line_num + end_line))
        
        if [[ "$dev_mode" == "true" ]]; then
            # Keep the content, remove the conditional tags
            sed -i "${line_num}d" "$temp_file"
            sed -i "$((end_line - 1))d" "$temp_file"
        else
            # Remove the entire conditional block
            sed -i "${line_num},${end_line}d" "$temp_file"
        fi
    done
    
    # Remove {#extend} lines (for now, just strip them)
    sed -i '/^{#extend/d' "$temp_file"
}

# Process template variables with type formatting
process_template_variables() {
    local temp_file="$1"
    local user_role="$2"
    local user_level="$3"
    local session_id="$4"
    local display_mode="$5"
    local system_status="$6"
    local timestamp="$7"
    local dev_mode="$8"
    
    # Simple variable substitution
    sed -i "s/{USER-ROLE}/$user_role/g" "$temp_file"
    sed -i "s/{USER-LEVEL}/$user_level/g" "$temp_file"
    sed -i "s/{SESSION-ID}/$session_id/g" "$temp_file"
    sed -i "s/{DISPLAY-MODE}/$display_mode/g" "$temp_file"
    sed -i "s/{SYSTEM-STATUS}/$system_status/g" "$temp_file"
    sed -i "s/{TIMESTAMP}/$timestamp/g" "$temp_file"
    sed -i "s/{DEV-MODE}/$dev_mode/g" "$temp_file"
    
    # Formatted variable substitution
    local user_role_title=$(echo "$user_role" | sed 's/.*/\L&/' | sed 's/^./\U&/')
    sed -i "s/{USER-ROLE:title}/$user_role_title/g" "$temp_file"
    sed -i "s/{USER-LEVEL:number}/$user_level/g" "$temp_file"
}

# Simple variable substitution fallback (legacy - not used with new render_template)
substitute_variables() {
    local content="$1"
    
    if [[ -f "$VARIABLE_MANAGER" ]]; then
        local user_role=$("$VARIABLE_MANAGER" GET "USER-ROLE" 2>/dev/null || echo "GHOST")
        local user_level=$("$VARIABLE_MANAGER" GET "USER-LEVEL" 2>/dev/null || echo "10")
        
        content="${content//\{USER-ROLE\}/$user_role}"
        content="${content//\{USER-LEVEL\}/$user_level}"
    fi
    
    echo "$content"
}

# Render help with templates
render_help_template() {
    local help_type="${1:-basic}"
    local current_role="${2:-GHOST}"
    
    # Set template variables for help context
    export UDOS_CURRENT_ROLE="$current_role"
    export UDOS_HELP_TYPE="$help_type"
    
    local template_file="help-${help_type}.md"
    
    # Try to render template, fallback to static help
    if ! render_template "commands/$template_file" "help"; then
        # Fallback to traditional help display
        case "$help_type" in
            "complete") show_complete_help ;;
            "variable") show_variable_help ;;
            *) show_basic_help ;;
        esac
    fi
}

# Render status with templates  
render_status_template() {
    local status_type="${1:-system}"
    local context="${2:-status}"
    
    # Update system variables for status display
    if [[ -f "$VARIABLE_MANAGER" ]]; then
        "$VARIABLE_MANAGER" SET "SYSTEM-STATUS" "$(get_system_status)" >/dev/null 2>&1 || true
        "$VARIABLE_MANAGER" SET "TIMESTAMP" "$(date '+%Y-%m-%d %H:%M:%S')" >/dev/null 2>&1 || true
    fi
    
    local template_file="dashboards/${status_type}-dashboard.md"
    
    if ! render_template "$template_file" "$context"; then
        # Fallback to traditional status display
        show_traditional_status
    fi
}

# Get current system status
get_system_status() {
    local status="healthy"
    
    # Check dependencies
    if [[ -f "$SELF_HEALING" ]]; then
        if ! "$SELF_HEALING" status >/dev/null 2>&1; then
            status="needs-healing"
        fi
    fi
    
    # Check core services
    if [[ ! -f "$VARIABLE_MANAGER" ]] || [[ ! -f "$TEMPLATE_ENGINE" ]]; then
        status="degraded"
    fi
    
    echo "$status"
}

# ════════════════════════════════════════════════════════════════
# �🎯 COMMAND ROUTING
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
        "GET"|"SET"|"LIST")
            handle_variable_command "$command" "$action" "$params"
            ;;
        "STORY")
            handle_story_command "$action" "$params"
            ;;
        "SYSTEM")
            handle_system_command "$action" "$params"
            ;;
        "ROLE")
            handle_role_command "$action" "$params"
            ;;
        "TEMPLATE")
            handle_template_command "$action" "$params"
            ;;
        "STATUS")
            handle_status_command "$action" "$params"
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

# Handle variable commands (GET/SET) - Enhanced integration with optimized variable system
handle_variable_command() {
    local command="$1"
    local action="$2"
    local params="$3"

    if [[ -f "$SCRIPT_DIR/variable-manager.sh" ]]; then
        case "$command" in
            "GET")
                log_info "Getting variable: $action"
                local value
                if value=$("$SCRIPT_DIR/variable-manager.sh" GET "$action" 2>/dev/null); then
                    echo "Variable: $action = $value"

                    # Show additional variable information for enhanced feedback
                    if [[ -f "$SCRIPT_DIR/variable-manager.sh" ]]; then
                        local var_def
                        if var_def=$("$SCRIPT_DIR/variable-manager.sh" DEF "$action" 2>/dev/null); then
                            local var_type=$(echo "$var_def" | jq -r '.type // "unknown"' 2>/dev/null)
                            local var_scope=$(echo "$var_def" | jq -r '.scope // "unknown"' 2>/dev/null)
                            echo "Type: $var_type | Scope: $var_scope"
                        fi
                    fi
                else
                    log_error "Variable '$action' not found or no value set"
                    # Suggest available variables
                    echo "Use [GET|LIST] to see available variables"
                fi
                ;;
            "SET")
                if [[ -z "$params" ]]; then
                    log_error "SET command requires a value parameter"
                    echo "Usage: [SET|variable*value]"
                    return 1
                fi
                log_info "Setting variable: $action = $params"
                if "$SCRIPT_DIR/variable-manager.sh" SET "$action" "$params" 2>/dev/null; then
                    log_success "Variable '$action' set successfully"
                    # Show updated value for confirmation
                    local new_value
                    if new_value=$("$SCRIPT_DIR/variable-manager.sh" GET "$action" 2>/dev/null); then
                        echo "New value: $action = $new_value"
                    fi
                else
                    log_error "Failed to set variable '$action'"
                    return 1
                fi
                ;;
            "LIST")
                log_info "Listing all variables"
                "$SCRIPT_DIR/variable-manager.sh" LIST 2>/dev/null || log_error "Failed to list variables"
                ;;
            *)
                log_error "Unknown variable command: $command"
                echo "Available variable commands: GET, SET, LIST"
                return 1
                ;;
        esac
    else
        log_warning "Variable manager not found - install variable system"
        echo "Run: ./uCORE/code/variable-system-optimizer.sh"
        return 1
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

# Handle template commands for dynamic content generation
handle_template_command() {
    local action="$1"
    local params="$2"
    local current_role=$(get_current_role)
    local session_id="$$"

    case "$action" in
        "LIST"|"")
            echo "📋 Available Templates:"
            echo ""
            echo "🏠 Base Templates:"
            find "$UDOS_ROOT/uMEMORY/system/templates/base" -name "*.md" 2>/dev/null | sed 's|.*/||; s|\.md$||' | sed 's/^/  • /' || echo "  (none found)"
            
            echo ""
            echo "📖 Command Help Templates:"
            find "$UDOS_ROOT/uMEMORY/system/templates/commands" -name "*.md" 2>/dev/null | sed 's|.*/||; s|\.md$||' | sed 's/^/  • /' || echo "  (none found)"
            
            echo ""
            echo "📊 Dashboard Templates:"
            find "$UDOS_ROOT/uMEMORY/system/templates/dashboards" -name "*.md" 2>/dev/null | sed 's|.*/||; s|\.md$||' | sed 's/^/  • /' || echo "  (none found)"
            
            echo ""
            echo "📝 Form Templates:"
            find "$UDOS_ROOT/uMEMORY/system/templates/forms" -name "*.md" 2>/dev/null | sed 's|.*/||; s|\.md$||' | sed 's/^/  • /' || echo "  (none found)"
            ;;
        "RENDER")
            if [[ -z "$params" ]]; then
                log_error "TEMPLATE RENDER requires template name"
                echo "Usage: [TEMPLATE|RENDER*template-name]"
                echo "Use [TEMPLATE|LIST] to see available templates"
                return 1
            fi
            
            log_info "Rendering template: $params"
            
            # Try different template locations
            local template_found=false
            for template_dir in "commands" "dashboards" "forms" "base"; do
                local template_path="$UDOS_ROOT/uMEMORY/system/templates/$template_dir/$params.md"
                if [[ -f "$template_path" ]]; then
                    render_template "$template_dir/$params.md" "manual" "$session_id"
                    template_found=true
                    break
                fi
            done
            
            if [[ "$template_found" == "false" ]]; then
                log_error "Template not found: $params"
                echo "Use [TEMPLATE|LIST] to see available templates"
                return 1
            fi
            ;;
        "VARIABLES"|"VARS")
            echo "🔧 Template Variables Available:"
            echo ""
            if [[ -f "$VARIABLE_MANAGER" ]]; then
                "$VARIABLE_MANAGER" LIST "$session_id" | grep -E "^\s*[A-Z][A-Z0-9_-]*:" | sed 's/^/  {/' | sed 's/:.*$/}/'
            else
                echo "  (Variable manager not available)"
            fi
            ;;
        "STATUS")
            echo "🎨 Template System Status:"
            echo ""
            if [[ -f "$TEMPLATE_ENGINE" ]]; then
                echo "  ✅ Template Engine: Available"
            else
                echo "  ❌ Template Engine: Not Found"
            fi
            
            if [[ -f "$VARIABLE_MANAGER" ]]; then
                echo "  ✅ Variable Manager: Available"
            else
                echo "  ❌ Variable Manager: Not Found"
            fi
            
            local template_count=$(find "$UDOS_ROOT/uMEMORY/system/templates" -name "*.md" 2>/dev/null | wc -l)
            echo "  📋 Available Templates: $template_count"
            ;;
        *)
            log_error "Unknown TEMPLATE action: $action"
            echo "Available actions:"
            echo "  LIST - Show all available templates"
            echo "  RENDER*name - Render specific template"
            echo "  VARIABLES - Show available template variables"
            echo "  STATUS - Show template system status"
            return 1
            ;;
    esac
}

# Handle status commands with template integration
handle_status_command() {
    local action="$1"
    local params="$2"
    local current_role=$(get_current_role)

    case "$action" in
        "DASHBOARD"|"")
            # Render simple dashboard template
            if ! render_template "dashboards/simple-dashboard.md" "dashboard"; then
                # Fallback to basic status
                show_system_status
            fi
            ;;
        "SYSTEM")
            # System-specific status
            if ! render_template "dashboards/simple-dashboard.md" "status"; then
                show_system_status
            fi
            ;;
        "PROJECT")
            # Project-specific status
            echo "📁 Project Status:"
            if [[ -f "$VARIABLE_MANAGER" ]]; then
                echo "  Project Name: $("$VARIABLE_MANAGER" GET "PROJECT-NAME" 2>/dev/null || echo "Not Set")"
                echo "  Project Type: $("$VARIABLE_MANAGER" GET "PROJECT-TYPE" 2>/dev/null || echo "Not Set")"
                echo "  Workspace: $("$VARIABLE_MANAGER" GET "WORKSPACE-PATH" 2>/dev/null || echo "Not Set")"
            else
                echo "  (Variable manager not available)"
            fi
            ;;
        *)
            log_error "Unknown STATUS action: $action"
            echo "Available actions:"
            echo "  DASHBOARD - Show main system dashboard"
            echo "  SYSTEM - Show detailed system status"
            echo "  PROJECT - Show project-specific status"
            return 1
            ;;
    esac
}

# Handle story commands for interactive variable collection
handle_story_command() {
    local action="$1"
    local params="$2"

    if [[ -f "$SCRIPT_DIR/variable-manager.sh" ]]; then
        case "$action" in
            "CREATE")
                if [[ -z "$params" ]]; then
                    log_error "STORY CREATE requires parameters: name*title*variables"
                    echo "Usage: [STORY|CREATE*story-name*Story Title*var1,var2,var3]"
                    return 1
                fi

                # Parse parameters: name*title*variables
                local story_name="${params%%\**}"
                local remaining="${params#*\*}"
                local story_title="${remaining%%\**}"
                local variables="${remaining#*\*}"

                log_info "Creating story: $story_name"
                if "$SCRIPT_DIR/variable-manager.sh" STORY CREATE "$story_name" "$story_title" "$variables" 2>/dev/null; then
                    log_success "Story '$story_name' created successfully"
                else
                    log_error "Failed to create story '$story_name'"
                    return 1
                fi
                ;;
            "EXECUTE"|"RUN")
                if [[ -z "$params" ]]; then
                    log_error "STORY EXECUTE requires story name parameter"
                    echo "Usage: [STORY|EXECUTE*story-name] or [STORY|RUN*story-name]"
                    return 1
                fi

                local story_name="$params"
                local story_file="$UDOS_ROOT/uMEMORY/system/stories/${story_name}.json"

                log_info "Executing story: $story_name"
                if "$SCRIPT_DIR/variable-manager.sh" STORY EXECUTE "$story_file" 2>/dev/null; then
                    log_success "Story '$story_name' executed successfully"
                else
                    log_error "Failed to execute story '$story_name'"
                    echo "Available stories in uMEMORY/system/stories/"
                    return 1
                fi
                ;;
            "LIST")
                log_info "Listing available stories"
                local stories_dir="$UDOS_ROOT/uMEMORY/system/stories"
                if [[ -d "$stories_dir" ]]; then
                    echo "📖 Available Stories:"
                    find "$stories_dir" -name "*.json" -type f | while read -r story_file; do
                        local story_name=$(basename "$story_file" .json)
                        local story_title=""
                        if command -v jq >/dev/null 2>&1; then
                            story_title=$(jq -r '.metadata.title // "No title"' "$story_file" 2>/dev/null)
                        fi
                        echo "  $story_name${story_title:+ - $story_title}"
                    done
                else
                    log_warning "No stories directory found"
                fi
                ;;
            *)
                log_error "Unknown STORY action: $action"
                echo "Available actions: CREATE, EXECUTE, RUN, LIST"
                return 1
                ;;
        esac
    else
        log_warning "Variable manager not found - story system unavailable"
        return 1
    fi
}

# Handle help commands
handle_help_command() {
    local action="$1"
    local params="$2"
    local current_role=$(get_current_role)

    # Use template rendering for enhanced help
    if [[ -n "$action" ]]; then
        case "$action" in
            "COMPLETE"|"FULL")
                render_help_template "complete" "$current_role"
                ;;
            "VARIABLE"|"VAR")
                render_help_template "variable" "$current_role"
                ;;
            "BASIC"|"SIMPLE")
                render_help_template "basic" "$current_role"
                ;;
            *)
                # Command-specific help
                if ! render_template "commands/help-$action.md" "help"; then
                    show_command_help "$action"
                fi
                ;;
        esac
    else
        # General help with role-aware template
        if ! render_help_template "help" "$current_role"; then
            show_general_help
        fi
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
        echo "│ [LIST]               - List all variables"
        echo "│ [STORY|LIST]         - List available stories"
        echo "│ [STORY|RUN*name]     - Execute story for data collection"
        echo "└─────────────────────────────────────────"
    else
        echo "┌─ Variable Operations (TOMB+ required) ────"
        echo "│ [GET|variable]       - ❌ Requires TOMB+"
        echo "│ [SET|variable*value] - ❌ Requires TOMB+"
        echo "│ [LIST]               - ❌ Requires TOMB+"
        echo "│ [STORY|LIST]         - ❌ Requires TOMB+"
        echo "│ [STORY|RUN*name]     - ❌ Requires TOMB+"
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
        "GET"|"SET"|"LIST"|"VARIABLE"|"VAR")
            echo "🔧 Variable System Commands"
            echo "  [GET|variable]       - Get variable value with details"
            echo "  [SET|variable*value] - Set variable value with confirmation"
            echo "  [LIST]               - List all available variables by scope"
            echo ""
            echo "🎯 Enhanced Variable Features:"
            echo "  • Centralized storage in uMEMORY/system"
            echo "  • Cross-component sharing (commands, templates, uSCRIPTs)"
            echo "  • Role-specific variable access"
            echo "  • Environment export with UDOS_ prefix"
            echo ""
            echo "📋 Common Variables:"
            echo "  USER-ROLE, USER-LEVEL, DISPLAY-MODE, PROJECT-NAME"
            echo "  TILE-CODE, TIMEZONE, DEV-MODE, DEBUG-LEVEL"
            ;;
        "STORY")
            echo "📖 Interactive Story System Commands"
            echo "  [STORY|LIST]                     - List available stories"
            echo "  [STORY|RUN*story-name]           - Execute story for variable collection"
            echo "  [STORY|CREATE*name*title*vars]   - Create new story template"
            echo ""
            echo "🎯 Story Features:"
            echo "  • Interactive variable collection"
            echo "  • Role-based story execution"
            echo "  • Multi-variable data gathering"
            echo "  • Guided user input with validation"
            echo ""
            echo "📋 Available Role Stories:"
            echo "  ghost-startup, tomb-startup, crypt-startup, drone-startup"
            echo "  knight-startup, imp-startup, sorcerer-startup, wizard-startup"
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
