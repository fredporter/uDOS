#!/bin/bash
# uDOS Health Monitor Daemon v1.0.4.1
# Continuous system health monitoring and alerting
# Location: uCORE/code/health-monitor-daemon.sh

set -euo pipefail

# Get script directory and uDOS root
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
UDOS_ROOT="$(cd "$SCRIPT_DIR/../.." && pwd)"
TASK_MANAGER="$SCRIPT_DIR/task-manager.sh"

# Configuration
MONITOR_INTERVAL=30  # seconds
ALERT_THRESHOLD_COUNT=3  # consecutive alerts before escalation
PID_FILE="$UDOS_ROOT/sandbox/.health-monitor.pid"
LOG_FILE="$UDOS_ROOT/sandbox/logs/health-monitor.log"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
NC='\033[0m'

# Logging functions
log_info() {
    echo -e "$(date '+%Y-%m-%d %H:%M:%S') ${BLUE}[INFO]${NC} $1" | tee -a "$LOG_FILE"
}

log_success() {
    echo -e "$(date '+%Y-%m-%d %H:%M:%S') ${GREEN}[SUCCESS]${NC} $1" | tee -a "$LOG_FILE"
}

log_warning() {
    echo -e "$(date '+%Y-%m-%d %H:%M:%S') ${YELLOW}[WARNING]${NC} $1" | tee -a "$LOG_FILE"
}

log_error() {
    echo -e "$(date '+%Y-%m-%d %H:%M:%S') ${RED}[ERROR]${NC} $1" | tee -a "$LOG_FILE"
}

# Alert state tracking
ALERT_STATE_FILE="$UDOS_ROOT/sandbox/health/alert-state.json"
declare -A alert_counts

# Initialize alert state
init_alert_state() {
    mkdir -p "$(dirname "$ALERT_STATE_FILE")"
    if [ ! -f "$ALERT_STATE_FILE" ]; then
        echo '{"cpu": 0, "memory": 0, "disk": 0, "load": 0}' > "$ALERT_STATE_FILE"
    fi

    # Load existing alert counts
    if [ -f "$ALERT_STATE_FILE" ]; then
        alert_counts[cpu]=$(jq -r '.cpu' "$ALERT_STATE_FILE")
        alert_counts[memory]=$(jq -r '.memory' "$ALERT_STATE_FILE")
        alert_counts[disk]=$(jq -r '.disk' "$ALERT_STATE_FILE")
        alert_counts[load]=$(jq -r '.load' "$ALERT_STATE_FILE")
    fi
}

# Update alert state
update_alert_state() {
    local component="$1"
    local count="$2"

    alert_counts[$component]=$count

    local alert_json=$(cat <<EOF
{
    "cpu": ${alert_counts[cpu]},
    "memory": ${alert_counts[memory]},
    "disk": ${alert_counts[disk]},
    "load": ${alert_counts[load]}
}
EOF
    )

    echo "$alert_json" > "$ALERT_STATE_FILE"
}

# Check if daemon is already running
check_running() {
    if [ -f "$PID_FILE" ]; then
        local pid=$(cat "$PID_FILE")
        if kill -0 "$pid" 2>/dev/null; then
            return 0  # Running
        else
            rm -f "$PID_FILE"
            return 1  # Not running
        fi
    fi
    return 1  # Not running
}

# Start daemon
start_daemon() {
    if check_running; then
        log_warning "Health monitor daemon is already running (PID: $(cat "$PID_FILE"))"
        return 1
    fi

    log_info "Starting uDOS Health Monitor Daemon..."

    # Create log directory
    mkdir -p "$(dirname "$LOG_FILE")"

    # Initialize alert state
    init_alert_state

    # Start daemon in background
    (
        echo $$ > "$PID_FILE"
        monitor_loop
    ) &

    local daemon_pid=$!
    sleep 1

    if kill -0 "$daemon_pid" 2>/dev/null; then
        log_success "Health monitor daemon started (PID: $daemon_pid)"
    else
        log_error "Failed to start health monitor daemon"
        rm -f "$PID_FILE"
        return 1
    fi
}

