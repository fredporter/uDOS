

#!/bin/bash
# uDOS_Launcher.sh – Opens a new Terminal window and launches uDOS
# uDOS by Master & Otter 🦦

osascript <<APPLESCRIPT
tell application "Terminal"
  do script "cd ~/uDOS && bash uDOS_Run.sh"
  delay 0.5
  set bounds of front window to {100, 100, 1380, 820}
end tell
APPLESCRIPT