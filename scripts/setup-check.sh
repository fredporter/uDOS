#!/bin/bash
# setup-check.sh — Validate uOS setup, initialize user/session/version

BASE="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
UMEM="$BASE/uMemory"
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
USER_FILE="$UMEM/state/user.md"
echo ""
echo "👤 User configuration:"
if [ -f "$USER_FILE" ]; then
  echo "$pass Found user file."
else
  echo "$fail No user file found. Starting new user setup..."

  read -p "🪪 Enter your username: " uname
  uid=$(openssl rand -hex 3)
  created=$(date '+%Y-%m-%d %H:%M:%S')

  cat > "$USER_FILE" <<EOF
# uOS User Profile

**Username**: $uname  
**User ID**: $uid  
**Created**: $created  

Welcome to uOS, $uname!
EOF

  echo "✅ Created: state/user.md"
  echo "👋 Welcome, $uname. Your ID is $uid."
fi

# -------------------------------------
# 5. Version file check
VERSION_FILE="$UMEM/state/version.md"
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
SESSION_FILE="$UMEM/state/session.md"
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

# Create fresh move index for this session
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