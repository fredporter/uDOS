#!/bin/bash
# uCode CLI v1.4.5 — Unified Input/Output Shell for uOS

# ──────────────────────────────────────────────
# 📁 Environment and Defaults
# ──────────────────────────────────────────────
UROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
TEMPLATE_DIR="$UROOT/templates"
MEMORY_DIR="${UOS_MEMORY_DIR:-$UROOT/uMemory}"
KNOWLEDGE_DIR="${UOS_KNOWLEDGE_DIR:-$UROOT/uKnowledge}"
LOG_DIR="$MEMORY_DIR/logs"
MOVE_DIR="$LOG_DIR/moves"
SESSION_FILE="$LOG_DIR/session-$(date +%Y-%m-%d).md"
ERROR_LOG="$LOG_DIR/errors/$(date +%Y-%m-%d)-errorlog.md"
DEFAULT_EDITOR="${EDITOR:-nano}"

mkdir -p "$MOVE_DIR" "$LOG_DIR/errors"

# ──────────────────────────────────────────────
# 📌 Startup Header
# ──────────────────────────────────────────────
clear
echo "🌀 uCode CLI started. Type 'help' for available commands."
echo ""
echo "📚 uKnowledge: $KNOWLEDGE_DIR"
echo "🧠 uMemory: $MEMORY_DIR"
echo "📝 Log file: $SESSION_FILE"
echo ""

echo "- Session started at $(date)" >> "$SESSION_FILE"

refresh_uos() {
  echo "♻️ Refreshing uOS environment..."
  bash "$UROOT/scripts/setup-check.sh"
  bash "$UROOT/scripts/dashboard-sync.sh"
  echo "✅ uOS refreshed."
}

# ──────────────────────────────────────────────
# 🧠 Logging Functions
# ──────────────────────────────────────────────

log_error() {
  echo "- [$(date)] ERROR: $1" >> "$ERROR_LOG"
}

log_move() {
  local cmd="$1"
  local ts_epoch ts_iso user path output

  ts_epoch=$(date +%s)
  ts_iso=$(date -u +"%Y-%m-%dT%H:%M:%SZ")
  user=$(whoami)
  path="$MOVE_DIR/$(date +%Y-%m-%d)-move-$ts_epoch.md"
  output=""  # Placeholder for future command output capture

  echo "- [$ts_iso] Move: \`$cmd\` → [$path]" >> "$SESSION_FILE"

  if cp "$TEMPLATE_DIR/move-template.md" "$path" 2>/dev/null; then
    sed -i.bak \
      -e "s/{{timestamp}}/$ts_epoch/g" \
      -e "s/{{iso8601}}/$ts_iso/g" \
      -e "s/{{username}}/$user/g" \
      -e "s/{{command}}/$cmd/g" \
      -e "s/{{output}}/$output/g" \
      "$path"
    rm -f "$path.bak"
    echo "📄 New move created: $path"
  else
    echo -e "Move: $cmd\nTimestamp: $ts_iso\nUser: $user\nCommand: $cmd" > "$path"
    echo "⚠️ No move template found. Using blank file."
    log_error "Missing move template for: $cmd"
  fi
}

# Show dashboard on startup
bash "$UROOT/scripts/dashboard-sync.sh"

# ──────────────────────────────────────────────
# 🚦 Command Dispatcher Loop
# ──────────────────────────────────────────────

while true; do
  read -rp "🌀 uCode→ " cmd args

  case "$cmd" in
    help)
      cat <<EOF
🧭 Commands:
  new [move|mission|milestone|legacy]  → Create new item
  log [type]                          → Save current draft (coming soon)
  redo [type]                         → Remove current draft (coming soon)
  undo move                          → Revert last move (confirm)
  run [script]                       → Run a script from scripts/
  dash                              → Show dashboard
  recent                            → Show last 5 session moves
  map                               → Show current region map
  mission                           → Show current mission
  move                              → Log manual move
  tree                              → Show project tree
  list                              → List visible files
  refresh                           → Refresh uOS environment
  restart                           → Restart CLI
  exit                              → Quit
