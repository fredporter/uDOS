#!/bin/bash

# === uOS Move 007: Finalize File from Sandbox ===

SANDBOX="$HOME/uOS/sandbox"
UMEMORY="$HOME/uOS/uMemory"
UKNOWLEDGE="$HOME/uOS/uKnowledge"

echo "🧪 Finalizing file from sandbox..."

echo "📜 Files available in sandbox:"
ls "$SANDBOX"/*.md 2>/dev/null || { echo "❌ No .md files in sandbox."; exit 1; }

read -p "🔍 Enter filename (e.g., temp-mission.md): " filename
FILEPATH="$SANDBOX/$filename"

if [[ ! -f "$FILEPATH" ]]; then
  echo "❌ File not found: $FILEPATH"
  exit 1
fi

echo "📂 Choose destination:"
echo "1. uMemory → missions/"
echo "2. uMemory → milestones/"
echo "3. uMemory → legacy/"
echo "4. uMemory → logs/moves/"
echo "5. uKnowledge → general/"
echo "6. uKnowledge → map/"
read -p "Selection [1-6]: " choice

# Timestamped final name
DATESTAMP=$(date '+%Y-%m-%d')
EPOCH=$(date '+%s')

case $choice in
  1) DEST="$UMEMORY/missions/${DATESTAMP}-mission-${EPOCH}.md" ;;
  2) DEST="$UMEMORY/milestones/${DATESTAMP}-milestone-${EPOCH}.md" ;;
  3) DEST="$UMEMORY/legacy/${DATESTAMP}-legacy-${EPOCH}.md" ;;
  4) DEST="$UMEMORY/logs/moves/${DATESTAMP}-move-${EPOCH}.md" ;;
  5) DEST="$UKNOWLEDGE/general/${DATESTAMP}-note-${EPOCH}.md" ;;
  6) DEST="$UKNOWLEDGE/map/${DATESTAMP}-location-${EPOCH}.md" ;;
  *) echo "❌ Invalid selection."; exit 1 ;;
esac

echo "✅ Copying $filename to → $DEST"
cp "$FILEPATH" "$DEST"

read -p "🧹 Delete original from sandbox? [y/N]: " delete_choice
[[ "$delete_choice" =~ ^[Yy]$ ]] && rm "$FILEPATH" && echo "🧽 Sandbox cleaned."

echo "🎉 File finalized and stored."