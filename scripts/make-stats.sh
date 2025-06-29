#!/bin/bash

# make-stats.sh — Generate dashboard stats into uMemory (Enhanced)

UHOME="${HOME}/uDOS"
UROOT="$UHOME"
UMEMORY="$UROOT/uMemory"
UKNOWLEDGE="$UROOT/uKnowledge"
STATE="$UMEMORY/state"
LOG_DIR="$UMEMORY/logs"
MOVE_LOGS="$LOG_DIR/moves"
DATESTAMP=$(date '+%Y-%m-%d')

HEADLESS="${UCODE_HEADLESS:-false}"

mkdir -p "$LOG_DIR"

# ─────────────────────────────────────────────────────────────────────────────
# Count markdown files in known categories
# ─────────────────────────────────────────────────────────────────────────────
count_files() {
  find "$1" -type f -name '*.md' 2>/dev/null | wc -l | tr -d ' '
}

TOTAL_MOVES=$(grep -h '^\[' "$LOG_DIR"/move-log-*.md 2>/dev/null | wc -l)
TOTAL_MISSIONS=$(count_files "$UMEMORY/missions")
TOTAL_MILESTONES=$(count_files "$UMEMORY/milestones")
TOTAL_LEGACY=$(count_files "$UMEMORY/legacy")
SANDBOX_DRAFTS=$(count_files "$UROOT/sandbox")
TOTAL_ROOMS=$(count_files "$UKNOWLEDGE/rooms")

# ─────────────────────────────────────────────────────────────────────────────
# Uptime, RAM and Host Metrics
# ─────────────────────────────────────────────────────────────────────────────
UPTIME=$(uptime -p 2>/dev/null || echo "Unavailable")
MEMORY=$(free -m 2>/dev/null | awk '/Mem:/ { print $3 "MB used / " $2 "MB total" }' || echo "Unavailable")
HOSTNAME=$(hostname)
DISK_USAGE=$(df -h "$UROOT" | awk 'NR==2 {print $5 " used of " $2}')

VERSION_FILE="$UROOT/sandbox/version.md"
UDOS_VERSION=$(cat "$VERSION_FILE" 2>/dev/null || echo "Unknown Version")

# ─────────────────────────────────────────────────────────────────────────────
# User State Info: lifespan
# ─────────────────────────────────────────────────────────────────────────────
USER_FILE="$STATE/instance.md"
LIFESPAN="n/a"

if [ -f "$USER_FILE" ]; then
  LIFESPAN=$(grep -i '^Lifespan:' "$USER_FILE" | cut -d':' -f2- | xargs)
fi

# ─────────────────────────────────────────────────────────────────────────────
# Extract latest mission title
# ─────────────────────────────────────────────────────────────────────────────
LAST_MISSION=$(find "$UMEMORY/missions" -name '*.md' -type f -print0 | xargs -0 ls -t 2>/dev/null | head -n 1 | xargs grep -m 1 '^# ' | cut -d'#' -f2- | xargs)

# ─────────────────────────────────────────────────────────────────────────────
# Append stats summary to today's move log
# ─────────────────────────────────────────────────────────────────────────────
DAILY_MOVE_LOG="$LOG_DIR/move-log-${DATESTAMP}.md"

mkdir -p "$(dirname "$DAILY_MOVE_LOG")"
touch "$DAILY_MOVE_LOG"

summary="Moves: $TOTAL_MOVES | Missions: $TOTAL_MISSIONS | Milestones: $TOTAL_MILESTONES | Rooms: $TOTAL_ROOMS | Drafts: $SANDBOX_DRAFTS | Uptime: $UPTIME | RAM: $MEMORY | Space: $DISK_USAGE | Version: $UDOS_VERSION | LastMission: $LAST_MISSION"
echo "[STATS] $summary" >> "$DAILY_MOVE_LOG"

if [[ "$HEADLESS" != "true" ]]; then
  echo "[$(date +%H:%M:%S)] → make-stats summary written" >> "$UHOME/sandbox/dash-log-$DATESTAMP.md"
fi

echo "✅ System stats appended to: $DAILY_MOVE_LOG"