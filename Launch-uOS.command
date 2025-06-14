#!/bin/bash

echo "🔁 Launching uOS..."

# Step into the uOS root directory
cd ~/uOS || exit

# Stop existing containers (if any)
echo "🧼 Stopping previous uOS containers..."
docker-compose down

# Rebuild container
echo "🔨 Rebuilding uOS container..."
docker-compose build

# Launch uOS CLI shell
echo "🚀 Starting uOS interactive shell..."
docker-compose run --rm uos