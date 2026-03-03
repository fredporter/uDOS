#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_ROOT="$(cd "${SCRIPT_DIR}/.." && pwd)"

if ! command -v go >/dev/null 2>&1; then
  echo "Go toolchain not found. Install Go 1.22+ to build udos-tui." >&2
  exit 127
fi

mkdir -p "${REPO_ROOT}/tui/bin"
cd "${REPO_ROOT}/tui"
go build -o "${REPO_ROOT}/tui/bin/udos-tui" ./cmd/udos-tui
echo "Built ${REPO_ROOT}/tui/bin/udos-tui"
