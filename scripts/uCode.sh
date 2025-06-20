#!/bin/bash
# uCode CLI v1.3 — Action-Based Shell for uOS
# Supports: new, run, log, redo, undo + dash, recent

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
UOS_ROOT="$HOME/uOS"
UOS_MEMORY="$UOS_ROOT/uMemory"
UOS_KNOWLEDGE="$UOS_ROOT/uKnowledge"
TEMPLATES="$UOS_ROOT/templates"
LOG_PATH="$UOS_MEMORY/logs/moves"
STATE_PATH="$UOS_MEMORY/state"

mkdir -p "$LOG_PATH" "$STATE_PATH"

log_move() {
  local cmd="$1"
  local ts
  ts=$(date +"%Y-%m-%d %H:%M:%S")
  echo "- [$ts] Move: \`$cmd\`" >> "$LOG_PATH/moves.md"
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

run_script() {
  local name="$1"
  local script="$UOS_ROOT/scripts/${name}.sh"
  if [[ -x "$script" ]]; then
    bash "$script"
    log_move "run $name"
  else
    echo "❌ Script not found: $script"
  fi
}

log_current_item() {
  local type="$1"
  local src="$STATE_PATH/current_${type}.md"
  if [[ -f "$src" ]]; then
    echo "📥 Logging current $type..."
    local target="$UOS_MEMORY/${type}s/$(date +%Y-%m-%d)-${type}-$(date +%s).md"
    cp "$src" "$target"
    echo "✅ Saved as $target"
    log_move "log $type"
  else
    echo "❌ No current $type to log."
  fi
}

redo_item() {
  local type="$1"
  local current="$STATE_PATH/current_${type}.md"
  [[ -f "$current" ]] && rm "$current" && echo "🗑️ Removed current $type." || echo "No active $type."
  log_move "redo $type"
}

undo_move() {
  local last_file
  last_file=$(ls -1t "$LOG_PATH"/20*-move-*.md 2>/dev/null | head -n 1)
  if [[ -f "$last_file" ]]; then
    echo "🕓 Last Move:"
    cat "$last_file"
    read -p "↩️ Undo this move? (y/N): " confirm
    if [[ "$confirm" =~ ^[Yy]$ ]]; then
      rm "$last_file"
      echo "✅ Move undone."
    else
      echo "❎ Move kept."
    fi
  else
    echo "❌ No move found to undo."
  fi
}

show_recent_moves() {
  echo "📜 Recent Moves:"
  tail -n 10 "$LOG_PATH/moves.md" 2>/dev/null || echo "No moves yet."
}

show_dashboard() {
  bash "$SCRIPT_DIR/dashboard.sh"
  log_move "dash"
}

# === MAIN LOOP ===
clear
echo "🌿 Welcome to uCode v1.3 — Type 'help' for options."

while true; do
  read -rp "uCode > " cmd

  case "$cmd" in
    help)
      echo "🧭 Commands:"
      echo "  new [object]     → Create new mission/move/etc."
      echo "  run [script]     → Run containerized script"
      echo "  log [object]     → Commit current draft"
      echo "  redo [object]    → Discard current draft"
      echo "  undo move        → Delete last move"
      echo "  dash             → View dashboard"
      echo "  recent           → Show last moves"
      echo "  exit             → Quit uCode"
      ;;
    dash)
      show_dashboard
      ;;
    recent)
      show_recent_moves
      ;;
    undo\ move)
      undo_move
      ;;
    exit)
      echo "👋 Exiting uCode. Goodbye, Master."
      break
      ;;
    new\ *)
      obj="${cmd#new }"
      create_from_template "$obj"
      ;;
    run\ *)
      script="${cmd#run }"
      run_script "$script"
      ;;
    log\ *)
      obj="${cmd#log }"
      log_current_item "$obj"
      ;;
    redo\ *)
      obj="${cmd#redo }"
      redo_item "$obj"
      ;;
    *)
      echo "❓ Unknown command: $cmd"
      ;;
  esac
done
