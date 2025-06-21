#!/bin/bash
# Quit-uOS.command – graceful shutdown for uOS

echo "🛑 Shutting down uOS..."

# Navigate to uOS directory
cd ~/uOS || {
  echo "❌ Error: ~/uOS directory not found."
  exit 1
}

# Log shutdown timestamp
timestamp=$(date +"%Y-%m-%d %H:%M:%S")
log_file="./uMemory/logs/dashlog-$(date +"%Y-%m-%d").md"

# Ensure log directory exists
mkdir -p ./uMemory/logs

echo "- [$timestamp] Session closed via Quit-uOS.command" >> "$log_file"

# Stop and remove containers and network
docker compose down

echo "✅ uOS shutdown complete. All containers stopped."
