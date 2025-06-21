#!/bin/bash
# uCode v1.4.2 – Unified Shell for uOS with logging and fallback editor

# Resolve script location
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
UOS_ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"

# Paths
UOS_MEMORY_DIR="${UOS_MEMORY_DIR:-$UOS_ROOT/uMemory}"
UOS_TEMPLATE_DIR="${UOS_TEMPLATE_DIR:-$UOS_ROOT/templates}"
UOS_LOG_DIR="$UOS_MEMORY_DIR/logs"
UOS_MOVES_DIR="$UOS_LOG_DIR/moves"
UOS_ERROR_DIR="$UOS_LOG_DIR/errors"
DASHLOG="$UOS_LOG_DIR/dashlog-$(date '+%Y-%m-%d').md"

# Init logging folders
mkdir -p "$UOS_MOVES_DIR" "$UOS_ERROR_DIR"

# Error logging helper
log_error() {
  local msg="$1"
  local now="$(date '+%Y-%m-%d %H:%M:%S')"
  echo "- [$now] $msg" >> "$UOS_ERROR_DIR/error-$(date '+%Y-%m-%d').md"
}

# Move logger
log_move() {
  local cmd="$1"
  local ts=$(date '+%Y-%m-%d %H:%M:%S')
  local id=$(date +%s)
  local file="$UOS_MOVES_DIR/$(date '+%Y-%m-%d')-move-${id}.md"

  {
    echo "---"
    echo "id: move-${id}"
    echo "type: move"
    echo "timestamp: ${ts}"
    echo "user: $(whoami)"
    echo "container: uos-container"
    echo "description: "$cmd""
    echo "result: "${cmd_output}""
    echo "tags: [uos, move, log]"
    echo "---"
    echo ""
    echo "## ➤ Move"
    echo ""
    echo "**Command:**"
    echo "\`\`\`bash"
    echo "$cmd"
    echo "\`\`\`"
    echo ""
    echo "**Output:**"
    echo "\`\`\`"
    echo "$cmd_output"
    echo "\`\`\`"
  } > "$file"

  echo "- [${ts}] Move: \`$cmd\` → [$file]" >> "$DASHLOG"
}

# Startup Display
clear
echo "🌀 uCode CLI v1.4.2 started."
echo "📚 Knowledge: $UOS_ROOT/uKnowledge"
echo "🧠 Memory: $UOS_MEMORY_DIR"
echo "📝 Moves Log: $UOS_MOVES_DIR"
echo "🔧 Config: $UOS_ROOT/config"
echo ""

echo "╔═══════════════════[ uOS DASHBOARD ]════════════════════╗"
echo "║ User: Master                                            ║"
echo "║ Location: The Crypt                                     ║"
echo "║ Mission: Activate uCode Interface                      ║"
echo "║ Date: $(date '+%A, %d %B %Y %H:%M:%S')                  ║"
echo "╚═════════════════════════════════════════════════════════╝"
echo "- Session started at $(date)" >> "$DASHLOG"

# Command List
commands=("new" "log" "redo" "undo" "run" "dash" "recent" "map" "mission" "move" "tree" "list" "restart" "exit" "help")

# Begin CLI
while true; do
  read -rp "🌀 uCode→ " cmd args

  case "$cmd" in
    new)
      if [[ "$args" == "move" ]]; then
        ts=$(date +%s)
        out="$UOS_MEMORY_DIR/moves/$(date '+%Y-%m-%d')-move-${ts}.md"
        cp "$UOS_TEMPLATE_DIR/move-template.md" "$out" || { log_error "Template not found: move-template.md"; continue; }
        ${EDITOR:-nano} "$out" || log_error "Editor failed or not set"
        log_move "new move"
      else
        echo "⚠️  new type not supported"
      fi
      ;;
    run)
      script="$UOS_ROOT/scripts/${args}.sh"
      if [ -f "$script" ]; then
        cmd_output="$(bash "$script" 2>&1)"
        echo "$cmd_output"
        log_move "run $args.sh"
      else
        echo "❌ Script not found: $script"
        log_error "Script missing: $script"
      fi
      ;;
    dash)
      bash "$SCRIPT_DIR/dashboard.sh" || log_error "Dashboard script failed"
      log_move "dash"
      ;;
    recent)
      tail -n 5 "$DASHLOG"
      ;;
    map)
      cat "$UOS_ROOT/uKnowledge/map/current_region.txt" 2>/dev/null || echo "No map found"
      log_move "map"
      ;;
    mission)
      cat "$UOS_MEMORY_DIR/state/current_mission.md" 2>/dev/null || echo "No active mission"
      log_move "mission"
      ;;
    move)
      echo "Manual move at $(date)" >> "$DASHLOG"
      log_move "manual move"
      ;;
    tree)
      bash "$SCRIPT_DIR/ucode-tree.sh"
      log_move "tree"
      ;;
    list)
      ls -1p | grep -v '^\.' || echo "(empty)"
      log_move "list"
      ;;
    restart)
      echo "Restarting shell..."
      exec "$BASH_SOURCE"
      ;;
    exit)
      echo "Goodbye."
      break
      ;;
    help)
      echo "🧭 Commands:"
      printf "  %s\n" "${commands[@]}"
      ;;
    *)
      echo "❓ Unknown command: $cmd"
      ;;
  esac
done
