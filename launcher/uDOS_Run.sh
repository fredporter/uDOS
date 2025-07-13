#!/bin/bash

# Set UROOT as the project root (2 levels up from this script)
export UROOT="$(cd "$(dirname "$0")/.." && pwd)"
export UHOME="$HOME"

# Ensure we always run from root
cd "$UROOT/uCode"

# Start the system
bash start.sh
