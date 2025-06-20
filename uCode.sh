#!/bin/bash
# uCode CLI v1.2 — Single-process Command Interface for uOS

# Set script directory
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

# Default paths
UOS_MEMORY_DIR="${UOS_MEMORY_DIR:-/uMemory}"
UOS_KNOWLEDGE_DIR="${UOS_KNOWLEDGE_DIR:-/uKnowledge}"
UOS_CONFIG_DIR="${UOS_CONFIG_DIR:-/config}"
MOVE_LOG="${UOS_MEMORY_DIR}/logs/moves.md"

# Print startup status
clear
echo "🌀 uCode loaded. Type 'help' for available commands."
echo ""
echo "📚 uKnowledge mounted at: $UOS_KNOWLEDGE_DIR"
echo "🧠 uMemory mounted at: $UOS_MEMORY_DIR"
echo "📝 Move log path: $MOVE_LOG"
echo "🔧 Config directory: $UOS_CONFIG_DIR"
echo ""

# Dashboard header
echo "╔═══════════════════[ uOS STATUS DASHBOARD ]════════════════════╗"
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
  echo "- [$ts] Move: \`$cmd\`" >> "$MOVE_LOG"
}

# Known command list
known=("dash" "map" "mission" "move" "tree" "list" "recent" "restart" "exit" "help")

# Begin CLI loop
while true; do
  read -rp "uCode > " cmd

  case "$cmd" in
    dash)
      bash "$SCRIPT_DIR/dashboard.sh"
      log_move "dash"
      ;;
    map)
      cat "$UOS_KNOWLEDGE_DIR/map/current_region.txt" 2>/dev/null || echo "No map loaded."
      log_move "map"
      ;;
    mission)
      cat "$UOS_MEMORY_DIR/state/current_mission.md" 2>/dev/null || echo "No mission active."
      log_move "mission"
      ;;
    move)
      echo "🔧 Move recorded at $(date)" >> "$MOVE_LOG"
      log_move "manual move"
      echo "Move recorded."
      ;;
    tree)
      bash "$SCRIPT_DIR/ucode-tree.sh"
      log_move "tree"
      ;;
    list)
      echo "📂 Current directory: $(pwd)"
      echo "📄 Visible contents:"
      ls -1p | grep -v '^\.' || echo "(empty)"
      log_move "list"
      ;;
    recent)
      echo "📜 Recent Moves:"
      tail -n 5 "$MOVE_LOG"
      log_move "recent"
      ;;
    restart)
      echo "🔄 Restarting uCode CLI..."
      log_move "restart"
      exec "$BASH_SOURCE"
      ;;
    exit)
      echo "👋 Exiting uCode CLI. Goodbye, Master."
      break
      ;;
    help)
      echo "🧭 Available Commands:"
      echo "  dash         → View dashboard"
      echo "  map          → Show current map region"
      echo "  mission      → View current mission"
      echo "  move         → Record manual move"
      echo "  tree         → View directory structure"
      echo "  list         → Show visible files"
      echo "  recent       → Tail move log"
      echo "  restart      → Restart this shell"
      echo "  exit         → Quit uCode"
      ;;
    *)
      echo "❓ Unknown command: $cmd"

      best_match=""
      shortest_distance=999
      for option in "${known[@]}"; do
        dist=$(echo "$cmd $option" | awk '
          function min(a,b,c) { return (a<b ? (a<c?a:c) : (b<c?b:c)) }
          function edit(s,t) {
            m = length(s)
            n = length(t)
            for (i=0;i<=m;i++) d[i,0]=i
            for (j=0;j<=n;j++) d[0,j]=j
            for (i=1;i<=m;i++) {
              for (j=1;j<=n;j++) {
                cost = (substr(s,i,1)==substr(t,j,1)) ? 0 : 1
                d[i,j] = min(d[i-1,j]+1, d[i,j-1]+1, d[i-1,j-1]+cost)
              }
            }
            return d[m,n]
          }
          { print edit($1,$2) }
        ')
        if (( dist < shortest_distance )); then
          shortest_distance=$dist
          best_match="$option"
        fi
      done

      if (( shortest_distance <= 2 )); then
        echo "💡 Did you mean: '$best_match'?"
      else
        echo "📘 Type 'help' for available commands."
      fi
      ;;
  esac
done