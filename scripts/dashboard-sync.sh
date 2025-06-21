#!/bin/bash
# dashboard-sync.sh — Generate ASCII dashboard status snapshot for uOS CLI

BASE="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
UMEM="$BASE/uMemory"
STATE="$UMEM/state"
LOGS="$UMEM/logs/moves"

# ─────────────────────────────────────────────────────────────────────────────
# Load user data safely using sed (BusyBox compatible)
# ─────────────────────────────────────────────────────────────────────────────
USER_FILE="$STATE/user.md"
USERNAME="Unknown"
LOCATION="Unknown"
MISSION="(none)"
LIFESPAN="n/a"
PRIVACY="crypt"

if [ -f "$USER_FILE" ]; then
  USERNAME=$(sed -n 's/\*\*Username\*\*: //p' "$USER_FILE")
  LOCATION=$(sed -n 's/\*\*Location\*\*: //p' "$USER_FILE")
  MISSION=$(sed -n 's/\*\*Mission\*\*: //p' "$USER_FILE")
  LIFESPAN=$(sed -n 's/\*\*Lifespan\*\*: //p' "$USER_FILE")
  PRIVACY=$(sed -n 's/\*\*Privacy\*\*: //p' "$USER_FILE")
fi

# ─────────────────────────────────────────────────────────────────────────────
# Load datetime + mission fallback
# ─────────────────────────────────────────────────────────────────────────────
DATETIME=$(date '+%Y-%m-%d %H:%M:%S')
MISSION_FILE="$STATE/active_mission.md"
if [ -f "$MISSION_FILE" ]; then
  MISSION=$(head -n 1 "$MISSION_FILE" | sed 's/# *//')
fi

# ─────────────────────────────────────────────────────────────────────────────
# Today’s Focus & Region Pointer (default values for now)
# ─────────────────────────────────────────────────────────────────────────────
TODAYS_FOCUS="Suggested Move: Run 'log_mission.sh' to begin your next journey"
REGION_POINTER="/vault/crypt"

# ─────────────────────────────────────────────────────────────────────────────
# Recent Moves (from latest session index file)
# ─────────────────────────────────────────────────────────────────────────────
LATEST_INDEX=$(ls -t "$LOGS"/index-sess-*.md 2>/dev/null | head -1)
RECENT_MOVES=()
if [ -f "$LATEST_INDEX" ]; then
  while IFS= read -r line; do
    move=$(echo "$line" | sed 's/- .*Move: //')
    RECENT_MOVES+=("$move")
  done < <(grep 'Move:' "$LATEST_INDEX" | tail -5)
fi

# ─────────────────────────────────────────────────────────────────────────────
# Map + Tower placeholders
# ─────────────────────────────────────────────────────────────────────────────
MAP_PEEK="No map data available."
TOWER_KNOWLEDGE="No rooms indexed yet."

# ─────────────────────────────────────────────────────────────────────────────
# Health Check
# ─────────────────────────────────────────────────────────────────────────────
HEALTH_CHECK="No stat log available. Run generate_stats.sh."
ENCRYPTION_STATUS="[ENABLED]"
SYNC_STATUS="Local OK, No pending exports"

# ─────────────────────────────────────────────────────────────────────────────
# ASCII Dashboard Output
# ─────────────────────────────────────────────────────────────────────────────
cat <<EOF
╔═══════════════════════════[ uOS STATUS DASHBOARD ]═══════════════════════════╗
║ User: $USERNAME                             $DATETIME ║
║ Location: $LOCATION                                                    ║
║ Active Mission: $MISSION                                                    ║
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
║ $HEALTH_CHECK                                                                ║
║ Encryption: $ENCRYPTION_STATUS   Privacy: $PRIVACY   Lifespan: $LIFESPAN     ║
║ Sync Status: $SYNC_STATUS                                                  ║
╚═══════════════════════════════════════════════════════════════════════════════╝

🧭 Use 'help' for available commands. Make your next move, Master.
EOF