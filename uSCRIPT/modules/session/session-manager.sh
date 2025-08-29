#!/bin/bash

# uDOS Session Manager v1.0.5.1 
# Enhanced session management with persistent state and auto-restore

set -euo pipefail

# Get script directory and uDOS root
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
UDOS_ROOT="$(cd "$SCRIPT_DIR/../.." && pwd)"

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
PURPLE='\033[0;35m'
NC='\033[0m'

# Session configuration
SESSION_DIR="$UDOS_ROOT/sandbox/sessions"
CURRENT_SESSION_FILE="$SESSION_DIR/current.json"
SESSION_CONFIG_FILE="$SESSION_DIR/config.json"

# Create session directories
mkdir -p "$SESSION_DIR"
mkdir -p "$UDOS_ROOT/sandbox/logs"

# Get current session ID
get_current_session_id() {
    if [[ -f "$CURRENT_SESSION_FILE" ]]; then
        python3 -c "
import json
try:
    with open('$CURRENT_SESSION_FILE', 'r') as f:
        data = json.load(f)
    print(data.get('session_id', ''))
except:
    pass
" 2>/dev/null || echo ""
    else
        echo ""
    fi
}

# Generate session ID
generate_session_id() {
    local prefix="${1:-session}"
    local timestamp=$(date +%Y%m%d_%H%M%S)
    local random=$(printf "%04d" $((RANDOM % 10000)))
    echo "${prefix}_${timestamp}_${random}"
}

