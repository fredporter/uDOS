#!/bin/bash
# Setup and build Wizard Dashboard (Svelte + Tailwind)

set -e

DASHBOARD_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

echo "🎨 Setting up Wizard Dashboard..."
echo ""

# Check Node.js
if ! command -v node &> /dev/null; then
    echo "❌ Node.js not found. Install from https://nodejs.org/"
    exit 1
fi

echo "✅ Node.js $(node --version)"
echo "✅ npm $(npm --version)"
echo ""

# Install dependencies
echo "📦 Installing dependencies..."
cd "$DASHBOARD_DIR"
npm install

# Build
echo ""
echo "🏗️  Building dashboard..."
npm run build

echo ""
echo "✅ Dashboard built successfully!"
echo "📁 Output: $DASHBOARD_DIR/dist/"
echo ""
echo "🚀 Wizard server will serve from: http://localhost:8765/"
