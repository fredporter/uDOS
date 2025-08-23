#!/bin/bash
# user-move-logger.sh - User Move Logging System
# Integrates with uCORE move logging to provide user-accessible move tracking

# Configuration
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
UDOS_ROOT="$(cd "$SCRIPT_DIR/../../.." && pwd)"
UMEMORY_DIR="$UDOS_ROOT/uMEMORY"
USER_MOVES_DIR="$UMEMORY_DIR/user/moves"

# Core system logs
SESSION_MOVES_LOG="$UMEMORY_DIR/system/session-moves.json"
DAILY_MOVES_LOG="$UMEMORY_DIR/system/daily-moves-$(date +%Y%m%d).json"

# Generate uHEX code for session files
generate_uhex() {
    openssl rand -hex 4 | tr '[:lower:]' '[:upper:]' 2>/dev/null || printf "%08X" $((RANDOM * RANDOM))
}

# User logs
USER_SESSION_LOG="$USER_MOVES_DIR/uLOG-$(generate_uhex)-session-$(date +%Y%m%d).md"
USER_DAILY_SUMMARY="$USER_MOVES_DIR/uLOG-$(date +%Y%m%d)-daily-summary.md"
USER_MOVE_PATTERNS="$USER_MOVES_DIR/uDATA-$(date +%Y%m%d)-move-patterns.json"

# Colors
CYAN='\033[0;36m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m'

# Ensure directories exist
mkdir -p "$USER_MOVES_DIR"

# Initialize user move logging
init_user_move_logging() {
    echo -e "${CYAN}[USER-MOVES]${NC} Initializing user move logging system"
    
    # Create user session log if it doesn't exist
    if [[ ! -f "$USER_SESSION_LOG" ]]; then
        cat > "$USER_SESSION_LOG" << EOF
# User Move Log - $(date +%Y-%m-%d)

## Session Information
- **Date**: $(date)
- **Session ID**: USER_$(date +%Y%m%d_%H%M%S)_$$
- **User**: $(whoami)

## Moves

EOF
    fi
    
    # Initialize move patterns tracking
    if [[ ! -f "$USER_MOVE_PATTERNS" ]]; then
        cat > "$USER_MOVE_PATTERNS" << EOF
{
    "initialized": "$(date -u +%Y-%m-%dT%H:%M:%SZ)",
    "patterns": {
        "frequent_moves": {},
        "move_sequences": [],
        "time_patterns": {},
        "session_stats": {
            "total_sessions": 0,
            "total_moves": 0,
            "average_moves_per_session": 0
        }
    }
}
EOF
    fi
    
    echo -e "${GREEN}[USER-MOVES]${NC} User move logging initialized"
}

# Log a user move
log_user_move() {
    local move_type="$1"
    local description="$2"
    local location="${3:-unknown}"
    local context="${4:-}"
    
    local timestamp=$(date)
    local time_short=$(date +%H:%M:%S)
    
    # Log to user session file
    cat >> "$USER_SESSION_LOG" << EOF
### $time_short - $move_type
- **Description**: $description
- **Location**: $location
- **Context**: $context
- **Timestamp**: $timestamp

EOF
    
    # Update move patterns
    update_move_patterns "$move_type" "$location"
    
    echo -e "${CYAN}[USER-MOVES]${NC} Logged: $move_type - $description"
}

