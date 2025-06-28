#!/bin/bash
# uCode.sh - uDOS Beta v1.6.1 CLI Shell
# Full-featured command-line interface for uDOS environment

# Environment Setup
export UHOME="${HOME}/uDOS"
export UDOS_LOG="${UHOME}/udos.log"
export UDOS_IDENTITY="${UHOME}/identity.md"
export UDOS_DASHBOARD="${UHOME}/uMemory/state/dashboard.json"
export UDOS_MOVES_DIR="${UHOME}/uMemory/logs/moves"
mkdir -p "$UHOME"

# Ensure uMemory subdirectories exist
mkdir -p "${UHOME}/uMemory/missions" "${UHOME}/uMemory/milestones" "${UHOME}/uMemory/legacies"
mkdir -p "${UHOME}/uMemory/logs/errors"
mkdir -p "${UHOME}/uMemory/logs/moves"
mkdir -p "${UHOME}/uMemory/state"

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

if [[ -x "$UHOME/scripts/make-stats.sh" ]]; then
  bash "$UHOME/scripts/make-stats.sh"
fi

if [[ -x "$UHOME/scripts/dashboard-sync.sh" ]]; then
  bash "$UHOME/scripts/dashboard-sync.sh"
fi
if [ ! -f "$UDOS_IDENTITY" ]; then
  echo "⚙️ No identity file found. Running check-setup..."
  bash "$UHOME/scripts/check-setup.sh"
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
  local file="${UDOS_MOVES_DIR}/${id}.md"
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

cmd_check() {
  subcmd=$(echo "$args" | awk '{print toupper($1)}')
  case "$subcmd" in
    TIME)
      cmd_time
      ;;
    LOCATION)
      cmd_location
      ;;
    LOG)
      cmd_log
      ;;
    SETUP)
      bash "$UHOME/scripts/check-setup.sh"
      log_info "CHECK SETUP executed"
      log_move_template "check setup"
      ;;
    IDENTITY)
      cmd_identity
      ;;
    *)
      echo "🔎 CHECK what?"
      echo "   TIME      → View or set timezone"
      echo "   LOCATION  → View or set location code"
      echo "   LOG       → Log mission/milestone/legacy"
      echo "   SETUP     → Run full environment check"
      echo "   IDENTITY  → Display current identity"
      ;;
  esac
}

cmd_identity() {
  echo "🆔 Current uDOS Identity:"
  if [ -f "$UDOS_IDENTITY" ]; then
    cat "$UDOS_IDENTITY"
  else
    echo "❌ No identity file found."
  fi
  log_info "IDENTITY command executed"
  log_move_template "identity"
}

cmd_log() {
  echo -ne $'\033[1;34m📝 Log Entry Type:\033[0m '
  read what
  if [[ "$what" =~ ^(mission|milestone|legacy)$ ]]; then
    bash "$UHOME/scripts/make-log.sh" "$what"
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
  bash "$UHOME/scripts/make-stats.sh"
}

cmd_time() {
  echo "🕒 Current timezone: $(date +%Z)"
  echo "🕓 UTC offset: $(date +%z)"
  read -rp "🌐 Enter new timezone (e.g., Australia/Sydney) or leave blank to keep: " new_tz
  if [[ -n "$new_tz" ]]; then
    export TZ="$new_tz"
    echo "✅ Timezone updated to: $(date +%Z) (UTC$(date +%z))"
  else
    echo "ℹ️ Timezone unchanged."
  fi
  log_info "TIME command executed"
  log_move_template "time"
}

cmd_location() {
  echo "📍 Current location (based on timezone): $(date +%Z)"
  read -rp "🗺️ Enter new location code (or leave blank to keep current): " new_loc
  if [[ -n "$new_loc" ]]; then
    echo "✅ Location updated: $new_loc"
    echo "$new_loc" > "$UHOME/uMemory/state/location.md"
  else
    echo "ℹ️ Location unchanged."
  fi
  log_info "LOCATION command executed"
  log_move_template "location"
}

cmd_list() {
  echo "📂 Current directory: $(pwd)"
  ls -1Ap | grep -v '^\.'
}

cmd_mission() {
  cat "$UHOME/state/current_mission.md" 2>/dev/null || echo "🎯 No mission active."
}

cmd_map() {
  cat "$UHOME/uKnowledge/map/current_region.md" 2>/dev/null || echo "🗺️ No map loaded."
}

cmd_dash() {
  echo "📈 Displaying dashboard..."
  cat "$UHOME/uTemplate/dashboards/dashboard-header.md"
  [ -f "$UDOS_DASHBOARD" ] && cat "$UDOS_DASHBOARD"
  cat "$UHOME/uTemplate/dashboards/dashboard-footer.md"
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
  bash "$UHOME/scripts/make-structure.sh"

  echo "🔍 Rechecking setup and permissions..."
  bash "$UHOME/scripts/check-setup.sh"

  echo "📊 Rebuilding stats and dashboard..."
  bash "$UHOME/scripts/make-stats.sh"
  bash "$UHOME/scripts/dashboard-sync.sh"

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
  read -n1 -rp $'\033[1;34m👉 Select DESTROY option:\033[0m ' choice
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
      rm -rf "$UHOME/uMemory"
      echo "✅ Identity and memory deleted."
      log_info "DESTROY mode B: identity and uMemory"
      ;;
    C)
      echo "⚠️ Deleting all uMemory contents except 'legacy'..."
      rm -f "$UDOS_IDENTITY" "$UDOS_LOG"
      find "$UHOME/uMemory" -mindepth 1 -maxdepth 1 ! -name "legacy" -exec rm -rf {} +
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
  read -n1 -rp $'\033[1;34m👉 Choose next step:\033[0m ' next
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
  echo -ne "\033[1;36m🌀 \033[0m"
  sleep 1
  read -rp $'\033[1;32muDOS> \033[0m' input
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
    CHECK)
      cmd_check
      ;;
    TREE)
      cmd_tree
      ;;
    STATS)
      cmd_stats
      ;;
    TIME)
      cmd_time
      ;;
    LOCATION)
      cmd_location
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
      echo "   GO/START   → Alias for RUN"
      echo "   CHECK      → Run subcommands (TIME, LOCATION, LOG, SETUP, IDENTITY)"
      echo "   TREE      → Show file tree"
      echo "   STATS     → Generate dashboard stats"
      echo "   TIME      → Check or set your timezone"
      echo "   LOCATION  → Check or set your location code"
      echo "   LIST      → List current folder"
      echo "   MAP       → Show current region"
      echo "   MISSION   → Display active mission"
      echo "   DASH      → Show dashboard"
      echo "   SYNC      → Sync dashboard"
      echo "   RESTART   → Restart shell"
      echo "   REBOOT    → Reboot system"
      echo "   DESTROY   → Delete your identity"
      echo "   IDENTITY  → Display user identity file"
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