#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_ROOT="$(cd "${SCRIPT_DIR}/.." && pwd)"

cd "${REPO_ROOT}/core"
echo "[demo] Running core renderer regression tests"
npm run -s test:renderer
npm run -s test:renderer-cli
echo "[demo] Renderer regression checks passed"
