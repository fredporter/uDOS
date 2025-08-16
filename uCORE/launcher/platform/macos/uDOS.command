#!/bin/bash
# macOS uDOS Launcher
# Double-click launcher for Finder integration

# Set working directory to script location
cd "$(dirname "$0")"

# Navigate to uDOS root (assuming launcher is in uCORE/launcher/platform/macos)
UDOS_ROOT="$(cd ../../../.. && pwd)"

# Source universal launcher
source "$UDOS_ROOT/uCORE/launcher/universal/start-udos.sh"
