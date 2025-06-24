#!/bin/bash
# uDOS_Launcher.sh – Full launch logic for uDOS from Terminal
# uDOS by Master & Otter 🦦 v1.0

echo "🔁 Launching uDOS..."

# Resize the current Terminal window
osascript <<APPLESCRIPT
tell application "Terminal"
  set bounds of front window to {100, 100, 1380, 820}
end tell
APPLESCRIPT

# Navigate to uDOS directory
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

# Optional: Prepare logs directory
mkdir -p ~/uDOS/logs

# Stop any existing containers
echo "🧼 Stopping previous uDOS containers..."
docker compose down || echo "⚠️  Nothing to stop."

# Rebuild the container
echo "🔨 Rebuilding uDOS container..."
docker compose build

# Launch interactive uDOS shell and pipe output to log (optional)
echo "🚀 Starting uDOS interactive shell..."
exec docker compose run --rm udos | tee -a ~/uDOS/logs/udos-$(date +%Y-%m-%d).log