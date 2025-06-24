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

echo "🎉 Done! Launcher created at: $DEST_APP"
open "$DEST_APP"