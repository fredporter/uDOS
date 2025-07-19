#!/bin/bash
# Enhanced uDOS Move Logging System v2.1.0
# Compliant with template standards, shortcodes, and ASCII visualization

set -euo pipefail

# Configuration
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
UDOS_HOME="${HOME}/uDOS"
UMEMORY="${UDOS_HOME}/uMemory"
UTEMPLATE="${UDOS_HOME}/uTemplate"
SANDBOX="${UDOS_HOME}/sandbox"

# Date and time
TODAY="$(date +%Y-%m-%d)"
NOW="$(date +%H:%M:%S)"
TIMESTAMP="$(date +%Y-%m-%dT%H:%M:%SZ)"
DAY_OF_WEEK="$(date +%A)"

# File paths
DAILY_LOG="${UMEMORY}/moves/daily-log-${TODAY}.md"
MOVE_LOG="${UMEMORY}/moves/moves-${TODAY}.md"
STATS_FILE="${UMEMORY}/state/stats-${TODAY}.json"
ANALYTICS_FILE="${UMEMORY}/state/analytics-${TODAY}.json"
ERROR_LOG="${UMEMORY}/logs/errors-${TODAY}.log"
TEMPLATE_FILE="${UTEMPLATE}/daily-move-log-v2.md"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[0;33m'
BLUE='\033[0;34m'
PURPLE='\033[0;35m'
CYAN='\033[0;36m'
BOLD='\033[1m'
NC='\033[0m'

# Logging functions
log_info() { echo -e "${BLUE}📊 $1${NC}"; }
log_success() { echo -e "${GREEN}✅ $1${NC}"; }
log_warning() { echo -e "${YELLOW}⚠️  $1${NC}"; }
log_error() { echo -e "${RED}❌ $1${NC}"; }

# Initialize stats file if it doesn't exist
init_stats() {
    if [ ! -f "$STATS_FILE" ]; then
        cat > "$STATS_FILE" << EOF
{
    "date": "$TODAY",
    "day_of_week": "$DAY_OF_WEEK",
    "initialized": "$TIMESTAMP",
    "moves": {
        "total": 0,
        "mission": 0,
        "system": 0,
        "file": 0,
        "development": 0
    },
    "commands": {
        "total": 0,
        "unique": 0,
        "success": 0,
        "failed": 0
    },
    "timing": {
        "session_start": "$TIMESTAMP",
        "session_duration": 0,
        "average_command_time": 0
    },
    "performance": {
        "productivity_score": 0,
        "efficiency_score": 0,
        "completion_rate": 0
    },
    "objectives": {
        "total": 0,
        "completed": 0,
        "in_progress": 0,
        "pending": 0
    }
}
EOF
    fi
}

# Update statistics
update_stat() {
    local stat_path="$1"
    local value="$2"
    local operation="${3:-set}"
    
    if [ ! -f "$STATS_FILE" ]; then
        init_stats
    fi
    
    case "$operation" in
        "increment")
            current=$(jq -r "$stat_path" "$STATS_FILE" 2>/dev/null || echo "0")
            new_value=$((current + value))
            ;;
        "set")
            new_value="$value"
            ;;
        "append")
            # For arrays
            new_value="$value"
            ;;
    esac
    
    # Update the JSON file
    temp_file=$(mktemp)
    jq "$stat_path = $new_value" "$STATS_FILE" > "$temp_file" && mv "$temp_file" "$STATS_FILE"
}

