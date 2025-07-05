#!/bin/bash
# uDOS_Run.sh – Full launch logic for uDOS (minimal tab version)
# uDOS by Master & Otter 🦦

echo "🐚 Running uDOS..."
echo "Welcome to uDOS, your personal OS 🦦"

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
  echo "✅ Docker is now running."
fi


# Stop any existing containers
echo "🧼 Cleaning up previous uDOS containers..."
docker compose down || echo "⚠️  Nothing to stop."

# Rebuild the container
echo "🔨 Rebuilding uDOS container..."
docker compose build

# Launch interactive uDOS shell and pipe output to log
echo "🚀 Starting uDOS interactive shell..."
docker compose run --rm udos scripts/start.sh | tee

