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
echo "╔═══════════════════════════[ uOS STATUS DASHBOARD ]═══════════════════════════╗"
echo "║ User: Master                           $(date '+%Y-%m-%d %H:%M:%S')                ║"
echo "║ Location: The Crypt                                                           ║"
echo "║ Active Mission: Activate uCode Interface                                      ║"
echo "╠═══════════════════════════════════════════════════════════════════════════════╣"

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
    # Extract timestamp from filename
    move_date=$(basename "$move_file" | cut -d'-' -f1-3 | tr '-' '/')
    
    # Extract the Move name from inside the file
    move_name=$(grep -i '^Move:' "$move_file" | cut -d':' -f2- | xargs)
    
    # Fallback if no move name found
    if [[ -z "$move_name" ]]; then
      move_name="[unnamed move]"
    fi
    
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
