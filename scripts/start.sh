#!/bin/bash
# start.sh – uDOS inside-container entrypoint

UHOME="/root/uDOS"
if [ -s "$UHOME/sandbox/user.md" ]; then
  echo "✅ User profile already initialized: $UHOME/sandbox/user.md"
  exit 0
fi
echo "🌀 Launching uDOS..."

# Create required directories
bash "$UHOME/scripts/make-structure.sh"

# Run full identity and system setup
bash "$UHOME/scripts/check-setup.sh"

# Only then launch the uCode shell
exec bash "$UHOME/scripts/uCode.sh"