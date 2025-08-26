#!/bin/bash
# uDOS Simple Development Mode Launcher
# Streamlined development without VS Code CLI dependencies

set -euo pipefail

UDOS_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/../../.." && pwd)"
export UDOS_ROOT
export UDOS_MODE="vscode-dev"

# Colors
readonly GREEN='\033[0;32m'
readonly BLUE='\033[0;34m'
readonly YELLOW='\033[1;33m'
readonly RED='\033[0;31m'
readonly WHITE='\033[1;37m'
readonly NC='\033[0m'

echo -e "${WHITE}🧙‍♂️ uDOS Simple Development Mode${NC}"
echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"

# Start development server in background
start_dev_server() {
    echo -e "${BLUE}🚀 Starting uDOS development server...${NC}"

    cd "$UDOS_ROOT"

    # Kill any existing server
    pkill -f "uNETWORK/server/server.py" 2>/dev/null || true

    # Activate Python virtual environment
    source "$UDOS_ROOT/uSCRIPT/activate-venv.sh"

    # Start server with development flags
    export UDOS_CURRENT_ROLE="wizard"
    export UDOS_ACCESS_LEVEL="100"
    export UDOS_DEV_MODE="true"

    python "$UDOS_ROOT/uNETWORK/server/server.py" &
    SERVER_PID=$!
    echo $SERVER_PID > /tmp/udos-dev-server.pid

    # Wait for server to start
    local attempts=0
    while [[ $attempts -lt 15 ]]; do
        if curl -s http://localhost:8080/api/status >/dev/null 2>&1; then
            echo -e "${GREEN}✅ Development server running on http://localhost:8080${NC}"
            return 0
        fi
        echo -e "${YELLOW}⏳ Waiting for server... ($((attempts + 1))/15)${NC}"
        sleep 1
        ((attempts++))
    done

    echo -e "${RED}❌ Failed to start development server${NC}"
    return 1
}

# Stop development server
stop_dev_server() {
    echo -e "${YELLOW}🛑 Stopping development server...${NC}"

    # Kill server process
    if [ -f /tmp/udos-dev-server.pid ]; then
        local pid=$(cat /tmp/udos-dev-server.pid)
        kill -TERM $pid 2>/dev/null || kill -9 $pid 2>/dev/null || true
        rm -f /tmp/udos-dev-server.pid
    fi

    # Also kill any remaining python server processes
    pkill -f "uNETWORK/server/server.py" 2>/dev/null || true

    echo -e "${GREEN}✅ Development server stopped${NC}"
}

# Show development info
show_dev_info() {
    echo ""
    echo -e "${WHITE}🖥️ uDOS Development Environment Ready${NC}"
    echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
    echo -e "${YELLOW}🌐 Server: http://localhost:8080${NC}"
    echo -e "${YELLOW}🔧 API: http://localhost:8080/api/status${NC}"
    echo -e "${YELLOW}📁 Project: $UDOS_ROOT${NC}"
    echo -e "${YELLOW}🧙‍♂️ Role: Wizard (Development Mode)${NC}"
    echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
    echo ""
    echo -e "${WHITE}Next steps:${NC}"
    echo "1. Open VS Code manually: ${YELLOW}open -a 'Visual Studio Code' '$UDOS_ROOT'${NC}"
    echo "2. Open browser to: ${YELLOW}http://localhost:8080${NC}"
    echo "3. Install VS Code CLI tools if needed: Cmd+Shift+P > 'Shell Command: Install code command in PATH'"
    echo ""
    echo -e "${WHITE}Development commands:${NC}"
    echo "  s | status     - Show server status"
    echo "  r | restart    - Restart development server"
    echo "  u | ui         - Open UI in browser"
    echo "  q | quit       - Stop development server"
    echo ""

    dev_cli_loop
}

# Development CLI command loop
dev_cli_loop() {
    while true; do
        read -p "🧙‍♂️ uDOS-DEV> " -r command args

        case "$command" in
            "status"|"s")
                show_status
                ;;
            "restart"|"r")
                restart_dev_server
                ;;
            "ui"|"u")
                open http://localhost:8080
                echo -e "${GREEN}✅ UI opened in browser${NC}"
                ;;
            "quit"|"q"|"exit")
                stop_dev_server
                break
                ;;
            "help"|"h"|"")
                echo "Commands: status(s), restart(r), ui(u), quit(q)"
                ;;
            *)
                echo -e "${RED}Unknown command: $command${NC} (try 'help')"
                ;;
        esac
    done
}

# Show development status
show_status() {
    echo -e "${BLUE}📊 Development Status:${NC}"
    echo "─────────────────────────────"

    # Check server
    if curl -s http://localhost:8080/api/status >/dev/null 2>&1; then
        echo -e "🟢 Server: ${GREEN}Running on port 8080${NC}"
    else
        echo -e "🔴 Server: ${RED}Not responding${NC}"
    fi

    # Check files
    if [ -f "$UDOS_ROOT/uNETWORK/server/server.py" ]; then
        echo -e "🟢 Server File: ${GREEN}Available${NC}"
    else
        echo -e "🔴 Server File: ${RED}Missing${NC}"
    fi

    echo -e "📁 Working directory: ${YELLOW}$PWD${NC}"
    echo -e "🧙‍♂️ Role: ${WHITE}Wizard (Development Mode)${NC}"
}

# Restart development server
restart_dev_server() {
    echo -e "${YELLOW}🔄 Restarting development server...${NC}"
    stop_dev_server
    sleep 1
    start_dev_server
    echo -e "${GREEN}✅ Development server restarted${NC}"
}

# Cleanup on exit
cleanup() {
    echo -e "\n${YELLOW}🧹 Cleaning up development session...${NC}"
    stop_dev_server
    echo -e "${WHITE}👋 uDOS Development session ended${NC}"
}

trap cleanup EXIT INT TERM

# Main execution
main() {
    echo -e "${BLUE}🔧 Initializing uDOS Development Environment...${NC}"

    # Start development server
    start_dev_server || {
        echo -e "${RED}❌ Failed to start development server${NC}"
        exit 1
    }

    # Show development info and start CLI
    show_dev_info
}

# Execute main function
main "$@"
