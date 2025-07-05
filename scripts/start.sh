#!/bin/bash
# Canonical startup for uDOS (replaces uDOS_Run.sh)
mkdir -p sandbox
if [ ! -s "sandbox/user.md" ]; then
  # No logging if headless
  if [[ "$UCODE_HEADLESS" != "true" ]]; then
    echo "🧑 Creating new user profile..."
  fi
  bash scripts/make-structure.sh
  bash scripts/check-setup.sh
else
  USERNAME=$(grep 'Username:' sandbox/user.md | cut -d ':' -f2 | xargs)
  [[ -z "$USERNAME" ]] && USERNAME="user"
  if [[ "$UCODE_HEADLESS" != "true" ]]; then
    echo "✅ Found user profile: sandbox/user.md"
    echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
    echo "🦦 Welcome back to uDOS, $USERNAME!"
    echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
  fi
fi

exec bash scripts/uCode.sh

if [[ "$UCODE_HEADLESS" != "true" ]]; then
  echo ""
  echo "🌀 uDOS started successfully."
  echo "Type 'help' or 'dash' to begin."
fi