#!/bin/bash
# uDOS Universal Startup Script with Role Support v1.3.1
# Enhanced launcher with UI/Server separation and role management

set -euo pipefail

# Configuration
export UDOS_ROOT="${UDOS_ROOT:-$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)}"
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
    echo "  --server-only  Start only uSERVER CLI operations"
    echo "  --help         Show this help message"
}

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
            export UDOS_ROLE_ICON="⚰️ "
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

# Check role permissions
check_role_permissions() {
    local role_dir="$UDOS_ROOT/$ROLE"
    
    if [[ ! -d "$role_dir" ]]; then
        echo -e "${RED}❌ Role '$ROLE' not available${NC}"
        echo -e "${YELLOW}💡 Available roles:${NC}"
        for available_role in ghost tomb drone imp sorcerer wizard; do
            if [[ -d "$UDOS_ROOT/$available_role" ]]; then
                echo "   - $available_role"
            fi
        done
        exit 1
    fi
    
    # Check permissions file if exists
    local permissions_file="$role_dir/permissions.json"
    if [[ -f "$permissions_file" ]]; then
        echo -e "${GREEN}✅ Role permissions validated${NC}"
    fi
}

# Initialize role environment
initialize_role_environment() {
    echo -e "${BLUE}🔧 Initializing $UDOS_ROLE_NAME environment...${NC}"
    
    # Set role-specific environment variables
    export UDOS_CURRENT_ROLE="$ROLE"
    export UDOS_WORK_DIR="$UDOS_ROOT/$ROLE"
    
    # Create role session directory
    local session_dir="$UDOS_ROOT/$ROLE/sessions/$(date +%Y%m%d-%H%M%S)"
    mkdir -p "$session_dir"
    export UDOS_SESSION_DIR="$session_dir"
    
    # Change to role working directory
    cd "$UDOS_WORK_DIR"
    
    echo -e "${GREEN}✅ Environment initialized${NC}"
    echo -e "${CYAN}📁 Working directory: $UDOS_WORK_DIR${NC}"
    echo ""
}

# Start uSERVER for role
start_userver() {
    if [[ -f "$UDOS_ROOT/uSERVER/start-server.sh" ]]; then
        echo -e "${BLUE}🔧 Starting uSERVER for $UDOS_ROLE_NAME...${NC}"
        
        # Export role information for server
        export UDOS_SERVER_ROLE="$ROLE"
        export UDOS_SERVER_ACCESS_LEVEL="$UDOS_ACCESS_LEVEL"
        export UDOS_SERVER_PORT="$UDOS_SERVER_PORT"
        export UDOS_SERVER_HOST="127.0.0.1"
        
        # Start server with role configuration
        "$UDOS_ROOT/uSERVER/start-server.sh" \
            --role="$ROLE" \
            --port="$UDOS_SERVER_PORT" \
            --daemon
            
        # Wait for server to start
        local max_attempts=15
        local attempt=1
        
        while [[ $attempt -le $max_attempts ]]; do
            if curl -s "http://127.0.0.1:${UDOS_SERVER_PORT}/api/status" >/dev/null 2>&1; then
                echo -e "${GREEN}✅ uSERVER started on port $UDOS_SERVER_PORT${NC}"
                return 0
            fi
            echo -e "${YELLOW}⏳ Waiting for uSERVER... ($attempt/$max_attempts)${NC}"
            sleep 1
            ((attempt++))
        done
        
        echo -e "${RED}❌ uSERVER failed to start${NC}"
        return 1
    else
        echo -e "${YELLOW}⚠️  uSERVER not available${NC}"
        return 1
    fi
}

# Launch UI omniview
launch_ui_omniview() {
    if [[ "$UI_MODE" == "true" ]]; then
        echo -e "${CYAN}🌐 Launching UI omniview...${NC}"
        
        local ui_url="http://127.0.0.1:${UDOS_UI_PORT}?role=${ROLE}&level=${UDOS_ACCESS_LEVEL}"
        
        # Open browser
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
        
        echo -e "${GREEN}✅ UI omniview launched${NC}"
        echo -e "${CYAN}🌐 URL: $ui_url${NC}"
    fi
}

# Start role-specific CLI
start_role_cli() {
    echo ""
    echo -e "${WHITE}🖥️  $UDOS_ROLE_NAME CLI Operations${NC}"
    echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
    echo ""
    echo -e "${WHITE}Available commands:${NC}"
    echo "  status      - Show system status"
    echo "  logs        - View system logs"
    echo "  capabilities- Show role capabilities"
    echo "  session     - Session information"
    echo "  ui          - Open UI omniview"
    echo "  quit        - Exit $UDOS_ROLE_NAME mode"
    echo ""
    
    # CLI command loop
    role_cli_loop
}

