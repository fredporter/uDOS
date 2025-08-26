#!/bin/bash
# uDOS Dashboard v1.0.4.1 - Unified System Status Viewer
# Shows server status, UI, logs, and running components

UDOS_ROOT="${UDOS_ROOT:-$(cd "$(dirname "${BASH_SOURCE[0]}")/../../.." && pwd)}"
UDOS_SERVER_PORT="${UDOS_SERVER_PORT:-8080}"
LOG_FILE="$UDOS_ROOT/uNETWORK/server/server.log"

RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
CYAN='\033[0;36m'
NC='\033[0m'
BOLD='\033[1m'

# Server status
function show_server_status() {
    echo -e "${BOLD}${BLUE}uSERVER Status${NC}"
    if curl -s "http://127.0.0.1:${UDOS_SERVER_PORT}/api/status" >/dev/null 2>&1; then
        echo -e "${GREEN}✅ Running on port ${UDOS_SERVER_PORT}${NC}"
        echo -e "${CYAN}URL: http://localhost:${UDOS_SERVER_PORT}${NC}"
    else
        echo -e "${RED}❌ Not running${NC}"
    fi
    echo
}

# UI status
function show_ui_status() {
    echo -e "${BOLD}${BLUE}UI Status${NC}"
    echo -e "${CYAN}Open in browser: http://localhost:${UDOS_SERVER_PORT}${NC}"
    echo
}

# Show recent logs
function show_logs() {
    echo -e "${BOLD}${BLUE}Recent Server Logs${NC}"
    if [ -f "$LOG_FILE" ]; then
        tail -20 "$LOG_FILE"
    else
        echo "No log file found."
    fi
    echo
}

# Show running processes
function show_processes() {
    echo -e "${BOLD}${BLUE}uDOS Processes${NC}"
    ps aux | grep -E 'server.py|start-udos.sh' | grep -v grep
    echo
}

# Main dashboard
clear
cat <<EOF
${BOLD}${CYAN}🌀 uDOS Dashboard v1.0.4.1${NC}
========================================
EOF
show_server_status
show_ui_status
show_logs
show_processes
cat <<EOF
========================================
${YELLOW}Tip: Open http://localhost:${UDOS_SERVER_PORT} in your browser for the UI.${NC}
EOF
