#!/bin/bash
# uCode CLI v1.4.1 — Unified Command Shell for uOS

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
UOS_ROOT="$HOME/uOS"
UOS_MEMORY="$UOS_ROOT/uMemory"
UOS_KNOWLEDGE="$UOS_ROOT/uKnowledge"
UOS_CONFIG="$UOS_ROOT/config"
TEMPLATES="$UOS_ROOT/templates"

MOVE_LOG_DIR="$UOS_MEMORY/logs/moves"
STATE_PATH="$UOS_MEMORY/state"
SESSION_LOG="$UOS_MEMORY/logs/dashlog-$(date +%F).md"
MOVE_LOG="$MOVE_LOG_DIR/moves.md"

mkdir -p "$MOVE_LOG_DIR" "$STATE_PATH"

touch "$STATE_PATH/current_mission.md"
touch "$STATE_PATH/current_milestone.md"
touch "$STATE_PATH/current_legacy.md"

if [ ! -f "$SESSION_LOG" ]; then
  echo "# 🧭 Dashlog – $(date +%F)" > "$SESSION_LOG"
  echo "- Session started at $(date)" >> "$SESSION_LOG"
fi

log_move() {
  local cmd="$1"
  local output="$2"
  local ts=$(date +"%Y-%m-%d %H:%M:%S")
  local epoch=$(date +%s)
  local move_file="$MOVE_LOG_DIR/$(date +%F)-move-${epoch}.md"

  cat > "$move_file" <<EOF
# Move: $cmd

## 🔖 ID
move_${epoch}

## 📅 Timestamp
$ts

## 📥 Input
$cmd

## 📤 Output
$output

## 🧾 Notes
Auto-logged by uCode CLI
EOF

  echo "- [$ts] Move: \`$cmd\` → [$move_file]" >> "$SESSION_LOG"
  echo "- [$ts] Move: \`$cmd\`" >> "$MOVE_LOG"
}

create_from_template() {
  local type="$1"
  local template="$TEMPLATES/${type}-template.md"
  local filename="$UOS_MEMORY/${type}s/$(date +%F)-${type}-$(date +%s).md"
  mkdir -p "$(dirname "$filename")"
  cp "$template" "$filename"
  cp "$filename" "$STATE_PATH/current_${type}.md"
  echo "📄 New $type created: $filename"
  nano "$filename"
  log_move "new $type" "Created $filename"
}

log_current_item() {
  local type="$1"
  local src="$STATE_PATH/current_${type}.md"
  if [[ -f "$src" ]]; then
    local target="$UOS_MEMORY/${type}s/$(date +%F)-${type}-$(date +%s).md"
    cp "$src" "$target"
    echo "✅ Logged $type to $target"
    log_move "log $type" "$target"
  else
    echo "❌ No current $type to log."
    log_move "log $type" "No current file to log"
  fi
}

redo_item() {
  local type="$1"
  local file="$STATE_PATH/current_${type}.md"
  [[ -f "$file" ]] && rm "$file" && echo "🗑️ Removed current $type." || echo "No active $type."
  log_move "redo $type" "Removed current $type"
}

undo_move() {
  local last_file
  last_file=$(ls -1t "$MOVE_LOG_DIR"/20*-move-*.md 2>/dev/null | head -n 1)
  if [[ -f "$last_file" ]]; then
    echo "🕓 Last Move File:"
    echo "$last_file"
    cat "$last_file"
    read -p "↩️ Undo this move? (y/N): " confirm
    if [[ "$confirm" =~ ^[Yy]$ ]]; then
      rm "$last_file"
      echo "✅ Move undone."
      log_move "undo move" "Removed $last_file"
    else
      echo "❎ Move kept."
    fi
  else
    echo "❌ No move file found to undo."
  fi
}

run_script() {
  local name="$1"
  [[ "$name" != *.sh ]] && name="${name}.sh"
  local script="$UOS_ROOT/scripts/$name"
  if [[ -x "$script" ]]; then
    out=$(bash "$script")
    echo "$out"
    log_move "run $name" "$out"
  else
    echo "❌ Script not found: $script"
    log_move "run $name" "Script not found"
  fi
}

show_dashboard() {
  if [[ -x "$SCRIPT_DIR/dashboard.sh" ]]; then
    out=$(bash "$SCRIPT_DIR/dashboard.sh")
    echo "$out"
    log_move "dash" "$out"
  else
    echo "⚠️ dashboard.sh not found."
  fi
}

# — MINI DASHLOAD —
clear
echo "🌀 uCode v1.4.1 ready – Type 'help' for commands"
echo "📚 Knowledge: $UOS_KNOWLEDGE"
echo "🧠 Memory: $UOS_MEMORY"
echo "📝 Session log: $SESSION_LOG"
echo ""

# === CLI LOOP ===
while true; do
  read -rp "🌀 uCode→ " cmd

  case "$cmd" in
    help)
      cat <<EOF
🧭 Commands:
  new [type]       → Create new mission/move/milestone/legacy
  log [type]       → Save current draft to archive
  redo [type]      → Remove current draft
  undo move        → Revert last move (confirm)
  run [script]     → Run script from uOS/scripts
  dash             → Show dashboard
  recent           → Show last 5 session moves
  map              → Show current region
  mission          → Print current mission
  move             → Log manual move
  tree             → Show project tree
  list             → List visible files
  restart          → Restart shell
  exit             → Quit
EOF
      ;;
    dash) show_dashboard ;;
    list) out=$(ls -1p | grep -v '^\.' || echo "(empty)"); echo "$out"; log_move "list" "$out" ;;
    tree) out=$(bash "$SCRIPT_DIR/ucode-tree.sh"); echo "$out"; log_move "tree" "$out" ;;
    map) file="$UOS_KNOWLEDGE/map/current_region.txt"; out=$(cat "$file" 2>/dev/null || echo "No map loaded."); echo "$out"; log_move "map" "$out" ;;
    mission) file="$STATE_PATH/current_mission.md"; out=$(cat "$file" 2>/dev/null || echo "No mission active."); echo "$out"; log_move "mission" "$out" ;;
    recent) out=$(tail -n 5 "$SESSION_LOG"); echo "$out"; log_move "recent" "$out" ;;
    restart) log_move "restart" "restarting"; exec "$BASH_SOURCE" ;;
    exit) echo "👋 Goodbye, Master."; log_move "exit" "CLI closed"; break ;;
    undo\ move) undo_move ;;
    new\ *) create_from_template "${cmd#new }" ;;
    log\ *) log_current_item "${cmd#log }" ;;
    redo\ *) redo_item "${cmd#redo }" ;;
    run\ *) run_script "${cmd#run }" ;;
    move) echo "🔧 Manual move recorded."; log_move "manual move" "manual input" ;;
    *) echo "❓ Unknown command: $cmd"; log_move "$cmd" "Unknown command" ;;
  esac
done
