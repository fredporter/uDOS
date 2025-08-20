#!/bin/bash

# uDOS Wizard Development Mode Logging System
# File: wizard-dev-logging.sh
# Purpose: Comprehensive dev mode logging and error handling for wizard environment
# Level: 100/100 - Full Development Authority
# uHEX: E8011F36 - Wizard Dev Mode Logging System

set -euo pipefail

# Configuration
WIZARD_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
DEV_LOGS_DIR="$WIZARD_ROOT/logs"
DEV_ERRORS_DIR="$WIZARD_ROOT/errors" 
DEV_ANALYTICS_DIR="$WIZARD_ROOT/analytics"
DEV_SESSION_DIR="$WIZARD_ROOT/sessions"

# Ensure directories exist
mkdir -p "$DEV_LOGS_DIR" "$DEV_ERRORS_DIR" "$DEV_ANALYTICS_DIR" "$DEV_SESSION_DIR"

# Date and time
TODAY="$(date +%Y%m%d)"
NOW="$(date +%H%M%S)"
TIMESTAMP="$(date +%Y-%m-%dT%H:%M:%SZ)"
DAY_OF_WEEK="$(date +%A)"

# Color codes for development output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
PURPLE='\033[0;35m'
CYAN='\033[0;36m'
BOLD='\033[1m'
DIM='\033[2m'
NC='\033[0m'

# Unicode symbols for wizard context
WIZARD_SYMBOLS=(
    "🧙‍♂️" "⚡" "🔮" "📚" "⚙️" "🎯" "🚀" "💾" "🔬" "🎨"
    "🛠️" "📊" "🔍" "💡" "🎪" "🌟" "🔥" "💫" "✨" "🌀"
)

# Generate wizard-themed log prefixes
get_wizard_symbol() {
    local context="$1"
    case "$context" in
        "error") echo "🔥" ;;
        "warning") echo "⚠️" ;;
        "info") echo "💡" ;;
        "success") echo "✨" ;;
        "debug") echo "🔍" ;;
        "performance") echo "⚡" ;;
        "security") echo "🛡️" ;;
        "system") echo "⚙️" ;;
        "wizard") echo "🧙‍♂️" ;;
        *) echo "${WIZARD_SYMBOLS[$((RANDOM % ${#WIZARD_SYMBOLS[@]}))]}" ;;
    esac
}

# Logging functions with wizard theming
log_wizard_info() {
    local symbol=$(get_wizard_symbol "info")
    echo -e "${CYAN}$symbol $1${NC}"
    dev_log "INFO" "$1" "wizard"
}

log_wizard_success() {
    local symbol=$(get_wizard_symbol "success")
    echo -e "${GREEN}$symbol $1${NC}"
    dev_log "SUCCESS" "$1" "wizard"
}

log_wizard_warning() {
    local symbol=$(get_wizard_symbol "warning")
    echo -e "${YELLOW}$symbol $1${NC}"
    dev_log "WARNING" "$1" "wizard"
}

log_wizard_error() {
    local symbol=$(get_wizard_symbol "error")
    echo -e "${RED}$symbol $1${NC}"
    dev_log "ERROR" "$1" "wizard" true
}

log_wizard_debug() {
    local symbol=$(get_wizard_symbol "debug")
    if [[ "${WIZARD_DEBUG:-false}" == "true" ]]; then
        echo -e "${DIM}$symbol $1${NC}"
        dev_log "DEBUG" "$1" "wizard"
    fi
}

log_wizard_performance() {
    local symbol=$(get_wizard_symbol "performance")
    echo -e "${PURPLE}$symbol $1${NC}"
    dev_log "PERFORMANCE" "$1" "wizard"
}

# Core development logging function
dev_log() {
    local level="$1"
    local message="$2"
    local context="${3:-development}"
    local is_error="${4:-false}"
    
    local log_file="$DEV_LOGS_DIR/wizard-dev-$TODAY.log"
    local session_id="${DEV_SESSION_ID:-$(generate_session_id)}"
    
    # Create structured log entry
    cat >> "$log_file" << EOF
[$TIMESTAMP] [$level] [$context] [$session_id]
Message: $message
Thread: $(get_thread_info)
Memory: $(get_memory_usage)
Context: $(get_dev_context)
---
EOF

    # Log errors to separate error file
    if [[ "$is_error" == "true" ]]; then
        log_dev_error "$message" "$context" "$level"
    fi
    
    # Update development analytics
    update_dev_analytics "$level" "$context"
}

