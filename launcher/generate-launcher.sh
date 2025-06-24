#!/bin/bash
# uDOS Launcher Generator v1.0
# Otter x Master

DESKTOP_PATH=~/Desktop
ICON_NAME="diamond.icns"
ICONSET_PATH="$(cd "$(dirname "$0")" && pwd)/diamond-icon.iconset"
ICON_SOURCE="$(cd "$(dirname "$0")" && pwd)/${ICON_NAME}"

echo "🔎 Checking iconset and converting if needed..."

if [ ! -f "$ICON_SOURCE" ]; then
  if [ -d "$ICONSET_PATH" ]; then
    echo "🔄 Converting iconset to .icns..."
    iconutil -c icns "$ICONSET_PATH" -o "$ICON_SOURCE"
    echo "✅ Created icon file at $ICON_SOURCE"
  else
    echo "❌ Iconset not found at $ICONSET_PATH. Skipping conversion."
  fi
else
  echo "✅ Icon found at $ICON_SOURCE"
fi

SCRIPT_NAME="uDOS Launcher"

mkdir -p "$HOME/.udos"
TARGET_SCRIPT="$HOME/.udos/$SCRIPT_NAME"

echo "🔧 Generating uDOS Launcher on Desktop..."

# 1. Create directory for the launcher shortcut
# mkdir -p "$LAUNCHER_DIR"

# 2. Write the launch script
cat > "$TARGET_SCRIPT" <<'EOF'
#!/bin/bash
# uDOS Launcher v1.0 – Clean launch with resize & feedback
# uDOS by Master & ChatGPT

echo "🔁 Launching uDOS..."

# Resize current Terminal window BEFORE shell starts
osascript <<APPLESCRIPT
tell application "Terminal"
  set bounds of front window to {100, 100, 1380, 820}
end tell
APPLESCRIPT

# Step into uDOS directory
cd ~/uDOS || {
  echo "❌ Error: ~/uDOS directory not found."
  exit 1
}

# Ensure Docker is running
if ! docker info >/dev/null 2>&1; then
  echo "🐳 Starting Docker Desktop..."
  open -a Docker
  while ! docker info >/dev/null 2>&1; do
    echo "⌛ Waiting for Docker to initialise..."
    sleep 2
  done
fi

# Stop any existing containers (cleanup)
echo "🧼 Stopping previous uDOS containers..."
docker compose down || echo "⚠️  Nothing to stop."

# Rebuild container
echo "🔨 Rebuilding uDOS container..."
docker compose build

# Launch uDOS interactive shell (same window)
echo "🚀 Starting uDOS interactive shell..."
docker compose run --rm udos
EOF

# 3. Make the script executable
chmod +x "$TARGET_SCRIPT"

# 4. Attach custom icon (if available)
if [ -f "$ICON_SOURCE" ]; then
  echo "🎨 Assigning icon to launcher..."
  cp "$ICON_SOURCE" "$DESKTOP_PATH/diamond.icns"
  defaults write "$DESKTOP_PATH/Info" CFBundleIconFile "diamond.icns"
  touch "$DESKTOP_PATH"
else
  echo "⚠️  Icon not found at $ICON_SOURCE. Skipping icon assignment."
fi

echo "✅ uDOS Launcher script created internally at: $TARGET_SCRIPT"

# 5. Create uDOS Launcher .app wrapper using shell-based binary
APP_NAME="uDOS Launcher.app"
APP_PATH="$DESKTOP_PATH/$APP_NAME"

echo "🧱 Creating .app wrapper at $APP_PATH..."

mkdir -p "$APP_PATH/Contents/MacOS"
mkdir -p "$APP_PATH/Contents/Resources"

# Write Info.plist
cat > "$APP_PATH/Contents/Info.plist" <<EOF
<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0">
<dict>
  <key>CFBundleExecutable</key>
  <string>uDOS-Wrapper</string>
  <key>CFBundleIconFile</key>
  <string>diamond</string>
  <key>CFBundleIdentifier</key>
  <string>com.master.udos.launcher</string>
  <key>CFBundleName</key>
  <string>uDOS Launcher</string>
  <key>CFBundlePackageType</key>
  <string>APPL</string>
</dict>
</plist>
EOF

# Create executable wrapper script
cat > "$APP_PATH/Contents/MacOS/uDOS-Wrapper" <<EOF
#!/bin/bash
bash ~/launcher/Launcher.command
EOF

chmod +x "$APP_PATH/Contents/MacOS/uDOS-Wrapper"

echo "🎉 .app Launcher created: $APP_PATH"