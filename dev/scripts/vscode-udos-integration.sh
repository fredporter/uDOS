#!/bin/bash

# uDOS + VS Code Integration Manager
# Ensures uDOS is always running alongside VS Code development

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
UDOS_ROOT="$(cd "$SCRIPT_DIR/../.." && pwd)"

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
PURPLE='\033[0;35m'
NC='\033[0m'

# Integration state files
INTEGRATION_PID_FILE="$UDOS_ROOT/dev/vscode-udos-integration.pid"
UDOS_MONITOR_PID_FILE="$UDOS_ROOT/dev/udos-monitor.pid"

# Check if uDOS is running
check_udos_status() {
    local udos_processes=$(ps aux | grep -E "(command-router|udos)" | grep -v grep | wc -l)
    
    if [ "$udos_processes" -gt 0 ]; then
        echo -e "${GREEN}✅ uDOS processes detected ($udos_processes)${NC}"
        return 0
    else
        echo -e "${RED}❌ No uDOS processes running${NC}"
        return 1
    fi
}

# Start uDOS terminal integration
start_udos_terminal() {
    echo -e "${BLUE}🌀 Starting uDOS Terminal Integration...${NC}"
    
    # Source the simple terminal test to get uDOS running
    if [[ -f "$UDOS_ROOT/dev/vscode/simple-terminal-test.sh" ]]; then
        cd "$UDOS_ROOT"
        source ./dev/vscode/simple-terminal-test.sh
        echo -e "${GREEN}✅ uDOS terminal environment loaded${NC}"
    else
        echo -e "${YELLOW}⚠️  Simple terminal test not found${NC}"
    fi
}

# Start uDOS command monitoring
start_udos_monitor() {
    local monitor_script="$UDOS_ROOT/dev/scripts/udos-vscode-monitor.sh"
    
    cat > "$monitor_script" << 'EOF'
#!/bin/bash
# uDOS + VS Code Integration Monitor

UDOS_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
PID_FILE="$UDOS_ROOT/dev/udos-monitor.pid"

# Check if already running
if [[ -f "$PID_FILE" ]] && kill -0 "$(cat "$PID_FILE")" 2>/dev/null; then
    echo "uDOS monitor already running (PID: $(cat "$PID_FILE"))"
    exit 0
fi

# Store PID
echo $$ > "$PID_FILE"

echo "🖥️  Starting uDOS + VS Code Integration Monitor (PID: $$)"

while true; do
    # Check if VS Code is running
    if pgrep -f "Visual Studio Code" >/dev/null; then
        # VS Code is running - ensure uDOS is accessible
        cd "$UDOS_ROOT"
        
        # Test uDOS command router
        if ! timeout 5s ./uCORE/code/command-router.sh "[STATUS]" >/dev/null 2>&1; then
            echo "$(date): uDOS command router not responding - attempting restart"
            source ./dev/vscode/simple-terminal-test.sh >/dev/null 2>&1 || true
        fi
        
        # Ensure completion is available
        if ! type udos >/dev/null 2>&1; then
            echo "$(date): uDOS completion not available - reloading"
            source ./dev/vscode/simple-terminal-test.sh >/dev/null 2>&1 || true
        fi
    fi
    
    sleep 30  # Check every 30 seconds
done
EOF

    chmod +x "$monitor_script"
    
    # Start in background
    nohup "$monitor_script" > "$UDOS_ROOT/dev/udos-monitor.log" 2>&1 &
    
    echo -e "${GREEN}🖥️  uDOS + VS Code monitor started${NC}"
}

# Stop uDOS monitor
stop_udos_monitor() {
    if [[ -f "$UDOS_MONITOR_PID_FILE" ]]; then
        local pid=$(cat "$UDOS_MONITOR_PID_FILE")
        if kill -0 "$pid" 2>/dev/null; then
            kill "$pid"
            rm -f "$UDOS_MONITOR_PID_FILE"
            echo -e "${GREEN}🛑 uDOS monitor stopped${NC}"
        else
            rm -f "$UDOS_MONITOR_PID_FILE"
            echo -e "${YELLOW}⚠️  uDOS monitor was not running${NC}"
        fi
    fi
}

# Start development session with full integration
start_development_session() {
    echo "┌─────────────────────────────────────────┐"
    echo "│     🚀 uDOS + VS Code Development       │"
    echo "│         Integration Starting            │"
    echo "└─────────────────────────────────────────┘"
    echo ""
    
    # 1. Start uDOS terminal integration
    start_udos_terminal
    echo ""
    
    # 2. Implement safety protocol
    echo -e "${PURPLE}🛡️  Implementing development safety protocol...${NC}"
    "$UDOS_ROOT/dev/scripts/development-safety-protocol.sh" implement
    echo ""
    
    # 3. Start uDOS monitoring
    start_udos_monitor
    echo ""
    
    # 4. Test uDOS commands work
    echo -e "${BLUE}🧪 Testing uDOS command integration...${NC}"
    cd "$UDOS_ROOT"
    
    if timeout 10s ./uCORE/code/command-router.sh "[STATUS]" >/dev/null 2>&1; then
        echo -e "${GREEN}✅ uDOS command router responding${NC}"
    else
        echo -e "${YELLOW}⚠️  uDOS command router timeout - may need manual intervention${NC}"
    fi
    
    # 5. Test auto-completion
    if type udos >/dev/null 2>&1; then
        echo -e "${GREEN}✅ uDOS auto-completion available${NC}"
    else
        echo -e "${YELLOW}⚠️  uDOS auto-completion not loaded${NC}"
    fi
    
    echo ""
    echo -e "${GREEN}🎉 Development session ready!${NC}"
    echo ""
    echo "🔧 Active Integrations:"
    echo "  • uDOS command router accessible"
    echo "  • Auto-completion enabled (udos <TAB>)"
    echo "  • Development safety protocol active"
    echo "  • Background monitoring running"
    echo "  • Auto-commit every 30 minutes"
    echo "  • Auto-backup every 15 minutes"
    echo ""
    echo "📋 Available Commands:"
    echo "  ./uCORE/code/command-router.sh '[COMMAND]'"
    echo "  udos [command] (with auto-completion)"
    echo "  ./dev/scripts/development-safety-protocol.sh [action]"
    echo ""
}

