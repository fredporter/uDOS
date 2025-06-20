#!/bin/bash

# === uOS Move 012 (Revised): Generate Dashboard Stats into uMemory ===

UMEMORY="$HOME/uOS/uMemory"
LOG_DIR="$UMEMORY/logs"
DATESTAMP=$(date '+%Y-%m-%d')
ULOG="$LOG_DIR/ulog-${DATESTAMP}.md"

mkdir -p "$LOG_DIR"

# Count .md files in each category
count_files() {
  find "$1" -type f -name '*.md' | wc -l | tr -d ' '
}

TOTAL_MOVES=$(count_files "$UMEMORY/logs/moves")
TOTAL_MISSIONS=$(count_files "$UMEMORY/missions")
TOTAL_MILESTONES=$(count_files "$UMEMORY/milestones")
TOTAL_LEGACY=$(count_files "$UMEMORY/legacy")
SANDBOX_DRAFTS=$(count_files "$HOME/uOS/sandbox")

# Overwrite or create today's ulog
cat <<EOF > "$ULOG"
### uOS Daily Summary — $DATESTAMP

🎮 Moves:         $TOTAL_MOVES
📌 Missions:      $TOTAL_MISSIONS
🧭 Milestones:    $TOTAL_MILESTONES
🪦 Legacy:        $TOTAL_LEGACY
🧪 Drafts:        $SANDBOX_DRAFTS

EOF

cat "$ULOG"