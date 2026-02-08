#!/bin/bash
# uCODE lightweight launcher (core|wizard|goblin)

set -e

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
REPO_ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"
LOG_DIR="$REPO_ROOT/memory/logs/udos/scripts"
LOG_FILE="$LOG_DIR/ucode-launcher-$(date +%Y-%m-%d).jsonl"
LEGACY_LOG_DIR="$REPO_ROOT/memory/logs"
LEGACY_LOG_FILE="$LEGACY_LOG_DIR/ucode-launcher.log"
SESSION_ID="S-$(python3 -c 'import secrets; print(secrets.token_urlsafe(8))')"

mkdir -p "$LOG_DIR" "$LEGACY_LOG_DIR"

log_event() {
    local level="$1"
    local msg="$2"
    local event="${3:-launcher.event}"
    local ts
    ts="$(date -u +"%Y-%m-%dT%H:%M:%SZ")"
    printf '{"ts":"%s","ts_mono_ms":%s,"schema":"udos-log-v1.3","level":"%s","msg":"%s","component":"script","category":"launcher","event":"%s","session_id":"%s","corr_id":"-","ctx":{"script":"ucode-launcher"}}\n' \
      "$ts" "$(python3 -c 'import time; print(int(time.monotonic()*1000))')" "$level" "${msg//"/\\"}" "$event" "$SESSION_ID" >> "$LOG_FILE"
    printf '[%s] [%s] %s\n' "$ts" "$level" "$msg" >> "$LEGACY_LOG_FILE"
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

show_ucode_banner() {
    if _udos_is_quiet; then
        return 0
    fi

    REPO_ROOT="$REPO_ROOT" python3 - <<'PY' 2>/dev/null || true
import os
from core.commands.draw_handler import DrawHandler

handler = DrawHandler()
result = handler.handle("DRAW", ["block", "ucodesmile-ascii.md", "--rainbow"])
output = result.get("output") if isinstance(result, dict) else None
if output:
    print(output)
    print("")
else:
    path = os.path.join(os.environ.get("REPO_ROOT", ""), "memory", "system", "ucodesmile-ascii.md")
    try:
        with open(path, "r") as f:
            print(f.read())
            print("")
    except Exception:
        pass
PY
}

start_wizard_if_needed() {
    local base_url="${WIZARD_BASE_URL:-http://localhost:8765}"
    if curl -s --connect-timeout 2 "${base_url}/health" >/dev/null 2>&1; then
        log_event "info" "Wizard server already running."
        return 0
    fi

    if [ "${WIZARD_AUTOSTART:-1}" = "0" ]; then
        log_event "warn" "Wizard autostart disabled."
        return 0
    fi

    echo ""
    echo "Launching Wizard server..."
    log_event "info" "Wizard health check failed. Attempting to start server."
    if [ -x "$REPO_ROOT/.venv/bin/python3" ]; then
        PYTHON_CMD="$REPO_ROOT/.venv/bin/python3"
    elif [ -x "$REPO_ROOT/.venv/bin/python" ]; then
        PYTHON_CMD="$REPO_ROOT/.venv/bin/python"
    else
        PYTHON_CMD="python3"
    fi
    (cd "$REPO_ROOT" && nohup "$PYTHON_CMD" -m wizard.server --no-interactive > "$REPO_ROOT/memory/logs/wizard-server.log" 2>&1 &)

    total_steps=40
    for i in $(seq 1 $total_steps); do
        if curl -s --connect-timeout 2 "${base_url}/health" >/dev/null 2>&1; then
            echo ""
            echo "Wizard server is live."
            log_event "info" "Wizard server started."
            return 0
        fi
        printf "\r[%d/%d] waiting for Wizard..." "$i" "$total_steps"
        sleep 0.5
    done

    echo ""
    log_event "error" "Wizard server failed to start after wait loop."
    echo "Wizard server did not start. Try: ./bin/Launch-uCODE.command wizard server"
    return 1
}

load_env_safe() {
    local env_file="$1"
    [ -f "$env_file" ] || return 0
    while IFS= read -r line || [ -n "$line" ]; do
        # Trim leading/trailing whitespace
        line="${line#"${line%%[![:space:]]*}"}"
        line="${line%"${line##*[![:space:]]}"}"
        # Skip blanks and comments
        [ -z "$line" ] && continue
        case "$line" in
            \#*) continue ;;
        esac
        # Strip optional leading export
        if [[ "$line" == export\ * ]]; then
            line="${line#export }"
        fi
        # Only accept KEY=VALUE lines
        if [[ "$line" =~ ^[A-Za-z_][A-Za-z0-9_]*= ]]; then
            local key="${line%%=*}"
            local value="${line#*=}"
            # Remove surrounding quotes if present
            if [[ "$value" =~ ^\".*\"$ ]]; then
                value="${value:1:${#value}-2}"
            elif [[ "$value" =~ ^\'.*\'$ ]]; then
                value="${value:1:${#value}-2}"
            fi
            export "$key=$value"
        fi
    done < "$env_file"
}

load_env_safe "$REPO_ROOT/.env"

source "$SCRIPT_DIR/udos-common.sh"

parse_common_flags "$@"

component="${1:-core}"
mode="${2:-}"

# Preserve TTY for prompt_toolkit (bottom toolbar + live hints)
if [ -z "$UDOS_TTY" ]; then
    export UDOS_TTY=1
fi

# Check for --rebuild flag in any position
for arg in "$@"; do
    if [ "$arg" = "--rebuild" ]; then
        export UDOS_REBUILD=1
        echo "🔄 Rebuild mode: Clearing Python cache..."
    fi
done

case "$component" in
    core|wizard|goblin) ;;
    --rebuild)
        # If --rebuild is first arg, default to core
        component="core"
        ;;
    *)
        echo "Usage: ./Launch-uCODE.command [core|wizard|goblin] [mode] [--rebuild] [--quiet] [--tty] [--no-log]" >&2
        exit 1
        ;;
esac

if [ -z "$mode" ]; then
    case "$component" in
        core) mode="tui" ;;
        wizard) mode="server" ;;
        goblin) mode="dev" ;;
    esac
fi

# Core TUI is now the single entry point (Vibe routing merged)
if [ "$component" = "core" ] && [ "$mode" = "tui" ]; then
    export UDOS_LAUNCHER_BANNER=1
    show_ucode_banner
    health_checklist
fi

# Strip --rebuild from args before passing to launch
args=()
for arg in "$@"; do
    if [ "$arg" != "--rebuild" ] && [ "$arg" != "$component" ] && [ "$arg" != "$mode" ]; then
        args+=("$arg")
    fi
done

launch_component "$component" "$mode" "${args[@]}"
