#!/bin/bash
# Create Automator-based uDOS launcher
# This creates a native macOS app using Automator

echo "🤖 Creating Automator-based uDOS Launcher"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"

AUTOMATOR_APP="$HOME/Desktop/uDOS Launcher.app"

# Create Automator app
/usr/bin/osascript <<EOF
tell application "Automator"
    set myWorkflow to make new workflow with properties {workflow type:application}
    
    -- Add Run Shell Script action
    tell myWorkflow
        set myAction to make new action with properties {name:"Run Shell Script"}
        tell myAction
            set value of setting "inputMethod" to 0
            set value of setting "COMMAND_STRING" to "#!/bin/bash
# uDOS Launcher Script

UDOS_PATH=\"\$HOME/uDOS\"

if [[ ! -d \"\$UDOS_PATH\" ]]; then
    osascript -e 'display dialog \"uDOS not found at ~/uDOS. Please clone the repository first.\" buttons {\"OK\"} default button \"OK\" with icon stop'
    exit 1
fi

if command -v code &> /dev/null; then
    choice=\$(osascript -e 'display dialog \"Choose launch method:\" buttons {\"Terminal\", \"VS Code\"} default button \"VS Code\"' -e 'button returned of result')
    
    if [[ \"\$choice\" == \"VS Code\" ]]; then
        cd \"\$UDOS_PATH\"
        code .
        osascript -e 'display notification \"uDOS opened in VS Code!\" with title \"uDOS\"'
    else
        cd \"\$UDOS_PATH\"
        osascript -e 'tell application \"Terminal\" to do script \"cd \$UDOS_PATH && ./start-udos.sh\"'
    fi
else
    cd \"\$UDOS_PATH\"
    osascript -e 'tell application \"Terminal\" to do script \"cd \$UDOS_PATH && ./start-udos.sh\"'
fi"
        end tell
    end tell
    
    save myWorkflow in "$AUTOMATOR_APP"
    close myWorkflow
end tell
EOF

if [[ -f "$AUTOMATOR_APP" ]]; then
    echo "✅ Automator app created: $AUTOMATOR_APP"
    echo "📱 You can drag this to Applications or Dock"
    open -R "$AUTOMATOR_APP"
else
    echo "❌ Failed to create Automator app"
fi
