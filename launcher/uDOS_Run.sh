#!/bin/bash

# Set UROOT as the project root (one level up from this script)
export UROOT="$(cd "$(dirname "$0")/.." && pwd)"
export UHOME="$HOME"

# Ensure we always run from project root
cd "$UROOT"

# Check if ucode.sh exists
if [ ! -f "$UROOT/uCode/ucode.sh" ]; then
  echo "❌ uCode script not found at $UROOT/uCode/ucode.sh"
  echo "➡️  Please check your uDOS installation or adjust uDOS_Run.sh"
  exit 1
fi

# Start the uCode system
bash "$UROOT/uCode/ucode.sh"
