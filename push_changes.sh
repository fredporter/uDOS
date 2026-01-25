#!/bin/bash
cd /Users/fredbook/Code/uDOS

echo "=== Git Status ==="
git status --short

echo ""
echo "=== Adding changes ==="
git add -A

echo ""
echo "=== Committing ==="
git commit -m "fix: Wire up HELP command to display full command reference

- Update GridRenderer to display 'help' key from command results
- Update HelpHandler to return 'message' field in all response dicts
- Add message field showing command count to _show_all_commands()
- Suppress urllib3 SSL warning on macOS (LibreSSL vs OpenSSL)
- HELP now displays full command list organized by category
- Supports: HELP [command] | HELP CATEGORY <cat> | HELP SYNTAX <cmd>"

echo ""
echo "=== Pushing to remote ==="
git push origin main

echo ""
echo "=== Done ==="
git log --oneline -1
