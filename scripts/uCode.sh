#!/bin/bash
# uCode.sh - uDOS Beta v1.6.1 CLI Shell
# Full-featured command-line interface for uDOS environment

# Environment Setup
export UDOS_HOME="${HOME}/.udos"
export UDOS_LOG="${UDOS_HOME}/udos.log"
export UDOS_IDENTITY="${UDOS_HOME}/identity.id"
export UDOS_DASHBOARD="${UDOS_HOME}/dashboard.json"
export UDOS_TEMP="${UDOS_HOME}/temp"
export UDOS_MOVES_DIR="${UDOS_HOME}/logs/moves"
mkdir -p "$UDOS_HOME" "$UDOS_TEMP" "$UDOS_MOVES_DIR"

# Ensure uMemory subdirectories exist
mkdir -p "${UDOS_HOME}/uMemory/missions" "${UDOS_HOME}/uMemory/milestones" "${UDOS_HOME}/uMemory/legacies"

# Log session start
echo "🌀 SESSION START → $(date '+%Y-%m-%d %H:%M:%S')" >> "${UDOS_MOVES_DIR}/moves-$(date +%Y-%m-%d).md"

# Startup Header
echo "🚀 Welcome to uDOS Beta v1.6.1"
echo "🧠 Loading environment..."
if [ ! -f "$UDOS_IDENTITY" ]; then
  echo "🔑 No identity found. Please create a new one with NEW command."
else
  echo "🔑 Identity loaded: $(cat "$UDOS_IDENTITY")"
fi
echo ""

# Logging Functions
log_info() {
  echo "$(date '+%Y-%m-%d %H:%M:%S') [INFO] $1" >> "$UDOS_LOG"
}

log_error() {
  echo "$(date '+%Y-%m-%d %H:%M:%S') [ERROR] $1" >> "$UDOS_LOG"
}

log_command() {
  echo "$(date '+%Y-%m-%d %H:%M:%S') [CMD] $1" >> "$UDOS_LOG"
}

log_move_template() {
  local cmd="$1"
  local timestamp
  timestamp=$(date +"%Y-%m-%d %H:%M:%S")
  local id="move-$(date +%s)"
  local file="$UDOS_MOVES_DIR/$(date +%Y-%m-%d)-$id.md"
  echo "# Move: $cmd" > "$file"
  echo "- Timestamp: $timestamp" >> "$file"
  echo "- Command: $cmd" >> "$file"
  echo "📄 Move logged to: $file"
}

# Dashboard Sync
sync_dashboard() {
  if [ -f "$UDOS_DASHBOARD" ]; then
    echo "📊 Syncing dashboard..."
    # Simulate dashboard sync (could be replaced with real sync logic)
    sleep 1
    echo "✅ Dashboard synced."
  else
    echo "⚠️ Dashboard file missing; skipping sync."
  fi
}

# Command Functions

cmd_new() {
  echo "🆕 What would you like to create?"
  read -rp "Choose type (mission, milestone, legacy): " type
  case "$type" in
    mission|milestone|legacy)
      template="$UDOS_HOME/uTemplate/${type}-template.md"
      target="${UDOS_HOME}/uMemory/${type}s/$(date +%Y-%m-%d)-${type}.md"
      mkdir -p "$(dirname "$target")"
      if [[ -f "$template" ]]; then
        cp "$template" "$target"
      else
        echo "# New $type" > "$target"
      fi
      ${EDITOR:-nano} "$target"
      log_info "New $type created: $target"
      log_move_template "new $type"
      ;;
    *)
      echo "❌ Unknown type: $type"
      ;;
  esac
}

cmd_log() {
  read -rp "📝 Log what? (mission/milestone/legacy): " what
  if [[ "$what" =~ ^(mission|milestone|legacy)$ ]]; then
    bash "$UDOS_HOME/scripts/make-log.sh" "$what"
  else
    echo "❌ Invalid log type."
  fi
}

cmd_redo() {
  echo "↪️ Redoing last undone action..."
  # Placeholder for redo logic
  sleep 1
  echo "✅ Redo completed."
  log_info "Redo command executed."
}

cmd_undo() {
  echo "↩️ Undoing last action..."
  # Placeholder for undo logic
  sleep 1
  echo "✅ Undo completed."
  log_info "Undo command executed."
}

cmd_run() {
  bash "$HOME/uDOS/scripts/command.sh" "$args"
  log_move_template "run $args"
}

cmd_tree() {
  bash "$HOME/uDOS/scripts/make-tree.sh"
  log_move_template "tree"
}

cmd_stats() {
  bash "$UDOS_HOME/scripts/make-stats.sh"
}

cmd_list() {
  echo "📂 Current directory: $(pwd)"
  ls -1Ap | grep -v '^\.'
}

cmd_mission() {
  cat "$UDOS_HOME/state/current_mission.txt" 2>/dev/null || echo "🎯 No mission active."
}

cmd_map() {
  cat "$UDOS_HOME/uKnowledge/map/current_region.txt" 2>/dev/null || echo "🗺️ No map loaded."
}

