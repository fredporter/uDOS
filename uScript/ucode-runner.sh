#!/bin/bash
CMD="$1"
SCRIPT="$2"

if [[ "$CMD" == "run" && "$SCRIPT" == *.md ]]; then
  LANG=$(grep -m1 '^LANGUAGE:' "$SCRIPT" | cut -d':' -f2 | xargs)
  [[ -z "$LANG" ]] && LANG="uCode"

  case "$LANG" in
    python)
      PY=$(grep -v "^'" "$SCRIPT" | grep -v "^#" | grep -v "^LANGUAGE:" | sed '/^$/d')
      TMP=$(mktemp)
      echo "$PY" > "$TMP"
      python3 "$TMP"
      rm "$TMP"
      ;;
    bash)
      SH=$(grep -v "^'" "$SCRIPT" | grep -v "^#" | grep -v "^LANGUAGE:" | sed '/^$/d')
      TMP=$(mktemp)
      echo "$SH" > "$TMP"
      bash "$TMP"
      rm "$TMP"
      ;;
    uCode|*)
      echo "[uCode] Would interpret $SCRIPT"
      ;;
  esac
else
  echo "Usage: $0 run <script.md>"
  exit 1
fi
