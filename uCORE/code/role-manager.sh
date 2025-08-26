#!/bin/bash
# uDOS Role Manager v1.0.4.1
# Comprehensive role management system for uCODE access control
# Phase 2 Implementation - Enhanced Role Validation and Management

set -euo pipefail

# Configuration
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
UDOS_ROOT="$(cd "$SCRIPT_DIR/../.." && pwd)"

# Role configuration
ROLE_CONFIG_DIR="$UDOS_ROOT/uMEMORY/role"
SANDBOX_ROLE_FILE="$UDOS_ROOT/sandbox/current-role.conf"
MEMORY_ROLE_FILE="$UDOS_ROOT/uMEMORY/role/current.txt"

# Source logging functions
source "$SCRIPT_DIR/logging.sh" 2>/dev/null || {
    log_info() { echo -e "\033[0;36m[INFO]\033[0m $1"; }
    log_success() { echo -e "\033[0;32m[SUCCESS]\033[0m $1"; }
    log_warning() { echo -e "\033[0;33m[WARNING]\033[0m $1"; }
    log_error() { echo -e "\033[0;31m[ERROR]\033[0m $1"; }
}

# ════════════════════════════════════════════════════════════════
# 🛠️ CORE ROLE FUNCTIONS
# ════════════════════════════════════════════════════════════════

# Get current role from memory system
get_current_role() {
    # Check sandbox first (session-based)
    if [[ -f "$SANDBOX_ROLE_FILE" ]]; then
        local sandbox_role=$(grep "^ROLE=" "$SANDBOX_ROLE_FILE" 2>/dev/null | cut -d'=' -f2 | tr -d '"' | tr '[:lower:]' '[:upper:]')
        if [[ -n "$sandbox_role" ]] && is_valid_role "$sandbox_role"; then
            echo "$sandbox_role"
            return 0
        fi
    fi

    # Check memory system (persistent)
    if [[ -f "$MEMORY_ROLE_FILE" ]]; then
        local memory_role=$(cat "$MEMORY_ROLE_FILE" 2>/dev/null | tr -d ' \n\r' | tr '[:lower:]' '[:upper:]')
        if [[ -n "$memory_role" ]] && is_valid_role "$memory_role"; then
            echo "$memory_role"
            return 0
        fi
    fi

    # Default to GHOST if no valid role found
    echo "GHOST"
}

# Get role permission level
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

# Get role description
get_role_description() {
    local role="$1"
    case "$role" in
        "GHOST") echo "Demo installation, read-only access" ;;
        "TOMB") echo "Basic storage and simple operations" ;;
        "CRYPT") echo "Secure storage and standard operations" ;;
        "DRONE") echo "Automation tasks and maintenance" ;;
        "KNIGHT") echo "Security functions and standard operations" ;;
        "IMP") echo "Development tools and automation" ;;
        "SORCERER") echo "Advanced administration and debugging" ;;
        "WIZARD") echo "Full development access and core system control" ;;
        *) echo "Unknown role" ;;
    esac
}

# Check if role is valid
is_valid_role() {
    local role="$1"
    local level=$(get_role_level "$role")
    [[ $level -gt 0 ]]
}

# Validate role transition permissions
can_set_role() {
    local current_role="$1"
    local target_role="$2"
    local current_level=$(get_role_level "$current_role")
    local target_level=$(get_role_level "$target_role")

    # WIZARD can set any role
    if [[ "$current_role" == "WIZARD" ]]; then
        return 0
    fi

    # SORCERER can set roles up to IMP level
    if [[ "$current_role" == "SORCERER" && $target_level -le 60 ]]; then
        return 0
    fi

    # KNIGHT can set roles up to DRONE level
    if [[ "$current_role" == "KNIGHT" && $target_level -le 40 ]]; then
        return 0
    fi

    # Users can downgrade their own role
    if [[ $target_level -lt $current_level ]]; then
        return 0
    fi

    return 1
}

# ════════════════════════════════════════════════════════════════
# 🎯 ROLE MANAGEMENT OPERATIONS
# ════════════════════════════════════════════════════════════════

