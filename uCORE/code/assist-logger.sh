#!/bin/bash

# uDOS Assist Mode Logger v1.3.3
# Integrates AI-driven logging with uMEMORY and uCORE
# Location: /Users/agentdigital/uDOS/uCORE/code/assist-logger.sh

set -euo pipefail

# Configuration
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
UDOS_ROOT="$(dirname "$(dirname "$SCRIPT_DIR")")"
UMEMORY_DIR="$UDOS_ROOT/uMEMORY"
CURRENT_ROLE_CONF="$UDOS_ROOT/sandbox/current-role.conf"

# Assist Mode detection
ASSIST_MODE_FILE="$UDOS_ROOT/dev/.assist-mode"
MODE="COMMAND"  # Default mode (IO)

# Get current role
get_current_role() {
    if [[ -f "$CURRENT_ROLE_CONF" ]]; then
        grep "CURRENT_ROLE=" "$CURRENT_ROLE_CONF" | cut -d'=' -f2 | tr -d '"'
    else
        echo "wizard"
    fi
}

CURRENT_ROLE=$(get_current_role)

# Mode detection
detect_mode() {
    if [[ -f "$ASSIST_MODE_FILE" ]]; then
        MODE="ASSIST"
    else
        MODE="COMMAND"
    fi
}

# Enhanced logging with context awareness
log_with_context() {
    local level="$1"
    local component="$2"
    local message="$3"
    local context="${4:-}"

    detect_mode

    local timestamp=$(date '+%Y-%m-%d %H:%M:%S')
    local role_log_dir=""

    # Determine log directory based on level
    case "$level" in
        "ERROR")
            role_log_dir="$UMEMORY_DIR/log/errors/$CURRENT_ROLE"
            ;;
        "DEBUG")
            role_log_dir="$UMEMORY_DIR/log/debug/$CURRENT_ROLE"
            ;;
        "MISSION")
            role_log_dir="$UMEMORY_DIR/log/missions/$CURRENT_ROLE"
            ;;
        "MILESTONE")
            role_log_dir="$UMEMORY_DIR/log/milestones/$CURRENT_ROLE"
            ;;
        "MOVE")
            role_log_dir="$UMEMORY_DIR/log/moves/$CURRENT_ROLE"
            ;;
        *)
            role_log_dir="$UMEMORY_DIR/log/daily/$CURRENT_ROLE"
            ;;
    esac

    mkdir -p "$role_log_dir"

    # Enhanced log format with mode and context
    local log_file="$role_log_dir/$(echo "$component" | tr '[:upper:]' '[:lower:]')-$(date '+%Y%m%d').log"
    local mode_indicator="[CMD]"

    if [[ "$MODE" == "ASSIST" ]]; then
        mode_indicator="[AI]"
    fi

    # Create structured log entry
    local log_entry="[$timestamp] [$level] $mode_indicator [$component] $message"

    if [[ -n "$context" ]]; then
        log_entry="$log_entry | Context: $context"
    fi

    echo "$log_entry" >> "$log_file"

    # If in Assist Mode, also analyze and suggest
    if [[ "$MODE" == "ASSIST" && "$level" != "DEBUG" ]]; then
        analyze_log_entry "$level" "$component" "$message" "$context"
    fi
}

# AI-style log analysis and suggestions
analyze_log_entry() {
    local level="$1"
    local component="$2"
    local message="$3"
    local context="$4"

    local suggestions_file="$UMEMORY_DIR/log/daily/$CURRENT_ROLE/ai-suggestions-$(date '+%Y%m%d').log"
    local timestamp=$(date '+%Y-%m-%d %H:%M:%S')

    # Generate contextual suggestions based on log patterns
    local suggestion=""

    case "$level" in
        "ERROR")
            suggestion="🔍 Consider reviewing error patterns and implementing preventive measures"
            ;;
        "MISSION")
            suggestion="🎯 Track mission progress and consider milestone creation"
            ;;
        "MILESTONE")
            suggestion="🏆 Document milestone achievement and plan next objectives"
            ;;
        "MOVE")
            suggestion="📊 Analyze move patterns for workflow optimization"
            ;;
        *)
            suggestion="📝 Consider categorizing this activity for better tracking"
            ;;
    esac

    echo "[$timestamp] [AI-SUGGESTION] [$component] $suggestion | Original: $message" >> "$suggestions_file"
}

# Integration with uCORE commands
enhance_core_logging() {
    local command="$1"
    local result="$2"
    local execution_time="${3:-0}"

    detect_mode

    local context="Execution time: ${execution_time}ms"

    if [[ "$result" == "0" ]]; then
        log_with_context "INFO" "uCORE" "Command executed successfully: $command" "$context"
    else
        log_with_context "ERROR" "uCORE" "Command failed: $command (exit code: $result)" "$context"
    fi

    # If in Assist Mode, provide command optimization suggestions
    if [[ "$MODE" == "ASSIST" ]]; then
        suggest_command_optimization "$command" "$result" "$execution_time"
    fi
}

# Command optimization suggestions
suggest_command_optimization() {
    local command="$1"
    local result="$2"
    local execution_time="$3"

    local optimization_file="$UMEMORY_DIR/log/daily/$CURRENT_ROLE/command-optimization-$(date '+%Y%m%d').log"
    local timestamp=$(date '+%Y-%m-%d %H:%M:%S')

    local suggestion=""

    # Time-based suggestions
    if [[ "$execution_time" -gt 5000 ]]; then
        suggestion="⚡ Consider optimizing slow command: $command (${execution_time}ms)"
    elif [[ "$result" != "0" ]]; then
        suggestion="🛠️ Review failed command for error patterns: $command"
    elif [[ "$command" == *"backup"* ]]; then
        suggestion="💾 Consider scheduling regular backups instead of manual execution"
    elif [[ "$command" == *"test"* ]]; then
        suggestion="🧪 Consider automating test execution in development workflow"
    else
        suggestion="✅ Command executed efficiently: $command"
    fi

    echo "[$timestamp] [OPTIMIZATION] $suggestion" >> "$optimization_file"
}

# Main function for external integration
main() {
    case "${1:-}" in
        "log")
            log_with_context "${2:-INFO}" "${3:-SYSTEM}" "${4:-No message}" "${5:-}"
            ;;
        "enhance")
            enhance_core_logging "${2:-unknown}" "${3:-0}" "${4:-0}"
            ;;
        "mode")
            detect_mode
            echo "$MODE"
            ;;
        *)
            echo "Usage: assist-logger [log|enhance|mode]"
            echo ""
            echo "Commands:"
            echo "  log LEVEL COMPONENT MESSAGE [CONTEXT]  - Log with context awareness"
            echo "  enhance COMMAND RESULT [TIME]          - Enhance core command logging"
            echo "  mode                                   - Show current mode (ASSIST/COMMAND)"
            ;;
    esac
}

# Execute main function with all arguments
main "$@"
