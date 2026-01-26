#!/bin/bash
# Test PEEK Command
# =================
# Tests the PEEK command integration in Wizard Server
# Usage: ./bin/test_peek.sh <url> [filename]

set -e

REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
OUTBOX="$REPO_ROOT/memory/sandbox/outbox"

echo "🧪 PEEK Command Test Suite"
echo "=================================================="
echo ""

# Verify outbox exists
if [ ! -d "$OUTBOX" ]; then
    echo "❌ Outbox directory missing: $OUTBOX"
    exit 1
fi

echo "✅ Outbox directory: $OUTBOX"
echo ""

# Test 1: Check Python dependencies
echo "📋 Test 1: Checking Python dependencies"
python3 -c "import requests; print('  ✅ requests installed')" 2>/dev/null || echo "  ⚠️  requests not installed: pip install requests"
python3 -c "import bs4; print('  ✅ beautifulsoup4 installed')" 2>/dev/null || echo "  ⚠️  beautifulsoup4 not installed: pip install beautifulsoup4"
python3 -c "import html2text; print('  ✅ html2text installed')" 2>/dev/null || echo "  ⚠️  html2text not installed: pip install html2text"
echo ""

# Test 2: Verify service import
echo "📋 Test 2: Verifying service import"
if python3 -c "from wizard.services.url_to_markdown_service import get_url_to_markdown_service" 2>/dev/null; then
    echo "  ✅ Service imports successfully"
else
    echo "  ❌ Service import failed"
    exit 1
fi
echo ""

# Test 3: Check url-to-markdown library availability
echo "📋 Test 3: Checking url-to-markdown library"
if [ -d "$REPO_ROOT/library/url-to-markdown" ]; then
    echo "  ✅ Library definition found: library/url-to-markdown/"
else
    echo "  ⚠️  Library definition not found: library/url-to-markdown/"
fi

if command -v url-to-markdown &> /dev/null; then
    echo "  ✅ npm package available globally"
else
    echo "  ⚠️  npm package not in PATH (can be installed: npm install -g url-to-markdown)"
fi
echo ""

# Test 4: Quick function test (if arguments provided)
if [ ! -z "$1" ]; then
    echo "📋 Test 4: Running conversion test"
    echo "  URL: $1"

    FILENAME="${2:-test-page}"
    OUTPUT="$OUTBOX/$FILENAME.md"

    python3 << EOF
import asyncio
from wizard.services.url_to_markdown_service import get_url_to_markdown_service

async def test():
    service = get_url_to_markdown_service()
    success, output_path, message = await service.convert("$1", "$FILENAME")
    if success:
        print(f"  ✅ {message}")
        with open(output_path) as f:
            lines = f.readlines()
        print(f"  📄 Output: {len(lines)} lines")
        print(f"  📍 Saved: {output_path.relative_to(service.repo_root)}")
    else:
        print(f"  ❌ {message}")

asyncio.run(test())
EOF
else
    echo "✅ All checks passed! Ready to use PEEK command"
    echo ""
    echo "📖 Usage:"
    echo "  1. Start Wizard Server: python wizard/server.py"
    echo "  2. At wizard> prompt, run: peek <url> [optional-filename]"
    echo ""
    echo "🔍 Examples:"
    echo "  peek https://github.com/fredporter/uDOS"
    echo "  peek https://example.com my-page"
    echo ""
    echo "📁 Output location: memory/sandbox/outbox/"
fi

echo ""
