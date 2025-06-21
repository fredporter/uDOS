#!/bin/bash
# uCode v1.4.2 — Unified command shell for uOS with logging and fallback support

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
UOS_ROOT="$(dirname "$SCRIPT_DIR")"

# Default directories
UOS_MEMORY_DIR="${UOS_MEMORY_DIR:-$UOS_ROOT/uMemory}"
UOS_KNOWLEDGE_DIR="${UOS_KNOWLEDGE_DIR:-$UOS_ROOT/uKnowledge}"
UOS_CONFIG_DIR="${UOS_CONFIG_DIR:-$UOS_ROOT/config}"
MOVE_LOG="$UOS_MEMORY_DIR/logs/moves/moves.md"

source "$SCRIPT_DIR/error-logger.sh"

ensure_dirs() {
  mkdir -p "$UOS_MEMORY_DIR/logs/moves"
  mkdir -p "$UOS_MEMORY_DIR/logs/errors"
  mkdir -p "$UOS_MEMORY_DIR/state"
}
ensure_dirs

echo "🌀 uCode CLI started. Type 'help' for available commands."
echo "📚 uKnowledge: $UOS_KNOWLEDGE_DIR"
echo "🧠 uMemory: $UOS_MEMORY_DIR"
echo "📝 Log file: $MOVE_LOG"
echo ""

session_ts=$(date)
echo "- Session started at $session_ts" >> "$MOVE_LOG"

log_move() {
  local cmd="$1"
  local now="$(date '+%Y-%m-%d %H:%M:%S')"
  local move_id="$(date +%s)"
  local file="$UOS_MEMORY_DIR/logs/moves/$(date +%Y-%m-%d)-move-$move_id.md"
  echo "- [$now] Move: \`$cmd\` → [$file]" >> "$MOVE_LOG"
  echo "# uOS Move Log" > "$file"
  echo "**Command:** $cmd" >> "$file"
  echo "**Time:** $now" >> "$file"
}

print_help() {
  echo "🧭 Commands:"
  echo "  new [type]       → Create new mission/move/milestone/legacy"
  echo "  log [type]       → Save current draft to archive"
  echo "  redo [type]      → Remove current draft"
  echo "  undo move        → Revert last move (confirm)"
  echo "  run [script]     → Run script from uOS/scripts"
  echo "  dash             → Show dashboard"
  echo "  recent           → Show last 5 session moves"
  echo "  map              → Show current region"
  echo "  mission          → Print current mission"
  echo "  move             → Log manual move"
  echo "  tree             → Show project tree"
  echo "  list             → List visible files"
  echo "  restart          → Restart shell"
  echo "  exit             → Quit"
}

while true; do
  read -rp "🌀 uCode→ " cmd args

  case "$cmd" in
    new)
      type="$args"
      tpl="$UOS_ROOT/templates/${type}-template.md"
      if [ ! -f "$tpl" ]; then log_error "❌ Template missing: $tpl"; echo "❌ Template not found: $tpl"; continue; fi
      ts=$(date +%s)
      out="$UOS_MEMORY_DIR/${type}s/$(date +%Y-%m-%d)-${type}-$ts.md"
      mkdir -p "$(dirname "$out")"
      cp "$tpl" "$out" || { log_error "❌ Failed to copy $tpl"; continue; }
      echo "📄 New $type created: $out"
      ${EDITOR:-nano} "$out" || vi "$out"
      ;;
    log)
      echo "(logging not implemented yet)"
      ;;
    redo)
      echo "(redo not implemented yet)"
      ;;
    undo)
      echo "(undo not implemented yet)"
      ;;
    run)
      script="$SCRIPT_DIR/$args.sh"
      if [ ! -f "$script" ]; then log_error "❌ Script not found: $script"; echo "❌ Script not found: $script"; continue; fi
      bash "$script"
      log_move "run $args.sh"
      ;;
    dash)
      bash "$SCRIPT_DIR/dashboard.sh" || log_error "❌ Failed to run dashboard"
      log_move "dash"
      ;;
    recent)
      tail -n 5 "$MOVE_LOG"
      ;;
    map)
      cat "$UOS_KNOWLEDGE_DIR/map/current_region.txt" 2>/dev/null || echo "❌ No region map"
      ;;
    mission)
      cat "$UOS_MEMORY_DIR/state/current_mission.md" 2>/dev/null || echo "❌ No active mission"
      ;;
    move)
      log_move "manual move"
      echo "📝 Move recorded."
      ;;
    tree)
      bash "$SCRIPT_DIR/ucode-tree.sh"
      ;;
    list)
      ls -1p | grep -v '^\.' || echo "(empty)"
      ;;
    restart)
      echo "🔄 Restarting..."
      exec "$BASH_SOURCE"
      ;;
    help)
      print_help
      ;;
exit)
echo "👋 Exiting uCode CLI. Goodbye, Master."
break
;;

With the following enhanced logic:

exit)
echo "👋 Exiting uCode CLI. Goodbye, Master."

read -rp "🛑 Also shut down Docker container? (y/N): " confirm_shutdown
case "$confirm_shutdown" in
y|Y)
echo "🔌 Running Quit-uOS.command..."
if [ -x "$HOME/uOS/Quit-uOS.command" ]; then
"$HOME/uOS/Quit-uOS.command"
else
echo "⚠️ Quit-uOS.command not found or not executable."
fi
;;
*)
echo "🌀 Docker container will remain running."
;;
esac

break
;;
    *)
      echo "❓ Unknown command: $cmd"
      ;;
  esac
done
