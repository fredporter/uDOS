#!/bin/bash

# uOS Launcher Script
# Ensure Docker container runs interactively with uCode prompt

echo "🔁 Launching uOS..."

# Step into Docker folder inside ~/uOS
cd ~/uOS/docker || {
  echo "❌ Failed to find uOS docker folder."
  exit 1
}

# Shutdown any existing container
echo "🧼 Stopping previous uOS containers..."
docker-compose down

# Rebuild container
echo "🔨 Rebuilding uOS container..."
docker-compose build

# Run uOS interactively with terminal input/output
echo "🚀 Starting uOS interactive shell..."
docker-compose run --rm uos