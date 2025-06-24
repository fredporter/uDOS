#!/bin/bash
# uDOS Launcher Generator v1.0
# Otter x Master

DESKTOP_PATH=~/Desktop
ICON_NAME="diamond.icns"

# Try both icon locations
ICON_SOURCE=""
if [ -f "$(cd "$(dirname "$0")" && pwd)/Contents/Resources/diamond.icns" ]; then
  ICON_SOURCE="$(cd "$(dirname "$0")" && pwd)/Contents/Resources/diamond.icns"
elif [ -f "$(cd "$(dirname "$0")" && pwd)/diamond.icns" ]; then
  ICON_SOURCE="$(cd "$(dirname "$0")" && pwd)/diamond.icns"
else
  echo "⚠️  No icon source found. App will use default icon."
fi

echo "🔎 Using icon source: $ICON_SOURCE"

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

APP_NAME="uDOS Launcher.app"
APP_PATH="$DESKTOP_PATH/$APP_NAME"

echo "🧹 Cleaning previous launcher at $APP_PATH..."
rm -rf "$APP_PATH"

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
bash ~/.udos/uDOS\ Launcher
EOF

chmod +x "$APP_PATH/Contents/MacOS/uDOS-Wrapper"

ICON_DEST="$APP_PATH/Contents/Resources/diamond.icns"

if [ -n "$ICON_SOURCE" ] && [ -f "$ICON_SOURCE" ]; then
  echo "🎨 Copying icon into app bundle..."
  cp "$ICON_SOURCE" "$ICON_DEST"
  touch "$APP_PATH"
  if command -v SetFile >/dev/null 2>&1; then
    /usr/bin/SetFile -a C "$APP_PATH"
    echo "✅ Custom icon flag set"
  else
    echo "⚠️  SetFile not available; skipping custom icon flag"
  fi
else
  echo "⚠️  No valid icon source found, skipping custom icon."
fi

# Force macOS to refresh icon cache
echo "🔁 Refreshing Finder icon cache..."
touch "$APP_PATH"
qlmanage -r > /dev/null 2>&1
qlmanage -r cache > /dev/null 2>&1

# Clean up accidental loose files on Desktop
rm -f "$DESKTOP_PATH/diamond.icns"
rm -f "$DESKTOP_PATH/Info.plist"

echo "🎉 .app Launcher created: $APP_PATH"