#!/bin/bash
# check_permissions.sh – Auto-fix permissions for uDOS scripts
# uDOS by Master & Otter 🦦

UDOSE_HOME="/root/uDOS"

LOG_FILE="$UDOSE_HOME/uMemory/logs/permissions-$(date +%Y-%m-%d).log"
TARGET_DIRS=("$UDOSE_HOME/launcher" "$UDOSE_HOME/scripts" "$UDOSE_HOME/uTemplate" "$UDOSE_HOME/sandbox")

mkdir -p "$(dirname "$LOG_FILE")"

fixed_count=0

echo "🔐 Checking uDOS script permissions..." | tee -a "$LOG_FILE"
echo "Timestamp: $(date)" >> "$LOG_FILE"

for dir in "${TARGET_DIRS[@]}"; do
  if [ -d "$dir" ]; then
    echo "📂 Scanning $dir..." >> "$LOG_FILE"
    find "$dir" -type f \( -name "*.sh" -o -name "*.command" \) | while read -r file; do
      if [[ "$file" == "$LOG_FILE" ]]; then continue; fi
      if [ ! -x "$file" ]; then
        chmod +x "$file"
        echo "✅ Fixed permissions: $file" | tee -a "$LOG_FILE"
        fixed_count=$((fixed_count + 1))
      else
        echo "✔️ OK: $file" >> "$LOG_FILE"
      fi
    done
  else
    echo "⚠️ Directory not found: $dir" >> "$LOG_FILE"
  fi
done

echo "✅ Permission check complete." | tee -a "$LOG_FILE"
echo "Total files fixed: $fixed_count" | tee -a "$LOG_FILE"
