#!/bin/bash
# uOS Dashboard v1.1 — Combines static blocks + live memory stats

UROOT="$(dirname "$(realpath "$0")")/.."   # One level up from scripts/
UMEMORY="$UROOT/uMemory"
UKNOWLEDGE="$UROOT/uKnowledge"
LOG_DIR="$UMEMORY/logs"
ULOG=$(ls -1t "$LOG_DIR"/ulog-*.md 2>/dev/null | head -n 1)
REGION="$UKNOWLEDGE/map/current_region.txt"
ROOMS_DIR="$UKNOWLEDGE/rooms"
RECENT_MOVES_DIR="$UMEMORY/logs/moves"

# Header
clear
USER_FILE="$UROOT/sandbox/user.md"
if [[ -f "$USER_FILE" && -s "$USER_FILE" ]]; then
  USER_NAME=$(grep -i '^Username:' "$USER_FILE" | head -n1 | cut -d':' -f2- | xargs)
  if [[ -z "$USER_NAME" ]]; then
    USER_NAME="(unknown)"
  fi
else
  USER_NAME="(unknown)"
fi
# DEBUG: Uncomment to debug user file
# echo "DEBUG: USER_FILE contents:"; cat "$USER_FILE"
# echo "DEBUG: Parsed USER_NAME: $USER_NAME"
printf "╔═══════════════════════════[ uOS STATUS DASHBOARD ]═══════════════════════════╗\n"
printf "║ User: %-32s %s ║\n" "$USER_NAME" "$(date '+%Y-%m-%d %H:%M:%S')"

LOCATION=$(grep -i '^Location:' "$UMEMORY/state/instance.md" 2>/dev/null | cut -d':' -f2- | xargs)
[ -z "$LOCATION" ] && LOCATION="Unknown"
printf "║ Location: %-64s║\n" "$LOCATION"

MISSION_FILE="$UMEMORY/state/current_mission.md"
if [[ -f "$MISSION_FILE" ]]; then
  # Try to extract Title: line for mission name
  ACTIVE_MISSION=$(grep -i '^Title:' "$MISSION_FILE" | head -n1 | cut -d':' -f2- | xargs)
fi
if [[ -z "$ACTIVE_MISSION" ]]; then
  # Fallback to instance.md Mission:
  ACTIVE_MISSION=$(grep -i '^Mission:' "$UMEMORY/state/instance.md" 2>/dev/null | cut -d':' -f2- | xargs)
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
if ls "$RECENT_MOVES_DIR"/*.md &>/dev/null; then
  recent_moves=$(ls -1t "$RECENT_MOVES_DIR"/*.md 2>/dev/null | head -n 5)
  for move_file in $recent_moves; do
    # Extract ISO date from inside file or fallback to filename
    move_date=$(grep -i '^timestamp:' "$move_file" | cut -d'T' -f1 | cut -d':' -f2- | xargs)
    [ -z "$move_date" ] && move_date=$(basename "$move_file" | cut -d'-' -f1-3 | tr '-' '/')

    # Extract command from YAML
    move_name=$(grep -i '^command:' "$move_file" | head -n1 | cut -d':' -f2- | sed 's/^ *//;s/^"//;s/"$//')

    # Fallback if no move name
    [ -z "$move_name" ] && move_name="[unnamed move]"

    printf "║ [%s] Move: %-60s║\n" "$move_date" "$move_name"
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
  ls -1 "$ROOMS_DIR" | head -n 5 | while read -r room; do
    printf "║ - %s%-70s║\n" "" "$room"
  done
else
  echo "║ No rooms indexed yet.                                                         ║"
fi
echo "╠═══════════════════════════════════════════════════════════════════════════════╣"
echo ""

# Health Check Block (Live Stats)
echo "║ ✅ Health Check                                                               ║"
if [[ -f "$ULOG" ]]; then
  grep -E 'Moves|Missions|Milestones|Legacy|Drafts' "$ULOG" | while read -r stat; do
    printf "║ %s%-74s║\n" "" "$stat"
  done
else
  echo "║ No stat log available. Run generate_stats.sh.                                 ║"
fi

SHARING=$(grep -i '^Sharing:' "$UMEMORY/state/instance.md" 2>/dev/null | cut -d':' -f2- | xargs)
LIFESPAN=$(grep -i '^Lifespan:' "$UMEMORY/state/instance.md" 2>/dev/null | cut -d':' -f2- | xargs)
UOS_VERSION=$(grep -i '^uOS Version:' "$UMEMORY/state/instance.md" 2>/dev/null | cut -d':' -f2- | xargs)

printf "║ Sharing: %-65s║\n" "${SHARING:-Unknown}"
printf "║ Lifespan: %-64s║\n" "${LIFESPAN:-Unknown}"

if [[ "$LIFESPAN" == "0" ]]; then
  MOVES_REMAINING="∞"
else
  MOVES_REMAINING=$(( LIFESPAN * 1000 ))
fi
printf "║ Moves Remaining: %-57s║\n" "$MOVES_REMAINING"

printf "║ uOS Version: %-61s║\n" "${UOS_VERSION:-Unknown}"

echo "╚═══════════════════════════════════════════════════════════════════════════════╝"
echo ""
echo "🧭 Use 'help' for available commands. Make your next move, Master."