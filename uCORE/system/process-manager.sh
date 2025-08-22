#!/bin/bash
# uDOS Process Manager - Single Instance Control & Resource Management
set -euo pipefail

UDOS_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
UDOS_PID_DIR="/tmp/udos"
UDOS_LOCK_FILE="/tmp/udos/udos.lock"
UDOS_SERVER_PID="/tmp/udos/server.pid"
UDOS_SESSION_FILE="/tmp/udos/session.info"

# Colors
readonly RED='\033[0;31m'
readonly GREEN='\033[0;32m'
readonly YELLOW='\033[1;33m'
readonly BLUE='\033[0;34m'
readonly WHITE='\033[1;37m'
readonly NC='\033[0m'

# Ensure PID directory exists
mkdir -p "$UDOS_PID_DIR"

# Single instance enforcement
ensure_single_instance() {
    local component="$1"
    local force="${2:-false}"
    
    echo -e "${BLUE}🔍 Checking for existing uDOS instances...${NC}"
    
    # Check lock file
    if [ -f "$UDOS_LOCK_FILE" ]; then
        local existing_pid=$(cat "$UDOS_LOCK_FILE" 2>/dev/null || echo "")
        
        if [ -n "$existing_pid" ] && kill -0 "$existing_pid" 2>/dev/null; then
            if [ "$force" = "true" ]; then
                echo -e "${YELLOW}⚠️  Forcing shutdown of existing instance (PID: $existing_pid)${NC}"
                force_shutdown_all
            else
                echo -e "${RED}❌ uDOS is already running (PID: $existing_pid)${NC}"
                show_existing_session
                exit 1
            fi
        else
            echo -e "${YELLOW}🧹 Cleaning up stale lock file${NC}"
            rm -f "$UDOS_LOCK_FILE"
        fi
    fi
    
    # Create new lock
    echo $$ > "$UDOS_LOCK_FILE"
    echo -e "${GREEN}✅ Single instance lock acquired${NC}"
}

show_existing_session() {
    echo ""
    echo -e "${BLUE}📊 Existing uDOS Session:${NC}"
    echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
    
    if [ -f "$UDOS_SESSION_FILE" ]; then
        cat "$UDOS_SESSION_FILE"
    else
        echo "No session info available"
    fi
    
    echo ""
    echo -e "${WHITE}Options:${NC}"
    echo "  1. Connect to existing session: udos attach"
    echo "  2. Force restart: udos force"
    echo "  3. Stop current session: udos stop"
}

# Resource monitoring
check_system_resources() {
    echo -e "${BLUE}🔧 Checking system resources...${NC}"
    
    # Check memory usage
    local memory_usage=$(ps -A -o %mem | awk '{s+=$1} END {print s}')
    if (( $(echo "$memory_usage > 80" | bc -l 2>/dev/null || echo "0") )); then
        echo -e "${YELLOW}⚠️  High memory usage detected: ${memory_usage}%${NC}"
        echo "Consider closing other applications before starting uDOS"
        read -p "Continue anyway? [y/N]: " -n 1 -r
        echo
        if [[ ! $REPLY =~ ^[Yy]$ ]]; then
            exit 1
        fi
    fi
    
    # Check available ports
    if lsof -Pi :8080 -sTCP:LISTEN -t >/dev/null 2>&1; then
        local port_pid=$(lsof -Pi :8080 -sTCP:LISTEN -t)
        echo -e "${YELLOW}⚠️  Port 8080 is already in use by PID: $port_pid${NC}"
        
        # Check if it's our process
        if [ -f "$UDOS_SERVER_PID" ] && [ "$(cat $UDOS_SERVER_PID)" = "$port_pid" ]; then
            echo -e "${GREEN}✅ Port is used by existing uDOS server${NC}"
            return 0
        else
            echo -e "${RED}❌ Port is used by another process${NC}"
            return 1
        fi
    fi
    
    echo -e "${GREEN}✅ System resources OK${NC}"
}

# Controlled server startup
start_managed_server() {
    local mode="$1"
    
    echo -e "${BLUE}🚀 Starting uDOS server in managed mode...${NC}"
    
    # Kill any existing server
    stop_server_if_running
    
    # Start server with resource limits
    cd "$UDOS_ROOT"
    
    export UDOS_CURRENT_ROLE="wizard"
    export UDOS_ACCESS_LEVEL="100"
    export UDOS_DEV_MODE="true"
    export UDOS_MANAGED="true"
    
    python3 uSERVER/server.py &
    local server_pid=$!
    echo $server_pid > "$UDOS_SERVER_PID"
    
    # Wait for server to start
    local attempts=0
    while [ $attempts -lt 15 ]; do
        if curl -s http://localhost:8080/api/status >/dev/null 2>&1; then
            echo -e "${GREEN}✅ Server started successfully (PID: $server_pid)${NC}"
            record_session_info "$mode" "$server_pid"
            return 0
        fi
        echo -e "${YELLOW}⏳ Waiting for server... ($((attempts + 1))/15)${NC}"
        sleep 1
        ((attempts++))
    done
    
    echo -e "${RED}❌ Server failed to start${NC}"
    return 1
}

record_session_info() {
    local mode="$1"
    local server_pid="$2"
    
    cat > "$UDOS_SESSION_FILE" << EOF
🧙‍♂️ uDOS Session Information
━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Started: $(date)
Mode: $mode
Server PID: $server_pid
Lock PID: $$
UI URL: http://localhost:8080
Working Dir: $UDOS_ROOT
━━━━━━━━━━━━━━━━━━━━━━━━━━━━
EOF
}

