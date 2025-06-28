#!/bin/bash
# check-permissions.sh – Auto-fix permissions for uDOS scripts
# uDOS by Master & Otter 🦦

UHOME="${HOME}/uDOS"

TARGET_DIRS=("$UHOME/launcher" "$UHOME/scripts" "$UHOME/uTemplate" "$UHOME/sandbox" "$UHOME/uMemory" "$UHOME/uKnowledge")

fixed_count=0

for dir in "${TARGET_DIRS[@]}"; do
  if [ -d "$dir" ]; then
    find "$dir" -type f \( -name "*.sh" -o -name "*.command" \) | while read -r file; do
      if [ ! -x "$file" ]; then
        chmod +x "$file"
        fixed_count=$((fixed_count + 1))
      fi
    done
  fi
done

echo "🔧 Permission audit complete: $fixed_count file(s) fixed."

echo "[$(date +%H:%M:%S)] → check-permissions complete" >> "$UHOME/sandbox/dash-log-$(date +%Y-%m-%d).md"

echo "[$(date +%H:%M:%S)] → check-permissions → $fixed_count files fixed" >> "$UHOME/uMemory/logs/move-log-$(date +%Y-%m-%d).md"
