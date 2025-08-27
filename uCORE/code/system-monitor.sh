#!/bin/bash
# uDOS System Monitor v1.0.4.1
# Simple monitoring for uDOS background services and components
# Location: uCORE/code/system-monitor.sh

set -euo pipefail

# Get script directory and uDOS root
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
UDOS_ROOT="$(cd "$SCRIPT_DIR/../.." && pwd)"

# Configuration
MONITOR_DIR="$UDOS_ROOT/sandbox/monitor"
PID_DIR="$MONITOR_DIR/pids"
STATUS_FILE="$MONITOR_DIR/status.json"
LOG_FILE="$UDOS_ROOT/sandbox/logs/system-monitor.log"
USCRIPT_VENV="$UDOS_ROOT/uSCRIPT/venv/python"

# Function to run with venv (only when needed)
run_with_venv() {
    if [ -f "$USCRIPT_VENV/bin/activate" ]; then
        (source "$USCRIPT_VENV/bin/activate" && "$@")
    else
        "$@"
    fi
}

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
NC='\033[0m'

# Logging
log() {
    echo -e "$(date '+%Y-%m-%d %H:%M:%S') $1" | tee -a "$LOG_FILE"
}

# Initialize monitoring
init_monitor() {
    mkdir -p "$MONITOR_DIR" "$PID_DIR"
    log "${BLUE}[INFO]${NC} System monitor initialized"
}

# Check if process is running by PID
is_running() {
    local pid="$1"
    [ -n "$pid" ] && kill -0 "$pid" 2>/dev/null
}

# Get process info
get_process_info() {
    local pid="$1"
    if is_running "$pid"; then
        local cpu=$(ps -p "$pid" -o %cpu= 2>/dev/null | tr -d ' ' || echo "0")
        local mem=$(ps -p "$pid" -o %mem= 2>/dev/null | tr -d ' ' || echo "0")
        local cmd=$(ps -p "$pid" -o comm= 2>/dev/null || echo "unknown")
        echo "running $cpu $mem $cmd"
    else
        echo "stopped 0 0 unknown"
    fi
}

# Monitor uDOS Server
check_server() {
    local server_pid=""

    # Check for Flask server process
    server_pid=$(pgrep -f "uNETWORK/server/server.py" 2>/dev/null | head -1 || echo "")

    if [ -n "$server_pid" ]; then
        local info=$(get_process_info "$server_pid")
        echo "$server_pid $info"
    else
        echo "0 stopped 0 0 server"
    fi
}

# Monitor Health Daemon
check_health_daemon() {
    local daemon_pid=""
    local pid_file="$UDOS_ROOT/sandbox/.health-monitor.pid"

    if [ -f "$pid_file" ]; then
        daemon_pid=$(cat "$pid_file" 2>/dev/null || echo "")
        if is_running "$daemon_pid"; then
            local info=$(get_process_info "$daemon_pid")
            echo "$daemon_pid $info"
        else
            rm -f "$pid_file"
            echo "0 stopped 0 0 health-daemon"
        fi
    else
        echo "0 stopped 0 0 health-daemon"
    fi
}

# Monitor VS Code (if running)
check_vscode() {
    local vscode_pid=$(pgrep -f "Visual Studio Code" 2>/dev/null | head -1 || echo "")

    if [ -n "$vscode_pid" ]; then
        local info=$(get_process_info "$vscode_pid")
        echo "$vscode_pid $info"
    else
        echo "0 stopped 0 0 vscode"
    fi
}

# Monitor other uDOS processes
check_udos_processes() {
    # Check for any uDOS-related background processes
    local processes=$(pgrep -f "uDOS\|uCORE\|uNETWORK\|uSCRIPT" 2>/dev/null || echo "")
    local count=0

    if [ -n "$processes" ]; then
        count=$(echo "$processes" | wc -l | tr -d ' ')
    fi

    echo "$count"
}

