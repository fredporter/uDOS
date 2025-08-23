#!/bin/bash
# session-manager.sh - Session-based development environment for /sandbox
# Handles session start/end, move logging, undo/redo, and daily compilation

set -euo pipefail

# Get script directory and uDOS root
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
UDOS_ROOT="$(cd "$SCRIPT_DIR/../.." && pwd)"

# Source logging from uCORE
source "$SCRIPT_DIR/logging.sh" 2>/dev/null || {
    log_info() { echo -e "\033[0;36m[INFO]\033[0m $1"; }
    log_success() { echo -e "\033[0;32m[SUCCESS]\033[0m $1"; }
    log_warning() { echo -e "\033[0;33m[WARNING]\033[0m $1"; }
    log_error() { echo -e "\033[0;31m[ERROR]\033[0m $1"; }
}

# Configuration
SANDBOX_DIR="$UDOS_ROOT/sandbox"
SESSION_DIR="$SANDBOX_DIR/session"
DEV_DIR="$SANDBOX_DIR/dev"
TEMP_DIR="$SANDBOX_DIR/temp"
UMEMORY_DIR="$UDOS_ROOT/uMEMORY"

# Session files
CURRENT_SESSION="$SESSION_DIR/current-session.json"
SESSION_MOVES="$SESSION_DIR/moves/current-session.json"
UNDO_STACK="$SESSION_DIR/undo-stack/undo-stack.json"
SESSION_LOG="$SESSION_DIR/logs/session-$(date +%Y%m%d_%H%M%S).log"

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
PURPLE='\033[0;35m'
CYAN='\033[0;36m'
NC='\033[0m'
BOLD='\033[1m'

# ═══════════════════════════════════════════════════════════════════════
# SESSION MANAGEMENT
# ═══════════════════════════════════════════════════════════════════════

# Start a new development session
start_session() {
    local session_id="session_$(date +%Y%m%d_%H%M%S)_$$"
    local user_role=$(get_user_role)

    # Ensure directories exist
    mkdir -p "$SESSION_DIR/logs" "$SESSION_DIR/moves" "$SESSION_DIR/undo-stack"
    mkdir -p "$DEV_DIR" "$TEMP_DIR"

    # Create session metadata
    cat > "$CURRENT_SESSION" << EOF
{
    "session_id": "$session_id",
    "user_role": "$user_role",
    "started": "$(date -u +%Y-%m-%dT%H:%M:%SZ)",
    "status": "active",
    "workspace": "$SANDBOX_DIR",
    "moves_count": 0,
    "undo_available": 0,
    "redo_available": 0,
    "dev_files": [],
    "temp_files": [],
    "last_activity": "$(date -u +%Y-%m-%dT%H:%M:%SZ)"
}
EOF

    # Initialize session moves log
    cat > "$SESSION_MOVES" << EOF
{
    "session_id": "$session_id",
    "started": "$(date -u +%Y-%m-%dT%H:%M:%SZ)",
    "moves": [],
    "current_position": 0
}
EOF

    # Initialize undo stack
    cat > "$UNDO_STACK" << EOF
{
    "session_id": "$session_id",
    "stack": [],
    "position": 0,
    "max_size": 50
}
EOF

    # Create session log
    echo "$(date '+%Y-%m-%d %H:%M:%S') [SESSION] Started session: $session_id (role: $user_role)" > "$SESSION_LOG"

    log_success "Development session started: $session_id"
    log_info "Workspace: $SANDBOX_DIR"
    log_info "Session logs: $SESSION_DIR"

    # Show session status
    show_session_status
}

# End current session and compile to daily summary
end_session() {
    if [ ! -f "$CURRENT_SESSION" ]; then
        log_warning "No active session found"
        return 1
    fi

    local session_id=$(jq -r '.session_id' "$CURRENT_SESSION")
    local start_time=$(jq -r '.started' "$CURRENT_SESSION")
    local end_time=$(date -u +%Y-%m-%dT%H:%M:%SZ)
    local moves_count=$(jq -r '.moves | length // 0' "$SESSION_MOVES" 2>/dev/null || echo "0")

    # Update session metadata
    jq --arg end_time "$end_time" --arg status "completed" --argjson moves_count "$moves_count" '
        .ended = $end_time |
        .status = $status |
        .moves_count = $moves_count |
        .duration_minutes = ((now - (.started | fromdateiso8601)) / 60 | floor)
    ' "$CURRENT_SESSION" > "$CURRENT_SESSION.tmp" && mv "$CURRENT_SESSION.tmp" "$CURRENT_SESSION"

    # Compile session summary
    compile_session_summary "$session_id"

    # Archive session files
    archive_session_files "$session_id"

    # Clean up temp files
    cleanup_temp_files

    log_success "Session ended: $session_id"
    log_info "Session summary compiled to daily log"
    log_info "Session files archived"
}

