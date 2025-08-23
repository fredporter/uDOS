#!/bin/bash
# uSERVER Startup Script v1.3.3 - Enhanced with uSCRIPT venv Integration
# Integrated with uCORE for complete system management

set -euo pipefail

# Configuration
export UDOS_ROOT="${UDOS_ROOT:-$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)}"
export USERVER_PORT="${USERVER_PORT:-8080}"
export USERVER_HOST="${USERVER_HOST:-127.0.0.1}"
SERVER_PID_FILE="/tmp/udos-server.pid"
SERVER_LOCK_FILE="/tmp/udos-server.lock"
USCRIPT_VENV="$UDOS_ROOT/uSCRIPT/venv/python"

# Load error handler
source "$UDOS_ROOT/uCORE/system/error-handler.sh" 2>/dev/null || true

# Color definitions (compatible with error handler)
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
PURPLE='\033[0;35m'
CYAN='\033[0;36m'
WHITE='\033[1;37m'
NC='\033[0m'
readonly NC='\033[0m'

# Server state
SERVER_PID=""
DAEMON_MODE=false
ROLE="${UDOS_CURRENT_ROLE:-wizard}"

# Initialize error handling
init_error_logging
export UDOS_DEV_MODE="${UDOS_DEV_MODE:-true}"  # Enable dev mode for servers

# Parse arguments
DAEMON_MODE=false
ROLE="${UDOS_CURRENT_ROLE:-wizard}"
COMMAND=""

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
        status|stop|restart)
            COMMAND="$1"
            shift
            ;;
        --help)
            show_help
            exit 0
            ;;
        *)
            echo -e "${RED}Unknown option: $1${NC}"
            show_help
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

# Check for existing server instance
check_existing_server() {
    if [[ -f "$SERVER_PID_FILE" ]]; then
        local existing_pid=$(cat "$SERVER_PID_FILE")
        if kill -0 "$existing_pid" 2>/dev/null; then
            echo -e "${YELLOW}⚠️  uSERVER is already running (PID: $existing_pid)${NC}"
            echo -e "${CYAN}🌐 URL: http://$USERVER_HOST:$USERVER_PORT${NC}"
            echo ""
            echo -e "${WHITE}Options:${NC}"
            echo "  1. Stop existing and restart"
            echo "  2. Connect to existing server"
            echo "  3. Cancel"

            read -p "Choose option (1-3): " choice
            case $choice in
                1)
                    stop_existing_server
                    return 0
                    ;;
                2)
                    echo -e "${GREEN}✅ Connecting to existing server${NC}"
                    exit 0
                    ;;
                3)
                    echo -e "${YELLOW}Cancelled${NC}"
                    exit 0
                    ;;
                *)
                    echo -e "${RED}Invalid choice${NC}"
                    exit 1
                    ;;
            esac
        else
            # Clean up stale PID file
            rm -f "$SERVER_PID_FILE"
        fi
    fi

    # Check if port is in use by another process
    if lsof -Pi :$USERVER_PORT -sTCP:LISTEN -t >/dev/null 2>&1; then
        echo -e "${RED}❌ Port $USERVER_PORT is already in use by another process${NC}"
        exit 1
    fi
}

# Stop existing server
stop_existing_server() {
    if [[ -f "$SERVER_PID_FILE" ]]; then
        local pid=$(cat "$SERVER_PID_FILE")
        echo -e "${YELLOW}🛑 Stopping existing server (PID: $pid)...${NC}"

        # Try graceful shutdown first
        if kill -TERM "$pid" 2>/dev/null; then
            local count=0
            while kill -0 "$pid" 2>/dev/null && [[ $count -lt 10 ]]; do
                sleep 1
                ((count++))
            done

            # Force kill if still running
            if kill -0 "$pid" 2>/dev/null; then
                echo -e "${YELLOW}⚠️  Force killing server...${NC}"
                kill -KILL "$pid" 2>/dev/null || true
            fi
        fi

        rm -f "$SERVER_PID_FILE" "$SERVER_LOCK_FILE"
        echo -e "${GREEN}✅ Existing server stopped${NC}"
    fi

    # Also kill any stray python processes
    pkill -f "uNETWORK/server/server.py" 2>/dev/null || true
}
# Check Python availability and use uSCRIPT venv
check_python() {
    # First, try to use uSCRIPT virtual environment
    if [[ -f "$USCRIPT_VENV/bin/activate" ]]; then
        echo -e "${GREEN}✅ Using uSCRIPT virtual environment${NC}"
        source "$USCRIPT_VENV/bin/activate"
        PYTHON_CMD="python"
        USING_VENV=true
    elif command -v python3 >/dev/null 2>&1; then
        echo -e "${YELLOW}⚠️ uSCRIPT venv not found, using system Python${NC}"
        PYTHON_CMD="python3"
        USING_VENV=false
    elif command -v python >/dev/null 2>&1; then
        echo -e "${YELLOW}⚠️ uSCRIPT venv not found, using system Python${NC}"
        PYTHON_CMD="python"
        USING_VENV=false
    else
        echo -e "${RED}❌ Python not found${NC}"
        echo "Please install Python 3.7+ or set up uSCRIPT environment:"
        echo "  cd $UDOS_ROOT/uSCRIPT && ./setup-environment.sh"
        exit 1
    fi

    # Check Python version
    local python_version=$($PYTHON_CMD --version 2>&1 | cut -d' ' -f2)
    echo -e "${GREEN}✅ Python $python_version${NC}"

    if [[ "$USING_VENV" == "true" ]]; then
        echo -e "${BLUE}📦 Virtual environment: $USCRIPT_VENV${NC}"
    fi
}

