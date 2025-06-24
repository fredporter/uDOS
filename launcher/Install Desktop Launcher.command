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

echo "🎨 Skipping icon embedding: no iconset or .icns file found in this folder."
echo "📝 To add a custom app icon, place 'diamond-icon.iconset' or 'diamond.icns' in the same folder and re-run this script."

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