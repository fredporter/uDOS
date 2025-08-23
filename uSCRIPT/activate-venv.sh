#!/bin/bash
# Activate uSCRIPT Python virtual environment
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
source "$SCRIPT_DIR/venv/python/bin/activate"
echo "uSCRIPT Python virtual environment activated"
echo "Use 'deactivate' to exit"
