#!/bin/bash
# uDOS Web Extension Launcher
# Bulletproof startup script for all web servers
# Usage: ./launch_web.sh [extension] [port]

set -e  # Exit on error

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Get script directory
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
UDOS_ROOT="$(cd "$SCRIPT_DIR/../.." && pwd)"
WEB_EXTENSIONS="$UDOS_ROOT/extensions/web"

# Function to print colored messages
print_info() {
    echo -e "${BLUE}ℹ️  $1${NC}"
}

print_success() {
    echo -e "${GREEN}✅ $1${NC}"
}

print_warning() {
    echo -e "${YELLOW}⚠️  $1${NC}"
}

print_error() {
    echo -e "${RED}❌ $1${NC}"
}

# Function to check if port is in use
is_port_in_use() {
    local port=$1
    lsof -i :$port -sTCP:LISTEN -t >/dev/null 2>&1
}

# Function to kill process on port
kill_port() {
    local port=$1
    print_warning "Killing existing process on port $port..."
    lsof -ti :$port | xargs kill -9 2>/dev/null || true
    sleep 1
}

# Function to activate virtual environment
activate_venv() {
    if [ -f "$UDOS_ROOT/.venv/bin/activate" ]; then
        source "$UDOS_ROOT/.venv/bin/activate"
        print_success "Virtual environment activated"
    else
        print_warning "No virtual environment found, using system Python"
    fi
}

# Function to verify Python installation
check_python() {
    if ! command -v python3 &> /dev/null; then
        print_error "python3 not found!"
        exit 1
    fi
    print_info "Python: $(python3 --version)"
}

# Function to start dashboard
start_dashboard() {
    local port=${1:-8887}
    local server_dir="$WEB_EXTENSIONS/dashboard"

    print_info "Starting uDOS Dashboard on port $port..."

    if [ ! -f "$server_dir/server.py" ]; then
        print_error "Dashboard server not found at $server_dir/server.py"
        exit 1
    fi

    if is_port_in_use $port; then
        kill_port $port
    fi

    cd "$server_dir"
    python3 server.py $port > /tmp/udos-dashboard.log 2>&1 &
    local pid=$!

    sleep 2

    if kill -0 $pid 2>/dev/null; then
        print_success "Dashboard started on http://localhost:$port (PID: $pid)"
        echo $pid > /tmp/udos-dashboard.pid

        # Open in browser if not in CI
        if [ -z "$CI" ] && command -v open &> /dev/null; then
            sleep 1
            open "http://localhost:$port" 2>/dev/null || true
        fi
    else
        print_error "Failed to start dashboard. Check logs: /tmp/udos-dashboard.log"
        cat /tmp/udos-dashboard.log
        exit 1
    fi
}

# Function to start markdown viewer
start_markdown_viewer() {
    local port=${1:-8889}
    local server_dir="$WEB_EXTENSIONS/markdown-viewer"

    print_info "Starting Markdown Viewer on port $port..."

    if [ ! -f "$server_dir/server.py" ]; then
        print_error "Markdown Viewer server not found at $server_dir/server.py"
        exit 1
    fi

    if is_port_in_use $port; then
        kill_port $port
    fi

    cd "$server_dir"
    python3 server.py --port $port > /tmp/udos-markdown.log 2>&1 &
    local pid=$!

    sleep 2

    if kill -0 $pid 2>/dev/null; then
        print_success "Markdown Viewer started on http://localhost:$port (PID: $pid)"
        echo $pid > /tmp/udos-markdown.pid
    else
        print_error "Failed to start Markdown Viewer. Check logs: /tmp/udos-markdown.log"
        cat /tmp/udos-markdown.log
        exit 1
    fi
}

# Function to start font editor
start_font_editor() {
    local port=${1:-8888}
    local server_dir="$WEB_EXTENSIONS/font-editor"

    print_info "Starting Font Editor on port $port..."

    if [ ! -f "$server_dir/server.py" ]; then
        print_error "Font Editor server not found at $server_dir/server.py"
        exit 1
    fi

    if is_port_in_use $port; then
        kill_port $port
    fi

    cd "$server_dir"
    python3 server.py --port $port > /tmp/udos-font-editor.log 2>&1 &
    local pid=$!

    sleep 2

    if kill -0 $pid 2>/dev/null; then
        print_success "Font Editor started on http://localhost:$port (PID: $pid)"
        echo $pid > /tmp/udos-font-editor.pid
    else
        print_error "Failed to start Font Editor. Check logs: /tmp/udos-font-editor.log"
        cat /tmp/udos-font-editor.log
        exit 1
    fi
}

