#!/bin/bash
# Native uDOS Launcher App Creator – No Platypus

APP_NAME="uDOS Launcher"
SCRIPT_PATH="$HOME/uDOS/launcher/app-wrapper.sh"
ICON_PATH="$HOME/uDOS/launcher/diamond.icns"
DEST_APP="$HOME/Desktop/$APP_NAME.app"

echo "🧹 Cleaning up previous launcher..."
rm -rf "$DEST_APP"

echo "📁 Creating app bundle structure..."
mkdir -p "$DEST_APP/Contents/MacOS"
mkdir -p "$DEST_APP/Contents/Resources"

echo "📄 Copying script..."
cp "$SCRIPT_PATH" "$DEST_APP/Contents/MacOS/$APP_NAME"
chmod +x "$DEST_APP/Contents/MacOS/$APP_NAME"

echo "🎨 Adding icon..."
cp "$ICON_PATH" "$DEST_APP/Contents/Resources/diamond.icns"

echo "🧠 Writing Info.plist..."
cat > "$DEST_APP/Contents/Info.plist" <<EOF
<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN"
  "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0">
<dict>
  <key>CFBundleExecutable</key>
  <string>$APP_NAME</string>
  <key>CFBundleIdentifier</key>
  <string>com.agentdigital.udos.launcher</string>
  <key>CFBundleName</key>
  <string>$APP_NAME</string>
  <key>CFBundleIconFile</key>
  <string>diamond</string>
</dict>
</plist>
EOF

echo "🔓 Removing quarantine flags..."
xattr -dr com.apple.quarantine "$DEST_APP"

echo "✅ Desktop launcher installed successfully. You may now open it from the Desktop."

# 📦 Install Terminal profile if available
PROFILE_SOURCE="$HOME/uDOS/launcher/uDOS.terminal"
if [[ -f "$PROFILE_SOURCE" ]]; then
  echo "🖼️ Installing Terminal profile..."
  open "$PROFILE_SOURCE"
  sleep 2
  osascript -e 'tell application "Terminal" to close front window' &>/dev/null
  defaults write com.apple.Terminal "Startup Window Settings" -string "uDOS"
  defaults write com.apple.Terminal "Default Window Settings" -string "uDOS"
  echo "✅ Terminal profile 'uDOS' imported and set as default."

  echo "🧠 Writing AppleScript launcher to open Terminal cleanly..."
  cat > "$DEST_APP/Contents/MacOS/$APP_NAME" <<LAUNCHER
#!/bin/bash
osascript -e 'tell application "Terminal" to do script "bash ~/uDOS/scripts/uCode.sh"'
LAUNCHER
  chmod +x "$DEST_APP/Contents/MacOS/$APP_NAME"
else
  echo "⚠️ Terminal profile 'uDOS.terminal' not found. Skipping profile setup."
fi
