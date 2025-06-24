#!/bin/bash
# check_permissions.sh — Validate permissions for uDOS directories and scripts

UDOSE_HOME="/root/uDOS"

LOG_FILE="$UDOSE_HOME/uMemory/logs/permissions-$(date +%Y-%m-%d).log"
TARGET_DIRS=("$UDOSE_HOME/launcher" "$UDOSE_HOME/scripts")
SYSTEM_CMD="$UDOSE_HOME/scripts/system-command.sh"

mkdir -p "$(dirname "$LOG_FILE")"

{
  echo "🔍 Checking permissions for uDOS..."

  for dir in "${TARGET_DIRS[@]}"; do
    if [ -d "$dir" ]; then
      echo "Checking directory: $dir"
      perm=$(stat -c "%a" "$dir")
      owner=$(stat -c "%U" "$dir")
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
    perm=$(stat -c "%a" "$SYSTEM_CMD")
    owner=$(stat -c "%U" "$SYSTEM_CMD")
    echo "Permissions: $perm, Owner: $owner"
    if [ "$perm" -ge 700 ] && [ "$owner" == "$(whoami)" ]; then
      echo "✅ $SYSTEM_CMD permissions are correctly set."
    else
      echo "❌ $SYSTEM_CMD permissions are NOT correctly set."
    fi
  else
    echo "❌ System command script $SYSTEM_CMD does not exist."
  fi

  echo "🧪 Permission check complete. Log saved to $LOG_FILE"
} | tee -a "$LOG_FILE"