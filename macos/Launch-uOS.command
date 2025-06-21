#!/bin/bash
# Launch-uOS.command v1.4 – Clean launch with resize & feedback
# uOS by Master & ChatGPT

echo "🔁 Launching uOS..."

# Resize current Terminal window BEFORE shell starts
osascript <<EOF
tell application "Terminal"
  set bounds of front window to {100, 100, 1380, 820}
end tell
EOF

# Step into uOS directory
cd ~/uOS || {
  echo "❌ Error: ~/uOS directory not found."
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
echo "🧼 Stopping previous uOS containers..."
docker compose down || echo "⚠️  Nothing to stop."

# Rebuild container
echo "🔨 Rebuilding uOS container..."
docker compose build

# Launch uOS interactive shell (same window)
echo "🚀 Starting uOS interactive shell..."
docker compose run --rm uos
