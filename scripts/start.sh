#!/bin/bash
if [ ! -s "sandbox/user.md" ]; then
  echo "🧑 No user profile found. Running user setup..."
  bash scripts/start.sh
else
  USERNAME=$(grep 'Username:' sandbox/user.md | cut -d ':' -f2 | xargs)
  echo "✅ Found user profile: sandbox/user.md"
  echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
  echo "🦦 Welcome back to uDOS, $USERNAME!"
  echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
fi