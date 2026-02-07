#!/bin/bash
# Vibe launcher (with Wizard MCP)

set -e

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
REPO_ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"
LOG_DIR="$REPO_ROOT/memory/logs/udos/scripts"
LOG_FILE="$LOG_DIR/vibe-launcher-$(date +%Y-%m-%d).jsonl"
LEGACY_LOG_DIR="$REPO_ROOT/memory/logs"
LEGACY_LOG_FILE="$LEGACY_LOG_DIR/vibe-launcher.log"
SESSION_ID="S-$(python3 -c 'import secrets; print(secrets.token_urlsafe(8))')"

mkdir -p "$LOG_DIR" "$LEGACY_LOG_DIR"

log_event() {
  local level="$1"
  local msg="$2"
  local event="${3:-launcher.event}"
  local ts
  ts="$(date -u +"%Y-%m-%dT%H:%M:%SZ")"
  printf '{"ts":"%s","ts_mono_ms":%s,"schema":"udos-log-v1.3","level":"%s","msg":"%s","component":"script","category":"launcher","event":"%s","session_id":"%s","corr_id":"-","ctx":{"script":"vibe-launcher"}}\n' \
    "$ts" "$(python3 -c 'import time; print(int(time.monotonic()*1000))')" "$level" "${msg//"/\\"}" "$event" "$SESSION_ID" >> "$LOG_FILE"
  printf '[%s] [%s] %s\n' "$ts" "$level" "$msg" >> "$LEGACY_LOG_FILE"
}

banner() {
  local reset=$'\033[0m'
  local colors=(1 3 2 6 4 5 1 3 2 6 4 5 1 3 2)
  local palette_file="$REPO_ROOT/wizard/dashboard/src/lib/util/udosPalette.ts"
  local palette_rgb=()
  local color_mode="${UDOS_BANNER_COLOR_MODE:-terminal}"
  if [ -f "$palette_file" ]; then
    while IFS= read -r line; do
      palette_rgb+=("$line")
    done < <(python3 -c 'import re, pathlib; data=pathlib.Path("'"$palette_file"'").read_text(); hexes=re.findall(r"hex:\\s*\\\"(#?[0-9A-Fa-f]{6})\\\"", data); \
print("\\n".join("{},{},{}".format(int(h[0:2],16), int(h[2:4],16), int(h[4:6],16)) for h in (x.lstrip("#") for x in hexes)))')
  fi
  local version_text="${UDOS_VERSION_TEXT:-uDOS v1.3.x}"
  if [ -f "$REPO_ROOT/version.json" ]; then
    local version_val
    version_val="$(python3 -c 'import json; from pathlib import Path; path=Path("'"$REPO_ROOT"'")/"version.json";\ntry:\n    data=json.loads(path.read_text());\n    print(data.get("display") or data.get("version") or "");\nexcept Exception:\n    print("")')"
    if [ -n "$version_val" ]; then
      version_text="uDOS $version_val"
    fi
  fi
  # Keep a fixed 11-char version block for clean alignment.
  local padded
  padded="$(printf '%-11s' "${version_text:0:11}")"
  local version_line="██   ████████████████   ${padded}   █████████████████   ██"
  local lines=(
"████████████████████████████████████████████████████████████"
"██                                                        ██"
"██   ██████████████████████████████████████████████████   ██"
"██   ██  ████  ███      ███      ███       ███       ██   ██"
"██   ██  ████  ██  ███████  ████  ██  ████  ██  ███████   ██"
"██   ██  ████  ██  ███████  ████  ██  ████  ██      ███   ██"
"██   ██  ████  ██  ███████  ████  ██  ████  ██  ███████   ██"
"██   ███      ████      ███      ███       ███       ██   ██"
"██   ██████████████████████████████████████████████████   ██"
"██   ███████████████    ███████████    ████████████████   ██"
"${version_line}"
"██   ██████████████████████████████████████████████████   ██"
"██                                                        ██"
"████████████████████████████████████████████████████████████"
  )
  local idx=0
  for line in "${lines[@]}"; do
    if [ "$color_mode" = "udos" ] && [ "${#palette_rgb[@]}" -gt 0 ]; then
      local rgb="${palette_rgb[$((idx % ${#palette_rgb[@]}))]}"
      local r g b
      IFS=, read -r r g b <<< "$rgb"
      printf "\033[38;2;%s;%s;%sm%s%s\n" "$r" "$g" "$b" "$line" "$reset"
    else
      local colour="${colors[$((idx % ${#colors[@]}))]}"
      printf "\033[3%sm%s%s\n" "$colour" "$line" "$reset"
    fi
    idx=$((idx + 1))
  done
}

