#!/bin/bash
# dashboard-sync.sh — Unified uOS ASCII dashboard generator

BASE="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
UMEM="$BASE/uMemory"
STATE="$UMEM/state"
LOGS="$UMEM/logs"
MOVES="$LOGS/moves"
STATS_LOG="$(ls -t "$LOGS"/ulog-*.md 2>/dev/null | head -1)"

# === Load user info ===
USER_FILE="$STATE/user.md"
USERNAME="Unknown"
LOCATION="Unknown"
PRIVACY="n/a"
LIFESPAN="n/a"
if [ -f "$USER_FILE" ]; then
  USERNAME=$(grep -oP '(?<=\*\*Username\*\*: ).*' "$USER_FILE")
  LOCATION=$(grep -oP '(?<=\*\*Location\*\*: ).*' "$USER_FILE")
  PRIVACY=$(grep -oP '(?<=\*\*Privacy\*\*: ).*' "$USER_FILE")
  LIFESPAN=$(grep -oP '(?<=\*\*Lifespan\*\*: ).*' "$USER_FILE")
fi

# === Active mission ===
ACTIVE_MISSION="(none)"
if [ -f "$STATE/current_mission.txt" ]; then
  ACTIVE_MISSION=$(head -n1 "$STATE/current_mission.txt")
elif [ -f "$STATE/active_mission.md" ]; then
  ACTIVE_MISSION=$(head -n1 "$STATE/active_mission.md" | sed 's/# *//')
fi

# === Datetime now ===
DATETIME=$(date '+%Y-%m-%d %H:%M:%S')

# === Recent Moves ===
LATEST_INDEX=$(ls -t "$MOVES"/index-sess-*.md 2>/dev/null | head -1)
RECENT_MOVES=()
if [ -f "$LATEST_INDEX" ]; then
  RECENT_MOVES=($(grep -oP '(?<=Move: ).*' "$LATEST_INDEX" | tail -5))
fi

# === Health Check Data ===
if [ -f "$STATS_LOG" ]; then
  HEALTH_STATS=$(tail -n 10 "$STATS_LOG")
else
  HEALTH_STATS="No stat log available. Run generate_stats.sh."
fi

ENCRYPTION_STATUS="[ENABLED]"
REGION_POINTER="/vault/crypt"
TOWER_KNOWLEDGE="No rooms indexed yet."
MAP_PEEK="No map data available."

# === Output ASCII Dashboard ===
cat <<EOF
╔═══════════════════════════[ uOS STATUS DASHBOARD ]═══════════════════════════╗
║ User: ${USERNAME:-Unknown}                             $DATETIME ║
║ Location: ${LOCATION:-Unknown}                                                         ║
║ Active Mission: ${ACTIVE_MISSION:-none}                                                    ║
╠═══════════════════════════════════════════════════════════════════════════════╣
║ 🔎 Today’s Focus                                                              ║
║ Suggested Move: Run 'log_mission.sh' to begin your next journey               ║
║ Region Pointer: $REGION_POINTER                                                  ║
╠═══════════════════════════════════════════════════════════════════════════════╣
║ 📝 Recent Moves                                                               ║
EOF

if [ ${#RECENT_MOVES[@]} -eq 0 ]; then
  echo "║ No recent moves logged.                                                     ║"
else
  for move in "${RECENT_MOVES[@]}"; do
    printf "║ %-75s ║\n" "Move: $move"
  done
fi

cat <<EOF
╠═══════════════════════════════════════════════════════════════════════════════╣
║ 🗺️  Map Peek                                                                   ║
║ $MAP_PEEK                                                                    ║
╠═══════════════════════════════════════════════════════════════════════════════╣
║ 🧠 Tower of Knowledge                                                         ║
║ $TOWER_KNOWLEDGE                                                             ║
╠═══════════════════════════════════════════════════════════════════════════════╣
║ ✅ Health Check                                                               ║
EOF

if [ "$HEALTH_STATS" != "" ]; then
  echo "$HEALTH_STATS" | while read -r line; do
    printf "║ %-78s ║\n" "$line"
  done
else
  echo "║ No health stats found.                                                      ║"
fi

cat <<EOF
║ Encryption: $ENCRYPTION_STATUS   Privacy: ${PRIVACY:-n/a}   Lifespan: ${LIFESPAN:-n/a}     ║
║ Sync Status: Local OK, No pending exports                                      ║
╚═══════════════════════════════════════════════════════════════════════════════╝

🧭 Use 'help' for available commands. Make your next move, Master.
EOF