#!/bin/bash
# setup-check.sh — Validate uDOS setup, initialize user/version

BASE="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
UMEM="$BASE/uMemory"
STATE="$UMEM/state"
pass="✅"
fail="❌"

echo "🔍 Checking uDOS setup..."

# -------------------------------------
# 1. Templates check
echo ""
echo "📁 Templates:"
for t in mission milestone legacy; do
  file="$BASE/uTemplate/${t}-template.md"
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
required_dirs=( logs logs/errors milestones missions legacy state )
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
USER_FILE="$BASE/sandbox/user.md"
if [ ! -s "$USER_FILE" ]; then
  echo "👤 No user profile found or empty — starting first-time setup."

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
    read -p "🔒 Choose a sharing level [0] tomb (closed - default), [1] crypt (explicit sharing), or [2] beacon (open)? " sharing_input
    if [ "$sharing_input" == "1" ]; then
      sharing="crypt"
      echo "Selected sharing mode: crypt"
      break
    elif [ "$sharing_input" == "2" ]; then
      sharing="beacon"
      echo "Selected sharing mode: beacon"
      break
    else
      sharing="tomb"
      echo "Selected sharing mode: tomb"
      break
    fi
  done

  while true; do
    read -p "⏳ How long does this instance live? [0] infinite moves (default), or type number of moves in 000s from 1 to 999 " lifespan_input
    if [[ "$lifespan_input" == "0" ]]; then
      lifespan="0"
      echo "Lifespan set to infinite moves (0)."
      break
    elif [[ "$lifespan_input" =~ ^[0-9]{3}$ ]] && [[ "$lifespan_input" -ge 1 ]] && [[ "$lifespan_input" -le 999 ]]; then
      lifespan="$lifespan_input"
      break
    else
      lifespan="0"
      echo "Invalid input. Lifespan set to infinite moves (0)."
      break
    fi
  done

  read -s -p "🔑 Set a password (leave blank to skip): " password
  echo
  if [ -n "$password" ]; then
    read -s -p "🔑 Confirm your password: " password_confirm
    echo
    if [ "$password" != "$password_confirm" ]; then
      echo "❌ Passwords do not match. Skipping password setup."
      password=""
    fi
  fi

  created=$(date '+%Y-%m-%d %H:%M:%S')
  version=$(git -C "$BASE" describe --tags --abbrev=0 2>/dev/null || echo "uDOS Beta v1.6.1")

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
uDOS Version: $version
EOF

  echo "✅ User profile created: $USER_FILE"
  echo "👋 Welcome, $uname."
else
  echo "✅ User profile exists and is non-empty: $USER_FILE"
fi

# -------------------------------------
# 5. Version file check
VERSION_FILE="$BASE/sandbox/version.md"
echo ""
echo "📦 uDOS Version:"
if [ ! -s "$VERSION_FILE" ]; then
  version=$(git -C "$BASE" describe --tags --abbrev=0 2>/dev/null || echo "uDOS Beta v1.6.1")
  echo "$version" > "$VERSION_FILE"
  echo "$pass Initialized version.md with $version"
else
  echo "$pass Found version.md"
fi

# -------------------------------------
echo ""
echo "🧪 uDOS setup complete."