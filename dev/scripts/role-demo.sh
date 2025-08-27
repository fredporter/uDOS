#!/bin/bash
# Demo script showing role-based error handling differences

UDOS_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
source "$UDOS_ROOT/dev/scripts/enhanced-debug.sh"

echo "🎭 Role-Based Error Handling Demo"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"

# Test as user
echo ""
echo "👤 As Regular User:"
export UDOS_CURRENT_ROLE="user"
export UDOS_DEV_MODE="false"
setup_debug_config

# Trigger a permission error
echo "Attempting permission error..."
chmod -x /tmp/test_error.sh 2>/dev/null || true
echo '#!/bin/bash' > /tmp/test_error.sh
echo 'echo "test"' >> /tmp/test_error.sh
/tmp/test_error.sh 2>&1 || echo "(Error handled gracefully for user)"

echo ""
echo "🛡️ As Admin:"
export UDOS_CURRENT_ROLE="admin"
setup_debug_config

# Trigger missing file error
echo "Attempting missing file error..."
cat /tmp/nonexistent_file_demo.txt 2>&1 || echo "(Error handled with moderate detail)"

echo ""
echo "👑 As Developer:"
export UDOS_CURRENT_ROLE="wizard"
export UDOS_DEV_MODE="true"
setup_debug_config

# Show debug info
show_debug_info

# Clean up
rm -f /tmp/test_error.sh
