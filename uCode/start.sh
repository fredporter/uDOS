#!/bin/bash
cd "$(dirname "$0")/.." || exit 1
# Canonical startup for uDOS 

mkdir -p "$UROOT/sandbox"

if [ ! -s "sandbox/user.md" ]; then
  # No logging if headless
  echo "🧑 Creating new user profile..."
  bash "$UROOT/uCode/structure.sh" build --input
  bash "$UROOT/uCode/check.sh" all
else
  USERNAME=$(grep 'Username:' sandbox/user.md | cut -d ':' -f2 | xargs)
  [[ -z "$USERNAME" ]] && USERNAME="user"
  echo "✅ Found user profile: sandbox/user.md"
  echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
  echo "🦦 Welcome back to uDOS, $USERNAME!"
  echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
fi

echo ""
echo "🌀 uDOS started successfully."
echo "Type 'help' or 'dash' to begin."

bash "$UROOT/uCode/uCode.sh"
