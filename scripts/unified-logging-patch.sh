#!/bin/bash

# === PATCH: uOS Unified Logging & Session Tracking ===

UOS_ROOT="$HOME/uOS"
MEMORY_DIR="$UOS_ROOT/uMemory"
LOG_DIR="$MEMORY_DIR/logs"
STATE_DIR="$MEMORY_DIR/state"
TEMPLATE_DIR="$UOS_ROOT/templates"
SCRIPT_DIR="$UOS_ROOT/scripts"

# 1. Rename existing ulog to dashlog
if [ -f "$LOG_DIR/ulog-2025-06-14.md" ]; then
  mv "$LOG_DIR/ulog-2025-06-14.md" "$LOG_DIR/dashlog-2025-06-14.md"
  echo "✅ Renamed ulog-2025-06-14.md → dashlog-2025-06-14.md"
fi

# 2. Ensure all required folders exist
mkdir -p "$LOG_DIR/moves"
mkdir -p "$MEMORY_DIR/missions"
mkdir -p "$MEMORY_DIR/milestones"
mkdir -p "$MEMORY_DIR/legacy"
mkdir -p "$STATE_DIR"

# 3. Create today's dashlog if not exists
today=$(date +%F)
dashlog="$LOG_DIR/dashlog-$today.md"
if [ ! -f "$dashlog" ]; then
  echo "# 🧭 uOS Dashlog – $today" > "$dashlog"
  echo "Session started at $(date)" >> "$dashlog"
  echo "✅ Created new session dashlog: $dashlog"
fi

# 4. Create state files if missing
touch "$STATE_DIR/current_mission.txt"
touch "$STATE_DIR/current_milestone.txt"
touch "$STATE_DIR/current_legacy.txt"

echo "✅ Verified mission/milestone/legacy state files."

# 5. Update uCode.sh with unified logging logic (pseudocode only - manual patch required)

cat <<'INFO'

🧠 NEXT STEP: In scripts/uCode.sh, update main CLI loop:
- Log each valid command to both:
    → dashlog (summary)
    → logs/moves/<timestamp>.md (detailed)
- Auto-create dashlog on start if missing
- Log move ID, time, command, output
- Use log_move function to:
    - Append move .md
    - Add entry to dashlog
    - Update stats if available

✏️ Suggested move file:
  uMemory/logs/moves/2025-06-21-move-<epoch>.md

📄 dashlog format:
  - [Time] Move: <cmd>
  - Links to per-move logs

INFO

echo "🚀 Unified logging patch complete. Time to update uCode.sh manually!"
