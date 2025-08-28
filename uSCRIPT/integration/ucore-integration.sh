#!/bin/bash
# uSCRIPT-uCORE Integration v1.3.3
# Provides compatibility layer for uCORE logging, error handling, backup protocols,
# and role-based permissions integration for uSCRIPT

set -euo pipefail

# Configuration
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
UDOS_ROOT="$(cd "$SCRIPT_DIR/../../.." && pwd)"
UCORE_PATH="$UDOS_ROOT/uCORE"
UMEMORY_PATH="$UDOS_ROOT/uMEMORY"
SANDBOX_PATH="$UDOS_ROOT/sandbox"
USCRIPT_PATH="$UDOS_ROOT/uSCRIPT"

# Source uCORE protocols
if [[ -f "$UCORE_PATH/core/logging.sh" ]]; then
    source "$UCORE_PATH/core/logging.sh"
else
    # Fallback logging functions
    log_info() { echo "[INFO] $1"; }
    log_success() { echo "[SUCCESS] $1"; }
    log_warning() { echo "[WARNING] $1"; }
    log_error() { echo "[ERROR] $1"; }
    log_debug() { echo "[DEBUG] $1"; }
fi

# Source uCORE error handler if available
if [[ -f "$UCORE_PATH/system/error-handler.sh" ]]; then
    export UDOS_USCRIPT_INTEGRATION="true"
    source "$UCORE_PATH/system/error-handler.sh"
fi

# Load role permissions
load_role_permissions() {
    local role_file="$UMEMORY_PATH/system/uDATA-user-roles.json"

    if [[ -f "$role_file" ]]; then
        log_debug "Loading role permissions from $role_file"
        export USCRIPT_ROLE_FILE="$role_file"
    else
        log_warning "Role permissions file not found: $role_file"
        return 1
    fi
}

# Get current role
get_current_role() {
    local role_conf="$SANDBOX_PATH/current-role.conf"

    if [[ -f "$role_conf" ]]; then
        local role=$(grep "^CURRENT_ROLE=" "$role_conf" | cut -d'=' -f2)
        echo "${role:-wizard}"
    else
        echo "wizard"  # Default role
    fi
}

