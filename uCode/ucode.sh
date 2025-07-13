# --- Devcontainer Command ---
cmd_devcontainer() {
  echo "🛠️  Checking devcontainer setup..."
  if [ -d "$UHOME/.devcontainer" ]; then
    echo "📁 .devcontainer directory exists."
    tree "$UHOME/.devcontainer" 2>/dev/null || ls -R "$UHOME/.devcontainer"
    echo ""
    if [ -f "$UHOME/uCode/setup-dev.sh" ]; then
      echo "🚀 Running dev setup script..."
      bash "$UHOME/uCode/setup-dev.sh"
    else
      echo "⚠️ setup-dev.sh not found. Skipping script execution."
    fi
  else
    echo "❌ .devcontainer folder not found in $UHOME"
  fi
  echo ""
}
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

# Track if session end has been logged
export UCODE_SESSION_ENDED=false

# --- uDOS Version Detection ---
IDENTITY_FILE="$UHOME/uMemory/state/identity.md"
if [[ -f "$IDENTITY_FILE" ]]; then
  UVERSION=$(grep "Version:" "$IDENTITY_FILE" | cut -d':' -f2 | xargs)
else
  UVERSION="Unknown"
fi

log_move() {
  local cmd="$1"
  local trimmed="${cmd// }"
  if [[ "$UCODE_BOOTING" == "true" || -z "$trimmed" || "$cmd" == "exit" || "$cmd" == "bye" ]]; then
    return
  fi
  bash "$UHOME/uCode/log.sh" move "$cmd"
}


# Startup Header
echo "🚀 Welcome to uDOS $UVERSION"
echo -e "\033[1;31m _    _  ____   ___   ____  ______ _____  \033[0m"
echo -e "\033[1;33m| |  | |/ __ \ / _ \ / __ \|  ____|  __ \ \033[0m"
echo -e "\033[1;32m| |  | | |  | | | | | |  | | |__  | |  | |\033[0m"
echo -e "\033[1;36m| |  | | |  | | | | | |  | |  __| | |  | |\033[0m"
echo -e "\033[1;34m| |__| | |__| | |_| | |__| | |____| |__| |\033[0m"
echo -e "\033[1;35m \____/ \____/ \___/ \____/|______|_____/ \033[0m"
echo -e "    \033[1;37muCode Shell · $UVERSION 🌀\033[0m"
echo ""
echo "🧠 Loading environment..."

USER_FILE="$UHOME/sandbox/user.md"
if [[ ! -f "$USER_FILE" ]]; then
  echo "⚙️ No identity file found. Running check-setup..."
  bash "$UHOME/uCode/check-setup.sh"

  if [[ -f "$USER_FILE" ]]; then
    echo "✅ Identity confirmed."
  else
    echo "❌ Identity file still not found after setup."
    exit 1
  fi
  echo "🔍 check-setup.sh completed."
  echo ""
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

  [[ -z "$username" ]] && username="user"

  echo "🔑 Identity loaded: User: $username"
  echo "Location: $location"
  echo "Created: $created"
  echo "Timezone: $timezone"
  echo ""
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

echo ""

echo "📋 Session Info:"
echo "- Hostname: $(hostname)"
echo "- Shell: $SHELL"
echo "- User: $username"
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
      bash "$UHOME/uCode/check.sh" all
      ;;
    IDENTITY)
      cmd_identity
      ;;
    INPUT)
      bash "$UHOME/uCode/structure.sh" build --input
      ;;
    STATS)
      cmd_stats
      ;;
    MISSION)
      cmd_mission
      ;;
    MAP)
      cmd_map
      ;;
    *)
      echo "🔎 CHECK what?"
      echo "   TIME      → View or set timezone"
      echo "   LOCATION  → View or set location code"
      echo "   LOG       → Log mission/milestone/legacy"
      echo "   SETUP     → Run full environment check"
      echo "   IDENTITY  → Display current identity"
      echo "   INPUT     → Generate user input file"
      echo "   STATS     → Generate dashboard stats"
      echo "   MISSION   → Display active mission"
      echo "   MAP       → Show current region"
      echo ""
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
  echo ""
}

cmd_log() {
  read -rp "📝 What do you want to log (mission/milestone/legacy)? " what
  if [[ "$what" =~ ^(mission|milestone|legacy)$ ]]; then
    bash "$UHOME/uCode/log.sh" move "Logged $what entry"
  else
    echo "❌ Invalid log type."
  fi
  echo ""
}

cmd_stats() {
  bash "$UHOME/uCode/make-stats.sh"
}

cmd_mission() {
  cat "$UHOME/state/current_mission.md" 2>/dev/null || echo "🎯 No mission active."
  echo ""
}

cmd_map() {
  cat "$UHOME/uKnowledge/map/current_region.md" 2>/dev/null || echo "🗺️ No map loaded."
  echo ""
}

cmd_run() {
  bash "$HOME/uDOS/uCode/command.sh" "$args"
}

cmd_tree() {
  bash "$HOME/uDOS/uCode/make-tree.sh"
}

# --- Timezone Command ---
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
  echo ""
}

