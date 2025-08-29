#!/bin/bash

# uDOS Simple Browser Launcher v1.0.5.1
# Manages the Electron-based browser for uDOS services

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
UDOS_ROOT="$(cd "$SCRIPT_DIR/../.." && pwd)"
BROWSER_DIR="$SCRIPT_DIR"

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

# Check if Node.js is available
check_nodejs() {
    if ! command -v node >/dev/null 2>&1; then
        echo -e "${RED}❌ Node.js not found${NC}"
        echo "Please install Node.js to use uDOS Simple Browser"
        echo "Visit: https://nodejs.org/"
        return 1
    fi
    
    local node_version
    node_version=$(node --version | cut -d'v' -f2)
    echo -e "${GREEN}✅ Node.js found: v$node_version${NC}"
    return 0
}

# Check if Electron is installed
check_electron() {
    cd "$BROWSER_DIR"
    
    if [[ ! -d "node_modules" ]] || ! npm list electron >/dev/null 2>&1; then
        echo -e "${YELLOW}⚠️  Electron dependencies not found${NC}"
        return 1
    fi
    
    echo -e "${GREEN}✅ Electron dependencies found${NC}"
    return 0
}

# Install dependencies
install_dependencies() {
    echo -e "${BLUE}📦 Installing Simple Browser dependencies...${NC}"
    cd "$BROWSER_DIR"
    
    if ! npm install; then
        echo -e "${RED}❌ Failed to install dependencies${NC}"
        return 1
    fi
    
    echo -e "${GREEN}✅ Dependencies installed successfully${NC}"
    return 0
}

# Start the browser
start_browser() {
    echo -e "${BLUE}🌐 Starting uDOS Simple Browser...${NC}"
    cd "$BROWSER_DIR"
    
    # Check if already running
    if pgrep -f "simple-browser.js" >/dev/null; then
        echo -e "${YELLOW}⚠️  Simple Browser already running${NC}"
        return 0
    fi
    
    # Start browser
    if npm start; then
        echo -e "${GREEN}✅ Simple Browser started${NC}"
        return 0
    else
        echo -e "${RED}❌ Failed to start Simple Browser${NC}"
        return 1
    fi
}

# Stop the browser
stop_browser() {
    echo -e "${BLUE}🛑 Stopping uDOS Simple Browser...${NC}"
    
    local pids
    pids=$(pgrep -f "simple-browser.js" || true)
    
    if [[ -z "$pids" ]]; then
        echo -e "${YELLOW}⚠️  Simple Browser not running${NC}"
        return 0
    fi
    
    for pid in $pids; do
        kill "$pid" 2>/dev/null || true
    done
    
    echo -e "${GREEN}✅ Simple Browser stopped${NC}"
    return 0
}

# Show browser status
show_status() {
    echo "🌐 uDOS Simple Browser Status"
    echo "─────────────────────────────────"
    
    # Node.js status
    echo -n "Node.js: "
    if check_nodejs >/dev/null 2>&1; then
        local version
        version=$(node --version)
        echo -e "${GREEN}Available ($version)${NC}"
    else
        echo -e "${RED}Not Available${NC}"
    fi
    
    # Dependencies status
    echo -n "Dependencies: "
    if check_electron >/dev/null 2>&1; then
        echo -e "${GREEN}Installed${NC}"
    else
        echo -e "${YELLOW}Missing${NC}"
    fi
    
    # Running status
    echo -n "Browser Process: "
    if pgrep -f "simple-browser.js" >/dev/null; then
        local pid
        pid=$(pgrep -f "simple-browser.js")
        echo -e "${GREEN}Running (PID: $pid)${NC}"
    else
        echo -e "${RED}Not Running${NC}"
    fi
    
    # Configuration
    echo ""
    echo "Configuration:"
    echo "  Location: $BROWSER_DIR"
    echo "  Main Script: simple-browser.js"
    echo "  UI File: browser-ui.html"
    echo "  Package: package.json"
}

# Setup browser (install dependencies)
setup_browser() {
    echo -e "${BLUE}🔧 Setting up uDOS Simple Browser...${NC}"
    
    if ! check_nodejs; then
        echo -e "${RED}❌ Setup failed: Node.js required${NC}"
        return 1
    fi
    
    if ! install_dependencies; then
        echo -e "${RED}❌ Setup failed: Could not install dependencies${NC}"
        return 1
    fi
    
    echo -e "${GREEN}✅ Simple Browser setup complete${NC}"
    echo ""
    echo "🚀 Ready to launch with:"
    echo "  $0 start"
    return 0
}

# Open browser with specific URL
open_url() {
    local url="$1"
    echo -e "${BLUE}🌐 Opening URL in Simple Browser: $url${NC}"
    
    # Start browser if not running
    if ! pgrep -f "simple-browser.js" >/dev/null; then
        start_browser &
        sleep 3  # Give it time to start
    fi
    
    # TODO: Send URL to running browser instance
    echo -e "${GREEN}✅ Browser launched (navigate manually to: $url)${NC}"
}

# Show help
show_help() {
    echo "uDOS Simple Browser Launcher v1.0.5.1"
    echo ""
    echo "Usage: $0 [command] [args]"
    echo ""
    echo "Commands:"
    echo "  start        - Start the Simple Browser"
    echo "  stop         - Stop the Simple Browser"
    echo "  restart      - Restart the Simple Browser"
    echo "  status       - Show browser status"
    echo "  setup        - Install dependencies and setup"
    echo "  open [url]   - Open specific URL in browser"
    echo "  help         - Show this help"
    echo ""
    echo "Examples:"
    echo "  $0 setup                              # First-time setup"
    echo "  $0 start                              # Start browser"
    echo "  $0 open http://localhost:8080         # Open uDOS dashboard"
    echo "  $0 status                             # Check status"
    echo ""
    echo "Requirements:"
    echo "  • Node.js 16+ (https://nodejs.org/)"
    echo "  • Electron (installed via npm)"
    echo ""
    echo "uDOS Simple Browser provides secure access to localhost services"
    echo "with integrated toast notifications and uDOS system integration."
}

# Main command handling
main() {
    case "${1:-help}" in
        "start")
            if ! check_nodejs || ! check_electron; then
                echo -e "${YELLOW}⚠️  Dependencies missing. Run '$0 setup' first${NC}"
                exit 1
            fi
            start_browser
            ;;
        "stop")
            stop_browser
            ;;
        "restart")
            stop_browser
            sleep 2
            if check_nodejs && check_electron; then
                start_browser
            else
                echo -e "${YELLOW}⚠️  Dependencies missing. Run '$0 setup' first${NC}"
                exit 1
            fi
            ;;
        "status")
            show_status
            ;;
        "setup")
            setup_browser
            ;;
        "open")
            local url="${2:-http://localhost:8080}"
            open_url "$url"
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
}

main "$@"
