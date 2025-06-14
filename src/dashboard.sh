#!/bin/bash
# dashboard.sh - renders the ASCII Dashboard for uOS

# Header
clear
echo "╔═══════════════════════════[ uOS STATUS DASHBOARD ]═══════════════════════════╗"
echo "║ User: Master                           $(date '+%Y-%m-%d %H:%M:%S')                ║"
echo "║ Location: The Crypt                                                           ║"
echo "║ Active Mission: Activate uCode Interface                                      ║"
echo "╠═══════════════════════════════════════════════════════════════════════════════╣"

# Today’s Focus Block
echo "║ 🔎 Today’s Focus                                                              ║"
echo "║ Suggested Move: Run 'dashboard' to refresh view                               ║"
echo "║ Region Pointer: /vault/crypt                                                  ║"
echo "╠═══════════════════════════════════════════════════════════════════════════════╣"

# Recent Moves (show last 5 lines)
echo "║ 📝 Recent Moves                                                               ║"
tail -n 5 /uKnowledge/logs/moves.md 2>/dev/null | while read -r line; do
  printf "║ %s%-74s║\n" "" "$line"
done
echo "╠═══════════════════════════════════════════════════════════════════════════════╣"

# Map Peek Block
echo "║ 🗺️  Map Peek                                                                   ║"
if [ -f /uKnowledge/map/current_region.txt ]; then
  while read -r line; do
    printf "║ %s%-74s║\n" "" "$line"
  done < /uKnowledge/map/current_region.txt
else
  echo "║ No map data available.                                                        ║"
fi
echo "╠═══════════════════════════════════════════════════════════════════════════════╣"

# Tower Snapshot
echo "║ 🧠 Tower of Knowledge                                                         ║"
ls -1 /uKnowledge/rooms 2>/dev/null | head -n 5 | while read -r room; do
  printf "║ - %s%-70s║\n" "" "$room"
done
echo "╠═══════════════════════════════════════════════════════════════════════════════╣"

# Health Check
echo "║ ✅ Health Check                                                               ║"
echo "║ Logs: $(ls -1 /uKnowledge/logs | wc -l) files      Encryption: [ENABLED]               ║"
echo "║ Sync Status: Local OK, No pending exports                                    ║"
echo "╚═══════════════════════════════════════════════════════════════════════════════╝"
echo ""
echo "Use 'help' for available commands."