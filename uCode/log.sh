#!/bin/bash
# uDOS Logging System v1.0.0
# Handles system logging for moves, commands, and events

set -euo pipefail

UHOME="${HOME}/uDOS"
LOG_DIR="$UHOME/uMemory/logs"
MOVE_LOG="$LOG_DIR/move-log-$(date +%Y-%m-%d).md"

# Create logs directory if it doesn't exist
mkdir -p "$LOG_DIR"

# Color helpers
red() { echo -e "\033[0;31m$1\033[0m"; }
green() { echo -e "\033[0;32m$1\033[0m"; }
yellow() { echo -e "\033[0;33m$1\033[0m"; }
blue() { echo -e "\033[0;34m$1\033[0m"; }

# Log a move/command
log_move() {
    local command="$1"
    local timestamp=$(date '+%H:%M:%S')
    local date_header=$(date '+# %Y-%m-%d - uDOS Move Log')
    
    # Create or update daily log file
    if [[ ! -f "$MOVE_LOG" ]]; then
        echo "$date_header" > "$MOVE_LOG"
        echo "" >> "$MOVE_LOG"
    fi
    
    # Log the move
    echo "- **$timestamp**: \`$command\`" >> "$MOVE_LOG"
}

# Log a system event
log_event() {
    local event="$1"
    local level="${2:-INFO}"
    local system_log="$LOG_DIR/system-$(date +%Y-%m).md"
    local timestamp=$(date '+%Y-%m-%d %H:%M:%S')
    
    # Create monthly system log if it doesn't exist
    if [[ ! -f "$system_log" ]]; then
        echo "# uDOS System Log - $(date '+%B %Y')" > "$system_log"
        echo "" >> "$system_log"
    fi
    
    # Log the event
    echo "- **$timestamp** [$level]: $event" >> "$system_log"
}

# Log user activity
log_activity() {
    local activity="$1"
    local activity_log="$LOG_DIR/activity-$(date +%Y-%m-%d).md"
    local timestamp=$(date '+%H:%M:%S')
    
    # Create daily activity log if it doesn't exist
    if [[ ! -f "$activity_log" ]]; then
        echo "# uDOS Activity Log - $(date '+%A, %B %d, %Y')" > "$activity_log"
        echo "" >> "$activity_log"
    fi
    
    # Log the activity
    echo "- **$timestamp**: $activity" >> "$activity_log"
}

# Show recent logs
show_recent() {
    local log_type="${1:-move}"
    local count="${2:-10}"
    
    case "$log_type" in
        "move"|"moves")
            if [[ -f "$MOVE_LOG" ]]; then
                blue "📝 Recent Moves (Last $count):"
                tail -n "$count" "$MOVE_LOG" | grep "^-" | head -n "$count"
            else
                yellow "⚠️ No move log found for today"
            fi
            ;;
        "event"|"events")
            local system_log="$LOG_DIR/system-$(date +%Y-%m).md"
            if [[ -f "$system_log" ]]; then
                blue "📋 Recent Events (Last $count):"
                tail -n "$count" "$system_log" | grep "^-" | head -n "$count"
            else
                yellow "⚠️ No system log found for this month"
            fi
            ;;
        "activity")
            local activity_log="$LOG_DIR/activity-$(date +%Y-%m-%d).md"
            if [[ -f "$activity_log" ]]; then
                blue "🎯 Recent Activity (Last $count):"
                tail -n "$count" "$activity_log" | grep "^-" | head -n "$count"
            else
                yellow "⚠️ No activity log found for today"
            fi
            ;;
        *)
            red "❌ Unknown log type: $log_type"
            echo "Available types: move, event, activity"
            exit 1
            ;;
    esac
}

# Main function
main() {
    local action="${1:-help}"
    local content="${2:-}"
    local extra="${3:-}"
    
    case "$action" in
        "move")
            if [[ -z "$content" ]]; then
                red "❌ Move content required"
                echo "Usage: $0 move '<command>'"
                exit 1
            fi
            log_move "$content"
            ;;
        "event")
            if [[ -z "$content" ]]; then
                red "❌ Event content required"
                echo "Usage: $0 event '<event>' [level]"
                exit 1
            fi
            log_event "$content" "${extra:-INFO}"
            ;;
        "activity")
            if [[ -z "$content" ]]; then
                red "❌ Activity content required"
                echo "Usage: $0 activity '<activity>'"
                exit 1
            fi
            log_activity "$content"
            ;;
        "show"|"recent")
            show_recent "${content:-move}" "${extra:-10}"
            ;;
        "help"|"--help"|"-h")
            echo "🗒️ uDOS Logging System v1.0.0"
            echo ""
            echo "Usage: $0 <action> [content] [extra]"
            echo ""
            echo "Actions:"
            echo "  move <command>        - Log a command/move"
            echo "  event <event> [level] - Log a system event (INFO/WARN/ERROR)"
            echo "  activity <activity>   - Log user activity"
            echo "  show <type> [count]   - Show recent logs (move/event/activity)"
            echo "  help                  - Show this help"
            echo ""
            echo "Examples:"
            echo "  $0 move 'user typed: hello world'"
            echo "  $0 event 'User login' INFO"
            echo "  $0 activity 'Created new mission'"
            echo "  $0 show move 5"
            echo ""
            ;;
        *)
            red "❌ Unknown action: $action"
            echo "Use '$0 help' for usage information"
            exit 1
            ;;
    esac
}

# Run if called directly
if [[ "${BASH_SOURCE[0]}" == "${0}" ]]; then
    main "$@"
fi
