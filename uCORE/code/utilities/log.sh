#!/bin/bash
# uCORE Log Utility - Simple Logging Operations
# Handles logging operations for uCORE compatibility

set -euo pipefail

# Get script directory
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
UDOS_ROOT="$(cd "$SCRIPT_DIR/../../.." && pwd)"

# Logging functions
log_info() { echo -e "\033[0;36m[INFO]\033[0m $1"; }
log_success() { echo -e "\033[0;32m[SUCCESS]\033[0m $1"; }
log_warning() { echo -e "\033[0;33m[WARNING]\033[0m $1"; }
log_error() { echo -e "\033[0;31m[ERROR]\033[0m $1"; }

# Log directories
LOG_DIR="$UDOS_ROOT/sandbox/logs"
SYSTEM_LOG_DIR="$UDOS_ROOT/uMEMORY/system/logs"

# Write log entry
write_log() {
    local level="${1:-INFO}"
    local message="$2"
    local component="${3:-uCORE}"

    # Ensure log directory exists
    mkdir -p "$LOG_DIR"

    local timestamp=$(date '+%Y-%m-%d %H:%M:%S')
    local log_file="$LOG_DIR/$component-$(date '+%Y%m%d').log"

    # Write to log file
    echo "[$timestamp] [$level] $message" >> "$log_file"

    # Also display to console with colors
    case "$level" in
        ERROR)
            log_error "$message"
            ;;
        WARN|WARNING)
            log_warning "$message"
            ;;
        SUCCESS)
            log_success "$message"
            ;;
        *)
            log_info "$message"
            ;;
    esac
}

# View recent logs
view_recent() {
    local component="${1:-uCORE}"
    local lines="${2:-20}"

    local log_file="$LOG_DIR/$component-$(date '+%Y%m%d').log"

    if [ -f "$log_file" ]; then
        log_info "Recent $component logs (last $lines lines):"
        echo ""
        tail -n "$lines" "$log_file" | while IFS= read -r line; do
            # Color code log levels
            if [ "$line" =~ \[ERROR\] ]; then
                echo -e "\033[0;31m$line\033[0m"
            elif [ "$line" =~ \[WARN\] ]; then
                echo -e "\033[0;33m$line\033[0m"
            elif [ "$line" =~ \[SUCCESS\] ]; then
                echo -e "\033[0;32m$line\033[0m"
            else
                echo "$line"
            fi
        done
    else
        log_warning "No logs found for $component today"
    fi
}

