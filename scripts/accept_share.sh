#!/bin/bash

# === uDOS Move 010: Accept & Validate Shared File ===

SANDBOX="../sandbox"
MY_DEVICE_ID="frogbyte-999"
MY_KEY="$HOME/.uDOS/keys/private.pem"

read -p "📄 Path to incoming shared .md file: " SHARED_FILE

if [[ ! -f "$SHARED_FILE" ]]; then
  echo "❌ File not found."
  exit 1
fi

echo "🔍 Checking sharing metadata..."

# Extract frontmatter metadata
SHARE_OK=$(grep -q "^share: true" "$SHARED_FILE" && echo "yes" || echo "no")
AUTHORIZED=$(grep -q "$MY_DEVICE_ID" "$SHARED_FILE" && echo "yes" || echo "no")
EXPIRES=$(grep '^expires:' "$SHARED_FILE" | awk '{print $2}')
NOW=$(date '+%Y-%m-%d')

if [[ "$SHARE_OK" != "yes" ]]; then
  echo "⛔ Sharing not permitted."
  exit 1
fi

if [[ "$AUTHORIZED" != "yes" ]]; then
  echo "⛔ Your device is not authorized for this file."
  exit 1
fi

if [[ "$NOW" > "$EXPIRES" ]]; then
  echo "⏳ Share expired on: $EXPIRES"
  exit 1
fi

# Check for encryption flag
ENCRYPTED=$(grep -q "^encryption: true" "$SHARED_FILE" && echo "yes" || echo "no")

if [[ "$ENCRYPTED" == "yes" ]]; then
  echo "🔐 Attempting to decrypt..."
  # TODO: Replace with actual decryption command using $MY_KEY
  cp "$SHARED_FILE" "$SANDBOX/decrypted-$(basename "$SHARED_FILE")"
  echo "✅ Decrypted (simulation only)"
else
  cp "$SHARED_FILE" "$SANDBOX/$(basename "$SHARED_FILE")"
  echo "📥 Copied to sandbox for review."
fi

echo "📦 Recent sandbox contents:"
ls -1 "$SANDBOX"/*.md 2>/dev/null | tail -n 5
