#!/bin/bash
# uDOS System Variable Integration Manager v1.0.4.1
# Enhanced $VARIABLE system with role-based install settings and startup configuration

set -euo pipefail

# Configuration
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
UDOS_ROOT="$(cd "$SCRIPT_DIR/../.." && pwd)"

# Core components
VARIABLE_MANAGER="$UDOS_ROOT/uCORE/code/variable-manager.sh"
STARTUP_MANAGER="$UDOS_ROOT/uCORE/code/startup-story-manager.sh"
INSTALL_VARIABLES_DIR="$UDOS_ROOT/uMEMORY/system/install-configs"
ROLE_CONFIGS_DIR="$UDOS_ROOT/uMEMORY/system/role-configs"

# Create required directories
mkdir -p "$INSTALL_VARIABLES_DIR" "$ROLE_CONFIGS_DIR"

# Source logging functions
source "$SCRIPT_DIR/logging.sh" 2>/dev/null || {
    log_info() { echo -e "\033[0;36m[INFO]\033[0m $1"; }
    log_success() { echo -e "\033[0;32m[SUCCESS]\033[0m $1"; }
    log_warning() { echo -e "\033[0;33m[WARNING]\033[0m $1"; }
    log_error() { echo -e "\033[0;31m[ERROR]\033[0m $1"; }
}

# Initialize enhanced variable system with role-based configurations
init_enhanced_variable_system() {
    log_info "Initializing enhanced \$VARIABLE system with role-based configurations..."

    # Create install configuration variables
    create_install_variables

    # Create role-specific variable configurations
    create_role_variable_configs

    # Create startup integration system
    create_startup_integration

    # Create adventure tracking variables
    create_adventure_variables

    log_success "Enhanced variable system initialized!"
}

# Create install configuration variables
create_install_variables() {
    log_info "Creating install configuration variables..."

    cat > "$INSTALL_VARIABLES_DIR/install-system-variables.json" << 'EOF'
{
    "metadata": {
        "name": "uDOS Install System Variables",
        "version": "1.0.4.1",
        "type": "install",
        "created": "2025-08-28T00:00:00Z"
    },
    "variables": {
        "INSTALL-MODE": {
            "type": "string",
            "default": "interactive",
            "values": ["interactive", "guided", "automated", "custom"],
            "description": "Installation interaction mode",
            "scope": "install",
            "required": true,
            "story_prompt": "How do you prefer to install uDOS?",
            "story_help": "Interactive: Questions for each setting, Guided: Recommended defaults, Automated: Use all defaults"
        },
        "FIRST-RUN-ROLE": {
            "type": "string",
            "default": "GHOST",
            "values": ["GHOST", "TOMB", "CRYPT", "DRONE", "KNIGHT", "IMP", "SORCERER", "WIZARD"],
            "description": "Initial role assignment for first run",
            "scope": "install",
            "required": true,
            "story_prompt": "What role should be assigned for the first user?",
            "story_help": "This determines initial capabilities and access levels"
        },
        "ADVENTURE-MODE": {
            "type": "string",
            "default": "enabled",
            "values": ["enabled", "disabled", "optional"],
            "description": "Adventure tracking system activation",
            "scope": "install",
            "required": true,
            "story_prompt": "Enable adventure tracking and gamification?",
            "story_help": "Adventure mode adds quest tracking and achievement systems"
        },
        "STARTUP-STORY-AUTO": {
            "type": "string",
            "default": "first-run-only",
            "values": ["always", "first-run-only", "role-change", "manual", "disabled"],
            "description": "When to automatically run startup stories",
            "scope": "install",
            "required": true,
            "story_prompt": "When should startup stories automatically run?",
            "story_help": "Controls automatic execution of role-specific startup configurations"
        },
        "VARIABLE-PERSISTENCE": {
            "type": "string",
            "default": "session-and-permanent",
            "values": ["session-only", "permanent-only", "session-and-permanent", "role-based"],
            "description": "Variable storage persistence strategy",
            "scope": "install",
            "required": true,
            "story_prompt": "How should variables be stored?",
            "story_help": "Session-only: Reset each session, Permanent: Save across sessions, Role-based: Depends on role"
        },
        "DEV-MODE-DEFAULT": {
            "type": "string",
            "default": "role-based",
            "values": ["always-off", "role-based", "user-choice", "always-on"],
            "description": "Default development mode setting",
            "scope": "install",
            "required": true,
            "story_prompt": "How should development mode be configured by default?",
            "story_help": "Role-based: Available for IMP+ roles, User-choice: Ask each user"
        },
        "TUTORIAL-SYSTEM": {
            "type": "string",
            "default": "adaptive",
            "values": ["disabled", "basic", "standard", "adaptive", "comprehensive"],
            "description": "Tutorial and help system level",
            "scope": "install",
            "required": true,
            "story_prompt": "What level of tutorial system do you want?",
            "story_help": "Adaptive: Adjusts based on user role and experience level"
        },
        "THEME-SYSTEM": {
            "type": "string",
            "default": "role-themed",
            "values": ["single-theme", "user-choice", "role-themed", "adaptive"],
            "description": "Theme and visual configuration approach",
            "scope": "install",
            "required": true,
            "story_prompt": "How should visual themes be managed?",
            "story_help": "Role-themed: Different visual styles for each role level"
        }
    }
}
EOF

    log_success "Install configuration variables created"
}

