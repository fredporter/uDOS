#
# uDOS Ethos: Clean, flat, minimal data. Respect host system. Backup and cleanup always.
#
#!/bin/bash
# uDOS Health Monitor v1.3.1 - Continuous System Monitoring
set -euo pipefail

UDOS_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"

# Load error handler if available (avoid variable conflicts)
if [[ -f "$UDOS_ROOT/uCORE/system/error-handler.sh" ]]; then
    # Source without conflicting variables
    (source "$UDOS_ROOT/uCORE/system/error-handler.sh" >/dev/null 2>&1) || true
fi

# Monitoring configuration
MONITOR_INTERVAL=30
HEALTH_CHECK_URL="http://127.0.0.1:8080/api/health"
LOG_FILE="$UDOS_ROOT/wizard/logs/monitoring/health-monitor-$(date +%Y%m%d).log"
PID_FILE="/tmp/udos-health-monitor.pid"

# Thresholds
CPU_THRESHOLD=80
MEMORY_THRESHOLD=80
ERROR_THRESHOLD=5
RESTART_THRESHOLD=3

# Colors
readonly H_RED='\033[0;31m'
readonly H_GREEN='\033[0;32m'
readonly H_YELLOW='\033[1;33m'
readonly H_BLUE='\033[0;34m'
readonly H_WHITE='\033[1;37m'
readonly H_NC='\033[0m'

# Ensure monitoring log directory exists
mkdir -p "$(dirname "$LOG_FILE")"

# Initialize logging (simplified - no external dependencies)
touch "$LOG_FILE"

log_health() {
    local level="$1"
    local message="$2"
    local timestamp=$(date '+%Y-%m-%d %H:%M:%S')

    echo "[$timestamp] [$level] $message" >> "$LOG_FILE"

    if [[ "${UDOS_DEV_MODE:-false}" == "true" ]]; then
        echo -e "${H_WHITE}[$timestamp]${H_NC} $message"
    fi
}

check_server_health() {
    local health_status="unknown"
    local error_count=0
    local uptime=0

    # Try to get health data from server
    if command -v curl >/dev/null 2>&1; then
        local health_response=$(curl -s "$HEALTH_CHECK_URL" 2>/dev/null || echo '{"status":"unreachable"}')

        if echo "$health_response" | grep -q '"status"'; then
            health_status=$(echo "$health_response" | grep -o '"status":"[^"]*"' | cut -d'"' -f4)
            error_count=$(echo "$health_response" | grep -o '"error_count":[0-9]*' | cut -d':' -f2 || echo "0")
            uptime=$(echo "$health_response" | grep -o '"uptime":[0-9.]*' | cut -d':' -f2 || echo "0")
        else
            health_status="unreachable"
        fi
    else
        health_status="no_curl"
    fi

    echo "$health_status $error_count $uptime"
}

check_system_resources() {
    # CPU usage
    local cpu_usage=$(top -l 1 -n 0 | grep "CPU usage" | awk '{print $3}' | sed 's/%//' 2>/dev/null || echo "0")

    # Memory usage
    local memory_info=$(vm_stat 2>/dev/null)
    local pages_free=$(echo "$memory_info" | grep "Pages free" | awk '{print $3}' | sed 's/\.//')
    local pages_active=$(echo "$memory_info" | grep "Pages active" | awk '{print $3}' | sed 's/\.//')
    local pages_inactive=$(echo "$memory_info" | grep "Pages inactive" | awk '{print $3}' | sed 's/\.//')
    local pages_wired=$(echo "$memory_info" | grep "Pages wired down" | awk '{print $4}' | sed 's/\.//')

    local total_pages=$((pages_free + pages_active + pages_inactive + pages_wired))
    local used_pages=$((pages_active + pages_inactive + pages_wired))
    local memory_usage=0

    if [[ $total_pages -gt 0 ]]; then
        memory_usage=$((used_pages * 100 / total_pages))
    fi

    # Disk usage
    local disk_usage=$(df . | tail -1 | awk '{print $5}' | sed 's/%//')

    echo "$cpu_usage $memory_usage $disk_usage"
}

