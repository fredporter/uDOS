#!/bin/bash
# uSERVER Startup Script v1.3.1
# Integrated with uCORE for complete system management

set -euo pipefail

# Configuration
export UDOS_ROOT="${UDOS_ROOT:-$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)}"
export USERVER_PORT="${USERVER_PORT:-8080}"
export USERVER_HOST="${USERVER_HOST:-127.0.0.1}"

# Color definitions
readonly RED='\033[0;31m'
readonly GREEN='\033[0;32m'
readonly YELLOW='\033[1;33m'
readonly BLUE='\033[0;34m'
readonly PURPLE='\033[0;35m'
readonly CYAN='\033[0;36m'
readonly WHITE='\033[1;37m'
readonly NC='\033[0m'

# Server state
SERVER_PID=""
DAEMON_MODE=false
ROLE="${UDOS_CURRENT_ROLE:-wizard}"

# Parse arguments
while [[ $# -gt 0 ]]; do
    case $1 in
        --daemon)
            DAEMON_MODE=true
            shift
            ;;
        --role=*)
            ROLE="${1#*=}"
            shift
            ;;
        --port=*)
            USERVER_PORT="${1#*=}"
            shift
            ;;
        --help)
            show_help
            exit 0
            ;;
        *)
            echo -e "${RED}Unknown option: $1${NC}"
            exit 1
            ;;
    esac
done

show_help() {
    echo "uSERVER Startup Script v1.3.1"
    echo ""
    echo "Usage: $0 [OPTIONS]"
    echo ""
    echo "Options:"
    echo "  --daemon       Run in daemon mode"
    echo "  --role=ROLE    Set user role (default: wizard)"
    echo "  --port=PORT    Set server port (default: 8080)"
    echo "  --help         Show this help"
}

# Check Python availability
check_python() {
    if command -v python3 >/dev/null 2>&1; then
        PYTHON_CMD="python3"
    elif command -v python >/dev/null 2>&1; then
        PYTHON_CMD="python"
    else
        echo -e "${RED}❌ Python not found${NC}"
        echo "Please install Python 3.7+ to run uSERVER"
        exit 1
    fi
    
    # Check Python version
    local python_version=$($PYTHON_CMD --version 2>&1 | cut -d' ' -f2)
    echo -e "${GREEN}✅ Python $python_version${NC}"
}

# Install Python dependencies
install_dependencies() {
    echo -e "${BLUE}📦 Checking Python dependencies...${NC}"
    
    local requirements_file="$UDOS_ROOT/uSERVER/requirements.txt"
    
    if [[ -f "$requirements_file" ]]; then
        if $PYTHON_CMD -m pip install -r "$requirements_file" >/dev/null 2>&1; then
            echo -e "${GREEN}✅ Dependencies installed${NC}"
        else
            echo -e "${YELLOW}⚠️  Some dependencies may be missing${NC}"
        fi
    else
        echo -e "${YELLOW}⚠️  Requirements file not found${NC}"
    fi
}

# Run system setup check
run_setup_check() {
    echo -e "${BLUE}🔧 Running uCORE integration setup...${NC}"
    
    # Run uCORE startup sequence
    local startup_script="$UDOS_ROOT/uCORE/code/startup.sh"
    if [[ -f "$startup_script" ]]; then
        echo -e "${CYAN}🚀 Running uCORE startup sequence...${NC}"
        if bash "$startup_script" 2>/dev/null; then
            echo -e "${GREEN}✅ uCORE startup completed${NC}"
        else
            echo -e "${YELLOW}⚠️  uCORE startup had warnings${NC}"
        fi
    fi
    
    # Run setup check
    local setup_check="$UDOS_ROOT/uSERVER/setup-check.py"
    if [[ -f "$setup_check" ]]; then
        echo -e "${CYAN}🔍 Running system setup check...${NC}"
        if $PYTHON_CMD "$setup_check" 2>/dev/null; then
            echo -e "${GREEN}✅ System setup check passed${NC}"
        else
            echo -e "${YELLOW}⚠️  Setup check had warnings${NC}"
        fi
    fi
}

