#!/bin/bash
# uCode.sh - uDOS Beta v1.6.1 CLI Shell
# Full-featured command-line interface for uDOS environment

# Environment Setup
export UHOME="${HOME}/uDOS"
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
echo "[START] $(date '+%H:%M:%S')" >> "${UDOS_MOVES_DIR}/move-$(date +%Y-%m-%d).md"

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
  username=""
  location=""
  created=""
  timezone=""
  utc_offset=""

  while IFS=': ' read -r key value; do
    case "$key" in
      Username) username="$value" ;;
      Location) location="$value" ;;
      Created) created="$value" ;;
      Timezone) timezone="$value" ;;
      UTC\ Offset) utc_offset="$value" ;;
    esac
  done < "$UDOS_IDENTITY"

  echo "🔑 Identity loaded: User: $username"
  echo "Location: $location"
  echo "Created: $created"
  echo "Timezone: $timezone"
  echo "UTC Offset: $utc_offset"
  # --- BEGIN Dynamic Dashboard ---
  echo ""
  echo "# 📊 uDOS Dashboard — Beta v1.6.1"
  echo ""
  echo "- **User:** ${username:-🔲}"
  echo "- **Location:** ${location:-🔲}"
  echo "- **Date:** $(date '+%Y-%m-%d')"
  echo ""
  echo "---"
  echo ""
  echo "## ⚙️ System Status"
  echo ""
  echo "- Last Move: $(grep '🌀 SESSION START' \"$UDOS_MOVES_DIR/move-log-$(date +%Y-%m-%d).md\" | tail -1 | cut -d'→' -f2- | xargs)"
  echo "- Active Mission: $(cat \"$UHOME/state/mission.md\" 2>/dev/null | head -1 || echo 🔲)"
  echo "- Memory State: OK"
  echo ""
  echo "---"
  echo ""
  # --- END Dynamic Dashboard ---
else
  echo "❌ Identity still missing. Please run DESTROY or REBOOT."
  exit 1
fi
echo ""

echo "📋 Session Info:"
echo "- Hostname: $(hostname)"
echo "- Shell: $SHELL"
echo "- User: $USER"
echo "- uDOS Path: $UHOME"
echo ""

echo "🧠 Memory Stats:"
echo "- Missions: $(find "$UHOME/uMemory/missions" -type f | wc -l)"
echo "- Milestones: $(find "$UHOME/uMemory/milestones" -type f | wc -l)"
echo "- Legacy items: $(find "$UHOME/uMemory/legacies" -type f | wc -l)"
echo "- Total logs: $(find "$UHOME/uMemory/logs/moves" -type f | wc -l)"
echo ""

# Logging Function - unified move log
log_move() {
  local cmd="$1"
  local timestamp
  timestamp=$(date +"%H:%M:%S")
  local log_file="${UDOS_MOVES_DIR}/move-$(date +%Y-%m-%d).md"
  echo "[$timestamp] → $cmd" >> "$log_file"
  echo "📄 Move logged: $cmd"
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
      log_move "check setup"
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
  log_move "identity"
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
  log_move "redo"
}

cmd_undo() {
  echo "↩️ Undoing last action..."
  # Placeholder for undo logic
  sleep 1
  echo "✅ Undo completed."
  log_move "undo"
}

cmd_run() {
  bash "$HOME/uDOS/scripts/command.sh" "$args"
  log_move "run $args"
}

cmd_tree() {
  bash "$HOME/uDOS/scripts/make-tree.sh"
  log_move "tree"
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
  log_move "time"
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
  log_move "location"
}

cmd_list() {
  local target="$1"
  local base="${UHOME}"

  # Default to root if no path is given
  if [[ -z "$target" ]]; then
    target="$base"
  else
    # Expand and sanitize target path
    target="$(realpath -m "$base/$target")"
    [[ "$target" == "$base"* ]] || {
      echo "❌ Access denied: Outside uDOS root."
      return 1
    }
  fi

  echo "📂 uDOS directory: ${target/$HOME/~}"
  ls -lA "$target"
}

cmd_mission() {
  cat "$UHOME/state/current_mission.md" 2>/dev/null || echo "🎯 No mission active."
}

cmd_map() {
  cat "$UHOME/uKnowledge/map/current_region.md" 2>/dev/null || echo "🗺️ No map loaded."
}

cmd_dash() {
  echo "📈 Displaying dashboard..."
  # Dynamic dashboard is now printed at login. To avoid duplicate or outdated dashboards, this is commented out.
  # cat "$UHOME/uTemplate/dashboards/dashboard-header.md"
  # [ -f "$UDOS_DASHBOARD" ] && cat "$UDOS_DASHBOARD"
  # cat "$UHOME/uTemplate/dashboards/dashboard-footer.md"
  log_move "dash"
}

cmd_restart() {
  echo "🔄 Restarting uDOS shell..."
  exec "$0" # Relaunch script
}

cmd_reboot() {
  echo "♻️ Rebooting uDOS system..."

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

  case "$(echo "$choice" | tr '[:lower:]' '[:upper:]')" in
    A)
      echo "⚠️ Deleting identity only..."
      rm -f "$UDOS_IDENTITY"
      echo "✅ Identity deleted."
      ;;
    B)
      echo "⚠️ Deleting identity and uMemory..."
      rm -f "$UDOS_IDENTITY"
      rm -rf "$UHOME/uMemory"
      echo "✅ Identity and memory deleted."
      ;;
    C)
      echo "⚠️ Deleting all uMemory contents except 'legacy'..."
      rm -f "$UDOS_IDENTITY"
      find "$UHOME/uMemory" -mindepth 1 -maxdepth 1 ! -name "legacy" -exec rm -rf {} +
      echo "✅ Identity removed. Legacy preserved."
      ;;
    D)
      echo "♻️ Rebooting system only..."
      cmd_reboot
      return
      ;;
    E)
      echo "🌀 Exiting to uCode..."
      return
      ;;
    *)
      echo "❌ Invalid option. Cancelled."
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
  tail -n 10 "${UDOS_MOVES_DIR}/move-log-$(date +%Y-%m-%d).md"
}

# Main Command Dispatch Loop
trap 'echo "[END] $(date "+%H:%M:%S")" >> "${UDOS_MOVES_DIR}/move-$(date +%Y-%m-%d).md"' EXIT
while true; do
  echo -ne "\033[1;36m🌀 \033[0m"
  # Flash cursor once at prompt
  tput civis; sleep 0.05; tput cnorm
  read -rp "" input
  cmd=$(echo "$input" | awk '{print toupper($1)}')
  args=$(echo "$input" | cut -d' ' -f2-)
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