# Show integration status
show_integration_status() {
    echo "🖥️  uDOS + VS Code Integration Status"
    echo "───────────────────────────────────────"
    
    # VS Code status
    echo -n "VS Code: "
    if pgrep -f "Visual Studio Code" >/dev/null; then
        echo -e "${GREEN}Running${NC}"
    else
        echo -e "${YELLOW}Not Detected${NC}"
    fi
    
    # uDOS status
    echo -n "uDOS Processes: "
    check_udos_status || true
    
    # Command router test
    echo -n "Command Router: "
    cd "$UDOS_ROOT"
    if timeout 5s ./uCORE/code/command-router.sh "[STATUS]" >/dev/null 2>&1; then
        echo -e "${GREEN}Responsive${NC}"
    else
        echo -e "${RED}Not Responding${NC}"
    fi
    
    # Auto-completion
    echo -n "Auto-completion: "
    if type udos >/dev/null 2>&1; then
        echo -e "${GREEN}Available${NC}"
    else
        echo -e "${YELLOW}Not Loaded${NC}"
    fi
    
    # Monitor status
    echo -n "Integration Monitor: "
    if [[ -f "$UDOS_MONITOR_PID_FILE" ]] && kill -0 "$(cat "$UDOS_MONITOR_PID_FILE")" 2>/dev/null; then
        echo -e "${GREEN}Running (PID: $(cat "$UDOS_MONITOR_PID_FILE"))${NC}"
    else
        echo -e "${RED}Not Running${NC}"
    fi
    
    # Safety protocol status
    echo -n "Safety Protocol: "
    local safety_pid_file="$UDOS_ROOT/dev/safety-monitor.pid"
    if [[ -f "$safety_pid_file" ]] && kill -0 "$(cat "$safety_pid_file")" 2>/dev/null; then
        echo -e "${GREEN}Active${NC}"
    else
        echo -e "${RED}Not Active${NC}"
    fi
}

# Test uDOS commands
test_udos_commands() {
    echo -e "${BLUE}🧪 Testing uDOS command integration...${NC}"
    cd "$UDOS_ROOT"
    
    echo "Testing basic status command:"
    if timeout 10s ./uCORE/code/command-router.sh "[STATUS]"; then
        echo -e "${GREEN}✅ Status command works${NC}"
    else
        echo -e "${RED}❌ Status command failed${NC}"
    fi
    
    echo ""
    echo "Testing role command:"
    if timeout 10s ./uCORE/code/command-router.sh "[ROLE]"; then
        echo -e "${GREEN}✅ Role command works${NC}"
    else
        echo -e "${RED}❌ Role command failed${NC}"
    fi
    
    echo ""
    echo "Testing help command:"
    if timeout 10s ./uCORE/code/command-router.sh "[HELP]"; then
        echo -e "${GREEN}✅ Help command works${NC}"
    else
        echo -e "${RED}❌ Help command failed${NC}"
    fi
}

# Emergency restart function
emergency_restart() {
    echo -e "${YELLOW}🚨 Emergency restart of uDOS integration...${NC}"
    
    # Stop all monitors
    stop_udos_monitor
    "$UDOS_ROOT/dev/scripts/development-safety-protocol.sh" stop-monitor 2>/dev/null || true
    
    # Wait a moment
    sleep 2
    
    # Restart everything
    start_development_session
}

# Help function
show_help() {
    echo "uDOS + VS Code Integration Manager v1.0"
    echo ""
    echo "Usage: $0 [command]"
    echo ""
    echo "Commands:"
    echo "  start        - Start full development session integration"
    echo "  status       - Show integration status"
    echo "  test         - Test uDOS commands"
    echo "  restart      - Emergency restart of integration"
    echo "  stop         - Stop all integration monitors"
    echo "  help         - Show this help"
    echo ""
    echo "This script ensures uDOS runs alongside VS Code with:"
    echo "  • Command router accessibility"
    echo "  • Auto-completion support"
    echo "  • Development safety protocols"
    echo "  • Background monitoring"
}

# Command handling
case "${1:-help}" in
    "start")
        start_development_session
        ;;
    "status")
        show_integration_status
        ;;
    "test")
        test_udos_commands
        ;;
    "restart")
        emergency_restart
        ;;
    "stop")
        stop_udos_monitor
        "$UDOS_ROOT/dev/scripts/development-safety-protocol.sh" stop-monitor 2>/dev/null || true
        echo -e "${GREEN}🛑 All integration monitors stopped${NC}"
        ;;
    "help"|"-h"|"--help")
        show_help
        ;;
    *)
        echo "❌ Unknown command: $1"
        show_help
        exit 1
        ;;
esac