# Create role-specific variable configurations
create_role_variable_configs() {
    log_info "Creating role-specific variable configurations..."

    # GHOST role variables
    cat > "$ROLE_CONFIGS_DIR/ghost-variables.json" << 'EOF'
{
    "metadata": {
        "role": "GHOST",
        "level": 10,
        "description": "Variables specific to Ghost role operations"
    },
    "variables": {
        "DEMO-TIME-LIMIT": {
            "type": "string",
            "default": "30 minutes",
            "values": ["15 minutes", "30 minutes", "1 hour", "unlimited"],
            "description": "Maximum demo session duration",
            "scope": "role"
        },
        "TUTORIAL-PACE": {
            "type": "string",
            "default": "guided",
            "values": ["slow", "guided", "normal", "fast"],
            "description": "Tutorial progression speed",
            "scope": "role"
        },
        "SAFETY-LEVEL": {
            "type": "string",
            "default": "maximum",
            "values": ["standard", "high", "maximum"],
            "description": "System safety and sandboxing level",
            "scope": "role"
        }
    }
}
EOF

    # WIZARD role variables
    cat > "$ROLE_CONFIGS_DIR/wizard-variables.json" << 'EOF'
{
    "metadata": {
        "role": "WIZARD",
        "level": 100,
        "description": "Variables specific to Wizard role operations"
    },
    "variables": {
        "SYSTEM-ACCESS-LEVEL": {
            "type": "string",
            "default": "unrestricted",
            "values": ["restricted", "enhanced", "unrestricted", "omnipotent"],
            "description": "Level of system access granted",
            "scope": "role"
        },
        "AUTO-DEV-MODE": {
            "type": "string",
            "default": "project-based",
            "values": ["never", "on-request", "project-based", "always"],
            "description": "Automatic development mode activation",
            "scope": "role"
        },
        "USER-SPAWN-LIMIT": {
            "type": "string",
            "default": "unlimited",
            "values": ["5", "10", "25", "50", "unlimited"],
            "description": "Maximum users that can be spawned",
            "scope": "role"
        },
        "REALM-AUTHORITY": {
            "type": "string",
            "default": "full",
            "values": ["monitoring", "advisory", "administrative", "full"],
            "description": "Authority level over the entire uDOS realm",
            "scope": "role"
        }
    }
}
EOF

    # Create configs for all other roles
    create_remaining_role_configs

    log_success "Role-specific variable configurations created"
}

