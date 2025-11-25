#!/bin/bash
# Quick CLI test script for uDOS
# Tests startup, a few commands, and exit

cd /Users/fredbook/Code/uDOS
source .venv/bin/activate

echo "Testing uDOS CLI (non-interactive)..."
echo ""

# Send commands via stdin
python3 uDOS.py <<EOF
help
status
blank
exit
EOF

echo ""
echo "Test complete!"
