#!/bin/bash
# uCode.sh - uDOS Beta v1.6.1 CLI Shell

# Environment Setup
export UHOME="${HOME}/uDOS"
export UCODE_HOME="$UHOME/uCode"
export UCODE_DATASETS="$UCODE_HOME/datasets"
export UCODE_VARS="$UCODE_HOME/vars"
export UCODE_LOGS="$UCODE_HOME/logs"
export UCODE_TEMPLATES="$UCODE_HOME/templates"
export UCODE_EXAMPLES="$UCODE_HOME/examples"
export UDENT="$UCODE_VARS/user.md"
export UDOS_DASHBOARD="$UCODE_HOME/state/dashboard.json"
export UDOS_MOVES_DIR="$UCODE_LOGS/moves"
mkdir -p "$UCODE_HOME" "$UCODE_DATASETS" "$UCODE_VARS" "$UCODE_LOGS" "$UCODE_TEMPLATES" "$UCODE_EXAMPLES"
mkdir -p "$UCODE_LOGS/moves" "$UCODE_LOGS/errors" "$UCODE_HOME/state"

export UCODE_SESSION_ENDED=false

# --- uDOS Version Detection ---
IDENTITY_FILE="$UCODE_VARS/identity.md"
if [[ -f "$IDENTITY_FILE" ]]; then
  UVERSION=$(grep "Version:" "$IDENTITY_FILE" | cut -d':' -f2 | xargs)
else
  UVERSION="Unknown"
fi

# Log moves to uCode/logs/
log_move() {
  local cmd="$1"
  local trimmed="${cmd// }"
  if [[ "$UCODE_BOOTING" == "true" || -z "$trimmed" || "$cmd" == "exit" || "$cmd" == "bye" ]]; then
    return
  fi
  echo "$cmd" >> "$UCODE_LOGS/move-log-$(date +%Y-%m-%d).md"
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

USER_FILE="$UCODE_VARS/user.md"
if [[ ! -f "$USER_FILE" ]]; then
  echo "⚙️ No identity file found. Running check-setup..."
  bash "$UCODE_HOME/check.sh" setup

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
echo "- Datasets: $(find "$UCODE_DATASETS" -type f | wc -l)"
echo "- Templates: $(find "$UCODE_TEMPLATES" -type f | wc -l)"
echo "- Logs: $(find "$UCODE_LOGS" -type f | wc -l)"
echo ""

# Dashboard Sync
sync_dashboard() {
  if [ -f "$UDOS_DASHBOARD" ]; then
    echo "📊 Syncing dashboard..."
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
    TIME) cmd_time ;;
    LOCATION) cmd_location ;;
    LOG) cmd_log ;;
    SETUP) bash "$UCODE_HOME/check.sh" all ;;
    IDENTITY) cmd_identity ;;
    INPUT) bash "$UCODE_HOME/structure.sh" build --input ;;
    STATS) cmd_stats ;;
    MISSION) cmd_mission ;;
    MAP) cmd_map ;;
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
    bash "$UCODE_HOME/log.sh" move "$cmd"
  else
    echo "❌ Invalid log type."
  fi
  echo ""
}

cmd_stats() {
  bash "$UCODE_HOME/make-stats.sh"
}

cmd_mission() {
  cat "$UCODE_HOME/state/current_mission.md" 2>/dev/null || echo "🎯 No mission active."
  echo ""
}

cmd_map() {
  cat "$UCODE_DATASETS/map/current_region.md" 2>/dev/null || echo "🗺️ No map loaded."
  echo ""
}

