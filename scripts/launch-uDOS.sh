#!/bin/bash
# launch-uDOS.sh

UDOSE_HOME="${UDOSE_HOME:-$HOME/uDOS}"

echo "🌀 Launching uDOS..."

# Run setup check — use absolute path inside container
"$UDOSE_HOME/scripts/check-setup.sh"

# Start uCode CLI or Dashboard
"$UDOSE_HOME/scripts/uCode.sh"