# Compile session data into daily summary
compile_session_summary() {
    local session_id="$1"
    local today=$(date +%Y%m%d)
    local daily_summary="$SESSION_DIR/logs/daily-summary-$today.json"
    local session_data=$(cat "$CURRENT_SESSION")

    # Create or update daily summary
    if [ ! -f "$daily_summary" ]; then
        cat > "$daily_summary" << EOF
{
    "date": "$today",
    "created": "$(date -u +%Y-%m-%dT%H:%M:%SZ)",
    "sessions": [],
    "total_moves": 0,
    "total_duration_minutes": 0,
    "dev_activity": {
        "files_created": 0,
        "files_modified": 0,
        "experiments_run": 0,
        "tests_executed": 0
    }
}
EOF
    fi

    # Add session to daily summary
    local session_summary=$(echo "$session_data" | jq '{
        session_id,
        started,
        ended,
        duration_minutes,
        moves_count,
        user_role,
        status
    }')

    jq --argjson session "$session_summary" '
        .sessions += [$session] |
        .total_moves += ($session.moves_count // 0) |
        .total_duration_minutes += ($session.duration_minutes // 0) |
        .last_updated = (now | strftime("%Y-%m-%dT%H:%M:%SZ"))
    ' "$daily_summary" > "$daily_summary.tmp" && mv "$daily_summary.tmp" "$daily_summary"

    log_info "Session compiled to daily summary: daily-summary-$today.json"
}

# Archive session files to uMEMORY at end of day
archive_daily_summary() {
    local today=$(date +%Y%m%d)
    local daily_summary="$SESSION_DIR/logs/daily-summary-$today.json"

    if [ -f "$daily_summary" ]; then
        # Ensure uMEMORY user directory exists
        local user_role=$(get_user_role)
        mkdir -p "$UMEMORY_DIR/user/$user_role/daily-logs"

        # Move daily summary to uMEMORY
        cp "$daily_summary" "$UMEMORY_DIR/user/$user_role/daily-logs/"
        log_success "Daily summary archived to uMEMORY: $user_role/daily-logs/"

        # Clean up old session files (keep last 3 days in sandbox)
        find "$SESSION_DIR/logs" -name "daily-summary-*.json" -mtime +3 -delete 2>/dev/null || true
        find "$SESSION_DIR/logs" -name "session-*.log" -mtime +3 -delete 2>/dev/null || true
    fi
}

# Archive individual session files
archive_session_files() {
    local session_id="$1"
    local archive_dir="$SESSION_DIR/archive/$(date +%Y%m%d)"

    mkdir -p "$archive_dir"

    # Archive session files with session ID
    if [ -f "$SESSION_MOVES" ]; then
        cp "$SESSION_MOVES" "$archive_dir/${session_id}-moves.json"
    fi

    if [ -f "$UNDO_STACK" ]; then
        cp "$UNDO_STACK" "$archive_dir/${session_id}-undo.json"
    fi

    if [ -f "$SESSION_LOG" ]; then
        cp "$SESSION_LOG" "$archive_dir/${session_id}.log"
    fi

    log_info "Session files archived to: $archive_dir"
}

# Clean up temp files
cleanup_temp_files() {
    if [ -d "$TEMP_DIR" ]; then
        # Remove files older than 1 hour
        find "$TEMP_DIR" -type f -mmin +60 -delete 2>/dev/null || true
        log_info "Cleaned up temp files older than 1 hour"
    fi
}

# ═══════════════════════════════════════════════════════════════════════
# DEVELOPMENT WORKSPACE FUNCTIONS
# ═══════════════════════════════════════════════════════════════════════

# Create new development file
create_dev_file() {
    local filename="$1"
    local template="${2:-script}"
    local dev_file="$DEV_DIR/$filename"

    case "$template" in
        script)
            cat > "$dev_file" << 'EOF'
#!/bin/bash
# Development script created in sandbox
# Edit and test here before moving to final location

set -euo pipefail

echo "Development script template"
EOF
            ;;
        experiment)
            cat > "$dev_file" << 'EOF'
#!/bin/bash
# Experiment script - testing new functionality
# Safe to modify and test

echo "Experiment: $(basename "$0")"
echo "Started: $(date)"
EOF
            ;;
        test)
            cat > "$dev_file" << 'EOF'
#!/bin/bash
# Test script for development
# Add test cases here

echo "Test: $(basename "$0")"
echo "Running tests..."
EOF
            ;;
        *)
            touch "$dev_file"
            ;;
    esac

    chmod +x "$dev_file"
    log_move "create_dev_file" "Created development file: $filename" '{"file":"'$(basename "$dev_file")'","template":"'$template'"}'
    log_success "Created development file: $dev_file"
}

# ═══════════════════════════════════════════════════════════════════════
# UTILITY FUNCTIONS
# ═══════════════════════════════════════════════════════════════════════

# Get user role
get_user_role() {
    if [ -f "$SANDBOX_DIR/user.md" ]; then
        grep "^\*\*Role\*\*:" "$SANDBOX_DIR/user.md" 2>/dev/null | sed 's/^\*\*Role\*\*: *//' | head -1
    else
        echo "ghost"
    fi
}

