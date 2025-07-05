#!/bin/bash
# Canonical startup for uDOS 

mkdir -p sandbox

if [ ! -s "sandbox/user.md" ]; then
  # No logging if headless
  echo "🧑 Creating new user profile..."
  bash "$UROOT/scripts/make-structure.sh"
  bash "$UROOT/scripts/check-setup.sh"
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

bash "$UROOT/scripts/uCode.sh"