# Update move patterns analysis
update_move_patterns() {
    local move_type="$1"
    local location="$2"
    
    # Check if jq is available for JSON processing
    if command -v jq >/dev/null 2>&1 && [[ -f "$USER_MOVE_PATTERNS" ]]; then
        local temp_file=$(mktemp)
        
        jq --arg type "$move_type" \
           --arg loc "$location" \
           --arg ts "$(date -u +%Y-%m-%dT%H:%M:%SZ)" \
           '
           .patterns.frequent_moves[$type] = (.patterns.frequent_moves[$type] // 0) + 1 |
           .patterns.frequent_moves[$loc] = (.patterns.frequent_moves[$loc] // 0) + 1 |
           .patterns.session_stats.total_moves += 1 |
           .last_updated = $ts
           ' \
           "$USER_MOVE_PATTERNS" > "$temp_file" && mv "$temp_file" "$USER_MOVE_PATTERNS"
    fi
}

# Generate daily summary
generate_daily_summary() {
    echo -e "${CYAN}[USER-MOVES]${NC} Generating daily summary"
    
    local today=$(date +%Y-%m-%d)
    local move_count=0
    
    # Count moves from session log
    if [[ -f "$USER_SESSION_LOG" ]]; then
        move_count=$(grep -c "^### " "$USER_SESSION_LOG" 2>/dev/null || echo 0)
    fi
    
    cat > "$USER_DAILY_SUMMARY" << EOF
# Daily Move Summary - $today

## Overview
- **Date**: $today
- **Total Moves**: $move_count
- **Session Duration**: $(date +%H:%M:%S)
- **User**: $(whoami)

## Move Breakdown

EOF
    
    # Extract move types and counts
    if [[ -f "$USER_SESSION_LOG" ]]; then
        echo "### Move Types" >> "$USER_DAILY_SUMMARY"
        grep "^### " "$USER_SESSION_LOG" | sed 's/^### [0-9:]*[[:space:]]*-[[:space:]]*//' | sort | uniq -c | while read count type; do
            echo "- **$type**: $count times" >> "$USER_DAILY_SUMMARY"
        done
        
        echo "" >> "$USER_DAILY_SUMMARY"
        echo "### Recent Moves" >> "$USER_DAILY_SUMMARY"
        tail -n 20 "$USER_SESSION_LOG" >> "$USER_DAILY_SUMMARY"
    fi
    
    echo -e "${GREEN}[USER-MOVES]${NC} Daily summary created: $USER_DAILY_SUMMARY"
}

# Display user move statistics
show_user_stats() {
    echo -e "${CYAN}[USER-MOVES]${NC} User Move Statistics"
    echo "=================================="
    
    local today_moves=0
    if [[ -f "$USER_SESSION_LOG" ]]; then
        today_moves=$(grep -c "^### " "$USER_SESSION_LOG" 2>/dev/null || echo 0)
    fi
    
    echo "Today's Moves: $today_moves"
    echo "Session Log: $USER_SESSION_LOG"
    echo "Daily Summary: $USER_DAILY_SUMMARY"
    echo "Move Patterns: $USER_MOVE_PATTERNS"
    
    # Show recent moves
    if [[ -f "$USER_SESSION_LOG" && $today_moves -gt 0 ]]; then
        echo ""
        echo "Recent Moves:"
        grep "^### " "$USER_SESSION_LOG" | tail -5 | while read line; do
            echo "  $line"
        done
    fi
}

# Sync with core system logs
sync_with_core_logs() {
    echo -e "${CYAN}[USER-MOVES]${NC} Syncing with core system logs"
    
    # Check if core session log exists
    if [[ -f "$SESSION_MOVES_LOG" ]]; then
        local core_moves=$(jq -r '.moves | length' "$SESSION_MOVES_LOG" 2>/dev/null || echo 0)
        echo "Core system moves: $core_moves"
        
        # Extract recent moves from core system
        if command -v jq >/dev/null 2>&1 && [[ $core_moves -gt 0 ]]; then
            echo "" >> "$USER_SESSION_LOG"
            echo "## Core System Moves (Recent)" >> "$USER_SESSION_LOG"
            
            jq -r '.moves[-5:] | .[] | "### \(.timestamp | split("T")[1] | split(".")[0]) - \(.type)\n- **Description**: \(.description)\n- **ID**: \(.id)\n"' "$SESSION_MOVES_LOG" >> "$USER_SESSION_LOG"
        fi
    fi
    
    echo -e "${GREEN}[USER-MOVES]${NC} Sync completed"
}

# Main function
main() {
    case "${1:-help}" in
        "init")
            init_user_move_logging
            ;;
        "log")
            log_user_move "$2" "$3" "${4:-}" "${5:-}"
            ;;
        "summary")
            generate_daily_summary
            ;;
        "stats")
            show_user_stats
            ;;
        "sync")
            sync_with_core_logs
            ;;
        "help"|*)
            echo "User Move Logger v1.0"
            echo "Usage: $0 {init|log|summary|stats|sync|help}"
            echo ""
            echo "Commands:"
            echo "  init                    Initialize user move logging"
            echo "  log <type> <desc> [loc] Log a user move"
            echo "  summary                 Generate daily summary"
            echo "  stats                   Show move statistics"
            echo "  sync                    Sync with core system logs"
            echo "  help                    Show this help"
            echo ""
            echo "Examples:"
            echo "  $0 init"
            echo "  $0 log navigation 'Opened sandbox' 'sandbox/'"
            echo "  $0 log creation 'Created new file' 'uSCRIPT/'"
            echo "  $0 summary"
            ;;
    esac
}

# Run main function
main "$@"
