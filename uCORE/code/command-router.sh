#!/bin/bash
# uDOS Command Router - Enhanced with Undo/Redo and Move Logging
# Handles command parsing, routing, and session-based state management

# Get uDOS root directory
UDOS_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"

# Session management for undo/redo
UNDO_STACK_FILE="/tmp/udos-undo-stack-$$"
REDO_STACK_FILE="/tmp/udos-redo-stack-$$"
MAX_UNDO_OPERATIONS=50

# Color definitions for logging
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Basic logging functions
log_info() { echo -e "${BLUE}ℹ️  $1${NC}"; }
log_success() { echo -e "${GREEN}✅ $1${NC}"; }
log_warning() { echo -e "${YELLOW}⚠️  $1${NC}"; }
log_error() { echo -e "${RED}❌ $1${NC}"; }

# Initialize session stacks
initialize_session_stacks() {
    touch "$UNDO_STACK_FILE"
    touch "$REDO_STACK_FILE"
    # Clean up on exit
    trap 'rm -f "$UNDO_STACK_FILE" "$REDO_STACK_FILE"' EXIT
}

# Add command to undo stack
add_to_undo_stack() {
    local command="$1"
    local args="$2"
    local timestamp="$3"
    local pre_state="$4"

    # Add to undo stack with metadata
    echo "$timestamp|$command|$args|$pre_state" >> "$UNDO_STACK_FILE"

    # Maintain stack size limit
    if [[ $(wc -l < "$UNDO_STACK_FILE") -gt $MAX_UNDO_OPERATIONS ]]; then
        tail -n $MAX_UNDO_OPERATIONS "$UNDO_STACK_FILE" > "${UNDO_STACK_FILE}.tmp"
        mv "${UNDO_STACK_FILE}.tmp" "$UNDO_STACK_FILE"
    fi

    # Clear redo stack when new command is executed
    > "$REDO_STACK_FILE"
}

# Capture system state before command execution
capture_pre_state() {
    local command="$1"
    local state=""

    case "$command" in
        DESTROY|destroy)
            # Capture current directory structure
            state="pwd:$(pwd)|files:$(ls -la | wc -l)"
            ;;
        BACKUP|backup)
            # Capture backup state
            state="backups:$(ls backup/ 2>/dev/null | wc -l)"
            ;;
        MISSION|mission)
            # Capture mission state
            local current_role=$(get_current_role)
            state="missions:$(find uMEMORY/role/$current_role/user/missions/ -name "*.md" 2>/dev/null | wc -l)"
            ;;
        TRASH|trash)
            # Capture trash state
            local current_role=$(get_current_role)
            local trash_dir="$UDOS_ROOT/uMEMORY/trash/$current_role"
            state="trash_items:$(ls -1 "$trash_dir" 2>/dev/null | wc -l)|role:$current_role"
            ;;
        ROLE|role)
            # Capture current role state
            local current_role=$(get_current_role)
            state="role:$current_role|timestamp:$(date '+%s')"
            ;;
        *)
            # Generic state capture
            state="timestamp:$(date '+%s')|role:$(get_current_role)"
            ;;
    esac

    echo "$state"
}

# Get current role helper function
get_current_role() {
    if [[ -f "$UDOS_ROOT/sandbox/current-role.conf" ]]; then
        grep "CURRENT_ROLE=" "$UDOS_ROOT/sandbox/current-role.conf" | cut -d'=' -f2 | tr -d '"'
    else
        echo "wizard"
    fi
}

# Enhanced logging functions with undo/redo support
log_command_start() {
    local command="$1"
    local args="$2"

    # Use assist-logger if available, otherwise basic logging
    if [[ -x "$UCORE/code/assist-logger.sh" ]]; then
        "$UCORE/code/assist-logger.sh" log "INFO" "uCORE" "Command started: $command $args" "Runtime classification in progress"
    fi
}

log_command_completion() {
    local command="$1"
    local args="$2"
    local result="$3"
    local execution_time="$4"

    # Use assist-logger for enhanced logging
    if [[ -x "$UCORE/code/assist-logger.sh" ]]; then
        "$UCORE/code/assist-logger.sh" enhance "$command $args" "$result" "$execution_time"
    fi

    # Also log as a move for tracking
    log_move "$command" "$args" "$result" "$execution_time"
}

log_move() {
    local command="$1"
    local args="$2"
    local result="$3"
    local execution_time="$4"

    # Get current role
    local current_role=$(get_current_role)

    # Log to moves directory
    local moves_dir="$UDOS_ROOT/uMEMORY/log/moves/$current_role"
    mkdir -p "$moves_dir"

    local timestamp=$(date '+%Y-%m-%d %H:%M:%S')
    local log_file="$moves_dir/core-moves-$(date '+%Y%m%d').log"

    local status_icon="✅"
    if [[ "$result" != "0" ]]; then
        status_icon="❌"
    fi

    # Enhanced move log with undo/redo context
    local undo_available="false"
    local redo_available="false"

    if [[ -f "$UNDO_STACK_FILE" && -s "$UNDO_STACK_FILE" ]]; then
        undo_available="true"
    fi

    if [[ -f "$REDO_STACK_FILE" && -s "$REDO_STACK_FILE" ]]; then
        redo_available="true"
    fi

    echo "[$timestamp] $status_icon uCORE: $command $args | Result: $result | Time: ${execution_time}ms | Undo: $undo_available | Redo: $redo_available" >> "$log_file"
}