# Stop daemon
stop_daemon() {
    if [ -f "$PID_FILE" ]; then
        local pid=$(cat "$PID_FILE")
        if kill -0 "$pid" 2>/dev/null; then
            kill -TERM "$pid"
            sleep 2
            if kill -0 "$pid" 2>/dev/null; then
                kill -KILL "$pid"
            fi
            rm -f "$PID_FILE"
            log_success "Health monitor daemon stopped"
        else
            log_warning "Daemon PID file exists but process not running"
            rm -f "$PID_FILE"
        fi
    else
        log_warning "Health monitor daemon is not running"
    fi
}

# Restart daemon
restart_daemon() {
    log_info "Restarting health monitor daemon..."
    stop_daemon
    sleep 2
    start_daemon
}

# Main monitoring loop
monitor_loop() {
    log_info "Health monitor daemon started - monitoring every ${MONITOR_INTERVAL}s"

    # Trap signals for clean shutdown
    trap 'log_info "Received shutdown signal"; cleanup_and_exit' TERM INT

    while true; do
        # Collect system metrics
        if ! "$TASK_MANAGER" metrics >/dev/null 2>&1; then
            log_error "Failed to collect system metrics"
        fi

        # Process scheduled tasks
        if ! "$TASK_MANAGER" cron >/dev/null 2>&1; then
            log_warning "Failed to process scheduled tasks"
        fi

        # Check health status and handle alerts
        check_health_and_alert

        # Sleep for next iteration
        sleep "$MONITOR_INTERVAL"
    done
}

# Check health status and handle alerts
check_health_and_alert() {
    local health_file="$UDOS_ROOT/sandbox/health/status.json"

    if [ ! -f "$health_file" ]; then
        log_warning "Health status file not found"
        return
    fi

    local health_data=$(cat "$health_file")
    local overall_status=$(echo "$health_data" | jq -r '.overall_status')

    # Check individual components
    local cpu_status=$(echo "$health_data" | jq -r '.component_status.cpu // "normal"')
    local memory_status=$(echo "$health_data" | jq -r '.component_status.memory // "normal"')
    local disk_status=$(echo "$health_data" | jq -r '.component_status.disk // "normal"')
    local load_status=$(echo "$health_data" | jq -r '.component_status.load // "normal"')

    # Process alerts for each component
    process_component_alert "cpu" "$cpu_status"
    process_component_alert "memory" "$memory_status"
    process_component_alert "disk" "$disk_status"
    process_component_alert "load" "$load_status"

    # Overall system alert
    if [ "$overall_status" = "critical" ]; then
        send_critical_alert "System is in critical state"
    fi
}

# Process individual component alerts
process_component_alert() {
    local component="$1"
    local status="$2"

    if [ "$status" = "warning" ] || [ "$status" = "critical" ]; then
        # Increment alert count
        local current_count=${alert_counts[$component]}
        local new_count=$((current_count + 1))
        update_alert_state "$component" "$new_count"

        # Check if threshold reached
        if [ "$new_count" -ge "$ALERT_THRESHOLD_COUNT" ]; then
            send_escalated_alert "$component" "$status" "$new_count"
            # Reset count after escalation
            update_alert_state "$component" 0
        else
            log_warning "${component^^} $status ($new_count/$ALERT_THRESHOLD_COUNT)"
        fi
    else
        # Reset count for normal status
        if [ "${alert_counts[$component]}" -gt 0 ]; then
            log_info "${component^^} returned to normal"
            update_alert_state "$component" 0
        fi
    fi
}

# Send escalated alert
send_escalated_alert() {
    local component="$1"
    local status="$2"
    local count="$3"

    local alert_message="${component^^} has been in $status state for $count consecutive checks"
    log_error "ALERT ESCALATED: $alert_message"

    # Create alert task for notification
    local alert_task_name="Health Alert: ${component^^} $status"
    local alert_command="echo 'HEALTH ALERT: $alert_message' >> $UDOS_ROOT/sandbox/health/alerts/$(date +%Y%m%d_%H%M%S)_${component}_alert.txt"

    # Ensure alerts directory exists
    mkdir -p "$UDOS_ROOT/sandbox/health/alerts"

    # Create notification task
    if command -v "$TASK_MANAGER" >/dev/null 2>&1; then
        "$TASK_MANAGER" create "$alert_task_name" "$alert_command" "alert" >/dev/null 2>&1 || true
    fi

    # Additional notification methods can be added here
    # - Email notifications
    # - Slack/Discord webhooks
    # - System notifications
    # - Log forwarding
}

