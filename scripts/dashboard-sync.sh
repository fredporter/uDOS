#!/bin/bash
# dashboard-sync.sh — Generate and display uOS status dashboard (improved)

UROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
MEMORY_DIR="${UOS_MEMORY_DIR:-$UROOT/uMemory}"
KNOWLEDGE_DIR="${UOS_KNOWLEDGE_DIR:-$UROOT/uKnowledge}"

STATE_DIR="$MEMORY_DIR/state"
MOVE_DIR="$MEMORY_DIR/logs/moves"
SESSION_FILE="$MEMORY_DIR/logs/session-$(date +%Y-%m-%d).md"

NOW="$(date '+%Y-%m-%d %H:%M:%S')"

# Initialize all user variables with sensible defaults
USER_NAME="Unknown"
USER_ID="N/A"
INSTANCE_ID="N/A"
INSTANCE_NUMBER="N/A"
CREATED="N/A"
LOCATION="Unknown"
ACTIVE_MISSION="none"
LEGACY="none"
LIFESPAN="n/a"
PRIVACY="n/a"
UOS_VERSION="n/a"

USER_FILE="$STATE_DIR/user.md"
if [[ -f "$USER_FILE" ]]; then
  while IFS= read -r line; do
    # Parse lines of the form: **Key**: Value
    if [[ "$line" =~ \*\*(.+)\*\*:\ (.+) ]]; then
      key="${BASH_REMATCH[1]}"
      value="${BASH_REMATCH[2]}"
      # Trim whitespace from key and value
      key="${key//[[:space:]]/}"
      value="${value#"${value%%[![:space:]]*}"}"
      value="${value%"${value##*[![:space:]]}"}"

      case "$key" in
        Username) USER_NAME="$value" ;;
        "UserID") USER_ID="$value" ;;
        "InstanceID") INSTANCE_ID="$value" ;;
        "InstanceNumber") INSTANCE_NUMBER="$value" ;;
        Created) CREATED="$value" ;;
        Location) LOCATION="$value" ;;
        Mission) ACTIVE_MISSION="$value" ;;
        Legacy) LEGACY="$value" ;;
        Lifespan) LIFESPAN="$value" ;;
        Privacy) PRIVACY="$value" ;;
        "uOSVersion") UOS_VERSION="$value" ;;
      esac
    fi
  done < "$USER_FILE"
fi

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
PRIVACY_STATUS="$PRIVACY"
LIFESPAN_STATUS="$LIFESPAN"
SYNC_STATUS="Local OK, No pending exports"

# Dashboard width (75 chars)
WIDTH=75

printf '╔%s╗\n' "$(printf '═%.0s' $(seq 1 $WIDTH))"
printf '║ User: %-59s %19s ║\n' "$USER_NAME" "$NOW"
printf '║ User ID: %-65s ║\n' "$USER_ID"
printf '║ Instance ID: %-60s ║\n' "$INSTANCE_ID"
printf '║ Instance Number: %-54s ║\n' "$INSTANCE_NUMBER"
printf '║ Created: %-66s ║\n' "$CREATED"
printf '║ Location: %-67s ║\n' "$LOCATION"
printf '║ Active Mission: %-59s ║\n' "$ACTIVE_MISSION"
printf '║ Legacy: %-68s ║\n' "$LEGACY"
printf '║ uOS Version: %-63s ║\n' "$UOS_VERSION"
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