# Log a move with enhanced metadata
log_move() {
    local command="$1"
    local move_type="${2:-system}"
    local context="${3:-}"
    local duration="${4:-0}"
    local success="${5:-true}"
    
    # Ensure directories exist
    mkdir -p "$(dirname "$MOVE_LOG")"
    mkdir -p "$(dirname "$DAILY_LOG")"
    
    # Initialize move log if needed
    if [ ! -f "$MOVE_LOG" ]; then
        echo "# 📊 Enhanced Move Log — $TODAY" > "$MOVE_LOG"
        echo "" >> "$MOVE_LOG"
        echo "**Generated**: $TIMESTAMP  " >> "$MOVE_LOG"
        echo "**Template Version**: v2.1.0" >> "$MOVE_LOG"
        echo "" >> "$MOVE_LOG"
        echo "---" >> "$MOVE_LOG"
        echo "" >> "$MOVE_LOG"
    fi
    
    # Generate move ID
    local move_count
    move_count=$(jq -r '.moves.total' "$STATS_FILE" 2>/dev/null || echo "0")
    local move_id="move_${TODAY}_$(printf "%03d" $((move_count + 1)))"
    
    # Log the move with shortcode format
    cat >> "$MOVE_LOG" << EOF
\`\`\`shortcode
{MOVE_ENTRY}
move_id: $move_id
timestamp: $NOW
command: "$command"
type: $move_type
duration: ${duration}s
success: $success
context: "$context"
session_time: $(date +%s)
{/MOVE_ENTRY}
\`\`\`

EOF
    
    # Update statistics
    update_stat '.moves.total' 1 increment
    update_stat ".moves.$move_type" 1 increment
    update_stat '.commands.total' 1 increment
    
    if [ "$success" = "true" ]; then
        update_stat '.commands.success' 1 increment
    else
        update_stat '.commands.failed' 1 increment
    fi
    
    log_info "Logged move: $command [$move_type]"
}

# Log an error with enhanced context
log_error_enhanced() {
    local error_message="$1"
    local command="${2:-unknown}"
    local context="${3:-}"
    
    mkdir -p "$(dirname "$ERROR_LOG")"
    
    # Log to error file
    cat >> "$ERROR_LOG" << EOF
[$TIMESTAMP] ❌ ERROR
Command: $command
Message: $error_message
Context: $context
---
EOF
    
    # Update error statistics
    update_stat '.commands.failed' 1 increment
    
    log_error "Error logged: $error_message"
}

# Generate ASCII progress bar
generate_progress_bar() {
    local current="$1"
    local total="$2"
    local width="${3:-20}"
    
    if [ "$total" -eq 0 ]; then
        echo "░░░░░░░░░░░░░░░░░░░░"
        return
    fi
    
    local percentage=$((current * 100 / total))
    local filled=$((current * width / total))
    local empty=$((width - filled))
    
    local bar=""
    for ((i=0; i<filled; i++)); do
        bar+="█"
    done
    for ((i=0; i<empty; i++)); do
        bar+="░"
    done
    
    echo "$bar"
}

# Generate daily report with template processing
generate_daily_report() {
    log_info "Generating enhanced daily report..."
    
    if [ ! -f "$STATS_FILE" ]; then
        init_stats
    fi
    
    # Read current statistics
    local stats
    stats=$(cat "$STATS_FILE")
    
    # Extract data
    local moves_total
    moves_total=$(echo "$stats" | jq -r '.moves.total')
    local moves_mission
    moves_mission=$(echo "$stats" | jq -r '.moves.mission')
    local moves_system
    moves_system=$(echo "$stats" | jq -r '.moves.system')
    local moves_file
    moves_file=$(echo "$stats" | jq -r '.moves.file')
    local moves_dev
    moves_dev=$(echo "$stats" | jq -r '.moves.development')
    
    local commands_total
    commands_total=$(echo "$stats" | jq -r '.commands.total')
    local commands_success
    commands_success=$(echo "$stats" | jq -r '.commands.success')
    local commands_failed
    commands_failed=$(echo "$stats" | jq -r '.commands.failed')
    
    # Calculate metrics
    local success_rate=0
    if [ "$commands_total" -gt 0 ]; then
        success_rate=$((commands_success * 100 / commands_total))
    fi
    
    local error_count
    error_count=$(wc -l < "$ERROR_LOG" 2>/dev/null || echo "0")
    
    # Generate progress bars
    local progress_bar
    progress_bar=$(generate_progress_bar "$commands_success" "$commands_total" 30)
    
    # Calculate success rate after error count
    local success_rate=0
    if [ "$commands_total" -gt 0 ]; then
        success_rate=$((commands_success * 100 / commands_total))
    fi
    
    # Calculate session time
    local session_start
    session_start=$(echo "$stats" | jq -r '.timing.session_start')
    local session_duration="Unknown"
    if [ "$session_start" != "null" ]; then
        local start_epoch
        start_epoch=$(date -j -f "%Y-%m-%dT%H:%M:%SZ" "$session_start" "+%s" 2>/dev/null || echo "0")
        local current_epoch
        current_epoch=$(date +%s)
        local duration_seconds=$((current_epoch - start_epoch))
        local hours=$((duration_seconds / 3600))
        local minutes=$(((duration_seconds % 3600) / 60))
        session_duration="${hours}h ${minutes}m"
    fi
    
    # Calculate error count safely
    local error_count=0
    if [ -f "$ERROR_LOG" ]; then
        error_count=$(wc -l < "$ERROR_LOG" 2>/dev/null || echo "0")
    fi
    
    # Copy template and substitute variables
    if [ -f "$TEMPLATE_FILE" ]; then
        cp "$TEMPLATE_FILE" "$DAILY_LOG"
        
        # Simple template substitution
        sed -i '' "s/{{log_date}}/$TODAY/g" "$DAILY_LOG"
        sed -i '' "s/{{day_of_week}}/$DAY_OF_WEEK/g" "$DAILY_LOG"
        sed -i '' "s/{{timestamp}}/$TIMESTAMP/g" "$DAILY_LOG"
        sed -i '' "s/{{moves_count}}/$moves_total/g" "$DAILY_LOG"
        sed -i '' "s/{{commands_count}}/$commands_total/g" "$DAILY_LOG"
        sed -i '' "s/{{errors_count}}/$error_count/g" "$DAILY_LOG"
        sed -i '' "s/{{session_time}}/$session_duration/g" "$DAILY_LOG"
        sed -i '' "s/{{progress_bar}}/$progress_bar/g" "$DAILY_LOG"
        sed -i '' "s/{{completion_percentage}}/$success_rate/g" "$DAILY_LOG"
        sed -i '' "s/{{mission_moves}}/$moves_mission/g" "$DAILY_LOG"
        sed -i '' "s/{{system_moves}}/$moves_system/g" "$DAILY_LOG"
        sed -i '' "s/{{file_moves}}/$moves_file/g" "$DAILY_LOG"
        sed -i '' "s/{{dev_moves}}/$moves_dev/g" "$DAILY_LOG"
        sed -i '' "s/{{success_rate}}/$success_rate/g" "$DAILY_LOG"
        sed -i '' "s/{{total_commands}}/$commands_total/g" "$DAILY_LOG"
        sed -i '' "s/{{generation_timestamp}}/$TIMESTAMP/g" "$DAILY_LOG"
        
    else
        log_warning "Template file not found, creating basic report"
        
        cat > "$DAILY_LOG" << EOF
# 📊 Daily Activity Report - $TODAY

**Generated**: $TIMESTAMP  
**Day**: $DAY_OF_WEEK

## Summary
- **Total Moves**: $moves_total
- **Commands**: $commands_total  
- **Success Rate**: $success_rate%
- **Errors**: $error_count
- **Session Time**: $session_duration

## Move Categories
- Mission: $moves_mission
- System: $moves_system  
- File: $moves_file
- Development: $moves_dev

## Progress
[$progress_bar] $success_rate%

---
*Generated by uDOS Enhanced Logging System v2.1.0*
EOF
    fi
    
    log_success "Daily report generated: $DAILY_LOG"
}

# Archive old files
archive_old_files() {
    local archive_date="$1"
    local archive_dir="${UMEMORY}/archive/$(date -j -v-7d +%Y-%m)"
    
    mkdir -p "$archive_dir"
    
    # Archive files older than 7 days
    find "${UMEMORY}/moves" -name "*.md" -mtime +7 -exec mv {} "$archive_dir/" \;
    find "${UMEMORY}/state" -name "stats-*.json" -mtime +7 -exec mv {} "$archive_dir/" \;
    find "${UMEMORY}/logs" -name "errors-*.log" -mtime +7 -exec mv {} "$archive_dir/" \;
    
    log_info "Archived files older than 7 days to: $archive_dir"
}

# Export data in different formats
export_data() {
    local format="$1"
    local output_dir="${UMEMORY}/exports/$(date +%Y-%m-%d)"
    
    mkdir -p "$output_dir"
    
    case "$format" in
        "json")
            cp "$STATS_FILE" "$output_dir/daily-stats.json"
            log_success "Exported JSON data to: $output_dir/daily-stats.json"
            ;;
        "csv")
            # Convert JSON to CSV (simplified)
            {
                echo "metric,value"
                jq -r '.moves | to_entries[] | "\(.key),\(.value)"' "$STATS_FILE"
            } > "$output_dir/daily-stats.csv"
            log_success "Exported CSV data to: $output_dir/daily-stats.csv"
            ;;
        "markdown")
            cp "$DAILY_LOG" "$output_dir/daily-report.md"
            log_success "Exported Markdown report to: $output_dir/daily-report.md"
            ;;
        *)
            log_error "Unknown export format: $format"
            ;;
    esac
}

# Show usage
show_usage() {
    echo "Enhanced uDOS Move Logging System v2.1.0"
    echo
    echo "Usage: $0 [command] [options]"
    echo
    echo "Commands:"
    echo "  move <command> [type] [context] [duration] [success]"
    echo "    Log a move with enhanced metadata"
    echo "    Types: mission, system, file, development"
    echo
    echo "  error <message> [command] [context]"
    echo "    Log an error with context"
    echo
    echo "  report"
    echo "    Generate daily report with template processing"
    echo
    echo "  stats"
    echo "    Show current statistics"
    echo
    echo "  export <format>"
    echo "    Export data (json, csv, markdown)"
    echo
    echo "  archive [days]"
    echo "    Archive files older than specified days (default: 7)"
    echo
    echo "  init"
    echo "    Initialize logging system"
    echo
    echo "Examples:"
    echo "  $0 move \"dash build\" system \"Building dashboard\" 15 true"
    echo "  $0 error \"Command not found\" \"invalid-cmd\" \"User typo\""
    echo "  $0 report"
    echo "  $0 export json"
}

# Main command processing
main() {
    case "${1:-help}" in
        move)
            if [ $# -lt 2 ]; then
                log_error "Command required for move logging"
                show_usage
                exit 1
            fi
            log_move "$2" "${3:-system}" "${4:-}" "${5:-0}" "${6:-true}"
            ;;
        error)
            if [ $# -lt 2 ]; then
                log_error "Error message required"
                show_usage
                exit 1
            fi
            log_error_enhanced "$2" "${3:-unknown}" "${4:-}"
            ;;
        report)
            generate_daily_report
            ;;
        stats)
            if [ -f "$STATS_FILE" ]; then
                log_info "Current statistics:"
                jq '.' "$STATS_FILE"
            else
                log_warning "No statistics file found. Run 'init' first."
            fi
            ;;
        export)
            if [ $# -lt 2 ]; then
                log_error "Export format required"
                show_usage
                exit 1
            fi
            export_data "$2"
            ;;
        archive)
            archive_old_files "${2:-7}"
            ;;
        init)
            init_stats
            log_success "Logging system initialized"
            ;;
        help|--help|-h)
            show_usage
            ;;
        *)
            log_error "Unknown command: ${1:-}"
            show_usage
            exit 1
            ;;
    esac
}

# Ensure required directories exist
mkdir -p "${UMEMORY}/moves" "${UMEMORY}/state" "${UMEMORY}/logs" "${UMEMORY}/exports" "${UMEMORY}/archive"

# Initialize stats if needed
if [ ! -f "$STATS_FILE" ]; then
    init_stats
fi

# Run main function
main "$@"