# Enhanced error logging for development
log_dev_error() {
    local error_message="$1"
    local context="${2:-unknown}"
    local level="${3:-ERROR}"
    
    local error_file="$DEV_ERRORS_DIR/wizard-errors-$TODAY.log"
    local error_id="ERR_${TODAY}_${NOW}_$(printf "%04X" $RANDOM)"
    
    cat >> "$error_file" << EOF
🔥 WIZARD DEVELOPMENT ERROR - $error_id
═══════════════════════════════════════════════════════════════
Timestamp: $TIMESTAMP
Level: $level
Context: $context
Session: ${DEV_SESSION_ID:-unknown}
Thread: $(get_thread_info)
Environment: $(get_dev_environment)
Stack Trace: $(get_stack_trace)

Error Message:
$error_message

System State:
$(get_system_state)

Development Context:
$(get_dev_context)

Recommendations:
$(generate_error_recommendations "$error_message" "$context")

═══════════════════════════════════════════════════════════════
EOF

    # Create error notification for development environment
    create_error_notification "$error_id" "$error_message" "$context"
}

# Session management for development
generate_session_id() {
    local session_id="WIZ_${TODAY}_${NOW}_$(printf "%04X" $RANDOM)"
    export DEV_SESSION_ID="$session_id"
    
    # Create session file
    cat > "$DEV_SESSION_DIR/session-$session_id.json" << EOF
{
    "session_id": "$session_id",
    "start_time": "$TIMESTAMP",
    "environment": "wizard",
    "user": "${USER:-unknown}",
    "git_branch": "$(git rev-parse --abbrev-ref HEAD 2>/dev/null || echo 'unknown')",
    "git_commit": "$(git rev-parse --short HEAD 2>/dev/null || echo 'unknown')",
    "wizard_version": "v1.3",
    "system_info": {
        "os": "$(uname -s)",
        "arch": "$(uname -m)",
        "hostname": "$(hostname)",
        "shell": "$SHELL"
    },
    "performance": {
        "memory_start": "$(get_memory_usage)",
        "cpu_start": "$(get_cpu_usage)"
    },
    "activities": []
}
EOF
    
    echo "$session_id"
}

# Performance monitoring
get_memory_usage() {
    if command -v free >/dev/null 2>&1; then
        free -h | grep Mem | awk '{print $3"/"$2}'
    elif command -v vm_stat >/dev/null 2>&1; then
        vm_stat | grep "Pages active" | awk '{print $3}' | sed 's/\.//'
    else
        echo "unknown"
    fi
}

get_cpu_usage() {
    if command -v top >/dev/null 2>&1; then
        top -l 1 -n 0 | grep "CPU usage" | awk '{print $3}' 2>/dev/null || echo "unknown"
    else
        echo "unknown"
    fi
}

get_thread_info() {
    echo "PID:$$ PPID:$PPID Thread:$(basename "$0")"
}

get_system_state() {
    cat << EOF
Load Average: $(uptime | awk -F'load average:' '{print $2}' | sed 's/^[ \t]*//')
Disk Usage: $(df -h . | tail -1 | awk '{print $5}')
Network: $(ping -c 1 google.com >/dev/null 2>&1 && echo "online" || echo "offline")
Git Status: $(git status --porcelain 2>/dev/null | wc -l | tr -d ' ') uncommitted changes
EOF
}

get_dev_environment() {
    cat << EOF
WIZARD_ROOT: $WIZARD_ROOT
DEV_MODE: ${WIZARD_DEV_MODE:-false}
LOG_LEVEL: ${WIZARD_LOG_LEVEL:-info}
DEBUG: ${WIZARD_DEBUG:-false}
PATH: $PATH
EOF
}

get_dev_context() {
    cat << EOF
Working Directory: $(pwd)
Script Name: $(basename "$0")
Arguments: $*
Terminal: ${TERM:-unknown}
Session Type: ${SSH_TTY:+ssh}${SSH_TTY:-local}
EOF
}

get_stack_trace() {
    local i=1
    while caller $i 2>/dev/null; do
        ((i++))
    done | while read line func file; do
        echo "  at $func ($file:$line)"
    done
}

# Analytics and reporting
update_dev_analytics() {
    local level="$1"
    local context="$2"
    
    local analytics_file="$DEV_ANALYTICS_DIR/wizard-analytics-$TODAY.json"
    
    # Initialize analytics file if it doesn't exist
    if [[ ! -f "$analytics_file" ]]; then
        cat > "$analytics_file" << EOF
{
    "date": "$TODAY",
    "wizard_session": "${DEV_SESSION_ID:-unknown}",
    "log_levels": {},
    "contexts": {},
    "performance_metrics": {},
    "error_analysis": {},
    "development_stats": {
        "commits": 0,
        "files_modified": 0,
        "lines_added": 0,
        "lines_removed": 0,
        "build_success": 0,
        "build_failed": 0,
        "tests_passed": 0,
        "tests_failed": 0
    }
}
EOF
    fi
    
    # Update analytics using jq if available
    if command -v jq >/dev/null 2>&1; then
        local temp_file=$(mktemp)
        jq ".log_levels[\"$level\"] += 1 | .contexts[\"$context\"] += 1" "$analytics_file" > "$temp_file" && mv "$temp_file" "$analytics_file"
    fi
}

