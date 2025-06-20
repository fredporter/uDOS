#!/bin/bash

UMEMORY="$HOME/uOS/uMemory/milestones"
TEMPLATE="$HOME/uOS/templates/milestone-template.md"
DATESTAMP=$(date '+%Y-%m-%d')
EPOCH=$(date '+%s')
FILENAME="${DATESTAMP}-milestone-${EPOCH}.md"
DEST="$UMEMORY/$FILENAME"

mkdir -p "$UMEMORY"
cp "$TEMPLATE" "$DEST"

echo "📝 Milestone file created: $DEST"
nano "$DEST"