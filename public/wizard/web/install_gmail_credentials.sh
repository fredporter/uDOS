#!/bin/bash
# Install Gmail Credentials Helper

echo "🔍 Looking for downloaded credentials..."
echo ""

# Find most recent client_secret file in Downloads
LATEST=$(ls -t ~/Downloads/client_secret_*.json 2>/dev/null | head -1)

if [ -z "$LATEST" ]; then
    echo "❌ No credentials file found in ~/Downloads/"
    echo ""
    echo "Expected filename pattern: client_secret_*.json"
    echo ""
    echo "Please:"
    echo "  1. Download OAuth credentials from Google Cloud Console"
    echo "  2. Make sure file is in ~/Downloads/"
    echo "  3. Run this script again"
    echo ""
    exit 1
fi

echo "✅ Found: $LATEST"
echo ""
echo "📋 File info:"
ls -lh "$LATEST"
echo ""

# Copy to uDOS
TARGET="/Users/fredbook/Code/uDOS/memory/system/user/gmail_credentials.json"
cp "$LATEST" "$TARGET"

# Secure permissions
chmod 600 "$TARGET"

echo "✅ Installed to: $TARGET"
echo ""
echo "📋 Verification:"
ls -lh "$TARGET"
echo ""
echo "🎉 Setup complete!"
echo ""
echo "Next steps:"
echo "  1. Start OAuth server: python wizard/web/gmail_oauth_server.py"
echo "  2. Visit: http://127.0.0.1:8080/gmail/"
echo "  3. Click 'Sign in with Google'"
echo ""
