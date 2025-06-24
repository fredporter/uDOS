#!/bin/bash

UDOSE_HOME="${UDOSE_HOME:-$HOME/uDOS}"
UROOT="$UDOSE_HOME"
UMEMORY="$UROOT/uMemory/milestones"
TEMPLATE="$UROOT/uTemplate/milestone-template.md"
DATESTAMP=$(date +%Y%m%d)
TIMESTAMP=$(date +%H%M%S%3N)
LOCATION=$(cat "$UROOT/uMemory/state/location.txt" 2>/dev/null || echo "F00:00:00")
LOCATION_SAFE=$(echo "$LOCATION" | tr -d ':')
TIMEZONE="AEST"
FILENAME="milestone-${DATESTAMP}-${TIMESTAMP}-${TIMEZONE}-${LOCATION_SAFE}.md"
DEST="$UMEMORY/$FILENAME"

mkdir -p "$UMEMORY"
cp "$TEMPLATE" "$DEST"

echo "📝 Milestone file created: $DEST"
nano "$DEST"