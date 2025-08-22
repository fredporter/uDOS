#!/bin/bash
# uDOS Desktop Launcher v1.3.1 - Clean Single Instance Startup
cd "$(dirname "$0")"

echo "🧙‍♂️ Starting uDOS v1.3.1..."

# Check for existing instance
if pgrep -f "uSERVER/server.py" >/dev/null; then
    echo "⚠️  uDOS server is already running"
    echo "Opening UI in browser..."
    open http://localhost:8080 2>/dev/null
    exit 0
fi

# Use the managed launcher for single instance control
./uCORE/launcher/universal/start-udos-managed.sh start development