# Create remaining role variable configs
create_remaining_role_configs() {
    # TOMB role
    cat > "$ROLE_CONFIGS_DIR/tomb-variables.json" << 'EOF'
{
    "metadata": {
        "role": "TOMB",
        "level": 20,
        "description": "Variables for Tomb Keeper archival operations"
    },
    "variables": {
        "ARCHIVE-AUTO-ORGANIZATION": {
            "type": "string",
            "default": "chronological",
            "values": ["none", "chronological", "categorical", "smart"],
            "description": "Automatic file organization method",
            "scope": "role"
        },
        "BACKUP-COMPRESSION": {
            "type": "string",
            "default": "standard",
            "values": ["none", "light", "standard", "maximum"],
            "description": "Archive compression level",
            "scope": "role"
        },
        "RETENTION-POLICY": {
            "type": "string",
            "default": "permanent",
            "values": ["1-year", "2-years", "5-years", "permanent"],
            "description": "Data retention policy for archives",
            "scope": "role"
        }
    }
}
EOF

    # CRYPT role
    cat > "$ROLE_CONFIGS_DIR/crypt-variables.json" << 'EOF'
{
    "metadata": {
        "role": "CRYPT",
        "level": 30,
        "description": "Variables for Crypt Guardian security operations"
    },
    "variables": {
        "ENCRYPTION-LEVEL": {
            "type": "string",
            "default": "strong",
            "values": ["basic", "standard", "strong", "military"],
            "description": "Encryption strength for protected data",
            "scope": "role"
        },
        "ACCESS-LOG-DETAIL": {
            "type": "string",
            "default": "detailed",
            "values": ["minimal", "standard", "detailed", "forensic"],
            "description": "Level of access logging detail",
            "scope": "role"
        },
        "THREAT-RESPONSE": {
            "type": "string",
            "default": "proactive",
            "values": ["passive", "reactive", "proactive", "aggressive"],
            "description": "Security threat response mode",
            "scope": "role"
        }
    }
}
EOF

    # DRONE role
    cat > "$ROLE_CONFIGS_DIR/drone-variables.json" << 'EOF'
{
    "metadata": {
        "role": "DRONE",
        "level": 40,
        "description": "Variables for Automation Drone operations"
    },
    "variables": {
        "AUTOMATION-AGGRESSIVENESS": {
            "type": "string",
            "default": "moderate",
            "values": ["conservative", "moderate", "aggressive", "maximum"],
            "description": "How aggressively to automate processes",
            "scope": "role"
        },
        "ERROR-HANDLING": {
            "type": "string",
            "default": "retry-then-notify",
            "values": ["fail-fast", "retry-once", "retry-then-notify", "retry-indefinitely"],
            "description": "How to handle automation errors",
            "scope": "role"
        },
        "RESOURCE-LIMITS": {
            "type": "string",
            "default": "standard",
            "values": ["conservative", "standard", "generous", "unlimited"],
            "description": "Resource usage limits for automation",
            "scope": "role"
        }
    }
}
EOF

    # KNIGHT role
    cat > "$ROLE_CONFIGS_DIR/knight-variables.json" << 'EOF'
{
    "metadata": {
        "role": "KNIGHT",
        "level": 50,
        "description": "Variables for Digital Knight service operations"
    },
    "variables": {
        "SERVICE-DEDICATION": {
            "type": "string",
            "default": "balanced",
            "values": ["minimal", "standard", "balanced", "dedicated", "zealous"],
            "description": "Level of dedication to user service",
            "scope": "role"
        },
        "PROTECTION-SCOPE": {
            "type": "string",
            "default": "system-wide",
            "values": ["personal", "team", "system-wide", "realm-wide"],
            "description": "Scope of protection responsibilities",
            "scope": "role"
        },
        "HONOR-STRICTNESS": {
            "type": "string",
            "default": "high",
            "values": ["flexible", "moderate", "high", "absolute"],
            "description": "Adherence level to code of honor",
            "scope": "role"
        }
    }
}
EOF

    # IMP role
    cat > "$ROLE_CONFIGS_DIR/imp-variables.json" << 'EOF'
{
    "metadata": {
        "role": "IMP",
        "level": 60,
        "description": "Variables for Clever Imp creative operations"
    },
    "variables": {
        "CREATIVITY-CHAOS-LEVEL": {
            "type": "string",
            "default": "controlled",
            "values": ["ordered", "controlled", "chaotic", "pure-chaos"],
            "description": "Level of creative chaos allowed",
            "scope": "role"
        },
        "EXPERIMENT-SAFETY": {
            "type": "string",
            "default": "safe-sandbox",
            "values": ["production-safe", "safe-sandbox", "risky-sandbox", "danger-zone"],
            "description": "Safety level for creative experiments",
            "scope": "role"
        },
        "SHARING-DEFAULT": {
            "type": "string",
            "default": "selective",
            "values": ["private", "selective", "open", "public"],
            "description": "Default sharing level for creations",
            "scope": "role"
        }
    }
}
EOF

    # SORCERER role
    cat > "$ROLE_CONFIGS_DIR/sorcerer-variables.json" << 'EOF'
{
    "metadata": {
        "role": "SORCERER",
        "level": 80,
        "description": "Variables for Sorcerer magical operations"
    },
    "variables": {
        "MAGICAL-POWER-LIMIT": {
            "type": "string",
            "default": "high",
            "values": ["conservative", "moderate", "high", "maximum"],
            "description": "Maximum magical power utilization",
            "scope": "role"
        },
        "SPELL-COMPLEXITY": {
            "type": "string",
            "default": "advanced",
            "values": ["basic", "intermediate", "advanced", "master"],
            "description": "Complexity level of available spells",
            "scope": "role"
        },
        "APPRENTICE-LIMIT": {
            "type": "string",
            "default": "5",
            "values": ["1", "3", "5", "10", "unlimited"],
            "description": "Maximum apprentices to mentor",
            "scope": "role"
        }
    }
}
EOF
}

