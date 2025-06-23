#!/bin/bash
# launch-uDOS.sh

echo "🌀 Launching uDOS..."

# Run setup check — use relative path inside container
./scripts/setup-check.sh

# Start uCode CLI or Dashboard
./scripts/uCode.sh