# Check role permissions for uSCRIPT operations
check_uscript_permission() {
    local action="$1"
    local current_role=$(get_current_role)

    # Load role permissions using Python helper
    local permission_check=$(python3 -c "
import json
import sys

try:
    with open('$UMEMORY_PATH/system/uDATA-user-roles.json', 'r') as f:
        content = f.read().strip()

    # Parse uDATA format (one JSON object per line)
    role_permissions = {}
    for line in content.split('\n'):
        if line.strip():
            role_data = json.loads(line)
            role_permissions[role_data['role']] = role_data

    # Get current role permissions
    role_data = role_permissions.get('$current_role', {})
    permissions = role_data.get('permissions', {})

    # Check specific action
    if '$action' in permissions:
        result = permissions['$action']
        if isinstance(result, bool):
            print('true' if result else 'false')
        elif result in ['full', 'read_write', True]:
            print('true')
        elif result in ['limited', 'read_only']:
            print('true' if '$action' in ['read', 'list', 'info'] else 'false')
        else:
            print('false')
    elif '$action'.startswith('script_'):
        script_perm = permissions.get('script_editing', False)
        if script_perm == 'user_only' and '$action' in ['script_read', 'script_list']:
            print('true')
        elif script_perm in [True, 'full']:
            print('true')
        else:
            print('false')
    else:
        # Default permissions for read operations
        print('true' if '$action' in ['read', 'list', 'info', 'status'] else 'false')

except Exception as e:
    print('false')
")

    [[ "$permission_check" == "true" ]]
}

# Enhanced script execution with role checking
execute_script_with_role_check() {
    local script_name="$1"
    shift
    local script_args=("$@")
    local current_role=$(get_current_role)

    log_info "Executing script '$script_name' as role '$current_role'"

    # Check execution permissions
    if ! check_uscript_permission "script_execute"; then
        log_error "Permission denied: Role '$current_role' cannot execute scripts"
        return 1
    fi

    # Check if script exists in catalog
    local catalog_file="$USCRIPT_PATH/registry/catalog.json"
    if [[ ! -f "$catalog_file" ]]; then
        log_error "Script catalog not found: $catalog_file"
        return 1
    fi

    # Get script information
    local script_info=$(jq --arg name "$script_name" '.scripts[$name]' "$catalog_file" 2>/dev/null)
    if [[ "$script_info" == "null" ]]; then
        log_error "Script '$script_name' not found in catalog"
        return 1
    fi

    # Check script security level against role permissions
    local security_level=$(echo "$script_info" | jq -r '.security_level // "safe"')
    local script_type=$(echo "$script_info" | jq -r '.type // "unknown"')

    if ! check_script_security_permission "$security_level" "$current_role"; then
        log_error "Permission denied: Role '$current_role' cannot execute '$security_level' level scripts"
        return 1
    fi

    # Log execution attempt
    log_info "Script security check passed: $script_name ($security_level level)"

    # Set environment variables for role context
    export UDOS_CURRENT_ROLE="$current_role"
    export UDOS_SCRIPT_CONTEXT="true"
    export UDOS_INTEGRATION_MODE="ucore"

    # Create execution log entry
    local exec_id="EXEC_$(date +%s)_${script_name}"
    local exec_log="$USCRIPT_PATH/runtime/logs/executions/${exec_id}.log"
    mkdir -p "$(dirname "$exec_log")"

    {
        echo "Execution ID: $exec_id"
        echo "Script: $script_name"
        echo "Type: $script_type"
        echo "Security Level: $security_level"
        echo "Role: $current_role"
        echo "Start Time: $(date '+%Y-%m-%d %H:%M:%S')"
        echo "Command: ${script_args[*]}"
        echo "Integration: uCORE v1.3.3"
        echo "====================================="
    } > "$exec_log"

    # Execute the actual script
    local start_time=$(date +%s)
    local exit_code=0

    # Call original uSCRIPT execution function
    if "$USCRIPT_PATH/uscript.sh" run "$script_name" "${script_args[@]}" 2>&1 | tee -a "$exec_log"; then
        log_success "Script '$script_name' executed successfully"
    else
        exit_code=$?
        log_error "Script '$script_name' failed with exit code $exit_code"

        # Log error to uCORE error system
        if command -v log_error >/dev/null 2>&1; then
            log_error "USCRIPT_EXECUTION_FAILED" "Script $script_name failed (exit: $exit_code)"
        fi
    fi

    # Complete execution log
    local end_time=$(date +%s)
    local duration=$((end_time - start_time))

    {
        echo "====================================="
        echo "End Time: $(date '+%Y-%m-%d %H:%M:%S')"
        echo "Duration: ${duration}s"
        echo "Exit Code: $exit_code"
    } >> "$exec_log"

    return $exit_code
}

# Check script security level permissions
check_script_security_permission() {
    local security_level="$1"
    local role="$2"

    case "$security_level" in
        "safe")
            # All roles can execute safe scripts
            return 0
            ;;
        "elevated")
            # Requires imp level or higher
            case "$role" in
                "wizard"|"sorcerer"|"imp"|"knight") return 0 ;;
                *) return 1 ;;
            esac
            ;;
        "admin")
            # Requires wizard or sorcerer level
            case "$role" in
                "wizard"|"sorcerer") return 0 ;;
                *) return 1 ;;
            esac
            ;;
        *)
            log_warning "Unknown security level: $security_level"
            return 1
            ;;
    esac
}

