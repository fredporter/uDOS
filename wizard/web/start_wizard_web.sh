#!/bin/bash
# Start Wizard Server Web Interface

set -euo pipefail

REPO_ROOT="$(cd "$(dirname "$0")/../.." && pwd)"
WIZARD_VENV="$REPO_ROOT/wizard/.venv"

if [ ! -x "$WIZARD_VENV/bin/python" ]; then
  echo "Wizard environment not installed. Run: ./bin/ucli wizard install" >&2
  exit 1
fi

# Activate Wizard venv
source "$WIZARD_VENV/bin/activate"

# Start server
echo "🧙 Starting Wizard Server Web Interface..."
echo "📍 Dashboard: http://127.0.0.1:8080/"
echo ""
python -c "from wizard.web.app import start_web_server; start_web_server()"
