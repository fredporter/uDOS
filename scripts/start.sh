#!/bin/bash
if [ ! -s "sandbox/user.md" ]; then
  echo "🧑 Creating new user profile..."
  bash scripts/make-structure.sh
  bash scripts/check-setup.sh
else
  USERNAME=$(grep 'Username:' sandbox/user.md | cut -d ':' -f2 | xargs)
  echo "✅ Found user profile: sandbox/user.md"
  echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
  echo "🦦 Welcome back to uDOS, $USERNAME!"
  echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
fi

exec bash scripts/uCode.sh