#!/bin/bash
# dashboard-sync.sh — Generate ASCII dashboard status snapshot for uOS CLI

BASE="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd"
UMEM="$BASE/uMemory"
STATE="$UMEM/state"
LOGS="$UMEM/logs/moves"

# Load user info
USER_FILE="$STATE/user.md"
USERNAME="Unknown"
if [ -f "$USER_FILE" ]; then
  USERNAME=$(grep -oP '(?<=\*\*Username\*\*: ).*' "$USER_FILE" | head -1)
fi

# Load current datetime
DATETIME=$(date '+%Y-%m-%d %H:%M:%S')

# Load active mission (fallback)
ACTIVE_MISSION="(none)"
MISSION_FILE="$STATE/active_mission.md"
if [ -f "$MISSION_FILE" ]; then
  ACTIVE_MISSION=$(head -n 1 "$MISSION_FILE" | sed 's/# *//')
fi

# Today's Focus (fallback text)
TODAYS_FOCUS="Suggested Move: Run 'log_mission.sh' to begin your next journey"
REGION_POINTER="/vault/crypt"

# Recent moves: list last 5 move entries from latest session index
LATEST_INDEX=$(ls -t $LOGS/index-sess-*.md 2>/dev/null | head -1)
RECENT_MOVES=()
if [ -f "$LATEST_INDEX" ]; then
  RECENT_MOVES=($(grep -oP '(?<=Move: ).*' "$LATEST_INDEX" | tail -5))
fi

# Map Peek and Tower of Knowledge placeholders
MAP_PEEK="No map data available."
TOWER_KNOWLEDGE="No rooms indexed yet."

# Health Check placeholders
HEALTH_CHECK="No stat log available. Run generate_stats.sh."
ENCRYPTION_STATUS="[ENABLED]"
SYNC_STATUS="Local OK, No pending exports"

# Build dashboard ASCII output
cat <<EOF
╔═══════════════════════════[ uOS STATUS DASHBOARD ]═══════════════════════════╗
║ User: $USERNAME                             $DATETIME ║
║ Location: Unknown                                                         ║
║ Active Mission: $ACTIVE_MISSION                                                    ║
╠═══════════════════════════════════════════════════════════════════════════════╣
║ 🔎 Today’s Focus                                                              ║
║ $TODAYS_FOCUS                                                               ║
║ Region Pointer: $REGION_POINTER                                              ║
╠═══════════════════════════════════════════════════════════════════════════════╣
║ 📝 Recent Moves                                                               ║
EOF

if [ ${#RECENT_MOVES[@]} -eq 0 ]; then
  echo "║ No recent moves logged.                                                     ║"
else
  for move in "${RECENT_MOVES[@]}"; do
    # Pad or truncate move description to 75 chars for clean formatting
    line=$(printf "║ %-75s ║" "Move: $move")
    echo "$line"
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
║ $HEALTH_CHECK                                                                ║
║ Encryption: $ENCRYPTION_STATUS      Sync Status: $SYNC_STATUS                 ║
╚═══════════════════════════════════════════════════════════════════════════════╝

🧭 Use 'help' for available commands. Make your next move, Master.
EOF