# Create startup integration system
create_startup_integration() {
    log_info "Creating startup integration system..."

    cat > "$UDOS_ROOT/uCORE/code/startup-variable-integration.sh" << 'EOF'
#!/bin/bash
# Startup Variable Integration - Connects variables with startup stories
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
UDOS_ROOT="$(cd "$SCRIPT_DIR/../.." && pwd)"

# Load variable values and apply them to startup stories
integrate_startup_variables() {
    local role="$1"
    local session_id="${2:-startup-$(date +%s)}"

    # Get role-specific variables
    local role_lower=$(echo "$role" | tr '[:upper:]' '[:lower:]')
    local role_config="$UDOS_ROOT/uMEMORY/system/role-configs/${role_lower}-variables.json"

    if [[ -f "$role_config" ]]; then
        echo "🔧 Applying $role role-specific variable configurations..."

        # Apply each variable from role config as a system default
        jq -r '.variables | to_entries[] | "\(.key)=\(.value.default)"' "$role_config" | while IFS='=' read -r var_name var_value; do
            if [[ -n "$var_name" && -n "$var_value" ]]; then
                "$UDOS_ROOT/uCORE/code/variable-manager.sh" SET "$var_name" "$var_value" "$session_id"
            fi
        done

        echo "✅ Role-specific variables applied for $role"
    fi

    # Apply install-time variables
    local install_config="$UDOS_ROOT/uMEMORY/system/install-configs/install-system-variables.json"
    if [[ -f "$install_config" ]]; then
        echo "🔧 Applying install-time variable configurations..."

        jq -r '.variables | to_entries[] | "\(.key)=\(.value.default)"' "$install_config" | while IFS='=' read -r var_name var_value; do
            if [[ -n "$var_name" && -n "$var_value" ]]; then
                "$UDOS_ROOT/uCORE/code/variable-manager.sh" SET "$var_name" "$var_value" "$session_id"
            fi
        done

        echo "✅ Install-time variables applied"
    fi
}

# Check if startup story should run automatically
should_run_startup_story() {
    local role="$1"

    # Get STARTUP-STORY-AUTO setting
    local auto_setting=$("$UDOS_ROOT/uCORE/code/variable-manager.sh" GET "STARTUP-STORY-AUTO" 2>/dev/null || echo "first-run-only")

    case "$auto_setting" in
        "always")
            return 0
            ;;
        "first-run-only")
            # Check if this is first run for this role
            local role_marker="$UDOS_ROOT/sandbox/.${role,,}-startup-complete"
            [[ ! -f "$role_marker" ]]
            ;;
        "role-change")
            # Check if role has changed since last startup
            local last_startup_role=$(cat "$UDOS_ROOT/sandbox/.last-startup-role" 2>/dev/null || echo "")
            [[ "$role" != "$last_startup_role" ]]
            ;;
        "manual"|"disabled")
            return 1
            ;;
        *)
            return 1
            ;;
    esac
}

