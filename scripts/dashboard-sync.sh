#!/bin/bash
# dashboard-sync.sh — Generate and display uOS status dashboard (improved)

UROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
MEMORY_DIR="${UOS_MEMORY_DIR:-$UROOT/uMemory}"
KNOWLEDGE_DIR="${UOS_KNOWLEDGE_DIR:-$UROOT/uKnowledge}"

STATE_DIR="$MEMORY_DIR/state"
MOVE_DIR="$MEMORY_DIR/logs/moves"
SESSION_FILE="$MEMORY_DIR/logs/session-$(date +%Y-%m-%d).md"

NOW="$(date '+%Y-%m-%d %H:%M:%S')"

# Fetch User name cleanly
USER_NAME="Unknown"
USER_FILE="$STATE_DIR/user.md"
if [[ -f "$USER_FILE" ]]; then
  # Extract username from lines like "username: Master"
  USER_NAME=$(grep -iE '^\s*(username|user):' "$USER_FILE" | head -1 | sed -E 's/^\s*(username|user):\s*//I' | tr -d '\r\n')
  if [[ -z "$USER_NAME" ]]; then
    # fallback to first non-empty line without markdown decorations
    USER_NAME=$(grep -vE '^\s*#|^\s*$' "$USER_FILE" | head -1 | tr -d '\r\n')
  fi
fi
[[ -z "$USER_NAME" ]] && USER_NAME=$(whoami 2>/dev/null || echo "Unknown")

# Fetch Location
LOCATION="Unknown"
LOC_FILE="$STATE_DIR/location.txt"
if [[ -f "$LOC_FILE" ]]; then
  LOCATION=$(head -1 "$LOC_FILE" | tr -d '\r\n')
fi

# Fetch Active Mission
ACTIVE_MISSION="none"
for f in "$STATE_DIR/current_mission.md" "$STATE_DIR/current_mission.txt"; do
  if [[ -f "$f" ]]; then
    ACTIVE_MISSION=$(head -1 "$f" | tr -d '\r\n')
    [[ -n "$ACTIVE_MISSION" ]] && break
  fi
done
[[ -z "$ACTIVE_MISSION" ]] && ACTIVE_MISSION="none"

# Fetch Recent Moves (up to 5 newest)
RECENT_MOVES=()
if compgen -G "$MOVE_DIR/*.md" > /dev/null; then
  RECENT_MOVES=($(ls -1t "$MOVE_DIR"/*.md | head -5))
fi

RECENT_DISPLAY=()
if [[ ${#RECENT_MOVES[@]} -eq 0 ]]; then
  RECENT_DISPLAY+=("No recent moves logged.")
else
  for move_file in "${RECENT_MOVES[@]}"; do
    basename_file=$(basename "$move_file")
    date_part=$(echo "$basename_file" | cut -d'-' -f1-3)

    # Try to parse a 'Command:' or 'Move:' line from the move file for command description
    cmd_line=$(grep -m1 -E '^(Command:|Move:)' "$move_file" | sed -E 's/^(Command:|Move:)\s*//I' | tr -d '\r\n')
    # Fallback: use filename if no command line found
    if [[ -z "$cmd_line" ]]; then
      cmd_line="$basename_file"
    fi
    RECENT_DISPLAY+=("[$date_part] Move: $cmd_line")
  done
fi

# Map Peek
MAP_PEEK="No map data available."
MAP_FILE="$KNOWLEDGE_DIR/map/current_region.txt"
if [[ -f "$MAP_FILE" ]]; then
  MAP_PEEK=$(head -5 "$MAP_FILE" | sed 's/^/  /')
fi

# Tower of Knowledge placeholder
TOWER_PEAK="No rooms indexed yet."

# Health Check placeholder
STAT_LOG="$MEMORY_DIR/logs/statistics.log"
HEALTH_CHECK="No stat log available. Run generate_stats.sh."
if [[ -f "$STAT_LOG" ]]; then
  HEALTH_CHECK="Stat log available."
fi

# Encryption, Privacy, Lifespan, Sync Status placeholders
ENCRYPTION_STATUS="[ENABLED]"
PRIVACY_STATUS="n/a"
LIFESPAN_STATUS="n/a"
SYNC_STATUS="Local OK, No pending exports"

# Dashboard width (75 chars)
WIDTH=75

printf '╔%s╗\n' "$(printf '═%.0s' $(seq 1 $WIDTH))"
printf '║ User: %-59s %19s ║\n' "$USER_NAME" "$NOW"
printf '║ Location: %-67s ║\n' "$LOCATION"
printf '║ Active Mission: %-59s ║\n' "$ACTIVE_MISSION"
printf '╠%s╣\n' "$(printf '═%.0s' $(seq 1 $WIDTH))"

printf '║ 🔎 Today’s Focus%56s ║\n' ""
printf '║ Suggested Move: Run '\''log_mission.sh'\'' to begin your next journey%7s ║\n' ""
printf '║ Region Pointer: /vault/crypt%52s ║\n' ""
printf '╠%s╣\n' "$(printf '═%.0s' $(seq 1 $WIDTH))"

printf '║ 📝 Recent Moves%58s ║\n' ""
for line in "${RECENT_DISPLAY[@]}"; do
  printf '║ %-73s ║\n' "$line"
done

printf '╠%s╣\n' "$(printf '═%.0s' $(seq 1 $WIDTH))"

printf '║ 🗺️  Map Peek%61s ║\n' ""
while IFS= read -r line; do
  printf '║ %-73s ║\n' "$line"
done <<< "$MAP_PEEK"

printf '╠%s╣\n' "$(printf '═%.0s' $(seq 1 $WIDTH))"

printf '║ 🧠 Tower of Knowledge%49s ║\n' ""
printf '║ %-73s ║\n' "$TOWER_PEAK"

printf '╠%s╣\n' "$(printf '═%.0s' $(seq 1 $WIDTH))"

printf '║ ✅ Health Check%56s ║\n' ""
printf '║ %-73s ║\n' "$HEALTH_CHECK"
printf '║ Encryption: %-9s   Privacy: %-6s   Lifespan: %-6s ║\n' "$ENCRYPTION_STATUS" "$PRIVACY_STATUS" "$LIFESPAN_STATUS"
printf '║ Sync Status: %-45s ║\n' "$SYNC_STATUS"

printf '╚%s╝\n' "$(printf '═%.0s' $(seq 1 $WIDTH))"

echo ""
echo "🧭 Use 'help' for available commands. Make your next move, Master."