progress_bar() {
  local step="$1"
  local total="$2"
  local width=40
  local filled=$(( step * width / total ))
  local empty=$(( width - filled ))
  local bar=""
  bar+="["
  bar+="$(printf '%0.s#' $(seq 1 $filled))"
  bar+="$(printf '%0.s-' $(seq 1 $empty))"
  bar+="]"
  printf "%s" "$bar"
}

health_checklist() {
  echo ""
  echo "Health checklist"
  echo "- If Wizard fails: run ./bin/Launch-uCODE.command wizard server"
  echo "- If Vibe CLI missing: pip install mistral-vibe"
  echo "- If Ollama down: ollama serve"
  echo "- If Mistral missing: set MISTRAL_API_KEY"
  echo "- If models missing: ollama pull <model>"
  echo "- If setup is blocked: run SETUP in uCODE"
  echo "- For stuck builds: REPAIR (from uCODE)"
}

ucode_ready_block() {
  echo ""
  echo "UCODE ready"
  echo "- AI prompts: '?' or 'OK'"
  echo "- Commands: '/' (ucode first, then shell if enabled)"
  echo "- Auto route: no prefix → ucode → shell → AI"
}

friendly_fail() {
  echo ""
  echo "Wizard server did not start."
  echo "Try: ./bin/Launch-uCODE.command wizard server"
  echo "Or run: REPAIR (from uCODE)"
  echo "Check logs: memory/logs/wizard-server.log and memory/logs/udos/scripts/vibe-launcher-$(date +%Y-%m-%d).jsonl"
}

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

echo ""
banner

if [ -z "${WIZARD_ADMIN_TOKEN:-}" ]; then
  log_event "warn" "WIZARD_ADMIN_TOKEN is not set."
  echo "WIZARD_ADMIN_TOKEN is not set."
  echo "uCODE-prefixed commands may fail until it is set."
fi

# Start Wizard server if not running
if ! curl -s --connect-timeout 2 "${WIZARD_BASE_URL}/health" >/dev/null 2>&1; then
  echo ""
  echo "Launching Wizard server..."
  log_event "info" "Wizard health check failed. Attempting to start server."
  if [ -x "$REPO_ROOT/.venv/bin/python3" ]; then
    PYTHON_CMD="$REPO_ROOT/.venv/bin/python3"
  else
    PYTHON_CMD="python3"
  fi
  (cd "$REPO_ROOT" && nohup "$PYTHON_CMD" -m wizard.server --no-interactive > "$REPO_ROOT/memory/logs/wizard-server.log" 2>&1 &)
  wizard_pid=$!

  total_steps=40
  for i in $(seq 1 $total_steps); do
    if curl -s --connect-timeout 2 "${WIZARD_BASE_URL}/health" >/dev/null 2>&1; then
      echo ""
      echo "Wizard server is live."
      log_event "info" "Wizard server started (PID ${wizard_pid})."
      break
    fi
    printf "\r%s %s" "$(progress_bar $i $total_steps)" "waiting for Wizard..."
    sleep 0.5
  done

  if ! curl -s --connect-timeout 2 "${WIZARD_BASE_URL}/health" >/dev/null 2>&1; then
    log_event "error" "Wizard server failed to start after wait loop."
    echo ""
    friendly_fail
    exit 1
  fi
else
  log_event "info" "Wizard server already running."
fi

health_checklist
ucode_ready_block

if ! command -v vibe >/dev/null 2>&1; then
  log_event "error" "vibe CLI not found. Install with: pip install mistral-vibe"
  echo ""
  echo "vibe CLI not found. Install with: pip install mistral-vibe"
  exit 1
fi

cd "$REPO_ROOT"

export VIBE_CONFIG_PATH="$REPO_ROOT/.vibe/config.toml"
echo ""
echo "Vibe is ready."
echo ""
exec "$REPO_ROOT/bin/vibe-wrapper.sh"
