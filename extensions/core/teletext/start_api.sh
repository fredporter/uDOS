#!/bin/bash
# uDOS v1.0.19 - Teletext API Server Launcher

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
UDOS_ROOT="$(cd "$SCRIPT_DIR/../../../.." && pwd)"

echo "🌀 uDOS Teletext API Server Launcher"
echo "======================================"
echo "Script dir: $SCRIPT_DIR"
echo "uDOS root:  $UDOS_ROOT"
echo ""

# Check for virtual environment
if [ -d "$UDOS_ROOT/.venv" ]; then
    echo "✅ Using virtual environment: $UDOS_ROOT/.venv"
    PYTHON="$UDOS_ROOT/.venv/bin/python"
else
    echo "⚠️  No virtual environment found, using system Python"
    PYTHON="python3"
fi

# Check dependencies
echo "📦 Checking dependencies..."
$PYTHON -m pip show flask > /dev/null 2>&1
if [ $? -ne 0 ]; then
    echo "❌ Flask not installed"
    echo "Installing dependencies..."
    $PYTHON -m pip install -r "$SCRIPT_DIR/requirements.txt" -q
fi

# Start server
echo ""
echo "🚀 Starting Teletext API Server..."
echo ""

cd "$SCRIPT_DIR"
export PYTHONPATH="$UDOS_ROOT:$PYTHONPATH"
$PYTHON api_server.py "$@"
