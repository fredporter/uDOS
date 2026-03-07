#!/usr/bin/env bash
set -euo pipefail

REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$REPO_ROOT"

export UV_PROJECT_ENVIRONMENT="${UV_PROJECT_ENVIRONMENT:-.venv}"
export PYTHONWARNINGS="${PYTHONWARNINGS:-error}"

if [[ -x "./.venv/bin/python" ]]; then
  PYTHON_BIN="./.venv/bin/python"
elif command -v python3 >/dev/null 2>&1; then
  PYTHON_BIN="$(command -v python3)"
else
  echo "No python interpreter found (expected .venv or python3 on PATH)." >&2
  exit 127
fi

echo "[demo] strict core stdlib python lane"
"$PYTHON_BIN" -m py_compile scripts/check_core_stdlib_contract.py
"$PYTHON_BIN" scripts/check_core_stdlib_contract.py

PYTEST_DISABLE_PLUGIN_AUTOLOAD=1 uv run --group dev python -m pytest \
  -p pytest_asyncio.plugin \
  -p pytest_timeout \
  core/tests/ucode_min_spec_command_test.py \
  core/tests/workflow_handler_test.py \
  core/tests/workflow_scheduler_test.py \
  core/tests/ulogic_parser_test.py \
  "$@"

echo "[demo] strict core stdlib python lane passed"
