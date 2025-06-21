#!/bin/bash
# Quit-uOS.command – graceful shutdown for uOS

echo "🛑 Shutting down uOS..."

# Get path of this .command script and go up to root uOS dir
SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
cd "$SCRIPT_DIR/.." || {
  echo "❌ Error: Unable to locate uOS root directory."
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
