#!/bin/bash
set -euo pipefail

REPO_ROOT="${REPO_ROOT:-$(cd "$(dirname "$0")/.." && pwd)}"
WIZARD_BASE_URL="${WIZARD_BASE_URL:-http://localhost:8765}"

if ! command -v vibe >/dev/null 2>&1; then
  echo "❌ vibe CLI not found. Install with: pip install mistral-vibe"
  exit 1
fi

if [ -z "${WIZARD_ADMIN_TOKEN:-}" ]; then
  echo "⚠️  WIZARD_ADMIN_TOKEN is not set."
  echo "   uCODE-prefixed commands may fail until it is set."
fi

_ucode_dispatch() {
  local input="$1"
  local response
  response="$(curl -sS \
    -H "Content-Type: application/json" \
    -H "X-Admin-Token: ${WIZARD_ADMIN_TOKEN:-}" \
    -d "{\"command\": \"${input//\"/\\\"}\"}" \
    "${WIZARD_BASE_URL}/api/ucode/dispatch")"
  python3 - <<'PY' "$response"
import json, sys
raw = sys.argv[1]
try:
    data = json.loads(raw)
except Exception:
    print(raw)
    sys.exit(0)

rendered = data.get("rendered")
if rendered:
    print(rendered)
    sys.exit(0)

result = data.get("result") or {}
if isinstance(result, dict):
    output = result.get("output")
    if output:
        print(output)
        sys.exit(0)
    message = result.get("message")
    if message:
        print(message)
        sys.exit(0)

print(raw)
PY
}

_vibe_prompt() {
  local prompt="$1"
  local status=0
  vibe -p "$prompt" --continue --workdir "$REPO_ROOT" >/dev/null 2>&1 || status=$?
  if [ "$status" -ne 0 ]; then
    vibe -p "$prompt" --workdir "$REPO_ROOT"
  fi
}

cd "$REPO_ROOT"
echo "🧪 Vibe wrapper active. Prefix uCODE with ':' or 'OK', shell with '/'."

while true; do
  printf "> "
  IFS= read -r line || exit 0
  trimmed="${line#"${line%%[![:space:]]*}"}"
  [ -z "$trimmed" ] && continue

  case "$trimmed" in
    exit|quit) exit 0 ;;
  esac

  if [[ "$trimmed" == :* ]] || [[ "$trimmed" == /* ]] || [[ "$trimmed" =~ ^[Oo][Kk]($|[[:space:]]) ]]; then
    _ucode_dispatch "$trimmed"
  else
    _vibe_prompt "$trimmed"
  fi
done
