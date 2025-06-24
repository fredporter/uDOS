tell application "Terminal"
  activate
  delay 0.3

  set newTab to do script "cd ~/uDOS/launcher && ./uDOS_Run.sh"
  delay 0.7

  -- Resize and name the window
  set bounds of front window to {100, 100, 1380, 820}
  set custom title of front window to "uDOS"
end tell