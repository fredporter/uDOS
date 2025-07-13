#!/bin/bash
echo "🧹 Cleaning up uScript workspace..."

# Remove logs
rm -f ./logs/*.log
rm -f ./logs/ucode.log

# Optionally reset variables
echo '{}' > ./vars/user-vars.json

# Optionally remove temp files
find . -name '*.tmp' -delete

echo "✅ Cleanup complete."