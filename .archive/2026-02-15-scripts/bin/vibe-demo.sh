#!/bin/bash
# Minimal Vibe demo helper

set -e

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
REPO_ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"

export WIZARD_BASE_URL="${WIZARD_BASE_URL:-http://localhost:8765}"

if [ -z "${WIZARD_ADMIN_TOKEN:-}" ]; then
  echo "⚠️  WIZARD_ADMIN_TOKEN is not set."
  echo "   Generate one via Wizard admin token endpoint or set it in .env."
fi

if ! command -v python3 >/dev/null 2>&1; then
  echo "❌ python3 not found."
  exit 1
fi

if [ ! -f "$REPO_ROOT/.vibe/config.toml" ]; then
  echo "❌ Missing .vibe/config.toml."
  exit 1
fi

echo "✅ MCP smoke check:"
python3 "$REPO_ROOT/mcp/wizard/server.py" --health || true

cat <<'GUIDE'

Try these in Vibe:
- wizard_health
- wizard_providers_list
- wizard_config_get
- ucode_dispatch "HELP"
- ucode_dispatch "MAP"
- ucode_dispatch "PANEL"
- ucode_dispatch "TELL location"
- ucode_dispatch "FIND tokyo"

GUIDE

echo "Launching Vibe..."
exec vibe
