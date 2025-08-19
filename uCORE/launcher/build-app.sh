#!/bin/bash
# uDOS macOS App Builder
# Creates a simple, clean .app bundle for Finder

set -e

APP_DIR="$PWD/uDOS.app"
MACOS_DIR="$APP_DIR/Contents/MacOS"
RESOURCES_DIR="$APP_DIR/Contents/Resources"
PLIST_PATH="$APP_DIR/Contents/Info.plist"
LAUNCH_SCRIPT="$MACOS_DIR/uDOS_Launcher"
ICON_SRC="$(dirname "$0")/assets/diamond.icns"
ICON_DST="$RESOURCES_DIR/uDOS.icns"

echo "🍎 Building uDOS.app"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"

# Clean up old app
if [[ -d "$APP_DIR" ]]; then
    echo "🧹 Removing old app bundle..."
    rm -rf "$APP_DIR"
fi

# Create directory structure
mkdir -p "$MACOS_DIR" "$RESOURCES_DIR"

# Create modern Info.plist
cat > "$PLIST_PATH" <<EOF
<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN"
 "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0">
<dict>
  <key>CFBundleExecutable</key>
  <string>uDOS_Launcher</string>
  <key>CFBundleIdentifier</key>
  <string>com.udos.modern</string>
  <key>CFBundleName</key>
  <string>uDOS Modern</string>
  <key>CFBundleDisplayName</key>
  <string>uDOS Modern</string>
  <key>CFBundleVersion</key>
  <string>2.0</string>
  <key>CFBundleShortVersionString</key>
  <string>2.0</string>
  <key>CFBundleIconFile</key>
  <string>uDOS.icns</string>
  <key>LSUIElement</key>
  <false/>
  <key>NSHighResolutionCapable</key>
  <true/>
  <key>NSRequiresAquaSystemAppearance</key>
  <false/>
</dict>
</plist>
EOF

# Create modern launch script
cat > "$LAUNCH_SCRIPT" <<'EOF'
#!/bin/bash
# Modern uDOS Launcher Script

UDOS_PATH="$HOME/uDOS"

# Check if uDOS exists
if [[ ! -d "$UDOS_PATH" ]]; then
    /usr/bin/osascript <<OSA
display dialog "uDOS not found at ~/uDOS

Please clone the repository first:
git clone https://github.com/fredporter/uDOS.git ~/uDOS" buttons {"OK"} default button "OK" with icon stop
OSA
    exit 1
fi

# Check for VS Code
if command -v code &> /dev/null; then
    # Show choice dialog
    choice=$(/usr/bin/osascript <<OSA
display dialog "🌀 uDOS Modern Launcher

Choose your preferred launch method:" buttons {"Terminal", "VS Code", "Cancel"} default button "VS Code" with icon note
button returned of result
OSA
)

    case "$choice" in
        "VS Code")
            cd "$UDOS_PATH"
            code .
            /usr/bin/osascript <<OSA
display notification "uDOS opened in VS Code! Use Cmd+Shift+P → '🌀 Start uDOS'" with title "uDOS Modern"
OSA
            ;;
        "Terminal")
            cd "$UDOS_PATH"
            /usr/bin/osascript <<OSA
tell application "Terminal"
    activate
    if not (exists window 1) then
        do script "cd '$UDOS_PATH' && exec ./uCORE/launcher/universal/start-udos.sh"
    else
        do script "cd '$UDOS_PATH' && exec ./uCORE/launcher/universal/start-udos.sh" in window 1
    end if
end tell
OSA
            ;;
        "Cancel")
            exit 0
            ;;
    esac
else
    # No VS Code, launch in Terminal
    cd "$UDOS_PATH"
    /usr/bin/osascript <<OSA
tell application "Terminal"
    activate
    if not (exists window 1) then
        do script "cd '$UDOS_PATH' && exec ./uCORE/launcher/universal/start-udos.sh"
    else
        do script "cd '$UDOS_PATH' && exec ./uCORE/launcher/universal/start-udos.sh" in window 1
    end if
end tell
OSA
fi
EOF

chmod +x "$LAUNCH_SCRIPT"

# Copy icon if available
if [[ -f "$ICON_SRC" ]]; then
    echo "💎 Adding app icon..."
    cp "$ICON_SRC" "$ICON_DST"
else
    echo "⚠️  No icon found - using default"
fi

# Clear quarantine flags
echo "🧹 Clearing quarantine flags..."
xattr -dr com.apple.quarantine "$APP_DIR" 2>/dev/null || true

echo "✅ Modern uDOS app created: $APP_DIR"
echo "📱 You can now drag this to Applications or Dock"

# Open in Finder
open -R "$APP_DIR"
