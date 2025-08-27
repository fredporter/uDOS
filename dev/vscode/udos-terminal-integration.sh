#!/bin/bash
# uDOS VS Code Terminal Integration
# Makes VS Code feel like native uDOS with persistent CLI output stream

set -euo pipefail

UDOS_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
export UDOS_ROOT

# Colors for VS Code terminal
readonly GREEN='\033[0;32m'
readonly BLUE='\033[0;34m'
readonly YELLOW='\033[1;33m'
readonly WHITE='\033[1;37m'
readonly NC='\033[0m'

echo -e "${WHITE}🧙‍♂️ uDOS Development Terminal${NC}"
echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"

# Start uDOS in VS Code terminal mode
start_udos_terminal() {
    echo -e "${BLUE}🌀 Starting uDOS CLI stream in VS Code...${NC}"
    
    # Set VS Code terminal mode
    export UDOS_VSCODE_MODE="true"
    export UDOS_TERMINAL_INTEGRATION="true"
    export UDOS_OUTPUT_STREAM="vscode-terminal"
    
    # Start uDOS with persistent terminal
    cd "$UDOS_ROOT"
    exec ./uCORE/code/ucode.sh
}

# Monitor mode - keep terminal as output stream
monitor_udos() {
    echo -e "${YELLOW}📊 uDOS Output Stream (VS Code Terminal)${NC}"
    echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
    
    # Tail uDOS logs in real-time
    tail -f "$UDOS_ROOT/sandbox/logs/"*.log 2>/dev/null || {
        echo -e "${YELLOW}⏳ Waiting for uDOS session logs...${NC}"
        sleep 2
        monitor_udos
    }
}

# Integration mode - VS Code as uDOS frontend
integration_mode() {
    echo -e "${GREEN}🔗 VS Code + uDOS Integration Mode${NC}"
    echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
    
    # Start background services
    start_udos_services
    
    # Keep terminal as output stream
    monitor_udos
}

start_udos_services() {
    # Start uDOS core in background
    cd "$UDOS_ROOT"
    ./uCORE/code/ucode.sh --daemon &
    
    # Start web export for preview
    ./uNETWORK/display/udos-display.sh export dashboard &
    
    echo -e "${GREEN}✅ uDOS services running${NC}"
    echo -e "${BLUE}   CLI: This terminal (output stream)${NC}"
    echo -e "${BLUE}   Web: http://localhost:8080${NC}"
    echo -e "${BLUE}   Desktop: Available via tasks${NC}"
}

# Main execution
case "${1:-terminal}" in
    "terminal")
        start_udos_terminal
        ;;
    "monitor")
        monitor_udos
        ;;
    "integration")
        integration_mode
        ;;
    *)
        echo "Usage: $0 {terminal|monitor|integration}"
        exit 1
        ;;
esac
