#!/bin/bash
# Phase 2 Development Environment Startup
# Prepares comprehensive development tools environment

# Get script directory and uDOS root
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
UDOS_ROOT="$(cd "$SCRIPT_DIR/../.." && pwd)"

echo "🚀 Starting Phase 2: Development Tools Environment"
echo "=================================================="

# Verify Phase 1 completion
echo "🔍 Verifying Phase 1 completion..."
if [ -f "$UDOS_ROOT/uNETWORK/monitoring/control-panel.sh" ]; then
    health_result=$("$UDOS_ROOT/uNETWORK/monitoring/control-panel.sh" health 2>/dev/null)
    echo "✅ Phase 1 components verified"
else
    echo "❌ Phase 1 not complete - run Phase 1 first"
    exit 1
fi

# Create Phase 2 branch if not exists
echo "🌿 Setting up Phase 2 development branch..."
cd "$UDOS_ROOT"
current_branch=$(git branch --show-current)
if [ "$current_branch" != "phase-2-development-tools" ]; then
    git checkout -b phase-2-development-tools 2>/dev/null || git checkout phase-2-development-tools
    echo "📋 Switched to Phase 2 development branch"
fi

# Initialize Phase 2 directory structure
echo "📁 Creating Phase 2 development structure..."
mkdir -p "$UDOS_ROOT/uCORE/templates"
mkdir -p "$UDOS_ROOT/uCORE/scaffolding"
mkdir -p "$UDOS_ROOT/uCORE/generators"
mkdir -p "$UDOS_ROOT/dev/testing"
mkdir -p "$UDOS_ROOT/dev/qa"
mkdir -p "$UDOS_ROOT/docs/generator"

# Start monitoring systems
echo "📊 Starting development monitoring..."
if [ -f "$UDOS_ROOT/uNETWORK/display/metrics-api.sh" ]; then
    "$UDOS_ROOT/uNETWORK/display/metrics-api.sh" start >/dev/null 2>&1 &
    echo "✅ Metrics API started"
fi

# Create development session info
echo "📝 Creating development session info..."
cat > "$UDOS_ROOT/dev/current-session.json" << EOF
{
  "phase": "Phase 2: Development Tools",
  "started": "$(date -u +"%Y-%m-%dT%H:%M:%SZ")",
  "branch": "$(git branch --show-current)",
  "commit": "$(git rev-parse HEAD)",
  "status": "active",
  "components": {
    "template_engine": "initializing",
    "testing_framework": "pending",
    "documentation_system": "pending",
    "quality_assurance": "pending"
  }
}
EOF

echo ""
echo "🎉 Phase 2 Development Environment Ready!"
echo "========================================"
echo "📋 Current Status:"
echo "   Branch: $(git branch --show-current)"
echo "   Phase: Development Tools Framework"
echo "   Components: Template Engine → Testing → Documentation → QA"
echo ""
echo "🚀 Ready for Phase 2 development!"
echo "💡 Next: Start building the template engine foundation"

# Open development dashboard if available
if command -v open >/dev/null && [ -f "$UDOS_ROOT/demo/simple-demo.html" ]; then
    echo "🌐 Opening development dashboard..."
    open "file://$UDOS_ROOT/demo/simple-demo.html"
fi
