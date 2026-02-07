#!/bin/bash
set -euo pipefail

REPO_ROOT="${REPO_ROOT:-$(cd "$(dirname "$0")/.." && pwd)}"
WIZARD_BASE_URL="${WIZARD_BASE_URL:-http://localhost:8765}"
VENV_PY="${REPO_ROOT}/.venv/bin/python"
if [ -x "$VENV_PY" ]; then
  PYTHON_BIN="$VENV_PY"
else
  PYTHON_BIN="python3"
fi

if ! command -v vibe >/dev/null 2>&1; then
  echo "vibe CLI not found. Install with: pip install mistral-vibe"
  exit 1
fi

if [ -z "${WIZARD_ADMIN_TOKEN:-}" ]; then
  echo "WIZARD_ADMIN_TOKEN is not set."
  echo "uCODE-prefixed commands may fail until it is set."
fi

ADMIN_HEADER=()
if [ -n "${WIZARD_ADMIN_TOKEN:-}" ]; then
  ADMIN_HEADER=(-H "Authorization: Bearer ${WIZARD_ADMIN_TOKEN}")
fi

ALLOWLIST=()

_fetch_allowlist() {
  local payload
  payload="$(curl -sS "${ADMIN_HEADER[@]}" "${WIZARD_BASE_URL}/api/ucode/allowlist" || true)"
  if [ -z "$payload" ]; then
    return
  fi
  ALLOWLIST=()
  while IFS= read -r line; do
    [ -n "$line" ] && ALLOWLIST+=("$line")
  done < <("$PYTHON_BIN" - <<'PY' "$payload"
import json, sys
raw = sys.argv[1]
try:
    data = json.loads(raw)
except Exception:
    sys.exit(0)
for item in data.get("allowlist", []):
    if isinstance(item, str):
        print(item.upper())
PY
)
}

_is_ucode_command() {
  local token="$1"
  local upper
  upper="$(printf '%s' "$token" | tr '[:lower:]' '[:upper:]')"
  if [ "${#ALLOWLIST[@]}" -eq 0 ]; then
    return 1
  fi
  for cmd in "${ALLOWLIST[@]}"; do
    if [ "$upper" = "$cmd" ]; then
      return 0
    fi
  done
  return 1
}

_ucode_dispatch_raw() {
  local input="$1"
  local response
  response="$(curl -sS -w $'\n%{http_code}' \
    -H "Content-Type: application/json" \
    "${ADMIN_HEADER[@]}" \
    -d "{\"command\": \"${input//\"/\\\"}\"}" \
    "${WIZARD_BASE_URL}/api/ucode/dispatch")"
  printf "%s" "$response"
}

