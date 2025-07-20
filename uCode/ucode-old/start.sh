#!/bin/bash
cd "$(dirname "$0")/.." || exit 1
# Canonical startup for uDOS - v1.7.1 Reorganized

# Set environment variables
UHOME="${HOME}/uDOS"
UROOT="$(pwd)"

mkdir -p "$UHOME/uMemory"

if [ ! -s "sandbox/identity.md" ]; then
  # No logging if headless
  echo "🧑 Creating new user profile..."
  bash "uCode/structure.sh" build --input
  bash "uCode/check.sh" all
else
  USERNAME=$(grep 'Username:' sandbox/identity.md | cut -d ':' -f2 | xargs)
  [[ -z "$USERNAME" ]] && USERNAME="user"
  echo "✅ Found user profile: sandbox/identity.md"
  echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
  echo "🦦 Welcome back to uDOS, $USERNAME!"
  echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
fi

echo ""
echo "🌀 uDOS started successfully."
echo "Type 'help' or 'dash' to begin."

bash "$UROOT/uCode/ucode.sh"
