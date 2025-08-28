#!/bin/bash
# uDOS VS Code Terminal Integration v1.0.4.3
# Makes VS Code terminal a native uDOS interface with seamless command integration

set -euo pipefail

UDOS_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
export UDOS_ROOT

# Colors for VS Code terminal
readonly GREEN='\033[0;32m'
readonly BLUE='\033[0;34m'
readonly YELLOW='\033[1;33m'
readonly WHITE='\033[1;37m'
readonly PURPLE='\033[0;35m'
readonly NC='\033[0m'

# Terminal integration functions
source "$UDOS_ROOT/uCORE/code/logging.sh" 2>/dev/null || {
    log_info() { echo -e "\033[0;36m[INFO]\033[0m $1"; }
    log_success() { echo -e "\033[0;32m[SUCCESS]\033[0m $1"; }
    log_warning() { echo -e "\033[0;33m[WARNING]\033[0m $1"; }
    log_error() { echo -e "\033[0;31m[ERROR]\033[0m $1"; }
}

echo -e "${WHITE}🧙‍♂️ uDOS Development Terminal v1.0.4.3${NC}"
echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"

# Setup terminal environment for uDOS integration
setup_terminal_environment() {
    # Set VS Code terminal mode
    export UDOS_VSCODE_MODE="true"
    export UDOS_TERMINAL_INTEGRATION="true"
    export UDOS_OUTPUT_STREAM="vscode-terminal"
    export UDOS_EXPRESS_DEV="true"
    
    # Add uDOS commands to PATH
    export PATH="$UDOS_ROOT/uCORE/bin:$PATH"
    
    # Create terminal command aliases
    create_terminal_aliases
    
    # Setup command completion
    setup_command_completion
    
    log_success "Terminal environment configured for uDOS integration"
}

# Create seamless command aliases for VS Code terminal
create_terminal_aliases() {
    # Create temporary alias file
    local alias_file="$UDOS_ROOT/sandbox/temp/vscode-aliases.sh"
    mkdir -p "$(dirname "$alias_file")"
    
    cat > "$alias_file" << 'EOF'
# uDOS Terminal Integration Aliases v1.0.4.3

# Core uDOS command router - seamless integration
udos() {
    "$UDOS_ROOT/uCORE/code/command-router.sh" "$@"
}

# Express development commands
dash() {
    udos "[STATUS|DASHBOARD]"
}

assist() {
    if [[ "${1:-}" == "enter" ]]; then
        udos "[ASSIST|ENTER]"
    elif [[ "${1:-}" == "exit" ]]; then
        udos "[ASSIST|EXIT]"
    else
        udos "[ASSIST|STATUS]"
    fi
}

role() {
    udos "[ROLE]"
}

heal() {
    udos "[SYSTEM|HEAL]"
}

templates() {
    if [[ "${1:-}" == "list" ]]; then
        udos "[TEMPLATE|LIST]"
    elif [[ -n "${1:-}" ]]; then
        udos "[TEMPLATE|RENDER*$1]"
    else
        udos "[TEMPLATE|STATUS]"
    fi
}

# Quick template rendering
help_dev() {
    udos "[TEMPLATE|RENDER*help]"
}

# Development workflow commands
dev_status() {
    echo "🔧 uDOS Development Status"
    echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
    udos "[ROLE]"
    echo ""
    udos "[STATUS|DASHBOARD]"
}

# Express navigation
goto_dev() {
    cd "$UDOS_ROOT/dev" && pwd
}

goto_core() {
    cd "$UDOS_ROOT/uCORE" && pwd  
}

goto_sandbox() {
    cd "$UDOS_ROOT/sandbox" && pwd
}

# Show available uDOS commands
udos_help() {
    echo -e "\033[1;36m🧙‍♂️ uDOS Terminal Commands\033[0m"
    echo -e "\033[0;34m━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\033[0m"
    echo ""
    echo -e "\033[1;33m⚡ Express Commands:\033[0m"
    echo "  dash              - Show development dashboard"
    echo "  assist [enter]    - Enter/status ASSIST mode"
    echo "  role              - Show current role and permissions"
    echo "  heal              - Run self-healing dependency check"
    echo "  templates [name]  - List or render templates"
    echo "  help_dev          - Show context-aware help"
    echo ""
    echo -e "\033[1;33m🎯 Navigation:\033[0m"
    echo "  goto_dev          - Navigate to development directory"
    echo "  goto_core         - Navigate to uCORE directory"
    echo "  goto_sandbox      - Navigate to sandbox workspace"
    echo ""
    echo -e "\033[1;33m🔧 Development:\033[0m"
    echo "  dev_status        - Complete development status overview"
    echo "  udos '[COMMAND]'  - Execute any uDOS command directly"
    echo ""
    echo -e "\033[1;33m💡 Examples:\033[0m"
    echo "  udos '[TEMPLATE|LIST]'        - List all templates"
    echo "  udos '[GET|USER-ROLE]'        - Get user role variable"
    echo "  udos '[SYSTEM|STATUS]'        - System status details"
    echo ""
    echo -e "\033[0;36mType 'udos_help' anytime to see this help\033[0m"
}

EOF

    # Source the aliases
    source "$alias_file"
    
    log_info "Terminal aliases created and loaded"
}

# Setup command completion for uDOS commands
setup_command_completion() {
    # Basic completion for udos command
    complete -W "[STATUS|DASHBOARD] [ROLE] [ASSIST|ENTER] [ASSIST|EXIT] [TEMPLATE|LIST] [HELP] [SYSTEM|HEAL]" udos
    
    log_info "Command completion configured"
}

