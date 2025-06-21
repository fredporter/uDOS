#!/bin/bash
# Launch-uOS.command v1.2 – Clean launch with resize & feedback
# uOS by Master & ChatGPT

echo "🔁 Launching uOS..."

# Resize current Terminal window BEFORE shell starts
osascript <<EOF
tell application "Terminal"
    set bounds of front window to {0, 22, 1280, 720}
end tell
EOF

# Step into uOS directory
cd ~/uOS || {
  echo "❌ Error: ~/uOS directory not found."
  exit 1
}

# Stop existing container
echo "🧼 Stopping previous uOS containers..."
docker compose down

# Rebuild container
echo "🔨 Rebuilding uOS container..."
docker compose build

# Launch uOS interactive shell (reuses this window)
echo "🚀 Starting uOS interactive shell..."
docker compose run --rm uos
