#!/bin/bash
# uDOS Managed Launcher v1.3.1 - Single Instance System
set -euo pipefail

UDOS_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/../../../" && pwd)"
source "$UDOS_ROOT/uCORE/system/process-manager.sh"

show_usage() {
    echo -e "${WHITE}🧙‍♂️ uDOS Managed Launcher v1.3.1${NC}"
    echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
    echo "Usage: $0 [COMMAND] [OPTIONS]"
    echo ""
    echo -e "${WHITE}Commands:${NC}"
    echo "  start [mode]    Start uDOS (development|production|testing)"
    echo "  attach          Connect to existing session"
    echo "  status          Show current session status"
    echo "  stop            Stop all uDOS processes"
    echo "  restart         Restart current session"
    echo "  force           Force restart (kill existing)"
    echo ""
    echo -e "${WHITE}Examples:${NC}"
    echo "  $0 start development    # Start in development mode"
    echo "  $0 attach               # Connect to running session"
    echo "  $0 force development    # Force restart in dev mode"
}

main() {
    local command="${1:-start}"
    local mode="${2:-development}"

    case "$command" in
        "start")
            start_udos_managed "$mode"
            ;;
        "attach")
            attach_to_session
            ;;
        "status")
            show_session_status
            ;;
        "stop")
            force_shutdown_all
            ;;
        "restart")
            restart_session
            ;;
        "force")
            ensure_single_instance "udos" true
            check_system_resources
            start_managed_server "$mode"
            start_managed_cli "$mode"
            ;;
        "help"|"--help"|"-h")
            show_usage
            ;;
        *)
            echo -e "${RED}❌ Unknown command: $command${NC}"
            show_usage
            exit 1
            ;;
    esac
}

start_udos_managed() {
    local mode="$1"

    echo -e "${WHITE}🧙‍♂️ Starting uDOS Managed Session v1.3.1${NC}"
    echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"

    # Ensure single instance
    ensure_single_instance "udos" false

    # Check system resources
    check_system_resources

    # Start managed server
    start_managed_server "$mode"

    # Start appropriate interface
    case "$mode" in
        "development")
            start_development_interface
            ;;
        "production")
            start_production_interface
            ;;
        "testing")
            start_testing_interface
            ;;
    esac

    # Start managed CLI
    start_managed_cli "$mode"
}

start_development_interface() {
    echo -e "${BLUE}🔧 Starting development interface...${NC}"

    # Check if VS Code should be opened
    if command -v code >/dev/null 2>&1; then
        echo -e "${BLUE}📝 Opening VS Code workspace...${NC}"
        if [ -f "$UDOS_ROOT/.vscode/udos-dev.code-workspace" ]; then
            code "$UDOS_ROOT/.vscode/udos-dev.code-workspace" 2>/dev/null &
        else
            code "$UDOS_ROOT" 2>/dev/null &
        fi

        # Give VS Code time to start
        sleep 3

        # Open live preview if available
        code --command "livePreview.start.preview.atFile" "$UDOS_ROOT/uCORE/launcher/universal/ucode-ui/index.html" 2>/dev/null &
    fi

    # Open browser UI
    echo -e "${BLUE}🌐 Opening browser UI...${NC}"
    sleep 2
    open http://localhost:8080 2>/dev/null || echo "Open browser to: http://localhost:8080"
}

start_production_interface() {
    echo -e "${BLUE}🌐 Starting production interface...${NC}"

    # Only open browser, no VS Code
    sleep 2
    open http://localhost:8080 2>/dev/null || echo "Open browser to: http://localhost:8080"
}

start_testing_interface() {
    echo -e "${BLUE}🧪 Starting testing interface...${NC}"

    # Minimal interface for testing
    echo "Testing mode - UI available at: http://localhost:8080"
}

start_managed_cli() {
    local mode="$1"

    echo ""
    echo -e "${WHITE}🖥️ uDOS Managed CLI - $mode mode${NC}"
    echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
    echo -e "${WHITE}Session commands:${NC}"
    echo "  status     - Show session status"
    echo "  logs       - Show server logs"
    echo "  ui         - Open UI in browser"
    echo "  restart    - Restart server"
    echo "  stop       - Stop entire session"
    echo "  quit       - Exit CLI (server continues)"
    echo ""

    session_cli_loop
}

main "$@"
