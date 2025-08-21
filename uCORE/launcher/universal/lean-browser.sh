#!/bin/bash
# uDOS Lean Browser Launcher
# Launches a minimal Chromium browser optimized for retro computing displays

# Default settings
DISPLAY_MODE="bbc"    # bbc, c64, amiga, terminal, modern
PIXEL_PERFECT=true
KIOSK_MODE=false
WIDTH=640
HEIGHT=480

# Parse command line arguments
while [[ $# -gt 0 ]]; do
    case $1 in
        --display)
            DISPLAY_MODE="$2"
            shift 2
            ;;
        --size)
            SIZE="$2"
            IFS='x' read -r WIDTH HEIGHT <<< "$SIZE"
            shift 2
            ;;
        --kiosk)
            KIOSK_MODE=true
            shift
            ;;
        --no-pixel-perfect)
            PIXEL_PERFECT=false
            shift
            ;;
        --help)
            echo "uDOS Lean Browser Launcher"
            echo "Usage: $0 [options]"
            echo ""
            echo "Options:"
            echo "  --display MODE    Set display mode (bbc, c64, amiga, terminal, modern)"
            echo "  --size WIDTHxHEIGHT  Set window size (e.g., 640x480)"
            echo "  --kiosk          Enable kiosk mode (fullscreen, no UI)"
            echo "  --no-pixel-perfect   Disable pixel perfect rendering"
            echo "  --help           Show this help message"
            echo ""
            echo "Examples:"
            echo "  $0 --display bbc --size 320x250"
            echo "  $0 --display c64 --size 320x200 --kiosk"
            echo "  $0 --display amiga --size 640x256"
            exit 0
            ;;
        *)
            echo "Unknown option: $1"
            exit 1
            ;;
    esac
done

# Set display-specific dimensions
case $DISPLAY_MODE in
    bbc)
        if [[ $WIDTH -eq 640 && $HEIGHT -eq 480 ]]; then
            WIDTH=320
            HEIGHT=250
        fi
        ;;
    c64)
        if [[ $WIDTH -eq 640 && $HEIGHT -eq 480 ]]; then
            WIDTH=320
            HEIGHT=200
        fi
        ;;
    amiga)
        if [[ $WIDTH -eq 640 && $HEIGHT -eq 480 ]]; then
            WIDTH=640
            HEIGHT=256
        fi
        ;;
esac

# Build Chromium flags
CHROMIUM_FLAGS=(
    "--app=http://localhost:8080"
    "--window-size=$WIDTH,$HEIGHT"
    "--disable-web-security"
    "--disable-features=TranslateUI,VizDisplayCompositor"
    "--disable-extensions"
    "--disable-plugins"
    "--disable-sync"
    "--disable-default-apps"
    "--disable-background-timer-throttling"
    "--disable-backgrounding-occluded-windows"
    "--disable-renderer-backgrounding"
    "--disable-background-networking"
    "--no-first-run"
    "--no-default-browser-check"
    "--disable-infobars"
    "--disable-session-crashed-bubble"
    "--disable-restore-session-state"
    "--disable-dev-shm-usage"
    "--no-sandbox"
    "--disable-gpu-sandbox"
    "--disable-software-rasterizer"
)

# Add kiosk mode flags
if [ "$KIOSK_MODE" = true ]; then
    CHROMIUM_FLAGS+=(
        "--kiosk"
        "--start-fullscreen"
        "--disable-pinch"
        "--overscroll-history-navigation=0"
    )
fi

# Add pixel perfect rendering flags
if [ "$PIXEL_PERFECT" = true ]; then
    CHROMIUM_FLAGS+=(
        "--force-device-scale-factor=1"
        "--disable-font-subpixel-positioning"
        "--disable-lcd-text"
    )
fi

echo "🚀 Launching uDOS Lean Browser..."
echo "📺 Display Mode: $DISPLAY_MODE"
echo "📏 Window Size: ${WIDTH}×${HEIGHT}"
echo "🎨 Pixel Perfect: $PIXEL_PERFECT"
echo "🖥️  Kiosk Mode: $KIOSK_MODE"
echo ""

# Check if uDOS server is running
if ! curl -s http://localhost:8080 > /dev/null; then
    echo "❌ uDOS server not running on localhost:8080"
    echo "💡 Start the server first: cd uCORE/launcher/universal/ucode-ui && python app.py"
    exit 1
fi

# Launch Chromium
echo "🌐 Starting Chromium with lean configuration..."
chromium "${CHROMIUM_FLAGS[@]}" &

# Store PID for later management
BROWSER_PID=$!
echo "🆔 Browser PID: $BROWSER_PID"

# Wait for browser to start
sleep 2

# Send display mode to uDOS interface via curl
echo "📡 Configuring display mode..."
curl -s -X POST http://localhost:8080/api/display \
    -H "Content-Type: application/json" \
    -d "{\"mode\":\"$DISPLAY_MODE\",\"width\":$WIDTH,\"height\":$HEIGHT,\"pixelPerfect\":$PIXEL_PERFECT}" \
    > /dev/null

echo "✅ uDOS Lean Browser launched successfully!"
echo "💡 Use 'display', 'size', 'kiosk', 'pixels' commands in uDOS interface"
echo "🛑 Press Ctrl+C to close browser"

# Wait for interrupt
trap "kill $BROWSER_PID 2>/dev/null; echo '🛑 Browser closed'; exit 0" INT
wait $BROWSER_PID
