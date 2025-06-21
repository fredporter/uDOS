#!/bin/bash
# uCode CLI v1.4.4 — Unified Input/Output Shell for uOS

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
QUIT_CMD="$UROOT/macos/Quit-uOS.command"

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
  local ts_epoch=$(date +%s)
  local ts_iso=$(date -u +"%Y-%m-%dT%H:%M:%SZ")
  local user=$(whoami)
  local path="$MOVE_DIR/$(date +%Y-%m-%d)-move-$ts_epoch.md"
  local output=""

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
      echo "🧺 Undoing last move not yet implemented."
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
      bash "$UROOT/scripts/dashboard.sh" || echo "❌ Failed to load dashboard."
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
      bash "$UROOT/scripts/ucode-tree.sh"
      log_move "tree"
      ;;
    
    list)
      echo "📂 Current directory: $(pwd)"
      echo "📄 Visible contents:"
      ls -1p | grep -v '^\.' || echo "(empty)"
      ;;
    
    restart)
      echo "🔄 Restarting uCode CLI..."
      exec bash "$BASH_SOURCE"
      ;;
    
    exit)
      echo "👋 Exiting uCode CLI. Goodbye, Master."

      if grep -q docker /proc/1/cgroup 2>/dev/null; then
        echo "🧩 Detected Docker environment — container remains running."
      else
        read -rp "🛑 Also shut down Docker container? (y/N): " confirm_shutdown
        case "$confirm_shutdown" in
          y|Y)
            echo "🔌 Running Quit-uOS.command..."
            if [[ -x "$QUIT_CMD" ]]; then
              "$QUIT_CMD"
            else
              echo "⚠️ Quit-uOS.command not found or not executable at $QUIT_CMD"
              log_error "exit: Quit-uOS.command missing or not executable"
            fi
            ;;
          *)
            echo "🌀 Docker container will remain running."
            ;;
        esac
      fi
      break
      ;;
    
    *)
      echo "❓ Unknown command: $cmd"
      ;;
  esac
done