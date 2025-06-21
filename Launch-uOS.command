#!/bin/bash

# ╔════════════════════════════════════════════════════════════════╗
# ║ uOS Launcher (Mac)                                            ║
# ║ Launches Docker + Terminal window at custom resolution        ║
# ╚════════════════════════════════════════════════════════════════╝

# 1. Define base directory
cd ~/uOS || exit

# 2. Optional: Prelaunch Docker.app if not running
if ! pgrep -f Docker.app >/dev/null; then
  echo "🐳 Starting Docker Desktop..."
  open -a Docker
  while ! docker system info >/dev/null 2>&1; do
    echo "⌛ Waiting for Docker to initialise..."
    sleep 2
  done
fi

# 3. Stop previous containers (cleanup)
echo "🔁 Launching uOS..."
echo "🧼 Stopping previous uOS containers..."
docker-compose down

# 4. Rebuild container
echo "🔨 Rebuilding uOS container..."
docker-compose build

# 5. Launch full-resolution uOS terminal via AppleScript (macOS-specific)
osascript <<EOF
  tell application "Terminal"
    do script "cd ~/uOS && docker-compose run --rm uos"
    delay 0.5
    set bounds of front window to {100, 100, 1400, 1000} -- approx 160x90 char grid
  end tell
EOF

exit 0
