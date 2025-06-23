#!/bin/bash

# === uDOS Move 007: Finalise File from Sandbox ===

SANDBOX="../sandbox"
UMEMORY="../uMemory"
UKNOWLEDGE="../uKnowledge"

echo "🧪 Finalising file from sandbox..."

# List available .md files
echo "📜 Files available in sandbox:"
ls "$SANDBOX"/*.md 2>/dev/null || {
  echo "❌ No .md files in sandbox. Aborting."
  exit 1
}

# Get filename input
read -p "🔍 Enter filename (e.g., temp-mission.md): " filename
FILEPATH="$SANDBOX/$filename"

if [[ ! -f "$FILEPATH" ]]; then
  echo "❌ File not found: $FILEPATH. Aborting."
  exit 1
fi

# Select destination
echo "📂 Choose destination:"
echo "1. uMemory → missions/"
echo "2. uMemory → milestones/"
echo "3. uMemory → legacy/"
echo "4. uMemory → logs/notes/"
echo "5. uKnowledge → general/"
echo "6. uKnowledge → map/"
read -p "Selection [1-6]: " choice

# Generate timestamped destination filename
DATESTAMP=$(date '+%Y-%m-%d')
EPOCH=$(date '+%s')

case $choice in
  1) DEST="$UMEMORY/missions/${DATESTAMP}-mission-${EPOCH}.md" ;;
  2) DEST="$UMEMORY/milestones/${DATESTAMP}-milestone-${EPOCH}.md" ;;
  3) DEST="$UMEMORY/legacy/${DATESTAMP}-legacy-${EPOCH}.md" ;;
  4) DEST="$UMEMORY/logs/notes/${DATESTAMP}-note-${EPOCH}.md" ;;
  5) DEST="$UKNOWLEDGE/general/${DATESTAMP}-note-${EPOCH}.md" ;;
  6) DEST="$UKNOWLEDGE/map/${DATESTAMP}-location-${EPOCH}.md" ;;
  *) echo "❌ Invalid selection. Aborting."; exit 1 ;;
esac

# Copy file
echo "✅ Copying $filename to → $DEST"
cp "$FILEPATH" "$DEST"

# Offer to delete original
read -p "🧹 Delete original from sandbox? [y/N]: " delete_choice
if [[ "$delete_choice" =~ ^[Yy]$ ]]; then
  rm "$FILEPATH"
  echo "🧽 Sandbox cleaned."
fi

echo "🎉 File finalized and stored."
