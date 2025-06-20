#!/bin/bash

# === uOS Move 011-A: Log New Mission ===

UMEMORY="$HOME/uOS/uMemory/missions"
TEMPLATE="$HOME/uOS/templates/mission-template.md"
DATESTAMP=$(date '+%Y-%m-%d')
EPOCH=$(date '+%s')
FILENAME="${DATESTAMP}-mission-${EPOCH}.md"
DEST="$UMEMORY/$FILENAME"

mkdir -p "$UMEMORY"
cp "$TEMPLATE" "$DEST"

echo "📝 Mission file created: $DEST"
nano "$DEST"