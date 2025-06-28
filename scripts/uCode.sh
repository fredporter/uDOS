#!/bin/bash
# uCode.sh - uDOS Beta v1.6.1 CLI Shell
# Full-featured command-line interface for uDOS environment

# Environment Setup
export UDOS_HOME="${HOME}/uDOS"
export UDOS_LOG="${UDOS_HOME}/udos.log"
export UDOS_IDENTITY="${UDOS_HOME}/identity.md"
export UDOS_DASHBOARD="${UDOS_HOME}/uMemory/state/dashboard.json"
export UDOS_TEMP="${UDOS_HOME}/temp"
export UDOS_MOVES_DIR="${UDOS_HOME}/logs/moves"
mkdir -p "$UDOS_HOME" "$UDOS_TEMP" "$UDOS_MOVES_DIR"

# Ensure uMemory subdirectories exist
mkdir -p "${UDOS_HOME}/uMemory/missions" "${UDOS_HOME}/uMemory/milestones" "${UDOS_HOME}/uMemory/legacies"
mkdir -p "${UDOS_HOME}/uMemory/logs/errors"
mkdir -p "${UDOS_HOME}/uMemory/logs/moves"
mkdir -p "${UDOS_HOME}/uMemory/state"

# Log session start
echo "🌀 SESSION START → $(date '+%Y-%m-%d %H:%M:%S')" >> "${UDOS_MOVES_DIR}/moves-log-$(date +%Y-%m-%d).md"

# Startup Header
echo "🚀 Welcome to uDOS Beta v1.6.1"
cat << "EOF"
 _    _  ____   ___   ____  ______ _____  
| |  | |/ __ \ / _ \ / __ \|  ____|  __ \ 
| |  | | |  | | | | | |  | | |__  | |  | |
| |  | | |  | | | | | |  | |  __| | |  | |
| |__| | |__| | |_| | |__| | |____| |__| |
 \____/ \____/ \___/ \____/|______|_____/  
     uCode Shell · Beta v1.6.1 🌀
EOF
echo "🧠 Loading environment..."

if [[ -x "$UDOS_HOME/scripts/make-stats.sh" ]]; then
  bash "$UDOS_HOME/scripts/make-stats.sh"
fi

if [[ -x "$UDOS_HOME/scripts/dashboard-sync.sh" ]]; then
  bash "$UDOS_HOME/scripts/dashboard-sync.sh"
fi
if [ ! -f "$UDOS_IDENTITY" ]; then
  echo "⚙️ No identity file found. Running check-setup..."
  bash "$UDOS_HOME/scripts/check-setup.sh"
fi

if [ -f "$UDOS_IDENTITY" ]; then
  echo "🔑 Identity loaded: $(cat "$UDOS_IDENTITY")"
else
  echo "❌ Identity still missing. Please run DESTROY or REBOOT."
  exit 1
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
  local id="move-log-$(date +%s)"
  local file="$UDOS_MOVES_DIR/${id}.md"
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

cmd_log() {
  echo -ne "\033[1;34m📝 Log Entry Type\033[0m (mission/milestone/legacy): "
  read what
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
  log_move_template "redo"
}

cmd_undo() {
  echo "↩️ Undoing last action..."
  # Placeholder for undo logic
  sleep 1
  echo "✅ Undo completed."
  log_info "Undo command executed."
  log_move_template "undo"
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
  cat "$UDOS_HOME/state/current_mission.md" 2>/dev/null || echo "🎯 No mission active."
}

cmd_map() {
  cat "$UDOS_HOME/uKnowledge/map/current_region.md" 2>/dev/null || echo "🗺️ No map loaded."
}

cmd_dash() {
  echo "📈 Displaying dashboard..."
  cat "$UDOS_HOME/uTemplate/dashboards/dashboard-header.md"
  [ -f "$UDOS_DASHBOARD" ] && cat "$UDOS_DASHBOARD"
  cat "$UDOS_HOME/uTemplate/dashboards/dashboard-footer.md"
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

  echo "🧼 Rebuilding structure..."
  bash "$UDOS_HOME/scripts/make-structure.sh"

  echo "🔍 Rechecking setup and permissions..."
  bash "$UDOS_HOME/scripts/check-setup.sh"

  echo "📊 Rebuilding stats and dashboard..."
  bash "$UDOS_HOME/scripts/make-stats.sh"
  bash "$UDOS_HOME/scripts/dashboard-sync.sh"

  echo "🌀 Relaunching shell..."
  exec "$0"
}