# Start uSERVER
start_server() {
    echo -e "${BLUE}🚀 Starting uSERVER...${NC}"
    echo -e "${CYAN}📍 Host: $USERVER_HOST${NC}"
    echo -e "${CYAN}🌐 Port: $USERVER_PORT${NC}"
    echo -e "${CYAN}🎭 Role: $ROLE${NC}"
    echo ""
    
    # Set environment variables for server
    export UDOS_CURRENT_ROLE="$ROLE"
    export UDOS_SERVER_MODE="integrated"
    export FLASK_ENV="development"
    
    # Change to server directory
    cd "$UDOS_ROOT/uSERVER"
    
    # Start server
    local server_script="$UDOS_ROOT/uSERVER/server.py"
    
    if [[ "$DAEMON_MODE" == "true" ]]; then
        echo -e "${BLUE}🔧 Starting in daemon mode...${NC}"
        $PYTHON_CMD "$server_script" >/dev/null 2>&1 &
        SERVER_PID=$!
        
        # Wait for server to start
        sleep 3
        
        if kill -0 "$SERVER_PID" 2>/dev/null; then
            echo -e "${GREEN}✅ uSERVER started successfully (PID: $SERVER_PID)${NC}"
            echo -e "${CYAN}🌐 Access UI: http://$USERVER_HOST:$USERVER_PORT${NC}"
            
            # Store PID for management
            echo "$SERVER_PID" > "$UDOS_ROOT/uSERVER/.server.pid"
        else
            echo -e "${RED}❌ Failed to start uSERVER${NC}"
            exit 1
        fi
    else
        echo -e "${BLUE}🔧 Starting in interactive mode...${NC}"
        echo -e "${YELLOW}Press Ctrl+C to stop server${NC}"
        echo ""
        
        # Trap for clean shutdown
        trap cleanup_server INT TERM
        
        $PYTHON_CMD "$server_script"
    fi
}

# Cleanup server on exit
cleanup_server() {
    if [[ -n "$SERVER_PID" ]]; then
        echo -e "\n${YELLOW}🛑 Stopping uSERVER...${NC}"
        kill "$SERVER_PID" 2>/dev/null || true
        rm -f "$UDOS_ROOT/uSERVER/.server.pid"
        echo -e "${GREEN}✅ uSERVER stopped${NC}"
    fi
    exit 0
}

# Show server status
show_status() {
    if [[ -f "$UDOS_ROOT/uSERVER/.server.pid" ]]; then
        local pid=$(cat "$UDOS_ROOT/uSERVER/.server.pid")
        if kill -0 "$pid" 2>/dev/null; then
            echo -e "${GREEN}✅ uSERVER is running (PID: $pid)${NC}"
            echo -e "${CYAN}🌐 URL: http://$USERVER_HOST:$USERVER_PORT${NC}"
        else
            echo -e "${RED}❌ uSERVER is not running${NC}"
            rm -f "$UDOS_ROOT/uSERVER/.server.pid"
        fi
    else
        echo -e "${RED}❌ uSERVER is not running${NC}"
    fi
}

# Stop server
stop_server() {
    if [[ -f "$UDOS_ROOT/uSERVER/.server.pid" ]]; then
        local pid=$(cat "$UDOS_ROOT/uSERVER/.server.pid")
        if kill -0 "$pid" 2>/dev/null; then
            echo -e "${YELLOW}🛑 Stopping uSERVER...${NC}"
            kill "$pid"
            rm -f "$UDOS_ROOT/uSERVER/.server.pid"
            echo -e "${GREEN}✅ uSERVER stopped${NC}"
        else
            echo -e "${YELLOW}⚠️  uSERVER was not running${NC}"
            rm -f "$UDOS_ROOT/uSERVER/.server.pid"
        fi
    else
        echo -e "${YELLOW}⚠️  uSERVER is not running${NC}"
    fi
}

# Main function
main() {
    echo -e "${PURPLE}"
    echo "   🔧 uSERVER - uDOS Integrated Server"
    echo "   ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
    echo -e "${NC}"
    echo -e "${WHITE}Omni-device uCODE Window Server v1.3.1${NC}"
    echo ""
    
    check_python
    install_dependencies
    run_setup_check
    start_server
}

# Handle special commands
case "${1:-start}" in
    "status")
        show_status
        exit 0
        ;;
    "stop")
        stop_server
        exit 0
        ;;
    "restart")
        stop_server
        sleep 2
        exec "$0" --daemon
        ;;
    "start"|"")
        main
        ;;
    *)
        main
        ;;
esac