check_processes() {
    local server_running=false
    local process_count=0

    # Check for uDOS server
    if pgrep -f "uSERVER/server.py" >/dev/null; then
        server_running=true
    fi

    # Count uDOS related processes
    process_count=$(pgrep -f "udos\|uSERVER" | wc -l || echo "0")

    echo "$server_running $process_count"
}

generate_health_report() {
    local timestamp=$(date '+%Y-%m-%d %H:%M:%S')

    # Get health data
    read -r health_status error_count uptime <<< "$(check_server_health)"
    read -r cpu_usage memory_usage disk_usage <<< "$(check_system_resources)"
    read -r server_running process_count <<< "$(check_processes)"

    # System overload check
    local overload="normal"
    if [[ $cpu_usage -gt $CPU_THRESHOLD || $memory_usage -gt $MEMORY_THRESHOLD || $disk_usage -gt 90 ]]; then
        overload="overload"
    fi

    # Create health report
    cat >> "$LOG_FILE" << EOF
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
HEALTH REPORT: $timestamp
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Server Status: $health_status
Server Running: $server_running
Error Count: $error_count
Uptime: ${uptime}s
CPU Usage: ${cpu_usage}%
Memory Usage: ${memory_usage}%
Disk Usage: ${disk_usage}%
Process Count: $process_count
Role: ${UDOS_CURRENT_ROLE:-unknown}
System Overload: $overload
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

EOF

    # Check for issues and alert
    local issues=()

    if [[ "$health_status" == "critical" ]]; then
        issues+=("Server health critical")
    elif [[ "$health_status" == "unreachable" ]]; then
        issues+=("Server unreachable")
    fi

    if [[ "$server_running" == "false" ]]; then
        issues+=("Server not running")
    fi

    if [[ $error_count -gt $ERROR_THRESHOLD ]]; then
        issues+=("High error count: $error_count")
    fi

    if [[ ${cpu_usage%.*} -gt $CPU_THRESHOLD ]]; then
        issues+=("High CPU usage: ${cpu_usage}%")
    fi

    if [[ $memory_usage -gt $MEMORY_THRESHOLD ]]; then
        issues+=("High memory usage: ${memory_usage}%")
    fi

    if [[ $disk_usage -gt 90 ]]; then
        issues+=("Low disk space: ${disk_usage}%")
    fi

    if [[ "$overload" == "overload" ]]; then
        issues+=("System overload detected")
    fi

    # Report issues
    if [[ ${#issues[@]} -gt 0 ]]; then
        log_health "WARNING" "🔍 System health issues detected"

        for issue in "${issues[@]}"; do
            log_health "ISSUE" "$issue"

            # Log critical issues to error system if available
            if [[ "$issue" == *"critical"* || "$issue" == *"unreachable"* || "$issue" == *"not running"* ]]; then
                if command -v "$UDOS_ROOT/uCORE/system/error-handler.sh" >/dev/null 2>&1; then
                    echo "HEALTH_CRITICAL|$(date +%s)|$issue" >> "$UDOS_ROOT/wizard/logs/errors/health-critical-$(date +%Y%m%d).log"
                fi
            fi
        done

        # Take corrective action for critical issues
        if [[ "$server_running" == "false" && "$health_status" != "unreachable" ]]; then
            log_health "ACTION" "Attempting to restart server"
            attempt_server_restart
        fi
    else
        log_health "INFO" "All systems healthy"
    fi
}

attempt_server_restart() {
    log_health "ACTION" "🔄 Attempting server restart due to health issues"

    # Simple restart loop detection
    local restart_log="/tmp/udos-health-restarts.log"
    local current_time=$(date +%s)
    local restart_window=300  # 5 minutes

    # Clean old restart entries
    if [[ -f "$restart_log" ]]; then
        local temp_log=$(mktemp)
        while IFS= read -r line; do
            local restart_time=$(echo "$line" | cut -d'|' -f1)
            if [[ $((current_time - restart_time)) -lt $restart_window ]]; then
                echo "$line" >> "$temp_log"
            fi
        done < "$restart_log"
        mv "$temp_log" "$restart_log"
    fi

    # Count recent restarts
    local restart_count=0
    if [[ -f "$restart_log" ]]; then
        restart_count=$(wc -l < "$restart_log")
    fi

    if [[ $restart_count -ge $RESTART_THRESHOLD ]]; then
        log_health "ERROR" "Too many recent restarts ($restart_count), aborting automatic restart"
        return 1
    fi

    # Log this restart attempt
    echo "${current_time}|health-monitor" >> "$restart_log"

    # Attempt restart
    if [[ -f "$UDOS_ROOT/uSERVER/start-server.sh" ]]; then
        "$UDOS_ROOT/uSERVER/start-server.sh" restart &
        log_health "ACTION" "Server restart initiated"

        # Wait a bit and check if it worked
        sleep 10
        if pgrep -f "uSERVER/server.py" >/dev/null; then
            log_health "SUCCESS" "Server restart successful"
            reset_loop_detection
        else
            log_health "ERROR" "Server restart failed"
        fi
    else
        log_health "ERROR" "Server start script not found"
    fi
}

start_monitoring() {
    # Check if already running
    if [[ -f "$PID_FILE" ]]; then
        local existing_pid=$(cat "$PID_FILE")
        if kill -0 "$existing_pid" 2>/dev/null; then
            echo -e "${H_YELLOW}Health monitor already running (PID: $existing_pid)${H_NC}"
            exit 1
        else
            rm -f "$PID_FILE"
        fi
    fi

    # Create PID file
    echo $$ > "$PID_FILE"

    # Set up cleanup
    trap 'cleanup_monitor' EXIT INT TERM

    echo -e "${H_GREEN}🔍 Starting uDOS Health Monitor v1.3.1${H_NC}"
    log_health "INFO" "Health monitor started (PID: $$)"

    # Main monitoring loop
    while true; do
        generate_health_report
        sleep "$MONITOR_INTERVAL"
    done
}

stop_monitoring() {
    if [[ -f "$PID_FILE" ]]; then
        local pid=$(cat "$PID_FILE")
        if kill -0 "$pid" 2>/dev/null; then
            kill "$pid"
            rm -f "$PID_FILE"
            echo -e "${H_GREEN}Health monitor stopped${H_NC}"
        else
            echo -e "${H_YELLOW}Health monitor not running${H_NC}"
            rm -f "$PID_FILE"
        fi
    else
        echo -e "${H_YELLOW}Health monitor not running${H_NC}"
    fi
}

show_status() {
    if [[ -f "$PID_FILE" ]]; then
        local pid=$(cat "$PID_FILE")
        if kill -0 "$pid" 2>/dev/null; then
            echo -e "${H_GREEN}✅ Health monitor running (PID: $pid)${H_NC}"

            # Show recent health summary
            if [[ -f "$LOG_FILE" ]]; then
                echo -e "${H_BLUE}Recent health checks:${H_NC}"
                tail -10 "$LOG_FILE" | grep -E "(HEALTH REPORT|ISSUE|WARNING)" | tail -5
            fi
        else
            echo -e "${H_RED}❌ Health monitor not running (stale PID file)${H_NC}"
            rm -f "$PID_FILE"
        fi
    else
        echo -e "${H_RED}❌ Health monitor not running${H_NC}"
    fi
}

cleanup_monitor() {
    log_health "INFO" "Health monitor stopping (PID: $$)"
    rm -f "$PID_FILE"
}

show_help() {
    echo "uDOS Health Monitor v1.3.1"
    echo ""
    echo "Usage: $0 [COMMAND]"
    echo ""
    echo "Commands:"
    echo "  start     Start health monitoring (default)"
    echo "  stop      Stop health monitoring"
    echo "  status    Show monitor status"
    echo "  report    Generate immediate health report"
    echo "  logs      Show recent health logs"
    echo "  help      Show this help"
}

# Main execution
case "${1:-start}" in
    "start")
        start_monitoring
        ;;
    "stop")
        stop_monitoring
        ;;
    "status")
        show_status
        ;;
    "report")
        generate_health_report
        echo "Health report generated: $LOG_FILE"
        ;;
    "logs")
        if [[ -f "$LOG_FILE" ]]; then
            tail -20 "$LOG_FILE"
        else
            echo "No health logs found"
        fi
        ;;
    "help")
        show_help
        ;;
    *)
        echo "Unknown command: $1"
        show_help
        exit 1
        ;;
esac
