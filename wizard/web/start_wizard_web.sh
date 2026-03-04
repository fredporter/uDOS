#!/bin/bash
# Start Wizard Server runtime (no embedded web app)
# Canonical lifecycle now routes through bin/udos.

set -euo pipefail

REPO_ROOT="$(cd "$(dirname "$0")/../.." && pwd)"
cd "$REPO_ROOT"

if [[ ! -x "${REPO_ROOT}/bin/udos" ]]; then
  echo "uDOS launcher is missing: ${REPO_ROOT}/bin/udos" >&2
  exit 1
fi

echo "Starting Wizard Server runtime via uDOS launcher..."
exec "${REPO_ROOT}/bin/udos" wizard start
