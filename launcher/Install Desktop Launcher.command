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

echo "🧩 Creating ~/.udos/uDOS Launcher target script..."
mkdir -p "$HOME/.udos"

LAUNCHER_TARGET="$HOME/.udos/uDOS Launcher"

if [ ! -f "$LAUNCHER_TARGET" ]; then
  cat <<EOF > "$LAUNCHER_TARGET"
#!/bin/bash
echo '🚀 uDOS Launcher script running!'
cd \$HOME/uDOS && open -a Terminal .
EOF
  chmod +x "$LAUNCHER_TARGET"
  echo "✅ Created default launcher script at ~/.udos/uDOS Launcher"
else
  echo "ℹ️ Found existing launcher at ~/.udos/uDOS Launcher"
fi

echo "✅ uDOS Launcher installed. You may now double-click it from your Desktop!"