# Mark startup story as complete for role
mark_startup_complete() {
    local role="$1"
    local role_marker="$UDOS_ROOT/sandbox/.${role,,}-startup-complete"

    echo "$(date '+%Y-%m-%d %H:%M:%S')" > "$role_marker"
    echo "$role" > "$UDOS_ROOT/sandbox/.last-startup-role"
}

# Main integration function
main() {
    local command="${1:-integrate}"
    local role="${2:-$(cat "$UDOS_ROOT/sandbox/current-role.conf" | grep "^ROLE=" | cut -d'=' -f2 | tr -d '"' || echo "GHOST")}"

    case "$command" in
        "integrate")
            integrate_startup_variables "$role"
            ;;
        "should-run")
            should_run_startup_story "$role"
            ;;
        "mark-complete")
            mark_startup_complete "$role"
            ;;
        *)
            echo "Usage: $0 {integrate|should-run|mark-complete} [ROLE]"
            exit 1
            ;;
    esac
}

main "$@"
EOF

    chmod +x "$UDOS_ROOT/uCORE/code/startup-variable-integration.sh"
    log_success "Startup integration system created"
}

# Create adventure tracking variables
create_adventure_variables() {
    log_info "Creating adventure tracking variables..."

    cat > "$UDOS_ROOT/uMEMORY/system/variables/adventure-variables.json" << 'EOF'
{
    "metadata": {
        "name": "Adventure Tracking Variables",
        "version": "1.0.4.1",
        "type": "adventure",
        "created": "2025-08-28T00:00:00Z"
    },
    "variables": {
        "ADVENTURE-MODE": {
            "type": "string",
            "default": "enabled",
            "values": ["enabled", "disabled", "stealth"],
            "description": "Adventure tracking system status",
            "scope": "adventure",
            "required": false
        },
        "CURRENT-QUEST": {
            "type": "string",
            "default": "",
            "description": "Currently active quest identifier",
            "scope": "adventure",
            "required": false
        },
        "QUEST-PROGRESS": {
            "type": "string",
            "default": "0",
            "pattern": "^[0-9]+$",
            "description": "Current quest progress percentage",
            "scope": "adventure",
            "required": false
        },
        "TOTAL-ACHIEVEMENTS": {
            "type": "string",
            "default": "0",
            "pattern": "^[0-9]+$",
            "description": "Total achievements unlocked",
            "scope": "adventure",
            "required": false
        },
        "ROLE-MASTERY-LEVEL": {
            "type": "string",
            "default": "novice",
            "values": ["novice", "apprentice", "journeyman", "expert", "master"],
            "description": "Mastery level in current role",
            "scope": "adventure",
            "required": false
        },
        "PREFERRED-QUEST-TYPE": {
            "type": "string",
            "default": "balanced",
            "values": ["learning", "building", "protecting", "exploring", "balanced"],
            "description": "Preferred type of quests and challenges",
            "scope": "adventure",
            "required": false
        },
        "ADVENTURE-THEME": {
            "type": "string",
            "default": "classic-fantasy",
            "values": ["classic-fantasy", "sci-fi", "cyberpunk", "steampunk", "minimalist"],
            "description": "Adventure narrative theme preference",
            "scope": "adventure",
            "required": false
        }
    }
}
EOF

    log_success "Adventure tracking variables created"
}