# Create new session
create_session() {
    local session_name="${1:-development}"
    local session_id
    session_id=$(generate_session_id "$session_name")
    
    echo -e "${BLUE}🚀 Creating new session: $session_id${NC}"
    
    # Get user info
    local user_file="$UDOS_ROOT/sandbox/user.md"
    local username="unknown"
    local user_role="GHOST"
    
    if [[ -f "$user_file" ]]; then
        username=$(grep "^\*\*Username\*\*:" "$user_file" 2>/dev/null | cut -d':' -f2 | tr -d ' ' || echo "unknown")
        user_role=$(grep "^\*\*Role\*\*:" "$user_file" 2>/dev/null | cut -d':' -f2 | tr -d ' ' || echo "GHOST")
    fi
    
    # Create session data
    local session_data
    session_data=$(python3 -c "
import json
from datetime import datetime
import os

session = {
    'session_id': '$session_id',
    'session_name': '$session_name',
    'created': datetime.now().isoformat(),
    'last_updated': datetime.now().isoformat(),
    'status': 'active',
    'user': {
        'username': '$username',
        'role': '$user_role',
        'level': 100 if '$user_role' == 'WIZARD' else 10
    },
    'system': {
        'udos_version': '1.0.5.1',
        'platform': os.uname().sysname,
        'working_directory': '$UDOS_ROOT',
        'pid': os.getpid()
    },
    'features': {
        'toast_manager': True,
        'simple_browser': True,
        'multi_pane_terminal': True,
        'session_management': True
    },
    'state': {
        'last_command': '',
        'command_count': 0,
        'error_count': 0,
        'toast_count': 0
    },
    'auto_restore': {
        'enabled': True,
        'restore_working_directory': True,
        'restore_environment': True,
        'restore_tmux_sessions': False
    }
}

print(json.dumps(session, indent=2))
")
    
    # Save session data
    local session_file="$SESSION_DIR/$session_id.json"
    echo "$session_data" > "$session_file"
    
    # Update current session
    echo "{\"session_id\": \"$session_id\", \"updated\": \"$(date -Iseconds)\"}" > "$CURRENT_SESSION_FILE"
    
    echo -e "${GREEN}✅ Session created: $session_id${NC}"
    echo -e "${BLUE}📁 Session file: $session_file${NC}"
    
    return 0
}

# Save current session state
save_session() {
    local session_id
    session_id=$(get_current_session_id)
    
    if [[ -z "$session_id" ]]; then
        echo -e "${YELLOW}⚠️  No active session to save${NC}"
        return 1
    fi
    
    local session_file="$SESSION_DIR/$session_id.json"
    
    if [[ ! -f "$session_file" ]]; then
        echo -e "${RED}❌ Session file not found: $session_file${NC}"
        return 1
    fi
    
    echo -e "${BLUE}💾 Saving session state: $session_id${NC}"
    
    # Update session with current state
    python3 -c "
import json
from datetime import datetime
import os

try:
    with open('$session_file', 'r') as f:
        session = json.load(f)
    
    # Update state
    session['last_updated'] = datetime.now().isoformat()
    session['state']['last_command'] = os.environ.get('LAST_COMMAND', '')
    session['system']['pid'] = os.getpid()
    session['system']['working_directory'] = os.getcwd()
    
    with open('$session_file', 'w') as f:
        json.dump(session, f, indent=2)
    
    print('Session state saved successfully')
except Exception as e:
    print(f'Error saving session: {e}')
    exit(1)
"
    
    echo -e "${GREEN}✅ Session state saved${NC}"
    return 0
}

# Restore session
restore_session() {
    local session_id="${1:-}"
    
    if [[ -z "$session_id" ]]; then
        session_id=$(get_current_session_id)
    fi
    
    if [[ -z "$session_id" ]]; then
        echo -e "${YELLOW}⚠️  No session specified or active${NC}"
        return 1
    fi
    
    local session_file="$SESSION_DIR/$session_id.json"
    
    if [[ ! -f "$session_file" ]]; then
        echo -e "${RED}❌ Session file not found: $session_file${NC}"
        return 1
    fi
    
    echo -e "${BLUE}🔄 Restoring session: $session_id${NC}"
    
    # Parse session data and restore
    python3 -c "
import json
import os

try:
    with open('$session_file', 'r') as f:
        session = json.load(f)
    
    print(f\"Session: {session['session_name']} ({session['session_id']})\")
    print(f\"Created: {session['created']}\")
    print(f\"User: {session['user']['username']} ({session['user']['role']})\")
    
    # Restore working directory if enabled
    if session.get('auto_restore', {}).get('restore_working_directory', False):
        wd = session['system']['working_directory']
        print(f\"Restoring working directory: {wd}\")
        os.chdir(wd)
    
    # Set current session
    with open('$CURRENT_SESSION_FILE', 'w') as f:
        json.dump({'session_id': session['session_id'], 'updated': session['last_updated']}, f)
    
    print('Session restored successfully')
    
except Exception as e:
    print(f'Error restoring session: {e}')
    exit(1)
"
    
    echo -e "${GREEN}✅ Session restored${NC}"
    return 0
}

# List sessions
list_sessions() {
    echo "📋 uDOS Sessions"
    echo "─────────────────────────────────────────────────────────────────"
    
    if [[ ! -d "$SESSION_DIR" ]] || [[ -z "$(ls -A "$SESSION_DIR"/*.json 2>/dev/null || true)" ]]; then
        echo -e "${YELLOW}No sessions found${NC}"
        return 0
    fi
    
    local current_session
    current_session=$(get_current_session_id)
    
    printf "%-20s %-15s %-10s %-12s %s\n" "SESSION ID" "NAME" "STATUS" "USER" "CREATED"
    printf "%-20s %-15s %-10s %-12s %s\n" "$(printf '%*s' 20 '' | tr ' ' '-')" "$(printf '%*s' 15 '' | tr ' ' '-')" "$(printf '%*s' 10 '' | tr ' ' '-')" "$(printf '%*s' 12 '' | tr ' ' '-')" "$(printf '%*s' 19 '' | tr ' ' '-')"
    
    for session_file in "$SESSION_DIR"/*.json; do
        [[ -f "$session_file" ]] || continue
        [[ "$(basename "$session_file")" != "current.json" ]] || continue
        [[ "$(basename "$session_file")" != "config.json" ]] || continue
        
        python3 -c "
import json
from datetime import datetime

try:
    with open('$session_file', 'r') as f:
        session = json.load(f)
    
    session_id = session['session_id']
    name = session['session_name'][:14]
    status = session.get('status', 'unknown')[:9]
    user = session['user']['username'][:11]
    created = session['created'][:19].replace('T', ' ')
    
    # Mark current session
    if session_id == '$current_session':
        status = status + '*'
    
    print(f'{session_id:<20} {name:<15} {status:<10} {user:<12} {created}')
    
except Exception as e:
    print(f'Error reading session file: {e}')
" 2>/dev/null || echo "Error reading $(basename "$session_file")"
    done
    
    echo ""
    if [[ -n "$current_session" ]]; then
        echo -e "${GREEN}Current session: $current_session${NC} (marked with *)"
    else
        echo -e "${YELLOW}No active session${NC}"
    fi
}

# Show session info
show_session_info() {
    local session_id="${1:-}"
    
    if [[ -z "$session_id" ]]; then
        session_id=$(get_current_session_id)
    fi
    
    if [[ -z "$session_id" ]]; then
        echo -e "${YELLOW}⚠️  No session specified or active${NC}"
        return 1
    fi
    
    local session_file="$SESSION_DIR/$session_id.json"
    
    if [[ ! -f "$session_file" ]]; then
        echo -e "${RED}❌ Session file not found: $session_file${NC}"
        return 1
    fi
    
    echo "📊 Session Information: $session_id"
    echo "═══════════════════════════════════════════════════════════════════"
    
    python3 -c "
import json
from datetime import datetime

try:
    with open('$session_file', 'r') as f:
        session = json.load(f)
    
    print(f\"Session ID: {session['session_id']}\")
    print(f\"Name: {session['session_name']}\")
    print(f\"Status: {session.get('status', 'unknown')}\")
    print(f\"Created: {session['created']}\")
    print(f\"Last Updated: {session['last_updated']}\")
    print()
    
    print(\"User Information:\")
    user = session['user']
    print(f\"  Username: {user['username']}\")
    print(f\"  Role: {user['role']}\")
    print(f\"  Level: {user['level']}\")
    print()
    
    print(\"System Information:\")
    sys = session['system']
    print(f\"  uDOS Version: {sys['udos_version']}\")
    print(f\"  Platform: {sys['platform']}\")
    print(f\"  Working Directory: {sys['working_directory']}\")
    print(f\"  Process ID: {sys['pid']}\")
    print()
    
    print(\"Features:\")
    features = session['features']
    for feature, enabled in features.items():
        status = '✅' if enabled else '❌'
        print(f\"  {feature.replace('_', ' ').title()}: {status}\")
    print()
    
    print(\"Session State:\")
    state = session['state']
    print(f\"  Last Command: {state.get('last_command', 'none')}\")
    print(f\"  Command Count: {state.get('command_count', 0)}\")
    print(f\"  Error Count: {state.get('error_count', 0)}\")
    print(f\"  Toast Count: {state.get('toast_count', 0)}\")
    print()
    
    print(\"Auto-Restore Settings:\")
    auto_restore = session.get('auto_restore', {})
    print(f\"  Enabled: {'✅' if auto_restore.get('enabled', False) else '❌'}\")
    print(f\"  Restore Working Directory: {'✅' if auto_restore.get('restore_working_directory', False) else '❌'}\")
    print(f\"  Restore Environment: {'✅' if auto_restore.get('restore_environment', False) else '❌'}\")
    print(f\"  Restore tmux Sessions: {'✅' if auto_restore.get('restore_tmux_sessions', False) else '❌'}\")
    
except Exception as e:
    print(f'Error reading session: {e}')
    exit(1)
"
    
    return 0
}

# Show status
show_status() {
    echo "🎯 uDOS Session Manager v1.0.5.1"
    echo "═══════════════════════════════════════════════════════════════════"
    
    local current_session
    current_session=$(get_current_session_id)
    
    if [[ -n "$current_session" ]]; then
        echo -e "${GREEN}Active Session: $current_session${NC}"
        show_session_info "$current_session"
    else
        echo -e "${YELLOW}No active session${NC}"
        echo ""
        echo "📋 Available Sessions:"
        list_sessions
    fi
}

# Auto-save session (called periodically)
auto_save() {
    local session_id
    session_id=$(get_current_session_id)
    
    if [[ -n "$session_id" ]]; then
        save_session >/dev/null 2>&1 || true
    fi
}

# Show help
show_help() {
    echo "uDOS Session Manager v1.0.5.1"
    echo ""
    echo "Usage: $0 [command] [args]"
    echo ""
    echo "Commands:"
    echo "  create [name]    - Create new session (default: development)"
    echo "  save             - Save current session state"
    echo "  restore [id]     - Restore session (default: current)"
    echo "  list             - List all sessions"
    echo "  info [id]        - Show session information (default: current)"
    echo "  status           - Show session manager status"
    echo "  auto-save        - Auto-save current session (used by monitors)"
    echo "  help             - Show this help"
    echo ""
    echo "Session Features:"
    echo "  • Persistent state tracking"
    echo "  • User and system information"
    echo "  • Auto-restore functionality"
    echo "  • Integration with uDOS features"
    echo "  • JSON-based storage"
    echo ""
    echo "Session Directory: $SESSION_DIR"
    echo "Current Session: $(get_current_session_id || echo 'none')"
}

# Main command handling
main() {
    case "${1:-status}" in
        "create")
            create_session "${2:-development}"
            ;;
        "save")
            save_session
            ;;
        "restore")
            restore_session "${2:-}"
            ;;
        "list")
            list_sessions
            ;;
        "info")
            show_session_info "${2:-}"
            ;;
        "status")
            show_status
            ;;
        "auto-save")
            auto_save
            ;;
        "help"|"-h"|"--help")
            show_help
            ;;
        *)
            echo "❌ Unknown command: $1"
            show_help
            exit 1
            ;;
    esac
}

main "$@"

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
