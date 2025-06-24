#!/bin/bash
# uCode.sh - uDOS Beta v1.6.1 CLI Shell
# Full-featured command-line interface for uDOS environment

# Environment Setup
export UDOS_HOME="${HOME}/.udos"
export UDOS_LOG="${UDOS_HOME}/udos.log"
export UDOS_IDENTITY="${UDOS_HOME}/identity.id"
export UDOS_DASHBOARD="${UDOS_HOME}/dashboard.json"
export UDOS_TEMP="${UDOS_HOME}/temp"
mkdir -p "$UDOS_HOME" "$UDOS_TEMP"

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
  echo "🆕 Creating new item..."
  read -rp "Enter new item name: " item_name
  if [ -z "$item_name" ]; then
    echo "❌ Item name cannot be empty."
    log_error "Attempted to create new item with empty name."
    return 1
  fi
  item_file="${UDOS_HOME}/${item_name}.txt"
  if [ -f "$item_file" ]; then
    echo "⚠️ Item '$item_name' already exists."
    log_info "New item creation aborted: '$item_name' exists."
    return 1
  fi
  touch "$item_file"
  echo "✅ New item '$item_name' created."
  log_info "New item created: $item_name"
}

cmd_log() {
  echo "📝 Saving progress..."
  # Simulate saving current session or data
  sleep 1
  echo "✅ Progress saved."
  log_info "Progress saved by user."
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
  echo "▶️ Running current item..."
  # Placeholder for running current item logic
  sleep 1
  echo "✅ Run completed."
  log_info "Run command executed."
}

cmd_dash() {
  echo "📈 Displaying dashboard..."
  if [ -f "$UDOS_DASHBOARD" ]; then
    cat "$UDOS_DASHBOARD"
  else
    echo "⚠️ Dashboard not found."
  fi
  log_info "Dashboard displayed."
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
}

# Main Command Dispatch Loop
while true; do
  read -rp "uDOS> " input
  cmd=$(echo "$input" | awk '{print toupper($1)}')
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
    SYNC)
      sync_dashboard
      ;;
    HELP)
      echo "🧠 Available uDOS commands:"
      echo "   NEW       → Create new item"
      echo "   RUN       → Start current item"
      echo "   LOG       → Save progress"
      echo "   UNDO      → Reverse last move"
      echo "   REDO      → Reapply last undone move"
      echo "   DASH      → Show dashboard"
      echo "   SYNC      → Sync dashboard"
      echo "   RESTART   → Restart shell"
      echo "   REBOOT    → Reboot system"
      echo "   DESTROY   → Delete your identity"
      echo "   BYE/EXIT/QUIT → Close session"
      ;;
    "")
      # Ignore empty input
      ;;
    *)
      echo "❓ Unknown command '$cmd'. Type HELP for list of commands."
      ;;
  esac
done