#!/usr/bin/env bash
set -euo pipefail

REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$REPO_ROOT"

export UV_PROJECT_ENVIRONMENT="${UV_PROJECT_ENVIRONMENT:-.venv}"

if [[ -x "./.venv/bin/python" ]]; then
  PYTHON_BIN="./.venv/bin/python"
else
  echo "Missing .venv Python. Run ./bin/udos install first." >&2
  exit 127
fi

if [[ ! -x "./bin/udos" ]]; then
  echo "Missing launcher: ./bin/udos" >&2
  exit 127
fi

echo "[demo] strict wizard advanced command lane"

# CLI smoke: ensure launcher command contract is reachable and JSON serializable.
status_json="$(./bin/udos --json status)"
"$PYTHON_BIN" -c 'import json,sys; p=json.loads(sys.stdin.read()); assert "action" in p and p["action"]=="status"; assert "details" in p' <<<"$status_json"

# Strict advanced command coverage for launcher + repair + port conflict handling.
"$PYTHON_BIN" -m pytest -q -n0 \
  wizard/tests/udos_launcher_cli_test.py \
  wizard/tests/udos_launcher_service_test.py \
  wizard/tests/port_manager_service_test.py \
  "$@"

echo "[demo] strict wizard advanced command lane passed"
