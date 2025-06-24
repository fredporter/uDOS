#!/bin/bash
# uDOS Platypus Launcher Builder
# Requires Platypus CLI installed via https://sveinbjorn.org/platypus

APP_NAME="uDOS Launcher"
ICON_PATH="$(cd "$(dirname "$0")" && pwd)/diamond.icns"
SCRIPT_PATH="$HOME/.udos/$APP_NAME"
DEST_APP="$HOME/Desktop/$APP_NAME.app"

echo "🔍 Checking for Platypus CLI..."
if ! command -v platypus &> /dev/null; then
  echo "❌ Platypus CLI not found. Please install it from https://sveinbjorn.org/platypus and ensure 'platypus' is in your PATH."
  exit 1
fi

echo "🧹 Removing previous launcher..."
rm -rf "$DEST_APP"

echo "🚀 Building $APP_NAME with Platypus..."
platypus \
  -a "$APP_NAME" \
  -o None \
  -i "$ICON_PATH" \
  -p /bin/bash \
  -V "1.0" \
  -B \
  -R \
  "$SCRIPT_PATH" \
  "$DEST_APP"

if [ $? -eq 0 ]; then
  echo "✅ Launcher built successfully: $DEST_APP"
else
  echo "❌ Failed to build launcher"
fi