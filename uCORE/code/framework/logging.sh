#!/bin/bash
# uCORE Logging & Error Handling Framework
# Universal Device Operating System
# Version: 1.0.5.2

# Logging Configuration
# ====================

# Log levels
declare -r LOG_LEVEL_DEBUG=0
declare -r LOG_LEVEL_INFO=1
declare -r LOG_LEVEL_WARN=2
declare -r LOG_LEVEL_ERROR=3
declare -r LOG_LEVEL_FATAL=4

# Current log level (default: INFO)
UDOS_LOG_LEVEL=${UDOS_LOG_LEVEL:-$LOG_LEVEL_INFO}

# Log file locations
UDOS_LOG_DIR="${UDOS_MEMORY}/logs"
UDOS_MAIN_LOG="${UDOS_LOG_DIR}/udos.log"
UDOS_ERROR_LOG="${UDOS_LOG_DIR}/error.log"
UDOS_DEBUG_LOG="${UDOS_LOG_DIR}/debug.log"

# Initialize logging system
init_logging() {
    # Create log directory
    mkdir -p "$UDOS_LOG_DIR"
    
    # Initialize log files
    touch "$UDOS_MAIN_LOG" "$UDOS_ERROR_LOG" "$UDOS_DEBUG_LOG"
    
    # Set up log rotation if logrotate is available
    if command -v logrotate >/dev/null 2>&1; then
        setup_log_rotation
    fi
    
    return 0
}

# Log function with levels
udos_log() {
    local level="$1"
    local component="$2"
    local message="$3"
    local log_file="${4:-$UDOS_MAIN_LOG}"
    
    local timestamp="$(date '+%Y-%m-%d %H:%M:%S')"
    local log_entry="[$timestamp] [$level] [$component] $message"
    
    # Check if we should log based on level
    case "$level" in
        "DEBUG") local numeric_level=$LOG_LEVEL_DEBUG ;;
        "INFO")  local numeric_level=$LOG_LEVEL_INFO ;;
        "WARN")  local numeric_level=$LOG_LEVEL_WARN ;;
        "ERROR") local numeric_level=$LOG_LEVEL_ERROR ;;
        "FATAL") local numeric_level=$LOG_LEVEL_FATAL ;;
        *) local numeric_level=$LOG_LEVEL_INFO ;;
    esac
    
    if [[ $numeric_level -ge $UDOS_LOG_LEVEL ]]; then
        echo "$log_entry" | tee -a "$log_file"
        
        # Also log errors to error log
        if [[ "$level" == "ERROR" || "$level" == "FATAL" ]]; then
            echo "$log_entry" >> "$UDOS_ERROR_LOG"
        fi
        
        # Debug messages go to debug log
        if [[ "$level" == "DEBUG" ]]; then
            echo "$log_entry" >> "$UDOS_DEBUG_LOG"
        fi
    fi
}

# Convenience logging functions
log_debug() {
    udos_log "DEBUG" "${1:-SYSTEM}" "$2"
}

log_info() {
    udos_log "INFO" "${1:-SYSTEM}" "$2"
}

log_warn() {
    udos_log "WARN" "${1:-SYSTEM}" "$2"
}

log_error() {
    udos_log "ERROR" "${1:-SYSTEM}" "$2"
}

log_fatal() {
    udos_log "FATAL" "${1:-SYSTEM}" "$2"
}

# Error handling functions
# =======================

# Set error handling mode
set_error_mode() {
    local mode="$1"
    
    case "$mode" in
        "strict")
            set -euo pipefail
            trap 'handle_error $? $LINENO $BASH_LINENO "$BASH_COMMAND" "${FUNCNAME[@]}"' ERR
            ;;
        "permissive")
            set +euo pipefail
            trap - ERR
            ;;
        *)
            log_error "ERROR_HANDLER" "Unknown error mode: $mode"
            return 1
            ;;
    esac
}

