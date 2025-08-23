#!/bin/bash
# uNETWORK Server Management Script
# Provides easy server management commands

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
SERVER_SCRIPT="$SCRIPT_DIR/start-server.sh"
SERVER_PID_FILE="/tmp/udos-server.pid"

# Colors
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

show_status() {
    echo -e "${BLUE}uDOS Server Status${NC}"
    echo "=================="

    if [[ -f "$SERVER_PID_FILE" ]]; then
        local pid=$(cat "$SERVER_PID_FILE")
        if ps -p "$pid" > /dev/null 2>&1; then
            echo -e "${GREEN}✅ Server is running (PID: $pid)${NC}"
            echo "URL: http://127.0.0.1:8080"
        else
            echo -e "${RED}❌ Server PID file exists but process is not running${NC}"
            rm -f "$SERVER_PID_FILE"
        fi
    else
        echo -e "${YELLOW}⚠️ Server is not running${NC}"
    fi

    echo
    echo "Logs:"
    if [[ -f "$SCRIPT_DIR/server.log" ]]; then
        echo "  📄 $SCRIPT_DIR/server.log ($(wc -l < "$SCRIPT_DIR/server.log") lines)"
    else
        echo "  📄 No log file found"
    fi
}

start_server() {
    echo -e "${BLUE}Starting uDOS Server...${NC}"
    cd "$SCRIPT_DIR"
    ./start-server.sh
}

stop_server() {
    echo -e "${BLUE}Stopping uDOS Server...${NC}"

    if [[ -f "$SERVER_PID_FILE" ]]; then
        local pid=$(cat "$SERVER_PID_FILE")
        if ps -p "$pid" > /dev/null 2>&1; then
            kill "$pid"
            echo -e "${GREEN}✅ Server stopped${NC}"
            rm -f "$SERVER_PID_FILE"
        else
            echo -e "${YELLOW}⚠️ Server was not running${NC}"
            rm -f "$SERVER_PID_FILE"
        fi
    else
        # Fallback: kill by process name
        pkill -f "uNETWORK/server/server.py" && echo -e "${GREEN}✅ Server stopped${NC}" || echo -e "${YELLOW}⚠️ No server process found${NC}"
    fi
}

restart_server() {
    echo -e "${BLUE}Restarting uDOS Server...${NC}"
    stop_server
    sleep 2
    start_server
}

show_logs() {
    local lines=${1:-50}
    if [[ -f "$SCRIPT_DIR/server.log" ]]; then
        echo -e "${BLUE}Recent server logs (last $lines lines):${NC}"
        echo "=================================="
        tail -n "$lines" "$SCRIPT_DIR/server.log"
    else
        echo -e "${YELLOW}⚠️ No log file found at $SCRIPT_DIR/server.log${NC}"
    fi
}

test_server() {
    echo -e "${BLUE}Testing server API...${NC}"
    if command -v python3 >/dev/null 2>&1; then
        cd "$SCRIPT_DIR/examples"
        python3 test-api.py
    else
        echo -e "${RED}❌ Python3 not found - cannot run API tests${NC}"
    fi
}

show_help() {
    echo "uDOS Server Management"
    echo "====================="
    echo
    echo "Usage: $0 <command>"
    echo
    echo "Commands:"
    echo "  status    - Show server status"
    echo "  start     - Start the server"
    echo "  stop      - Stop the server"
    echo "  restart   - Restart the server"
    echo "  logs [N]  - Show recent logs (default: 50 lines)"
    echo "  test      - Test server API endpoints"
    echo "  help      - Show this help"
}

case "${1:-status}" in
    "status")   show_status ;;
    "start")    start_server ;;
    "stop")     stop_server ;;
    "restart")  restart_server ;;
    "logs")     show_logs "$2" ;;
    "test")     test_server ;;
    "help")     show_help ;;
    *)          show_help ;;
esac
