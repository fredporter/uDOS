#!/bin/bash
# Vibe launcher (with Wizard MCP)

set -e

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
REPO_ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"

# Ensure Vibe prompt is installed in ~/.vibe/prompts
PROMPTS_DIR="$HOME/.vibe/prompts"
SRC_PROMPT="$REPO_ROOT/.vibe/prompts/udos_router.md"
DST_PROMPT="$PROMPTS_DIR/udos_router.md"
mkdir -p "$PROMPTS_DIR"
if [ -f "$SRC_PROMPT" ]; then
  if [ ! -f "$DST_PROMPT" ] || ! cmp -s "$SRC_PROMPT" "$DST_PROMPT"; then
    cp "$SRC_PROMPT" "$DST_PROMPT"
  fi
fi

if [ -f "$REPO_ROOT/.env" ]; then
  set -a
  # shellcheck disable=SC1090
  . "$REPO_ROOT/.env"
  set +a
fi

export WIZARD_BASE_URL="${WIZARD_BASE_URL:-http://localhost:8765}"
export VIBE_SYSTEM_PROMPT_ID="udos_router"

if [ -z "${WIZARD_ADMIN_TOKEN:-}" ]; then
  echo "⚠️  WIZARD_ADMIN_TOKEN is not set."
  echo "   Generate one via Wizard admin token endpoint or set it in .env."
fi

# Start Wizard server if not running
if ! curl -s --connect-timeout 2 "${WIZARD_BASE_URL}/health" >/dev/null 2>&1; then
  echo "🧙 Starting Wizard server..."
  mkdir -p "$REPO_ROOT/memory/logs"
  nohup python3 -m wizard.server --no-interactive > "$REPO_ROOT/memory/logs/wizard-server.log" 2>&1 &
  wizard_pid=$!
  # Wait up to 10s for health
  for i in {1..20}; do
    if curl -s --connect-timeout 2 "${WIZARD_BASE_URL}/health" >/dev/null 2>&1; then
      echo "✅ Wizard server started (PID: $wizard_pid)"
      break
    fi
    sleep 0.5
  done
fi

if ! command -v vibe >/dev/null 2>&1; then
  echo "❌ vibe CLI not found. Install with: pip install mistral-vibe"
  exit 1
fi

cd "$REPO_ROOT"


export VIBE_CONFIG_PATH="$REPO_ROOT/.vibe/config.toml"
echo "🚀 Launching Vibe with MCP (Wizard)"
exec "$REPO_ROOT/bin/vibe-wrapper.sh"
