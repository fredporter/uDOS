#!/bin/bash
# Launch-uDOS.command v1.0 – Clean launch with resize & feedback
# uDOS by Master & ChatGPT

echo "🔁 Launching uDOS..."
echo "📦 uDOS Launcher v1.0"

# Resize current Terminal window BEFORE shell starts
osascript <<EOF
tell application "Terminal"
  set bounds of front window to {100, 100, 1380, 820}
end tell
EOF

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
echo "✅ uDOS session ended. Welcome back, Master."
