#!/bin/bash
# check-permissions.sh – Auto-fix permissions for uDOS scripts
# uDOS by Master & Otter 🦦

UHOME="${HOME}/uDOS"

mkdir -p "$UHOME/sandbox"
mkdir -p "$UHOME/uMemory/logs"

TARGET_DIRS=("$UHOME/launcher" "$UHOME/scripts" "$UHOME/uTemplate" "$UHOME/sandbox" "$UHOME/uMemory" "$UHOME/uKnowledge")

fixed_count=0

for dir in "${TARGET_DIRS[@]}"; do
  if [ -d "$dir" ]; then
    for file in $(find "$dir" -type f \( -name "*.sh" -o -name "*.command" \)); do
      if [ ! -x "$file" ]; then
        chmod +x "$file"
        fixed_count=$((fixed_count + 1))
      fi
    done
  fi
done

echo "🔧 Permission audit complete: $fixed_count file(s) fixed."

echo "[$(date +%H:%M:%S)] → check-permissions complete" >> "$UHOME/sandbox/dash-log-$(date +%Y-%m-%d).md"
