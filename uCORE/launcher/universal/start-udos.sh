#!/bin/bash
# uDOS Universal Startup Script v1.3.1 - Enhanced CLI with Background Server
# Keeps server running while providing interactive CLI with status and options

set -euo pipefail

# Configuration
export UDOS_ROOT="${UDOS_ROOT:-$(cd "$(dirname "${BASH_SOURCE[0]}")/../../../" && pwd)}"
export UDOS_VERSION="1.3.1"
export UDOS_UI_PORT="${UDOS_UI_PORT:-8080}"
export UDOS_SERVER_PORT="${UDOS_SERVER_PORT:-8080}"

# Color definitions
readonly RED='\033[0;31m'
readonly GREEN='\033[0;32m'
readonly YELLOW='\033[1;33m'
readonly BLUE='\033[0;34m'
readonly PURPLE='\033[0;35m'
readonly CYAN='\033[0;36m'
readonly WHITE='\033[1;37m'
readonly NC='\033[0m'
readonly BOLD='\033[1m'

# Global variables
SERVER_PID=""
SERVER_LOG_FILE="$UDOS_ROOT/uSERVER/server.log"

show_help() {
    echo "uDOS Universal Startup Script v$UDOS_VERSION"
    echo ""
    echo "Usage: $0 [ROLE] [OPTIONS]"
    echo ""
    echo "Roles:"
    echo "  ghost     - Level 10: Demo and evaluation"
    echo "  tomb      - Level 20: Archive management"
    echo "  drone     - Level 40: Task automation"
    echo "  imp       - Level 60: Development tools"
    echo "  sorcerer  - Level 80: Advanced user management"
    echo "  wizard    - Level 100: Full system access (default)"
    echo ""
    echo "Options:"
    echo "  --ui-mode      Launch with UI omniview"
    echo "  --server-only  Start only uSERVER (no CLI)"
    echo "  --vscode-dev   Start VS Code development mode"
    echo "  --help         Show this help message"
    echo ""
    echo "CLI Commands (when server running):"
    echo "  status         Show detailed system status"
    echo "  server         Server management options"
    echo "  ui             Open UI omniview in browser"
    echo "  logs           View server logs"
    echo "  restart        Restart uSERVER"
    echo "  shutdown       Stop server and exit"
    echo "  help           Show available commands"
}

# Parse command line arguments
ROLE="${1:-wizard}"
UI_MODE=false
SERVER_ONLY=false

while [[ $# -gt 0 ]]; do
    case $1 in
        --role=*)
            ROLE="${1#*=}"
            shift
            ;;
        --ui-mode)
            UI_MODE=true
            shift
            ;;
        --server-only)
            SERVER_ONLY=true
            shift
            ;;
        --vscode-dev|--vscode|--dev)
            echo -e "${BLUE}🧙‍♂️ Starting VS Code Development Mode...${NC}"
            exec "$UDOS_ROOT/uCORE/launcher/vscode/start-vscode-dev.sh"
            ;;
        --help)
            show_help
            exit 0
            ;;
        *)
            ROLE="$1"
            shift
            ;;
    esac
done

# Role configuration
configure_role() {
    case "$ROLE" in
        "ghost")
            export UDOS_ACCESS_LEVEL=10
            export UDOS_ROLE_NAME="Ghost"
            export UDOS_ROLE_ICON="👻"
            export UDOS_ROLE_COLOR="$CYAN"
            export UDOS_CAPABILITIES="demo,docs"
            ;;
        "tomb")
            export UDOS_ACCESS_LEVEL=20
            export UDOS_ROLE_NAME="Tomb"
            export UDOS_ROLE_ICON="⚰️"
            export UDOS_ROLE_COLOR="$YELLOW"
            export UDOS_CAPABILITIES="archive,backup,restore"
            ;;
        "drone")
            export UDOS_ACCESS_LEVEL=40
            export UDOS_ROLE_NAME="Drone"
            export UDOS_ROLE_ICON="🤖"
            export UDOS_ROLE_COLOR="$BLUE"
            export UDOS_CAPABILITIES="automation,monitoring,tasks"
            ;;
        "imp")
            export UDOS_ACCESS_LEVEL=60
            export UDOS_ROLE_NAME="Imp"
            export UDOS_ROLE_ICON="👹"
            export UDOS_ROLE_COLOR="$RED"
            export UDOS_CAPABILITIES="development,scripting,templates"
            ;;
        "sorcerer")
            export UDOS_ACCESS_LEVEL=80
            export UDOS_ROLE_NAME="Sorcerer"
            export UDOS_ROLE_ICON="🔮"
            export UDOS_ROLE_COLOR="$PURPLE"
            export UDOS_CAPABILITIES="advanced,management,administration"
            ;;
        "wizard")
            export UDOS_ACCESS_LEVEL=100
            export UDOS_ROLE_NAME="Wizard"
            export UDOS_ROLE_ICON="🧙‍♂️"
            export UDOS_ROLE_COLOR="$WHITE"
            export UDOS_CAPABILITIES="full,development,git,administration"
            ;;
        *)
            echo -e "${RED}❌ Unknown role: $ROLE${NC}"
            echo "Available roles: ghost, tomb, drone, imp, sorcerer, wizard"
            exit 1
            ;;
    esac
}