EOF
      ;;

    new)
      case "$args" in
        move)
          id=$(date +%s)
          path="$MOVE_DIR/$(date +%Y-%m-%d)-move-${id}.md"
          if cp "$TEMPLATE_DIR/move-template.md" "$path" 2>/dev/null; then
            echo "📄 New move created: $path"
            $DEFAULT_EDITOR "$path"
          else
            echo "# Move: manual creation" > "$path"
            echo "⚠️ No move template found. Using blank file: $path"
            log_error "new: move template missing"
            $DEFAULT_EDITOR "$path"
          fi
          ;;
        mission|milestone|legacy)
          path="$MEMORY_DIR/${args}s/$(date +%Y-%m-%d)-${args}.md"
          if cp "$TEMPLATE_DIR/${args}-template.md" "$path" 2>/dev/null; then
            echo "📄 New $args created: $path"
            $DEFAULT_EDITOR "$path"
          else
            echo "# $args created on $(date)" > "$path"
            echo "⚠️ No $args template found. Blank file created."
            log_error "new: missing template for $args"
            $DEFAULT_EDITOR "$path"
          fi
          ;;
        *)
          echo "❌ Usage: new [move|mission|milestone|legacy]"
          ;;
      esac
      ;;

    log)
      echo "📝 Logging for $args is not yet implemented."
      ;;

    redo)
      echo "🧹 Redo logic placeholder for: $args"
      ;;

    undo)
      if [[ "$args" == "move" ]]; then
        last_move=$(ls -1t "$MOVE_DIR"/*.md 2>/dev/null | head -1)
        if [[ -z "$last_move" ]]; then
          echo "⚠️ No moves to undo."
        else
          read -rp "⚠️ Confirm undo last move $(basename "$last_move")? (y/N): " confirm
          if [[ "$confirm" =~ ^[Yy]$ ]]; then
            rm -f "$last_move"
            echo "✅ Last move undone: $(basename "$last_move")"
            echo "- Undo move: $(basename "$last_move")" >> "$SESSION_FILE"
          else
            echo "❌ Undo canceled."
          fi
        fi
      else
        echo "❌ Usage: undo move"
      fi
      ;;

    run)
      script="$UROOT/scripts/$args.sh"
      if [[ -f "$script" ]]; then
        bash "$script"
        log_move "run $args"
      else
        echo "❌ Script not found: $script"
        log_error "run: script not found $script"
      fi
      ;;

    dash)
      bash "$UROOT/scripts/dashboard-sync.sh" || echo "❌ Failed to load dashboard."
      log_move "dash"
      ;;

    recent)
      echo "📜 Recent Moves:"
      tail -n 5 "$SESSION_FILE"
      ;;

    map)
      cat "$KNOWLEDGE_DIR/map/current_region.txt" 2>/dev/null || echo "🗺️ No map loaded."
      ;;

    mission)
      cat "$MEMORY_DIR/state/current_mission.txt" 2>/dev/null || echo "🎯 No mission active."
      ;;

    move)
      log_move "manual move"
      ;;

    tree)
      bash "$UROOT/scripts/ucode-tree.sh"
      log_move "tree"
      ;;

    list)
      echo "📂 Current directory: $(pwd)"
      echo "📄 Visible contents:"
      ls -1p | grep -v '^\.' || echo "(empty)"
      ;;

    refresh)
      refresh_uos
      ;;

    restart)
      echo "🔄 Restarting uCode CLI..."
      exec bash "$BASH_SOURCE"
      ;;

    exit)
      echo "👋 Exiting uCode CLI. Goodbye, Master."

      # Detect Docker container (exit shell cleanly)
      if grep -q docker /proc/1/cgroup 2>/dev/null; then
        echo "🧩 Detected Docker environment — container will exit cleanly."
        break
      fi

      # macOS Terminal GUI auto-close
      if [[ "$OSTYPE" == darwin* ]]; then
        echo "🌀 Closing Terminal window..."
        osascript -e 'tell application "Terminal" to close front window' &>/dev/null
        exit 0
      fi

      exit 0
      ;;

    *)
      echo "❓ Unknown command: $cmd"
      ;;
  esac
done