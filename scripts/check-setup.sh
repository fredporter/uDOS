#!/bin/bash
# check_permissions.sh — Validate permissions for uDOS directories and scripts

LOG_FILE="$HOME/uDOS/logs/permission-check.log"
TARGET_DIRS=("$HOME/uDOS/launcher" "$HOME/uDOS/scripts")
SYSTEM_CMD="$HOME/uDOS/scripts/system-command.sh"

mkdir -p "$HOME/uDOS/logs"

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
done | tee -a "$LOG_FILE"

if [ -f "$SYSTEM_CMD" ]; then
  perm=$(stat -c "%a" "$SYSTEM_CMD")
  owner=$(stat -c "%U" "$SYSTEM_CMD")
  echo "Checking system command script: $SYSTEM_CMD"
  echo "Permissions: $perm, Owner: $owner"
  if [ "$perm" -ge 700 ] && [ "$owner" == "$(whoami)" ]; then
    echo "✅ $SYSTEM_CMD permissions are correctly set."
  else
    echo "❌ $SYSTEM_CMD permissions are NOT correctly set."
  fi
else
  echo "❌ System command script $SYSTEM_CMD does not exist."
fi | tee -a "$LOG_FILE"

echo "🧪 Permission check complete. Log saved to $LOG_FILE"