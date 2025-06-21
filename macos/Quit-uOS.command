#!/bin/bash
# Quit-uOS.command — Graceful shutdown for uOS (macOS & Docker-aware)

echo "🛑 Shutting down uOS..."

# Resolve absolute path to root of uOS repo
SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
UOS_ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"
export PATH="/usr/local/bin:/opt/homebrew/bin:/usr/bin:/bin:$PATH"

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

# After successful shutdown
echo "✅ uOS shutdown complete."

# Auto-close Terminal window if on macOS
if [[ "$OSTYPE" == "darwin"* ]]; then
  osascript -e 'tell application "Terminal" to close front window' &>/dev/null
fi