# Show role banner
show_role_banner() {
    echo -e "${UDOS_ROLE_COLOR}"
    echo "   ██╗   ██╗██████╗  ██████╗ ███████╗"
    echo "   ██║   ██║██╔══██╗██╔═══██╗██╔════╝"
    echo "   ██║   ██║██║  ██║██║   ██║███████╗"
    echo "   ██║   ██║██║  ██║██║   ██║╚════██║"
    echo "   ╚██████╔╝██████╔╝╚██████╔╝███████║"
    echo "    ╚═════╝ ╚═════╝  ╚═════╝ ╚══════╝"
    echo -e "${NC}"
    echo -e "${UDOS_ROLE_COLOR}${UDOS_ROLE_ICON} ${UDOS_ROLE_NAME} Mode ${NC}${WHITE}(Level $UDOS_ACCESS_LEVEL)${NC}"
    echo -e "${YELLOW}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
    echo ""
}

# Start uSERVER in background
start_userver_background() {
    echo -e "${BLUE}🔧 Starting uSERVER for $UDOS_ROLE_NAME...${NC}"

    # Set environment variables for server
    export UDOS_SERVER_ROLE="$ROLE"
    export UDOS_SERVER_ACCESS_LEVEL="$UDOS_ACCESS_LEVEL"
    export UDOS_SERVER_PORT="$UDOS_SERVER_PORT"
    export UDOS_SERVER_HOST="127.0.0.1"

    # Start server in background with logging
    cd "$UDOS_ROOT/uSERVER"
    nohup python3 server.py > "$SERVER_LOG_FILE" 2>&1 &
    SERVER_PID=$!

    # Save PID for later reference
    echo "$SERVER_PID" > "$UDOS_ROOT/uSERVER/server.pid"

    echo -e "${YELLOW}⏳ Starting server (PID: $SERVER_PID)...${NC}"

    # Wait for server to start
    local max_attempts=15
    local attempt=1

    while [[ $attempt -le $max_attempts ]]; do
        if curl -s "http://127.0.0.1:${UDOS_SERVER_PORT}/api/status" >/dev/null 2>&1; then
            echo -e "${GREEN}✅ uSERVER started successfully on port $UDOS_SERVER_PORT${NC}"
            echo -e "${CYAN}🌐 URL: http://127.0.0.1:${UDOS_SERVER_PORT}${NC}"
            return 0
        fi
        echo -e "${YELLOW}⏳ Waiting for uSERVER... ($attempt/$max_attempts)${NC}"
        sleep 1
        ((attempt++))
    done

    echo -e "${RED}❌ uSERVER failed to start${NC}"
    return 1
}

# Check if server is running
is_server_running() {
    if [[ -n "$SERVER_PID" ]] && kill -0 "$SERVER_PID" 2>/dev/null; then
        return 0
    elif curl -s "http://127.0.0.1:${UDOS_SERVER_PORT}/api/status" >/dev/null 2>&1; then
        return 0
    else
        return 1
    fi
}

# Get server status details
get_server_status() {
    if is_server_running; then
        local status_json=$(curl -s "http://127.0.0.1:${UDOS_SERVER_PORT}/api/status" 2>/dev/null)
        if [[ -n "$status_json" ]]; then
            echo "$status_json"
        else
            echo '{"status":"running","details":"API unavailable"}'
        fi
    else
        echo '{"status":"stopped"}'
    fi
}

