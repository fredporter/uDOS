#!/bin/bash
# dashboard-sync.sh — Generate and display uOS status dashboard (improved)

UROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
MEMORY_DIR="${UOS_MEMORY_DIR:-$UROOT/uMemory}"
KNOWLEDGE_DIR="${UOS_KNOWLEDGE_DIR:-$UROOT/uKnowledge}"

STATE_DIR="$MEMORY_DIR/state"
MOVE_DIR="$MEMORY_DIR/logs/moves"
SESSION_FILE="$MEMORY_DIR/logs/session-$(date +%Y-%m-%d).md"
NOW="$(date '+%Y-%m-%d %H:%M:%S')"

# Initialize user variables with safe defaults
USER_NAME="Unknown"
PASSWORD="N/A"
CREATED="N/A"
LOCATION="Unknown"
ACTIVE_MISSION="none"
LEGACY="none"
LIFESPAN="n/a"
SHARING="n/a"
UOS_VERSION="n/a"

# Read Username and Password from sandbox user.md
SANDBOX_USER_FILE="$UROOT/sandbox/user.md"
if [[ -f "$SANDBOX_USER_FILE" ]]; then
  while IFS= read -r line; do
    if [[ "$line" =~ \*\*(.+)\*\*:\ (.+) ]]; then
      key="${BASH_REMATCH[1]//[[:space:]]/}"
      value="$(echo "${BASH_REMATCH[2]}" | xargs)"
      case "$key" in
        Username) USER_NAME="$value" ;;
        Password) PASSWORD="$value" ;;
      esac
    fi
  done < "$SANDBOX_USER_FILE"
fi

# Read other fields from instance.md
INSTANCE_FILE="$STATE_DIR/instance.md"
if [[ -f "$INSTANCE_FILE" ]]; then
  while IFS= read -r line; do
    if [[ "$line" =~ \*\*(.+)\*\*:\ (.+) ]]; then
      key="${BASH_REMATCH[1]//[[:space:]]/}"
      value="$(echo "${BASH_REMATCH[2]}" | xargs)"
      case "$key" in
        Created) CREATED="$value" ;;
        Location) LOCATION="$value" ;;
        Mission) ACTIVE_MISSION="$value" ;;
        Legacy) LEGACY="$value" ;;
        Lifespan) LIFESPAN="$value" ;;
        Sharing) SHARING="$value" ;;
        uOSVersion) UOS_VERSION="$value" ;;
      esac
    fi
  done < "$INSTANCE_FILE"
fi

# Recent Moves
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
    cmd_line=$(grep -m1 -E '^(Command:|Move:)' "$move_file" | sed -E 's/^(Command:|Move:)\s*//I' | tr -d '\r\n')
    [[ -z "$cmd_line" ]] && cmd_line="$basename_file"
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

# Health Check from ulog
ULOG_FILE="$MEMORY_DIR/logs/ulog-$(date +%Y-%m-%d).md"
HEALTH_CHECK_LINES=()
if [[ -f "$ULOG_FILE" ]]; then
  while IFS= read -r line; do
    case "$line" in
      "🕰️  Uptime:"*)          UPTIME="${line#*: }" ;;
      "💾 Memory:"*)           MEMORY_USAGE="${line#*: }" ;;
      "🎮 Total Moves:"*)      TOTAL_MOVES="${line#*: }" ;;
      "📑 Moves Today:"*)      MOVES_TODAY="${line#*: }" ;;
      "🧪 Drafts in Sandbox:"*) SANDBOX_DRAFTS="${line#*: }" ;;
    esac
  done < "$ULOG_FILE"

  [[ -n "$UPTIME" ]] && HEALTH_CHECK_LINES+=("Uptime: $UPTIME")
  [[ -n "$MEMORY_USAGE" ]] && HEALTH_CHECK_LINES+=("Memory: $MEMORY_USAGE")
  [[ -n "$TOTAL_MOVES" ]] && HEALTH_CHECK_LINES+=("Total Moves: $TOTAL_MOVES")
  [[ -n "$MOVES_TODAY" ]] && HEALTH_CHECK_LINES+=("Moves Today: $MOVES_TODAY")
  [[ -n "$SANDBOX_DRAFTS" ]] && HEALTH_CHECK_LINES+=("Sandbox Drafts: $SANDBOX_DRAFTS")
else
  HEALTH_CHECK_LINES+=("No stat log available. Run refresh or generate_stats.sh.")
fi

ENCRYPTION_STATUS="[ENABLED]"
SHARING_STATUS="$SHARING"
LIFESPAN_STATUS="$LIFESPAN"
SYNC_STATUS="Local OK, No pending exports"

# Compute Moves Remaining
if [[ "$LIFESPAN" == "0" ]]; then
  MOVES_REMAINING="∞"
else
  # Attempt to parse LIFESPAN as number, default to 0 if invalid
  if [[ "$LIFESPAN" =~ ^[0-9]+$ ]]; then
    MOVES_REMAINING=$((LIFESPAN * 1000))
  else
    MOVES_REMAINING="N/A"
  fi
fi

HEALTH_CHECK_LINES+=("Moves Remaining: $MOVES_REMAINING")

# Display dashboard
WIDTH=75
printf '╔%s╗\n' "$(printf '═%.0s' $(seq 1 $WIDTH))"
printf '║ User: %-59s %19s ║\n' "$USER_NAME" "$NOW"
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
for line in "${HEALTH_CHECK_LINES[@]}"; do
  printf '║ %-73s ║\n' "$line"
done
printf '║ Encryption: %-9s   Privacy: %-6s   Lifespan: %-6s ║\n' "$ENCRYPTION_STATUS" "$SHARING_STATUS" "$LIFESPAN_STATUS"
printf '║ Sync Status: %-45s ║\n' "$SYNC_STATUS"
printf '╚%s╝\n' "$(printf '═%.0s' $(seq 1 $WIDTH))"

echo ""
echo "🧭 Use 'help' for available commands. Make your next move, Master."