# Generate status report
generate_status() {
    local timestamp=$(date -u +%Y-%m-%dT%H:%M:%SZ)

    # Get component status
    local server_status=$(check_server)
    local health_status=$(check_health_daemon)
    local vscode_status=$(check_vscode)
    local udos_process_count=$(check_udos_processes)

    # Parse status data
    read -r server_pid server_state server_cpu server_mem server_cmd <<< "$server_status"
    read -r health_pid health_state health_cpu health_mem health_cmd <<< "$health_status"
    read -r vscode_pid vscode_state vscode_cpu vscode_mem vscode_cmd <<< "$vscode_status"

    # Calculate running components
    local running_count=0
    [ "$server_state" = "running" ] && running_count=$((running_count + 1))
    [ "$health_state" = "running" ] && running_count=$((running_count + 1))
    [ "$vscode_state" = "running" ] && running_count=$((running_count + 1))

    # Get system load
    local system_load=$(uptime | awk -F'load average:' '{print $2}' | awk '{print $1}' | sed 's/,//' || echo '0.0')

    # Create JSON status
    cat > "$STATUS_FILE" <<EOF
{
    "timestamp": "$timestamp",
    "components": {
        "server": {
            "pid": $server_pid,
            "status": "$server_state",
            "cpu_percent": $server_cpu,
            "memory_percent": $server_mem,
            "command": "$server_cmd"
        },
        "health_daemon": {
            "pid": $health_pid,
            "status": "$health_state",
            "cpu_percent": $health_cpu,
            "memory_percent": $health_mem,
            "command": "$health_cmd"
        },
        "vscode": {
            "pid": $vscode_pid,
            "status": "$vscode_state",
            "cpu_percent": $vscode_cpu,
            "memory_percent": $vscode_mem,
            "command": "$vscode_cmd"
        }
    },
    "summary": {
        "total_udos_processes": $udos_process_count,
        "running_components": $running_count,
        "system_load": "$system_load"
    }
}
EOF
}

# Show status dashboard
show_status() {
    generate_status

    if [ ! -f "$STATUS_FILE" ]; then
        log "${RED}[ERROR]${NC} Status file not found"
        return 1
    fi

    local status_data=$(cat "$STATUS_FILE")

    echo -e "${BLUE}╔══════════════════════════════════════════════════════════════════╗${NC}"
    echo -e "${BLUE}║${NC}                   ${GREEN}🎯 uDOS System Monitor${NC}                   ${BLUE}║${NC}"
    echo -e "${BLUE}║${NC}                      ${YELLOW}Live Status Dashboard${NC}                   ${BLUE}║${NC}"
    echo -e "${BLUE}╚══════════════════════════════════════════════════════════════════╝${NC}"
    echo ""

    # Server status
    local server_status=$(echo "$status_data" | jq -r '.components.server.status')
    local server_pid=$(echo "$status_data" | jq -r '.components.server.pid')
    local server_cpu=$(echo "$status_data" | jq -r '.components.server.cpu_percent')
    local server_mem=$(echo "$status_data" | jq -r '.components.server.memory_percent')

    echo -e "${GREEN}🌐 uDOS Server${NC}"
    if [ "$server_status" = "running" ]; then
        echo -e "   Status: ${GREEN}●${NC} Running (PID: $server_pid)"
        echo -e "   CPU: ${server_cpu}% | Memory: ${server_mem}%"
        echo -e "   URL: ${BLUE}http://localhost:8080${NC}"
    else
        echo -e "   Status: ${RED}●${NC} Stopped"
        echo -e "   Start: ${YELLOW}./uNETWORK/server/start-server.sh${NC}"
    fi
    echo ""

    # Health daemon status
    local health_status=$(echo "$status_data" | jq -r '.components.health_daemon.status')
    local health_pid=$(echo "$status_data" | jq -r '.components.health_daemon.pid')

    echo -e "${GREEN}🏥 Health Monitor${NC}"
    if [ "$health_status" = "running" ]; then
        echo -e "   Status: ${GREEN}●${NC} Running (PID: $health_pid)"
    else
        echo -e "   Status: ${RED}●${NC} Stopped"
        echo -e "   Start: ${YELLOW}./uCORE/code/health-monitor-daemon.sh start${NC}"
    fi
    echo ""

    # VS Code status
    local vscode_status=$(echo "$status_data" | jq -r '.components.vscode.status')
    local vscode_pid=$(echo "$status_data" | jq -r '.components.vscode.pid')

    echo -e "${GREEN}💻 VS Code IDE${NC}"
    if [ "$vscode_status" = "running" ]; then
        echo -e "   Status: ${GREEN}●${NC} Running (PID: $vscode_pid)"
    else
        echo -e "   Status: ${YELLOW}●${NC} Not detected"
        echo -e "   Start: ${YELLOW}./dev/vscode/start-vscode-dev.sh${NC}"
    fi
    echo ""

    # System summary
    local total_processes=$(echo "$status_data" | jq -r '.summary.total_udos_processes')
    local system_load=$(echo "$status_data" | jq -r '.summary.system_load')

    echo -e "${BLUE}📊 System Summary${NC}"
    echo -e "   uDOS Processes: $total_processes"
    echo -e "   System Load: $system_load"
    echo -e "   Last Updated: $(date)"
}