# Enhanced installation integration
create_enhanced_install_integration() {
    log_info "Creating enhanced installation integration..."

    cat > "$UDOS_ROOT/uCORE/code/enhanced-install-integration.sh" << 'EOF'
#!/bin/bash
# Enhanced Installation Integration with Variable System
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
UDOS_ROOT="$(cd "$SCRIPT_DIR/../.." && pwd)"

# Run complete installation with variable integration
run_complete_installation() {
    echo "🚀 uDOS Enhanced Installation with Variable Integration"
    echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"

    # 1. Initialize the enhanced variable system
    "$UDOS_ROOT/uCORE/code/system-variable-integration.sh" init

    # 2. Run installation configuration story
    "$UDOS_ROOT/uCORE/code/variable-manager.sh" STORY EXECUTE \
        "$UDOS_ROOT/uMEMORY/system/stories/installation-setup.json" "install-$(date +%s)"

    # 3. Initialize startup story system
    "$UDOS_ROOT/uCORE/code/startup-story-manager.sh" create-stories

    # 4. Run user onboarding story
    "$UDOS_ROOT/uCORE/code/variable-manager.sh" STORY EXECUTE \
        "$UDOS_ROOT/uMEMORY/system/stories/user-onboarding.json" "onboard-$(date +%s)"

    # 5. Get selected role and run role-specific startup
    local user_role=$("$UDOS_ROOT/uCORE/code/variable-manager.sh" GET "USER-ROLE" || echo "GHOST")
    "$UDOS_ROOT/uCORE/code/startup-story-manager.sh" startup "$user_role"

    # 6. Apply role-specific variable configurations
    "$UDOS_ROOT/uCORE/code/startup-variable-integration.sh" integrate "$user_role"
    "$UDOS_ROOT/uCORE/code/startup-variable-integration.sh" mark-complete "$user_role"

    # 7. Initialize adventure system if enabled
    local adventure_mode=$("$UDOS_ROOT/uCORE/code/variable-manager.sh" GET "ADVENTURE-MODE" || echo "enabled")
    if [[ "$adventure_mode" == "enabled" ]]; then
        echo "🎲 Initializing adventure system..."
        echo "Welcome to your uDOS adventure!" > "$UDOS_ROOT/sandbox/logs/adventure.log"
        echo "[$(date '+%Y-%m-%d %H:%M:%S')] 🎯 INSTALLATION_COMPLETE: uDOS installation completed with role $user_role" >> "$UDOS_ROOT/sandbox/logs/adventure.log"
    fi

    echo ""
    echo "✅ Enhanced installation complete!"
    echo "🎭 Role: $user_role"
    echo "🎲 Adventure Mode: $adventure_mode"
    echo ""
    echo "Next steps:"
    echo "  • Run: ./uCORE/code/startup-story-manager.sh adventure"
    echo "  • Or: ./uCORE/code/ucode.sh"
}

# Quick role-based installation
quick_install_for_role() {
    local target_role="$1"

    echo "🚀 Quick Installation for $target_role Role"
    echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"

    # Set up minimal variable system
    "$UDOS_ROOT/uCORE/code/system-variable-integration.sh" init

    # Set role without story
    "$UDOS_ROOT/uCORE/code/variable-manager.sh" SET "USER-ROLE" "$target_role"
    echo "ROLE=\"$target_role\"" > "$UDOS_ROOT/sandbox/current-role.conf"
    echo "TIMESTAMP=\"$(date '+%Y-%m-%d %H:%M:%S %Z')\"" >> "$UDOS_ROOT/sandbox/current-role.conf"

    # Apply role-specific variables
    "$UDOS_ROOT/uCORE/code/startup-variable-integration.sh" integrate "$target_role"

    # Enable adventure mode by default
    "$UDOS_ROOT/uCORE/code/variable-manager.sh" SET "ADVENTURE-MODE" "enabled"

    echo "✅ Quick installation complete for $target_role role!"
}

main() {
    case "${1:-full}" in
        "full")
            run_complete_installation
            ;;
        "quick")
            quick_install_for_role "${2:-GHOST}"
            ;;
        *)
            echo "Usage: $0 {full|quick} [ROLE]"
            exit 1
            ;;
    esac
}

main "$@"
EOF

    chmod +x "$UDOS_ROOT/uCORE/code/enhanced-install-integration.sh"
    log_success "Enhanced installation integration created"
}

