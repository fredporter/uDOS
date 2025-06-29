#!/bin/bash
# uCode.sh - uDOS Beta v1.6.1 CLI Shell
# Full-featured command-line interface for uDOS environment

# Environment Setup
export UHOME="${HOME}/uDOS"
export UDENT="$UHOME/sandbox/user.md"
export UDOS_DASHBOARD="${UHOME}/uMemory/state/dashboard.json"
export UDOS_MOVES_DIR="${UHOME}/uMemory/logs/moves"
mkdir -p "$UHOME"
# --- Ensure required folders exist before any logging or stats ---
mkdir -p "$UHOME/uMemory/logs/moves"
# mkdir -p "$UHOME/sandbox"
mkdir -p "${UHOME}/uMemory/missions" "${UHOME}/uMemory/milestones" "${UHOME}/uMemory/legacy"
mkdir -p "${UHOME}/uMemory/logs/errors"
mkdir -p "${UHOME}/uMemory/state"

# --- uDOS Version Detection ---
IDENTITY_FILE="$UHOME/uMemory/state/identity.md"
if [[ -f "$IDENTITY_FILE" ]]; then
  UVERSION=$(grep "Version:" "$IDENTITY_FILE" | cut -d':' -f2 | xargs)
else
  UVERSION="Unknown"
fi

log_move() {
  if [[ "$UCODE_BOOTING" == "true" ]]; then return; fi
  local cmd="$1"
  local log_file="$UHOME/uMemory/logs/move-log-$(date +%Y-%m-%d).md"
  echo "[$(date +%H:%M:%S)] → $cmd" >> "$log_file"
}

# Log session start
move_log_file="$UHOME/uMemory/logs/move-log-$(date +%Y-%m-%d).md"
if [[ -f "$move_log_file" ]]; then
  echo "📘 Daily move log located for $(date +%Y-%m-%d)"
else
  echo "📗 Daily move log initiated for $(date +%Y-%m-%d)"
fi
echo "🌀 SESSION START → $(date '+%Y-%m-%d %H:%M:%S')" >> "$move_log_file"

# Startup Header
echo "🚀 Welcome to uDOS $UVERSION"
cat << EOF
 _    _  ____   ___   ____  ______ _____  
| |  | |/ __ \ / _ \ / __ \|  ____|  __ \ 
| |  | | |  | | | | | |  | | |__  | |  | |
| |  | | |  | | | | | |  | |  __| | |  | |
| |__| | |__| | |_| | |__| | |____| |__| |
 \____/ \____/ \___/ \____/|______|_____/  
     uCode Shell · $UVERSION 🌀
EOF
echo "🧠 Loading environment..."

USER_FILE="$UHOME/sandbox/user.md"
if [[ ! -f "$USER_FILE" ]]; then
  echo "⚙️ No identity file found. Running check-setup..."
  bash "$UHOME/scripts/check-setup.sh"

  if [[ -f "$USER_FILE" ]]; then
    echo "✅ Identity confirmed."
  else
    echo "❌ Identity file still not found after setup."
    exit 1
  fi
  echo "🔍 check-setup.sh completed."
fi

if [ -f "$UDENT" ]; then
  username=""
  location=""
  created=""
  timezone=""

  while IFS=':' read -r key value; do
    key=$(echo "$key" | sed 's/^[-* ]*//;s/\*\*$//;s/^ *//;s/ *$//')
    value=$(echo "$value" | xargs)
    case "$key" in
      Username) username="$value" ;;
      Location) location="$value" ;;
      Created) created="$value" ;;
      Timezone) timezone="$value" ;;
    esac
  done < "$UDENT"

  echo "🔑 Identity loaded: User: $username"
  echo "Location: $location"
  echo "Created: $created"
  echo "Timezone: $timezone"
else
  echo "❌ Identity still missing. Please run DESTROY or REBOOT."
  exit 1
fi

PASSWORD=$(grep "Password" "$UDENT" | cut -d':' -f2- | xargs)
if [[ -n "$PASSWORD" && "$REBOOT_FLAG" == "true" ]]; then
  echo -n "🔐 Enter password to continue: "
  read -rs input_pw
  echo ""
  if [[ "$input_pw" != "$PASSWORD" ]]; then
    echo "❌ Incorrect password. Aborting."
    exit 1
  else
    echo "✅ Password accepted."
  fi
fi

# Run stats and dashboard sync after setup check
export UCODE_BOOTING=true
if [[ -x "$UHOME/scripts/make-stats.sh" ]]; then
  bash "$UHOME/scripts/make-stats.sh"
