#!/bin/bash
# launch-uOS.sh — Boot uOS + run initial checks
set -e

echo "🚀 uOS is launching..."

# Run setup check
/scripts/setup-check.sh

# Start uCode CLI or Dashboard
/scripts/uCode.sh