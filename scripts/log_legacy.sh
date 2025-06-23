#!/bin/bash

UROOT="$HOME/uDOS"
UMEMORY="$UROOT/uMemory/legacy"
TEMPLATE="$UROOT/uTemplate/legacy-template.md"
DATESTAMP=$(date +%Y%m%d)
TIMESTAMP=$(date +%H%M%S%3N)
LOCATION=$(cat "$UROOT/uMemory/state/location.txt" 2>/dev/null || echo "F00:00:00")
LOCATION_SAFE=$(echo "$LOCATION" | tr -d ':')
TIMEZONE="AEST"
FILENAME="legacy-${DATESTAMP}-${TIMESTAMP}-${TIMEZONE}-${LOCATION_SAFE}.md"
DEST="$UMEMORY/$FILENAME"

mkdir -p "$UMEMORY"
cp "$TEMPLATE" "$DEST"

echo "📝 Legacy file created: $DEST"
nano "$DEST"