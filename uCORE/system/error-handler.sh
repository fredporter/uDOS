#!/bin/bash
# uDOS Error Handler Core v1.3.1 - Comprehensive Error Management
set -euo pipefail

# Error Handler Configuration
export UDOS_ERROR_HANDLER_VERSION="1.3.1"
export UDOS_ERROR_LOG_DIR="${UDOS_ROOT}/wizard/logs/errors"
export UDOS_DEBUG_LOG_DIR="${UDOS_ROOT}/wizard/logs/debug"
export UDOS_CRASH_LOG_DIR="${UDOS_ROOT}/wizard/logs/crashes"
export UDOS_LOOP_DETECTION_FILE="/tmp/udos-loop-detection"
export UDOS_ERROR_THRESHOLD=5
export UDOS_LOOP_THRESHOLD=3

# Load core display systems if not already loaded
if [[ "$UDOS_POLAROID_INITIALIZED" != "1" ]]; then
    # Load UTF-8 and color systems
    SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
    if [[ -f "$SCRIPT_DIR/../uSCRIPT/library/shell/ensure-utf8.sh" ]]; then
        source "$SCRIPT_DIR/../uSCRIPT/library/shell/ensure-utf8.sh"
    fi
    if [[ -f "$SCRIPT_DIR/polaroid-colors.sh" ]]; then
        source "$SCRIPT_DIR/polaroid-colors.sh"
    fi
fi

# Legacy color definitions for compatibility (will use Polaroid colors if loaded)
if [[ -z "${RED:-}" ]]; then
    readonly RED='\033[0;31m'
    readonly GREEN='\033[0;32m'
    readonly YELLOW='\033[1;33m'
    readonly BLUE='\033[0;34m'
    readonly PURPLE='\033[0;35m'
    readonly CYAN='\033[0;36m'
    readonly WHITE='\033[1;37m'
    readonly NC='\033[0m'
fi

# Ensure log directories exist
init_error_logging() {
    mkdir -p "$UDOS_ERROR_LOG_DIR" "$UDOS_DEBUG_LOG_DIR" "$UDOS_CRASH_LOG_DIR"

    # Initialize loop detection
    echo "0" > "$UDOS_LOOP_DETECTION_FILE"

    # Set up error traps
    trap 'handle_error $? $LINENO $BASH_COMMAND' ERR
    trap 'handle_exit' EXIT
    trap 'handle_signal SIGINT' INT
    trap 'handle_signal SIGTERM' TERM
}

# Generate unique error ID
generate_error_id() {
    echo "E$(date +%Y%m%d%H%M%S)-$(openssl rand -hex 4 2>/dev/null || echo $(( RANDOM % 10000 )))"
}

# Role-based error messages
get_role_error_message() {
    local error_type="$1"
    local role="${UDOS_CURRENT_ROLE:-wizard}"

    case "$role" in
        "ghost")
            case "$error_type" in
                "crash") echo "👻 The spectral plane encountered turbulence. Attempting ethereal recovery..." ;;
                "loop") echo "👻 Caught in a ghostly loop. Breaking the ethereal cycle..." ;;
                "permission") echo "👻 The spirits deny access to this realm..." ;;
                *) echo "👻 A phantom error has manifested. Investigating the otherworld..." ;;
            esac
            ;;
        "tomb")
            case "$error_type" in
                "crash") echo "⚰️ Ancient systems have crumbled. Excavating from the ruins..." ;;
                "loop") echo "⚰️ Trapped in an eternal cycle. Breaking the burial chains..." ;;
                "permission") echo "⚰️ The tomb guardian forbids entry..." ;;
                *) echo "⚰️ Archaeological error detected. Consulting the dead scrolls..." ;;
            esac
            ;;
        "crypt")
            case "$error_type" in
                "crash") echo "🪦 Crypt systems sealed. Attempting resurrection..." ;;
                "loop") echo "🪦 Crypt recursion detected. Breaking the seal..." ;;
                "permission") echo "🪦 Crypt access denied. Sacred data protected..." ;;
                *) echo "🪦 Cryptic error encountered. Deciphering ancient code..." ;;
            esac
            ;;
        "drone")
            case "$error_type" in
                "crash") echo "🤖 Drone systems offline. Initiating emergency protocols..." ;;
                "loop") echo "🤖 Recursive algorithm detected. Breaking infinite execution..." ;;
                "permission") echo "🤖 Access denied by security protocols..." ;;
                *) echo "🤖 System anomaly detected. Running diagnostic subroutines..." ;;
            esac
            ;;
        "imp")
            case "$error_type" in
                "crash") echo "👹 Mischievous code has caused chaos! Imp cleanup in progress..." ;;
                "loop") echo "👹 Caught in an imp's trick loop. Breaking the spell..." ;;
                "permission") echo "👹 The imp's pranks are restricted in this area..." ;;
                *) echo "👹 Impish error detected. Applying creative debugging..." ;;
            esac
            ;;
        "knight")
            case "$error_type" in
                "crash") echo "🛡️ The Knight stands guard. System breach repelled, recovery in progress..." ;;
                "loop") echo "🛡️ Knight detected a recursive battle. Breaking the siege..." ;;
                "permission") echo "🛡️ Knightly honor restricts this action..." ;;
                *) echo "🛡️ Knightly error encountered. Consulting the code of chivalry..." ;;
            esac
            ;;
        "sorcerer")
