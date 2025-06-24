#!/bin/bash
# uDOS_Launcher.sh – Opens a new Terminal window and launches uDOS
# uDOS by Master & Otter 🦦

echo "📦 uDOS is launching in a new Terminal window..."
sleep 0.8
osascript <<APPLESCRIPT
tell application "Terminal"
  set alreadyOpen to false
  repeat with w in windows
    if name of w contains "uDOS" then
      set alreadyOpen to true
      exit repeat
    end if
  end repeat

  if not alreadyOpen then
    do script "cd ~/uDOS/launcher && ./uDOS_Run.sh"
    delay 0.5
    set bounds of front window to {100, 100, 1380, 820}
  end if
end tell
APPLESCRIPT