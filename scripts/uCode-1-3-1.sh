#!/bin/bash
# uCode CLI v1.3.1 — Unified Command Shell for uOS
# Supports: new, log, run, redo, undo, dash, recent, map, mission, move, tree, list, restart, exit

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
UOS_ROOT="$HOME/uOS"
UOS_MEMORY="$UOS_ROOT/uMemory"
UOS_KNOWLEDGE="$UOS_ROOT/uKnowledge"
TEMPLATES="$UOS_ROOT/templates"
LOG_PATH="$UOS_MEMORY/logs/moves"
STATE_PATH="$UOS_MEMORY/state"
MOVE_LOG="$LOG_PATH/moves.md"

mkdir -p "$LOG_PATH" "$STATE_PATH"

log_move() {
  local cmd="$1"
  local ts
  ts=$(date +"%Y-%m-%d %H:%M:%S")
  echo "- [$ts] Move: \`$cmd\`" >> "$MOVE_LOG"
}

create_from_template() {
  local type="$1"
  local template="$TEMPLATES/${type}-template.md"
  local filename="$UOS_MEMORY/${type}s/$(date +%Y-%m-%d)-${type}-$(date +%s).md"
  mkdir -p "$(dirname "$filename")"
  cp "$template" "$filename"
  cp "$filename" "$STATE_PATH/current_${type}.md"
  echo "📄 New $type created: $filename"
  nano "$filename"
  log_move "new $type"
}

log_current_item() {
  local type="$1"
  local src="$STATE_PATH/current_${type}.md"
  if [[ -f "$src" ]]; then
    local target="$UOS_MEMORY/${type}s/$(date +%Y-%m-%d)-${type}-$(date +%s).md"
    cp "$src" "$target"
    echo "✅ Logged $type as $target"
    log_move "log $type"
  else
    echo "❌ No current $type to log."
  fi
}

redo_item() {
  local type="$1"
  local file="$STATE_PATH/current_${type}.md"
  [[ -f "$file" ]] && rm "$file" && echo "🗑️ Removed current $type." || echo "No active $type."
  log_move "redo $type"
}

undo_move() {
  local last_file
  last_file=$(ls -1t "$LOG_PATH"/20*-move-*.md 2>/dev/null | head -n 1)
  if [[ -f "$last_file" ]]; then
    echo "🕓 Last Move:"
    cat "$last_file"
    read -p "↩️ Undo this move? (y/N): " confirm
    [[ "$confirm" =~ ^[Yy]$ ]] && rm "$last_file" && echo "✅ Move undone." || echo "❎ Move kept."
  else
    echo "❌ No move found to undo."
  fi
}

run_script() {
  local name="$1"
  [[ "$name" != *.sh ]] && name="${name}.sh"
  local script="$UOS_ROOT/scripts/$name"
  if [[ -x "$script" ]]; then
    bash "$script"
    log_move "run $name"
  else
    echo "❌ Script not found: $script"
  fi
}

show_dashboard() {
  [[ -x "$SCRIPT_DIR/dashboard.sh" ]] && bash "$SCRIPT_DIR/dashboard.sh" || echo "⚠️ dashboard.sh not found or not executable."
  log_move "dash"
}

# Mini dash on load
clear
# Print startup status
clear
echo "🌀 uCode→ loaded. Type 'help' for available commands."
echo ""
echo "📚 uKnowledge mounted at: $UOS_KNOWLEDGE_DIR"
echo "🧠 uMemory mounted at: $UOS_MEMORY_DIR"
echo "📝 Move log path: $MOVE_LOG"
echo "🔧 Config directory: $UOS_CONFIG_DIR"
echo ""
echo "╔═══════════════════════════[ uOS STATUS DASHBOARD ]═══════════════════════════╗"
echo "║ User: Master                           $(date '+%Y-%m-%d %H:%M:%S')                ║"
echo "║ Location: The Crypt                                                           ║"
echo "║ Active Mission: Activate uCode Interface                                      ║"
echo "╚═══════════════════════════════════════════════════════════════════════════════╝"
echo ""

# === MAIN LOOP ===
while true; do
  read -rp "🌀 uCode→ " cmd

  case "$cmd" in
    help)
      echo "🧭 Commands:"
      echo "  new [object]     → Create new mission/move/etc."
      echo "  log [object]     → Save current draft to archive"
      echo "  redo [object]    → Remove current draft"
      echo "  undo move        → Revert last move (with confirm)"
      echo "  run [script]     → Run containerized script"
      echo "  dash             → View dashboard"
      echo "  recent           → Show last 10 moves"
      echo "  map              → Show current region"
      echo "  mission          → View current mission"
      echo "  move             → Log manual move"
      echo "  tree             → Show file structure"
      echo "  list             → Show visible files"
      echo "  restart          → Restart this shell"
      echo "  exit             → Quit uCode"
      ;;
    dash)
      show_dashboard
      ;;
    recent)
      tail -n 10 "$MOVE_LOG" || echo "No recent moves."
      log_move "recent"
      ;;
    map)
      cat "$UOS_KNOWLEDGE/map/current_region.txt" 2>/dev/null || echo "No map loaded."
      log_move "map"
      ;;
    mission)
      cat "$UOS_MEMORY/state/current_mission.md" 2>/dev/null || echo "No mission active."
      log_move "mission"
      ;;
    move)
      echo "🔧 Manual move recorded at $(date)" >> "$MOVE_LOG"
      log_move "manual move"
      ;;
    tree)
      bash "$SCRIPT_DIR/ucode-tree.sh" 2>/dev/null || echo "Missing ucode-tree.sh"
      log_move "tree"
      ;;
    list)
      echo "📂 Directory: $(pwd)"
      ls -1p | grep -v '^\.' || echo "(empty)"
      log_move "list"
      ;;
    restart)
      log_move "restart"
      exec "$BASH_SOURCE"
      ;;
    exit)
      echo "👋 Exiting uCode. Goodbye, Master."
      break
      ;;
    undo\ move)
      undo_move
      ;;
    new\ *)
      create_from_template "${cmd#new }"
      ;;
    log\ *)
      log_current_item "${cmd#log }"
      ;;
    redo\ *)
      redo_item "${cmd#redo }"
      ;;
    run\ *)
      run_script "${cmd#run }"
      ;;
    *)
      echo "❓ Unknown command: $cmd"
      # Optional suggestion logic omitted for brevity
      ;;
  esac
done