#
# uDOS Ethos: Clean, flat, minimal data. Respect host system. Backup and cleanup always.
#
            case "$error_type" in
                "crash") echo "🔮 The spell has backfired! Consulting the arcane texts..." ;;
                "loop") echo "🔮 Caught in a magical recursion. Dispelling the enchantment..." ;;
                "permission") echo "🔮 The ward blocks your magical access..." ;;
                *) echo "🔮 Magical error detected. Reviewing the grimoire..." ;;
            esac
            ;;
        "wizard")
            case "$error_type" in
                "crash") echo "🧙‍♂️ System failure detected. Applying advanced recovery magic..." ;;
                "loop") echo "🧙‍♂️ Infinite loop detected. Casting break spell..." ;;
                "permission") echo "🧙‍♂️ Administrative privileges required for this operation..." ;;
                *) echo "🧙‍♂️ Arcane error encountered. Consulting the master texts..." ;;
            esac
            ;;
        *)
            case "$error_type" in
                "crash") echo "💥 System crash detected. Initiating recovery procedures..." ;;
                "loop") echo "🔄 Loop detected. Breaking infinite cycle..." ;;
                "permission") echo "🔒 Permission denied. Check access rights..." ;;
                *) echo "⚠️ Error detected. Investigating issue..." ;;
            esac
            ;;
    esac
}

# Enhanced error logging
log_error() {
    local error_id="$1"
    local error_type="$2"
    local error_code="$3"
    local line_number="$4"
    local command="$5"
    local stack_trace="$6"
    local role="${UDOS_CURRENT_ROLE:-wizard}"

    local timestamp=$(date '+%Y-%m-%d %H:%M:%S')
    local log_file="$UDOS_ERROR_LOG_DIR/error-$(date +%Y%m%d).log"

    # Create detailed error entry
    cat >> "$log_file" << EOF
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
ERROR: $error_id
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Timestamp: $timestamp
Type: $error_type
Code: $error_code
Line: $line_number
Command: $command
Role: $role
Stack: $stack_trace
Process: $$
PWD: $(pwd)
User: $(whoami)
System: $(uname -s) $(uname -r)
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

EOF

    # Role-specific error handling
    case "$role" in
        "wizard")
            # Enhanced logging for wizard mode
            cat >> "$UDOS_DEBUG_LOG_DIR/wizard-debug-$(date +%Y%m%d).log" << EOF
[DEBUG $timestamp] Error $error_id in wizard mode
Command: $command (line $line_number)
Stack trace: $stack_trace
Environment variables:
$(env | grep UDOS_ | sort)
Active processes:
$(ps aux | grep -E "(udos|uSERVER)" | grep -v grep)
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

EOF
            ;;
    esac
}