# --- Location Command ---
cmd_location() {
  echo "📍 Current location code: $(cat "$UHOME/uMemory/state/location.md" 2>/dev/null || echo "Unknown")"
  read -rp "🗺️ Enter new location code (or leave blank to keep current): " new_loc
  if [[ -n "$new_loc" ]]; then
    echo "$new_loc" > "$UHOME/uMemory/state/location.md"
    echo "✅ Location updated to $new_loc"
  else
    echo "ℹ️ Location unchanged."
  fi
  echo ""
}

cmd_list() {
  echo "📁 uDOS Directory Listing"
  echo ""
  echo "🗂️ sandbox/"
  tree -L 2 "$UHOME/sandbox" 2>/dev/null || ls -R "$UHOME/sandbox"
  echo ""
  echo "🧠 uMemory/"
  tree -L 2 "$UHOME/uMemory" 2>/dev/null || ls -R "$UHOME/uMemory"
  echo ""
  echo "📚 uKnowledge/"
  tree -L 2 "$UHOME/uKnowledge" 2>/dev/null || ls -R "$UHOME/uKnowledge"
  echo ""
}

cmd_dash() {
  echo ""

  bash "$UHOME/uCode/dash.sh"
  tail -n 60 "$UHOME/uMemory/rendered/dash-rendered.md" | grep -v '^<!--'
  echo ""
}

cmd_restart() {
  echo "🔄 Restarting uDOS shell..."
  exec "$0" # Relaunch script
}

cmd_reboot() {
  echo "♻️ Rebooting uDOS system..."

  echo "🧼 Rebuilding structure..."
  bash "$UHOME/uCode/structure.sh" build

  echo "🔍 Rechecking setup and permissions..."
  bash "$UHOME/uCode/check.sh" all

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
      ;;
    B)
      echo "⚠️ Deleting identity and uMemory..."
      rm -f "$UDENT"
      rm -rf "$UHOME/uMemory"
      echo "✅ Identity and memory deleted."
      ;;
    C)
      echo "⚠️ Deleting all uMemory contents except 'legacy'..."
      rm -f "$UDENT"
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

cmd_recent() {
  echo "📜 Recent moves:"
  tail -n 10 "$UHOME/uMemory/moves/moves-$(date +%Y-%m-%d).md"
  echo ""
}

# --- Development Diagnostics ---
cmd_debug() {
  echo "🔍 uDOS DEBUG MODE"
  echo "🧬 Environment Variables:"
  env | grep -E 'UHOME|USER|SHELL|PWD|TZ'
  echo ""
  echo "📄 Last 20 Moves:"
  tail -n 20 "$UHOME/uMemory/logs/move-log-$(date +%Y-%m-%d).md"
  echo ""
  echo "🗂️ Available Scripts:"
  ls -1 "$UHOME/scripts"
  echo ""
  echo "❗ Recent Errors (if any):"
  find "$UHOME/uMemory/logs/errors" -type f -exec tail -n 5 {} \;
  echo ""
  echo "🧩 uDOS Version: $UVERSION"
  echo ""
}

#
# Main Command Dispatch Loop
trap 'if [ "$UCODE_SESSION_ENDED" = false ]; then echo "🌀 SESSION END → $(date "+%Y-%m-%d %H:%M:%S")" >> "$UHOME/uMemory/logs/move-log-$(date +%Y-%m-%d).md"; export UCODE_SESSION_ENDED=true; fi' EXIT
trap 'echo -e "\n🛑 Interrupted. Type EXIT or BYE to quit safely."' SIGINT
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
  # Only log moves if not blank and not during boot
  if [[ -n "${input// }" && "$UCODE_BOOTING" != "true" ]]; then
    log_move "$input"
  fi
  case "$cmd" in
    LOG)
      cmd_log
      ;;
    RUN)
      cmd_run
      ;;
    TREE)
      cmd_tree
      ;;
    LIST)
      cmd_list "$args"
      ;;
    DASH)
      cmd_dash
      ;;
    SYNC)
      sync_dashboard
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
    IDENTITY)
      cmd_identity
      ;;
    DEVCON)
      cmd_devcontainer
      ;;
    QUIT)
      echo "👋 uDOS session ended."
      exit 0
      ;;
    RECENT)
      cmd_recent
      ;;
    CHECK)
      cmd_check
      ;;
    HELP)
      echo "🧩 uDOS Version: $UVERSION"
      echo "🧠 Available uDOS commands:"
      echo "   LOG       → Log mission/milestone/legacy"
      echo "   RUN       → Run a uScript"
      echo "   TREE      → Generate file tree"
      echo "   LIST      → List Sandbox and uMemory folders"
      echo "   DASH      → Show dashboard"
      echo "   SYNC      → Sync dashboard"
      echo "   RESTART   → Restart shell"
      echo "   REBOOT    → Reboot system"
      echo "   DESTROY   → Delete your identity and/or files"
      echo "   IDENTITY  → Display user identity file"
      echo "   DEVCON    → Check and run setup-dev.sh"
      echo "   QUIT      → Close session"
      echo "   RECENT    → Show last 10 moves"
      echo "   CHECK     → Run subcommands (TIME, LOCATION, LOG, SETUP, IDENTITY)"
      echo ""
      ;;
    "")
      # Ignore empty input
      ;;
    *)
      echo "❓ Unknown command '$cmd'. Type HELP for list of commands."
      ;;
  esac
done
