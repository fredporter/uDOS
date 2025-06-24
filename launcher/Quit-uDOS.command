#!/bin/bash
# Quit-uDOS.command v1.0 – Clean shutdown for Docker container
# Stop the uDOS container manually

echo "🛑 Stopping any running uDOS containers..."
docker compose down

echo "✅ uDOS container stopped."