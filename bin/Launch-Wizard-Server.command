#!/bin/bash

# Wizard Production Server Launcher (.command for macOS)
# Starts the always-on Wizard server with auth, AI routing, and webhooks
#
# Location: /bin/Launch-Wizard-Server.command
# Port: 8765
# API: http://localhost:8765/api/v1
# Docs: http://localhost:8765/docs
# Status: PRODUCTION v1.1.0.0 (stable, frozen)

# Get the repository root (this script is at /bin/)
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
REPO_ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"

cd "$REPO_ROOT"

# Display banner
cat << 'EOF'
╔═══════════════════════════════════════════════════════════════╗
║            🧙 Wizard Production Server v1.1.0.0               ║
║      Always-On • AI Routing • Webhooks • Device Auth          ║
╚═══════════════════════════════════════════════════════════════╝
EOF

# Check environment
echo ""
echo "[BOOT] Checking environment..."
echo "[BOOT] uDOS Root: $REPO_ROOT"

if [ ! -d ".venv" ]; then
    echo "[✗] Virtual environment not found at .venv/"
    exit 1
fi

echo "[BOOT] Features: AI Gateway, Dev Mode, Notion Sync, Task Scheduler, Binder Compiler, GitHub Integration"

echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "🧙 Wizard Production Server v1.1.0.0"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"

# Activate venv
echo "[BOOT] Activating virtual environment..."
source .venv/bin/activate

if [ $? -eq 0 ]; then
    echo "[✓] Virtual environment activated"
    PYTHON_VERSION=$(python --version 2>&1)
    echo "[BOOT] Python: $PYTHON_VERSION"
else
    echo "[✗] Failed to activate virtual environment"
    exit 1
fi

# Check dependencies
echo "[BOOT] Checking dependencies..."
python -c "import fastapi; import uvicorn; import sqlalchemy" 2>/dev/null
if [ $? -eq 0 ]; then
    echo "[✓] Dependencies installed and ready"
else
    echo "[⚠] Some dependencies may be missing"
fi

# Self-healing: Kill any existing Wizard instance
echo "[BOOT] Checking for existing Wizard server..."
EXISTING_PID=$(ps aux | grep "wizard.server" | grep -v grep | awk '{print $2}')
if [ ! -z "$EXISTING_PID" ]; then
    echo "[BOOT] Stopping existing Wizard server (PID: $EXISTING_PID)..."
    kill $EXISTING_PID 2>/dev/null
    sleep 2
    echo "[✓] Existing server stopped"
fi

# Start Wizard
echo "[BOOT] Starting Wizard Production Server on port 8765..."
echo ""
python -m wizard.server --port 8765

# Capture exit code
RESULT=$?
if [ $RESULT -eq 0 ]; then
    echo "[✓] Wizard Server stopped cleanly"
else
    echo "[✗] Failed to start Wizard Server on port 8765"
    echo ""
    echo "Troubleshooting:"
    echo "  1. Check if port 8765 is already in use: lsof -i :8765"
    echo "  2. Verify Python dependencies: pip install -r requirements.txt"
    echo "  3. Check Wizard logs: cat memory/logs/wizard-*.log"
fi

exit $RESULT