# Set role with validation
set_role() {
    local target_role="$1"
    local current_role=$(get_current_role)
    local force_mode="${2:-false}"

    # Validate target role
    if ! is_valid_role "$target_role"; then
        log_error "Invalid role: $target_role"
        show_available_roles
        return 1
    fi

    # Check transition permissions
    if [[ "$force_mode" != "true" ]] && ! can_set_role "$current_role" "$target_role"; then
        log_error "Permission denied: Cannot transition from $current_role to $target_role"
        echo "Current role: $current_role (Level $(get_role_level "$current_role"))"
        echo "Target role: $target_role (Level $(get_role_level "$target_role"))"
        echo "Use --force to bypass checks (if you have the authority)"
        return 1
    fi

    # Create backup of current role
    backup_current_role

    # Update sandbox role file
    mkdir -p "$(dirname "$SANDBOX_ROLE_FILE")"
    cat > "$SANDBOX_ROLE_FILE" << EOF
ROLE="$target_role"
PREVIOUS_ROLE="$current_role"
TIMESTAMP="$(date '+%Y-%m-%d %H:%M:%S %Z')"
TRANSITION_REASON="Manual role change"
EOF

    # Update memory role file
    mkdir -p "$(dirname "$MEMORY_ROLE_FILE")"
    echo "$target_role" > "$MEMORY_ROLE_FILE"

    # Log role change
    log_role_change "$current_role" "$target_role"

    log_success "Role changed: $current_role → $target_role"
    echo "New role level: $(get_role_level "$target_role")"
    echo "Description: $(get_role_description "$target_role")"

    return 0
}

# Show current role status
show_role_status() {
    local current_role=$(get_current_role)
    local current_level=$(get_role_level "$current_role")

    echo "═══════════════════════════════════════"
    echo "👤 Current Role Status"
    echo "═══════════════════════════════════════"
    echo "Role: $current_role"
    echo "Level: $current_level"
    echo "Description: $(get_role_description "$current_role")"
    echo "═══════════════════════════════════════"

    # Show role-specific capabilities
    show_role_capabilities "$current_role"
}

# Show available roles
show_available_roles() {
    echo "📋 Available Roles (Level: Description)"
    echo "───────────────────────────────────────"
    for role in GHOST TOMB CRYPT DRONE KNIGHT IMP SORCERER WIZARD; do
        local level=$(get_role_level "$role")
        local desc=$(get_role_description "$role")
        echo "  $role ($level): $desc"
    done
}

# Show role capabilities
show_role_capabilities() {
    local role="$1"
    local level=$(get_role_level "$role")

    echo ""
    echo "🔑 Role Capabilities for $role (Level $level):"
    echo "───────────────────────────────────────"

    # Basic commands (all roles)
    echo "✅ Basic Commands: HELP, SYSTEM|STATUS"

    # Variable commands (TOMB+)
    if [[ $level -ge 20 ]]; then
        echo "✅ Variable Operations: GET, SET"
    else
        echo "❌ Variable Operations: GET, SET (requires TOMB+)"
    fi

    # ASSIST basic commands (DRONE+)
    if [[ $level -ge 40 ]]; then
        echo "✅ ASSIST Basic: ENTER, EXIT, NEXT"
    else
        echo "❌ ASSIST Basic: ENTER, EXIT, NEXT (requires DRONE+)"
    fi

    # Role management (KNIGHT+)
    if [[ $level -ge 50 ]]; then
        echo "✅ Role Management: ROLE|GET, ROLE|SET"
    else
        echo "❌ Role Management: ROLE|GET, ROLE|SET (requires KNIGHT+)"
    fi

    # ASSIST advanced commands (IMP+)
    if [[ $level -ge 60 ]]; then
        echo "✅ ASSIST Advanced: FINALIZE, ROADMAP"
    else
        echo "❌ ASSIST Advanced: FINALIZE, ROADMAP (requires IMP+)"
    fi

    # System configuration (SORCERER+)
    if [[ $level -ge 80 ]]; then
        echo "✅ System Configuration: SYSTEM|CONFIGURE"
    else
        echo "❌ System Configuration: SYSTEM|CONFIGURE (requires SORCERER+)"
    fi

    # Core system modification (WIZARD only)
    if [[ $level -ge 100 ]]; then
        echo "✅ Core System Modification: SYSTEM|MODIFY, DEV access"
    else
        echo "❌ Core System Modification: SYSTEM|MODIFY, DEV access (requires WIZARD)"
    fi
}

