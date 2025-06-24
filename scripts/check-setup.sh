#!/bin/bash
# check-setup.sh — Validate permissions for uDOS directories and scripts

UDOSE_HOME="/root/uDOS"

LOG_FILE="$UDOSE_HOME/uMemory/logs/permissions-$(date +%Y-%m-%d).log"
TARGET_DIRS=(
  "$UDOSE_HOME/scripts"
  "$UDOSE_HOME/uTemplate"
  "$UDOSE_HOME/sandbox"
  "$UDOSE_HOME/uMemory"
  "$UDOSE_HOME/uMemory/logs"
)
SYSTEM_CMD="$UDOSE_HOME/scripts/command.sh"

mkdir -p "$(dirname "$LOG_FILE")"

get_stat() {
  # Try GNU stat format first, fallback to BSD/macOS stat
  if stat -c "%a %U" "$1" &>/dev/null; then
    stat -c "%a %U" "$1"
  else
    stat -f "%Lp %Su" "$1"
  fi
}

{
  echo "🔍 Checking permissions for uDOS..."

  for dir in "${TARGET_DIRS[@]}"; do
    if [ -d "$dir" ]; then
      echo "Checking directory: $dir"
      read -r perm owner <<< "$(get_stat "$dir")"
      echo "Permissions: $perm, Owner: $owner"
      if [ "$perm" -ge 700 ] && [ "$owner" == "$(whoami)" ]; then
        echo "✅ $dir permissions are correctly set."
      else
        echo "❌ $dir permissions are NOT correctly set."
      fi
    else
      echo "❌ Directory $dir does not exist."
    fi
  done

  if [ -f "$SYSTEM_CMD" ]; then
    echo "Checking system command script: $SYSTEM_CMD"
    read -r perm owner <<< "$(get_stat "$SYSTEM_CMD")"
    echo "Permissions: $perm, Owner: $owner"
    if [ "$perm" -ge 700 ] && [ "$owner" == "$(whoami)" ]; then
      echo "✅ $SYSTEM_CMD permissions are correctly set."
    else
      echo "❌ $SYSTEM_CMD permissions are NOT correctly set."
      echo "🔧 Fixing permissions for $SYSTEM_CMD..."
      chmod 700 "$SYSTEM_CMD"
      echo "Permissions corrected to 700."
    fi
  else
    echo "❌ System command script $SYSTEM_CMD does not exist."
  fi

  echo "🧪 Permission check complete. Log saved to $LOG_FILE"
} | tee -a "$LOG_FILE"