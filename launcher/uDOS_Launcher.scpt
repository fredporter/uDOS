tell application "Terminal"
  activate
  delay 0.3

  set newTab to do script "cd ~/uDOS/launcher && ./uDOS_Run.sh"
  delay 1.2

  -- Resize and name the window
  set winCount to count windows
  set bounds of window winCount to {100, 100, 1380, 820}
  set custom title of front window to "uDOS"
end tell