_ucode_render() {
  local body="$1"
  "$PYTHON_BIN" - <<'PY' "$body"
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

_ucode_is_success() {
  local body="$1"
  "$PYTHON_BIN" - <<'PY' "$body"
import json, sys
raw = sys.argv[1]
try:
    data = json.loads(raw)
except Exception:
    print("error")
    sys.exit(0)
result = data.get("result") or {}
status = None
if isinstance(result, dict):
    status = result.get("status")
if status is None:
    status = data.get("status")
if isinstance(status, str) and status.lower() == "error":
    print("error")
else:
    print("ok")
PY
}

_ucode_dispatch_print() {
  local input="$1"
  local response http body status
  response="$(_ucode_dispatch_raw "$input")"
  http="${response##*$'\n'}"
  body="${response%$'\n'*}"
  if [ -z "$body" ]; then
    return 1
  fi
  _ucode_render "$body"
  if [[ "$http" =~ ^2 ]]; then
    status="$(_ucode_is_success "$body")"
    [ "$status" = "ok" ]
    return $?
  fi
  return 1
}

_ucode_dispatch_quiet() {
  local input="$1"
  local response http body status
  response="$(_ucode_dispatch_raw "$input")"
  http="${response##*$'\n'}"
  body="${response%$'\n'*}"
  if [ -z "$body" ] || [[ ! "$http" =~ ^2 ]]; then
    return 1
  fi
  status="$(_ucode_is_success "$body")"
  if [ "$status" = "ok" ]; then
    _ucode_render "$body"
    return 0
  fi
  return 1
}

_print_ok_startup() {
  local payload
  payload="$(curl -sS "${ADMIN_HEADER[@]}" "${WIZARD_BASE_URL}/api/ucode/ok/status" || true)"
  if [ -z "$payload" ]; then
    return
  fi
  "$PYTHON_BIN" - <<'PY' "$payload"
import json, sys
raw = sys.argv[1]
try:
    data = json.loads(raw)
except Exception:
    sys.exit(0)

ok = data.get("ok") or {}
model = ok.get("model") or ok.get("default_model") or "unknown"
ctx = ok.get("context_window") or "?"
ready = ok.get("ready")
issue = ok.get("issue")
endpoint = ok.get("ollama_endpoint")
cloud = ok.get("cloud") or {}
cloud_ready = cloud.get("ready")
cloud_issue = cloud.get("issue")
auto_fallback = ok.get("auto_fallback")

print("\nVibe Local Status")
print("------------------")
if ready:
    print(f"OK: ready ({model}, ctx {ctx})")
else:
    msg = issue or "setup required"
    print(f"OK: attention ({msg}) ({model}, ctx {ctx})")
    if endpoint:
        print(f"Ollama endpoint: {endpoint}")
    if msg == "ollama down":
        print("Tip: start Ollama with `ollama serve`")
    if msg == "missing model":
        print(f"Tip: pull model with `ollama pull {model}`")
print("Mistral (cloud):", "ready" if cloud_ready else f"required ({cloud_issue or 'missing key'})")
if not cloud_ready:
    print("Tip: set MISTRAL_API_KEY or run SETUP")
print("OK fallback:", "auto" if auto_fallback else "manual")
print("Tip: OK EXPLAIN <file> | OK LOCAL")
PY
}

_vibe_prompt() {
  local prompt="$1"
  if ! vibe -p "$prompt" --continue --workdir "$REPO_ROOT"; then
    vibe -p "$prompt" --workdir "$REPO_ROOT"
  fi
}

_run_local_setup() {
  local raw="$1"
  "$PYTHON_BIN" - <<'PY' "$REPO_ROOT" "$raw"
import shlex
import sys
from pathlib import Path

repo_root = Path(sys.argv[1])
raw = sys.argv[2] if len(sys.argv) > 2 else ""
raw = raw.strip()
if raw.lower().startswith("setup"):
    raw = raw[5:].strip()
args = shlex.split(raw) if raw else []
sys.path.insert(0, str(repo_root))

from core.commands.setup_handler import SetupHandler

handler = SetupHandler()
result = handler.handle("SETUP", args, None, None)

def render(res):
    if isinstance(res, dict):
        output = res.get("output")
        if output:
            print(output)
            return
        message = res.get("message")
        if message:
            print(message)
            return
    print(res)

render(result)
PY
}

cd "$REPO_ROOT"

_fetch_allowlist
_print_ok_startup

echo "Vibe wrapper active."
echo "  AI: '?' or 'OK' (ex: ? explain this)"
echo "  Commands: '/' (ucode first, then shell if enabled)"
echo "  Auto: no prefix → ucode → shell → AI"

while true; do
  printf "> "
  IFS= read -r line || exit 0
  trimmed="${line#"${line%%[![:space:]]*}"}"
  [ -z "$trimmed" ] && continue

  case "$trimmed" in
    exit|quit) exit 0 ;;
  esac

  if [[ "$trimmed" == \?* ]]; then
    ok_payload="${trimmed#\?}"
    ok_payload="${ok_payload#"${ok_payload%%[![:space:]]*}"}"
    if [ -z "$ok_payload" ]; then
      _ucode_dispatch_print "OK" || true
    else
      _ucode_dispatch_print "OK $ok_payload" || true
    fi
    continue
  fi

  if [[ "$trimmed" =~ ^[Oo][Kk]($|[[:space:]]) ]]; then
    _ucode_dispatch_print "$trimmed" || true
    continue
  fi

  if [[ "$trimmed" == /* ]]; then
    cmd="${trimmed:1}"
    cmd="${cmd#"${cmd%%[![:space:]]*}"}"
    if [ -n "$cmd" ]; then
  if [[ "$cmd" =~ ^[Ss][Ee][Tt][Uu][Pp]($|[[:space:]]) ]]; then
        _run_local_setup "$cmd" || true
        continue
      fi
      first_token="${cmd%% *}"
      if _is_ucode_command "$first_token"; then
        _ucode_dispatch_print "$cmd" || true
      else
        _ucode_dispatch_print "/$cmd" || true
      fi
    fi
    continue
  fi

  if [[ "$trimmed" =~ ^[Ss][Ee][Tt][Uu][Pp]($|[[:space:]]) ]]; then
    _run_local_setup "$trimmed" || true
    continue
  fi

  first_token="${trimmed%% *}"
  if _is_ucode_command "$first_token"; then
    _ucode_dispatch_print "$trimmed" || true
    continue
  fi

  if _ucode_dispatch_quiet "/$trimmed"; then
    continue
  fi

  _vibe_prompt "$trimmed"
done