# Create startup command integration
create_startup_command_integration() {
    log_info "Creating startup command integration for uCODE system..."

    # Update the main ucode.sh to include variable and startup integration
    cat > "$UDOS_ROOT/uCORE/code/enhanced-startup.sh" << 'EOF'
#!/bin/bash
# Enhanced uDOS Startup with Variable and Adventure Integration
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
UDOS_ROOT="$(cd "$SCRIPT_DIR/../.." && pwd)"

# Enhanced startup sequence
enhanced_startup() {
    local current_role=$(cat "$UDOS_ROOT/sandbox/current-role.conf" 2>/dev/null | grep "^ROLE=" | cut -d'=' -f2 | tr -d '"' || echo "GHOST")

    echo "🌟 uDOS Enhanced Startup"
    echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
    echo "🎭 Role: $current_role"

    # Check if startup story should run
    if "$UDOS_ROOT/uCORE/code/startup-variable-integration.sh" should-run "$current_role"; then
        echo "🎯 Running $current_role startup story..."
        "$UDOS_ROOT/uCORE/code/startup-story-manager.sh" startup "$current_role"
        "$UDOS_ROOT/uCORE/code/startup-variable-integration.sh" mark-complete "$current_role"
    fi

    # Apply current variable integration
    "$UDOS_ROOT/uCORE/code/startup-variable-integration.sh" integrate "$current_role"

    # Check adventure mode
    local adventure_mode=$("$UDOS_ROOT/uCORE/code/variable-manager.sh" GET "ADVENTURE-MODE" 2>/dev/null || echo "enabled")
    if [[ "$adventure_mode" == "enabled" ]]; then
        echo "🎲 Adventure mode active!"
        echo "[$(date '+%Y-%m-%d %H:%M:%S')] 🚀 STARTUP: $current_role role session started" >> "$UDOS_ROOT/sandbox/logs/adventure.log"
    fi

    echo ""
    echo "Available commands:"
    echo "  🎲 adventure    - Enter interactive adventure mode"
    echo "  📊 status       - Show system and adventure status"
    echo "  🔧 variables    - Manage system variables"
    echo "  🎭 role         - Change current role"
    echo "  ❓ help         - Show help information"
    echo ""

    # Start interactive session
    start_interactive_session "$current_role"
}

# Interactive session with enhanced commands
start_interactive_session() {
    local role="$1"

    while true; do
        read -p "🎯 uDOS ($role)> " command args

        case "$command" in
            "adventure")
                "$UDOS_ROOT/uCORE/code/startup-story-manager.sh" adventure
                ;;
            "status")
                show_enhanced_status "$role"
                ;;
            "variables")
                "$UDOS_ROOT/uCORE/code/variable-manager.sh" LIST all
                ;;
            "role")
                change_role_interactive
                role=$(cat "$UDOS_ROOT/sandbox/current-role.conf" | grep "^ROLE=" | cut -d'=' -f2 | tr -d '"')
                ;;
            "startup")
                "$UDOS_ROOT/uCORE/code/startup-story-manager.sh" startup "$role"
                ;;
            "help")
                show_enhanced_help
                ;;
            "exit"|"quit")
                echo "👋 Farewell, $role!"
                break
                ;;
            "")
                # Empty command, continue
                ;;
            *)
                echo "❓ Unknown command: $command"
                echo "💡 Type 'help' for available commands"
                ;;
        esac
    done
}

# Show enhanced status
show_enhanced_status() {
    local role="$1"

    echo "📊 uDOS Enhanced Status"
    echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
    echo "🎭 Current Role: $role"

    # Show adventure stats if enabled
    local adventure_mode=$("$UDOS_ROOT/uCORE/code/variable-manager.sh" GET "ADVENTURE-MODE" 2>/dev/null || echo "disabled")
    if [[ "$adventure_mode" == "enabled" ]]; then
        local quest_count=$(grep -c "QUEST_START" "$UDOS_ROOT/sandbox/logs/adventure.log" 2>/dev/null || echo 0)
        local achievement_count=$(grep -c "ACHIEVEMENT" "$UDOS_ROOT/sandbox/logs/adventure.log" 2>/dev/null || echo 0)

        echo "🎲 Adventure Mode: Active"
        echo "🗡️ Quests Started: $quest_count"
        echo "🏆 Achievements: $achievement_count"
    else
        echo "🎲 Adventure Mode: Disabled"
    fi

    # Show key variables
    echo ""
    echo "🔧 Key Variables:"
    echo "   DISPLAY-MODE: $("$UDOS_ROOT/uCORE/code/variable-manager.sh" GET "DISPLAY-MODE" 2>/dev/null || echo "CLI")"
    echo "   DETAIL-LEVEL: $("$UDOS_ROOT/uCORE/code/variable-manager.sh" GET "DETAIL-LEVEL" 2>/dev/null || echo "STANDARD")"
    echo "   PROJECT-TYPE: $("$UDOS_ROOT/uCORE/code/variable-manager.sh" GET "PROJECT-TYPE" 2>/dev/null || echo "none")"
}

