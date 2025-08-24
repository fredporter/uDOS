#!/bin/bash
# uDOS Universal Startup Script v1.4.0 - Enhanced CLI with Background Server
# Keeps server running while providing interactive CLI with status and options
# Supports three-mode display system: CLI Terminal, Desktop App, Web Export

set -euo pipefail

# Configuration
export UDOS_ROOT="${UDOS_ROOT:-$(cd "$(dirname "${BASH_SOURCE[0]}")/../../../" && pwd)}"
export UDOS_VERSION="1.4.0"
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
SERVER_LOG_FILE="$UDOS_ROOT/uNETWORK/server/server.log"

show_help() {
    echo "uDOS Universal Startup Script v$UDOS_VERSION"
    echo ""
    echo "Usage: $0 [ROLE] [OPTIONS]"
    if [[ ! -x "$UDOS_ROOT/uNETWORK/server/server.py" ]]; then
        echo -e "${RED}❌ uNETWORK/server script missing or not executable${NC}"
        exit 1
    fi
    echo ""
    echo "Display Modes (v1.4):"
    echo "  CLI Terminal     - Always available for all roles (this script)"
    echo "  Desktop App      - DRONE+ roles (40+): ./uNETWORK/display/udos-display.sh app"
    echo "  Web Export       - DRONE+ roles (40+): ./uNETWORK/display/udos-display.sh export"
    echo ""
    echo "Role Hierarchy with Feature Access:"
    echo "  ghost     - Level 10: Demo/evaluation (uCORE only)"
    echo "  tomb      - Level 20: Archive management (uCORE only)"
    echo "  crypt     - Level 30: Security/encryption (uCORE + uNETWORK + uSCRIPT)"
    echo "  drone     - Level 40: Task automation (+ display modes - DRONE+)"
    echo "  knight    - Level 50: Protection/defense (inherits drone+)"
    echo "  user      - Level 55: Personal workspace (inherits knight+)"
    echo "  imp       - Level 60: Development tools (inherits user+)"
    echo "  dev       - Level 70: Advanced development (inherits imp+)"
    echo "  sorcerer  - Level 80: User management (+ Gemini-CLI - inherits dev+)"
    echo "  wizard    - Level 100: Full system access (+ VS Code dev - inherits sorcerer+)"
    echo ""
    echo "Feature Access Levels:"
    echo "  uCORE only       - Ghost, Tomb (basic CLI)"
    echo "  + uNETWORK       - Crypt+ (display system, networking)"
    echo "  + uSCRIPT        - Crypt+ (scripting environment)"
    echo "  + Display Modes  - DRONE+ (desktop app, web export)"
    echo "  + Gemini-CLI     - Sorcerer+ (AI assistance)"
    echo "  + VS Code Dev    - Wizard only (development environment)"
    echo ""
    echo "Options:"
    echo "  --ui-mode      Launch with UI omniview"
    echo "  --server-only  Start only uNETWORK/server (no CLI)"
    cd "$UDOS_ROOT/uNETWORK/server"
    echo "  --help         Show this help message"
    echo ""
    echo "CLI Commands (when server running):"
    echo "  status         Show detailed system status"
    echo "  server         Server management options"
    echo "  ui             Open UI omniview in browser"
    echo "  logs           View server logs"
    echo "  restart        Restart uNETWORK/server"
    echo "  shutdown       Stop server and exit"
    echo "  help           Show available commands"
}

# Parse command line arguments

# Interactive mode prompt if no arguments
if [[ $# -eq 0 ]]; then
    echo -e "\033[1;36m🌀 uDOS v1.4 Startup Mode\033[0m"
    echo "Choose your preferred launch mode:"
    echo "  1) CLI Terminal (always available)"
    echo "  2) Desktop Application (DRONE+ roles)"
    echo "  3) Web Export (sharing mode)"
    echo "  4) VS Code Dev Mode (Wizard only)"
    echo "  5) Exit"
    read -p "Enter choice [1-5]: " mode_choice
    case "$mode_choice" in
        1)
            set -- wizard
            ;;
        2)
            echo -e "\033[1;33m💡 Desktop app requires DRONE+ role (40+)\033[0m"
            echo "   Starting CLI mode with UI available..."
            set -- --ui-mode
            ;;
        3)
            echo -e "\033[1;33m💡 Web export requires DRONE+ role (40+)\033[0m"
            echo "   Starting CLI mode with UI available..."
            set -- --ui-mode
            ;;
        4)
            echo -e "\033[1;33m💡 VS Code dev mode requires Wizard role (100)\033[0m"
            set -- --vscode-dev
            ;;
        *)
            echo "Exiting."
            exit 0
            ;;
    esac
