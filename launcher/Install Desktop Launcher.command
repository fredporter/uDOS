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

ICON_SOURCE="$(pwd)/diamond.icns"
APP_PATH="$HOME/Desktop/uDOS Launcher.app"

if [ -f "$ICON_SOURCE" ]; then
  echo "💎 Copying icon to app bundle..."
  mkdir -p "$APP_PATH/Contents/Resources"
  cp "$ICON_SOURCE" "$APP_PATH/Contents/Resources/diamond.icns"
  touch "$APP_PATH"
  killall Finder
  echo "✅ Icon embedded successfully."
else
  echo "⚠️ Icon file not found at $ICON_SOURCE. Skipping icon embedding."
fi

echo "✅ uDOS Launcher installed. You may now double-click it from your Desktop!"