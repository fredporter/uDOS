#!/bin/bash
# uOS Launcher – Fullscreen Optimised Terminal Boot (macOS)
# Author: Master & AI — Side by Side ∴ v1.0

#d────────────────────────────────────────────────────────────
#d uOS Terminal Layout Notes:
#d - Target character grid: 320x180 characters
#d - Bounds used: {0, 22, 2048, 1440} = Fullscreen on Retina 13–15"
#d - This can later support:
#d    > dynamic tput/stty screen sizing
#d    > tiled grid terminal interface
#d────────────────────────────────────────────────────────────

echo "🔁 Launching uOS..."

# Step into the uOS project root
cd ~/uOS || exit 1

# Stop any previously running containers
echo "🧼 Stopping previous uOS containers..."
docker compose down

# Rebuild Docker container to ensure updates apply
echo "🔨 Rebuilding uOS container..."
docker compose build

# Launch uOS in fullscreen terminal using AppleScript
echo "🚀 Starting uOS interactive shell in fullscreen..."

osascript <<EOF
tell application "Terminal"
    do script "cd ~/uOS && docker compose run --rm uos"
    delay 0.5
    set bounds of front window to {0, 22, 2048, 1440}
end tell
EOF

exit 0