# Create role-specific backup
create_role_backup() {
    local backup_type="${1:-manual}"
    local description="${2:-uSCRIPT role backup}"
    local current_role=$(get_current_role)

    if ! check_uscript_permission "backup_create"; then
        log_error "Permission denied: Role '$current_role' cannot create backups"
        return 1
    fi

    local backup_dir="$UDOS_ROOT/backup/uscript"
    local timestamp=$(date +%Y%m%d-%H%M%S)
    local backup_file="$backup_dir/uscript-${backup_type}-${timestamp}-${current_role}.tar.gz"

    mkdir -p "$backup_dir"

    log_info "Creating uSCRIPT backup: $backup_file"

    # Include role-specific files
    local backup_sources=(
        "$USCRIPT_PATH/config"
        "$USCRIPT_PATH/registry"
        "$USCRIPT_PATH/runtime/logs"
    )

    # Add user scripts if permission allows
    if check_uscript_permission "script_read"; then
        if [[ -d "$USCRIPT_PATH/library/user" ]]; then
            backup_sources+=("$USCRIPT_PATH/library/user")
        fi
    fi

    # Create backup with compression
    if tar -czf "$backup_file" -C "$UDOS_ROOT" "${backup_sources[@]/#$UDOS_ROOT\//}" 2>/dev/null; then
        log_success "Backup created: $backup_file"

        # Log backup creation
        local backup_log="$backup_dir/backup-log.json"
        echo "{\"timestamp\":\"$(date -Iseconds)\",\"type\":\"$backup_type\",\"file\":\"$(basename "$backup_file")\",\"role\":\"$current_role\",\"description\":\"$description\"}" >> "$backup_log"

        echo "$backup_file"
        return 0
    else
        log_error "Failed to create backup: $backup_file"
        return 1
    fi
}

# Use sandbox with role permissions
use_sandbox() {
    local operation="${1:-read}"
    local sandbox_path="${2:-user}"
    local current_role=$(get_current_role)

    # Check sandbox permissions
    local sandbox_access=$(python3 -c "
import json
try:
    with open('$UMEMORY_PATH/system/uDATA-user-roles.json', 'r') as f:
        content = f.read().strip()

    for line in content.split('\n'):
        if line.strip():
            role_data = json.loads(line)
            if role_data['role'] == '$current_role':
                folder_access = role_data.get('folder_access', {})
                print(folder_access.get('sandbox', 'none'))
                break
    else:
        print('none')
except:
    print('none')
")

    case "$sandbox_access" in
        "none")
            log_error "Sandbox access denied for role '$current_role'"
            return 1
            ;;
        "demo_only")
            local full_path="$SANDBOX_PATH/demos/$sandbox_path"
            ;;
        "read_write_limited")
            local full_path="$SANDBOX_PATH/user/$sandbox_path"
            ;;
        "full")
            local full_path="$SANDBOX_PATH/$sandbox_path"
            ;;
        *)
            log_warning "Unknown sandbox access level: $sandbox_access"
            local full_path="$SANDBOX_PATH/user/$sandbox_path"
            ;;
    esac

    # Create directory if needed for write operations
    if [[ "$operation" == "write" && ! -d "$full_path" ]]; then
        mkdir -p "$full_path"
    fi

    if [[ -d "$full_path" || "$operation" == "write" ]]; then
        log_debug "Sandbox access granted: $full_path"
        echo "$full_path"
        return 0
    else
        log_error "Sandbox path not accessible: $full_path"
        return 1
    fi
}

# Access uMEMORY resources with role permissions
access_umemory_resource() {
    local resource_path="$1"
    local operation="${2:-read}"
    local current_role=$(get_current_role)

    # Check uMEMORY access permissions
    if ! check_uscript_permission "umemory_$operation"; then
        log_error "Permission denied: Role '$current_role' cannot $operation uMEMORY resources"
        return 1
    fi

    local full_path="$UMEMORY_PATH/$resource_path"

    if [[ ! -e "$full_path" ]]; then
        log_error "uMEMORY resource not found: $resource_path"
        return 1
    fi

    case "$operation" in
        "read")
            if [[ -f "$full_path" ]]; then
                cat "$full_path"
            elif [[ -d "$full_path" ]]; then
                ls -la "$full_path"
            fi
            ;;
        "write")
            if [[ -f "$full_path" && -w "$full_path" ]]; then
                echo "$full_path"  # Return path for writing
            else
                log_error "Cannot write to uMEMORY resource: $resource_path"
                return 1
            fi
            ;;
        "list")
            if [[ -d "$full_path" ]]; then
                find "$full_path" -type f -name "*.json" -o -name "*.udata" | head -20
            fi
            ;;
        *)
            log_error "Unknown operation: $operation"
            return 1
            ;;
    esac
}

