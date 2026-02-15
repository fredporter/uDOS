#!/bin/bash
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
REPO_ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"

TAG=""
VENV_DIR=".venv-smoke"
RUN_NPM_CI=1
KEEP_VENV=0

usage() {
  cat <<'USAGE'
Usage:
  ./bin/release-smoke.sh [--tag <tag>] [--venv <dir>] [--skip-npm-ci] [--keep-venv]

Examples:
  ./bin/release-smoke.sh --tag v1.3.13-rc.3
  ./bin/release-smoke.sh --venv .venv-rc
USAGE
}

while [ $# -gt 0 ]; do
  case "$1" in
    --tag)
      TAG="${2:-}"
      shift 2
      ;;
    --venv)
      VENV_DIR="${2:-}"
      shift 2
      ;;
    --skip-npm-ci)
      RUN_NPM_CI=0
      shift
      ;;
    --keep-venv)
      KEEP_VENV=1
      shift
      ;;
    -h|--help)
      usage
      exit 0
      ;;
    *)
      echo "Unknown option: $1" >&2
      usage
      exit 2
      ;;
  esac
done

cd "$REPO_ROOT"
export UDOS_ROOT="$REPO_ROOT"
export UDOS_MEMORY_ROOT="${UDOS_MEMORY_ROOT:-$REPO_ROOT/memory}"
export UDOS_QUIET="${UDOS_QUIET:-0}"
export UDOS_NO_LOG="${UDOS_NO_LOG:-0}"
export UDOS_TTY="${UDOS_TTY:-0}"
export UDOS_REBUILD="${UDOS_REBUILD:-0}"
export UDOS_FLAG_MODE="${UDOS_FLAG_MODE:-0}"
export UDOS_VENV_DIR="${UDOS_VENV_DIR:-$REPO_ROOT/.venv}"

WIZARD_STARTED=0
WIZARD_PORT=""
WIZARD_PID=""

cleanup() {
  if [ "$WIZARD_STARTED" -eq 1 ] && [ -n "$WIZARD_PID" ]; then
    if kill -0 "$WIZARD_PID" 2>/dev/null; then
      echo "Stopping Wizard server (PID $WIZARD_PID)..."
      kill "$WIZARD_PID" 2>/dev/null || true
    fi
  fi
}
trap cleanup EXIT

echo "==> Release smoke start"

if [ -n "$TAG" ]; then
  echo "==> Checkout tag: $TAG"
  git fetch --tags
  git checkout "$TAG"
fi

echo "==> Commit: $(git rev-parse --short HEAD)"

if [ "$KEEP_VENV" -eq 0 ]; then
  rm -rf "$VENV_DIR"
fi

echo "==> Creating virtual environment: $VENV_DIR"
python3 -m venv "$VENV_DIR"
source "$VENV_DIR/bin/activate"

echo "==> Installing package with wizard extras"
python -m pip install -U pip
python -m pip install '.[wizard]'
python -m pip install pytest httpx

echo "==> Running wizard tests"
python -m pytest -q wizard/tests

if [ "$RUN_NPM_CI" -eq 1 ]; then
  echo "==> Installing wizard dashboard deps (npm ci)"
  npm -C "$REPO_ROOT/wizard/dashboard" ci
fi

echo "==> Building wizard dashboard"
npm -C "$REPO_ROOT/wizard/dashboard" run build

echo "==> CLI help check"
"$REPO_ROOT/bin/ucli" --help >/dev/null

WIZARD_PORT="$(python - <<'PY'
import json
from pathlib import Path
port = 8765
cfg = Path("wizard/config/wizard.json")
try:
    if cfg.exists():
        data = json.loads(cfg.read_text())
        port = int(data.get("port", port))
except Exception:
    pass
print(port)
PY
)"
BASE_URL="http://127.0.0.1:${WIZARD_PORT}"

if curl -fsS --connect-timeout 2 "${BASE_URL}/health" >/dev/null 2>&1; then
  echo "==> Wizard already running on ${BASE_URL}"
else
  echo "==> Starting Wizard server"
  mkdir -p "$REPO_ROOT/memory/logs"
  nohup python -m wizard.server --no-interactive > "$REPO_ROOT/memory/logs/wizard-server.log" 2>&1 &
  WIZARD_PID="$!"
  for _ in $(seq 1 30); do
    if curl -fsS --connect-timeout 1 "${BASE_URL}/health" >/dev/null 2>&1; then
      break
    fi
    sleep 1
  done
  curl -fsS --connect-timeout 2 "${BASE_URL}/health" >/dev/null
  WIZARD_STARTED=1
  echo "==> Wizard started on ${BASE_URL} (PID: ${WIZARD_PID})"
fi

check_any_endpoint() {
  local name="$1"
  shift
  local path code
  for path in "$@"; do
    code="$(curl -sS -o /dev/null -w "%{http_code}" "${BASE_URL}${path}" || true)"
    case "$code" in
      200)
        echo "PASS ${name} via ${path} (${code})"
        return 0
        ;;
      401|403)
        echo "PASS ${name} via ${path} (${code}, auth-protected)"
        return 0
        ;;
    esac
  done
  echo "FAIL ${name} (paths tried: $*)" >&2
  return 1
}

check_any_optional_endpoint() {
  local name="$1"
  shift
  if check_any_endpoint "$name" "$@"; then
    return 0
  fi
  echo "WARN ${name} optional endpoint not available"
  return 0
}

echo "==> Endpoint checks"
check_any_endpoint "health" "/health" "/api/health"
check_any_endpoint "dashboard" "/dashboard"
check_any_optional_endpoint "logs api" "/api/logs"
check_any_optional_endpoint "ports api" "/api/ports" "/api/ports/list"
check_any_endpoint "ok status" "/api/ucode/ok/status"

echo "==> Release smoke passed"
