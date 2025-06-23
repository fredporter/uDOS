#!/bin/bash
# uDOS Dashboard Beta v1.6 — Combines static blocks + live memory stats

UROOT="$(dirname "$(realpath "$0")")/.."   # One level up from scripts/
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
printf "╔═══════════════════════════[ uDOS STATUS DASHBOARD ]═══════════════════════════╗\n"
printf "║ User: %-32s %s ║\n" "$USER_NAME" "$(date '+%Y-%m-%d %H:%M:%S')"

LOCATION=$(grep -i '^Location:' "$UMEMORY/state/instance.md" 2>/dev/null | cut -d':' -f2- | xargs)
LOCATION=$(echo -n "$LOCATION" | sed 's/[[:space:]]*$//')
[ -z "$LOCATION" ] && LOCATION="Unknown"
printf "║ Location: %-64s║\n" "$LOCATION"

MISSION_FILE="$UMEMORY/state/current_mission.md"
if [[ -f "$MISSION_FILE" ]]; then
  # Try to extract Title: line for mission name
  ACTIVE_MISSION=$(grep -i '^Title:' "$MISSION_FILE" | head -n1 | cut -d':' -f2- | xargs)
  ACTIVE_MISSION=$(echo -n "$ACTIVE_MISSION" | sed 's/[[:space:]]*$//')
fi
if [[ -z "$ACTIVE_MISSION" ]]; then
  # Fallback to instance.md Mission:
  ACTIVE_MISSION=$(grep -i '^Mission:' "$UMEMORY/state/instance.md" 2>/dev/null | cut -d':' -f2- | xargs)
  ACTIVE_MISSION=$(echo -n "$ACTIVE_MISSION" | sed 's/[[:space:]]*$//')
fi
[ -z "$ACTIVE_MISSION" ] && ACTIVE_MISSION="(none)"
printf "║ Mission: %-62s║\n" "$ACTIVE_MISSION"
printf "╠═══════════════════════════════════════════════════════════════════════════════╣\n"

# Today’s Focus Block
echo "║ 🔎 Today’s Focus                                                              ║"
echo "║ Suggested Move: Run 'log_mission.sh' to begin your next journey               ║"
echo "║ Region Pointer: /vault/crypt                                                  ║"
echo "╠═══════════════════════════════════════════════════════════════════════════════╣"

# Recent Moves
echo "║ 📝 Recent Moves                                                               ║"
if [[ -f "$ULOG" ]]; then
  tail -n 100 "$ULOG" | grep -v '^\[STATS\]' | tail -n 5 | while read -r line; do
    printf "║ %s%-74s║\n" "" "$line"
  done
else
  echo "║ No recent moves found.                                                        ║"
fi
echo "╠═══════════════════════════════════════════════════════════════════════════════╣"

# Map Peek Block
echo "║ 🗺️  Map Peek                                                                   ║"
if [[ -f "$REGION" ]]; then
  while read -r line; do
    printf "║ %s%-74s║\n" "" "$line"
  done < "$REGION"
else
  echo "║ No map data available.                                                        ║"
fi
echo "╠═══════════════════════════════════════════════════════════════════════════════╣"

# Tower Snapshot (Knowledge Rooms)
echo "║ 🧠 Tower of Knowledge                                                         ║"
if [[ -d "$ROOMS_DIR" ]]; then
  find "$ROOMS_DIR" -maxdepth 1 -type f -name '*.md' | sort | head -n 5 | while read -r room; do
    room_name=$(basename "$room")
    printf "║ - %s%-70s║\n" "" "$room_name"
  done
else
  echo "║ No rooms indexed yet.                                                         ║"
fi
echo "╠═══════════════════════════════════════════════════════════════════════════════╣"
echo ""

# Health Check Block (Live Stats)
echo "║ ✅ Health Check                                                               ║"
if [[ -f "$ULOG" ]]; then
  stats_found=0
  grep '^\[STATS\]' "$ULOG" | while read -r stat; do
    stats_found=1
    # Remove the [STATS] prefix for cleaner display
    stat_line=${stat#\[STATS\] }
    printf "║ %s%-74s║\n" "" "$stat_line"
  done
  if [[ $stats_found -eq 0 ]]; then
    echo "║ No system stats found.                                                        ║"
  fi
else
  echo "║ No system stats found.                                                        ║"
fi

SHARING=$(grep -i '^Sharing:' "$UMEMORY/state/instance.md" 2>/dev/null | cut -d':' -f2- | xargs)
SHARING=$(echo -n "$SHARING" | sed 's/[[:space:]]*$//')
LIFESPAN=$(grep -i '^Lifespan:' "$UMEMORY/state/instance.md" 2>/dev/null | cut -d':' -f2- | xargs)
LIFESPAN=$(echo -n "$LIFESPAN" | sed 's/[[:space:]]*$//')
UDOS_VERSION=$(grep -i '^uDOSVersion:' "$UMEMORY/state/instance.md" 2>/dev/null | cut -d':' -f2- | xargs)
UDOS_VERSION=$(echo -n "$UDOS_VERSION" | sed 's/[[:space:]]*$//')

printf "║ Sharing: %-65s║\n" "${SHARING:-Unknown}"
printf "║ Lifespan: %-64s║\n" "${LIFESPAN:-Unknown}"

if [[ "$LIFESPAN" == "0" ]]; then
  MOVES_REMAINING="∞"
else
  MOVES_REMAINING=$(( LIFESPAN * 1000 ))
fi
printf "║ Moves Remaining: %-57s║\n" "$MOVES_REMAINING"

printf "║ uDOS Version: %-61s║\n" "${UDOS_VERSION:-Unknown}"

echo "╚═══════════════════════════════════════════════════════════════════════════════╝"
echo ""
echo "🧭 Use 'help' for available commands. Make your next move, Master."