# Install Python dependencies
install_dependencies() {
    echo -e "${BLUE}📦 Checking Python dependencies...${NC}"

    local requirements_file="$UDOS_ROOT/uNETWORK/server/requirements.txt"

    if [[ "$USING_VENV" == "true" ]]; then
        echo -e "${GREEN}✅ Using uSCRIPT virtual environment${NC}"
        echo -e "${BLUE}💡 Dependencies managed by uSCRIPT - run './uSCRIPT/setup-environment.sh' to update${NC}"
    elif [[ -f "$requirements_file" ]]; then
        if $PYTHON_CMD -m pip install -r "$requirements_file" >/dev/null 2>&1; then
            echo -e "${GREEN}✅ Dependencies installed${NC}"
        else
            echo -e "${YELLOW}⚠️  Some dependencies may be missing${NC}"
            echo -e "${BLUE}💡 Consider setting up uSCRIPT virtual environment: cd $UDOS_ROOT/uSCRIPT && ./setup-environment.sh${NC}"
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
    local setup_check="$UDOS_ROOT/uNETWORK/server/setup-check.py"
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

    # Create lock file
    echo $$ > "$SERVER_LOCK_FILE"

    # Set environment variables for server
    export UDOS_CURRENT_ROLE="$ROLE"
    export UDOS_SERVER_MODE="integrated"
    export FLASK_ENV="development"

    # Change to server directory
    cd "$UDOS_ROOT/uNETWORK/server"

    # Start server
    local server_script="$UDOS_ROOT/uNETWORK/server/server.py"

    if [[ "$DAEMON_MODE" == "true" ]]; then
        echo -e "${BLUE}🔧 Starting in daemon mode...${NC}"
        nohup $PYTHON_CMD "$server_script" >/dev/null 2>&1 &
        SERVER_PID=$!
        echo "$SERVER_PID" > "$SERVER_PID_FILE"

        # Wait for server to start and verify
        local attempts=0
        while [[ $attempts -lt 15 ]]; do
            if curl -s "http://$USERVER_HOST:$USERVER_PORT/api/status" >/dev/null 2>&1; then
                echo -e "${GREEN}✅ uSERVER started successfully (PID: $SERVER_PID)${NC}"
                echo -e "${CYAN}🌐 Access UI: http://$USERVER_HOST:$USERVER_PORT${NC}"
                return 0
            fi
            echo -e "${YELLOW}⏳ Waiting for server... ($((attempts + 1))/15)${NC}"
            sleep 1
            ((attempts++))
        done

        echo -e "${RED}❌ Failed to start uSERVER${NC}"
        stop_existing_server
        exit 1
    else
        echo -e "${BLUE}🔧 Starting in interactive mode...${NC}"
        echo -e "${YELLOW}Press Ctrl+C to stop server${NC}"
        echo ""

        # Store PID for cleanup
        echo $$ > "$SERVER_PID_FILE"

        # Trap for clean shutdown
        trap cleanup_server INT TERM

        exec $PYTHON_CMD "$server_script"
    fi
}

# Cleanup server on exit
cleanup_server() {
    echo -e "\n${YELLOW}🛑 Stopping uSERVER...${NC}"
    rm -f "$SERVER_PID_FILE" "$SERVER_LOCK_FILE"
    pkill -f "uNETWORK/server/server.py" 2>/dev/null || true
    echo -e "${GREEN}✅ uSERVER stopped${NC}"
    exit 0
}

# Show server status
show_status() {
    if [[ -f "$SERVER_PID_FILE" ]]; then
        local pid=$(cat "$SERVER_PID_FILE")
        if kill -0 "$pid" 2>/dev/null; then
            echo -e "${GREEN}✅ uSERVER is running (PID: $pid)${NC}"
            echo -e "${CYAN}🌐 URL: http://$USERVER_HOST:$USERVER_PORT${NC}"
        else
            echo -e "${RED}❌ uSERVER is not running${NC}"
            rm -f "$SERVER_PID_FILE" "$SERVER_LOCK_FILE"
        fi
    else
        echo -e "${RED}❌ uSERVER is not running${NC}"
    fi
}

# Stop server
stop_server() {
    if [[ -f "$SERVER_PID_FILE" ]]; then
        local pid=$(cat "$SERVER_PID_FILE")
        if kill -0 "$pid" 2>/dev/null; then
            echo -e "${YELLOW}🛑 Stopping uSERVER...${NC}"
            kill "$pid" 2>/dev/null || true
            rm -f "$SERVER_PID_FILE" "$SERVER_LOCK_FILE"
            echo -e "${GREEN}✅ uSERVER stopped${NC}"
        else
            echo -e "${YELLOW}⚠️  uSERVER was not running${NC}"
            rm -f "$SERVER_PID_FILE" "$SERVER_LOCK_FILE"
        fi
    else
        echo -e "${YELLOW}⚠️  uSERVER is not running${NC}"
    fi

    # Kill any stray processes
    pkill -f "uNETWORK/server/server.py" 2>/dev/null || true
}

# Main function
main() {
    echo -e "${PURPLE}"
    echo "   🔧 uSERVER - uDOS Integrated Server"
    echo "   ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
    echo -e "${NC}"
    echo -e "${WHITE}Omni-device uCODE Window Server v1.3.1${NC}"
    echo ""

    check_existing_server
    check_python
    install_dependencies
    run_setup_check
    start_server
}

# Handle special commands
if [[ -n "$COMMAND" ]]; then
    case "$COMMAND" in
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
            DAEMON_MODE=true
            # Continue to main function
            ;;
    esac
fi

# Handle special commands (legacy support)
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
