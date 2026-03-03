#!/usr/bin/env bash
set -euo pipefail

unset UDOS_ROOT
unset USER_NAME
unset USER_ROLE
unset MISTRAL_API_KEY
unset UDOS_LOG_RING
export UV_PROJECT_ENVIRONMENT="${UV_PROJECT_ENVIRONMENT:-.venv}"

PYTEST_DISABLE_PLUGIN_AUTOLOAD=1 uv run --group dev python -m pytest \
  -p pytest_asyncio.plugin \
  -p pytest_timeout \
  -p xdist.plugin \
  -p anyio.pytest_plugin \
  -p respx.plugin \
  -p syrupy \
  -p pytest_textual_snapshot \
  "$@"
