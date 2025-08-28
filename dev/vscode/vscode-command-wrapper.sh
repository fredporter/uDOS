#!/bin/bash
# VS Code Command Wrapper for uDOS
# Safely executes uDOS commands through VS Code tasks

set -euo pipefail

# Get the uDOS root directory
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
UDOS_ROOT="$(cd "$SCRIPT_DIR/../.." && pwd)"

# Change to uDOS root directory
cd "$UDOS_ROOT"

# Execute the command router with the provided arguments
exec ./uCORE/code/command-router.sh "$@"
