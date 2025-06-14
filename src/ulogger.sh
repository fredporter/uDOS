#!/bin/bash

# uLogger: logs each Move into uKnowledge
LOG_DIR="/uKnowledge/logs/moves"
TEMPLATE="/uKnowledge/templates/move-template.md"
USERNAME=$(whoami)
TIMESTAMP=$(date +%s)
ISO8601=$(date -u +"%Y-%m-%dT%H:%M:%SZ")
DATE=$(date +%Y-%m-%d)

# Ensure log dir exists
mkdir -p "$LOG_DIR"

echo "🌀 uLogger active. Type your commands below (type 'exit' or Ctrl-D to quit)."
echo ""

while true; do
  echo -n "↪ "
  read -e CMD || break

  # Break loop on empty input
  [[ -z "$CMD" ]] && continue

  # Run command and capture output
  OUTPUT=$(eval "$CMD" 2>&1)
  STATUS=$?

  # Generate unique log ID
  ID="move-$TIMESTAMP"
  FILE="$LOG_DIR/$DATE-$ID.md"

  # Fill template
  cat "$TEMPLATE" | sed \
    -e "s|{{timestamp}}|$TIMESTAMP|g" \
    -e "s|{{iso8601}}|$ISO8601|g" \
    -e "s|{{username}}|$USERNAME|g" \
    -e "s|{{description}}|$CMD|g" \
    -e "s|{{command}}|$CMD|g" \
    -e "s|{{output}}|$OUTPUT|g" \
    -e "s|{{date}}|$DATE|g" \
    > "$FILE"

  echo -e "$OUTPUT"
done