# Error handler function
handle_error() {
    local exit_code="$1"
    local line_number="$2"
    local bash_lineno="$3"
    local command="$4"
    shift 4
    local function_stack=("$@")
    
    local error_msg="Command failed with exit code $exit_code"
    error_msg="${error_msg}\nLine: $line_number"
    error_msg="${error_msg}\nCommand: $command"
    
    if [[ ${#function_stack[@]} -gt 0 ]]; then
        error_msg="${error_msg}\nFunction stack: ${function_stack[*]}"
    fi
    
    log_error "ERROR_HANDLER" "$error_msg"
    
    # Generate error report
    generate_error_report "$exit_code" "$line_number" "$command" "${function_stack[@]}"
    
    # Decide if we should exit or continue
    if [[ $exit_code -ge 2 ]]; then
        log_fatal "ERROR_HANDLER" "Fatal error detected, exiting"
        exit "$exit_code"
    fi
}

# Generate detailed error report
generate_error_report() {
    local exit_code="$1"
    local line_number="$2"
    local command="$3"
    shift 3
    local function_stack=("$@")
    
    local report_file="${UDOS_LOG_DIR}/error_report_$(date +%Y%m%d_%H%M%S).log"
    
    {
        echo "==============================================="
        echo "uDOS Error Report"
        echo "==============================================="
        echo "Timestamp: $(date)"
        echo "Exit Code: $exit_code"
        echo "Line Number: $line_number"
        echo "Command: $command"
        echo "Function Stack: ${function_stack[*]}"
        echo ""
        echo "System Information:"
        if [[ -f "$UDOS_ROOT/VERSION" ]]; then
            echo "- uDOS Version: $(grep VERSION "$UDOS_ROOT/VERSION" | head -1 | cut -d'=' -f2 | tr -d '"')"
        fi
        echo "- Shell: $SHELL"
        echo "- OS: $(uname -s)"
        echo ""
        echo "Environment Variables:"
        env | grep "UDOS_" | sort
        echo ""
        echo "Recent Log Entries:"
        if [[ -f "$UDOS_MAIN_LOG" ]]; then
            tail -20 "$UDOS_MAIN_LOG" 2>/dev/null || echo "No log entries found"
        else
            echo "Log file not found"
        fi
        echo "==============================================="
    } > "$report_file"
    
    log_info "ERROR_HANDLER" "Error report generated: $report_file"
}

# Setup log rotation
setup_log_rotation() {
    local logrotate_config="/tmp/udos-logrotate.conf"
    
    cat > "$logrotate_config" << EOF
$UDOS_LOG_DIR/*.log {
    daily
    rotate 7
    compress
    delaycompress
    missingok
    notifempty
    create 644
}
EOF
    
    # Note: This would typically be installed to /etc/logrotate.d/
    # For now, we just create the config file
    log_info "LOGGING" "Log rotation configuration created at $logrotate_config"
}

# Performance monitoring
# =====================

# Start timing operation
start_timer() {
    local operation_name="$1"
    
    if [[ ${BASH_VERSION%%.*} -ge 4 ]]; then
        UDOS_TIMER_START[${operation_name}]=$(date +%s.%N)
    else
        # Bash 3.x compatibility
        local index=-1
        local i=0
        for key in $UDOS_TIMER_START_KEYS; do
            if [[ "$key" == "$operation_name" ]]; then
                index=$i
                break
            fi
            ((i++))
        done
        
        if [[ $index -eq -1 ]]; then
            UDOS_TIMER_START_KEYS="$UDOS_TIMER_START_KEYS $operation_name"
            UDOS_TIMER_START_VALUES="$UDOS_TIMER_START_VALUES $(date +%s)"
        else
            # Update existing
            local new_values=""
            i=0
            for val in $UDOS_TIMER_START_VALUES; do
                if [[ $i -eq $index ]]; then
                    new_values="$new_values $(date +%s)"
                else
                    new_values="$new_values $val"
                fi
                ((i++))
            done
            UDOS_TIMER_START_VALUES="$new_values"
        fi
    fi
}

# End timing operation
end_timer() {
    local operation_name="$1"
    local start_time=""
    
    if [[ ${BASH_VERSION%%.*} -ge 4 ]]; then
        start_time="${UDOS_TIMER_START[${operation_name}]:-}"
        if [[ -n "$start_time" ]]; then
            unset UDOS_TIMER_START[${operation_name}]
        fi
    else
        # Bash 3.x compatibility
        local index=-1
        local i=0
        for key in $UDOS_TIMER_START_KEYS; do
            if [[ "$key" == "$operation_name" ]]; then
                index=$i
                break
            fi
            ((i++))
        done
        
        if [[ $index -ne -1 ]]; then
            i=0
            for val in $UDOS_TIMER_START_VALUES; do
                if [[ $i -eq $index ]]; then
                    start_time="$val"
                    break
                fi
                ((i++))
            done
        fi
    fi
    
    if [[ -z "$start_time" ]]; then
        log_warn "TIMER" "Timer not started for operation: $operation_name"
        return 1
    fi
    
    local end_time=$(date +%s)
    local duration=$((end_time - start_time))
    
    log_info "TIMER" "Operation '$operation_name' completed in ${duration}s"
}

# Initialize arrays for timers
if [[ ${BASH_VERSION%%.*} -ge 4 ]]; then
    declare -A UDOS_TIMER_START
else
    # For bash 3.x compatibility, use a simple approach
    UDOS_TIMER_START_KEYS=""
    UDOS_TIMER_START_VALUES=""
fi

# Export functions
export -f init_logging udos_log log_debug log_info log_warn log_error log_fatal
export -f set_error_mode handle_error generate_error_report
export -f start_timer end_timer
