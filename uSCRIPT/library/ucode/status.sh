#!/bin/bash
# uDOS Status Module v1.3
# Handles system status, health checks, and diagnostics

# Get uDOS paths
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
UDOS_ROOT="$(cd "$SCRIPT_DIR/../../.." UDOS_ROOT="$(cd "$SCRIPT_DIR/../../../.." && pwd)"UDOS_ROOT="$(cd "$SCRIPT_DIR/../../../.." && pwd)" pwd)"
UMEMORY="$UDOS_ROOT/uMEMORY"
UCORE="$UDOS_ROOT/uCORE"
SANDBOX="$UDOS_ROOT/sandbox"

# Colors
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

check_ucode_status() {
    echo -e "${BLUE}🔍 uDOS System Status${NC}"
    echo ""
    
    # Core system checks
    echo "Core System:"
    [[ -f "$UCORE/code/ucode-v13.sh" ]] && echo -e "  ✓ ${GREEN}Modular uCORE${NC}" || echo -e "  ✗ ${RED}Missing modular uCORE${NC}"
    [[ -f "$UDOS_ROOT/ucode.sh" ]] && echo -e "  ✓ ${GREEN}Legacy ucode.sh${NC}" || echo -e "  ✗ ${RED}Missing legacy ucode.sh${NC}"
    [[ -x "$UCORE/code/ucode-v13.sh" ]] && echo -e "  ✓ ${GREEN}Executable permissions${NC}" || echo -e "  ⚠ ${YELLOW}Check permissions${NC}"
    
    echo ""
    echo "Authentication:"
    [[ -f "$SANDBOX/user.md" ]] && echo -e "  ✓ ${GREEN}User data present${NC}" || echo -e "  ✗ ${RED}No user data${NC}"
    [[ -f "$UCORE/code/user-auth.sh" ]] && echo -e "  ✓ ${GREEN}Authentication module${NC}" || echo -e "  ✗ ${RED}Missing auth module${NC}"
    
    echo ""
    echo "Session Logging:"
    [[ -f "$UCORE/code/session-logger.sh" ]] && echo -e "  ✓ ${GREEN}Session logger${NC}" || echo -e "  ✗ ${RED}Missing session logger${NC}"
    local session_count=$(find "$UMEMORY" -name "*Session.md" 2>/dev/null | wc -l)
    echo -e "  📊 ${session_count} session logs found"
    
    echo ""
    echo "uSCRIPT Modules:"
    local module_count=$(find "$UDOS_ROOT/uSCRIPT/library/ucode" -name "*.sh" 2>/dev/null | wc -l)
    echo -e "  📦 ${module_count} modules available"
    
    echo ""
    echo "Memory System:"
    [[ -d "$UMEMORY/templates" ]] && echo -e "  ✓ ${GREEN}Templates directory${NC}" || echo -e "  ✗ ${RED}Missing templates${NC}"
    [[ -d "$UMEMORY/user" ]] && echo -e "  ✓ ${GREEN}User memory${NC}" || echo -e "  ✗ ${RED}Missing user memory${NC}"
    
    # Check recent activity
    echo ""
    echo "Recent Activity:"
    local latest_log=$(find "$UMEMORY" -name "*Session.md" -exec stat -f "%m %N" {} \; 2>/dev/null | sort -nr | head -1 | cut -d' ' -f2-)
    if [[ -n "$latest_log" ]]; then
        local log_basename=$(basename "$latest_log")
        echo -e "  📝 Latest session: ${log_basename}"
    else
        echo -e "  📝 No recent sessions"
    fi
}

check_system_health() {
    echo -e "${BLUE}🏥 System Health Check${NC}"
    echo ""
    
    # Disk space check
    local disk_usage=$(df "$UDOS_ROOT" | tail -1 | awk '{print $5}' | tr -d '%')
    echo "Storage:"
    if [[ $disk_usage -lt 80 ]]; then
        echo -e "  ✓ ${GREEN}Disk usage: ${disk_usage}%${NC}"
    elif [[ $disk_usage -lt 90 ]]; then
        echo -e "  ⚠ ${YELLOW}Disk usage: ${disk_usage}%${NC}"
    else
        echo -e "  ✗ ${RED}Disk usage: ${disk_usage}% (Critical)${NC}"
    fi
    
    # Memory check
    echo ""
    echo "Performance:"
    local memory_pressure=$(memory_pressure 2>/dev/null | grep "System-wide memory free percentage" | awk '{print $5}' | tr -d '%' 2>/dev/null || echo "N/A")
    if [[ "$memory_pressure" != "N/A" ]]; then
        echo -e "  📊 Memory free: ${memory_pressure}%"
    fi
    
    # Process check
    local ucode_processes=$(pgrep -f "ucode" | wc -l)
    echo -e "  🔄 Active ucode processes: ${ucode_processes}"
    
    # File permissions
    echo ""
    echo "Permissions:"
    local exec_files=0
    local total_files=0
    while IFS= read -r -d '' file; do
        ((total_files++))
        [[ -x "$file" ]] && ((exec_files++))
    done < <(find "$UCORE/code" -name "*.sh" -print0 2>/dev/null)
    
    echo -e "  🔐 Executable scripts: ${exec_files}/${total_files}"
}

show_module_status() {
    echo -e "${BLUE}📦 Module Status${NC}"
    echo ""
    
    local ucode_modules="$UDOS_ROOT/uSCRIPT/library/ucode"
    
    if [[ -d "$ucode_modules" ]]; then
        echo "Available modules:"
        for module in "$ucode_modules"/*.sh; do
            if [[ -f "$module" ]]; then
                local name=$(basename "$module" .sh)
                if [[ -x "$module" ]]; then
                    echo -e "  ✓ ${GREEN}${name}${NC}"
                else
                    echo -e "  ⚠ ${YELLOW}${name} (not executable)${NC}"
                fi
            fi
        done
    else
        echo -e "  ✗ ${RED}No modules directory found${NC}"
    fi
}

show_quick_stats() {
    local uptime=$(uptime | awk '{print $3,$4}' | sed 's/,//')
    local load=$(uptime | awk -F'load average:' '{print $2}')
    local date_time=$(date "+%Y-%m-%d %H:%M:%S")
    
    echo -e "${BLUE}📊 Quick Stats${NC}"
    echo ""
    echo "System: $date_time"
    echo "Uptime: $uptime"
    echo "Load: $load"
    echo ""
}

# Main function
status_main() {
    local action="${1:-full}"
    
    case "$action" in
        "full"|"all")
            show_quick_stats
            check_ucode_status
            echo ""
            check_system_health
            echo ""
            show_module_status
            ;;
        "health")
            check_system_health
            ;;
        "modules")
            show_module_status
            ;;
        "quick")
            show_quick_stats
            check_ucode_status
            ;;
        *)
            echo "Status module - Available actions: full, health, modules, quick"
            ;;
    esac
}

# Export main function
if [[ "${BASH_SOURCE[0]}" == "${0}" ]]; then
    status_main "$@"
fi