# Error recommendation system
generate_error_recommendations() {
    local error_message="$1"
    local context="$2"
    
    cat << EOF
1. Check the wizard development documentation
2. Verify environment variables and configuration
3. Ensure all dependencies are installed
4. Review recent git changes that might have caused the issue
5. Check system resources (memory, disk space, network)
6. Consult the wizard error handling guide
7. Enable debug mode for more detailed logging
8. Review similar errors in the error log history
EOF
}

# Error notification system
create_error_notification() {
    local error_id="$1"
    local error_message="$2"
    local context="$3"
    
    # Create desktop notification if available
    if command -v osascript >/dev/null 2>&1; then
        osascript -e "display notification \"$error_message\" with title \"Wizard Development Error\" subtitle \"$error_id\"" 2>/dev/null || true
    fi
    
    # Log to system log if available
    if command -v logger >/dev/null 2>&1; then
        logger -t "uDOS-Wizard" "Error $error_id: $error_message [$context]"
    fi
}

# Development activity tracking
track_dev_activity() {
    local activity_type="$1"
    local description="$2"
    local success="${3:-true}"
    
    local session_file="$DEV_SESSION_DIR/session-${DEV_SESSION_ID}.json"
    
    if [[ -f "$session_file" ]] && command -v jq >/dev/null 2>&1; then
        local activity_entry=$(cat << EOF
{
    "timestamp": "$TIMESTAMP",
    "type": "$activity_type",
    "description": "$description",
    "success": $success,
    "duration": 0
}
EOF
        )
        
        local temp_file=$(mktemp)
        jq ".activities += [$activity_entry]" "$session_file" > "$temp_file" && mv "$temp_file" "$session_file"
    fi
    
    log_wizard_info "Development Activity: $activity_type - $description"
}

# Main command interface
main() {
    case "${1:-help}" in
        "init")
            log_wizard_info "Initializing Wizard Development Logging System"
            generate_session_id >/dev/null
            log_wizard_success "Development logging initialized with session: $DEV_SESSION_ID"
            ;;
        "log")
            if [[ $# -lt 3 ]]; then
                log_wizard_error "Usage: $0 log <level> <message> [context]"
                exit 1
            fi
            dev_log "$2" "$3" "${4:-development}"
            ;;
        "error")
            if [[ $# -lt 2 ]]; then
                log_wizard_error "Usage: $0 error <message> [context]"
                exit 1
            fi
            log_wizard_error "$2"
            log_dev_error "$2" "${3:-unknown}" "ERROR"
            ;;
        "activity")
            if [[ $# -lt 3 ]]; then
                log_wizard_error "Usage: $0 activity <type> <description> [success]"
                exit 1
            fi
            track_dev_activity "$2" "$3" "${4:-true}"
            ;;
        "session")
            if [[ -n "${DEV_SESSION_ID:-}" ]]; then
                echo "Current session: $DEV_SESSION_ID"
                if [[ -f "$DEV_SESSION_DIR/session-$DEV_SESSION_ID.json" ]]; then
                    echo "Session details:"
                    cat "$DEV_SESSION_DIR/session-$DEV_SESSION_ID.json" | jq '.' 2>/dev/null || cat "$DEV_SESSION_DIR/session-$DEV_SESSION_ID.json"
                fi
            else
                echo "No active development session"
            fi
            ;;
        "analytics")
            local analytics_file="$DEV_ANALYTICS_DIR/wizard-analytics-$TODAY.json"
            if [[ -f "$analytics_file" ]]; then
                echo "📊 Wizard Development Analytics - $TODAY"
                cat "$analytics_file" | jq '.' 2>/dev/null || cat "$analytics_file"
            else
                log_wizard_warning "No analytics data available for today"
            fi
            ;;
        "report")
            generate_dev_report
            ;;
        "help"|*)
            show_wizard_usage
            ;;
    esac
}