cmd_run() {
  # Usage: RUN <script>
  script_path="$args"
  # Prefer uCode/examples/ if not absolute path
  if [[ ! "$script_path" = /* ]]; then
    script_path="$UCODE_EXAMPLES/$script_path"
  fi
  if [[ -f "$script_path" ]]; then
    bash "$UCODE_HOME/ucode-runner.sh" run "$script_path"
  else
    echo "❌ Script not found: $script_path"
    echo "   (Looked in $script_path)"
  fi
}

cmd_tree() {
  tree -L 2 "$UCODE_HOME" 2>/dev/null || ls -R "$UCODE_HOME"
}

cmd_list() {
  echo "📁 uCode Directory Listing"
  echo ""
  echo "🗂️ uCode/"
  tree -L 2 "$UCODE_HOME" 2>/dev/null || ls -R "$UCODE_HOME"
  echo ""
}

cmd_dash() {
  echo ""
  bash "$UCODE_HOME/dash.sh"
  tail -n 60 "$UCODE_HOME/rendered/dash-rendered.md" 2>/dev/null | grep -v '^<!--'
  echo ""
}

cmd_restart() {
  echo "🔄 Restarting uCode shell..."
  exec "$0"
}

cmd_reboot() {
  echo "♻️ Rebooting uCode system..."
  echo "🧼 Rebuilding structure..."
  bash "$UCODE_HOME/structure.sh" build
  echo "🔍 Rechecking setup and permissions..."
  bash "$UCODE_HOME/check.sh" all
  echo "🌀 Relaunching shell..."
  export REBOOT_FLAG=true
  exec "$0"
}

cmd_destroy() {
  echo "💥 uCode DESTROY Mode:"
  echo "  [A] Remove identity only"
  echo "  [B] Remove identity and all logs"
  echo "  [C] Remove identity, archive logs to /legacy, then delete logs"
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
      echo "⚠️ Deleting identity and logs..."
      rm -f "$UDENT"
      rm -rf "$UCODE_LOGS"
      echo "✅ Identity and logs deleted."
      ;;
    C)
      echo "⚠️ Deleting all logs except 'legacy'..."
      rm -f "$UDENT"
      find "$UCODE_LOGS" -mindepth 1 -maxdepth 1 ! -name "legacy" -exec rm -rf {} +
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
  tail -n 10 "$UCODE_LOGS/move-log-$(date +%Y-%m-%d).md"
  echo ""
}

cmd_debug() {
  echo "🔍 uCode DEBUG MODE"
  echo "🧬 Environment Variables:"
  env | grep -E 'UHOME|UCODE_HOME|USER|SHELL|PWD|TZ'
  echo ""
  echo "📄 Last 20 Moves:"
  tail -n 20 "$UCODE_LOGS/move-log-$(date +%Y-%m-%d).md"
  echo ""
  echo "🗂️ Available Scripts:"
  ls -1 "$UCODE_HOME"
  echo ""
  echo "❗ Recent Errors (if any):"
  find "$UCODE_LOGS/errors" -type f -exec tail -n 5 {} \;
  echo ""
  echo "🧩 uCode Version: $UVERSION"
  echo ""
}

cmd_devcontainer() {
  echo "🛠️  Devcontainer setup not implemented."
  echo ""
}

cmd_cleanup() {
  bash "$UCODE_HOME/../uScript/cleanup.sh"
}

# Main Command Dispatch Loop
trap 'if [ "$UCODE_SESSION_ENDED" = false ]; then echo "🌀 SESSION END → $(date "+%Y-%m-%d %H:%M:%S")" >> "$UCODE_LOGS/move-log-$(date +%Y-%m-%d).md"; export UCODE_SESSION_ENDED=true; fi' EXIT
trap 'echo -e "\n🛑 Interrupted. Type EXIT or BYE to quit safely."' SIGINT
while true; do
  printf "\033[?25h"
  printf "\033[?1c"
  printf "\033[1;30m█\033[0m\r"
  sleep 0.1
  printf "  \r"
  echo -ne "\033[1;36m🌀 \033[0m"
  read -r input
  cmd=$(echo "$input" | awk '{print toupper($1)}')
  args=$(echo "$input" | cut -d' ' -f2-)
  if [[ -n "${input// }" && "$UCODE_BOOTING" != "true" ]]; then
    log_move "$input"
  fi
  case "$cmd" in
    LOG) cmd_log ;;
    RUN) cmd_run ;;
    TREE) cmd_tree ;;
    LIST) cmd_list "$args" ;;
    DASH) cmd_dash ;;
    SYNC) sync_dashboard ;;
    RESTART) cmd_restart ;;
    REBOOT) cmd_reboot ;;
    DESTROY) cmd_destroy ;;
    IDENTITY) cmd_identity ;;
    DEVCON) cmd_devcontainer ;;
    QUIT) echo "👋 uCode session ended."; exit 0 ;;
    RECENT) cmd_recent ;;
    CHECK) cmd_check ;;
    DEBUG) cmd_debug ;;
    CLEANUP) cmd_cleanup ;;
    HELP)
      echo "🧩 uCode Version: $UVERSION"
      echo "🧠 Available uCode commands:"
      echo "   LOG       → Log mission/milestone/legacy"
      echo "   RUN       → Run a uCode script"
      echo "   TREE      → Generate file tree"
      echo "   LIST      → List uCode folders"
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
      echo "   DEBUG     → Show diagnostics"
      echo ""
      ;;
    "") ;;
    *) echo "❓ Unknown command '$cmd'. Type HELP for list of commands." ;;
  esac
done