# List available log files
list_logs() {
    log_info "Available log files:"

    if [ -d "$LOG_DIR" ]; then
        for log_file in "$LOG_DIR"/*.log; do
            if [ -f "$log_file" ]; then
                local name=$(basename "$log_file")
                local size=$(wc -l < "$log_file")
                local modified=$(date -r "$log_file" '+%Y-%m-%d %H:%M')
                echo "  📄 $name ($size lines, modified: $modified)"
            fi
        done
    fi

    if [ -d "$SYSTEM_LOG_DIR" ]; then
        echo ""
        log_info "System log files:"
        for log_file in "$SYSTEM_LOG_DIR"/*.log; do
            if [ -f "$log_file" ]; then
                local name=$(basename "$log_file")
                local size=$(wc -l < "$log_file")
                local modified=$(date -r "$log_file" '+%Y-%m-%d %H:%M')
                echo "  📄 $name ($size lines, modified: $modified)"
            fi
        done
    fi
}

# Search logs
search_logs() {
    local query="$1"
    local component="${2:-}"

    log_info "Searching logs for: $query"

    local search_pattern="$LOG_DIR"
    if [ -n "$component" ]; then
        search_pattern="$LOG_DIR/$component-*.log"
    else
        search_pattern="$LOG_DIR/*.log"
    fi

    local found=false
    for log_file in $search_pattern; do
        if [ -f "$log_file" ]; then
            local matches=$(grep -i "$query" "$log_file" 2>/dev/null)
            if [ -n "$matches" ]; then
                echo ""
                echo "In $(basename "$log_file"):"
                echo "$matches" | while IFS= read -r line; do
                    # Highlight search term
                    echo "$line" | sed "s/$query/$(echo -e '\033[1;33m')&$(echo -e '\033[0m')/gi"
                done
                found=true
            fi
        fi
    done

    if [ "$found" == false ]; then
        log_warning "No matches found for: $query"
    fi
}

# Clean old logs
clean_logs() {
    local days="${1:-7}"

    log_info "Cleaning logs older than $days days..."

    local count=0
    if [ -d "$LOG_DIR" ]; then
        while IFS= read -r -d '' log_file; do
            rm "$log_file"
            ((count++))
        done < <(find "$LOG_DIR" -name "*.log" -mtime +$days -print0 2>/dev/null)
    fi

    if [ $count -gt 0 ]; then
        log_success "Cleaned $count old log files"
    else
        log_info "No old log files to clean"
    fi
}

# Create system snapshot log
snapshot() {
    local description="${1:-System snapshot}"

    local snapshot_file="$LOG_DIR/uLOG-$(date '+%Y%m%d-%H%M%S')-Snapshot.md"

    cat > "$snapshot_file" << EOF
# uDOS System Snapshot

**Generated**: $(date '+%Y-%m-%d %H:%M:%S')
**Description**: $description
**uDOS Version**: v1.0.4.1

---

## System Status

**Timestamp**: $(date -Iseconds)
**User**: $(whoami)
**Directory**: $(pwd)
**Platform**: $(uname -s)

---

## Current Activity

$(if [ -f "$UDOS_ROOT/sandbox/user.md" ]; then
    echo "**User Role**: $(grep '^role:' "$UDOS_ROOT/sandbox/user.md" 2>/dev/null | cut -d' ' -f2 || echo 'Unknown')"
    echo "**Location**: $(grep '^location:' "$UDOS_ROOT/sandbox/user.md" 2>/dev/null | cut -d' ' -f2- || echo 'Unknown')"
fi)

---

## Recent Logs

$(tail -10 "$LOG_DIR"/uCORE-$(date '+%Y%m%d').log 2>/dev/null | sed 's/^/    /' || echo "    No recent logs")

---

*Generated by uCORE Log System*
EOF

    log_success "Snapshot created: $snapshot_file"
}

# Show usage
show_usage() {
    echo "Usage: log <command> [options]"
    echo ""
    echo "Commands:"
    echo "  write <level> <message> [component]  Write log entry"
    echo "  recent [component] [lines]           View recent logs"
    echo "  list                                 List available log files"
    echo "  search <query> [component]           Search logs"
    echo "  clean [days]                         Clean old logs (default: 7 days)"
    echo "  snapshot [description]               Create system snapshot"
    echo ""
    echo "Log Levels:"
    echo "  INFO, WARN, ERROR, SUCCESS, DEBUG"
    echo ""
    echo "Examples:"
    echo "  log write INFO 'System started'"
    echo "  log write ERROR 'Connection failed' network"
    echo "  log recent uCORE 30"
    echo "  log search 'ERROR' uCORE"
    echo "  log clean 3"
    echo "  log snapshot 'Before system update'"
}

# Main execution
main() {
    if [ $# -eq 0 ]; then
        show_usage
        return 1
    fi

    case "$1" in
        help|--help|-h)
            show_usage
            ;;
        write)
            if [ $# -lt 3 ]; then
                log_error "write requires level and message"
                return 1
            fi
            write_log "$2" "$3" "${4:-uCORE}"
            ;;
        recent)
            view_recent "${2:-uCORE}" "${3:-20}"
            ;;
        list)
            list_logs
            ;;
        search)
            if [ $# -lt 2 ]; then
                log_error "search requires query"
                return 1
            fi
            search_logs "$2" "${3:-}"
            ;;
        clean)
            clean_logs "${2:-7}"
            ;;
        snapshot)
            snapshot "${2:-System snapshot}"
            ;;
        *)
            log_error "Unknown command: $1"
            show_usage
            return 1
            ;;
    esac
}

# Run if executed directly
if [ "${BASH_SOURCE[0]}" == "${0}" ]; then
    main "$@"
fi