# ════════════════════════════════════════════════════════════════
# 🗃️ BACKUP AND LOGGING
# ════════════════════════════════════════════════════════════════

# Backup current role configuration
backup_current_role() {
    local timestamp=$(date '+%Y%m%d-%H%M%S%Z')
    local backup_dir="$UDOS_ROOT/sandbox/backup/roles"

    mkdir -p "$backup_dir"

    if [[ -f "$SANDBOX_ROLE_FILE" ]]; then
        cp "$SANDBOX_ROLE_FILE" "$backup_dir/role-config-$timestamp.conf"
    fi

    if [[ -f "$MEMORY_ROLE_FILE" ]]; then
        cp "$MEMORY_ROLE_FILE" "$backup_dir/role-memory-$timestamp.txt"
    fi
}

# Log role change
log_role_change() {
    local from_role="$1"
    local to_role="$2"
    local log_file="$UDOS_ROOT/sandbox/logs/role-changes.log"

    mkdir -p "$(dirname "$log_file")"

    cat >> "$log_file" << EOF
$(date '+%Y-%m-%d %H:%M:%S %Z') | ROLE_CHANGE | $from_role → $to_role | Level $(get_role_level "$from_role") → $(get_role_level "$to_role")
EOF
}

# ════════════════════════════════════════════════════════════════
# 🚀 MAIN EXECUTION
# ════════════════════════════════════════════════════════════════

main() {
    local action="${1:-status}"
    local target_role="${2:-}"
    local force_flag="${3:-}"

    case "$action" in
        "get"|"status")
            show_role_status
            ;;
        "set")
            if [[ -z "$target_role" ]]; then
                log_error "Target role required for SET operation"
                echo "Usage: $0 set ROLE_NAME [--force]"
                show_available_roles
                exit 1
            fi

            local force_mode="false"
            if [[ "$force_flag" == "--force" ]]; then
                force_mode="true"
            fi

            set_role "$target_role" "$force_mode"
            ;;
        "list")
            show_available_roles
            ;;
        "capabilities")
            local role="${target_role:-$(get_current_role)}"
            show_role_capabilities "$role"
            ;;
        "validate")
            local role="${target_role:-$(get_current_role)}"
            if is_valid_role "$role"; then
                log_success "Role '$role' is valid (Level $(get_role_level "$role"))"
            else
                log_error "Role '$role' is invalid"
                exit 1
            fi
            ;;
        "help")
            cat << EOF
🎯 uDOS Role Manager v1.0.4.1

Usage: $0 <action> [options]

Actions:
  get|status              Show current role status
  set ROLE [--force]      Change to specified role
  list                    List all available roles
  capabilities [ROLE]     Show capabilities for role
  validate [ROLE]         Validate role name
  help                    Show this help

Role Hierarchy (Level: Name):
  10:  GHOST    - Demo installation, read-only access
  20:  TOMB     - Basic storage and simple operations
  30:  CRYPT    - Secure storage and standard operations
  40:  DRONE    - Automation tasks and maintenance
  50:  KNIGHT   - Security functions and standard operations
  60:  IMP      - Development tools and automation
  80:  SORCERER - Advanced administration and debugging
  100: WIZARD   - Full development access and core system control

Examples:
  $0 status                    # Show current role
  $0 set WIZARD               # Change to WIZARD role
  $0 set DRONE --force        # Force change to DRONE role
  $0 capabilities IMP         # Show IMP role capabilities
  $0 list                     # List all roles

EOF
            ;;
        *)
            log_error "Unknown action: $action"
            echo "Use '$0 help' for usage information"
            exit 1
            ;;
    esac
}

# Execute main function if script is run directly
if [[ "${BASH_SOURCE[0]}" == "${0}" ]]; then
    main "$@"
fi
