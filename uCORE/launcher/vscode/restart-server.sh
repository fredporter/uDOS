#!/bin/bash
# Quick server restart script for uDOS development

UDOS_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"

echo "🔄 Restarting uDOS development server..."

# Kill existing server
pkill -f "uSERVER/server.py" 2>/dev/null || true
if [ -f /tmp/udos-dev-server.pid ]; then
    kill -9 $(cat /tmp/udos-dev-server.pid) 2>/dev/null || true
    rm -f /tmp/udos-dev-server.pid
fi

# Wait a moment
sleep 1

# Start new server
cd "$UDOS_ROOT"
export UDOS_CURRENT_ROLE="wizard"
export UDOS_ACCESS_LEVEL="100"
export UDOS_DEV_MODE="true"

python3 uSERVER/server.py &
echo $! > /tmp/udos-dev-server.pid

# Wait for server to start
sleep 3

if curl -s http://localhost:8080/api/status >/dev/null 2>&1; then
    echo "✅ Server restarted successfully"

    # Refresh VS Code preview if available
    code --command "livePreview.start.preview.atFile" "$UDOS_ROOT/uCORE/launcher/universal/ucode-ui/index.html" 2>/dev/null || true
else
    echo "❌ Failed to restart server"
    exit 1
fi
