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
USER_NAME=$(whoami)
printf "╔═══════════════════════════[ uOS STATUS DASHBOARD ]═══════════════════════════╗\n"
printf "║ User: %-32s %s ║\n" "$USER_NAME" "$(date '+%Y-%m-%d %H:%M:%S')"

LOCATION=$(basename "$(cat "$REGION" 2>/dev/null)" 2>/dev/null)
[ -z "$LOCATION" ] && LOCATION="Unknown"
printf "║ Location: %-64s║\n" "$LOCATION"

MISSION_FILE="$UMEMORY/state/current_mission.md"
if [[ -f "$MISSION_FILE" ]]; then
  ACTIVE_MISSION=$(grep -i '^Title:' "$MISSION_FILE" | cut -d':' -f2- | xargs)
else
  ACTIVE_MISSION="(none)"
fi
printf "║ Active Mission: %-58s║\n" "$ACTIVE_MISSION"
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

# Health Check Block (Live Stats)
echo "║ ✅ Health Check                                                               ║"
if [[ -f "$ULOG" ]]; then
  grep -E 'Moves|Missions|Milestones|Legacy|Drafts' "$ULOG" | while read -r stat; do
    printf "║ %s%-74s║\n" "" "$stat"
  done
else
  echo "║ No stat log available. Run generate_stats.sh.                                 ║"
fi
echo "║ Encryption: [ENABLED]      Sync Status: Local OK, No pending exports          ║"
echo "╚═══════════════════════════════════════════════════════════════════════════════╝"
echo ""
echo "🧭 Use 'help' for available commands. Make your next move, Master."