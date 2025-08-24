#!/bin/bash
# uDOS v1.4 Display System Setup Wrapper
# Redirects to the actual setup script in uNETWORK/display

set -euo pipefail

# Get the directory where this script is located
UDOS_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

# Check if the actual setup script exists
SETUP_SCRIPT="$UDOS_ROOT/uNETWORK/display/setup-display-system.sh"

if [[ ! -f "$SETUP_SCRIPT" ]]; then
    echo "❌ Display system setup script not found at: $SETUP_SCRIPT"
    echo "   Please ensure uNETWORK/display/setup-display-system.sh exists"
    exit 1
fi

# Make sure it's executable
chmod +x "$SETUP_SCRIPT"

# Pass all arguments to the actual setup script
exec "$SETUP_SCRIPT" "$@"