fi


ROLE="wizard"
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
        ghost|tomb|crypt|drone|knight|imp|user|dev|sorcerer|wizard)
            ROLE="$1"
            shift
            ;;
        *)
            echo -e "${RED}❌ Unknown option or role: $1${NC}"
            show_help
            exit 1
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
            export UDOS_CAPABILITIES="demo,docs,ucore-only"
            export UDOS_DRONE_PLUS="false"
            export UDOS_UNETWORK_ACCESS="false"
            export UDOS_USCRIPT_ACCESS="false"
            export UDOS_GEMINI_ACCESS="false"
            export UDOS_VSCODE_ACCESS="false"
            ;;
        "tomb")
            export UDOS_ACCESS_LEVEL=20
            export UDOS_ROLE_NAME="Tomb"
            export UDOS_ROLE_ICON="⚰️"
            export UDOS_ROLE_COLOR="$YELLOW"
            export UDOS_CAPABILITIES="archive,backup,restore,ucore-only"
            export UDOS_DRONE_PLUS="false"
            export UDOS_UNETWORK_ACCESS="false"
            export UDOS_USCRIPT_ACCESS="false"
            export UDOS_GEMINI_ACCESS="false"
            export UDOS_VSCODE_ACCESS="false"
            ;;
        "crypt")
            export UDOS_ACCESS_LEVEL=30
            export UDOS_ROLE_NAME="Crypt"
            export UDOS_ROLE_ICON="🔐"
            export UDOS_ROLE_COLOR="$PURPLE"
            export UDOS_CAPABILITIES="archive,backup,restore,security,encryption,ucore,unetwork,uscript"
            export UDOS_DRONE_PLUS="false"
            export UDOS_UNETWORK_ACCESS="true"
            export UDOS_USCRIPT_ACCESS="true"
            export UDOS_GEMINI_ACCESS="false"
            export UDOS_VSCODE_ACCESS="false"
            ;;
        "tomb")
            export UDOS_ACCESS_LEVEL=20
            export UDOS_ROLE_NAME="Tomb"
            export UDOS_ROLE_ICON="⚰️"
            export UDOS_ROLE_COLOR="$YELLOW"
            export UDOS_CAPABILITIES="archive,backup,restore"
            export UDOS_DRONE_PLUS="false"
            ;;
        "crypt")
            export UDOS_ACCESS_LEVEL=30
            export UDOS_ROLE_NAME="Crypt"
            export UDOS_ROLE_ICON="🔐"
            export UDOS_ROLE_COLOR="$PURPLE"
            export UDOS_CAPABILITIES="archive,backup,restore,security,encryption"
            export UDOS_DRONE_PLUS="false"
            ;;
        "drone")
            export UDOS_ACCESS_LEVEL=40
            export UDOS_ROLE_NAME="Drone"
            export UDOS_ROLE_ICON="🤖"
            export UDOS_ROLE_COLOR="$BLUE"
            export UDOS_CAPABILITIES="archive,backup,restore,security,encryption,automation,monitoring,tasks,ucore,unetwork,uscript,display-desktop,display-export"
            export UDOS_DRONE_PLUS="true"
            export UDOS_UNETWORK_ACCESS="true"
            export UDOS_USCRIPT_ACCESS="true"
            export UDOS_GEMINI_ACCESS="false"
            export UDOS_VSCODE_ACCESS="false"
            ;;
        "knight")
            export UDOS_ACCESS_LEVEL=50
            export UDOS_ROLE_NAME="Knight"
            export UDOS_ROLE_ICON="⚔️"
            export UDOS_ROLE_COLOR="$WHITE"
            export UDOS_CAPABILITIES="archive,backup,restore,security,encryption,automation,monitoring,tasks,protection,defense,ucore,unetwork,uscript,display-desktop,display-export"
            export UDOS_DRONE_PLUS="true"
            export UDOS_UNETWORK_ACCESS="true"
            export UDOS_USCRIPT_ACCESS="true"
            export UDOS_GEMINI_ACCESS="false"
            export UDOS_VSCODE_ACCESS="false"
            ;;
        "user")
            export UDOS_ACCESS_LEVEL=55
            export UDOS_ROLE_NAME="User"
            export UDOS_ROLE_ICON="👤"
            export UDOS_ROLE_COLOR="$GREEN"
            export UDOS_CAPABILITIES="archive,backup,restore,security,encryption,automation,monitoring,tasks,protection,defense,development,personal,ucore,unetwork,uscript,display-desktop,display-export"
            export UDOS_DRONE_PLUS="true"
            export UDOS_UNETWORK_ACCESS="true"
            export UDOS_USCRIPT_ACCESS="true"
            export UDOS_GEMINI_ACCESS="false"
            export UDOS_VSCODE_ACCESS="false"
            ;;
        "imp")
            export UDOS_ACCESS_LEVEL=60
            export UDOS_ROLE_NAME="Imp"
            export UDOS_ROLE_ICON="👹"
            export UDOS_ROLE_COLOR="$RED"
            export UDOS_CAPABILITIES="archive,backup,restore,security,encryption,automation,monitoring,tasks,protection,defense,development,personal,scripting,templates,ucore,unetwork,uscript,display-desktop,display-export"
            export UDOS_DRONE_PLUS="true"
            export UDOS_UNETWORK_ACCESS="true"
            export UDOS_USCRIPT_ACCESS="true"
            export UDOS_GEMINI_ACCESS="false"
            export UDOS_VSCODE_ACCESS="false"
            ;;
        "dev")
            export UDOS_ACCESS_LEVEL=70
            export UDOS_ROLE_NAME="Developer"
            export UDOS_ROLE_ICON="👨‍💻"
            export UDOS_ROLE_COLOR="$CYAN"
            export UDOS_CAPABILITIES="archive,backup,restore,security,encryption,automation,monitoring,tasks,protection,defense,development,personal,scripting,templates,debugging,advanced,ucore,unetwork,uscript,display-desktop,display-export"
            export UDOS_DRONE_PLUS="true"
            export UDOS_UNETWORK_ACCESS="true"
            export UDOS_USCRIPT_ACCESS="true"
            export UDOS_GEMINI_ACCESS="false"
            export UDOS_VSCODE_ACCESS="false"
            ;;
        "sorcerer")
            export UDOS_ACCESS_LEVEL=80
            export UDOS_ROLE_NAME="Sorcerer"
            export UDOS_ROLE_ICON="🔮"
            export UDOS_ROLE_COLOR="$PURPLE"
            export UDOS_CAPABILITIES="archive,backup,restore,security,encryption,automation,monitoring,tasks,protection,defense,development,personal,scripting,templates,debugging,advanced,management,administration,ucore,unetwork,uscript,gemini-cli,display-desktop,display-export"
            export UDOS_DRONE_PLUS="true"
            export UDOS_UNETWORK_ACCESS="true"
            export UDOS_USCRIPT_ACCESS="true"
            export UDOS_GEMINI_ACCESS="true"
            export UDOS_VSCODE_ACCESS="false"
            ;;
        "wizard")
            export UDOS_ACCESS_LEVEL=100
            export UDOS_ROLE_NAME="Wizard"
            export UDOS_ROLE_ICON="🧙‍♂️"
            export UDOS_ROLE_COLOR="$WHITE"
            export UDOS_CAPABILITIES="archive,backup,restore,security,encryption,automation,monitoring,tasks,protection,defense,development,personal,scripting,templates,debugging,advanced,management,administration,full,git,ucore,unetwork,uscript,gemini-cli,vscode-dev,display-desktop,display-export"
            export UDOS_DRONE_PLUS="true"
            export UDOS_UNETWORK_ACCESS="true"
            export UDOS_USCRIPT_ACCESS="true"
            export UDOS_GEMINI_ACCESS="true"
            export UDOS_VSCODE_ACCESS="true"
            ;;
        "knight")
            export UDOS_ACCESS_LEVEL=50
            export UDOS_ROLE_NAME="Knight"
            export UDOS_ROLE_ICON="⚔️"
            export UDOS_ROLE_COLOR="$WHITE"
            export UDOS_CAPABILITIES="archive,backup,restore,security,encryption,automation,monitoring,tasks,protection,defense,display-desktop,display-export"
            export UDOS_DRONE_PLUS="true"
            ;;
        "user")
            export UDOS_ACCESS_LEVEL=55
            export UDOS_ROLE_NAME="User"
            export UDOS_ROLE_ICON="�"
            export UDOS_ROLE_COLOR="$GREEN"
            export UDOS_CAPABILITIES="archive,backup,restore,security,encryption,automation,monitoring,tasks,protection,defense,development,personal,display-desktop,display-export"
            export UDOS_DRONE_PLUS="true"
            ;;
        "imp")
            export UDOS_ACCESS_LEVEL=60
            export UDOS_ROLE_NAME="Imp"
            export UDOS_ROLE_ICON="👹"
            export UDOS_ROLE_COLOR="$RED"
            export UDOS_CAPABILITIES="archive,backup,restore,security,encryption,automation,monitoring,tasks,protection,defense,development,personal,scripting,templates,display-desktop,display-export"
            export UDOS_DRONE_PLUS="true"
            ;;
        "dev")
            export UDOS_ACCESS_LEVEL=70
            export UDOS_ROLE_NAME="Developer"
            export UDOS_ROLE_ICON="👨‍💻"
            export UDOS_ROLE_COLOR="$CYAN"
            export UDOS_CAPABILITIES="archive,backup,restore,security,encryption,automation,monitoring,tasks,protection,defense,development,personal,scripting,templates,debugging,advanced,display-desktop,display-export"
            export UDOS_DRONE_PLUS="true"
            ;;
        "sorcerer")
            export UDOS_ACCESS_LEVEL=80
            export UDOS_ROLE_NAME="Sorcerer"
            export UDOS_ROLE_ICON="�"
            export UDOS_ROLE_COLOR="$PURPLE"
            export UDOS_CAPABILITIES="archive,backup,restore,security,encryption,automation,monitoring,tasks,protection,defense,development,personal,scripting,templates,debugging,advanced,management,administration,display-desktop,display-export"
            export UDOS_DRONE_PLUS="true"
            ;;
        "wizard")
            export UDOS_ACCESS_LEVEL=100
            export UDOS_ROLE_NAME="Wizard"
            export UDOS_ROLE_ICON="🧙‍♂️"
            export UDOS_ROLE_COLOR="$WHITE"
            export UDOS_CAPABILITIES="archive,backup,restore,security,encryption,automation,monitoring,tasks,protection,defense,development,personal,scripting,templates,debugging,advanced,management,administration,full,git,display-desktop,display-export"
            export UDOS_DRONE_PLUS="true"
            ;;
            export UDOS_CAPABILITIES="automation,monitoring,tasks,development,scripting,templates,debugging,advanced,display-desktop,display-export"
            export UDOS_DRONE_PLUS="true"
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
    
    # Show feature access
    echo -e "${WHITE}Feature Access:${NC}"
    echo -e "  ${GREEN}✅ uCORE${NC} (CLI Terminal)"
    
    if [[ "$UDOS_UNETWORK_ACCESS" == "true" ]]; then
        echo -e "  ${GREEN}✅ uNETWORK${NC} (Networking & Display System)"
    else
        echo -e "  ${RED}❌ uNETWORK${NC} (uCORE only)"
    fi
    
    if [[ "$UDOS_USCRIPT_ACCESS" == "true" ]]; then
        echo -e "  ${GREEN}✅ uSCRIPT${NC} (Scripting Environment)"
    else
        echo -e "  ${RED}❌ uSCRIPT${NC} (uCORE only)"
    fi
    
    if [[ "$UDOS_DRONE_PLUS" == "true" ]]; then
        echo -e "  ${GREEN}✅ Display Modes${NC} (Desktop App & Web Export)"
    else
        echo -e "  ${RED}❌ Display Modes${NC} (CLI Terminal only)"
    fi
    
    if [[ "$UDOS_GEMINI_ACCESS" == "true" ]]; then
        echo -e "  ${GREEN}✅ Gemini-CLI${NC} (AI Assistant)"
    else
        echo -e "  ${YELLOW}⚪ Gemini-CLI${NC} (Sorcerer+ only)"
    fi
    
    if [[ "$UDOS_VSCODE_ACCESS" == "true" ]]; then
        echo -e "  ${GREEN}✅ VS Code Dev${NC} (Development Environment)"
    else
        echo -e "  ${YELLOW}⚪ VS Code Dev${NC} (Wizard only)"
    fi
    
    echo -e "${YELLOW}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
    echo ""
}# Start uNETWORK/server in background
start_unetwork_server_background() {
    echo -e "${BLUE}🔧 Starting uNETWORK/server for $UDOS_ROLE_NAME...${NC}"

    # Set environment variables for server
    export UDOS_SERVER_ROLE="$ROLE"
    export UDOS_SERVER_ACCESS_LEVEL="$UDOS_ACCESS_LEVEL"
    export UDOS_SERVER_PORT="$UDOS_SERVER_PORT"
    export UDOS_SERVER_HOST="127.0.0.1"

    # Start server in background with logging
    cd "$UDOS_ROOT/uNETWORK/server"
    nohup python3 server.py > "$SERVER_LOG_FILE" 2>&1 &
    SERVER_PID=$!

    # Save PID for later reference
    echo "$SERVER_PID" > "$UDOS_ROOT/uNETWORK/server/server.pid"

    echo -e "${YELLOW}⏳ Starting server (PID: $SERVER_PID)...${NC}"

    # Wait for server to start
    local max_attempts=15
    local attempt=1

    while [[ $attempt -le $max_attempts ]]; do
        if curl -s "http://127.0.0.1:${UDOS_SERVER_PORT}/api/status" >/dev/null 2>&1; then
            echo -e "${GREEN}✅ uNETWORK/server started successfully on port $UDOS_SERVER_PORT${NC}"
            echo -e "${CYAN}🌐 URL: http://127.0.0.1:${UDOS_SERVER_PORT}${NC}"
            return 0
        fi
    echo -e "${YELLOW}⏳ Waiting for uNETWORK/server... ($attempt/$max_attempts)${NC}"
        sleep 1
        ((attempt++))
    done

    echo -e "${RED}❌ uNETWORK/server failed to start${NC}"
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
    echo -e "${WHITE}uNETWORK/server Status:${NC} ${GREEN}✅ Running${NC}"
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
    echo -e "${WHITE}uNETWORK/server Status:${NC} ${RED}❌ Not Running${NC}"
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
    echo -e "${YELLOW}🔄 Restarting uNETWORK/server...${NC}"

    if is_server_running; then
        echo -e "${BLUE}Stopping current server...${NC}"
        kill "$SERVER_PID" 2>/dev/null || true
        sleep 2
    fi

    start_unetwork_server_background
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
    echo "  ${GREEN}restart${NC}     - Restart uNETWORK/server"
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
                echo -e "${YELLOW}🛑 Shutting down uNETWORK/server...${NC}"
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
                echo "  ${GREEN}restart${NC}     - Restart uNETWORK/server"
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

main() {
    configure_role
    show_role_banner

    # Check for required install scripts and launcher
    if [[ ! -x "$UDOS_ROOT/uCORE/launcher/install-launcher.sh" ]]; then
        echo -e "${RED}❌ Launcher install script missing or not executable${NC}"
        echo -e "${YELLOW}Running install-launcher.sh...${NC}"
        bash "$UDOS_ROOT/uCORE/launcher/install-launcher.sh"
    fi

    # Check for server script
    if [[ ! -x "$UDOS_ROOT/uNETWORK/server/server.py" ]]; then
        echo -e "${RED}❌ uNETWORK/server script missing or not executable${NC}"
        exit 1
    fi

    if [[ "$SERVER_ONLY" == "true" ]]; then
        # Server-only mode (no CLI)
    if start_unetwork_server_background; then
            echo -e "${GREEN}✅ uNETWORK/server started in server-only mode${NC}"
            echo -e "${CYAN}🌐 URL: http://127.0.0.1:${UDOS_SERVER_PORT}${NC}"
            echo -e "${YELLOW}Press Ctrl+C to stop${NC}"

            # Keep script running
            while is_server_running; do
                sleep 5
            done
        else
            echo -e "${RED}❌ Failed to start uNETWORK/server${NC}"
            exit 1
        fi
    else
        # Normal mode with CLI
    if start_unetwork_server_background; then
            launch_ui_omniview
            start_enhanced_cli
        else
            echo -e "${RED}❌ Failed to start uNETWORK/server${NC}"
            echo -e "${YELLOW}Starting CLI without server...${NC}"
            start_enhanced_cli
        fi
    fi
}

# Execute main function
main
