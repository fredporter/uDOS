#!/bin/bash

# === uOS Move 012: Generate Dashboard Stats into uMemory (Enhanced) ===

UROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
UMEMORY="$UROOT/uMemory"
UKNOWLEDGE="$UROOT/uKnowledge"
STATE="$UMEMORY/state"
LOG_DIR="$UMEMORY/logs"
MOVE_LOGS="$LOG_DIR/moves"
DATESTAMP=$(date '+%Y-%m-%d')
ULOG="$LOG_DIR/ulog-${DATESTAMP}.md"

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
# Session Info: Number of moves today (from today’s session)
# ─────────────────────────────────────────────────────────────────────────────
SESSION_FILE="$LOG_DIR/session-${DATESTAMP}.md"
MOVES_TODAY=$(grep -c 'Move:' "$SESSION_FILE" 2>/dev/null || echo "0")

# ─────────────────────────────────────────────────────────────────────────────
# Write to today's Unified Log (ulog)
# ─────────────────────────────────────────────────────────────────────────────
cat <<EOF > "$ULOG"
### 🧠 uOS System Summary — $DATESTAMP

🔢 Instance ID:  $INSTANCE_ID
🔐 Lifespan:     $LIFESPAN
🧭 Hostname:     $HOSTNAME
🕰️  Uptime:      $UPTIME
💾 Memory:       $MEMORY
🖥️  OS Version:  $OS_VERSION

🎮 Total Moves:        $TOTAL_MOVES
📌 Missions Logged:    $TOTAL_MISSIONS
📍 Milestones:         $TOTAL_MILESTONES
🪦 Legacy Files:       $TOTAL_LEGACY
🧪 Drafts in Sandbox:  $SANDBOX_DRAFTS
📑 Moves Today:        $MOVES_TODAY

EOF

echo "✅ System stats updated: $ULOG"
cat "$ULOG"