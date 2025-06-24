#!/bin/bash
# app-wrapper.sh – Thin wrapper to open Terminal and run uDOS_Launcher.sh
# uDOS by Master & Otter 🦦 v1.0

osascript <<EOF
tell application "Terminal"
  activate
  do script "~/uDOS/launcher/uDOS_Launcher.sh"
end tell
EOF