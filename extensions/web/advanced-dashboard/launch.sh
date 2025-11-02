#!/bin/bash

# uDOS Advanced Dashboard Launcher
# Part of uDOS v1.0.10 - Option C Implementation

echo "🚀 Starting uDOS Advanced Dashboard..."
echo "📊 Combining C64 CSS3, Teletext, and Modern Web Technologies"
echo ""

# Check if we're in the right directory
if [ ! -d "extensions/web/advanced-dashboard" ]; then
    echo "❌ Error: Must be run from uDOS root directory"
    echo "   Current directory: $(pwd)"
    echo "   Expected structure: ./extensions/web/advanced-dashboard/"
    exit 1
fi

# Check if C64 CSS3 is installed
if [ ! -d "extensions/web/c64css3" ]; then
    echo "⚠️  C64 CSS3 framework not found. Installing..."
    cd extensions/web
    git clone https://github.com/RoelN/c64css3.git
    cd ../..
    echo "✅ C64 CSS3 framework installed"
fi

# Check if teletext framework exists
if [ ! -d "extensions/web/teletext" ]; then
    echo "❌ Error: Teletext framework not found"
    echo "   Expected: ./extensions/web/teletext/"
    exit 1
fi

# Start web server
echo "🌐 Starting web server on port 8080..."
cd extensions/web

# Kill any existing server on port 8080
lsof -ti:8080 | xargs kill -9 2>/dev/null || true

# Start new server
python3 -m http.server 8080 &
SERVER_PID=$!

echo "✅ Web server started (PID: $SERVER_PID)"
echo ""
echo "🎮 uDOS Advanced Dashboard is now running!"
echo ""
echo "📍 Access URLs:"
echo "   🖥️  Main Dashboard: http://localhost:8080/advanced-dashboard/"
echo "   🎯 C64 Demo:       http://localhost:8080/c64css3/"
echo "   📺 Teletext:      http://localhost:8080/teletext/"
echo "   🎨 NES Framework: http://localhost:8080/css-frameworks/nes-demo/"
echo "   🖱️  Classicy:      http://localhost:8080/classicy-desktop/"
echo ""
echo "⌨️  Keyboard Shortcuts:"
echo "   Ctrl+T     - Cycle themes"
echo "   Alt+1-8    - Switch modules"
echo "   F1         - Help"
echo ""
echo "🎨 Available Themes:"
echo "   • Retro Classic (Default)"
echo "   • Commodore 64"
echo "   • Teletext Green"
echo "   • Modern Dark"
echo ""
echo "🔧 Features:"
echo "   ✓ Real-time system monitoring"
echo "   ✓ C64 BASIC simulator"
echo "   ✓ Teletext data streams"
echo "   ✓ Interactive terminal"
echo "   ✓ Responsive design"
echo "   ✓ Typography system integration"
echo ""
echo "📱 Responsive Breakpoints:"
echo "   🖥️  Desktop:  1200px+ (3-column layout)"
echo "   📱 Tablet:   768-1200px (2-column layout)"
echo "   📱 Mobile:   <768px (single column)"
echo ""

# Function to open browser (optional)
open_browser() {
    if command -v open &> /dev/null; then
        # macOS
        open "http://localhost:8080/advanced-dashboard/"
    elif command -v xdg-open &> /dev/null; then
        # Linux
        xdg-open "http://localhost:8080/advanced-dashboard/"
    elif command -v start &> /dev/null; then
        # Windows
        start "http://localhost:8080/advanced-dashboard/"
    else
        echo "🌐 Please open your browser and navigate to:"
        echo "   http://localhost:8080/advanced-dashboard/"
    fi
}

# Ask if user wants to open browser
echo "🌐 Would you like to open the dashboard in your browser? (y/n)"
read -n 1 -r
echo ""
if [[ $REPLY =~ ^[Yy]$ ]]; then
    echo "🚀 Opening dashboard in browser..."
    open_browser
fi

echo ""
echo "ℹ️  Dashboard is running in the background"
echo "   Press Ctrl+C to stop the server"
echo "   Server PID: $SERVER_PID"
echo ""
echo "📊 Enjoy the retro-futuristic dashboard experience!"

# Wait for Ctrl+C
trap 'echo ""; echo "🛑 Stopping server..."; kill $SERVER_PID 2>/dev/null; echo "✅ Server stopped"; exit 0' INT

# Keep script running
wait $SERVER_PID
