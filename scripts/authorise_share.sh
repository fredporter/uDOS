#!/bin/bash

# === uDOS Move 009: Proximity Share Authorization ===

UDOSE_HOME="/root/uDOS"
UMEMORY="$UDOSE_HOME/uMemory"
KEYDIR="$UDOSE_HOME/keys"
LOG="$UMEMORY/logs/share-events.md"

mkdir -p "$KEYDIR"

read -p "📄 Enter path to file to authorize (e.g. $UMEMORY/missions/foo.md): " FILE

if [[ ! -f "$FILE" ]]; then
  echo "❌ Error: File does not exist → $FILE"
  exit 1
fi

read -p "🆔 Authorize device ID: " DEVICE_ID
read -p "🔑 Path to device's public key: " PUBLIC_KEY
read -p "📅 Expiration date (YYYY-MM-DD): " EXPIRY

# Insert metadata block after first --- in YAML frontmatter
# Platform-safe sed block (BSD + GNU)
if [[ "$OSTYPE" == "darwin"* ]]; then
  SED_INLINE=(-i '')
else
  SED_INLINE=(-i)
fi

sed "${SED_INLINE[@]}" "/^---$/a\\
share: true\\
shared_with:\\
  - device_id: \"$DEVICE_ID\"\\
    expires: \"$EXPIRY\"\\
    public_key: \"$PUBLIC_KEY\"\\
requires_proximity: true\\
encryption: true\\
audit: true
" "$FILE"

# Log the authorization event
TIMESTAMP=$(date '+%Y-%m-%d %H:%M:%S')
{
  echo "### Share Event"
  echo "- 🕓 $TIMESTAMP"
  echo "- 📄 File: $FILE"
  echo "- 📤 Shared with: $DEVICE_ID"
  echo "- ⏳ Expiry: $EXPIRY"
  echo ""
} >> "$LOG"

echo "✅ Sharing metadata injected and event logged."
