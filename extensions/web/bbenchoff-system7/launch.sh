#!/bin/bash
# Launch script for BBenchoff System 7 Extension
# Based on Brian Benchoff's System 7 CSS Recreation

echo "🍎 Starting BBenchoff System 7 Extension..."
echo "📁 Location: /Users/fredbook/Code/uDOS/extensions/web/bbenchoff-system7"
echo "🌐 URL: http://localhost:8083"
echo ""

# Check if port is already in use
if lsof -Pi :8083 -sTCP:LISTEN -t >/dev/null ; then
    echo "⚠️  Port 8083 is already in use. Stopping existing server..."
    pkill -f "python.*8083"
    sleep 2
fi

# Start the web server
echo "🚀 Starting web server on port 8083..."
cd "$(dirname "$0")"
python3 -m http.server 8083 &
SERVER_PID=$!

# Wait for server to start
sleep 2

# Check if server started successfully
if ps -p $SERVER_PID > /dev/null 2>&1; then
    echo "✅ BBenchoff System 7 Extension is running!"
    echo ""
    echo "🎯 Features:"
    echo "   • Authentic System 7 interface recreation"
    echo "   • Working window manager with drag/resize"
    echo "   • Classic Mac menu system"
    echo "   • Calculator app with keyboard support"
    echo "   • State persistence across sessions"
    echo "   • Desktop file system navigation"
    echo ""
    echo "🔗 Access URLs:"
    echo "   • Main Interface: http://localhost:8083"
    echo "   • Compare with Custom: http://localhost:8082 (Advanced Dashboard)"
    echo "   • Custom System 7: http://localhost:8081 (if running)"
    echo ""
    echo "⌨️  Keyboard Shortcuts:"
    echo "   • Cmd/Ctrl+W: Close window"
    echo "   • Cmd/Ctrl+H: Hide application"
    echo "   • F1: About dialog"
    echo "   • Calculator: Number keys, +, -, *, /, =, C"
    echo ""
    echo "🛑 To stop: pkill -f \"python.*8083\""
    echo ""

    # Try to open in browser if on macOS
    if [[ "$OSTYPE" == "darwin"* ]]; then
        echo "🌐 Opening in browser..."
        open "http://localhost:8083"
    fi

    echo "💾 Server PID: $SERVER_PID"
    echo "📊 Server logs will appear below..."
    echo "   (Press Ctrl+C to stop server)"
    echo ""

    # Keep script running and show server output
    wait $SERVER_PID
else
    echo "❌ Failed to start server!"
    exit 1
fi
