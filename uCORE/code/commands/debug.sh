#!/bin/bash
# User-friendly debug command
# Usage: DEBUG [logs|health|reset|test]

UDOS_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/../../.." && pwd)"
source "$UDOS_ROOT/dev/scripts/enhanced-debug.sh"

case "${1:-help}" in
    "logs"|"log")
        show_logs
        ;;
    "health"|"check")
        check_system
        ;;
    "reset"|"retry")
        retry_healing
        ;;
    "test")
        "$UDOS_ROOT/dev/scripts/test-debug-system.sh"
        ;;
    "help"|*)
        echo "🔧 uDOS Debug Commands:"
        echo "  DEBUG logs   - Show recent error logs and adventure entries"
        echo "  DEBUG health - Check system health status"
        echo "  DEBUG reset  - Reset error attempt counters"
        echo "  DEBUG test   - Run full debug system test"
        ;;
esac