# Show detailed system status
show_system_status() {
    echo -e "${BOLD}${BLUE}📊 uDOS System Status${NC}"
    echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"

    # Role Information
    echo -e "${WHITE}Role:${NC} $UDOS_ROLE_ICON $UDOS_ROLE_NAME (Level $UDOS_ACCESS_LEVEL)"
    echo -e "${WHITE}Capabilities:${NC} $UDOS_CAPABILITIES"
    echo -e "${WHITE}Working Directory:${NC} $UDOS_ROOT"
    echo ""

    # Server Status
    if is_server_running; then
        echo -e "${WHITE}uSERVER Status:${NC} ${GREEN}✅ Running${NC}"
        echo -e "${WHITE}Process ID:${NC} $SERVER_PID"
        echo -e "${WHITE}Port:${NC} $UDOS_SERVER_PORT"
        echo -e "${WHITE}URL:${NC} http://127.0.0.1:${UDOS_SERVER_PORT}"

        # Get detailed status from API
        local status_json=$(get_server_status)
        if echo "$status_json" | grep -q '"startup_complete":true'; then
            echo -e "${WHITE}Startup:${NC} ${GREEN}✅ Complete${NC}"
        else
            echo -e "${WHITE}Startup:${NC} ${YELLOW}⏳ In Progress${NC}"
        fi

        # Extract uptime if available
        local uptime=$(echo "$status_json" | python3 -c "import json,sys; data=json.load(sys.stdin); print(f\"{data.get('uptime', 0):.1f}s\")" 2>/dev/null || echo "Unknown")
        echo -e "${WHITE}Uptime:${NC} $uptime"

        # Extract connected clients
        local clients=$(echo "$status_json" | python3 -c "import json,sys; data=json.load(sys.stdin); print(data.get('clients', 0))" 2>/dev/null || echo "0")
        echo -e "${WHITE}Connected Clients:${NC} $clients"

    else
        echo -e "${WHITE}uSERVER Status:${NC} ${RED}❌ Not Running${NC}"
    fi
    echo ""

    # System Resources
    echo -e "${WHITE}System Resources:${NC}"
    echo -e "  ${WHITE}Memory:${NC} $(ps -o rss= -p $$ 2>/dev/null | awk '{print int($1/1024)"MB"}' || echo "Unknown")"
    echo -e "  ${WHITE}Disk Space:${NC} $(df -h "$UDOS_ROOT" | tail -1 | awk '{print $4}' || echo "Unknown") available"
    echo ""
}

# Server management menu
server_management() {
    echo -e "${BOLD}${BLUE}🔧 Server Management${NC}"
    echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
    echo "1. Restart Server"
    echo "2. View Live Logs"
    echo "3. Check Server Health"
    echo "4. Force Stop Server"
    echo "5. Back to Main Menu"
    echo ""

    read -p "Select option (1-5): " choice

    case $choice in
        1)
            restart_server
            ;;
        2)
            view_server_logs
            ;;
        3)
            check_server_health
            ;;
        4)
            force_stop_server
            ;;
        5)
            return
            ;;
        *)
            echo -e "${RED}Invalid option${NC}"
            ;;
    esac
}

# Restart server
restart_server() {
    echo -e "${YELLOW}🔄 Restarting uSERVER...${NC}"

    if is_server_running; then
        echo -e "${BLUE}Stopping current server...${NC}"
        kill "$SERVER_PID" 2>/dev/null || true
        sleep 2
    fi

    start_userver_background
}

# View server logs
view_server_logs() {
    echo -e "${BLUE}📋 Server Logs (last 20 lines)${NC}"
    echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"

    if [[ -f "$SERVER_LOG_FILE" ]]; then
        tail -20 "$SERVER_LOG_FILE"
    else
        echo "No log file found"
    fi

    echo ""
    echo "Press Enter to continue..."
    read
}

# Check server health
check_server_health() {
    echo -e "${BLUE}🏥 Server Health Check${NC}"
    echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"

    if is_server_running; then
        echo -e "${GREEN}✅ Server is responding${NC}"

        # Test specific endpoints
        echo "Testing endpoints:"

        if curl -s "http://127.0.0.1:${UDOS_SERVER_PORT}/api/status" >/dev/null; then
            echo -e "  ${GREEN}✅${NC} /api/status"
        else
            echo -e "  ${RED}❌${NC} /api/status"
        fi

        if curl -s "http://127.0.0.1:${UDOS_SERVER_PORT}/" >/dev/null; then
            echo -e "  ${GREEN}✅${NC} / (main page)"
        else
            echo -e "  ${RED}❌${NC} / (main page)"
        fi

    else
        echo -e "${RED}❌ Server is not responding${NC}"
    fi

    echo ""
    echo "Press Enter to continue..."
    read
}

# Force stop server
force_stop_server() {
    echo -e "${RED}⚠️  Force stopping server...${NC}"

    if [[ -n "$SERVER_PID" ]]; then
        kill -9 "$SERVER_PID" 2>/dev/null || true
    fi

    # Also try to kill any python server processes
    pkill -f "python3 server.py" 2>/dev/null || true

    echo -e "${GREEN}✅ Server stopped${NC}"
    SERVER_PID=""
}

