#!/bin/bash
# Integration script for Enhanced Debugging, Error Logging & Self-Healing System
# Integrates the new debugging capabilities with existing uDOS components

set -euo pipefail

UDOS_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
export UDOS_ROOT

# Colors
readonly GREEN='\033[0;32m'
readonly BLUE='\033[0;34m'
readonly YELLOW='\033[1;33m'
readonly WHITE='\033[1;37m'
readonly NC='\033[0m'

echo -e "${WHITE}🔧 Integrating Enhanced Debugging System${NC}"
echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"

# 1. Add enhanced debugging to core scripts
integrate_with_core() {
    echo -e "${YELLOW}🔗 Integrating with core uDOS scripts...${NC}"
    
    local core_scripts=(
        "$UDOS_ROOT/uCORE/code/ucode.sh"
        "$UDOS_ROOT/uCORE/launcher/universal/start-udos.sh"
        "$UDOS_ROOT/uSCRIPT/uscript.sh"
    )
    
    for script in "${core_scripts[@]}"; do
        if [[ -f "$script" ]] && ! grep -q "enhanced-debug.sh" "$script"; then
            echo "Integrating with $(basename "$script")..."
            
            # Add sourcing of enhanced debug at the top (after shebang and basic setup)
            local temp_file=$(mktemp)
            {
                head -5 "$script"
                echo ""
                echo "# Enhanced debugging integration"
                echo "if [[ -f \"\$UDOS_ROOT/dev/scripts/enhanced-debug.sh\" ]]; then"
                echo "    source \"\$UDOS_ROOT/dev/scripts/enhanced-debug.sh\""
                echo "fi"
                echo ""
                tail -n +6 "$script"
            } > "$temp_file"
            
            cp "$temp_file" "$script"
            rm "$temp_file"
            
            echo -e "${GREEN}  ✅ $(basename "$script") enhanced${NC}"
        else
            echo -e "${BLUE}  ℹ️ $(basename "$script") already integrated or missing${NC}"
        fi
    done
}

# 2. Add debugging tasks to VS Code
add_vscode_tasks() {
    echo -e "${YELLOW}🔗 Adding debugging tasks to VS Code...${NC}"
    
    local tasks_file="$UDOS_ROOT/.vscode/tasks.json"
    if [[ -f "$tasks_file" ]]; then
        # Check if debug tasks already exist
        if ! grep -q "Test Debug System" "$tasks_file"; then
            # Create backup
            cp "$tasks_file" "${tasks_file}.backup"
            
            # Add debug tasks before the closing bracket
            local temp_file=$(mktemp)
            sed '$d' "$tasks_file" > "$temp_file"  # Remove last line (closing bracket)
            
            cat >> "$temp_file" << 'EOF'
        ,
        {
            "label": "🧪 Test Debug System",
            "type": "shell",
            "command": "./dev/scripts/test-debug-system.sh",
            "group": "test",
            "presentation": {
                "echo": true,
                "reveal": "always",
                "focus": true,
                "panel": "new"
            },
            "problemMatcher": []
        },
        {
            "label": "🔍 Show Debug Logs",
            "type": "shell",
            "command": "bash",
            "args": ["-c", "source ./dev/scripts/enhanced-debug.sh && show_logs"],
            "group": "test",
            "presentation": {
                "echo": true,
                "reveal": "always",
                "focus": true,
                "panel": "shared"
            },
            "problemMatcher": []
        },
        {
            "label": "🩺 System Health Check",
            "type": "shell",
            "command": "bash",
            "args": ["-c", "source ./dev/scripts/enhanced-debug.sh && check_system"],
            "group": "test",
            "presentation": {
                "echo": true,
                "reveal": "always",
                "focus": true,
                "panel": "shared"
            },
            "problemMatcher": []
        },
        {
            "label": "🔄 Reset Debug Counters",
            "type": "shell",
            "command": "bash",
            "args": ["-c", "source ./dev/scripts/enhanced-debug.sh && retry_healing"],
            "group": "test",
            "presentation": {
                "echo": true,
                "reveal": "always",
                "focus": true,
                "panel": "shared"
            },
            "problemMatcher": []
        }
    ]
}
EOF
            
            mv "$temp_file" "$tasks_file"
            echo -e "${GREEN}  ✅ VS Code debug tasks added${NC}"
        else
            echo -e "${BLUE}  ℹ️ VS Code debug tasks already exist${NC}"
        fi
    else
        echo -e "${YELLOW}  ⚠️ VS Code tasks.json not found${NC}"
    fi
}

