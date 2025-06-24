tell application "Terminal"
  activate
  do script "cd ~/uDOS/launcher && ./uDOS_Run.sh" in (make new window with profile "uDOS")
end tell