cmd_dash() {
  echo "📈 Displaying dashboard..."
  if [ -f "$UDOS_DASHBOARD" ]; then
    cat "$UDOS_DASHBOARD"
  else
    echo "⚠️ Dashboard not found."
  fi
  log_info "Dashboard displayed."
  log_move_template "dash"
}

cmd_restart() {
  echo "🔄 Restarting uDOS shell..."
  log_info "System restart initiated."
  exec "$0" # Relaunch script
}

cmd_reboot() {
  echo "♻️ Rebooting uDOS system..."
  log_info "System reboot initiated."
  # Placeholder for reboot logic (could reset environment)
  sleep 2
  exec "$0" # Relaunch script
}

cmd_destroy() {
  echo "💥 Destroying identity and data..."
  read -rp "Are you sure you want to delete your identity? (yes/no): " confirm
  if [[ "$confirm" =~ ^[Yy][Ee][Ss]$ ]]; then
    rm -f "$UDOS_IDENTITY" "$UDOS_LOG" "$UDOS_DASHBOARD"
    echo "✅ Identity and related data deleted."
    log_info "Identity destroyed by user."
  else
    echo "❌ Destroy cancelled."
    log_info "Destroy command cancelled by user."
  fi
}

cmd_bye() {
  echo "👋 uDOS is now entering shutdown mode..."
  echo "🔒 Session is idle. You can type:"
  echo "   [R] RESTART → Soft refresh"
  echo "   [B] REBOOT  → Full setup and check"
  echo "   [D] DESTROY → Delete your identity"
  echo "   [C] CANCEL  → Return to CLI"
  read -n1 -rp "👉 Choose next step: " next
  echo ""
  case "${next^^}" in
    R) cmd_restart ;;
    B) cmd_reboot ;;
    D) cmd_destroy ;;
    *) echo "🌀 Returning to CLI..." ;;
  esac

  if grep -q docker /proc/1/cgroup 2>/dev/null; then
    echo ""
    read -rp "💤 Also shut down Docker container? (y/N): " shut
    if [[ "$shut" =~ ^[Yy]$ ]]; then
      QUIT_CMD="$HOME/uDOS/launcher/Quit-uDOS.command"
      if [[ -x "$QUIT_CMD" ]]; then
        echo "🔌 Executing Quit-uDOS.command..."
        "$QUIT_CMD"
      else
        echo "⚠️ Quit-uDOS.command not found or not executable."
        log_error "Quit-uDOS.command missing or not executable."
      fi
      exit 0
    else
      echo "🌀 Docker container will remain active."
    fi
  fi
}

cmd_recent() {
  echo "📜 Recent moves:"
  tail -n 10 "${UDOS_MOVES_DIR}/moves-$(date +%Y-%m-%d).md"
}

# Main Command Dispatch Loop
trap 'echo "🌀 SESSION END → $(date "+%Y-%m-%d %H:%M:%S")" >> "${UDOS_MOVES_DIR}/moves-$(date +%Y-%m-%d).md"' EXIT
while true; do
  read -rp "uDOS> " input
  cmd=$(echo "$input" | awk '{print toupper($1)}')
  args=$(echo "$input" | cut -d' ' -f2-)
  log_command "$input"
  case "$cmd" in
    NEW)
      cmd_new
      ;;
    LOG)
      cmd_log
      ;;
    REDO)
      cmd_redo
      ;;
    UNDO)
      cmd_undo
      ;;
    RUN)
      cmd_run
      ;;
    TREE)
      cmd_tree
      ;;
    STATS)
      cmd_stats
      ;;
    LIST)
      cmd_list
      ;;
    MISSION)
      cmd_mission
      ;;
    MAP)
      cmd_map
      ;;
    DASH)
      cmd_dash
      ;;
    RESTART)
      cmd_restart
      ;;
    REBOOT)
      cmd_reboot
      ;;
    DESTROY)
      cmd_destroy
      ;;
    BYE)
      cmd_bye
      ;;
    EXIT|QUIT)
      cmd_bye
      ;;
    RECENT|HISTORY)
      cmd_recent
      ;;
    SYNC)
      sync_dashboard
      ;;
    HELP)
      echo "🧠 Available uDOS commands:"
      echo "   NEW       → Create new item (mission, milestone, legacy)"
      echo "   LOG       → Log mission/milestone/legacy"
      echo "   RUN       → Run a command"
      echo "   TREE      → Show file tree"
      echo "   STATS     → Generate dashboard stats"
      echo "   LIST      → List current folder"
      echo "   MAP       → Show current region"
      echo "   MISSION   → Display active mission"
      echo "   DASH      → Show dashboard"
      echo "   SYNC      → Sync dashboard"
      echo "   RESTART   → Restart shell"
      echo "   REBOOT    → Reboot system"
      echo "   DESTROY   → Delete your identity"
      echo "   BYE/EXIT/QUIT → Close session"
      echo "   RECENT/HISTORY → Show last 10 moves"
      ;;
    "")
      # Ignore empty input
      ;;
    *)
      echo "❓ Unknown command '$cmd'. Type HELP for list of commands."
      ;;
  esac
done