# Role CLI command loop
role_cli_loop() {
    while true; do
        read -p "${UDOS_ROLE_ICON}${UDOS_ROLE_NAME}> " -r command args
        
        case "$command" in
            "status")
                show_role_status
                ;;
            "logs")
                show_role_logs
                ;;
            "capabilities")
                show_role_capabilities
                ;;
            "session")
                show_session_info
                ;;
            "ui")
                open_ui_omniview
                ;;
            "quit"|"exit")
                echo -e "${YELLOW}👋 Exiting $UDOS_ROLE_NAME mode${NC}"
                break
                ;;
            "")
                # Empty command, continue
                ;;
            *)
                echo -e "${RED}Unknown command: $command${NC}"
                echo "Type 'quit' to exit"
                ;;
        esac
    done
}

# Status and information functions
show_role_status() {
    echo -e "${BLUE}📊 $UDOS_ROLE_NAME Status${NC}"
    echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
    echo -e "${WHITE}Role:${NC} $UDOS_ROLE_ICON $UDOS_ROLE_NAME (Level $UDOS_ACCESS_LEVEL)"
    echo -e "${WHITE}Working Directory:${NC} $UDOS_WORK_DIR"
    echo -e "${WHITE}Session Directory:${NC} $UDOS_SESSION_DIR"
    echo -e "${WHITE}Capabilities:${NC} $UDOS_CAPABILITIES"
    
    # Check server status
    if curl -s "http://127.0.0.1:${UDOS_SERVER_PORT}/api/status" >/dev/null 2>&1; then
        echo -e "${WHITE}uSERVER:${NC} ${GREEN}✅ Running${NC} (Port $UDOS_SERVER_PORT)"
    else
        echo -e "${WHITE}uSERVER:${NC} ${RED}❌ Not running${NC}"
    fi
    
    echo ""
}

show_role_logs() {
    local log_file="$UDOS_ROOT/$ROLE/logs/$(date +%Y%m%d).log"
    if [[ -f "$log_file" ]]; then
        echo -e "${BLUE}📋 Recent $UDOS_ROLE_NAME logs:${NC}"
        tail -20 "$log_file"
    else
        echo -e "${YELLOW}ℹ️  No logs found for today${NC}"
    fi
}

show_role_capabilities() {
    echo -e "${BLUE}🔧 $UDOS_ROLE_NAME Capabilities${NC}"
    echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
    IFS=',' read -ra CAPS <<< "$UDOS_CAPABILITIES"
    for cap in "${CAPS[@]}"; do
        echo -e "  ${GREEN}✅${NC} $cap"
    done
    echo ""
}

show_session_info() {
    echo -e "${BLUE}📅 Session Information${NC}"
    echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
    echo -e "${WHITE}Session ID:${NC} $(basename "$UDOS_SESSION_DIR")"
    echo -e "${WHITE}Started:${NC} $(date)"
    echo -e "${WHITE}PID:${NC} $$"
    echo ""
}

open_ui_omniview() {
    local ui_url="http://127.0.0.1:${UDOS_UI_PORT}?role=${ROLE}&level=${UDOS_ACCESS_LEVEL}"
    echo -e "${CYAN}🌐 Opening UI omniview...${NC}"
    
    case "$(uname -s)" in
        Darwin) open "$ui_url" ;;
        Linux)  xdg-open "$ui_url" 2>/dev/null || echo "Open browser to: $ui_url" ;;
        *)      echo "Open browser to: $ui_url" ;;
    esac
}

# Main execution
main() {
    configure_role
    show_role_banner
    check_role_permissions
    initialize_role_environment
    
    if [[ "$SERVER_ONLY" == "false" ]]; then
        # Start uSERVER
        if start_userver; then
            # Launch UI if requested
            launch_ui_omniview
            # Start CLI interface
            start_role_cli
        else
            echo -e "${YELLOW}⚠️  Starting without uSERVER${NC}"
            start_role_cli
        fi
    else
        # Server-only mode
        start_userver
        if [[ $? -eq 0 ]]; then
            echo -e "${GREEN}✅ uSERVER started in server-only mode${NC}"
            echo -e "${CYAN}🌐 URL: http://127.0.0.1:${UDOS_SERVER_PORT}${NC}"
        else
            echo -e "${RED}❌ Failed to start uSERVER${NC}"
            exit 1
        fi
    fi
}

# Execute main function
main
