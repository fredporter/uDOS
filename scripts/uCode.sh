#!/bin/bash
# check_permissions.sh — Validate and fix permissions for uDOS scripts and files

LOG_FILE="$HOME/uDOS/uMemory/logs/permissions-$(date +%Y-%m-%d).log"
mkdir -p "$(dirname "$LOG_FILE")"

TARGET_DIRS=(
  "$HOME/uDOS/scripts"
  "$HOME/uDOS/uMemory"
  "$HOME/uDOS/uKnowledge"
  "$HOME/uDOS/sandbox"
)

echo "🔍 Starting permissions check at $(date)" | tee -a "$LOG_FILE"

for DIR in "${TARGET_DIRS[@]}"; do
  if [[ -d "$DIR" ]]; then
    find "$DIR" -type f ! -perm /u+x | while read -r FILE; do
      # Skip system-command.sh here to handle explicitly later
      if [[ "$(basename "$FILE")" == "system-command.sh" ]]; then
        continue
      fi
      chmod +x "$FILE"
      echo "✅ Fixed permissions: $FILE" | tee -a "$LOG_FILE"
    done
  else
    echo "⚠️ Directory not found: $DIR" | tee -a "$LOG_FILE"
  fi
done

# Explicit check for system-command.sh
SYSTEM_CMD="$HOME/uDOS/scripts/system-command.sh"
if [[ -f "$SYSTEM_CMD" && ! -x "$SYSTEM_CMD" ]]; then
  chmod +x "$SYSTEM_CMD"
  echo "✅ Fixed permissions: $SYSTEM_CMD" | tee -a "$LOG_FILE"
fi

echo "✅ Permissions check completed at $(date)" | tee -a "$LOG_FILE"