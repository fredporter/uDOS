tell application "Terminal"
  activate
  delay 0.3

  do script "cd ~/uDOS/launcher && ./uDOS_Run.sh"
  delay 1.0
  try
    set bounds of front window to {100, 100, 1380, 820}
  end try
  set custom title of front window to "uDOS"
end tell