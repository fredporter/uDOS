

#!/bin/bash
# uDOS_Launcher.sh – Opens a new Terminal window and launches uDOS
# uDOS by Master & Otter 🦦

echo "📦 uDOS is launching in a new Terminal window..."
sleep 0.8
osascript <<APPLESCRIPT
tell application "Terminal"
  do script "cd ~/uDOS && bash uDOS_Run.sh"
  delay 0.5
  set bounds of front window to {100, 100, 1380, 820}
end tell
APPLESCRIPT