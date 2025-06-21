#!/bin/bash
# setup-check.sh — Validate uOS setup, initialize user/session/version

BASE="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
UMEM="$BASE/uMemory"
STATE="$UMEM/state"
pass="✅"
fail="❌"

echo "🔍 Checking uOS setup..."

# -------------------------------------
# 1. Templates check
echo ""
echo "📁 Templates:"
for t in move mission milestone legacy; do
  file="$BASE/templates/${t}-template.md"
  if [ -f "$file" ]; then
    echo "$pass $t-template.md exists"
  else
    echo "$fail Missing $t-template.md"
  fi
done

# -------------------------------------
# 2. Folder structure check
echo ""
echo "📂 Required directories:"
required_dirs=( logs logs/moves logs/errors milestones missions state )
for d in "${required_dirs[@]}"; do
  path="$UMEM/$d"
  if [ -d "$path" ]; then
    echo "$pass uMemory/$d/"
  else
    echo "$fail Missing uMemory/$d/"
    mkdir -p "$path" && echo "📁 Created: uMemory/$d/"
  fi
done

# -------------------------------------
# 3. Editor check
echo ""
echo "📝 Editor availability:"
if command -v ${EDITOR:-nano} >/dev/null 2>&1; then
  echo "$pass Editor found: ${EDITOR:-nano}"
else
  echo "$fail No editor found! Set \$EDITOR or install nano/vi"
fi

# -------------------------------------
# 4. User file check
USER_FILE="$STATE/user.md"
if [ ! -f "$USER_FILE" ]; then
  echo "👤 No user profile found — starting first-time setup."

  while true; do
    read -p "🪪 Enter your username (no spaces or symbols): " uname
    if [[ "$uname" =~ ^[a-zA-Z0-9_-]+$ ]]; then
      break
    else
      echo "❌ Invalid username. Use only letters, numbers, dashes or underscores."
    fi
  done

  read -p "🌍 Location: " location
  read -p "🎯 Outline your Mission: " mission
  read -p "🏛️  What Legacy will you leave?: " legacy

  while true; do
    read -p "🔒 Privacy level [crypt/beacon]: " privacy
    if [[ "$privacy" == "crypt" || "$privacy" == "beacon" ]]; then
      break
    else
      echo "❌ Must be either 'crypt' or 'beacon'."
    fi
  done

  while true; do
    read -p "⏳ Lifespan [short/medium/long/infinite]: " lifespan
    if [[ "$lifespan" =~ ^(short|medium|long|infinite)$ ]]; then
      break
    else
      echo "❌ Must be one of: short, medium, long, infinite."
    fi
  done

  now=$(date '+%Y%m%d-%H%M%S')
  # Generate a 6-digit random number (000000 to 999999)
  rand_num=$(shuf -i 0-999999 -n 1)
  rand_num=$(printf "%06d" "$rand_num")

  uid="${uname}-${now}-${rand_num}"
  iid="${now}-${rand_num}"

  move_count=$(find "$UMEM/logs/moves/" -type f 2>/dev/null | wc -l | awk '{print $1}')
  instance_num=$((move_count + 1))

  created=$(date '+%Y-%m-%d %H:%M:%S')
  version=$(git -C "$BASE" describe --tags 2>/dev/null || echo "v0.0.1")

  cat > "$USER_FILE" <<EOF
# uOS User Profile

**Username**: $uname  
**User ID**: $uid  
**Instance ID**: $iid  
**Instance Number**: $instance_num  
**Created**: $created  
**Location**: $location  
**Mission**: $mission  
**Legacy**: $legacy  
**Lifespan**: $lifespan  
**Privacy**: $privacy  
**uOS Version**: $version

Welcome to uOS, $uname. Your instance is now active.
EOF

  echo "✅ User profile created: $USER_FILE"
  echo "✅ Created: state/user.md"
  echo "👋 Welcome, $uname. Your ID is $uid."
fi

# -------------------------------------
# 5. Version file check
VERSION_FILE="$STATE/version.md"
echo ""
echo "📦 uOS Version:"
if [ -f "$VERSION_FILE" ]; then
  echo "$pass Found version.md"
else
  version=$(git -C "$BASE" describe --tags 2>/dev/null || echo "v0.0.1")
  echo "**uOS Version**: $version" > "$VERSION_FILE"
  echo "$pass Initialized version.md with $version"
fi

# -------------------------------------
# 6. Session start and Move log index
SESSION_FILE="$STATE/session.md"
sid="sess-$(date '+%Y%m%d-%H%M')"
echo ""
echo "📆 Session startup:"
if [ -f "$SESSION_FILE" ]; then
  echo "$pass Previous session file found."
else
  echo "**Session ID**: $sid" > "$SESSION_FILE"
  echo "**Started**: $(date '+%Y-%m-%d %H:%M:%S')" >> "$SESSION_FILE"
  echo "$pass Created new session.md"
fi

MOVE_INDEX="$UMEM/logs/moves/index-$sid.md"
if [ ! -f "$MOVE_INDEX" ]; then
  echo "# Move Index – $sid" > "$MOVE_INDEX"
  echo "" >> "$MOVE_INDEX"
  echo "_All Moves from this session will be listed here._" >> "$MOVE_INDEX"
  echo "$pass Initialized: index-$sid.md"
else
  echo "$pass Move index already exists: $MOVE_INDEX"
fi

# -------------------------------------
echo ""
echo "🧪 uOS setup complete."