# Show integration status
show_integration_status() {
    local current_role=$(get_current_role)

    echo "uSCRIPT-uCORE Integration Status v1.3.3"
    echo "======================================="
    echo
    echo "Current Role: $current_role"
    echo "uCORE Path: $UCORE_PATH"
    echo "uMEMORY Path: $UMEMORY_PATH"
    echo "Sandbox Path: $SANDBOX_PATH"
    echo

    echo "Component Status:"
    echo "---------------"

    # Check uCORE components
    if [[ -f "$UCORE_PATH/core/logging.sh" ]]; then
        echo "✅ uCORE Logging: Available"
    else
        echo "❌ uCORE Logging: Not found"
    fi

    if [[ -f "$UCORE_PATH/system/error-handler.sh" ]]; then
        echo "✅ uCORE Error Handler: Available"
    else
        echo "❌ uCORE Error Handler: Not found"
    fi

    # Check role permissions
    if [[ -f "$UMEMORY_PATH/system/uDATA-user-roles.json" ]]; then
        echo "✅ Role Permissions: Loaded"
    else
        echo "❌ Role Permissions: Not found"
    fi

    # Check sandbox access
    if [[ -d "$SANDBOX_PATH" ]]; then
        echo "✅ Sandbox: Available"
    else
        echo "❌ Sandbox: Not found"
    fi

    echo
    echo "Permissions for role '$current_role':"
    echo "-----------------------------------"

    # Test key permissions
    local permissions=(
        "script_execute:Script Execution"
        "script_read:Script Reading"
        "backup_create:Backup Creation"
        "umemory_read:uMEMORY Read"
        "sandbox:Sandbox Access"
    )

    for perm_pair in "${permissions[@]}"; do
        IFS=':' read -r perm_name perm_desc <<< "$perm_pair"
        if check_uscript_permission "$perm_name"; then
            echo "✅ $perm_desc: Allowed"
        else
            echo "❌ $perm_desc: Denied"
        fi
    done
}

# Enhanced script listing with role filtering
list_available_scripts() {
    local current_role=$(get_current_role)

    if ! check_uscript_permission "script_read"; then
        log_error "Permission denied: Role '$current_role' cannot list scripts"
        return 1
    fi

    local catalog_file="$USCRIPT_PATH/registry/catalog.json"
    if [[ ! -f "$catalog_file" ]]; then
        log_error "Script catalog not found: $catalog_file"
        return 1
    fi

    echo "Available Scripts for Role: $current_role"
    echo "========================================"
    echo

    # Filter scripts by security level
    jq -r '.scripts | to_entries[] | select(.value.security_level) | "\(.key):\(.value.security_level):\(.value.description)"' "$catalog_file" | \
    while IFS=':' read -r script_name security_level description; do
        if check_script_security_permission "$security_level" "$current_role"; then
            echo "✅ $script_name ($security_level)"
            echo "   $description"
            echo
        fi
    done
}

# Main integration function
main() {
    local command="${1:-status}"
    shift || true

    # Initialize integration
    load_role_permissions

    case "$command" in
        "status"|"info")
            show_integration_status
            ;;
        "execute"|"run")
            execute_script_with_role_check "$@"
            ;;
        "list"|"scripts")
            list_available_scripts
            ;;
        "backup")
            create_role_backup "$@"
            ;;
        "sandbox")
            use_sandbox "$@"
            ;;
        "umemory")
            access_umemory_resource "$@"
            ;;
        "check-permission"|"check")
            local permission="${1:-script_execute}"
            if check_uscript_permission "$permission"; then
                echo "✅ Permission granted: $permission"
                exit 0
            else
                echo "❌ Permission denied: $permission"
                exit 1
            fi
            ;;
        *)
            echo "uSCRIPT-uCORE Integration v1.3.3"
            echo "Usage: $0 <command> [options]"
            echo
            echo "Commands:"
            echo "  status                    - Show integration status"
            echo "  execute <script> [args]   - Execute script with role checking"
            echo "  list                      - List available scripts for current role"
            echo "  backup [type] [desc]      - Create role-specific backup"
            echo "  sandbox <op> [path]       - Access sandbox with role permissions"
            echo "  umemory <path> [op]       - Access uMEMORY resources"
            echo "  check-permission <perm>   - Check specific permission"
            echo
            ;;
    esac
}

# Export functions for use by other scripts
export -f get_current_role
export -f check_uscript_permission
export -f check_script_security_permission
export -f use_sandbox
export -f access_umemory_resource

# Run main function if executed directly
if [[ "${BASH_SOURCE[0]}" == "${0}" ]]; then
    main "$@"
fi
