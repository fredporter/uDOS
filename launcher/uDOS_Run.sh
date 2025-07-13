#!/bin/bash

# Set UROOT as the project root (one level up from this script)
export UROOT="$(cd "$(dirname "$0")/.." && pwd)"
export UHOME="$HOME"

# Ensure we always run from project root
cd "$UROOT"

# Start the uCode system
bash uCode/uCode.sh
