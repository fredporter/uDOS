#!/bin/bash
# start.sh – uDOS inside-container entrypoint

UHOME="/root/uDOS"
echo "🌀 Launching uDOS..."

# Initialize directory structure
bash "$UHOME/scripts/make-structure.sh"

# Check setup and permissions
bash "$UHOME/scripts/check-setup.sh"

# Start the CLI
exec bash "$UHOME/scripts/uCode.sh"