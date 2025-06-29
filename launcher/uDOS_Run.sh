#!/bin/bash
# uDOS_Run.sh – Full launch logic for uDOS (minimal tab version)
# uDOS by Master & Otter 🦦

echo "🐚 Running uDOS..."
echo "Welcome to uDOS, your personal OS 🦦"
LOGFILE=~/uDOS/logs/udos-$(date +%Y-%m-%d).log
echo "===== uDOS launch started at $(date) =====" >> "$LOGFILE"

# Navigate to uDOS directory
cd ~/uDOS || {
  echo "❌ Error: ~/uDOS directory not found."
  exit 1
}

# Check for existing user profile
if [ ! -s "sandbox/user.md" ]; then
  echo "🧑 No user profile found. Running user setup..."
  bash scripts/start.sh
else
  USERNAME=$(grep 'Username:' sandbox/user.md | cut -d ':' -f2 | xargs)
  echo "✅ Found user profile: sandbox/user.md"
  echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
  echo "🦦 Welcome back to uDOS, $USERNAME!"
  echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
fi

# Ensure Docker is running
if ! docker info >/dev/null 2>&1; then
  echo "🐳 Starting Docker Desktop..."
  open -a Docker
  while ! docker info >/dev/null 2>&1; do
    echo "⌛ Waiting for Docker to initialise..."
    echo "⌛ Waiting for Docker to initialise..." >> "$LOGFILE"
    sleep 2
  done
  echo "✅ Docker is now running." >> "$LOGFILE"
fi

# Optional: Prepare logs directory
mkdir -p ~/uDOS/logs

# Stop any existing containers
echo "🧼 Cleaning up previous uDOS containers..."
docker compose down || echo "⚠️  Nothing to stop."

# Rebuild the container
echo "🔨 Rebuilding uDOS container..."
docker compose build

# Launch interactive uDOS shell and pipe output to log
echo "🚀 Starting uDOS interactive shell..."
docker compose run --rm udos scripts/start.sh | tee -a "$LOGFILE"

echo "===== uDOS session ended at $(date) =====" >> "$LOGFILE"
