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
  
  # List of known commands
known=("dash" "map" "mission" "move" "tree" "list" "recent" "restart" "exit" "help")

  # Find closest match using simple edit distance logic
  best_match=""
  shortest_distance=999

  for option in "${known[@]}"; do
    dist=$(echo "$cmd $option" | awk '
      function min(a,b,c) {
        return (a<b ? (a<c?a:c) : (b<c?b:c))
      }
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
      {
        print edit($1,$2)
      }')

    if (( dist < shortest_distance )); then
      shortest_distance=$dist
      best_match="$option"
    fi
  done

  if (( shortest_distance <= 2 )); then
    echo "💡 Did you mean: '$best_match'?"
  else
    echo "📘 Type 'help' for a list of available commands."
  fi
  ;;
  esac
done