# Loop detection system
detect_loop() {
    local process_name="$1"
    local current_count

    if [[ -f "$UDOS_LOOP_DETECTION_FILE" ]]; then
        current_count=$(cat "$UDOS_LOOP_DETECTION_FILE")
    else
        current_count=0
    fi

    # Increment counter
    ((current_count++))
    echo "$current_count" > "$UDOS_LOOP_DETECTION_FILE"

    # Check if threshold exceeded
    if [[ $current_count -gt $UDOS_LOOP_THRESHOLD ]]; then
        local error_id=$(generate_error_id)
        local role_message=$(get_role_error_message "loop")

        echo -e "${RED}$role_message${NC}"
        echo -e "${YELLOW}Loop detection: $process_name has restarted $current_count times${NC}"

        log_error "$error_id" "LOOP" "999" "0" "$process_name" "Loop threshold exceeded: $current_count > $UDOS_LOOP_THRESHOLD"

        # Reset counter and apply progressive backoff
        echo "0" > "$UDOS_LOOP_DETECTION_FILE"

        # Progressive delays to break loops
        local delay=$((current_count * 2))
        if [[ $delay -gt 30 ]]; then
            delay=30
        fi

        echo -e "${BLUE}Applying $delay second recovery delay...${NC}"
        sleep "$delay"

        return 1
    fi

    return 0
}

# Reset loop detection (call on successful startup)
reset_loop_detection() {
    echo "0" > "$UDOS_LOOP_DETECTION_FILE"
}

# Crash detection and recovery
detect_crash() {
    local process_name="$1"
    local expected_pid_file="$2"

    if [[ -f "$expected_pid_file" ]]; then
        local pid=$(cat "$expected_pid_file")

        if ! kill -0 "$pid" 2>/dev/null; then
            local error_id=$(generate_error_id)
            local role_message=$(get_role_error_message "crash")

            echo -e "${RED}$role_message${NC}"
            echo -e "${YELLOW}Crash detected: $process_name (PID: $pid) is no longer running${NC}"

            # Log crash details
            local crash_log="$UDOS_CRASH_LOG_DIR/crash-$(date +%Y%m%d%H%M%S).log"
            cat > "$crash_log" << EOF
CRASH REPORT: $error_id
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Process: $process_name
PID: $pid
PID File: $expected_pid_file
Timestamp: $(date)
Role: ${UDOS_CURRENT_ROLE:-unknown}

System State:
$(ps aux | grep -E "(udos|uSERVER)" | grep -v grep)

Recent Logs:
$(tail -20 "$UDOS_ERROR_LOG_DIR/error-$(date +%Y%m%d).log" 2>/dev/null || echo "No recent error logs")
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
EOF

            log_error "$error_id" "CRASH" "1" "0" "$process_name" "Process crashed unexpectedly"

            # Clean up stale PID file
            rm -f "$expected_pid_file"

            return 1
        fi
    fi

    return 0
}

# Handle errors with enhanced reporting
handle_error() {
    local exit_code="$1"
    local line_number="$2"
    local command="$3"

    local error_id=$(generate_error_id)
    local stack_trace=$(caller 0)
    local role_message=$(get_role_error_message "error")

    echo -e "${RED}$role_message${NC}"
    echo -e "${YELLOW}Error ID: $error_id${NC}"
    echo -e "${YELLOW}Exit Code: $exit_code${NC}"
    echo -e "${YELLOW}Line: $line_number${NC}"
    echo -e "${YELLOW}Command: $command${NC}"

    log_error "$error_id" "ERROR" "$exit_code" "$line_number" "$command" "$stack_trace"

    # Check if this is a critical error
    if [[ $exit_code -gt 100 ]]; then
        echo -e "${RED}Critical error detected. Initiating emergency shutdown...${NC}"
        emergency_shutdown
    fi
}

# Handle clean exit
handle_exit() {
    if [[ "${UDOS_DEV_MODE:-false}" == "true" ]]; then
        echo -e "${CYAN}Clean exit detected in dev mode${NC}"
        log_debug "CLEAN_EXIT" "Process exiting cleanly"
    fi
}

# Handle signals
handle_signal() {
    local signal="$1"
    local error_id=$(generate_error_id)
    local role_message=$(get_role_error_message "signal")

    echo -e "${YELLOW}$role_message${NC}"
    echo -e "${YELLOW}Signal received: $signal${NC}"

    log_error "$error_id" "SIGNAL" "0" "0" "Signal: $signal" "$(caller 0)"

    case "$signal" in
        "SIGINT")
            echo -e "${CYAN}Graceful shutdown requested...${NC}"
            cleanup_and_exit 0
            ;;
        "SIGTERM")
            echo -e "${CYAN}Termination requested...${NC}"
            cleanup_and_exit 0
            ;;
    esac
}

