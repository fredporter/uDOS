#!/bin/bash
set -e

echo "🚀 uOS is starting..."

# Verify uCode.sh exists
if [ ! -f scripts/uCode.sh ]; then
  echo "❌ ERROR: scripts/uCode.sh not found in /uOS"
  exit 1
fi

echo "✅ Found uCode.sh, launching..."
bash scripts/uCode.sh