#!/usr/bin/env bash
set -euo pipefail

export UV_PROJECT_ENVIRONMENT="${UV_PROJECT_ENVIRONMENT:-.venv}"

python3 -m py_compile scripts/check_core_stdlib_contract.py
python3 scripts/check_core_stdlib_contract.py

PYTEST_DISABLE_PLUGIN_AUTOLOAD=1 uv run --group dev python -m pytest \
  -p pytest_asyncio.plugin \
  -p pytest_timeout \
  core/tests/ucode_min_spec_command_test.py \
  core/tests/workflow_handler_test.py \
  core/tests/workflow_scheduler_test.py \
  core/tests/ulogic_parser_test.py \
  "$@"
