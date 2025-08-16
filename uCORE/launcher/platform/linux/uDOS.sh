#!/bin/bash
# Linux uDOS Launcher
# Cross-distribution launcher for Linux systems

# Set working directory to script location
cd "$(dirname "$0")"

# Navigate to uDOS root (assuming launcher is in uCORE/launcher/platform/linux)
UDOS_ROOT="$(cd ../../../.. && pwd)"

# Source universal launcher
source "$UDOS_ROOT/uCORE/launcher/universal/start-udos.sh"
