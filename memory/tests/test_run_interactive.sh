#!/bin/bash
# Test RUN command in interactive mode

cd /Users/fredbook/Code/uDOS

# Test 1: Check if RUN appears in HELP
echo "=== Test 1: Checking HELP output for RUN ==="
echo "HELP" | ./start_udos.sh 2>&1 | grep -i "RUN" | head -5

# Test 2: Try HELP RUN
echo ""
echo "=== Test 2: HELP RUN command ==="
echo "HELP RUN" | ./start_udos.sh 2>&1 | tail -30

# Test 3: Run the example script
echo ""
echo "=== Test 3: RUN examples/hello-automation.uscript ==="
echo "RUN examples/hello-automation.uscript" | ./start_udos.sh 2>&1 | tail -40

echo ""
echo "=== Tests Complete ==="
