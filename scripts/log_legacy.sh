#!/bin/bash

UMEMORY="$HOME/uOS/uMemory/legacy"
TEMPLATE="$HOME/uOS/templates/legacy-template.md"
DATESTAMP=$(date '+%Y-%m-%d')
EPOCH=$(date '+%s')
FILENAME="${DATESTAMP}-legacy-${EPOCH}.md"
DEST="$UMEMORY/$FILENAME"

mkdir -p "$UMEMORY"
cp "$TEMPLATE" "$DEST"

echo "📝 Legacy file created: $DEST"
nano "$DEST"