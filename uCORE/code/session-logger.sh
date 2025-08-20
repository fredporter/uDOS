#!/bin/bash

# uDOS Session Logger v1.3
# Creates uLOG files for each session (restart/reboot)
# Tracks session data, system state, and user activity

set -euo pipefail

# Colors for output
GREEN='\033[0;32m'
BLUE='\033[0;34m'
CYAN='\033[0;36m'
NC='\033[0m'

# Get the uDOS root directory
UDOS_ROOT="${UDOS_ROOT:-$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)}"
UMEMORY_DIR="$UDOS_ROOT/uMEMORY"
USER_FILE="$UDOS_ROOT/sandbox/user.md"

# Log functions
log_info() { echo -e "${CYAN}ℹ️  $1${NC}"; }
log_success() { echo -e "${GREEN}✅ $1${NC}"; }

# Generate hex filename for session log
generate_session_hex() {
    local date_stamp=$(date +%Y%m%d)
    local time_stamp=$(date +%H%M%S)
    local random_hex=$(printf "%08X" $((RANDOM * RANDOM)))
    echo "${date_stamp}-${time_stamp}-${random_hex}"
}

# Get user information from sandbox/user.md
get_user_info() {
    local key="$1"
    local default_value="${2:-Unknown}"
    
    if [[ ! -f "$USER_FILE" ]]; then
        echo "$default_value"
        return
    fi
    
    local value=$(grep "^\*\*${key}\*\*:" "$USER_FILE" 2>/dev/null | sed "s/^\*\*${key}\*\*: *//" | sed 's/^`//;s/`$//')
    echo "${value:-$default_value}"
}

# Get system information
get_system_info() {
    case "$1" in
        "uptime")
            uptime | awk '{print $3, $4}' | sed 's/,//'
            ;;
        "load")
            uptime | awk -F'load average:' '{print $2}' | xargs
            ;;
        "memory")
            if command -v free >/dev/null 2>&1; then
                free -h | awk '/^Mem:/ {print $3 "/" $2}'
            else
                # macOS alternative
                vm_stat | awk '
                /Pages free/ {free = $3}
                /Pages active/ {active = $3}
                /Pages inactive/ {inactive = $3}
                /Pages speculative/ {spec = $3}
                /Pages wired/ {wired = $3}
                END {
                    total = (free + active + inactive + spec + wired) * 4096 / 1024 / 1024 / 1024
                    used = (active + inactive + spec + wired) * 4096 / 1024 / 1024 / 1024
                    printf "%.1fG/%.1fG", used, total
                }'
            fi
            ;;
        "disk")
            df -h "$UDOS_ROOT" | awk 'NR==2 {print $3 "/" $2 " (" $5 " used)"}'
            ;;
        "processes")
            ps aux | wc -l
            ;;
    esac
}

# Count files in various directories
count_files() {
    local dir="$1"
    if [[ -d "$dir" ]]; then
        find "$dir" -type f 2>/dev/null | wc -l | xargs
    else
        echo "0"
    fi
}

# Get recent activity
get_recent_activity() {
    local activity_log=""
    
    # Check for recent uMEMORY files
    local recent_memory=$(find "$UMEMORY_DIR" -name "*.md" -mtime -1 2>/dev/null | wc -l | xargs)
    if [[ "$recent_memory" -gt 0 ]]; then
        activity_log="${activity_log}- $recent_memory recent uMEMORY files modified\n"
    fi
    
    # Check for recent sandbox activity
    local recent_sandbox=$(find "$UDOS_ROOT/sandbox" -type f -mtime -1 2>/dev/null | wc -l | xargs)
    if [[ "$recent_sandbox" -gt 0 ]]; then
        activity_log="${activity_log}- $recent_sandbox recent sandbox files modified\n"
    fi
    
    # Check for recent logs
    local recent_logs=$(find "$UDOS_ROOT" -name "*.log" -mtime -1 2>/dev/null | wc -l | xargs)
    if [[ "$recent_logs" -gt 0 ]]; then
        activity_log="${activity_log}- $recent_logs recent log files\n"
    fi
    
    if [[ -z "$activity_log" ]]; then
        echo "- No recent activity detected"
    else
        echo -e "$activity_log" | sed 's/\\n$//'
    fi
}

# Get session type (startup, restart, reboot, etc.)
get_session_type() {
    local session_type="${1:-startup}"
    case "$session_type" in
        "startup"|"start")
            echo "System Startup"
            ;;
        "restart"|"reload")
            echo "Session Restart"
            ;;
        "reboot")
            echo "System Reboot"
            ;;
        "destroy")
            echo "Security Destroy/Reboot"
            ;;
        "manual")
            echo "Manual Session Log"
            ;;
        *)
            echo "Session Event"
            ;;
    esac
}

