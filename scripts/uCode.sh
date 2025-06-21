```bash
#!/bin/bash
# uCode CLI v1.4.2 — Unified Input/Output Shell for uOS

# ──────────────────────────────────────────────
# 📁 Environment and Defaults
# ──────────────────────────────────────────────
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
UOS_ROOT="${SCRIPT_DIR%/*}"
TEMPLATE_DIR="$UOS_ROOT/templates"
MEMORY_DIR="${UOS_MEMORY_DIR:-$UOS_ROOT/uMemory}"
KNOWLEDGE_DIR="${UOS_KNOWLEDGE_DIR:-$UOS_ROOT/uKnowledge}"
LOG_DIR="$MEMORY_DIR/logs"
MOVE_DIR="$LOG_DIR/moves"
SESSION_FILE="$LOG_DIR/session-$(date +%Y-%m-%d).md"
DEFAULT_EDITOR="${EDITOR:-nano}"
ERROR_LOG="$LOG_DIR/errors/$(date +%Y-%m-%d)-errorlog.md"

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

# ──────────────────────────────────────────────
# 🧠 Logging Functions
# ──────────────────────────────────────────────

log_move() {
  local cmd="$1"
  local ts
  ts=$(date +"%Y-%m-%d %H:%M:%S")
  local id="move-$(date +%s)"
  local path="$MOVE_DIR/$(date +%Y-%m-%d)-$id.md"
  echo "- [$ts] Move: \`$cmd\` → [$path]" >> "$SESSION_FILE"

  cp "$TEMPLATE_DIR/move-template.md" "$path" 2>/dev/null || echo "# Move: $cmd" > "$path"
  sed -i '' "s/{{command}}/$cmd/" "$path" 2>/dev/null
  sed -i '' "s/{{timestamp}}/$(date +%s)/" "$path" 2>/dev/null
  echo "📄 New move created: $path"
}

log_error() {
  echo "- [$(date)] ERROR: $1" >> "$ERROR_LOG"
}

# ──────────────────────────────────────────────
# 🚦 Command Dispatcher
# ──────────────────────────────────────────────

while true; do
  read -rp "🌀 uCode→ " cmd args

  case "$cmd" in
    help)
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
      ;;
    new)
      case "$args" in
        move)
          id=$(date +%s)
          path="$MOVE_DIR/$(date +%Y-%m-%d)-move-${id}.md"
          if cp "$TEMPLATE_DIR/move-template.md" "$path" 2>/dev/null; then
            echo "📄 New move created: $path"
            ${EDITOR:-nano} "$path"
          else
            echo "❌ Template not found."
            log_error "Failed to create move: template missing"
          fi
          ;;
        mission|milestone|legacy)
          path="$MEMORY_DIR/${args}s/$(date +%Y-%m-%d)-${args}.md"
          cp "$TEMPLATE_DIR/${args}-template.md" "$path" 2>/dev/null || touch "$path"
          ${EDITOR:-nano} "$path"
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
      echo "🧺 Undoing last move not yet implemented."
      ;;
    run)
      script="$UOS_ROOT/scripts/$args.sh"
      if [ -f "$script" ]; then
        bash "$script"
        log_move "run $args"
      else
        echo "❌ Script not found: $script"
        log_error "run: script not found $script"
      fi
      ;;
    dash)
      bash "$UOS_ROOT/scripts/dashboard.sh" || echo "❌ Failed to load dashboard."
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
      cat "$MEMORY_DIR/state/current_mission.md" 2>/dev/null || echo "🎯 No mission active."
      ;;
    move)
      log_move "manual move"
      ;;
    tree)
      bash "$UOS_ROOT/scripts/ucode-tree.sh"
      log_move "tree"
      ;;
    list)
      echo "📂 Current directory: $(pwd)"
      echo "📄 Visible contents:"
      ls -1p | grep -v '^\.' || echo "(empty)"
      ;;
    restart)
      echo "🔄 Restarting uCode CLI..."
      exec "$BASH_SOURCE"
      ;;
    exit)
      echo "👋 Exiting uCode CLI. Goodbye, Master."

      read -rp "🛑 Also shut down Docker container? (y/N): " confirm_shutdown
      case "$confirm_shutdown" in
        y|Y)
          echo "🔌 Running Quit-uOS.command..."
          if [ -x "$HOME/uOS/Quit-uOS.command" ]; then
            "$HOME/uOS/Quit-uOS.command"
          else
            echo "⚠️ Quit-uOS.command not found or not executable at $HOME/uOS/Quit-uOS.command"
            log_error "exit: Quit-uOS.command missing or not executable"
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

```