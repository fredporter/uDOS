#!/bin/bash
# uDOS Dashboard Beta v1.6 — Combines static blocks + live memory stats

UHOME="${HOME}/uDOS"
UROOT="$UHOME"   # Base directory

bash "$UROOT/scripts/check-setup.sh" >/dev/null
UMEMORY="$UROOT/uMemory"
UKNOWLEDGE="$UROOT/uKnowledge"
LOG_DIR="$UMEMORY/logs"
ULOG=$(ls -1t "$LOG_DIR"/moves-log-*.md 2>/dev/null | head -n 1)
REGION="$UKNOWLEDGE/map/current_region.txt"
ROOMS_DIR="$UKNOWLEDGE/rooms"
RECENT_MOVES_DIR="$UMEMORY/logs/moves"

# Header
clear
USER_FILE="$UROOT/sandbox/user.md"
if [[ -f "$USER_FILE" && -s "$USER_FILE" ]]; then
  USER_NAME=$(grep -i '^Username:' "$USER_FILE" | head -n1 | cut -d':' -f2- | xargs)
  USER_NAME=$(echo -n "$USER_NAME" | sed 's/[[:space:]]*$//')
  if [[ -z "$USER_NAME" ]]; then
    USER_NAME="(unknown)"
  fi
else
  USER_NAME="(unknown)"
fi
# DEBUG: Uncomment to debug user file
# echo "DEBUG: USER_FILE contents:"; cat "$USER_FILE"
# echo "DEBUG: Parsed USER_NAME: $USER_NAME"
### Gather info for blocks
DATE_NOW="$(date '+%Y-%m-%d %H:%M:%S')"
LOCATION=$(grep -i '^Location:' "$UMEMORY/state/instance.md" 2>/dev/null | cut -d':' -f2- | xargs)
LOCATION=$(echo -n "$LOCATION" | sed 's/[[:space:]]*$//')
[ -z "$LOCATION" ] && LOCATION="Unknown"
MISSION_FILE="$UMEMORY/state/current_mission.md"
if [[ -f "$MISSION_FILE" ]]; then
  ACTIVE_MISSION=$(grep -i '^Title:' "$MISSION_FILE" | head -n1 | cut -d':' -f2- | xargs)
  ACTIVE_MISSION=$(echo -n "$ACTIVE_MISSION" | sed 's/[[:space:]]*$//')
fi
if [[ -z "$ACTIVE_MISSION" ]]; then
  ACTIVE_MISSION=$(grep -i '^Mission:' "$UMEMORY/state/instance.md" 2>/dev/null | cut -d':' -f2- | xargs)
  ACTIVE_MISSION=$(echo -n "$ACTIVE_MISSION" | sed 's/[[:space:]]*$//')
fi
[ -z "$ACTIVE_MISSION" ] && ACTIVE_MISSION="(none)"

# Next action (first actionable line from MOVE_LOG or fallback)
NEXT_ACTION="Type 'new mission' or 'log mission' to begin"

# Recent Moves
if [[ -f "$ULOG" ]]; then
  RECENT_MOVES=$(tail -n 100 "$ULOG" | grep -v '^\[STATS\]' | tail -n 5)
else
  RECENT_MOVES="No recent moves found."
fi

# Map Peek
if [[ -f "$REGION" ]]; then
  MAP_PEEK=$(cat "$REGION")
else
  MAP_PEEK="No map data available."
fi

# Tower
if [[ -d "$ROOMS_DIR" ]]; then
  TOWER_LIST=$(find "$ROOMS_DIR" -maxdepth 1 -type f -name '*.md' | sort | head -n 5 | xargs -n1 basename)
else
  TOWER_LIST=""
fi

# Health (from [STATS] lines)
render_template() {
  local file="$1"
  while IFS= read -r line; do
    eval "echo \"${line//\{\{/\${}\""
  done < "$file"
}

bash "$UROOT/scripts/make-dash.sh"
cat "$UROOT/uMemory/rendered/dash-rendered.md"

echo
echo "🧭 Use 'help' for available commands. Make your next move, Master."