# Open UI in browser
open_ui_browser() {
    if is_server_running; then
        local ui_url="http://127.0.0.1:${UDOS_UI_PORT}?role=${ROLE}&level=${UDOS_ACCESS_LEVEL}"
        echo -e "${CYAN}🌐 Opening UI omniview...${NC}"

        case "$(uname -s)" in
            Darwin)
                open "$ui_url"
                ;;
            Linux)
                xdg-open "$ui_url" 2>/dev/null || echo "Open browser to: $ui_url"
                ;;
            *)
                echo "Open browser to: $ui_url"
                ;;
        esac

        echo -e "${GREEN}✅ Browser opened${NC}"
    else
        echo -e "${RED}❌ Server not running - cannot open UI${NC}"
    fi
}

# Enhanced CLI interface with server status
start_enhanced_cli() {
    # Show initial status
    show_system_status

    echo -e "${BOLD}${WHITE}🖥️  $UDOS_ROLE_NAME CLI Operations${NC}"
    echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
    echo ""
    echo -e "${WHITE}Available commands:${NC}"
    echo "  ${GREEN}status${NC}      - Show detailed system status"
    echo "  ${GREEN}server${NC}      - Server management options"
    echo "  ${GREEN}ui${NC}          - Open UI omniview in browser"
    echo "  ${GREEN}logs${NC}        - View recent server logs"
    echo "  ${GREEN}restart${NC}     - Restart uSERVER"
    echo "  ${GREEN}shutdown${NC}    - Stop server and exit"
    echo "  ${GREEN}help${NC}        - Show available commands"
    echo ""

    # CLI command loop
    while true; do
        # Show server status indicator in prompt
        local status_indicator
        if is_server_running; then
            status_indicator="${GREEN}●${NC}"
        else
            status_indicator="${RED}●${NC}"
        fi

        read -p "${UDOS_ROLE_ICON}${UDOS_ROLE_NAME}${status_indicator}> " -r command args

        case "$command" in
            "status")
                show_system_status
                ;;
            "server")
                server_management
                ;;
            "ui")
                open_ui_browser
                ;;
            "logs")
                view_server_logs
                ;;
            "restart")
                restart_server
                ;;
            "shutdown"|"quit"|"exit")
                echo -e "${YELLOW}🛑 Shutting down uSERVER...${NC}"
                if is_server_running; then
                    kill "$SERVER_PID" 2>/dev/null || true
                    echo -e "${GREEN}✅ Server stopped${NC}"
                fi
                echo -e "${YELLOW}👋 Exiting $UDOS_ROLE_NAME mode${NC}"
                break
                ;;
            "help")
                echo -e "${WHITE}Available commands:${NC}"
                echo "  ${GREEN}status${NC}      - Show detailed system status"
                echo "  ${GREEN}server${NC}      - Server management options"
                echo "  ${GREEN}ui${NC}          - Open UI omniview in browser"
                echo "  ${GREEN}logs${NC}        - View recent server logs"
                echo "  ${GREEN}restart${NC}     - Restart uSERVER"
                echo "  ${GREEN}shutdown${NC}    - Stop server and exit"
                echo "  ${GREEN}help${NC}        - Show available commands"
                ;;
            "")
                # Empty command, continue
                ;;
            *)
                echo -e "${RED}Unknown command: $command${NC}"
                echo "Type 'help' for available commands"
                ;;
        esac
    done
}

# Launch UI if requested
launch_ui_omniview() {
    if [[ "$UI_MODE" == "true" ]]; then
        open_ui_browser
    fi
}

# Cleanup function
cleanup() {
    if [[ -n "$SERVER_PID" ]] && kill -0 "$SERVER_PID" 2>/dev/null; then
        echo -e "\n${YELLOW}🛑 Cleaning up...${NC}"
        kill "$SERVER_PID" 2>/dev/null || true
        echo -e "${GREEN}✅ Server stopped${NC}"
    fi
}

# Set trap for cleanup
trap cleanup EXIT INT TERM

# Main execution
main() {
    configure_role
    show_role_banner

    if [[ "$SERVER_ONLY" == "true" ]]; then
        # Server-only mode (no CLI)
        if start_userver_background; then
            echo -e "${GREEN}✅ uSERVER started in server-only mode${NC}"
            echo -e "${CYAN}🌐 URL: http://127.0.0.1:${UDOS_SERVER_PORT}${NC}"
            echo -e "${YELLOW}Press Ctrl+C to stop${NC}"

            # Keep script running
            while is_server_running; do
                sleep 5
            done
        else
            echo -e "${RED}❌ Failed to start uSERVER${NC}"
            exit 1
        fi
    else
        # Normal mode with CLI
        if start_userver_background; then
            launch_ui_omniview
            start_enhanced_cli
        else
            echo -e "${RED}❌ Failed to start uSERVER${NC}"
            echo -e "${YELLOW}Starting CLI without server...${NC}"
            start_enhanced_cli
        fi
    fi
}

# Execute main function
main
