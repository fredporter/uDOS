#!/bin/bash
# Quick Fix: Reset Secrets Tomb and Re-Enable Setup Sync
# Usage: ./wizard/tools/quick_fix_setup_sync.sh

set -e

cd "$(dirname "$0")/../.."

echo ""
echo "🔧 QUICK FIX: Setup Profile Sync"
echo "================================"
echo ""

# Check if secrets.tomb exists
if [ ! -f "wizard/secrets.tomb" ]; then
    echo "ℹ️  No secrets.tomb found. Nothing to fix!"
    echo "   Just complete the TUI setup story and it will work."
    exit 0
fi

echo "⚠️  This will reset your encrypted profiles."
echo "   You'll need to re-run the TUI setup story."
echo ""
read -p "Continue? [y/N]: " -n 1 -r
echo ""

if [[ ! $REPLY =~ ^[Yy]$ ]]; then
    echo "❌ Cancelled."
    exit 0
fi

# Backup
TIMESTAMP=$(date +%Y%m%d_%H%M%S)
BACKUP="wizard/secrets.tomb.backup.$TIMESTAMP"

echo ""
echo "📦 Creating backup: $BACKUP"
mv wizard/secrets.tomb "$BACKUP"

echo "✅ Done!"
echo ""
echo "📝 Next steps:"
echo "   1. Start Wizard Server: ./bin/ucli wizard"
echo "   2. Start uCLI: ./bin/ucli"
echo "   3. Complete the setup story questions"
echo "   4. Test: wizard> setup"
echo ""