# Start uDOS in VS Code terminal mode
start_udos_terminal() {
    echo -e "${BLUE}🌀 Starting uDOS Express Development Terminal...${NC}"
    
    # Setup terminal environment
    setup_terminal_environment
    
    # Show initial status
    echo -e "${GREEN}✨ uDOS Terminal Integration Active${NC}"
    echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
    
    # Show current authentication status
    echo -e "${PURPLE}🔐 Authentication Check:${NC}"
    udos "[ROLE]"
    
    echo ""
    echo -e "${YELLOW}💡 Type 'udos_help' for available commands${NC}"
    echo -e "${YELLOW}💡 Type 'dash' for development dashboard${NC}"
    echo -e "${YELLOW}💡 Type 'assist enter' to start development assistance${NC}"
    echo ""
    
    # Keep terminal active with uDOS integration
    exec "$SHELL"
}

# Monitor mode - keep terminal as output stream with real-time updates
monitor_udos() {
    echo -e "${YELLOW}📊 uDOS Output Stream (VS Code Terminal)${NC}"
    echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
    
    # Setup monitoring environment
    setup_terminal_environment
    
    # Show initial dashboard
    echo -e "${GREEN}🎛️ Real-Time uDOS Dashboard${NC}"
    udos "[STATUS|DASHBOARD]"
    
    echo ""
    echo -e "${YELLOW}📡 Monitoring uDOS activity... (Ctrl+C to exit)${NC}"
    echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
    
    # Monitor logs and authentication events
    while true; do
        if [[ -f "$UDOS_ROOT/sandbox/logs/auth.log" ]]; then
            echo -e "${GREEN}🔐 Recent Authentication Events:${NC}"
            tail -3 "$UDOS_ROOT/sandbox/logs/auth.log" 2>/dev/null || echo "No auth events yet"
            echo ""
        fi
        
        # Show current system status every 30 seconds
        echo -e "${BLUE}[$(date '+%H:%M:%S')] System Status Check:${NC}"
        udos "[SYSTEM|STATUS]" 2>/dev/null || echo "uDOS system check pending..."
        echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
        
        sleep 30
    done
}

# Integration mode - Full VS Code + uDOS integration with services
integration_mode() {
    echo -e "${GREEN}🔗 VS Code + uDOS Full Integration Mode${NC}"
    echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
    
    # Setup complete integration environment
    setup_terminal_environment
    
    # Start background services
    start_udos_services
    
    # Show integration status
    echo ""
    echo -e "${GREEN}✅ uDOS Full Integration Active${NC}"
    echo -e "${PURPLE}🎯 Available Interfaces:${NC}"
    echo -e "   📱 Terminal: Express commands (dash, assist, role, heal)"
    echo -e "   🌐 Web: http://localhost:8080 (auto-starting)"
    echo -e "   🖥️ Desktop: Available via VS Code tasks"
    echo -e "   📊 Real-time: Live dashboard updates"
    echo ""
    
    # Show current status
    udos "[STATUS|DASHBOARD]"
    
    # Keep monitoring in integration mode
    monitor_udos
}

# Start uDOS background services for integration
start_udos_services() {
    echo -e "${BLUE}🚀 Starting uDOS Services...${NC}"
    
    # Ensure directories exist
    mkdir -p "$UDOS_ROOT/sandbox/logs"
    
    # Start web export for preview (background)
    if [[ -f "$UDOS_ROOT/uNETWORK/display/udos-display.sh" ]]; then
        echo -e "${YELLOW}📡 Starting web export service...${NC}"
        (cd "$UDOS_ROOT" && ./uNETWORK/display/udos-display.sh export dashboard) &
        WEB_PID=$!
        echo "$WEB_PID" > "$UDOS_ROOT/sandbox/temp/web-service.pid"
        log_success "Web service started (PID: $WEB_PID)"
    fi
    
    # Start self-healing monitoring (background)
    echo -e "${YELLOW}🛠️ Starting self-healing monitor...${NC}"
    (
        while true; do
            sleep 300  # Check every 5 minutes
            "$UDOS_ROOT/uCORE/code/self-healing/dependency-healer.sh" status > "$UDOS_ROOT/sandbox/logs/healing-status.log" 2>&1
        done
    ) &
    HEAL_PID=$!
    echo "$HEAL_PID" > "$UDOS_ROOT/sandbox/temp/healing-monitor.pid"
    log_success "Self-healing monitor started (PID: $HEAL_PID)"
    
    echo ""
    log_success "uDOS services running in background"
    echo -e "${BLUE}   🖥️ Terminal: Express commands active${NC}"
    echo -e "${BLUE}   🌐 Web UI: http://localhost:8080${NC}"
    echo -e "${BLUE}   🛠️ Self-Healing: Automatic monitoring${NC}"
    echo -e "${BLUE}   📊 Dashboard: Real-time updates${NC}"
}

# Cleanup function for graceful shutdown
cleanup_services() {
    echo -e "${YELLOW}🧹 Cleaning up uDOS services...${NC}"
    
    # Kill web service
    if [[ -f "$UDOS_ROOT/sandbox/temp/web-service.pid" ]]; then
        kill $(cat "$UDOS_ROOT/sandbox/temp/web-service.pid") 2>/dev/null || true
        rm -f "$UDOS_ROOT/sandbox/temp/web-service.pid"
    fi
    
    # Kill healing monitor
    if [[ -f "$UDOS_ROOT/sandbox/temp/healing-monitor.pid" ]]; then
        kill $(cat "$UDOS_ROOT/sandbox/temp/healing-monitor.pid") 2>/dev/null || true
        rm -f "$UDOS_ROOT/sandbox/temp/healing-monitor.pid"
    fi
    
    log_success "Services cleaned up"
}

# Setup signal handlers
trap cleanup_services EXIT INT TERM

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
