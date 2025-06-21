#!/bin/bash

# ┌────────────────────────────────────────┐
# │   🧠 uOS In-Container Launch Script     │
# └────────────────────────────────────────┘

# Log folder
LOG_DIR="/uMemory/logs/system"
mkdir -p "$LOG_DIR"
LOG_FILE="$LOG_DIR/launch-$(date '+%Y-%m-%d_%H-%M-%S').log"

# Default values
EDITOR="${EDITOR:-nano}"
SCRIPT="main.py"
MODE="interactive"

echo "🚀 uOS is starting..." | tee -a "$LOG_FILE"

# Optional: check for dependencies
echo "🔍 Verifying Python entry script: $SCRIPT" | tee -a "$LOG_FILE"
if [[ ! -f "$SCRIPT" ]]; then
  echo "❌ ERROR: Cannot find $SCRIPT in working directory: $(pwd)" | tee -a "$LOG_FILE"
  exit 1
fi

# Parse command-line args
while [[ $# -gt 0 ]]; do
  case "$1" in
    --dev) MODE="dev"; shift ;;
    --script) SCRIPT="$2"; shift 2 ;;
    --headless) MODE="headless"; shift ;;
    -h|--help)
      echo "Usage: $0 [--dev] [--headless] [--script path/to/script.py]"
      exit 0
      ;;
    *) echo "⚠️ Unknown option: $1"; shift ;;
  esac
done

# Log mode
echo "📦 Launch Mode: $MODE" | tee -a "$LOG_FILE"
echo "📄 Script: $SCRIPT" | tee -a "$LOG_FILE"

# Main execution block
case "$MODE" in
  interactive)
    echo "👨‍💻 Launching interactive shell..." | tee -a "$LOG_FILE"
    python3 "$SCRIPT" | tee -a "$LOG_FILE"
    ;;
  dev)
    echo "🧪 Developer mode — shell with editor: $EDITOR" | tee -a "$LOG_FILE"
    $EDITOR "$SCRIPT"
    exec bash
    ;;
  headless)
    echo "🤖 Headless execution (non-interactive)" | tee -a "$LOG_FILE"
    python3 "$SCRIPT" > /dev/null 2>&1 &
    ;;
  *)
    echo "❌ Unknown mode: $MODE" | tee -a "$LOG_FILE"
    exit 1
    ;;
esac

