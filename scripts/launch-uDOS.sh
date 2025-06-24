#!/bin/bash
# launch-uDOS.sh – uDOS inside-container entrypoint

UDOSE_HOME="/root/uDOS"
echo "🌀 Launching uDOS..."

# Initialize directory structure
bash "$UDOSE_HOME/scripts/init-structure.sh"

# Check setup and permissions
bash "$UDOSE_HOME/scripts/check-setup.sh"

# Start the CLI
exec bash "$UDOSE_HOME/scripts/uCode.sh"