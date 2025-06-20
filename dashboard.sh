#!/bin/bash

# === uOS Dashboard View ===

LOG_DIR="$HOME/uOS/uMemory/logs"
ULOG=$(ls -1t "$LOG_DIR"/ulog-*.md 2>/dev/null | head -n 1)

clear
cat << "EOF"
+======================================+
|          🌿  uOS DASHBOARD           |
+======================================+
EOF

NOW=$(date '+%A, %d %B %Y — %H:%M:%S')
echo "📅 $NOW"
echo ""

if [[ -f "$ULOG" ]]; then
  cat "$ULOG"
else
  echo "⚠️ No daily stats found. Run generate_stats.sh."
fi

cat << "EOF"

+--------------------------------------+
|  💾 uMemory is alive and growing...  |
|  🧠 Every Move builds your legacy.   |
+--------------------------------------+
EOF