# Create session log
create_session_log() {
    local session_type="${1:-startup}"
    local session_hex=$(generate_session_hex)
    local session_file="$UMEMORY_DIR/uLOG-${session_hex}-Session.md"
    
    # Ensure uMEMORY directory exists
    mkdir -p "$UMEMORY_DIR"
    
    # Get user information
    local username=$(get_user_info "Username" "Unknown")
    local user_id=$(get_user_info "User ID" "Unknown")
    local user_role=$(get_user_info "Role" "user")
    local theme=$(get_user_info "Theme" "default")
    local timezone=$(get_user_info "Timezone" "Unknown")
    
    # Get system information
    local current_time=$(date "+%Y-%m-%d %H:%M:%S")
    local system_uptime=$(get_system_info "uptime")
    local system_load=$(get_system_info "load")
    local memory_usage=$(get_system_info "memory")
    local disk_usage=$(get_system_info "disk")
    local process_count=$(get_system_info "processes")
    
    # Get file counts
    local umemory_files=$(count_files "$UMEMORY_DIR")
    local sandbox_files=$(count_files "$UDOS_ROOT/sandbox")
    local script_files=$(count_files "$UDOS_ROOT/uSCRIPT")
    
    # Create the session log
    cat > "$session_file" << EOF
# 🔄 uDOS Session Log
**Session Type**: $(get_session_type "$session_type")  
**Session Time**: $current_time  
**Log Type**: Session Activity  
**Session ID**: $session_hex

## 👤 User Context
**Username**: $username  
**User ID**: $user_id  
**Role**: $user_role  
**Theme**: $theme  
**Timezone**: $timezone

## 🖥️ System State
**Uptime**: $system_uptime  
**Load Average**: $system_load  
**Memory Usage**: $memory_usage  
**Disk Usage**: $disk_usage  
**Active Processes**: $process_count

## 📊 Data Statistics
**uMEMORY Files**: $umemory_files  
**Sandbox Files**: $sandbox_files  
**Script Files**: $script_files  
**Total Session Logs**: $(find "$UMEMORY_DIR" -name "uLOG-*-Session.md" 2>/dev/null | wc -l | xargs)

## 🎯 Session Details
**Session Trigger**: $(get_session_type "$session_type")  
**Authentication**: $(if [[ -f "$USER_FILE" ]]; then echo "Valid"; else echo "Missing"; fi)  
**Backup Status**: $(if [[ -d "$UMEMORY_DIR/.backup" ]]; then echo "Available"; else echo "Not Configured"; fi)  
**Development Mode**: \${UDOS_DEV_MODE:-false}

## 📈 Recent Activity
$(get_recent_activity)

## 🔧 System Configuration
**uDOS Version**: v1.3  
**Platform**: $(uname -s)  
**Architecture**: $(uname -m)  
**Shell**: \$SHELL  
**Terminal**: \$TERM

---
*Session log created by uDOS Session Logger*  
*Tracks system state and activity for each session*  
*Part of uLOG system for comprehensive session tracking*
EOF

    log_success "Session log created: uLOG-${session_hex}-Session.md"
    log_info "Session type: $(get_session_type "$session_type")"
    log_info "Session time: $current_time"
    
    echo "$session_file"
}

# Show recent session logs
show_recent_sessions() {
    local count="${1:-5}"
    
    log_info "Recent session logs:"
    find "$UMEMORY_DIR" -name "uLOG-*-Session.md" -type f 2>/dev/null | \
        sort -r | head -n "$count" | \
        while read -r file; do
            local basename=$(basename "$file")
            local session_time=$(grep "^\*\*Session Time\*\*:" "$file" | sed 's/^\*\*Session Time\*\*: *//')
            local session_type=$(grep "^\*\*Session Type\*\*:" "$file" | sed 's/^\*\*Session Type\*\*: *//')
            echo "  📄 $basename"
            echo "     ⏰ $session_time"
            echo "     🎯 $session_type"
        done
}

# Main function
main() {
    case "${1:-help}" in
        "create"|"new")
            local session_type="${2:-startup}"
            create_session_log "$session_type"
            ;;
        "startup"|"start")
            create_session_log "startup"
            ;;
        "restart"|"reload")
            create_session_log "restart"
            ;;
        "reboot")
            create_session_log "reboot"
            ;;
        "destroy")
            create_session_log "destroy"
            ;;
        "manual")
            create_session_log "manual"
            ;;
        "list"|"recent")
            show_recent_sessions "${2:-5}"
            ;;
        "help"|"-h"|"--help"|*)
            echo -e "${BLUE}🔄 uDOS Session Logger${NC}"
            echo ""
            echo "Usage: $0 <command>"
            echo ""
            echo "Commands:"
            echo "  create [type]  - Create new session log (default: startup)"
            echo "  startup        - Log system startup"
            echo "  restart        - Log session restart"
            echo "  reboot         - Log system reboot"
            echo "  destroy        - Log security destroy/reboot"
            echo "  manual         - Create manual session log"
            echo "  list [count]   - Show recent session logs (default: 5)"
            echo "  help           - Show this help"
            echo ""
            echo "Session Types:"
            echo "  • startup   - System startup/initialization"
            echo "  • restart   - Session restart/reload"
            echo "  • reboot    - System reboot"
            echo "  • destroy   - Security destroy and reboot"
            echo "  • manual    - Manually triggered log"
            echo ""
            echo "Output:"
            echo "  • Creates uLOG-YYYYMMDD-HHMMSS-HEX-Session.md in uMEMORY/"
            echo "  • Includes system state, user context, and activity"
            echo "  • Tracks session statistics and configuration"
            ;;
    esac
}

# Run main function
main "$@"
