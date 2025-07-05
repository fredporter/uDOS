#!/bin/bash
# uDOS_Run.sh — Debugging wrapper for launching uDOS

echo "✅ uDOS_Run.sh reached" | tee -a /tmp/uDOS_debug.log
cd "$(dirname "$0")/../" || { echo "❌ Failed to cd to project root" | tee -a /tmp/uDOS_debug.log; exit 1; }
echo "📂 Now in: $(pwd)" | tee -a /tmp/uDOS_debug.log
exec bash scripts/start.sh
