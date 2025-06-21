#!/bin/bash
# uCode CLI v1.4 — Unified Input/Output Logger for uOS

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
UOS_MEMORY_DIR="${UOS_MEMORY_DIR:-/uMemory}"
UOS_KNOWLEDGE_DIR="${UOS_KNOWLEDGE_DIR:-/uKnowledge}"
UOS_CONFIG_DIR="${UOS_CONFIG_DIR:-/config}"
MOVE_LOG_DIR="$UOS_MEMORY_DIR/logs/moves"
SESSION_LOG="$UOS_MEMORY_DIR/logs/dashlog-$(date +%F).md"

mkdir -p "$MOVE_LOG_DIR"
mkdir -p "$UOS_MEMORY_DIR/state"

touch "$UOS_MEMORY_DIR/state/current_mission.txt"
touch "$UOS_MEMORY_DIR/state/current_milestone.txt"
touch "$UOS_MEMORY_DIR/state/current_legacy.txt"

if [ ! -f "$SESSION_LOG" ]; then
  echo "# 🧭 Dashlog – $(date +%F)" > "$SESSION_LOG"
  echo "- Session started at $(date)" >> "$SESSION_LOG"
fi

log_move() {
  local cmd="$1"
  local output="$2"
  local ts
  ts=$(date +"%Y-%m-%d %H:%M:%S")
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
Auto-logged by uOS CLI
EOF

  echo "- [$ts] Move: \`$cmd\` → [$move_file]" >> "$SESSION_LOG"
}

clear
echo "🌀 uCode CLI v1.4 – Welcome back, Master."
echo "📅 Session: $(date +%F)"
echo "📚 Knowledge: $UOS_KNOWLEDGE_DIR"
echo "🧠 Memory: $UOS_MEMORY_DIR"
echo ""

while true; do
  read -rp "uCode > " cmd

  case "$cmd" in
    dash)
      out=$(bash "$SCRIPT_DIR/dashboard.sh")
      echo "$out"
      log_move "dash" "$out"
      ;;
    list)
      out=$(ls -1p | grep -v '^\.' || echo "(empty)")
      echo "$out"
      log_move "list" "$out"
      ;;
    tree)
      out=$(bash "$SCRIPT_DIR/ucode-tree.sh")
      log_move "tree" "$out"
      ;;
    map)
      file="$UOS_KNOWLEDGE_DIR/map/current_region.txt"
      out=$(cat "$file" 2>/dev/null || echo "No map loaded.")
      echo "$out"
      log_move "map" "$out"
      ;;
    mission)
      file="$UOS_MEMORY_DIR/state/current_mission.txt"
      out=$(cat "$file" 2>/dev/null || echo "No mission active.")
      echo "$out"
      log_move "mission" "$out"
      ;;
    recent)
      out=$(tail -n 5 "$SESSION_LOG")
      echo "$out"
      log_move "recent" "$out"
      ;;
    restart)
      echo "🔄 Restarting uCode..."
      log_move "restart" "Restart triggered"
      exec "$BASH_SOURCE"
      ;;
    exit)
      echo "👋 Goodbye, Master."
      log_move "exit" "uCode exited"
      break
      ;;
    help)
      cat <<EOF
🧭 Available Commands:
  dash       → View dashboard
  map        → Show map region
  mission    → View current mission
  tree       → View project tree
  list       → List current folder
  recent     → Show last 5 moves
  restart    → Reload this shell
  exit       → Quit uCode
EOF
      ;;
    *)
      echo "❓ Unknown command: $cmd"
      log_move "$cmd" "Unknown command"
      ;;
  esac
done
