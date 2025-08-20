#!/bin/bash
# uDOS Session Module v1.3
# Session management interface for logging system

# Get uDOS paths
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
UDOS_ROOT="$(cd "$SCRIPT_DIR/../../.." && pwd)"
UCORE="$UDOS_ROOT/uCORE"
UMEMORY="$UDOS_ROOT/uMEMORY"

# Colors
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
CYAN='\033[0;36m'
NC='\033[0m'

# Source the session logger module
SESSION_LOGGER="$UCORE/code/session-logger.sh"
if [[ -f "$SESSION_LOGGER" ]]; then
    source "$SESSION_LOGGER"
else
    echo -e "${RED}Error: Session logger module not found at: $SESSION_LOGGER${NC}"
    echo "Expected location: $UCORE/code/session-logger.sh"
    exit 1
fi

show_current_session() {
    echo -e "${BLUE}📝 Current Session${NC}"
    echo ""
    
    # Generate current session info
    local session_hex=$(generate_session_hex)
    local timestamp=$(date "+%Y%m%d-%H%M%S")
    local session_id="uLOG-${timestamp}-${session_hex}-Session"
    
    echo "Session ID: $session_id"
    echo "Timestamp: $(date "+%Y-%m-%d %H:%M:%S")"
    echo "Hex Code: $session_hex"
    echo ""
    
    # Show system info
    echo -e "${CYAN}System Information:${NC}"
    get_system_info | head -10
}

