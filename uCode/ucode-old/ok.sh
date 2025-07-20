#!/bin/bash
# OK Companion - Quick access to uCompanions
# This is a simple wrapper that calls the OK Companion from the visual framework

# Set up environment
UHOME="${HOME}/uDOS"

# Check if visual framework exists
if [[ -f "${UHOME}/uCode/visual-framework.sh" ]]; then
    # Call the OK companion function
    "${UHOME}/uCode/visual-framework.sh" ok
else
    echo "❌ uDOS Visual Framework not found"
    echo "Please ensure uDOS is properly installed"
    exit 1
fi
