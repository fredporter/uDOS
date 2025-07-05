#!/bin/bash

# uDOS macOS App Launcher Builder
# Author: Otter, your terminal companion 🦦


set -e
set -x


APP_DIR="$PWD/uDOS.app"
MACOS_DIR="$APP_DIR/Contents/MacOS"
RESOURCES_DIR="$APP_DIR/Contents/Resources"
PLIST_PATH="$APP_DIR/Contents/Info.plist"
LAUNCH_SCRIPT="$MACOS_DIR/uDOS_Launcher"
ICON_SRC="$(dirname "$0")/assets/diamond.icns"
ICON_DST="$RESOURCES_DIR/uDOS.icns"

echo "📁 Building uDOS.app at: $APP_DIR"
echo "🔧 Creating uDOS macOS App bundle..."

# Create directory structure
mkdir -p "$MACOS_DIR" "$RESOURCES_DIR"

# Create Info.plist
cat > "$PLIST_PATH" <<EOF
<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN"
 "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0">
<dict>
  <key>CFBundleExecutable</key>
  <string>uDOS_Launcher</string>
  <key>CFBundleIdentifier</key>
  <string>com.uos.launcher</string>
  <key>CFBundleName</key>
  <string>uDOS</string>
  <key>CFBundleVersion</key>
  <string>1.0</string>
  <key>CFBundleIconFile</key>
  <string>uDOS.icns</string>
  <key>NSAppleScriptEnabled</key>
  <true/>
  <key>CFBundleURLTypes</key>
  <array>
    <dict>
      <key>CFBundleURLName</key>
      <string>Quit uDOS</string>
      <key>CFBundleURLSchemes</key>
      <array>
        <string>quitudos</string>
      </array>
    </dict>
  </array>
</dict>
</plist>
EOF

# Create launch script
cat > "$LAUNCH_SCRIPT" <<EOF
#!/bin/bash
# uDOS macOS Launcher (final hybrid version)

APP_ROOT="\$(cd "\$(dirname "\$0")/../.." && pwd)"
chmod +x "\$APP_ROOT/scripts/start.sh"
chmod +x "\$APP_ROOT/launcher/uDOS_Run.sh"

/usr/bin/osascript <<OSA
tell application "Terminal"
  if not (exists window 1) then reopen
  activate
  do script "cd \$APP_ROOT/launcher; bash uDOS_Run.sh"
end tell
OSA

sleep 2
EOF

chmod +x "$LAUNCH_SCRIPT"

# Use prebuilt .icns if available
if [[ -f "$ICON_SRC" ]]; then
  echo "💎 Copying diamond.icns to app bundle..."
  cp "$ICON_SRC" "$ICON_DST"
else
  echo "⚠️  No launcher/diamond.icns found — skipping icon installation."
fi

# Add Quit-uDOS.command inside the app bundle
QUIT_SCRIPT_SRC="Quit-uDOS.command"
QUIT_SCRIPT_DST="$MACOS_DIR/Quit-uDOS.command"

if [[ -f "$QUIT_SCRIPT_SRC" ]]; then
  echo "🛑 Embedding Quit-uDOS.command..."
  cp "$QUIT_SCRIPT_SRC" "$QUIT_SCRIPT_DST"
  chmod +x "$QUIT_SCRIPT_DST"
else
  echo "⚠️  Quit-uDOS.command not found — skipping embed."
fi

# Clear Gatekeeper quarantine flags (for local dev)
echo "🧹 Removing macOS quarantine flags..."
xattr -dr com.apple.quarantine "$APP_DIR"

echo "✅ uDOS.app has been created at: $APP_DIR"
open "$APP_DIR"

# --- Ensure .gitignore entries for generated files
echo "🛡️  Updating .gitignore for generated files..."
GITIGNORE_PATH="$(dirname "$0")/.gitignore"
IGNORE_ENTRIES=(
  "/launcher/uDOS_installation.log"
  "/launcher/uDOS.app"
)

for entry in "${IGNORE_ENTRIES[@]}"; do
  grep -qxF "$entry" "$GITIGNORE_PATH" || echo "$entry" >> "$GITIGNORE_PATH"
done