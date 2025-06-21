#!/bin/bash

# Terminal launch notes (160x90 characters ≈ 1280x720 pixels on most macOS fonts)
# Adjust window size manually or use AppleScript-based launcher if needed.

echo "🔁 Launching uOS..."

cd ~/uOS || exit

echo "🧼 Stopping previous uOS containers..."
docker-compose down

echo "🔨 Rebuilding uOS container..."
docker-compose build

echo "🚀 Starting uOS interactive shell..."
docker-compose run --rm uos