# Generate development report
generate_dev_report() {
    local report_file="$DEV_LOGS_DIR/wizard-dev-report-$TODAY.md"
    
    cat > "$report_file" << EOF
# 🧙‍♂️ Wizard Development Report - $TODAY

**Generated**: $TIMESTAMP  
**Session**: ${DEV_SESSION_ID:-unknown}  
**Environment**: wizard Development Level 100

## 📊 Development Statistics

$(generate_dev_statistics)

## 🔥 Error Summary

$(generate_error_summary)

## ⚡ Performance Metrics

$(generate_performance_summary)

## 🎯 Development Activities

$(generate_activity_summary)

## 🔍 System Health

$(generate_system_health)

---

*Generated by uDOS Wizard Development Logging System v1.3*
*uHEX: E8011F36 - Advanced Development Authority*
EOF

    log_wizard_success "Development report generated: $report_file"
}

generate_dev_statistics() {
    local log_file="$DEV_LOGS_DIR/wizard-dev-$TODAY.log"
    if [[ -f "$log_file" ]]; then
        echo "- **Total Log Entries**: $(wc -l < "$log_file")"
        echo "- **Error Count**: $(grep -c '\[ERROR\]' "$log_file" 2>/dev/null || echo 0)"
        echo "- **Warning Count**: $(grep -c '\[WARNING\]' "$log_file" 2>/dev/null || echo 0)"
        echo "- **Success Count**: $(grep -c '\[SUCCESS\]' "$log_file" 2>/dev/null || echo 0)"
    else
        echo "- No development logs available for today"
    fi
}

generate_error_summary() {
    local error_file="$DEV_ERRORS_DIR/wizard-errors-$TODAY.log"
    if [[ -f "$error_file" ]]; then
        echo "- **Error File Size**: $(wc -l < "$error_file") lines"
        echo "- **Recent Errors**: $(tail -5 "$error_file" | grep "Error Message:" | sed 's/Error Message: /- /')"
    else
        echo "- No errors logged today ✨"
    fi
}

generate_performance_summary() {
    echo "- **Memory Usage**: $(get_memory_usage)"
    echo "- **CPU Usage**: $(get_cpu_usage)"
    echo "- **Load Average**: $(uptime | awk -F'load average:' '{print $2}' | sed 's/^[ \t]*//')"
    echo "- **Disk Usage**: $(df -h . | tail -1 | awk '{print $5}')"
}

generate_activity_summary() {
    local session_file="$DEV_SESSION_DIR/session-${DEV_SESSION_ID}.json"
    if [[ -f "$session_file" ]] && command -v jq >/dev/null 2>&1; then
        echo "- **Activities Tracked**: $(jq '.activities | length' "$session_file")"
        echo "- **Successful Activities**: $(jq '[.activities[] | select(.success == true)] | length' "$session_file")"
        echo "- **Failed Activities**: $(jq '[.activities[] | select(.success == false)] | length' "$session_file")"
    else
        echo "- No activity tracking data available"
    fi
}

generate_system_health() {
    echo "$(get_system_state)"
}

show_wizard_usage() {
    cat << EOF
🧙‍♂️ uDOS Wizard Development Logging System v1.3
═══════════════════════════════════════════════════════════════

Usage: $0 [command] [options]

Commands:
  init                              Initialize development logging session
  log <level> <message> [context]   Log development message
  error <message> [context]         Log development error
  activity <type> <description>     Track development activity
  session                          Show current session information
  analytics                        Show development analytics
  report                           Generate comprehensive development report
  help                             Show this help message

Logging Levels:
  INFO, SUCCESS, WARNING, ERROR, DEBUG, PERFORMANCE

Examples:
  $0 init
  $0 log INFO "Starting wizard development"
  $0 error "Build failed" "compilation"
  $0 activity "build" "Compiling TypeScript"
  $0 report

Environment Variables:
  WIZARD_DEBUG=true               Enable debug logging
  WIZARD_LOG_LEVEL=debug          Set minimum log level
  WIZARD_DEV_MODE=true            Enable development mode features

Files Generated:
  wizard/logs/wizard-dev-YYYYMMDD.log       Daily development log
  wizard/errors/wizard-errors-YYYYMMDD.log  Error log
  wizard/analytics/wizard-analytics-YYYYMMDD.json  Analytics data
  wizard/sessions/session-ID.json           Session tracking

🔮 Advanced Development Authority - Level 100 Access
uHEX: E8011F36 - Wizard Dev Mode Logging System
EOF
}

# Initialize session if not already done
if [[ -z "${DEV_SESSION_ID:-}" ]]; then
    generate_session_id >/dev/null
fi

# Run main function if script is executed directly
if [[ "${BASH_SOURCE[0]}" == "${0}" ]]; then
    main "$@"
fi
