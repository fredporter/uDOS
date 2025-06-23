#!/bin/bash

# === uDOS Move 012: Generate Dashboard Stats into uMemory (Enhanced) ===

UROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
UMEMORY="$UROOT/uMemory"
UKNOWLEDGE="$UROOT/uKnowledge"
STATE="$UMEMORY/state"
LOG_DIR="$UMEMORY/logs"
MOVE_LOGS="$LOG_DIR/moves"
DATESTAMP=$(date '+%Y-%m-%d')

mkdir -p "$LOG_DIR"

# ─────────────────────────────────────────────────────────────────────────────
# Count markdown files in known categories
# ─────────────────────────────────────────────────────────────────────────────
count_files() {
  find "$1" -type f -name '*.md' 2>/dev/null | wc -l | tr -d ' '
}

TOTAL_MOVES=$(count_files "$MOVE_LOGS")
TOTAL_MISSIONS=$(count_files "$UMEMORY/missions")
TOTAL_MILESTONES=$(count_files "$UMEMORY/milestones")
TOTAL_LEGACY=$(count_files "$UMEMORY/legacy")
SANDBOX_DRAFTS=$(count_files "$UROOT/sandbox")

# ─────────────────────────────────────────────────────────────────────────────
# Uptime, RAM and Host Metrics
# ─────────────────────────────────────────────────────────────────────────────
UPTIME=$(uptime -p 2>/dev/null || echo "Unavailable")
MEMORY=$(free -m 2>/dev/null | awk '/Mem:/ { print $3 "MB used / " $2 "MB total" }' || echo "Unavailable")
HOSTNAME=$(hostname)
OS_VERSION=$(uname -a)

# ─────────────────────────────────────────────────────────────────────────────
# User State Info: lifespan, instance ID
# ─────────────────────────────────────────────────────────────────────────────
USER_FILE="$STATE/user.md"
LIFESPAN="n/a"
INSTANCE_ID="n/a"

if [ -f "$USER_FILE" ]; then
  LIFESPAN=$(sed -n 's/\*\*Lifespan\*\*: //p' "$USER_FILE")
  INSTANCE_ID=$(sed -n 's/\*\*Instance ID\*\*: //p' "$USER_FILE")
fi

# ─────────────────────────────────────────────────────────────────────────────
# Append stats summary to today's move log
# ─────────────────────────────────────────────────────────────────────────────
DAILY_MOVE_LOG="$LOG_DIR/moves-${DATESTAMP}.md"

echo "[STATS] Moves: $TOTAL_MOVES | Missions: $TOTAL_MISSIONS | Milestones: $TOTAL_MILESTONES | Drafts: $SANDBOX_DRAFTS | Uptime: $UPTIME | RAM: $MEMORY" >> "$DAILY_MOVE_LOG"

echo "✅ System stats appended to: $DAILY_MOVE_LOG"