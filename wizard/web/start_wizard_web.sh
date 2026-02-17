#!/bin/bash
# Start Wizard Server Web Interface

set -euo pipefail

REPO_ROOT="$(cd "$(dirname "$0")/../.." && pwd)"
WIZARD_VENV=""

if [ -n "${WIZARD_VENV_PATH:-}" ]; then
  if [[ "$WIZARD_VENV_PATH" = /* ]]; then
    CANDIDATES=("$WIZARD_VENV_PATH")
  else
    CANDIDATES=("$REPO_ROOT/$WIZARD_VENV_PATH")
  fi
else
  CANDIDATES=()
fi
CANDIDATES+=("$REPO_ROOT/venv")

for candidate in "${CANDIDATES[@]}"; do
  if [ -x "$candidate/bin/python" ]; then
    WIZARD_VENV="$candidate"
    break
  fi
done

if [ -z "$WIZARD_VENV" ]; then
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