stop_server_if_running() {
    if [ -f "$UDOS_SERVER_PID" ]; then
        local server_pid=$(cat "$UDOS_SERVER_PID")
        if kill -0 "$server_pid" 2>/dev/null; then
            echo -e "${YELLOW}🛑 Stopping existing server (PID: $server_pid)${NC}"
            kill -TERM "$server_pid" 2>/dev/null || true
            sleep 2
            kill -KILL "$server_pid" 2>/dev/null || true
        fi
        rm -f "$UDOS_SERVER_PID"
    fi
}

force_shutdown_all() {
    echo -e "${YELLOW}🧹 Force shutdown of all uDOS processes...${NC}"
    
    # Stop server
    stop_server_if_running
    
    # Kill any Python processes running uDOS
    pkill -f "uSERVER" 2>/dev/null || true
    pkill -f "udos" 2>/dev/null || true
    
    # Clean up lock files
    rm -f "$UDOS_LOCK_FILE"
    rm -f "$UDOS_SESSION_FILE"
    
    echo -e "${GREEN}✅ All uDOS processes stopped${NC}"
}

attach_to_session() {
    if [ ! -f "$UDOS_LOCK_FILE" ]; then
        echo -e "${RED}❌ No active uDOS session found${NC}"
        exit 1
    fi
    
    local session_pid=$(cat "$UDOS_LOCK_FILE")
    if ! kill -0 "$session_pid" 2>/dev/null; then
        echo -e "${RED}❌ Session PID is not running${NC}"
        force_shutdown_all
        exit 1
    fi
    
    echo -e "${BLUE}🔗 Attaching to existing uDOS session...${NC}"
    show_existing_session
    
    # Open UI in browser
    open http://localhost:8080 2>/dev/null || echo "Open browser to: http://localhost:8080"
    
    # Connect to session
    echo ""
    echo "Connected to uDOS session. Type 'quit' to detach."
    session_cli_loop
}

session_cli_loop() {
    while true; do
        read -p "🧙‍♂️ uDOS-SESSION> " -r command
        
        case "$command" in
            "status"|"s")
                show_session_status
                ;;
            "logs"|"l")
                show_dev_logs
                ;;
            "ui"|"u")
                open http://localhost:8080 2>/dev/null || echo "Open browser to: http://localhost:8080"
                echo -e "${GREEN}✅ UI opened in browser${NC}"
                ;;
            "restart"|"r")
                restart_session
                ;;
            "stop"|"shutdown")
                force_shutdown_all
                break
                ;;
            "quit"|"q"|"detach"|"exit")
                echo -e "${YELLOW}Detaching from session (server continues running)${NC}"
                break
                ;;
            "help"|"h"|"")
                echo "Commands: status(s), logs(l), ui(u), restart(r), stop, quit(q)"
                ;;
            *)
                echo -e "${RED}Unknown command: $command${NC} (try 'help')"
                ;;
        esac
    done
}

show_session_status() {
    echo -e "${BLUE}📊 Session Status:${NC}"
    echo "─────────────────────────────"
    
    if [ -f "$UDOS_SESSION_FILE" ]; then
        cat "$UDOS_SESSION_FILE"
    fi
    
    echo ""
    echo -e "${WHITE}🖥️  System Resources:${NC}"
    echo "   Memory: $(ps -A -o %mem | awk '{s+=$1} END {printf "%.1f%%", s}')"
    
    if [ -f "$UDOS_SERVER_PID" ]; then
        local server_pid=$(cat "$UDOS_SERVER_PID")
        if kill -0 "$server_pid" 2>/dev/null; then
            echo -e "   Server: ${GREEN}🟢 Running (PID: $server_pid)${NC}"
        else
            echo -e "   Server: ${RED}🔴 Not responding${NC}"
        fi
    else
        echo -e "   Server: ${RED}🔴 No PID file${NC}"
    fi
}

show_dev_logs() {
    echo -e "${BLUE}📋 Development Logs:${NC}"
    echo "─────────────────────"
    
    # Show recent logs
    if [ -f "$UDOS_ROOT/uSERVER/logs/server.log" ]; then
        tail -20 "$UDOS_ROOT/uSERVER/logs/server.log"
    else
        echo -e "${YELLOW}No server logs found${NC}"
        echo "Server should be logging to console..."
    fi
}

restart_session() {
    echo -e "${YELLOW}🔄 Restarting uDOS session...${NC}"
    
    # Get current mode
    local current_mode="development"
    if [ -f "$UDOS_SESSION_FILE" ]; then
        current_mode=$(grep "Mode:" "$UDOS_SESSION_FILE" | awk '{print $2}' 2>/dev/null || echo "development")
    fi
    
    # Restart server
    start_managed_server "$current_mode"
    
    echo -e "${GREEN}✅ Session restarted${NC}"
}

# Cleanup on exit
cleanup_on_exit() {
    if [ -f "$UDOS_LOCK_FILE" ] && [ "$(cat $UDOS_LOCK_FILE 2>/dev/null)" = "$$" ]; then
        echo ""
        echo -e "${YELLOW}🧹 Cleaning up session...${NC}"
        rm -f "$UDOS_LOCK_FILE"
        rm -f "$UDOS_SESSION_FILE"
    fi
}

trap cleanup_on_exit EXIT

# Export functions for use by other scripts
export -f ensure_single_instance
export -f check_system_resources
export -f start_managed_server
export -f force_shutdown_all
export -f attach_to_session
