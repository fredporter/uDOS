#!/bin/bash
# uDOS Desktop Launcher - Clean Single Instance Startup
cd "$(dirname "$0")"

echo "🧙‍♂️ Starting uDOS..."

# Use the managed launcher for single instance control
./uCORE/launcher/universal/start-udos-managed.sh start development
