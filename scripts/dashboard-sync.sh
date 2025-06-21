#!/bin/bash
# dashboard-sync.sh — Generate and display uOS status dashboard

# Base dirs
UROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
MEMORY_DIR="${UOS_MEMORY_DIR:-$UROOT/uMemory}"
KNOWLEDGE_DIR="${UOS_KNOWLEDGE_DIR:-$UROOT/uKnowledge}"

STATE_DIR="$MEMORY_DIR/state"
MOVE_DIR="$MEMORY_DIR/logs/moves"
SESSION_FILE="$MEMORY_DIR/logs/session-$(date +%Y-%m-%d).md"

# Timestamp
NOW="$(date '+%Y-%m-%d %H:%M:%S')"

# Fetch User: prefer state/user.md (frontmatter or first non-comment line), else fallback
USER_NAME="Unknown"
USER_FILE="$STATE_DIR/user.md"
if [[ -f "$USER_FILE" ]]; then
  # Attempt to extract username from frontmatter or first content line
  # Assume YAML frontmatter or simple key:value like "username: Master"
  USER_NAME=$(grep -E '^(username:|user:)' "$USER_FILE" | head -1 | sed -E 's/.*: *//')
  if [[ -z "$USER_NAME" ]]; then
    # fallback: first non-empty, non-comment line
    USER_NAME=$(grep -vE '^#|^$' "$USER_FILE" | head -1)
  fi
fi

# Fallback to whoami or environment variable if still empty
if [[ -z "$USER_NAME" ]]; then
  USER_NAME=$(whoami 2>/dev/null || echo "Unknown")
fi

# Fetch Location (assume location.txt or similar)
LOCATION="Unknown"
LOC_FILE="$STATE_DIR/location.txt"
if [[ -f "$LOC_FILE" ]]; then
  LOCATION=$(head -1 "$LOC_FILE" | tr -d '\r\n')
fi

# Fetch Active Mission (try current_mission.md or current_mission.txt)
ACTIVE_MISSION="none"
for f in "$STATE_DIR/current_mission.md" "$STATE_DIR/current_mission.txt"; do
  if [[ -f "$f" ]]; then
    ACTIVE_MISSION=$(head -1 "$f" | tr -d '\r\n')
    [[ -n "$ACTIVE_MISSION" ]] && break
  fi
done

# Prepare Recent Moves - list last 5 moves by date descending
RECENT_MOVES=()
if compgen -G "$MOVE_DIR/*.md" > /dev/null; then
  RECENT_MOVES=($(ls -1t "$MOVE_DIR"/*.md | head -5))
fi

# Compose Recent Moves display lines
RECENT_DISPLAY=()
if [[ ${#RECENT_MOVES[@]} -eq 0 ]]; then
  RECENT_DISPLAY+=("No recent moves logged.")
else
  for move_file in "${RECENT_MOVES[@]}"; do
    # Extract date and command line from move file frontmatter or content
    # For simplicity, try to get date from filename and command from first 'Move:' line
    basename_file=$(basename "$move_file")
    date_part=$(echo "$basename_file" | cut -d'-' -f1-3)
    # Attempt to extract command line inside move file (look for 'Command:' or 'Move:')
    cmd_line=$(grep -m1 -E '^(Command:|Move:)' "$move_file" | sed -E 's/^(Command:|Move:) *//')
    [[ -z "$cmd_line" ]] && cmd_line="[unnamed move]"
    RECENT_DISPLAY+=("[$date_part] Move: $cmd_line")
  done
fi

# Map Peek placeholder
MAP_PEEK="No map data available."
MAP_FILE="$KNOWLEDGE_DIR/map/current_region.txt"
if [[ -f "$MAP_FILE" ]]; then
  # Read first few lines, limit to 5
  MAP_PEEK=$(head -5 "$MAP_FILE" | sed 's/^/  /')
fi

# Tower of Knowledge placeholder
TOWER_PEAK="No rooms indexed yet."
# Could add logic here later to scan rooms or topics indexed

# Health Check placeholder
STAT_LOG="$MEMORY_DIR/logs/statistics.log"
HEALTH_CHECK="No stat log available. Run generate_stats.sh."
if [[ -f "$STAT_LOG" ]]; then
  HEALTH_CHECK="Stat log available."
fi

# Encryption, Privacy, Lifespan, Sync Status (placeholders; update as you build these features)
ENCRYPTION_STATUS="[ENABLED]"
PRIVACY_STATUS="n/a"
LIFESPAN_STATUS="n/a"
SYNC_STATUS="Local OK, No pending exports"

# Compose and print dashboard ASCII box
printf '╔%s╗\n' "$(printf '═%.0s' {1..75})"
printf '║ %-68s ║\n' "User: $USER_NAME $(printf '%0.0s ' $(seq 1 $((68 - ${#USER_NAME} - 5)))) $(date '+%Y-%m-%d %H:%M:%S')"
printf '║ Location: %-60s ║\n' "$LOCATION"
printf '║ Active Mission: %-53s ║\n' "$ACTIVE_MISSION"
printf '╠%s╣\n' "$(printf '═%.0s' {1..75})"

printf '║ 🔎 Today’s Focus%56s ║\n' ""
printf '║ Suggested Move: Run '"'"'log_mission.sh'"'"' to begin your next journey%7s ║\n' ""
printf '║ Region Pointer: /vault/crypt%52s ║\n' ""
printf '╠%s╣\n' "$(printf '═%.0s' {1..75})"

printf '║ 📝 Recent Moves%58s ║\n' ""
for line in "${RECENT_DISPLAY[@]}"; do
  printf '║ %-73s ║\n' "$line"
done
printf '╠%s╣\n' "$(printf '═%.0s' {1..75})"

printf '║ 🗺️  Map Peek%61s ║\n' ""
while IFS= read -r line; do
  printf '║ %-73s ║\n' "$line"
done <<< "$MAP_PEEK"
printf '╠%s╣\n' "$(printf '═%.0s' {1..75})"

printf '║ 🧠 Tower of Knowledge%49s ║\n' ""
printf '║ %-73s ║\n' "$TOWER_PEAK"
printf '╠%s╣\n' "$(printf '═%.0s' {1..75})"

printf '║ ✅ Health Check%56s ║\n' ""
printf '║ %-73s ║\n' "$HEALTH_CHECK"
printf '║ Encryption: %-9s   Privacy: %-6s   Lifespan: %-6s ║\n' "$ENCRYPTION_STATUS" "$PRIVACY_STATUS" "$LIFESPAN_STATUS"
printf '║ Sync Status: %-45s ║\n' "$SYNC_STATUS"
printf '╚%s╝\n' "$(printf '═%.0s' {1..75})"

echo ""
echo "🧭 Use 'help' for available commands. Make your next move, Master."