# Function to start terminal
start_terminal() {
    local port=${1:-8890}
    local server_dir="$WEB_EXTENSIONS/terminal"

    print_info "Starting Web Terminal on port $port..."

    if [ ! -f "$server_dir/server.py" ]; then
        print_error "Web Terminal server not found at $server_dir/server.py"
        exit 1
    fi

    if is_port_in_use $port; then
        kill_port $port
    fi

    cd "$server_dir"
    python3 server.py --port $port > /tmp/udos-terminal.log 2>&1 &
    local pid=$!

    sleep 2

    if kill -0 $pid 2>/dev/null; then
        print_success "Web Terminal started on http://localhost:$port (PID: $pid)"
        echo $pid > /tmp/udos-terminal.pid
    else
        print_error "Failed to start Web Terminal. Check logs: /tmp/udos-terminal.log"
        cat /tmp/udos-terminal.log
        exit 1
    fi
}

# Function to start all extensions
start_all() {
    print_info "Starting all uDOS web extensions..."
    activate_venv
    check_python

    start_dashboard 8887
    start_markdown_viewer 8889
    start_font_editor 8888
    start_terminal 8890

    echo ""
    print_success "All web extensions started!"
    echo ""
    echo "  🌀 Dashboard:        http://localhost:8887"
    echo "  🎨 Font Editor:      http://localhost:8888"
    echo "  📖 Markdown Viewer:  http://localhost:8889"
    echo "  💻 Web Terminal:     http://localhost:8890"
    echo ""
}

# Function to stop all extensions
stop_all() {
    print_info "Stopping all uDOS web extensions..."

    for port in 8887 8888 8889 8890; do
        if is_port_in_use $port; then
            kill_port $port
            print_success "Stopped server on port $port"
        fi
    done

    # Clean up PID files
    rm -f /tmp/udos-dashboard.pid /tmp/udos-markdown.pid /tmp/udos-font-editor.pid /tmp/udos-terminal.pid

    print_success "All servers stopped"
}

# Function to show status
show_status() {
    print_info "uDOS Web Extensions Status"
    echo ""

    declare -A servers=(
        [8887]="Dashboard"
        [8888]="Font Editor"
        [8889]="Markdown Viewer"
        [8890]="Web Terminal"
    )

    for port in "${!servers[@]}"; do
        if is_port_in_use $port; then
            local pid=$(lsof -ti :$port 2>/dev/null || echo "unknown")
            print_success "${servers[$port]} (port $port) - RUNNING (PID: $pid)"
        else
            echo -e "  ⭕ ${servers[$port]} (port $port) - STOPPED"
        fi
    done
    echo ""
}

# Main script logic
case "${1:-all}" in
    dashboard)
        activate_venv
        check_python
        start_dashboard ${2:-8887}
        ;;
    markdown-viewer|markdown)
        activate_venv
        check_python
        start_markdown_viewer ${2:-8889}
        ;;
    font-editor|font)
        activate_venv
        check_python
        start_font_editor ${2:-8888}
        ;;
    terminal|cmd)
        activate_venv
        check_python
        start_terminal ${2:-8890}
        ;;
    all)
        start_all
        ;;
    stop)
        stop_all
        ;;
    status)
        show_status
        ;;
    restart)
        stop_all
        sleep 2
        start_all
        ;;
    *)
        echo "uDOS Web Extension Launcher"
        echo ""
        echo "Usage: $0 [command] [port]"
        echo ""
        echo "Commands:"
        echo "  all              Start all web extensions (default)"
        echo "  dashboard [port] Start dashboard (default: 8887)"
        echo "  markdown [port]  Start markdown viewer (default: 8889)"
        echo "  font [port]      Start font editor (default: 8888)"
        echo "  terminal [port]  Start web terminal (default: 8890)"
        echo "  stop             Stop all servers"
        echo "  status           Show server status"
        echo "  restart          Restart all servers"
        echo ""
        echo "Examples:"
        echo "  $0               # Start all servers"
        echo "  $0 dashboard     # Start only dashboard"
        echo "  $0 status        # Check what's running"
        echo "  $0 stop          # Stop everything"
        echo ""
        exit 1
        ;;
esac
