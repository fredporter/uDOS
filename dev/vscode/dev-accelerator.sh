#!/bin/bash
# Enhanced VS Code Development Launcher for uDOS
# Provides fast development iteration with live reload

echo "🚀 uDOS Development Accelerator"
echo "=================================="

# Get script directory and uDOS root
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
UDOS_ROOT="$(cd "$SCRIPT_DIR/../../.." && pwd)"

# Color codes
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
RED='\033[0;31m'
NC='\033[0m'

# Check if VS Code is available
if ! command -v code >/dev/null 2>&1; then
    echo -e "${RED}❌ VS Code not found${NC}"
    echo "Please install VS Code and ensure 'code' command is available"
    exit 1
fi

# Function to check if server is running
check_server() {
    if pgrep -f "display-server.py" >/dev/null; then
        return 0
    else
        return 1
    fi
}

# Function to start development server
start_dev_server() {
    echo -e "${BLUE}🌐 Starting development server...${NC}"
    cd "$UDOS_ROOT"
    ./uNETWORK/display/udos-display.sh export dashboard >/dev/null 2>&1 &
    
    # Wait for server to start
    for i in {1..10}; do
        if check_server; then
            echo -e "${GREEN}✅ Development server running at http://localhost:8080${NC}"
            return 0
        fi
        sleep 1
    done
    
    echo -e "${RED}❌ Failed to start development server${NC}"
    return 1
}

# Function to reload server
reload_server() {
    echo -e "${YELLOW}🔄 Reloading development server...${NC}"
    pkill -f "display-server.py" >/dev/null 2>&1
    sleep 2
    start_dev_server
}

# Main development launcher
main() {
    case "${1:-start}" in
        "start")
            echo -e "${BLUE}📂 Opening uDOS in VS Code...${NC}"
            code "$UDOS_ROOT"
            
            echo -e "${BLUE}🧪 Running quick tests...${NC}"
            cd "$UDOS_ROOT"
            ./dev/scripts/test-first-time-launch.sh --quiet
            
            if ! check_server; then
                start_dev_server
            else
                echo -e "${GREEN}✅ Development server already running${NC}"
            fi
            
            echo ""
            echo -e "${GREEN}🎉 Development environment ready!${NC}"
            echo ""
            echo "Available commands:"
            echo "  • Ctrl+Shift+P → 'Tasks: Run Task' for quick actions"
            echo "  • F5 → Debug current script"
            echo "  • Ctrl+\` → Open integrated terminal"
            echo ""
            echo "Quick tasks available:"
            echo "  • 🎯 Dev: Test & Launch"
            echo "  • ⚡ Dev: Quick Reload Server"
            echo "  • 🔍 Dev: Watch Logs"
            echo "  • 🧹 Dev: Clean Sandbox"
            ;;
            
        "reload")
            reload_server
            ;;
            
        "stop")
            echo -e "${YELLOW}🛑 Stopping development server...${NC}"
            pkill -f "display-server.py" >/dev/null 2>&1
            echo -e "${GREEN}✅ Development server stopped${NC}"
            ;;
            
        "status")
            if check_server; then
                echo -e "${GREEN}✅ Development server running${NC}"
                echo "   URL: http://localhost:8080"
                echo "   PID: $(pgrep -f display-server.py)"
            else
                echo -e "${RED}❌ Development server not running${NC}"
            fi
            ;;
            
        "logs")
            echo -e "${BLUE}📝 Watching development logs...${NC}"
            echo "Press Ctrl+C to exit"
            tail -f "$UDOS_ROOT/sandbox/session/logs/display-server.log" 2>/dev/null || {
                echo -e "${YELLOW}⚠️  No logs found yet${NC}"
            }
            ;;
            
        "test")
            echo -e "${BLUE}🧪 Running comprehensive tests...${NC}"
            cd "$UDOS_ROOT"
            ./dev/scripts/test-first-time-launch.sh
            ;;
            
        "help"|*)
            echo "uDOS Development Accelerator"
            echo ""
            echo "Usage: $0 [command]"
            echo ""
            echo "Commands:"
            echo "  start   - Open VS Code and start development environment (default)"
            echo "  reload  - Reload the development server"
            echo "  stop    - Stop the development server"
            echo "  status  - Check development server status"
            echo "  logs    - Watch development logs"
            echo "  test    - Run comprehensive test suite"
            echo "  help    - Show this help message"
            ;;
    esac
}

# Run main function
main "$@"