# Send critical alert
send_critical_alert() {
    local message="$1"
    log_error "CRITICAL ALERT: $message"

    # Create critical alert file
    local critical_alert_file="$UDOS_ROOT/sandbox/health/alerts/CRITICAL_$(date +%Y%m%d_%H%M%S).txt"
    mkdir -p "$(dirname "$critical_alert_file")"

    cat > "$critical_alert_file" <<EOF
CRITICAL SYSTEM ALERT
====================
Time: $(date)
Message: $message

System Status:
$(cat "$UDOS_ROOT/sandbox/health/status.json" 2>/dev/null || echo "Status unavailable")

Action Required: Immediate attention needed
EOF

    # Flash alert to console if interactive
    if [ -t 1 ]; then
        for i in {1..3}; do
            echo -e "\a${RED}🚨 CRITICAL SYSTEM ALERT 🚨${NC}"
            sleep 1
        done
    fi
}

# Cleanup and exit
cleanup_and_exit() {
    log_info "Health monitor daemon shutting down..."
    rm -f "$PID_FILE"
    exit 0
}

# Show daemon status
show_status() {
    if check_running; then
        local pid=$(cat "$PID_FILE")
        local uptime_seconds=$(ps -o etime= -p "$pid" 2>/dev/null | tr -d ' ' || echo "unknown")
        echo -e "${GREEN}●${NC} Health monitor daemon is running (PID: $pid)"
        echo "   Uptime: $uptime_seconds"
        echo "   Log file: $LOG_FILE"
        echo "   Monitor interval: ${MONITOR_INTERVAL}s"
    else
        echo -e "${RED}●${NC} Health monitor daemon is not running"
    fi
}

# Show recent logs
show_logs() {
    local lines="${1:-20}"
    if [ -f "$LOG_FILE" ]; then
        echo "Last $lines lines from health monitor log:"
        echo "═══════════════════════════════════════════════"
        tail -n "$lines" "$LOG_FILE"
    else
        echo "No log file found: $LOG_FILE"
    fi
}

# Show help
show_help() {
    echo "uDOS Health Monitor Daemon v1.0.4.1"
    echo "Continuous system health monitoring and alerting"
    echo ""
    echo "Commands:"
    echo "  start     - Start the health monitor daemon"
    echo "  stop      - Stop the health monitor daemon"
    echo "  restart   - Restart the health monitor daemon"
    echo "  status    - Show daemon status"
    echo "  logs [n]  - Show last n lines of logs (default: 20)"
    echo "  config    - Show configuration"
    echo ""
    echo "Configuration:"
    echo "  Monitor interval: ${MONITOR_INTERVAL}s"
    echo "  Alert threshold: $ALERT_THRESHOLD_COUNT consecutive alerts"
    echo "  PID file: $PID_FILE"
    echo "  Log file: $LOG_FILE"
}

# Show configuration
show_config() {
    echo "uDOS Health Monitor Daemon Configuration"
    echo "═══════════════════════════════════════════════"
    echo "Monitor interval: ${MONITOR_INTERVAL}s"
    echo "Alert threshold: $ALERT_THRESHOLD_COUNT consecutive alerts"
    echo "PID file: $PID_FILE"
    echo "Log file: $LOG_FILE"
    echo "Task manager: $TASK_MANAGER"
    echo "Alert state file: $ALERT_STATE_FILE"
    echo ""
    echo "Directory structure:"
    echo "  Health data: $UDOS_ROOT/sandbox/health/"
    echo "  Metrics: $UDOS_ROOT/sandbox/metrics/"
    echo "  Tasks: $UDOS_ROOT/sandbox/tasks/"
    echo "  Logs: $UDOS_ROOT/sandbox/logs/"
}

# Main function
main() {
    local command="${1:-help}"

    case "$command" in
        start)
            start_daemon
            ;;
        stop)
            stop_daemon
            ;;
        restart)
            restart_daemon
            ;;
        status)
            show_status
            ;;
        logs)
            show_logs "$2"
            ;;
        config)
            show_config
            ;;
        help|--help|-h)
            show_help
            ;;
        *)
            echo "Unknown command: $command"
            show_help
            exit 1
            ;;
    esac
}

# Check dependencies
if ! command -v jq >/dev/null 2>&1; then
    log_error "jq is required but not installed"
    exit 1
fi

if [ ! -f "$TASK_MANAGER" ]; then
    log_error "Task manager not found: $TASK_MANAGER"
    exit 1
fi

# Execute main function
main "$@"
