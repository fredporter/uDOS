#!/bin/bash
# uDOS v1.4 Display Server Launcher
# Starts the Browser-UI server with proper environment setup

set -euo pipefail

UDOS_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
DISPLAY_SERVER="$UDOS_ROOT/uNETWORK/display/server/display-server.py"
PID_FILE="/tmp/udos-display-server.pid"

# Load core systems
source "$UDOS_ROOT/uSCRIPT/library/shell/ensure-utf8.sh"
source "$UDOS_ROOT/uCORE/system/polaroid-colors.sh"

# Function to check if server is running
is_server_running() {
    if [[ -f "$PID_FILE" ]]; then
        local pid=$(cat "$PID_FILE")
        if kill -0 "$pid" 2>/dev/null; then
            return 0
        else
            rm -f "$PID_FILE"
            return 1
        fi
    fi
    return 1
}

# Function to start server
start_server() {
    if is_server_running; then
        polaroid_echo "yellow" "⚠️  Display server already running (PID: $(cat $PID_FILE))"
        return 0
    fi
    
    polaroid_echo "cyan" "🚀 Starting uDOS Display Server..."
    
    # Check Python dependencies
    if ! python3 -c "import flask, flask_socketio, psutil" 2>/dev/null; then
        polaroid_echo "orange" "📦 Installing required Python packages..."
        pip3 install flask flask-socketio psutil eventlet
    fi
    
    # Start server in background
    cd "$UDOS_ROOT"
    python3 "$DISPLAY_SERVER" > /tmp/udos-display-server.log 2>&1 &
    local server_pid=$!
    
    # Save PID
    echo "$server_pid" > "$PID_FILE"
    
    # Wait a moment to check if it started successfully
    sleep 2
    if kill -0 "$server_pid" 2>/dev/null; then
        polaroid_echo "lime" "✅ Display server started successfully!"
        polaroid_echo "cyan" "   Server PID: $server_pid"
        polaroid_echo "cyan" "   Server URL: http://localhost:8080"
        polaroid_echo "cyan" "   Log file: /tmp/udos-display-server.log"
        
        # Open browser if requested
        if [[ "${1:-}" == "--open" ]] || [[ "${1:-}" == "-o" ]]; then
            sleep 1
            if command -v open >/dev/null 2>&1; then
                open "http://localhost:8080"
            elif command -v xdg-open >/dev/null 2>&1; then
                xdg-open "http://localhost:8080"
            else
                polaroid_echo "yellow" "   Please open http://localhost:8080 in your browser"
            fi
        fi
        
        return 0
    else
        polaroid_echo "orange" "❌ Failed to start display server"
        rm -f "$PID_FILE"
        return 1
    fi
}

# Function to stop server
stop_server() {
    if ! is_server_running; then
        polaroid_echo "yellow" "⚠️  Display server is not running"
        return 0
    fi
    
    local pid=$(cat "$PID_FILE")
    polaroid_echo "cyan" "🛑 Stopping display server (PID: $pid)..."
    
    if kill "$pid" 2>/dev/null; then
        # Wait for graceful shutdown
        local count=0
        while kill -0 "$pid" 2>/dev/null && [[ $count -lt 10 ]]; do
            sleep 1
            ((count++))
        done
        
        # Force kill if still running
        if kill -0 "$pid" 2>/dev/null; then
            kill -9 "$pid" 2>/dev/null
        fi
        
        rm -f "$PID_FILE"
        polaroid_echo "lime" "✅ Display server stopped"
    else
        polaroid_echo "orange" "❌ Failed to stop display server"
        rm -f "$PID_FILE"
        return 1
    fi
}

# Function to restart server
restart_server() {
    polaroid_echo "cyan" "🔄 Restarting display server..."
    stop_server
    sleep 2
    start_server "$@"
}

# Function to show status
show_status() {
    if is_server_running; then
        local pid=$(cat "$PID_FILE")
        polaroid_echo "lime" "✅ Display server is running"
        polaroid_echo "cyan" "   PID: $pid"
        polaroid_echo "cyan" "   URL: http://localhost:8080"
        
        # Show memory usage if possible
        if command -v ps >/dev/null 2>&1; then
            local mem_usage=$(ps -o rss= -p "$pid" 2>/dev/null | tr -d ' ')
            if [[ -n "$mem_usage" ]]; then
                local mem_mb=$((mem_usage / 1024))
                polaroid_echo "cyan" "   Memory: ${mem_mb}MB"
            fi
        fi
    else
        polaroid_echo "orange" "❌ Display server is not running"
    fi
}

# Function to show logs
show_logs() {
    local log_file="/tmp/udos-display-server.log"
    if [[ -f "$log_file" ]]; then
        polaroid_echo "cyan" "📝 Display server logs:"
        echo
        tail -n 20 "$log_file"
    else
        polaroid_echo "yellow" "⚠️  No log file found"
    fi
}

# Main command handler
main() {
    local command="${1:-start}"
    
    case "$command" in
        "start"|"-s"|"--start")
            start_server "${2:-}"
            ;;
        "stop"|"-k"|"--stop")
            stop_server
            ;;
        "restart"|"-r"|"--restart")
            restart_server "${2:-}"
            ;;
        "status"|"-t"|"--status")
            show_status
            ;;
        "logs"|"-l"|"--logs")
            show_logs
            ;;
        "open"|"-o"|"--open")
            if is_server_running; then
                if command -v open >/dev/null 2>&1; then
                    open "http://localhost:8080"
                elif command -v xdg-open >/dev/null 2>&1; then
                    xdg-open "http://localhost:8080"
                else
                    polaroid_echo "cyan" "🌐 Display server URL: http://localhost:8080"
                fi
            else
                polaroid_echo "orange" "❌ Display server is not running"
                polaroid_echo "cyan" "   Use: $0 start --open"
            fi
            ;;
        "help"|"-h"|"--help")
            cat << EOF
🎯 uDOS v1.4 Display Server Launcher

Usage: $0 <command> [options]

Commands:
  start [--open]    Start the display server (optionally open browser)
  stop              Stop the display server
  restart [--open]  Restart the display server
  status            Show server status
  logs              Show recent server logs
  open              Open browser to server URL
  help              Show this help

Examples:
  $0 start --open   # Start server and open browser
  $0 restart        # Restart server
  $0 status         # Check if running
  $0 logs           # View recent logs

Server URL: http://localhost:8080
EOF
            ;;
        *)
            polaroid_echo "orange" "❌ Unknown command: $command"
            polaroid_echo "cyan" "   Use: $0 help"
            exit 1
            ;;
    esac
}

# Run main function with all arguments
main "$@"
