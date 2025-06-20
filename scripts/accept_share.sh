#!/bin/bash

# === uOS Move 010: Accept & Validate Shared File ===

SANDBOX="$HOME/uOS/sandbox"
MY_DEVICE_ID="frogbyte-999"
MY_KEY="$HOME/.uOS/keys/private.pem"

read -p "📄 Path to incoming shared .md file: " SHARED_FILE

if [[ ! -f "$SHARED_FILE" ]]; then
  echo "❌ File not found."
  exit 1
fi

echo "🔍 Checking sharing metadata..."

# Extract sharing metadata from frontmatter
SHARE_OK=$(grep -q "share: true" "$SHARED_FILE" && echo "yes" || echo "no")
AUTHORIZED=$(grep -q "$MY_DEVICE_ID" "$SHARED_FILE" && echo "yes" || echo "no")
EXPIRES=$(grep 'expires:' "$SHARED_FILE" | awk '{print $2}')
NOW=$(date '+%Y-%m-%d')

if [[ "$SHARE_OK" != "yes" || "$AUTHORIZED" != "yes" ]]; then
  echo "⛔ Not authorized for this file."
  exit 1
fi

if [[ "$NOW" > "$EXPIRES" ]]; then
  echo "⏳ Share has expired: $EXPIRES"
  exit 1
fi

# Simulate decryption process
ENCRYPTED=$(grep -q "encryption: true" "$SHARED_FILE" && echo "yes" || echo "no")
if [[ "$ENCRYPTED" == "yes" ]]; then
  echo "🔐 Attempting to decrypt..."
  # Simulated decryption (add real OpenSSL/GPG logic later)
  cp "$SHARED_FILE" "$SANDBOX/decrypted-$(basename "$SHARED_FILE")"
  echo "✅ Decrypted (simulation only)"
else
  cp "$SHARED_FILE" "$SANDBOX/$(basename "$SHARED_FILE")"
  echo "📥 Copied to sandbox for review."
fi

echo "📦 Sandbox contents:"
ls -1 "$SANDBOX"/*.md | tail -n 5