#!/bin/bash
# uDOS Process Manager - Coordinate multiple development processes

LOCK_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)/locks"
UDOS_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"

mkdir -p "$LOCK_DIR"

# Process coordination
check_server_running() {
    if [[ -f "$LOCK_DIR/server.pid" ]] && kill -0 "$(cat "$LOCK_DIR/server.pid")" 2>/dev/null; then
        return 0
    fi
    return 1
}

start_server() {
    if check_server_running; then
        echo "uDOS server already running (PID: $(cat "$LOCK_DIR/server.pid"))"
        return 0
    fi

    echo "Starting uDOS server..."
    cd "$UDOS_ROOT/uNETWORK/server"
    python server.py &
    echo $! > "$LOCK_DIR/server.pid"
    echo "Server started (PID: $!)"
}

stop_server() {
    if [[ -f "$LOCK_DIR/server.pid" ]]; then
        local pid=$(cat "$LOCK_DIR/server.pid")
        if kill -0 "$pid" 2>/dev/null; then
            kill "$pid"
            echo "Stopped server (PID: $pid)"
        fi
        rm -f "$LOCK_DIR/server.pid"
    fi
}

status() {
    echo "uDOS Process Status:"
    if check_server_running; then
        echo "  🟢 Server: Running (PID: $(cat "$LOCK_DIR/server.pid"))"
    else
        echo "  🔴 Server: Not running"
    fi

    if pgrep -f "tauri dev" >/dev/null; then
        echo "  🟢 Tauri: Running"
    else
        echo "  🔴 Tauri: Not running"
    fi
}

case "$1" in
    start-server) start_server ;;
    stop-server) stop_server ;;
    status) status ;;
    *) echo "Usage: $0 {start-server|stop-server|status}" ;;
esac
