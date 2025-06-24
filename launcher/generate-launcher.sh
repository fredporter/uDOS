#!/bin/bash
# uDOS Launcher Generator v1.0
# Otter x Master

DESKTOP_PATH=~/Desktop
SCRIPT_NAME="uDOS Launcher"
ICON_NAME="diamond.icns"
ICON_SOURCE="$HOME/.udos/${ICON_NAME}"

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
  echo "💎 Applying diamond icon..."
  # Convert .icns to .rsrc using iconutil & DeRez if needed (macOS specific)
  /usr/bin/osascript <<APPLESCRIPT
  set iconPath to POSIX file "$ICON_SOURCE" as alias
  set targetFile to POSIX file "$TARGET_SCRIPT" as alias
  tell application "Finder"
    set icon of targetFile to icon of iconPath
  end tell
APPLESCRIPT
else
  echo "⚠️  Icon not found at $ICON_SOURCE. Skipping icon assignment."
fi

echo "✅ uDOS Launcher script created internally at: $TARGET_SCRIPT"

# 5. Create uDOS Launcher .app wrapper
APP_NAME="uDOS Launcher.app"
APP_PATH="$DESKTOP_PATH/$APP_NAME"

echo "🧱 Creating .app wrapper at $APP_PATH..."

# Use Automator-style AppleScript app as wrapper
APPLESCRIPT_WRAPPER='
on run
  do shell script "bash $HOME/.udos/uDOS\\ Launcher"
end run
'

# Build using osacompile
osacompile -o "$APP_PATH" -e "$APPLESCRIPT_WRAPPER"

ICONSET_PATH="launcher/diamond-icon.iconset"

if [ ! -f "$ICON_SOURCE" ]; then
  if [ -d "$ICONSET_PATH" ]; then
    echo "🔄 Converting iconset to .icns..."
    iconutil -c icns "$ICONSET_PATH" -o "$ICON_SOURCE"
  else
    echo "❌ Iconset not found at $ICONSET_PATH. Skipping conversion."
  fi
fi

# Apply icon if available
if [ -f "$ICON_SOURCE" ]; then
  echo "🎨 Applying icon to .app..."
  /usr/bin/osascript <<APPLESCRIPT
  set iconPath to POSIX file "$ICON_SOURCE" as alias
  set appPath to POSIX file "$APP_PATH" as alias
  tell application "Finder"
    set icon of appPath to icon of iconPath
  end tell
APPLESCRIPT
else
  echo "⚠️  Icon not found at $ICON_SOURCE. Skipping .app icon assignment."
fi

echo "🎉 .app Launcher created: $APP_PATH"