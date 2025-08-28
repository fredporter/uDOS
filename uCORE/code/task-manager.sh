#!/bin/bash
# uDOS Simple Task Manager v1.0
# Lean, fast, native bash for uCORE architecture
# Location: uCORE/code/task-manager.sh

set -euo pipefail

# Get uDOS root
UDOS_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
TASK_LOG="$UDOS_ROOT/sandbox/logs/tasks.log"

# Simple logging (uCORE native)
log_task() {
    echo "[$(date '+%Y-%m-%d %H:%M:%S')] $1" | tee -a "$TASK_LOG"
}

# Create task (minimal)
create_task() {
    local task_name="$1"
    local task_cmd="$2"
    local task_id="task_$(date +%s)"

    log_task "CREATE: $task_id - $task_name"
    echo "$task_id|$task_name|$task_cmd|created|$(date +%s)" >> "$TASK_LOG"
    echo "$task_id"
}

# Execute task (simple)
execute_task() {
    local task_id="$1"

    log_task "EXECUTE: $task_id"
    # Simple execution - just run the command
    if eval "$2" 2>&1 | tee -a "$TASK_LOG"; then
        log_task "SUCCESS: $task_id"
        return 0
    else
        log_task "FAILED: $task_id"
        return 1
    fi
}

# List tasks (minimal)
list_tasks() {
    echo "╔════════════════════════════════════╗"
    echo "║           📋 TASK LIST             ║"
    echo "╚════════════════════════════════════╝"

    if [[ -f "$TASK_LOG" ]]; then
        tail -10 "$TASK_LOG"
    else
        echo "No tasks logged yet."
    fi
}

# Clean old logs (uCORE hygiene)
clean_logs() {
    if [[ -f "$TASK_LOG" ]]; then
        # Keep last 100 lines
        tail -100 "$TASK_LOG" > "$TASK_LOG.tmp"
        mv "$TASK_LOG.tmp" "$TASK_LOG"
        log_task "CLEAN: Task log trimmed"
    fi
}

# Main function (simple command routing)
main() {
    local command="${1:-help}"

    # Ensure log directory exists
    mkdir -p "$(dirname "$TASK_LOG")"

    case "$command" in
        create)
            if [[ $# -lt 3 ]]; then
                echo "Usage: task-manager create <name> <command>"
                exit 1
            fi
            create_task "$2" "$3"
            ;;
        execute)
            if [[ $# -lt 3 ]]; then
                echo "Usage: task-manager execute <id> <command>"
                exit 1
            fi
            execute_task "$2" "$3"
            ;;
        list)
            list_tasks
            ;;
        clean)
            clean_logs
            ;;
        help|*)
            cat << 'EOF'
╔════════════════════════════════════╗
║       🔧 uDOS TASK MANAGER         ║
║         Lean & Native              ║
╠════════════════════════════════════╣
║ Commands:                          ║
║ create <name> <cmd>  - Create task ║
║ execute <id> <cmd>   - Run task    ║
║ list                 - Show tasks  ║
║ clean               - Clean logs   ║
║ help                - This help    ║
╚════════════════════════════════════╝
EOF
            ;;
    esac
}

# Execute main function
main "$@"
