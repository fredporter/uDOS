#!/bin/bash

# === uOS Move 009: Proximity Share Authorization ===

UMEMORY="$HOME/uOS/uMemory"
KEYDIR="$HOME/.uOS/keys"
LOG="$UMEMORY/logs/share-events.md"

mkdir -p "$KEYDIR"

read -p "📄 Path to file to authorize (e.g. $UMEMORY/missions/foo.md): " FILE

if [[ ! -f "$FILE" ]]; then
  echo "❌ File does not exist."
  exit 1
fi

read -p "🆔 Authorize device ID: " DEVICE_ID
read -p "🔑 Path to device's public key: " PUBLIC_KEY
read -p "📅 Expiration date (YYYY-MM-DD): " EXPIRY

# Append frontmatter share metadata
sed -i '' "s/^---/&\nshare: true\nshared_with:\n  - device_id: $DEVICE_ID\n    expires: $EXPIRY\n    public_key: $PUBLIC_KEY\nrequires_proximity: true\nencryption: true\naudit: true/" "$FILE"

# Log the authorization
TIMESTAMP=$(date '+%Y-%m-%d %H:%M:%S')
{
  echo "### Share Event"
  echo "- 🕓 $TIMESTAMP"
  echo "- 📄 File: $FILE"
  echo "- 📤 Shared with: $DEVICE_ID"
  echo "- ⏳ Expiry: $EXPIRY"
  echo ""
} >> "$LOG"

echo "✅ File updated with sharing metadata and logged."