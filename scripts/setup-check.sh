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
USER_FILE="$BASE/sandbox/user.txt"
if [ ! -f "$USER_FILE" ]; then
  echo "👤 No user profile found — starting first-time setup."

  while true; do
    read -p "🪪 Choose your username: " uname
    if [[ "$uname" =~ ^[a-zA-Z0-9_-]+$ ]]; then
      break
    else
      echo "❌ Invalid username. Use only letters, numbers, dashes or underscores."
    fi
  done

  read -p "🌍 Where in the world are you now? " location
  read -p "🎯 What's your mission today? " mission
  read -p "🏛️ What kind of legacy will you leave? " legacy

  while true; do
    read -p "🔒 Choose a sharing level [0] tomb (closed - default), [1] crypt (explicit sharing), or [2] beacon (open)? " sharing
    if [[ "$sharing" == "1" || "$sharing" == "2" ]]; then
      break
    else
      sharing="0"
      break
    fi
  done

  while true; do
    read -p "⏳ How long does this instance live? [0] infinite moves (default), or type number of moves in 000s from 1 to 999 " lifespan
    if [[ "$lifespan" == "0" ]]; then
      break
    elif [[ "$lifespan" =~ ^[0-9]{3}$ ]] && [[ "$lifespan" -ge 1 ]] && [[ "$lifespan" -le 999 ]]; then
      break
    else
      echo "❌ Must be '0' or a number from 001 to 999."
    fi
  done

  while true; do
    read -s -p "🔑 Set a password: " password
    echo
    read -s -p "🔑 Confirm your password: " password_confirm
    echo
    if [ "$password" == "$password_confirm" ] && [ -n "$password" ]; then
      break
    else
      echo "❌ Passwords do not match or empty. Please try again."
    fi
  done

  created=$(date '+%Y-%m-%d %H:%M:%S')
  version=$(git -C "$BASE" describe --tags 2>/dev/null || echo "v0.0.1")

  cat > "$USER_FILE" <<EOF
Username: $uname
Password: $password
EOF

  cat > "$STATE/instance.md" <<EOF
Created: $created
Location: $location
Mission: $mission
Legacy: $legacy
Lifespan: $lifespan
Sharing: $sharing
uOS Version: $version
EOF

  echo "✅ User profile created: $USER_FILE"
  echo "👋 Welcome, $uname."
fi

# -------------------------------------
# 5. Version file check
VERSION_FILE="$BASE/sandbox/version.txt"
echo ""
echo "📦 uOS Version:"
if [ -f "$VERSION_FILE" ]; then
  echo "$pass Found version.txt"
else
  version=$(git -C "$BASE" describe --tags 2>/dev/null || echo "v0.0.1")
  echo "$version" > "$VERSION_FILE"
  echo "$pass Initialized version.txt with $version"
fi

# -------------------------------------
echo ""
echo "🧪 uOS setup complete."