# Emergency shutdown procedure
emergency_shutdown() {
    local role_message=$(get_role_error_message "emergency")

    echo -e "${RED}$role_message${NC}"
    echo -e "${RED}EMERGENCY SHUTDOWN INITIATED${NC}"

    # Kill all uDOS processes
    pkill -f "uSERVER" 2>/dev/null || true
    pkill -f "start-udos" 2>/dev/null || true

    # Clean up lock files
    rm -f /tmp/udos-*.pid /tmp/udos-*.lock

    # Log emergency shutdown
    local error_id=$(generate_error_id)
    log_error "$error_id" "EMERGENCY" "999" "0" "Emergency shutdown" "System-wide emergency shutdown"

    exit 1
}

# Debug logging for dev mode
log_debug() {
    local debug_type="$1"
    local message="$2"

    if [[ "${UDOS_DEV_MODE:-false}" == "true" ]]; then
        local timestamp=$(date '+%Y-%m-%d %H:%M:%S')
        local debug_log="$UDOS_DEBUG_LOG_DIR/debug-$(date +%Y%m%d).log"

        echo "[$timestamp] $debug_type: $message" >> "$debug_log"
    fi
}

# Cleanup and exit
cleanup_and_exit() {
    local exit_code="${1:-0}"

    # Clean up temporary files
    rm -f "$UDOS_LOOP_DETECTION_FILE"

    # Log clean exit
    if [[ "${UDOS_DEV_MODE:-false}" == "true" ]]; then
        log_debug "CLEANUP" "Process exiting with code: $exit_code"
    fi

    exit "$exit_code"
}

# Process monitoring function
monitor_process() {
    local process_name="$1"
    local pid_file="$2"
    local restart_command="$3"

    while true; do
        # Check for crashes
        if detect_crash "$process_name" "$pid_file"; then
            echo -e "${GREEN}$process_name is running normally${NC}"
        else
            echo -e "${YELLOW}$process_name crashed, attempting restart...${NC}"

            # Check for loops before restarting
            if detect_loop "$process_name"; then
                echo -e "${BLUE}Restarting $process_name...${NC}"
                eval "$restart_command"
            else
                echo -e "${RED}Loop threshold exceeded for $process_name${NC}"
                emergency_shutdown
            fi
        fi

        sleep 10
    done
}

# Show error summary for wizard mode
show_error_summary() {
    if [[ "${UDOS_CURRENT_ROLE:-}" == "wizard" && "${UDOS_DEV_MODE:-false}" == "true" ]]; then
        echo -e "${WHITE}🧙‍♂️ Error Summary for $(date +%Y-%m-%d)${NC}"
        echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"

        local error_log="$UDOS_ERROR_LOG_DIR/error-$(date +%Y%m%d).log"
        if [[ -f "$error_log" ]]; then
            local error_count=$(grep -c "ERROR:" "$error_log" 2>/dev/null || echo "0")
            local crash_count=$(grep -c "CRASH" "$error_log" 2>/dev/null || echo "0")
            local loop_count=$(grep -c "LOOP" "$error_log" 2>/dev/null || echo "0")

            echo -e "${WHITE}Errors: ${error_count}${NC}"
            echo -e "${WHITE}Crashes: ${crash_count}${NC}"
            echo -e "${WHITE}Loops: ${loop_count}${NC}"

            if [[ $error_count -gt 0 ]]; then
                echo -e "${YELLOW}Recent errors:${NC}"
                tail -5 "$error_log" | grep "ERROR:" | cut -d' ' -f2-
            fi
        else
            echo -e "${GREEN}No errors logged today${NC}"
        fi

        echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
    fi
}

# Export functions for use by other scripts
export -f init_error_logging
export -f generate_error_id
export -f get_role_error_message
export -f log_error
export -f detect_loop
export -f reset_loop_detection
export -f detect_crash
export -f handle_error
export -f handle_exit
export -f handle_signal
export -f emergency_shutdown
export -f log_debug
export -f cleanup_and_exit
export -f monitor_process
export -f show_error_summary

# Initialize if called directly
if [[ "${BASH_SOURCE[0]}" == "${0}" ]]; then
    init_error_logging
    echo -e "${GREEN}✅ uDOS Error Handler v1.3.1 initialized${NC}"
    show_error_summary
fi