# Start a component
start_component() {
    local component="$1"

    case "$component" in
        server)
            log "${BLUE}[INFO]${NC} Starting uDOS Server with venv..."
            # Use the venv launcher in background
            if [ -f "$UDOS_ROOT/uNETWORK/server/launch-with-venv.sh" ]; then
                (cd "$UDOS_ROOT" && nohup ./uNETWORK/server/launch-with-venv.sh > /dev/null 2>&1 &)
            else
                log "${YELLOW}[WARN]${NC} Venv launcher not found, using regular start script"
                (cd "$UDOS_ROOT" && ./uNETWORK/server/start-server.sh --daemon)
            fi
            ;;
        health)
            log "${BLUE}[INFO]${NC} Starting Health Monitor..."
            "$UDOS_ROOT/uCORE/code/health-monitor-daemon.sh" start
            ;;
        vscode)
            log "${BLUE}[INFO]${NC} Starting VS Code Development Environment..."
            cd "$UDOS_ROOT"
            ./dev/vscode/start-vscode-dev.sh &
            ;;
        all)
            start_component server
            sleep 2
            start_component health
            ;;
        *)
            log "${RED}[ERROR]${NC} Unknown component: $component"
            echo "Available components: server, health, vscode, all"
            return 1
            ;;
    esac
}

# Stop a component
stop_component() {
    local component="$1"

    case "$component" in
        server)
            log "${BLUE}[INFO]${NC} Stopping uDOS Server..."
            pkill -f "uNETWORK/server/server.py" 2>/dev/null || true
            ;;
        health)
            log "${BLUE}[INFO]${NC} Stopping Health Monitor..."
            "$UDOS_ROOT/uCORE/code/health-monitor-daemon.sh" stop
            ;;
        vscode)
            log "${YELLOW}[WARNING]${NC} VS Code should be closed manually"
            ;;
        all)
            stop_component server
            stop_component health
            ;;
        *)
            log "${RED}[ERROR]${NC} Unknown component: $component"
            return 1
            ;;
    esac
}

# Monitor continuously
monitor_loop() {
    local interval="${1:-10}"

    log "${GREEN}[SUCCESS]${NC} Starting continuous monitoring (${interval}s intervals)"
    log "Press Ctrl+C to stop"

    trap 'log "${BLUE}[INFO]${NC} Monitoring stopped"; exit 0' INT TERM

    while true; do
        clear
        show_status
        echo ""
        echo "Monitoring every ${interval}s - Press Ctrl+C to stop"
        sleep "$interval"
    done
}

# Show help
show_help() {
    echo "uDOS System Monitor v1.0.4.1"
    echo "Simple monitoring for uDOS background services"
    echo ""
    echo "Commands:"
    echo "  status              - Show current status"
    echo "  start <component>   - Start component (server|health|vscode|all)"
    echo "  stop <component>    - Stop component (server|health|all)"
    echo "  monitor [interval]  - Continuous monitoring (default: 10s)"
    echo "  json               - Output status as JSON"
    echo ""
    echo "Components:"
    echo "  server   - uDOS Flask server (uNETWORK/server/server.py)"
    echo "  health   - Health monitoring daemon"
    echo "  vscode   - VS Code development environment"
    echo "  all      - All manageable components"
}

# Main function
main() {
    local command="${1:-status}"

    # Initialize if needed
    [ ! -d "$MONITOR_DIR" ] && init_monitor

    case "$command" in
        init)
            init_monitor
            ;;
        status)
            show_status
            ;;
        start)
            if [ -z "${2:-}" ]; then
                echo "Usage: $0 start <component>"
                echo "Components: server, health, vscode, all"
                exit 1
            fi
            start_component "$2"
            ;;
        stop)
            if [ -z "${2:-}" ]; then
                echo "Usage: $0 stop <component>"
                echo "Components: server, health, all"
                exit 1
            fi
            stop_component "$2"
            ;;
        monitor)
            monitor_loop "${2:-10}"
            ;;
        json)
            generate_status
            cat "$STATUS_FILE"
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

# Execute main function
main "$@"
