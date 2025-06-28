#!/bin/bash
# start.sh – uDOS inside-container entrypoint

UHOME="/root/uDOS"
echo "🌀 Launching uDOS..."

# Create required directories
bash "$UHOME/scripts/make-structure.sh"

# Run full identity and system setup
bash "$UHOME/scripts/check-setup.sh"

# Only then launch the uCode shell
exec bash "$UHOME/scripts/uCode.sh"