fi
if [[ -x "$UHOME/scripts/dashboard-sync.sh" ]]; then
  echo "⏳ Syncing dashboard..."
  SECONDS=0
  bash "$UHOME/scripts/dashboard-sync.sh"
  echo "✅ Dashboard sync complete in ${SECONDS}s."
fi
unset UCODE_BOOTING

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
echo "- Legacy items: $(find "$UHOME/uMemory/legacy" -type f | wc -l)"
echo "- Total logs: $(find "$UHOME/uMemory/logs/moves" -type f | wc -l)"
echo ""

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
      ;;
    IDENTITY)
      cmd_identity
      ;;
    INPUT)
      bash "$UHOME/scripts/make-input.sh"
      ;;
    *)
      echo "🔎 CHECK what?"
      echo "   TIME      → View or set timezone"
      echo "   LOCATION  → View or set location code"
      echo "   LOG       → Log mission/milestone/legacy"
      echo "   SETUP     → Run full environment check"
      echo "   IDENTITY  → Display current identity"
      echo "   INPUT     → Generate user input file"
      ;;
  esac
}

cmd_identity() {
  echo "🆔 Current uDOS Identity:"
  if [ -f "$UDENT" ]; then
    cat "$UDENT"
  else
    echo "❌ No identity file found."
  fi
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
}

cmd_undo() {
  echo "↩️ Undoing last action..."
  # Placeholder for undo logic
  sleep 1
  echo "✅ Undo completed."
}

cmd_run() {
  bash "$HOME/uDOS/scripts/command.sh" "$args"
}

cmd_tree() {
  bash "$HOME/uDOS/scripts/make-tree.sh"
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
  echo "📈 Building dashboard..."
  bash "$UHOME/scripts/make-dash.sh"
  echo ""
  echo "📋 Dashboard Output:"
  [ -f "$UHOME/sandbox/dash-log-$(date +%Y-%m-%d).md" ] && cat "$UHOME/sandbox/dash-log-$(date +%Y-%m-%d).md"
}

cmd_restart() {
  echo "🔄 Restarting uDOS shell..."
  log_move "System restart initiated."
  exec "$0" # Relaunch script
}

cmd_reboot() {
  echo "♻️ Rebooting uDOS system..."
  log_move "System reboot initiated."

  echo "🧼 Rebuilding structure..."
  bash "$UHOME/scripts/make-structure.sh"

  echo "🔍 Rechecking setup and permissions..."
  bash "$UHOME/scripts/check-setup.sh"

  echo "📊 Rebuilding stats and dashboard..."
  bash "$UHOME/scripts/make-stats.sh"
  bash "$UHOME/scripts/dashboard-sync.sh"

  echo "🌀 Relaunching shell..."
  export REBOOT_FLAG=true
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
      rm -f "$UDENT"
      echo "✅ Identity deleted."
      log_move "DESTROY mode A: identity only"
      ;;
    B)
      echo "⚠️ Deleting identity and uMemory..."
      rm -f "$UDENT"
      rm -rf "$UHOME/uMemory"
      echo "✅ Identity and memory deleted."
      log_move "DESTROY mode B: identity and uMemory"
      ;;
    C)
      echo "⚠️ Deleting all uMemory contents except 'legacy'..."
      rm -f "$UDENT"
      find "$UHOME/uMemory" -mindepth 1 -maxdepth 1 ! -name "legacy" -exec rm -rf {} +
      echo "✅ Identity removed. Legacy preserved."
      log_move "DESTROY mode C: preserved legacy only"
      ;;
    D)
      echo "♻️ Rebooting system only..."
      cmd_reboot
      return
      ;;
    E)
      echo "🌀 Exiting to uCode..."
      log_move "DESTROY mode E: soft return to uCode"
      return
      ;;
    *)
      echo "❌ Invalid option. Cancelled."
      log_move "DESTROY aborted"
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
  tail -n 10 "$UHOME/uMemory/logs/move-log-$(date +%Y-%m-%d).md"
}

#
# Main Command Dispatch Loop
trap 'echo "🌀 SESSION END → $(date "+%Y-%m-%d %H:%M:%S")" >> "$UHOME/uMemory/logs/move-log-$(date +%Y-%m-%d).md"' EXIT
while true; do
  # Prompt for input with visible swirl and blinking block cursor
  printf "\033[?25h"      # Show cursor
  printf "\033[?1c"       # Enable blinking block (may vary by terminal)
  printf "\033[1;30m█\033[0m\r"
  sleep 0.1
  printf "  \r"
  echo -ne "\033[1;36m🌀 \033[0m"
  read -r input
  cmd=$(echo "$input" | awk '{print toupper($1)}')
  args=$(echo "$input" | cut -d' ' -f2-)
  log_move "$input"
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