list_recent_sessions() {
    echo -e "${BLUE}📚 Recent Sessions${NC}"
    echo ""
    
    # Find all session logs
    local session_logs=($(find "$UMEMORY" -name "*Session.md" -exec stat -f "%m %N" {} \; 2>/dev/null | sort -nr | head -10))
    
    if [[ ${#session_logs[@]} -eq 0 ]]; then
        echo "No session logs found"
        return 0
    fi
    
    echo "Recent session logs:"
    echo ""
    
    local count=0
    for ((i=0; i<${#session_logs[@]}; i+=2)); do
        local timestamp="${session_logs[i]}"
        local filepath="${session_logs[i+1]}"
        local filename=$(basename "$filepath")
        local session_date=$(echo "$filename" | sed 's/uLOG-//' | sed 's/-[^-]*-Session.md//' | sed 's/\([0-9]\{8\}\)-\([0-9]\{6\}\)/\1 \2/')
        
        ((count++))
        echo "[$count] $filename"
        echo "    Date: $session_date"
        echo "    Path: $filepath"
        echo ""
        
        [[ $count -ge 5 ]] && break
    done
}

view_session_log() {
    local session_id="$1"
    
    if [[ -z "$session_id" ]]; then
        echo -e "${RED}Please provide a session ID or number${NC}"
        echo "Use 'session list' to see available sessions"
        return 1
    fi
    
    # If it's a number, get the nth session
    if [[ "$session_id" =~ ^[0-9]+$ ]]; then
        local session_logs=($(find "$UMEMORY" -name "*Session.md" -exec stat -f "%m %N" {} \; 2>/dev/null | sort -nr | head -10))
        local index=$((($session_id - 1) * 2 + 1))
        
        if [[ $index -lt ${#session_logs[@]} ]]; then
            local filepath="${session_logs[index]}"
            view_session_file "$filepath"
        else
            echo -e "${RED}Session number $session_id not found${NC}"
            return 1
        fi
    else
        # Look for session by partial ID
        local found_session=$(find "$UMEMORY" -name "*${session_id}*Session.md" | head -1)
        
        if [[ -n "$found_session" ]]; then
            view_session_file "$found_session"
        else
            echo -e "${RED}Session not found: $session_id${NC}"
            return 1
        fi
    fi
}

view_session_file() {
    local filepath="$1"
    local filename=$(basename "$filepath")
    
    echo -e "${BLUE}📖 Session Log: $filename${NC}"
    echo ""
    
    if [[ -f "$filepath" ]]; then
        # Show session header
        head -20 "$filepath"
        echo ""
        echo -e "${CYAN}--- End of preview ---${NC}"
        echo ""
        echo "Full path: $filepath"
        echo "Use 'cat \"$filepath\"' to view complete log"
    else
        echo -e "${RED}Session file not found: $filepath${NC}"
    fi
}

create_new_session() {
    echo -e "${BLUE}🆕 Creating New Session Log${NC}"
    echo ""
    
    # Use the session logger to create a new session
    if create_session_log; then
        echo -e "${GREEN}New session log created successfully${NC}"
        
        # Show the latest session
        local latest_session=$(find "$UMEMORY" -name "*Session.md" -exec stat -f "%m %N" {} \; 2>/dev/null | sort -nr | head -1 | cut -d' ' -f2-)
        if [[ -n "$latest_session" ]]; then
            echo "Created: $(basename "$latest_session")"
        fi
    else
        echo -e "${RED}Failed to create session log${NC}"
        return 1
    fi
}

cleanup_old_sessions() {
    echo -e "${BLUE}🧹 Session Cleanup${NC}"
    echo ""
    
    # Count current sessions
    local total_sessions=$(find "$UMEMORY" -name "*Session.md" 2>/dev/null | wc -l)
    echo "Total session logs: $total_sessions"
    
    # Find sessions older than 30 days
    local old_sessions=$(find "$UMEMORY" -name "*Session.md" -mtime +30 2>/dev/null)
    local old_count=$(echo "$old_sessions" | grep -c . 2>/dev/null || echo 0)
    
    if [[ $old_count -gt 0 ]]; then
        echo "Sessions older than 30 days: $old_count"
        echo ""
        echo -e "${YELLOW}Would you like to remove old sessions? (y/N):${NC} "
        read -r response
        
        if [[ "$response" =~ ^[Yy]$ ]]; then
            echo "$old_sessions" | xargs rm -f 2>/dev/null
            echo -e "${GREEN}Removed $old_count old session logs${NC}"
        else
            echo "Cleanup cancelled"
        fi
    else
        echo "No old sessions to clean up"
    fi
}

show_session_stats() {
    echo -e "${BLUE}📊 Session Statistics${NC}"
    echo ""
    
    # Count sessions by type
    local total_sessions=$(find "$UMEMORY" -name "*Session.md" 2>/dev/null | wc -l)
    local installation_logs=$(find "$UMEMORY" -name "*Installation.md" 2>/dev/null | wc -l)
    
    echo "Session logs: $total_sessions"
    echo "Installation logs: $installation_logs"
    echo ""
    
    # Show date range
    if [[ $total_sessions -gt 0 ]]; then
        local oldest=$(find "$UMEMORY" -name "*Session.md" -exec stat -f "%m %N" {} \; 2>/dev/null | sort -n | head -1 | cut -d' ' -f2-)
        local newest=$(find "$UMEMORY" -name "*Session.md" -exec stat -f "%m %N" {} \; 2>/dev/null | sort -nr | head -1 | cut -d' ' -f2-)
        
        if [[ -n "$oldest" ]] && [[ -n "$newest" ]]; then
            echo "Date range:"
            echo "  Oldest: $(basename "$oldest" | sed 's/uLOG-//' | sed 's/-[^-]*-Session.md//')"
            echo "  Newest: $(basename "$newest" | sed 's/uLOG-//' | sed 's/-[^-]*-Session.md//')"
        fi
    fi
    
    # Storage usage
    local storage_usage=$(du -sh "$UMEMORY" 2>/dev/null | cut -f1)
    echo ""
    echo "Storage usage: $storage_usage"
}

# Main function
session_main() {
    local action="${1:-current}"
    local param="${2:-}"
    
    case "$action" in
        "current")
            show_current_session
            ;;
        "list")
            list_recent_sessions
            ;;
        "view")
            view_session_log "$param"
            ;;
        "new")
            create_new_session
            ;;
        "cleanup")
            cleanup_old_sessions
            ;;
        "stats")
            show_session_stats
            ;;
        *)
            echo "Session module - Available actions: current, list, view [id], new, cleanup, stats"
            ;;
    esac
}

# Export main function
if [[ "${BASH_SOURCE[0]}" == "${0}" ]]; then
    session_main "$@"
fi
