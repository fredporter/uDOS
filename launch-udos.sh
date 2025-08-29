#!/bin/bash
# Unified uDOS launcher: Starts uCORE-Shell in CLI mode

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
UDOS_ROOT="$SCRIPT_DIR"

cd "$UDOS_ROOT"

if [ -x "./udos" ]; then
    ./udos shell
else
    echo "Error: uDOS executable not found in $UDOS_ROOT."
    exit 1
fi