# Enhanced route command with undo/redo support
route_command() {
    local command="$1"
    shift
    local args="$@"
    local start_time=$(date +%s)
    local timestamp=$(date '+%Y-%m-%d %H:%M:%S')

    # Initialize session stacks if not already done
    if [[ ! -f "$UNDO_STACK_FILE" ]]; then
        initialize_session_stacks
    fi

    # Handle special undo/redo/destroy/restore/repair commands first
    case "$command" in
        UNDO|undo)
            execute_undo "$args"
            return $?
            ;;
        REDO|redo)
            execute_redo "$args"
            return $?
            ;;
        DESTROY|destroy)
            execute_destroy "$args"
            return $?
            ;;
        RESTORE|restore)
            execute_restore "$args"
            return $?
            ;;
        REPAIR|repair)
            execute_repair "$args"
            return $?
            ;;
        TRASH|trash)
            execute_trash "$args"
            return $?
            ;;
        BACKUP|backup)
            execute_backup "$args"
            return $?
            ;;
        OK|ok)
            execute_ok_command "$args"
            return $?
            ;;
        END|end)
            execute_end_command "$args"
            return $?
            ;;
        ROLE|role)
            execute_role_management "$args"
            return $?
            ;;
        SETUP|setup)
            execute_setup_command "$args"
            return $?
            ;;
        DEV|dev)
            execute_dev_command "$args"
            return $?
            ;;
        VAR|var|VARIABLE|variable)
            execute_variable_command "$args"
            return $?
            ;;
        STORY|story)
            execute_story_command "$args"
            return $?
            ;;
    esac

    # Capture pre-state for undoable commands
    local pre_state=""
    if is_undoable_command "$command"; then
        pre_state=$(capture_pre_state "$command")
    fi

    # Log command initiation
    log_command_start "$command" "$args"

    # Classify command execution requirements
    local runtime="$(classify_command_runtime "$command")"
    local result=0

    case "$runtime" in
        bash)
            execute_bash_command "$command" $args
            result=$?
            ;;
        python)
            execute_python_command "$command" $args
            result=$?
            ;;
        isolated)
            execute_isolated_command "$command" $args
            result=$?
            ;;
        *)
            log_error "Unknown runtime: $runtime"
            result=1
            ;;
    esac

    # Add to undo stack if command was successful and undoable
    if [[ $result -eq 0 && -n "$pre_state" ]]; then
        add_to_undo_stack "$command" "$args" "$timestamp" "$pre_state"
    fi

    # Calculate execution time and log completion (macOS compatible)
    local end_time=$(date +%s)
    local execution_time=$((end_time - start_time))
    log_command_completion "$command" "$args" "$result" "$execution_time"

    return $result
}

# Check if command is undoable
is_undoable_command() {
    local command="$1"

    case "$command" in
        MISSION|mission|BACKUP|backup|DESTROY|destroy|TRASH|trash|ROLE|role)
            return 0
            ;;
        *)
            return 1
            ;;
    esac
}

# Classify command runtime requirements (enhanced with undo/redo/destroy/restore/repair)
classify_command_runtime() {
    local command="$1"

    case "$command" in
        # Pure bash commands (no venv needed)
        HELP|help|STATUS|status|TREE|tree|DISPLAY|display|LAYOUT|layout|ASCII|ascii|UNDO|undo|REDO|redo|OK|ok|END|end)
            echo "bash"
            ;;
        # Python-dependent commands (venv required)
        AI|ai|ANALYSIS|analysis|WEB|web|SERVER|server)
            echo "python"
            ;;
        # Isolated execution commands (including destroy/restore/repair/trash/backup/role/setup)
        DESTROY|destroy|BACKUP|backup|MISSION|mission|RESTORE|restore|REPAIR|repair|TRASH|trash|ROLE|role|SETUP|setup)
            echo "isolated"
            ;;
        # Default to bash for unknown commands
        *)
            echo "bash"
            ;;
    esac
}

# Undo/Redo/Destroy/Restore/Repair Implementation

