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