# Enhanced help
show_enhanced_help() {
    echo "🎯 uDOS Enhanced Commands"
    echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
    echo ""
    echo "🎲 Adventure & Role Commands:"
    echo "   adventure     - Enter interactive adventure mode"
    echo "   role          - Change current role with startup story"
    echo "   startup       - Run startup story for current role"
    echo ""
    echo "🔧 System Commands:"
    echo "   status        - Show enhanced system status"
    echo "   variables     - View and manage system variables"
    echo "   help          - Show this help"
    echo ""
    echo "🚪 Session Commands:"
    echo "   exit, quit    - End current session"
    echo ""
}

# Interactive role change
change_role_interactive() {
    echo "🎭 Role Change System"
    echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
    echo "Available roles:"
    echo "   10 👻 GHOST    - Ethereal explorer (demo access)"
    echo "   20 🗿 TOMB     - Archive keeper (storage focus)"
    echo "   30 🔐 CRYPT    - Security guardian (protection)"
    echo "   40 🤖 DRONE    - Automation specialist (efficiency)"
    echo "   50 ⚔️ KNIGHT   - System protector (service)"
    echo "   60 😈 IMP      - Creative developer (innovation)"
    echo "   80 🧙‍♂️ SORCERER - Advanced administrator (power)"
    echo "  100 🌟 WIZARD   - Supreme master (omnipotence)"
    echo ""

    read -p "🎯 Choose new role: " new_role
    new_role=$(echo "$new_role" | tr '[:lower:]' '[:upper:]')

    case "$new_role" in
        GHOST|TOMB|CRYPT|DRONE|KNIGHT|IMP|SORCERER|WIZARD)
            echo "ROLE=\"$new_role\"" > "$UDOS_ROOT/sandbox/current-role.conf"
            echo "TIMESTAMP=\"$(date '+%Y-%m-%d %H:%M:%S %Z')\"" >> "$UDOS_ROOT/sandbox/current-role.conf"

            echo "✅ Role changed to $new_role!"

            # Offer startup story
            read -p "🌟 Run $new_role startup story? (y/n): " run_startup
            if [[ "$run_startup" =~ ^[Yy] ]]; then
                "$UDOS_ROOT/uCORE/code/startup-story-manager.sh" startup "$new_role"
            fi
            ;;
        *)
            echo "❌ Invalid role choice"
            ;;
    esac
}

# Main execution
main() {
    case "${1:-start}" in
        "start"|"")
            enhanced_startup
            ;;
        "install")
            "$UDOS_ROOT/uCORE/code/enhanced-install-integration.sh" full
            ;;
        "quick-install")
            "$UDOS_ROOT/uCORE/code/enhanced-install-integration.sh" quick "${2:-GHOST}"
            ;;
        *)
            echo "Usage: $0 {start|install|quick-install} [ROLE]"
            exit 1
            ;;
    esac
}

main "$@"
EOF

    chmod +x "$UDOS_ROOT/uCORE/code/enhanced-startup.sh"
    log_success "Enhanced startup command integration created"
}

# Main execution function
main() {
    local command="${1:-init}"

    case "$command" in
        "init")
            init_enhanced_variable_system
            create_enhanced_install_integration
            create_startup_command_integration
            ;;
        "install")
            create_enhanced_install_integration
            ;;
        "startup")
            create_startup_command_integration
            ;;
        "help"|*)
            echo "🔧 uDOS System Variable Integration Manager"
            echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
            echo ""
            echo "Commands:"
            echo "  init       Initialize complete enhanced variable system"
            echo "  install    Create enhanced installation integration"
            echo "  startup    Create startup command integration"
            echo "  help       Show this help"
            echo ""
            echo "This creates:"
            echo "  • Role-specific variable configurations"
            echo "  • Install-time variable settings"
            echo "  • Adventure tracking variables"
            echo "  • Enhanced startup integration"
            echo "  • Interactive adventure system"
            ;;
    esac
}

# Execute main with all arguments
main "$@"