# Execute undo operation
execute_undo() {
    local args="$1"

    if [[ ! -s "$UNDO_STACK_FILE" ]]; then
        log_error "No operations to undo in current session"
        return 1
    fi

    # Get last operation from undo stack
    local last_operation=$(tail -1 "$UNDO_STACK_FILE")
    local timestamp=$(echo "$last_operation" | cut -d'|' -f1)
    local command=$(echo "$last_operation" | cut -d'|' -f2)
    local command_args=$(echo "$last_operation" | cut -d'|' -f3)
    local pre_state=$(echo "$last_operation" | cut -d'|' -f4)

    # Remove from undo stack
    head -n -1 "$UNDO_STACK_FILE" > "${UNDO_STACK_FILE}.tmp"
    mv "${UNDO_STACK_FILE}.tmp" "$UNDO_STACK_FILE"

    # Add to redo stack
    echo "$last_operation" >> "$REDO_STACK_FILE"

    # Execute undo logic based on command type
    log_info "Undoing: $command $command_args (from $timestamp)"

    case "$command" in
        MISSION|mission)
            undo_mission_command "$command_args" "$pre_state"
            ;;
        BACKUP|backup)
            undo_backup_command "$command_args" "$pre_state"
            ;;
        DESTROY|destroy)
            undo_destroy_command "$command_args" "$pre_state"
            ;;
        TRASH|trash)
            undo_trash_command "$command_args" "$pre_state"
            ;;
        ROLE|role)
            undo_role_command "$command_args" "$pre_state"
            ;;
        *)
            log_warning "Undo not implemented for command: $command"
            return 1
            ;;
    esac

    log_success "Undo completed for: $command $command_args"
    return 0
}

# Execute redo operation
execute_redo() {
    local args="$1"

    if [[ ! -s "$REDO_STACK_FILE" ]]; then
        log_error "No operations to redo in current session"
        return 1
    fi

    # Get last operation from redo stack
    local last_operation=$(tail -1 "$REDO_STACK_FILE")
    local timestamp=$(echo "$last_operation" | cut -d'|' -f1)
    local command=$(echo "$last_operation" | cut -d'|' -f2)
    local command_args=$(echo "$last_operation" | cut -d'|' -f3)

    # Remove from redo stack
    head -n -1 "$REDO_STACK_FILE" > "${REDO_STACK_FILE}.tmp"
    mv "${REDO_STACK_FILE}.tmp" "$REDO_STACK_FILE"

    # Re-execute the command
    log_info "Redoing: $command $command_args (from $timestamp)"

    # Execute the original command again
    route_command "$command" $command_args

    log_success "Redo completed for: $command $command_args"
    return 0
}

# Execute destroy operation with enhanced logging
execute_destroy() {
    local args="$1"
    local current_role=$(get_current_role)

    log_warning "DESTROY operation initiated by role: $current_role"
    log_warning "Arguments: $args"

    # Create destroy log entry
    local destroy_log="$UDOS_ROOT/uMEMORY/log/moves/$current_role/destroy-$(date '+%Y%m%d').log"
    mkdir -p "$(dirname "$destroy_log")"
    echo "[$(date '+%Y-%m-%d %H:%M:%S')] 🗑️  DESTROY initiated: $args | Role: $current_role" >> "$destroy_log"

    # Execute destroy via isolated command
    execute_isolated_command "destroy" $args
    local result=$?

    # Log destroy completion
    if [[ $result -eq 0 ]]; then
        echo "[$(date '+%Y-%m-%d %H:%M:%S')] ✅ DESTROY completed successfully" >> "$destroy_log"
        log_success "DESTROY operation completed"
    else
        echo "[$(date '+%Y-%m-%d %H:%M:%S')] ❌ DESTROY failed with exit code: $result" >> "$destroy_log"
        log_error "DESTROY operation failed"
    fi

    return $result
}

# Execute restore operation with enhanced logging
execute_restore() {
    local args="$1"
    local current_role=$(get_current_role)

    log_info "RESTORE operation initiated by role: $current_role"
    log_info "Arguments: $args"

    # Create restore log entry
    local restore_log="$UDOS_ROOT/uMEMORY/log/moves/$current_role/restore-$(date '+%Y%m%d').log"
    mkdir -p "$(dirname "$restore_log")"
    echo "[$(date '+%Y-%m-%d %H:%M:%S')] 🔄 RESTORE initiated: $args | Role: $current_role" >> "$restore_log"

    # Execute restore via isolated command
    execute_isolated_command "restore" $args
    local result=$?

    # Log restore completion
    if [[ $result -eq 0 ]]; then
        echo "[$(date '+%Y-%m-%d %H:%M:%S')] ✅ RESTORE completed successfully" >> "$restore_log"
        log_success "RESTORE operation completed"
    else
        echo "[$(date '+%Y-%m-%d %H:%M:%S')] ❌ RESTORE failed with exit code: $result" >> "$restore_log"
        log_error "RESTORE operation failed"
    fi

    return $result
}

