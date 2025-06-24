#!/bin/bash
# uDOS Dashboard Beta v1.6 — Combines static blocks + live memory stats

UDOSE_HOME="${UDOSE_HOME:-$HOME/uDOS}"
UROOT="$UDOSE_HOME"   # Base directory

bash "$UROOT/scripts/check-setup.sh" >/dev/null
UMEMORY="$UROOT/uMemory"
UKNOWLEDGE="$UROOT/uKnowledge"
LOG_DIR="$UMEMORY/logs"
ULOG=$(ls -1t "$LOG_DIR"/moves-*.md 2>/dev/null | head -n 1)
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
# HEALTH
printf "┌───────────── ✅ Health Stats ──────────────────────────────────────────────┐\n"
printf "│ 🎯 Moves: 0   🚀 Missions: 1   📌 Milestones: 1   📝 Drafts: 2                  │\n"
printf "│ 🏛️ Rooms: 0   ⏱️ Uptime: Unavailable   💾 RAM: 396MB / 7838MB   💽 Space: 49%%   │\n"
printf "│ 🧭 LastMission: N/A                                                          │\n"
printf "└────────────────────────────────────────────────────────────────────────────┘\n"

# Footer
SHARING=$(grep -i '^Sharing:' "$UMEMORY/state/instance.md" 2>/dev/null | cut -d':' -f2- | xargs)
SHARING=$(echo -n "$SHARING" | sed 's/[[:space:]]*$//')
LIFESPAN=$(grep -i '^Lifespan:' "$UMEMORY/state/instance.md" 2>/dev/null | cut -d':' -f2- | xargs)
LIFESPAN=$(echo -n "$LIFESPAN" | sed 's/[[:space:]]*$//')
UDOS_VERSION=$(grep -i '^uDOSVersion:' "$UMEMORY/state/instance.md" 2>/dev/null | cut -d':' -f2- | xargs)
UDOS_VERSION=$(echo -n "$UDOS_VERSION" | sed 's/[[:space:]]*$//')
if [[ "$LIFESPAN" == "0" || -z "$LIFESPAN" ]]; then
  MOVES_REMAINING="∞"
else
  MOVES_REMAINING=$(( LIFESPAN * 1000 ))
fi

### ASCII Dashboard (rounded blocks, max 80 chars)
# HEADER
printf "┌───────────────────────────── 🌀 uDOS Beta ────────────────────────────────┐\n"
printf "│ User: %-16s  %s\n" "$USER_NAME" "$DATE_NOW"
printf "│ Location: %-56s│\n" "$LOCATION"
printf "└────────────────────────────────────────────────────────────────────────────┘\n"

# FOCUS
printf "┌───────────── 🔎 Today’s Focus ─────────────────────────────────────────────┐\n"
printf "│ Mission: %-34s│\n" "$ACTIVE_MISSION"
printf "│ Next:    %-34s│\n" "$NEXT_ACTION"
printf "└────────────────────────────────────────────────────────────────────────────┘\n"

# MOVES
printf "┌──────────── 📝 Recent Moves ──────────────────────────────────────────────┐\n"
if [[ -n "$RECENT_MOVES" ]]; then
  while IFS= read -r line; do
    if [[ "$line" =~ ^🌀→ ]]; then
      timestamp=$(echo "$line" | awk -F'|' '{print $1}' | grep -oE '[0-9]{2}:[0-9]{2}:[0-9]{2}\.[0-9]{3}' || echo "--:--:--.---")
      summary=$(echo "$line" | cut -d'|' -f2 | xargs)
      printf "│ 🌀 %-56s %s │\n" "$summary" "$timestamp"
    elif [[ "$line" =~ ^💬← ]]; then
      echo "$line" | grep -q '✅' && emoji="✅" || emoji="💬"
      summary=$(echo "$line" | cut -d'←' -f2- | xargs)
      printf "│ %s %-60s │\n" "$emoji" "$summary"
    else
      printf "│ %-77s │\n" "$line"
    fi
  done <<< "$RECENT_MOVES"
else
  printf "│ %-77s │\n" "No recent moves found."
fi
printf "└────────────────────────────────────────────────────────────────────────────┘\n"

# MAP PEEK
printf "┌───────────── 🗺️  Map Peek ────────────────────────────────────────────────┐\n"
if [[ -n "$MAP_PEEK" ]]; then
  while IFS= read -r line; do
    printf "│ %-42s│\n" "$line"
  done <<< "$MAP_PEEK"
else
  printf "│ %-42s│\n" "No map data available."
fi
printf "└────────────────────────────────────────────────────────────────────────────┘\n"

# TOWER
printf "┌──────────── 🧠 Indexed Rooms ─────────────────────────────────────────────┐\n"
if [[ -n "$TOWER_LIST" ]]; then
  while IFS= read -r room; do
    printf "│ %-42s│\n" "$room"
  done <<< "$TOWER_LIST"
else
  printf "│ %-42s│\n" "No rooms indexed yet."
fi
printf "└────────────────────────────────────────────────────────────────────────────┘\n"

# LEGACY
printf "┌──────────── 🗃️  Legacy Archive ─────────────────────────────────────────────┐\n"
LEGACY_LOGS=$(find "$UMEMORY/legacy" -type f -name 'legacy-*.md' | sort -r | head -n 3)
if [[ -n "$LEGACY_LOGS" ]]; then
  while IFS= read -r file; do
    base=$(basename "$file")
    printf "│ %-77s │\n" "$base"
  done <<< "$LEGACY_LOGS"
else
  printf "│ %-77s │\n" "No legacy logs found."
fi
printf "└────────────────────────────────────────────────────────────────────────────┘\n"

# FOOTER
printf "┌───────────── 🧭 Status & Info ─────────────────────────────────────────────┐\n"
printf "│ Sharing: %-10s  Lifespan: %-6s  Version: %-8s│\n" "${SHARING:-Unknown}" "${LIFESPAN:-Unknown}" "${UDOS_VERSION:-uDOS Beta v0.0.1}"
printf "│ Moves Remaining: %-27s│\n" "$MOVES_REMAINING"
printf "└────────────────────────────────────────────────────────────────────────────┘\n"

echo
echo "🧭 Use 'help' for available commands. Make your next move, Master."
