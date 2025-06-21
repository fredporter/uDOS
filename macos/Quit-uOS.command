#!/bin/bash
# Quit-uOS.command — Graceful shutdown for uOS (macOS & Docker-aware)

echo "🛑 Shutting down uOS..."

# Resolve absolute path to root of uOS repo
SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
UOS_ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"

cd "$UOS_ROOT" || {
  echo "❌ Error: Unable to locate uOS root directory."
  exit 1
}

# 🧠 Timestamp + logging
TIMESTAMP="$(date +"%Y-%m-%d %H:%M:%S")"
LOG_DIR="$UOS_ROOT/uMemory/logs"
LOG_FILE="$LOG_DIR/dashlog-$(date +%Y-%m-%d).md"

mkdir -p "$LOG_DIR"
echo "- [$TIMESTAMP] Session closed via Quit-uOS.command" >> "$LOG_FILE"

# 🐳 Docker-safe shutdown
if ! command -v docker >/dev/null 2>&1; then
  echo "⚠️ Docker CLI not found in this environment."
  echo "   This is common when running from Finder or Automator."
else
  docker compose down >/dev/null 2>&1 && \
    echo "✅ uOS shutdown complete. All containers stopped." || \
    echo "⚠️ Could not stop Docker containers. Check Docker status."
fi