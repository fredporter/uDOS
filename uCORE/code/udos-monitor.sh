#!/bin/bash
# uDOS System Monitor v1.0.4.1 - Simple Process Monitor
# Lightweight monitoring for uDOS background services
# Location: uCORE/code/udos-monitor.sh

set -euo pipefail

# Get script directory and uDOS root
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
UDOS_ROOT="$(cd "$SCRIPT_DIR/../.." && pwd)"

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
NC='\033[0m'

# Check if process is running by PID
is_running() {
    local pid="$1"
    [ -n "$pid" ] && kill -0 "$pid" 2>/dev/null
}

# Get process CPU and memory usage
get_process_stats() {
    local pid="$1"
    if is_running "$pid"; then
        local cpu=$(ps -p "$pid" -o %cpu= 2>/dev/null | tr -d ' ' || echo "0")
        local mem=$(ps -p "$pid" -o %mem= 2>/dev/null | tr -d ' ' || echo "0")
        echo "$cpu $mem"
    else
        echo "0 0"
    fi
}

# Check uDOS Server
check_server() {
    local pid=$(pgrep -f "server.py" 2>/dev/null | head -1 || echo "")
    if [ -n "$pid" ]; then
        local stats=$(get_process_stats "$pid")
        echo "running $pid $stats"
    else
        echo "stopped 0 0 0"
    fi
}

# Check VS Code
check_vscode() {
    local pid=$(pgrep -f "Visual Studio Code" 2>/dev/null | head -1 || echo "")
    if [ -n "$pid" ]; then
        local stats=$(get_process_stats "$pid")
        echo "running $pid $stats"
    else
        echo "stopped 0 0 0"
    fi
}

# Count uDOS processes
count_udos_processes() {
    pgrep -f "uDOS\|uCORE\|uNETWORK\|uSCRIPT" 2>/dev/null | wc -l | tr -d ' '
}

# Get system load
get_system_load() {
    uptime | awk -F'load average:' '{print $2}' | awk '{print $1}' | sed 's/,//' | tr -d ' ' || echo "0.0"
}

# Show status
show_status() {
    # Get component status
    local server_info=$(check_server)
    local vscode_info=$(check_vscode)
    local udos_count=$(count_udos_processes)
    local sys_load=$(get_system_load)

    # Parse server info
    read -r server_status server_pid server_cpu server_mem <<< "$server_info"
    read -r vscode_status vscode_pid vscode_cpu vscode_mem <<< "$vscode_info"

    # Display dashboard
    echo -e "${BLUE}╔══════════════════════════════════════════════════════════════════╗${NC}"
    echo -e "${BLUE}║${NC}                   ${GREEN}🎯 uDOS System Monitor${NC}                   ${BLUE}║${NC}"
    echo -e "${BLUE}║${NC}                      ${YELLOW}Live Status Dashboard${NC}                   ${BLUE}║${NC}"
    echo -e "${BLUE}╚══════════════════════════════════════════════════════════════════╝${NC}"
    echo ""

    # uDOS Server
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

    # VS Code
    echo -e "${GREEN}💻 VS Code IDE${NC}"
    if [ "$vscode_status" = "running" ]; then
        echo -e "   Status: ${GREEN}●${NC} Running (PID: $vscode_pid)"
        echo -e "   CPU: ${vscode_cpu}% | Memory: ${vscode_mem}%"
    else
        echo -e "   Status: ${YELLOW}●${NC} Not running"
        echo -e "   Start: ${YELLOW}./dev/vscode/start-vscode-dev.sh${NC}"
    fi
    echo ""

    # System Summary
    echo -e "${BLUE}📊 System Summary${NC}"
    echo -e "   uDOS Processes: $udos_count"
    echo -e "   System Load: $sys_load"
    echo -e "   Last Updated: $(date)"
}

# Start component
start_component() {
    local component="$1"

    case "$component" in
        server)
            echo -e "${BLUE}[INFO]${NC} Starting uDOS Server..."
            cd "$UDOS_ROOT"
            ./uNETWORK/server/start-server.sh &
            ;;
        vscode)
            echo -e "${BLUE}[INFO]${NC} Starting VS Code..."
            cd "$UDOS_ROOT"
            ./dev/vscode/start-vscode-dev.sh &
            ;;
        *)
            echo -e "${RED}[ERROR]${NC} Unknown component: $component"
            echo "Available: server, vscode"
            return 1
            ;;
    esac
}

# Stop component
stop_component() {
    local component="$1"

    case "$component" in
        server)
            echo -e "${BLUE}[INFO]${NC} Stopping uDOS Server..."
            pkill -f "server.py" 2>/dev/null || true
            ;;
        *)
            echo -e "${RED}[ERROR]${NC} Unknown component: $component"
            return 1
            ;;
    esac
}

# Monitor continuously
monitor_loop() {
    local interval="${1:-5}"

    echo -e "${GREEN}[SUCCESS]${NC} Starting monitoring (${interval}s intervals)"
    echo "Press Ctrl+C to stop"

    trap 'echo -e "\n${BLUE}[INFO]${NC} Monitoring stopped"; exit 0' INT TERM

    while true; do
        clear
        show_status
        echo ""
        echo -e "${YELLOW}Monitoring every ${interval}s - Press Ctrl+C to stop${NC}"
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
    echo "  start <component>   - Start component (server|vscode)"
    echo "  stop <component>    - Stop component (server)"
    echo "  monitor [interval]  - Continuous monitoring (default: 5s)"
    echo ""
    echo "Examples:"
    echo "  $0 status"
    echo "  $0 start server"
    echo "  $0 monitor 10"
}

# Main function
main() {
    local command="${1:-status}"

    case "$command" in
        status)
            show_status
            ;;
        start)
            if [ -z "${2:-}" ]; then
                echo "Usage: $0 start <component>"
                echo "Components: server, vscode"
                exit 1
            fi
            start_component "$2"
            ;;
        stop)
            if [ -z "${2:-}" ]; then
                echo "Usage: $0 stop <component>"
                echo "Components: server"
                exit 1
            fi
            stop_component "$2"
            ;;
        monitor)
            monitor_loop "${2:-5}"
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
