#!/bin/bash
# uCode CLI - interactive shell for uOS

# Set script directory
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

# Print startup status
echo "🌀 uCode started. Type 'help' to begin."
echo ""
echo "📁 Checking system state..."

# Show mounting and logging
echo "📚 uKnowledge mounted at: ${UOS_KNOWLEDGE_DIR:-/uKnowledge}"
echo "🧠 uMemory mounted at: ${UOS_MEMORY_DIR:-/uMemory}"
echo "📝 Move log path: ${UOS_MEMORY_DIR:-/uMemory}/logs/moves.md"
echo "🔧 Config directory: ${UOS_CONFIG_DIR:-/config}"
echo ""

# Dashboard Display
echo "╔═══════════════════[ uOS DASHBOARD ]════════════════════╗"
echo "║ User: Master                                            ║"
echo "║ Location: The Crypt                                     ║"
echo "║ Mission: Activate uCode Interface                      ║"
echo "║ Date: $(date +"%A, %d %B %Y %H:%M:%S")                  ║"
echo "╚═════════════════════════════════════════════════════════╝"
echo ""

# Move logger
log_move() {
  local cmd="$1"
  local ts
  ts=$(date +"%Y-%m-%d %H:%M:%S")
  local log_path="${UOS_MEMORY_DIR:-/uMemory}/logs/moves.md"
  echo "- [$ts] Move: \`$cmd\`" >> "$log_path"
}

UOS_MEMORY_DIR="${UOS_MEMORY_DIR:-/uMemory}"

# Begin CLI loop
while true; do
  read -rp "uCode > " cmd

  case "$cmd" in
    dash)
      $SCRIPT_DIR/dashboard.sh
      log_move "dashboard check"
      ;;
    help)
      echo "Commands: dash, map, mission, move, tree, list, recent, restart, exit"
      ;;
    map)
      cat /uKnowledge/map/current_region.txt 2>/dev/null || echo "No map loaded."
      log_move "map"
      ;;
    mission)
      cat /uMemory/state/current_mission.md 2>/dev/null || echo "No mission active."
      log_move "mission"
      ;;
    move)
      echo "🔧 Move recorded at $(date)" >> "${UOS_MEMORY_DIR:-/uMemory}/logs/moves.md"
      log_move "manual move"
      echo "Manual move recorded."
      ;;
    tree)
      bash "$SCRIPT_DIR/ucode-tree.sh"
      log_move "tree"
      ;;
    list)
      echo "📂 Current directory: $(pwd)"
      echo "📄 Listing contents:"
      ls -1p | grep -v '^\.' || echo "(empty)"
      log_move "list directory"
      ;;
    recent)
      echo "📜 Recent Moves:"
      tail -n 5 "$UOS_MEMORY_DIR/logs/moves.md"
      log_move "recent"
      ;;
    restart)
      echo "🔄 Restarting uCode ..."
      log_move "restart"
      exec "$BASH_SOURCE"
      ;;
    exit)
      echo "Exiting uOS..."
      break
      ;;
    *)
      echo "❓ Unknown command: $cmd"
      ;;
  esac
done