#!/bin/bash
# launch-uOS.sh

echo "🌀 Launching uOS..."

# Run setup check — use relative path inside container
./scripts/setup-check.sh

# Start uCode CLI or Dashboard
./scripts/uCode.sh