#!/bin/bash
# check_permissions.sh – Auto-fix permissions for uDOS scripts
# uDOS by Master & Otter 🦦

LOG_FILE="$HOME/uDOS/uMemory/logs/permissions-$(date +%Y-%m-%d).log"
TARGET_DIRS=("$HOME/uDOS/launcher" "$HOME/uDOS/scripts")

mkdir -p "$(dirname "$LOG_FILE")"

echo "🔐 Checking uDOS script permissions..." | tee -a "$LOG_FILE"
echo "Timestamp: $(date)" >> "$LOG_FILE"

for dir in "${TARGET_DIRS[@]}"; do
  if [ -d "$dir" ]; then
    echo "📂 Scanning $dir..." >> "$LOG_FILE"
    find "$dir" -type f \( -name "*.sh" -o -name "*.command" \) | while read -r file; do
      if [ ! -x "$file" ]; then
        chmod +x "$file"
        echo "✅ Fixed permissions: $file" | tee -a "$LOG_FILE"
      else
        echo "✔️ OK: $file" >> "$LOG_FILE"
      fi
    done
  else
    echo "⚠️ Directory not found: $dir" >> "$LOG_FILE"
  fi
done

echo "✅ Permission check complete." | tee -a "$LOG_FILE"