# 3. Create user-friendly debug commands
create_debug_commands() {
    echo -e "${YELLOW}🔗 Creating user-friendly debug commands...${NC}"
    
    # Create a simple debug command for users
    local debug_cmd="$UDOS_ROOT/uCORE/code/commands/debug.sh"
    mkdir -p "$(dirname "$debug_cmd")"
    
    cat > "$debug_cmd" << 'EOF'
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
EOF
    
    chmod +x "$debug_cmd"
    echo -e "${GREEN}  ✅ DEBUG command created${NC}"
    
    # Create adventure log viewer
    local adventure_cmd="$UDOS_ROOT/uCORE/code/commands/adventure.sh"
    cat > "$adventure_cmd" << 'EOF'
#!/bin/bash
# View the NetHack-style adventure log

UDOS_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/../../.." && pwd)"
log_file="$UDOS_ROOT/sandbox/logs/adventure.log"

if [[ -f "$log_file" ]]; then
    echo "🎲 Your Adventure So Far:"
    echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
    cat "$log_file"
else
    echo "🎲 No adventures yet! Start using uDOS to begin your quest."
fi
EOF
    
    chmod +x "$adventure_cmd"
    echo -e "${GREEN}  ✅ ADVENTURE command created${NC}"
}

# 4. Update documentation
update_documentation() {
    echo -e "${YELLOW}📝 Creating debugging documentation...${NC}"
    
    cat > "$UDOS_ROOT/dev/docs/DEBUGGING-GUIDE.md" << 'EOF'
# 🧙‍♂️ uDOS Enhanced Debugging & Self-Healing Guide

## 🎯 Overview

uDOS features an advanced debugging system with NetHack-inspired error messages and automatic self-healing capabilities that adapt to your user role.

## 🎭 Role-Based Debugging

### 👑 Wizard/Developer
- **Full debug info** with stack traces and performance monitoring
- **Enhanced error details** with technical information
- **Interactive debug shells** for investigation
- **NetHack commentary** with witty error messages
- **Self-healing** with retry mechanisms

### 🛡️ Admin/Power User
- **Moderate debug info** with helpful suggestions
- **Self-healing** with progress indicators
- **System health monitoring**
- **Adventure log** access

### 👤 Regular User
- **Friendly error messages** with simple explanations
- **Automatic self-healing** (invisible to user)
- **Helpful hints** based on error type
- **No technical jargon**

## 🎲 NetHack-Style Error Messages

The system provides entertaining error messages inspired by NetHack:

- **Permission errors**: "The door is locked. You need a key."
- **Missing files**: "You search the dungeon but find nothing here."
- **Network issues**: "Your carrier pigeon got lost in a storm."
- **Memory problems**: "Your brain is full. You forget something important."
- **Disk space**: "Your bag of holding is completely full."

## 🔧 Self-Healing Mechanisms

uDOS automatically attempts to fix common issues:

1. **Permission fixes**: Automatically chmod +x scripts
2. **File restoration**: Restore from backups or templates
3. **Network recovery**: Try alternative endpoints
4. **Memory cleanup**: Clear temporary files and caches
5. **Disk cleanup**: Remove old logs and temporary files

## 📊 Available Commands

### Command Line
```bash
DEBUG logs      # Show recent error logs
DEBUG health    # System health check
DEBUG reset     # Reset error counters
DEBUG test      # Run debug system test
ADVENTURE       # View NetHack-style adventure log
```

### VS Code Tasks
- 🧪 Test Debug System
- 🔍 Show Debug Logs  
- 🩺 System Health Check
- 🔄 Reset Debug Counters

## 📁 Log Files

- `sandbox/logs/error.log` - Technical error details
- `sandbox/logs/adventure.log` - NetHack-style commentary
- `sandbox/logs/debug.log` - Detailed debug information (dev only)
- `sandbox/logs/performance.log` - Performance metrics (dev only)

## 🎮 Adventure Log Examples

```
2025-08-27 21:30:09 You enter the debugging dungeon...
2025-08-27 21:30:09 A wild segfault appears!
2025-08-27 21:30:09 You cast self-healing. It's super effective!
2025-08-27 21:30:10 The CPU sprites are working overtime!
2025-08-27 21:30:15 Your bag of holding is getting heavy.
```

## 🚀 Integration

The enhanced debugging system is automatically integrated with:
- Core uDOS scripts (ucode.sh, start-udos.sh, uscript.sh)
- VS Code development environment
- User command interface
- Performance monitoring system

## 🔍 Troubleshooting

If you encounter issues:
1. Run `DEBUG test` to verify system integrity
2. Check `DEBUG health` for system status
3. Use `DEBUG reset` to clear error counters
4. View `ADVENTURE` for a summary of recent events

The system provides increasingly helpful messages with each retry attempt, and developers get access to interactive debug shells for investigation.
EOF
    
    echo -e "${GREEN}  ✅ Documentation created${NC}"
}

