#!/bin/bash
# uDOS Platypus Launcher Builder
# Requires Platypus CLI installed via https://sveinbjorn.org/platypus

APP_NAME="uDOS Launcher"
ICON_PATH="$(cd "$(dirname "$0")" && pwd)/diamond.icns"
SCRIPT_PATH="$HOME/.udos/$APP_NAME"
DEST_APP="$HOME/Desktop/$APP_NAME.app"

echo "🔍 Checking for Platypus CLI..."
if ! command -v platypus &> /dev/null; then
  echo "❌ Platypus CLI not found."
  echo "📦 Attempting to install via Homebrew..."
  if ! command -v brew &> /dev/null; then
    echo "🔧 Homebrew not found. Installing Homebrew first..."
    /bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"
    export PATH="/opt/homebrew/bin:$PATH"
  fi
  brew install --cask platypus
  if [ ! -f "/usr/local/bin/platypus" ]; then
    echo "🔗 Linking Platypus CLI..."
    sudo ln -s /Applications/Platypus.app/Contents/MacOS/Platypus /usr/local/bin/platypus
  fi
  if ! command -v platypus &> /dev/null; then
    echo "❌ Platypus installation failed. Please install manually from https://sveinbjorn.org/platypus"
    exit 1
  fi
  echo "✅ Platypus installed successfully!"
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

echo "🔓 Removing macOS quarantine flag..."
xattr -d com.apple.quarantine "$DEST_APP" 2>/dev/null || echo "⚠️ Could not remove quarantine attribute (may not be set)."

if [ $? -eq 0 ]; then
  echo "✅ Launcher built successfully: $DEST_APP"
else
  echo "❌ Failed to build launcher"
fi