# Execute repair operation with enhanced logging
execute_repair() {
    local args="$1"
    local current_role=$(get_current_role)

    log_info "REPAIR operation initiated by role: $current_role"
    log_info "Arguments: $args"

    # Create repair log entry
    local repair_log="$UDOS_ROOT/uMEMORY/log/moves/$current_role/repair-$(date '+%Y%m%d').log"
    mkdir -p "$(dirname "$repair_log")"
    echo "[$(date '+%Y-%m-%d %H:%M:%S')] 🔧 REPAIR initiated: $args | Role: $current_role" >> "$repair_log"

    # Execute repair via isolated command
    execute_isolated_command "repair" $args
    local result=$?

    # Log repair completion
    if [[ $result -eq 0 ]]; then
        echo "[$(date '+%Y-%m-%d %H:%M:%S')] ✅ REPAIR completed successfully" >> "$repair_log"
        log_success "REPAIR operation completed"
    else
        echo "[$(date '+%Y-%m-%d %H:%M:%S')] ❌ REPAIR failed with exit code: $result" >> "$repair_log"
        log_error "REPAIR operation failed"
    fi

    return $result
}

# Execute trash management operation with uMEMORY integration
execute_trash() {
    local args="$1"
    local current_role=$(get_current_role)

    log_info "TRASH operation initiated by role: $current_role"
    log_info "Arguments: $args"

    # Create trash log entry
    local trash_log="$UDOS_ROOT/uMEMORY/log/moves/$current_role/trash-$(date '+%Y%m%d').log"
    mkdir -p "$(dirname "$trash_log")"
    echo "[$(date '+%Y-%m-%d %H:%M:%S')] 🗑️  TRASH initiated: $args | Role: $current_role" >> "$trash_log"

    # Ensure trash directory exists in uMEMORY
    local trash_dir="$UDOS_ROOT/uMEMORY/trash/$current_role"
    mkdir -p "$trash_dir"

    case "$args" in
        list|LIST)
            # List trash contents
            echo "Trash contents for role $current_role:"
            ls -la "$trash_dir" 2>/dev/null || echo "Trash is empty"
            ;;
        empty|EMPTY)
            # Empty trash with confirmation
            if [[ -d "$trash_dir" && "$(ls -A "$trash_dir" 2>/dev/null)" ]]; then
                echo "Emptying trash for role $current_role..."
                rm -rf "$trash_dir"/*
                echo "[$(date '+%Y-%m-%d %H:%M:%S')] ✅ TRASH emptied successfully" >> "$trash_log"
                log_success "Trash emptied successfully"
            else
                echo "Trash is already empty"
            fi
            ;;
        restore)
            # Restore items from trash
            shift 1  # Remove 'restore' argument
            local item="$1"
            if [[ -f "$trash_dir/$item" || -d "$trash_dir/$item" ]]; then
                mv "$trash_dir/$item" "$UDOS_ROOT/"
                echo "[$(date '+%Y-%m-%d %H:%M:%S')] ✅ TRASH restore: $item" >> "$trash_log"
                log_success "Restored from trash: $item"
            else
                echo "Item not found in trash: $item"
                return 1
            fi
            ;;
        *)
            # Move item to trash
            if [[ -f "$args" || -d "$args" ]]; then
                local basename_item=$(basename "$args")
                local timestamp=$(date '+%Y%m%d_%H%M%S')
                mv "$args" "$trash_dir/${timestamp}_${basename_item}"
                echo "[$(date '+%Y-%m-%d %H:%M:%S')] ✅ TRASH moved: $args -> ${timestamp}_${basename_item}" >> "$trash_log"
                log_success "Moved to trash: $args"
            else
                log_error "Item not found: $args"
                return 1
            fi
            ;;
    esac

    return 0
}

# Execute backup operation with uMEMORY integration
execute_backup() {
    local args="$1"
    local current_role=$(get_current_role)

    log_info "BACKUP operation initiated by role: $current_role"
    log_info "Arguments: $args"

    # Create backup log entry
    local backup_log="$UDOS_ROOT/uMEMORY/log/moves/$current_role/backup-$(date '+%Y%m%d').log"
    mkdir -p "$(dirname "$backup_log")"
    echo "[$(date '+%Y-%m-%d %H:%M:%S')] 💾 BACKUP initiated: $args | Role: $current_role" >> "$backup_log"

    case "$args" in
        create|CREATE)
            # Create new backup
            local timestamp=$(date '+%Y%m%d_%H%M%S')
            local backup_name="backup-${current_role}-${timestamp}.tar.gz"
            local backup_path="$UDOS_ROOT/backup/$backup_name"

            # Create backup directory if needed
            mkdir -p "$UDOS_ROOT/backup"

            # Create backup of current role's data
            tar -czf "$backup_path" -C "$UDOS_ROOT" \
                "uMEMORY/role/$current_role" \
                "sandbox" \
                2>/dev/null

            if [[ $? -eq 0 ]]; then
                echo "[$(date '+%Y-%m-%d %H:%M:%S')] ✅ BACKUP created: $backup_name" >> "$backup_log"
                log_success "Backup created: $backup_name"
            else
                echo "[$(date '+%Y-%m-%d %H:%M:%S')] ❌ BACKUP creation failed" >> "$backup_log"
                log_error "Backup creation failed"
                return 1
            fi
            ;;
        list|LIST)
            # List available backups
            echo "Available backups:"
            ls -la "$UDOS_ROOT/backup/"*${current_role}* 2>/dev/null || echo "No backups found for role $current_role"
            ;;
        restore)
            # Restore from backup
            shift 1  # Remove 'restore' argument
            local backup_file="$1"
            if [[ -f "$UDOS_ROOT/backup/$backup_file" ]]; then
                tar -xzf "$UDOS_ROOT/backup/$backup_file" -C "$UDOS_ROOT"
                echo "[$(date '+%Y-%m-%d %H:%M:%S')] ✅ BACKUP restored: $backup_file" >> "$backup_log"
                log_success "Restored from backup: $backup_file"
            else
                log_error "Backup file not found: $backup_file"
                return 1
            fi
            ;;
        *)
            # Execute backup via isolated command for other operations
            execute_isolated_command "backup" $args
            ;;
    esac

    return 0
}

# Get current assist mode status
get_assist_mode() {
    local assist_status_file="$UDOS_ROOT/sandbox/assist-mode.conf"
    if [[ -f "$assist_status_file" ]]; then
        grep "ASSIST_MODE=" "$assist_status_file" | cut -d'=' -f2 | tr -d '"'
    else
        echo "false"
    fi
}

# Set assist mode status
set_assist_mode() {
    local mode="$1"
    local assist_status_file="$UDOS_ROOT/sandbox/assist-mode.conf"
    mkdir -p "$(dirname "$assist_status_file")"
    echo "ASSIST_MODE=\"$mode\"" > "$assist_status_file"
}

# Execute OK command - context-dependent behavior
execute_ok_command() {
    local args="$1"
    local current_role=$(get_current_role)
    local assist_mode=$(get_assist_mode)

    log_info "OK command initiated by role: $current_role | Assist Mode: $assist_mode"

    if [[ "$assist_mode" == "true" ]]; then
        # In Assist Mode: OK means continue/proceed
        log_success "Assist Mode: Continuing with AI recommendations..."

        # Log the OK action
        local assist_log="$UDOS_ROOT/uMEMORY/log/moves/$current_role/assist-$(date '+%Y%m%d').log"
        mkdir -p "$(dirname "$assist_log")"
        echo "[$(date '+%Y-%m-%d %H:%M:%S')] ✅ OK: Continue in Assist Mode | Role: $current_role" >> "$assist_log"

        # Trigger workflow assist continue
        if [[ -x "$UDOS_ROOT/dev/workflow.sh" ]]; then
            "$UDOS_ROOT/dev/workflow.sh" assist continue
        fi
    else
        # Not in Assist Mode: OK enters Assist Mode
        log_info "Entering Assist Mode..."
        set_assist_mode "true"

        # Log the mode change
        local mode_log="$UDOS_ROOT/uMEMORY/log/moves/$current_role/mode-changes-$(date '+%Y%m%d').log"
        mkdir -p "$(dirname "$mode_log")"
        echo "[$(date '+%Y-%m-%d %H:%M:%S')] 🤖 ASSIST MODE ENTERED | Role: $current_role" >> "$mode_log"

        log_success "Entered Assist Mode (OI) - AI will analyze context and provide recommendations"

        # Trigger workflow assist enter
        if [[ -x "$UDOS_ROOT/dev/workflow.sh" ]]; then
            "$UDOS_ROOT/dev/workflow.sh" assist enter
        fi
    fi

    return 0
}

# Execute END command - exit Assist Mode to Command Mode
execute_end_command() {
    local args="$1"
    local current_role=$(get_current_role)
    local assist_mode=$(get_assist_mode)

    log_info "END command initiated by role: $current_role | Current Assist Mode: $assist_mode"

    if [[ "$assist_mode" == "true" ]]; then
        # Exit Assist Mode
        set_assist_mode "false"

        # Log the mode change
        local mode_log="$UDOS_ROOT/uMEMORY/log/moves/$current_role/mode-changes-$(date '+%Y%m%d').log"
        mkdir -p "$(dirname "$mode_log")"
        echo "[$(date '+%Y-%m-%d %H:%M:%S')] 👤 COMMAND MODE ENTERED | Role: $current_role" >> "$mode_log"

        log_success "Exited Assist Mode (OI) - Returned to Command Mode (IO)"

        # Trigger workflow assist exit
        if [[ -x "$UDOS_ROOT/dev/workflow.sh" ]]; then
            "$UDOS_ROOT/dev/workflow.sh" assist exit
        fi
    else
        log_warning "Already in Command Mode - END command has no effect"
    fi

    return 0
}

# Execute role management operations
execute_role_management() {
    local args="$1"
    local current_role=$(get_current_role)

    log_info "ROLE management initiated by role: $current_role"
    log_info "Arguments: $args"

    # Create role management log entry
    local role_log="$UDOS_ROOT/uMEMORY/log/moves/$current_role/role-management-$(date '+%Y%m%d').log"
    mkdir -p "$(dirname "$role_log")"
    echo "[$(date '+%Y-%m-%d %H:%M:%S')] 👤 ROLE management initiated: $args | Current Role: $current_role" >> "$role_log"

    case "$args" in
        list|LIST)
            # List available roles
            echo "Available roles:"
            echo "1. wizard - System Administrator"
            echo "2. crypt - Security Specialist"
            echo "3. imp - Development Assistant"
            echo "4. ghost - Background Monitor"
            echo "5. sorcerer - Advanced Operations"
            echo "6. tomb - Archive Manager"
            echo "7. drone - Automated Tasks"
            echo "8. extensions - Extension Manager"
            echo ""
            echo "Current role: $current_role"
            ;;
        switch)
            # Switch to different role
            shift 1  # Remove 'switch' argument
            local new_role="$1"

            # Validate role
            case "$new_role" in
                wizard|crypt|imp|ghost|sorcerer|tomb|drone|extensions)
                    # Update current role
                    local role_file="$UDOS_ROOT/sandbox/current-role.conf"
                    mkdir -p "$(dirname "$role_file")"
                    echo "CURRENT_ROLE=\"$new_role\"" > "$role_file"

                    # Initialize role-specific directories
                    mkdir -p "$UDOS_ROOT/uMEMORY/role/$new_role/user"
                    mkdir -p "$UDOS_ROOT/uMEMORY/log/moves/$new_role"
                    mkdir -p "$UDOS_ROOT/sandbox/$new_role"

                    echo "[$(date '+%Y-%m-%d %H:%M:%S')] ✅ ROLE switched: $current_role -> $new_role" >> "$role_log"
                    log_success "Role switched from $current_role to $new_role"
                    ;;
                *)
                    log_error "Invalid role: $new_role"
                    echo "Valid roles: wizard, crypt, imp, ghost, sorcerer, tomb, drone, extensions"
                    return 1
                    ;;
            esac
            ;;
        check|CHECK)
            # Check role setup and permissions
            echo "Role Setup Check for: $current_role"
            echo "================================"

            # Check role directories
            local role_dir="$UDOS_ROOT/uMEMORY/role/$current_role"
            local log_dir="$UDOS_ROOT/uMEMORY/log/moves/$current_role"
            local sandbox_dir="$UDOS_ROOT/sandbox/$current_role"

            echo "Role Directory: $(test -d "$role_dir" && echo "✅ EXISTS" || echo "❌ MISSING")"
            echo "Log Directory: $(test -d "$log_dir" && echo "✅ EXISTS" || echo "❌ MISSING")"
            echo "Sandbox Directory: $(test -d "$sandbox_dir" && echo "✅ EXISTS" || echo "❌ MISSING")"

            # Check for role-specific extensions/installers
            local extensions_dir="$UDOS_ROOT/uMEMORY/role/$current_role/extensions"
            echo "Extensions Directory: $(test -d "$extensions_dir" && echo "✅ EXISTS" || echo "❌ MISSING")"

            if [[ -d "$extensions_dir" ]]; then
                echo "Available Extensions:"
                ls -la "$extensions_dir" 2>/dev/null || echo "No extensions found"
            fi
            ;;
        install)
            # Install role-specific extensions/installers
            shift 1  # Remove 'install' argument
            local extension="$1"

            if [[ -z "$extension" ]]; then
                log_error "Extension name required"
                return 1
            fi

            # Check for extension installer
            local installer="$UDOS_ROOT/uMEMORY/role/$current_role/extensions/$extension/install.sh"
            if [[ -x "$installer" ]]; then
                echo "Installing extension: $extension for role: $current_role"
                "$installer"
                echo "[$(date '+%Y-%m-%d %H:%M:%S')] ✅ EXTENSION installed: $extension for $current_role" >> "$role_log"
                log_success "Extension installed: $extension"
            else
                log_error "Extension installer not found: $extension"
                return 1
            fi
            ;;
        *)
            log_error "Unknown role command: $args"
            echo "Available commands: list, switch <role>, check, install <extension>"
            return 1
            ;;
    esac

    return 0
}

# Execute setup command with enhanced role and testing management
execute_setup_command() {
    local args="$1"
    local current_role=$(get_current_role)

    log_info "SETUP command initiated by role: $current_role"
    log_info "Arguments: $args"

    # Create setup log entry
    local setup_log="$UDOS_ROOT/uMEMORY/log/moves/$current_role/setup-$(date '+%Y%m%d').log"
    mkdir -p "$(dirname "$setup_log")"
    echo "[$(date '+%Y-%m-%d %H:%M:%S')] ⚙️  SETUP initiated: $args | Role: $current_role" >> "$setup_log"

    case "$args" in
        role|ROLE)
            # Setup current role environment
            echo "Setting up environment for role: $current_role"

            # Create all necessary directories
            mkdir -p "$UDOS_ROOT/uMEMORY/role/$current_role/user"
            mkdir -p "$UDOS_ROOT/uMEMORY/role/$current_role/extensions"
            mkdir -p "$UDOS_ROOT/uMEMORY/log/moves/$current_role"
            mkdir -p "$UDOS_ROOT/sandbox/$current_role"

            # Create role-specific testing directory in sandbox (not dev)
            mkdir -p "$UDOS_ROOT/sandbox/$current_role/testing"

            # Create default configuration files
            local role_config="$UDOS_ROOT/sandbox/$current_role/config.conf"
            if [[ ! -f "$role_config" ]]; then
                cat > "$role_config" << EOF
# Configuration for role: $current_role
ROLE_NAME="$current_role"
CREATED_DATE="$(date '+%Y-%m-%d %H:%M:%S')"
TESTING_ENABLED="true"
TESTING_DIR="$UDOS_ROOT/sandbox/$current_role/testing"
EOF
            fi

            echo "[$(date '+%Y-%m-%d %H:%M:%S')] ✅ SETUP completed for role: $current_role" >> "$setup_log"
            log_success "Role setup completed for: $current_role"
            ;;
        test|TEST)
            # Setup testing environment in sandbox for current role
            local test_dir="$UDOS_ROOT/sandbox/$current_role/testing"
            mkdir -p "$test_dir"

            echo "Setting up testing environment for role: $current_role"
            echo "Testing directory: $test_dir"

            # Create basic testing structure
            mkdir -p "$test_dir/scripts"
            mkdir -p "$test_dir/data"
            mkdir -p "$test_dir/results"

            # Create default test script
            local test_script="$test_dir/scripts/basic-test.sh"
            if [[ ! -f "$test_script" ]]; then
                cat > "$test_script" << 'EOF'
#!/bin/bash
# Basic test script for uDOS role testing
# This script runs in sandbox, not dev mode

echo "Running basic tests for role: $(basename $(dirname $(dirname $PWD)))"
echo "Test timestamp: $(date)"
echo "Test environment: Sandbox (Production)"

# Add your role-specific tests here
echo "✅ Basic test completed"
EOF
                chmod +x "$test_script"
            fi

            echo "[$(date '+%Y-%m-%d %H:%M:%S')] ✅ TESTING setup completed for role: $current_role" >> "$setup_log"
            log_success "Testing environment setup completed in sandbox for: $current_role"
            ;;
        check|CHECK)
            # Check setup status
            echo "Setup Check for role: $current_role"
            echo "================================"

            # Check all required directories
            local checks=(
                "uMEMORY/role/$current_role/user"
                "uMEMORY/role/$current_role/extensions"
                "uMEMORY/log/moves/$current_role"
                "sandbox/$current_role"
                "sandbox/$current_role/testing"
            )

            for check_path in "${checks[@]}"; do
                local full_path="$UDOS_ROOT/$check_path"
                echo "$check_path: $(test -d "$full_path" && echo "✅ EXISTS" || echo "❌ MISSING")"
            done

            # Check configuration
            local role_config="$UDOS_ROOT/sandbox/$current_role/config.conf"
            echo "Role Config: $(test -f "$role_config" && echo "✅ EXISTS" || echo "❌ MISSING")"

            # Check testing setup
            local test_script="$UDOS_ROOT/sandbox/$current_role/testing/scripts/basic-test.sh"
            echo "Test Scripts: $(test -f "$test_script" && echo "✅ EXISTS" || echo "❌ MISSING")"
            ;;
        *)
            # Execute setup via isolated command for other operations
            execute_isolated_command "setup" $args
            ;;
    esac

    return 0
}

# Undo specific command implementations
undo_mission_command() {
    local command_args="$1"
    local pre_state="$2"

    # Extract mission count from pre_state
    local prev_mission_count=$(echo "$pre_state" | grep -o 'missions:[0-9]*' | cut -d':' -f2)
    local current_role=$(get_current_role)
    local missions_dir="$UDOS_ROOT/uMEMORY/role/$current_role/user/missions"

    # If mission was created, find and remove the most recent one
    if [[ "$command_args" == *"create"* ]]; then
        local newest_mission=$(find "$missions_dir" -name "*.md" -type f -exec stat -f "%m %N" {} + 2>/dev/null | sort -nr | head -1 | cut -d' ' -f2-)
        if [[ -n "$newest_mission" ]]; then
            rm -f "$newest_mission"
            log_info "Removed mission: $(basename "$newest_mission")"
        fi
    fi
}

undo_backup_command() {
    local command_args="$1"
    local pre_state="$2"

    # Extract backup count from pre_state
    local prev_backup_count=$(echo "$pre_state" | grep -o 'backups:[0-9]*' | cut -d':' -f2)

    # If backup was created, remove the most recent one
    if [[ "$command_args" == *"create"* ]]; then
        local newest_backup=$(ls -t "$UDOS_ROOT/backup/"*.tar.gz* 2>/dev/null | head -1)
        if [[ -n "$newest_backup" ]]; then
            rm -f "$newest_backup"
            log_info "Removed backup: $(basename "$newest_backup")"
        fi
    fi
}

undo_destroy_command() {
    local command_args="$1"
    local pre_state="$2"

    # For destroy commands, undo means restore
    log_info "Undo destroy: attempting restore operation"
    execute_restore "$command_args"
}

# Undo trash operations
undo_trash_command() {
    local command_args="$1"
    local pre_state="$2"
    local current_role=$(get_current_role)
    local trash_dir="$UDOS_ROOT/uMEMORY/trash/$current_role"

    case "$command_args" in
        empty|EMPTY)
            log_warning "Cannot undo trash empty operation - data permanently deleted"
            return 1
            ;;
        restore)
            # Undo restore means move back to trash
            shift 1  # Remove 'restore' argument
            local item="$1"
            if [[ -f "$UDOS_ROOT/$item" || -d "$UDOS_ROOT/$item" ]]; then
                local timestamp=$(date '+%Y%m%d_%H%M%S')
                mv "$UDOS_ROOT/$item" "$trash_dir/${timestamp}_${item}"
                log_info "Undid trash restore: moved $item back to trash"
            fi
            ;;
        *)
            # Undo move to trash means restore from trash
            local basename_item=$(basename "$command_args")
            local trash_item=$(ls -t "$trash_dir/"*"_${basename_item}" 2>/dev/null | head -1)
            if [[ -n "$trash_item" ]]; then
                mv "$trash_item" "$UDOS_ROOT/$basename_item"
                log_info "Undid trash: restored $basename_item from trash"
            fi
            ;;
    esac
}

# Undo role management operations
undo_role_command() {
    local command_args="$1"
    local pre_state="$2"

    # Extract previous role from pre_state
    local prev_role=$(echo "$pre_state" | grep -o 'role:[a-z]*' | cut -d':' -f2)

    case "$command_args" in
        switch)
            # Undo role switch by switching back to previous role
            if [[ -n "$prev_role" ]]; then
                local role_file="$UDOS_ROOT/sandbox/current-role.conf"
                echo "CURRENT_ROLE=\"$prev_role\"" > "$role_file"
                log_info "Undid role switch: restored previous role $prev_role"
            else
                log_warning "Cannot determine previous role for undo"
                return 1
            fi
            ;;
        *)
            log_warning "Undo not implemented for role command: $command_args"
            return 1
            ;;
    esac
}

# Execute bash-only command
execute_bash_command() {
    local command="$1"
    shift
    local args="$@"

    local script_path="$USCRIPT/library/ucode/${command}.sh"
    local ucore_path="$UDOS_ROOT/uCORE/core/utilities/${command}.sh"

    if [[ -f "$script_path" && -x "$script_path" ]]; then
        "$script_path" $args
    elif [[ -f "$ucore_path" && -x "$ucore_path" ]]; then
        "$ucore_path" $args
    else
        log_error "Script not found: $command (checked uSCRIPT and uCORE)"
        return 1
    fi
}

# Execute Python command with virtual environment
execute_python_command() {
    local command="$1"
    shift
    local args="$@"

    # Activate Python virtual environment
    source "$USCRIPT/bin/activate-venv.sh" python

    # Execute command
    execute_bash_command "$command" $args
}

# Execute isolated command in isolated session
execute_isolated_command() {
    local command="$1"
    shift
    local args="$@"

    # Use session manager for isolation
    "$USCRIPT/bin/session-manager.sh" execute "$command" $args
}

# Execute development mode commands
execute_dev_command() {
    local args="$1"
    local current_role=$(get_current_role)

    log_info "DEV command initiated by role: $current_role"
    log_info "Arguments: $args"

    # Route to dev command handler
    "$UDOS_ROOT/uCORE/core/dev-command.sh" $args
    return $?
}

# Execute variable management commands
execute_variable_command() {
    local args="$1"
    local current_role=$(get_current_role)

    log_info "VAR command initiated by role: $current_role"
    log_info "Arguments: $args"

    # Route to variable manager
    "$UDOS_ROOT/uCORE/core/variable-manager.sh" $args
    return $?
}# Execute STORY commands for variable collection
execute_story_command() {
    local args="$1"
    local current_role=$(get_current_role)

    log_info "STORY command initiated by role: $current_role"
    log_info "Arguments: $args"

    # Route to variable manager STORY subcommands
    "$UDOS_ROOT/uCORE/core/variable-manager.sh" STORY $args
    return $?
}