# 5. Run integration tests
run_integration_tests() {
    echo -e "${YELLOW}🧪 Running integration tests...${NC}"
    
    # Test that enhanced debugging works
    echo "Testing enhanced debugging integration..."
    if "$UDOS_ROOT/dev/scripts/test-debug-system.sh" >/dev/null 2>&1; then
        echo -e "${GREEN}  ✅ Enhanced debugging test passed${NC}"
    else
        echo -e "${RED}  ❌ Enhanced debugging test failed${NC}"
        return 1
    fi
    
    # Test user commands
    echo "Testing user-friendly commands..."
    if "$UDOS_ROOT/uCORE/code/commands/debug.sh" help >/dev/null 2>&1; then
        echo -e "${GREEN}  ✅ DEBUG command working${NC}"
    else
        echo -e "${RED}  ❌ DEBUG command failed${NC}"
        return 1
    fi
    
    if "$UDOS_ROOT/uCORE/code/commands/adventure.sh" >/dev/null 2>&1; then
        echo -e "${GREEN}  ✅ ADVENTURE command working${NC}"
    else
        echo -e "${RED}  ❌ ADVENTURE command failed${NC}"
        return 1
    fi
}

# Main integration process
main() {
    integrate_with_core
    add_vscode_tasks
    create_debug_commands
    update_documentation
    run_integration_tests
    
    echo -e "${GREEN}🎉 Enhanced Debugging System Integration Complete!${NC}"
    echo ""
    echo -e "${BLUE}📋 What's Available:${NC}"
    echo -e "${WHITE}  🎲 NetHack-inspired error messages${NC}"
    echo -e "${WHITE}  🔧 Automatic self-healing (up to 3 attempts)${NC}"
    echo -e "${WHITE}  🎭 Role-aware debugging (user/admin/wizard)${NC}"
    echo -e "${WHITE}  📊 Performance monitoring & system health${NC}"
    echo -e "${WHITE}  🎮 Adventure log with witty commentary${NC}"
    echo ""
    echo -e "${BLUE}🔧 Try these commands:${NC}"
    echo -e "${WHITE}  DEBUG test    ${BLUE}# Run full test suite${NC}"
    echo -e "${WHITE}  DEBUG health  ${BLUE}# Check system status${NC}"
    echo -e "${WHITE}  ADVENTURE     ${BLUE}# View your quest log${NC}"
}

# Run if executed directly
if [[ "${BASH_SOURCE[0]}" == "${0}" ]]; then
    main "$@"
fi