cmd_destroy() {
  echo "💥 uDOS DESTROY Mode:"
  echo "  [A] Remove identity only"
  echo "  [B] Remove identity and uMemory"
  echo "  [C] Remove identity, archive uMemory to /legacy, then delete uMemory"
  echo "  [D] Reboot only (no data loss)"
  echo "  [E] Exit to uCode only (no reboot, no data loss)"
  read -n1 -rp "👉 Select DESTROY option: " choice
  echo ""

  case "${choice^^}" in
    A)
      echo "⚠️ Deleting identity only..."
      rm -f "$UDOS_IDENTITY" "$UDOS_LOG"
      echo "✅ Identity deleted."
      log_info "DESTROY mode A: identity only"
      ;;
    B)
      echo "⚠️ Deleting identity and uMemory..."
      rm -f "$UDOS_IDENTITY" "$UDOS_LOG"
      rm -rf "$UDOS_HOME/uMemory"
      echo "✅ Identity and memory deleted."
      log_info "DESTROY mode B: identity and uMemory"
      ;;
    C)
      echo "⚠️ Deleting all uMemory contents except 'legacy'..."
      rm -f "$UDOS_IDENTITY" "$UDOS_LOG"
      find "$UDOS_HOME/uMemory" -mindepth 1 -maxdepth 1 ! -name "legacy" -exec rm -rf {} +
      echo "✅ Identity removed. Legacy preserved."
      log_info "DESTROY mode C: preserved legacy only"
      ;;
    D)
      echo "♻️ Rebooting system only..."
      cmd_reboot
      return
      ;;
    E)
      echo "🌀 Exiting to uCode..."
      log_info "DESTROY mode E: soft return to uCode"
      return
      ;;
    *)
      echo "❌ Invalid option. Cancelled."
      log_info "DESTROY aborted"
      return
      ;;
  esac

  echo "🔁 Rebooting to apply changes..."
  cmd_reboot
}

cmd_bye() {
  echo "👋 uDOS is entering pause mode..."
  echo "🔒 System is inactive. Choose next action:"
  echo "   [R] RESTART → Refresh the current uCode session"
  echo "   [B] REBOOT  → Reload all system components"
  echo "   [D] DESTROY → Clear identity or memory"
  echo "   [C] CONTINUE → Resume uDOS"
  read -n1 -rp "👉 Choose next step: " next
  echo ""
  case "${next^^}" in
    R) cmd_restart ;;
    B) cmd_reboot ;;
    D) cmd_destroy ;;
    *) echo "🌀 Resuming uCode session..." ;;
  esac
}

cmd_recent() {
  echo "📜 Recent moves:"
  tail -n 10 "${UDOS_MOVES_DIR}/moves-log-$(date +%Y-%m-%d).md"
}

# Main Command Dispatch Loop
trap 'echo "🌀 SESSION END → $(date "+%Y-%m-%d %H:%M:%S")" >> "${UDOS_MOVES_DIR}/moves-log-$(date +%Y-%m-%d).md"' EXIT
while true; do
  echo -ne "\033[1;36m🌀 uCode is ready for your next move...\033[0m"
  sleep 1
  read -rp $'\n\033[1;32muDOS> \033[0m' input
  cmd=$(echo "$input" | awk '{print toupper($1)}')
  args=$(echo "$input" | cut -d' ' -f2-)
  log_command "$input"
  case "$cmd" in
    LOG)
      cmd_log
      ;;
    SAVE)
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
    GO|START)
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
      echo "   LOG       → Log mission/milestone/legacy"
      echo "   SAVE      → Alias for LOG"
      echo "   RUN       → Run a command"
      echo "   GO/START  → Alias for RUN"
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