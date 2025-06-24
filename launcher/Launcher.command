#!/bin/bash
# uDOS Launcher Installer for macOS
# Version: v1.0

echo "🚀 Installing uDOS Launcher to your Desktop..."
echo "📦 uDOS Launcher v1.0"

# Ensure this script runs from inside the launcher folder
cd "$(dirname "$0")"

# Run the generator
chmod +x generate-launcher.sh
./generate-launcher.sh

echo "✅ uDOS Launcher installed. You may now double-click it from your Desktop!"