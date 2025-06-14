#!/bin/bash

# uOS Launcher Script
# Launches uOS from Mac into Docker with full path mapping for repo sync

echo "🔁 Launching uOS..."

# Step into uOS project directory
cd ~/uOS || {
  echo "❌ Could not enter ~/uOS"
  exit 1
}

# Ensure any previous session is closed
echo "🧼 Stopping previous uOS containers..."
docker-compose down

# Rebuild to catch changes
echo "🔨 Rebuilding uOS container..."
docker-compose build

# Launch container interactively with mounted repo path
echo "🚀 Starting uOS interactive shell..."
docker-compose run --rm uos