# Log move for undo/redo functionality
log_move() {
    local move_type="$1"
    local description="$2"
    local data="${3:-{}}"

    # Ensure session is active
    [ ! -f "$CURRENT_SESSION" ] && start_session

    local timestamp=$(date -u +%Y-%m-%dT%H:%M:%SZ)
    local move_id="move_$(date +%s)_$$"

    # Add to session moves
    if [ -f "$SESSION_MOVES" ]; then
        local temp_file=$(mktemp)
        jq --arg id "$move_id" --arg type "$move_type" --arg desc "$description" --arg ts "$timestamp" --arg data_raw "$data" '
            .moves += [{
                "id": $id,
                "type": $type,
                "description": $desc,
                "timestamp": $ts,
                "data": ($data_raw | try fromjson catch $data_raw)
            }] |
            .current_position = (.moves | length)
        ' "$SESSION_MOVES" > "$temp_file" && mv "$temp_file" "$SESSION_MOVES"
    fi

    # Update session activity
    if [ -f "$CURRENT_SESSION" ]; then
        local temp_file=$(mktemp)
        jq --arg ts "$timestamp" '.last_activity = $ts | .moves_count += 1' "$CURRENT_SESSION" > "$temp_file" && mv "$temp_file" "$CURRENT_SESSION"
    fi

    # Log to session log file
    echo "$(date '+%Y-%m-%d %H:%M:%S') [MOVE] $move_type: $description" >> "$SESSION_LOG"
}

# Show current session status
show_session_status() {
    if [ ! -f "$CURRENT_SESSION" ]; then
        echo -e "${YELLOW}No active session${NC}"
        return 1
    fi

    local session_data=$(cat "$CURRENT_SESSION")
    local session_id=$(echo "$session_data" | jq -r '.session_id')
    local user_role=$(echo "$session_data" | jq -r '.user_role')
    local started=$(echo "$session_data" | jq -r '.started')
    local moves_count=$(echo "$session_data" | jq -r '.moves_count // 0')
    local status=$(echo "$session_data" | jq -r '.status')

    echo -e "${BOLD}${CYAN}═══ SESSION STATUS ═══${NC}"
    echo -e "${BLUE}Session ID:${NC} $session_id"
    echo -e "${BLUE}User Role:${NC} $user_role"
    echo -e "${BLUE}Status:${NC} $status"
    echo -e "${BLUE}Started:${NC} $started"
    echo -e "${BLUE}Moves:${NC} $moves_count"
    echo -e "${BLUE}Workspace:${NC} $SANDBOX_DIR"

    # Show dev files
    if [ -d "$DEV_DIR" ]; then
        local dev_count=$(find "$DEV_DIR" -type f | wc -l | xargs)
        echo -e "${BLUE}Dev Files:${NC} $dev_count"
    fi

    # Show temp files
    if [ -d "$TEMP_DIR" ]; then
        local temp_count=$(find "$TEMP_DIR" -type f | wc -l | xargs)
        echo -e "${BLUE}Temp Files:${NC} $temp_count"
    fi
}

# ═══════════════════════════════════════════════════════════════════════
# COMMAND INTERFACE
# ═══════════════════════════════════════════════════════════════════════

show_help() {
    echo -e "${BOLD}${CYAN}uDOS Session Manager${NC}"
    echo "Sandbox-based development environment with session management"
    echo ""
    echo "Commands:"
    echo "  start                       - Start new development session"
    echo "  end                         - End current session and compile summary"
    echo "  status                      - Show current session status"
    echo "  create <file> [template]    - Create development file (script/experiment/test)"
    echo "  archive                     - Archive daily summaries to uMEMORY"
    echo "  cleanup                     - Clean up temp files"
    echo "  help                        - Show this help"
    echo ""
    echo "Session Management:"
    echo "  • All development work happens in /sandbox"
    echo "  • Session data tracked in /sandbox/session"
    echo "  • Daily summaries compiled at session end"
    echo "  • Final summaries archived to uMEMORY"
    echo "  • Undo/redo based on session moves"
}

main() {
    local command="${1:-help}"
    shift || true

    case "$command" in
        start)
            start_session
            ;;
        end)
            end_session
            ;;
        status)
            show_session_status
            ;;
        create)
            local filename="$1"
            local template="${2:-script}"
            if [ -z "$filename" ]; then
                log_error "Filename required"
                exit 1
            fi
            create_dev_file "$filename" "$template"
            ;;
        archive)
            archive_daily_summary
            ;;
        cleanup)
            cleanup_temp_files
            ;;
        help|--help|-h)
            show_help
            ;;
        *)
            log_error "Unknown command: $command"
            show_help
            exit 1
            ;;
    esac
}

# Auto-start session if none exists and command requires it
if [ "${1:-}" != "help" ] && [ "${1:-}" != "--help" ] && [ "${1:-}" != "-h" ] && [ "${1:-}" != "archive" ]; then
    if [ ! -f "$CURRENT_SESSION" ] && [ "${1:-}" != "start" ]; then
        log_info "No active session found, starting new session..."
        start_session
    fi
fi

# Run main function
main "$@"
