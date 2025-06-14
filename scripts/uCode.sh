#!/bin/bash
# uCode CLI - interactive shell for uOS

# Set script directory
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

# Print startup status
echo "🌀 uCode CLI started. Type 'help' to begin."
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

# Begin CLI loop
while true; do
  read -rp "uCode > " cmd

  case "$cmd" in
    dashboard)
      $SRC_DIR/dashboard.sh
      log_move "dashboard"
      ;;
    help)
      echo "Commands: dashboard, map, mission, move, tree, log, lost, recent, restart, exit"
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
      echo "Move recorded."
      ;;
    tree)
      SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
      bash "$SCRIPT_DIR/ucode-tree.sh"
      echo ""
      echo "🌳 Repository Structure:"
      cat "$SCRIPT_DIR/../repo_structure.txt"
      log_move "tree"
      ;;
    lost)
      echo "📂 Current directory: $(pwd)"
      echo "📄 Visible contents:"
      ls -1p | grep -v '^\.' || echo "(empty)"
      log_move "lost"
      ;;
    log)
      "$SCRIPT_DIR/ulogger.sh"
      log_move "log"
      ;;
    recent)
      echo "📜 Recent Moves:"
      tail -n 5 "${UOS_MEMORY_DIR:-/uMemory}/logs/moves.md"
      log_move "recent"
      ;;
    restart)
      echo "🔄 Restarting uCode CLI..."
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