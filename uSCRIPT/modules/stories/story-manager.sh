#!/bin/bash
# uDOS Startup Story Manager v1.0.4.1
# Role-based interactive startup stories with $VARIABLE integration and adventure tracking

set -euo pipefail

# Configuration
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
UDOS_ROOT="$(cd "$SCRIPT_DIR/../.." && pwd)"

# Core components
VARIABLE_MANAGER="$UDOS_ROOT/uCORE/code/variable-manager.sh"
ROLE_MANAGER="$UDOS_ROOT/uCORE/code/role-manager.sh"
STORY_DIR="$UDOS_ROOT/uMEMORY/system/stories"
ROLE_STORIES_DIR="$STORY_DIR/roles"
ADVENTURE_LOG="$UDOS_ROOT/sandbox/logs/adventure.log"

# Create required directories
mkdir -p "$ROLE_STORIES_DIR" "$(dirname "$ADVENTURE_LOG")"

# Source logging functions
source "$SCRIPT_DIR/logging.sh" 2>/dev/null || {
    log_info() { echo -e "\033[0;36m[INFO]\033[0m $1"; }
    log_success() { echo -e "\033[0;32m[SUCCESS]\033[0m $1"; }
    log_warning() { echo -e "\033[0;33m[WARNING]\033[0m $1"; }
    log_error() { echo -e "\033[0;31m[ERROR]\033[0m $1"; }
}

# Adventure logging function
adventure_log() {
    local action="$1"
    local detail="$2"
    local timestamp=$(date '+%Y-%m-%d %H:%M:%S')

    echo "[$timestamp] 🎲 $action: $detail" >> "$ADVENTURE_LOG"
}

# Get current role
get_current_role() {
    local role_file="$UDOS_ROOT/sandbox/current-role.conf"
    if [[ -f "$role_file" ]]; then
        grep "^ROLE=" "$role_file" | cut -d'=' -f2 | tr -d '"' || echo "GHOST"
    else
        echo "GHOST"
    fi
}

# Create role-specific startup stories
create_role_startup_stories() {
    log_info "Creating role-specific startup stories..."

    # GHOST role - Demo/Tutorial focus
    create_ghost_story

    # TOMB role - Basic user setup
    create_tomb_story

    # CRYPT role - Secure storage setup
    create_crypt_story

    # DRONE role - Automation configuration
    create_drone_story

    # KNIGHT role - Security and protection
    create_knight_story

    # IMP role - Development and creativity
    create_imp_story

    # SORCERER role - Advanced administration
    create_sorcerer_story

    # WIZARD role - Full system mastery
    create_wizard_story

    log_success "All role startup stories created"
}

# GHOST role startup story
create_ghost_story() {
    cat > "$ROLE_STORIES_DIR/ghost-startup.json" << 'EOF'
{
    "metadata": {
        "name": "ghost-startup",
        "title": "👻 Welcome, Ghost - Begin Your Journey",
        "type": "story",
        "role": "GHOST",
        "level": 10,
        "created": "2025-08-28T00:00:00Z"
    },
    "story": {
        "introduction": "🌟 Welcome to uDOS, mysterious wanderer! As a Ghost, you have access to a safe demonstration environment where you can explore without affecting the main system.",
        "context": "Ghost users experience uDOS through guided demos and tutorials. Your actions are sandboxed for learning.",
        "purpose": "Introduce basic concepts and demonstrate core functionality",
        "adventure_theme": "ethereal_exploration"
    },
    "variables": [
        {
            "name": "TUTORIAL-PREFERENCE",
            "type": "string",
            "description": "Preferred learning style",
            "required": true,
            "values": ["guided", "experimental", "reference"],
            "prompt": "How do you prefer to learn new systems?",
            "help": "Guided: Step-by-step tutorials, Experimental: Try things yourself, Reference: Documentation focus"
        },
        {
            "name": "DEMO-DURATION",
            "type": "string",
            "description": "Expected demo session length",
            "required": true,
            "values": ["15 minutes", "30 minutes", "1 hour", "explore freely"],
            "prompt": "How long do you plan to explore today?",
            "help": "This helps us suggest appropriate activities for your session"
        },
        {
            "name": "INTEREST-AREA",
            "type": "string",
            "description": "Primary area of interest",
            "required": false,
            "values": ["commands", "templates", "visualization", "automation", "general"],
            "prompt": "What aspect of uDOS interests you most?",
            "help": "We'll customize demonstrations based on your interests"
        }
    ],
    "adventure": {
        "starting_quest": "first_steps",
        "milestones": ["demo_complete", "tutorial_finished", "basics_mastered"],
        "rewards": ["demo_certificate", "tutorial_completion", "ghost_badge"]
    }
}
EOF
}

# TOMB role startup story
create_tomb_story() {
    cat > "$ROLE_STORIES_DIR/tomb-startup.json" << 'EOF'
{
    "metadata": {
        "name": "tomb-startup",
        "title": "🗿 Welcome, Tomb Keeper - Establish Your Archive",
        "type": "story",
        "role": "TOMB",
        "level": 20,
        "created": "2025-08-28T00:00:00Z"
    },
    "story": {
        "introduction": "🏛️ Greetings, Keeper of the Tomb! You have the sacred duty of maintaining and organizing information. Let's set up your archival system.",
        "context": "Tomb users focus on data storage, organization, and basic information management with enhanced security.",
        "purpose": "Configure storage preferences and organizational systems",
        "adventure_theme": "archival_mastery"
    },
    "variables": [
        {
            "name": "STORAGE-PRIORITY",
            "type": "string",
            "description": "Primary storage focus",
            "required": true,
            "values": ["documents", "projects", "references", "templates"],
            "prompt": "What type of information will you primarily store?",
            "help": "This affects how we organize your uMEMORY structure"
        },
        {
            "name": "BACKUP-FREQUENCY",
            "type": "string",
            "description": "Desired backup schedule",
            "required": true,
            "values": ["daily", "weekly", "monthly", "manual"],
            "prompt": "How often should we backup your data?",
            "help": "Automated backups protect your archived information"
        },
        {
            "name": "ORGANIZATION-STYLE",
            "type": "string",
            "description": "Preferred organization method",
            "required": true,
            "values": ["chronological", "categorical", "project-based", "custom"],
            "prompt": "How do you prefer to organize information?",
            "help": "We'll set up templates that match your organizational style"
        }
    ],
    "adventure": {
        "starting_quest": "establish_archive",
        "milestones": ["first_storage", "backup_configured", "archive_organized"],
        "rewards": ["tomb_seal", "keeper_badge", "storage_mastery"]
    }
}
EOF
}

# CRYPT role startup story
create_crypt_story() {
    cat > "$ROLE_STORIES_DIR/crypt-startup.json" << 'EOF'
{
    "metadata": {
        "name": "crypt-startup",
        "title": "🔐 Welcome, Crypt Guardian - Secure Your Vault",
        "type": "story",
        "role": "CRYPT",
        "level": 30,
        "created": "2025-08-28T00:00:00Z"
    },
    "story": {
        "introduction": "⚡ Hail, Guardian of the Crypt! Your role is to protect and secure sensitive information. Let's establish your security protocols.",
        "context": "Crypt users have enhanced security features and protected storage areas for sensitive work.",
        "purpose": "Configure security settings and protected storage areas",
        "adventure_theme": "guardian_protection"
    },
    "variables": [
        {
            "name": "SECURITY-PROFILE",
            "type": "string",
            "description": "Security configuration level",
            "required": true,
            "values": ["standard", "enhanced", "maximum", "custom"],
            "prompt": "What level of security do you require?",
            "help": "Higher security means more protection but additional verification steps"
        },
        {
            "name": "SENSITIVE-DATA-TYPES",
            "type": "string",
            "description": "Types of sensitive data to protect",
            "required": true,
            "values": ["personal", "business", "research", "development", "mixed"],
            "prompt": "What type of sensitive data will you store?",
            "help": "This helps us configure appropriate protection measures"
        },
        {
            "name": "ACCESS-VERIFICATION",
            "type": "string",
            "description": "Preferred verification method",
            "required": true,
            "values": ["password", "key-file", "dual-factor", "biometric"],
            "prompt": "How do you want to verify access to protected areas?",
            "help": "More secure methods provide better protection for your crypt"
        }
    ],
    "adventure": {
        "starting_quest": "secure_the_crypt",
        "milestones": ["vault_established", "security_configured", "protection_active"],
        "rewards": ["guardian_key", "crypt_seal", "security_mastery"]
    }
}
EOF
}

# DRONE role startup story
create_drone_story() {
    cat > "$ROLE_STORIES_DIR/drone-startup.json" << 'EOF'
{
    "metadata": {
        "name": "drone-startup",
        "title": "🤖 Welcome, Automation Drone - Configure Your Operations",
        "type": "story",
        "role": "DRONE",
        "level": 40,
        "created": "2025-08-28T00:00:00Z"
    },
    "story": {
        "introduction": "⚙️ Systems online, Automation Drone! You excel at repetitive tasks and systematic operations. Let's configure your automation preferences.",
        "context": "Drone users have access to automation tools, scripting capabilities, and systematic workflow management.",
        "purpose": "Set up automation preferences and workflow configurations",
        "adventure_theme": "systematic_efficiency"
    },
    "variables": [
        {
            "name": "AUTOMATION-FOCUS",
            "type": "string",
            "description": "Primary automation target",
            "required": true,
            "values": ["file-management", "data-processing", "system-monitoring", "workflow-automation"],
            "prompt": "What do you want to automate first?",
            "help": "We'll set up templates and scripts for your chosen automation area"
        },
        {
            "name": "SCHEDULE-PREFERENCE",
            "type": "string",
            "description": "Preferred automation schedule",
            "required": true,
            "values": ["real-time", "hourly", "daily", "on-demand"],
            "prompt": "When should automated tasks run?",
            "help": "This configures the default timing for your automation scripts"
        },
        {
            "name": "NOTIFICATION-LEVEL",
            "type": "string",
            "description": "Automation notification preferences",
            "required": true,
            "values": ["silent", "errors-only", "summary", "detailed"],
            "prompt": "How much feedback do you want from automated processes?",
            "help": "Controls how much information your automation systems provide"
        }
    ],
    "adventure": {
        "starting_quest": "automate_workflows",
        "milestones": ["first_automation", "schedule_active", "efficiency_gained"],
        "rewards": ["efficiency_badge", "automation_mastery", "drone_achievement"]
    }
}
EOF
}

# KNIGHT role startup story
create_knight_story() {
    cat > "$ROLE_STORIES_DIR/knight-startup.json" << 'EOF'
{
    "metadata": {
        "name": "knight-startup",
        "title": "⚔️ Welcome, Digital Knight - Establish Your Code of Honor",
        "type": "story",
        "role": "KNIGHT",
        "level": 50,
        "created": "2025-08-28T00:00:00Z"
    },
    "story": {
        "introduction": "🛡️ Hail and well met, Noble Knight! You stand as a protector of systems and guardian of proper procedures. Let's establish your code of honor.",
        "context": "Knights have responsibility for system protection, user assistance, and maintaining operational standards.",
        "purpose": "Configure protection protocols and service standards",
        "adventure_theme": "noble_service"
    },
    "variables": [
        {
            "name": "SERVICE-FOCUS",
            "type": "string",
            "description": "Primary service area",
            "required": true,
            "values": ["system-protection", "user-support", "quality-assurance", "training-assistance"],
            "prompt": "How do you wish to serve the realm?",
            "help": "This determines your primary responsibilities and available tools"
        },
        {
            "name": "VIGILANCE-LEVEL",
            "type": "string",
            "description": "System monitoring intensity",
            "required": true,
            "values": ["standard", "enhanced", "maximum", "custom"],
            "prompt": "How vigilantly should you monitor system health?",
            "help": "Higher vigilance provides better protection but requires more attention"
        },
        {
            "name": "ASSISTANCE-STYLE",
            "type": "string",
            "description": "Preferred assistance approach",
            "required": true,
            "values": ["proactive", "responsive", "educational", "collaborative"],
            "prompt": "How do you prefer to assist other users?",
            "help": "This configures your interaction style and notification preferences"
        }
    ],
    "adventure": {
        "starting_quest": "take_the_oath",
        "milestones": ["oath_sworn", "first_protection", "service_rendered"],
        "rewards": ["honor_badge", "protector_seal", "knight_achievement"]
    }
}
EOF
}

# IMP role startup story
create_imp_story() {
    cat > "$ROLE_STORIES_DIR/imp-startup.json" << 'EOF'
{
    "metadata": {
        "name": "imp-startup",
        "title": "😈 Welcome, Clever Imp - Unleash Your Creativity",
        "type": "story",
        "role": "IMP",
        "level": 60,
        "created": "2025-08-28T00:00:00Z"
    },
    "story": {
        "introduction": "🔥 Greetings, mischievous Imp! Your creativity and cunning make you perfect for development and innovation. Let's set up your creative workspace.",
        "context": "Imps have development access, script creation abilities, and creative tools for building custom solutions.",
        "purpose": "Configure development environment and creative tools",
        "adventure_theme": "creative_chaos"
    },
    "variables": [
        {
            "name": "CREATIVITY-FOCUS",
            "type": "string",
            "description": "Primary creative outlet",
            "required": true,
            "values": ["scripting", "templates", "automation", "experiments", "tools"],
            "prompt": "Where does your mischievous creativity flow best?",
            "help": "We'll set up development tools optimized for your creative focus"
        },
        {
            "name": "DEVELOPMENT-STYLE",
            "type": "string",
            "description": "Preferred development approach",
            "required": true,
            "values": ["rapid-prototyping", "experimental", "methodical", "collaborative"],
            "prompt": "How do you like to approach development projects?",
            "help": "This configures your development environment and tool preferences"
        },
        {
            "name": "SHARING-PREFERENCE",
            "type": "string",
            "description": "How to share your creations",
            "required": true,
            "values": ["open-sharing", "selective-sharing", "private-first", "collaborative"],
            "prompt": "How do you want to share your creative works?",
            "help": "Controls default permissions and sharing settings for your projects"
        }
    ],
    "adventure": {
        "starting_quest": "spark_creativity",
        "milestones": ["first_creation", "tool_mastery", "innovation_achieved"],
        "rewards": ["creativity_spark", "innovation_badge", "imp_mastery"]
    }
}
EOF
}

# SORCERER role startup story
create_sorcerer_story() {
    cat > "$ROLE_STORIES_DIR/sorcerer-startup.json" << 'EOF'
{
    "metadata": {
        "name": "sorcerer-startup",
        "title": "🧙‍♂️ Welcome, Wise Sorcerer - Channel Your Power",
        "type": "story",
        "role": "SORCERER",
        "level": 80,
        "created": "2025-08-28T00:00:00Z"
    },
    "story": {
        "introduction": "✨ Welcome, Master Sorcerer! Your deep knowledge and magical abilities grant you advanced powers over the system. Let's focus your arcane energies.",
        "context": "Sorcerers have advanced administration capabilities, system configuration access, and powerful automation tools.",
        "purpose": "Configure advanced system management and magical automation",
        "adventure_theme": "arcane_mastery"
    },
    "variables": [
        {
            "name": "MAGICAL-SPECIALTY",
            "type": "string",
            "description": "Your primary magical focus",
            "required": true,
            "values": ["system-enchantment", "data-transmutation", "workflow-conjuring", "knowledge-divination"],
            "prompt": "In which school of magic do you specialize?",
            "help": "This determines your advanced tools and automation capabilities"
        },
        {
            "name": "POWER-LEVEL",
            "type": "string",
            "description": "Preferred power utilization",
            "required": true,
            "values": ["conservative", "balanced", "aggressive", "maximum"],
            "prompt": "How do you prefer to channel your magical power?",
            "help": "Higher power levels enable more advanced features but require greater responsibility"
        },
        {
            "name": "APPRENTICE-MENTORING",
            "type": "string",
            "description": "Willingness to mentor lower roles",
            "required": true,
            "values": ["eager", "selective", "occasional", "focused"],
            "prompt": "Do you wish to mentor apprentices (lower roles)?",
            "help": "This enables mentoring features and assistance capabilities"
        }
    ],
    "adventure": {
        "starting_quest": "master_the_arcane",
        "milestones": ["spells_learned", "power_channeled", "wisdom_shared"],
        "rewards": ["arcane_mastery", "sorcerer_staff", "magical_achievement"]
    }
}
EOF
}

# WIZARD role startup story
create_wizard_story() {
    cat > "$ROLE_STORIES_DIR/wizard-startup.json" << 'EOF'
{
    "metadata": {
        "name": "wizard-startup",
        "title": "🧙‍♂️ Welcome, Supreme Wizard - Master of All Realms",
        "type": "story",
        "role": "WIZARD",
        "level": 100,
        "created": "2025-08-28T00:00:00Z"
    },
    "story": {
        "introduction": "🌟 All hail the Supreme Wizard! You have achieved mastery over all aspects of uDOS. With great power comes great responsibility - let's configure your omnipotent workspace.",
        "context": "Wizards have complete system access, development capabilities, and the power to modify core systems and spawn new users.",
        "purpose": "Configure master-level access and supreme administrative powers",
        "adventure_theme": "supreme_mastery"
    },
    "variables": [
        {
            "name": "MASTERY-FOCUS",
            "type": "string",
            "description": "Primary area of wizardly focus",
            "required": true,
            "values": ["core-development", "system-administration", "user-creation", "realm-expansion", "all-aspects"],
            "prompt": "Where will you direct your supreme powers?",
            "help": "This configures your primary dashboard and available supreme tools"
        },
        {
            "name": "DEV-MODE-PREFERENCE",
            "type": "string",
            "description": "Development mode activation preference",
            "required": true,
            "values": ["always-active", "on-demand", "project-based", "collaborative"],
            "prompt": "How do you want to manage development mode access?",
            "help": "Controls when you have write access to core system folders"
        },
        {
            "name": "REALM-MANAGEMENT",
            "type": "string",
            "description": "Approach to realm oversight",
            "required": true,
            "values": ["hands-on", "delegated", "monitoring", "emergencies-only"],
            "prompt": "How actively do you want to manage the entire realm?",
            "help": "This configures system monitoring and automatic intervention levels"
        },
        {
            "name": "LEGACY-CREATION",
            "type": "string",
            "description": "Focus for lasting contributions",
            "required": true,
            "values": ["tools-and-systems", "knowledge-documentation", "user-empowerment", "innovation-research"],
            "prompt": "What legacy do you wish to create for future users?",
            "help": "This guides suggestion systems and project recommendations"
        }
    ],
    "adventure": {
        "starting_quest": "ascend_to_mastery",
        "milestones": ["power_assumed", "realm_surveyed", "legacy_begun"],
        "rewards": ["supreme_mastery", "wizard_crown", "ultimate_achievement"]
    }
}
EOF
}

# Execute role-specific startup story
run_role_startup_story() {
    local role="$1"
    local role_lower=$(echo "$role" | tr '[:upper:]' '[:lower:]')
    local story_file="$ROLE_STORIES_DIR/${role_lower}-startup.json"

    adventure_log "ROLE_STARTUP" "Beginning $role startup story"

    if [[ ! -f "$story_file" ]]; then
        log_error "Startup story not found for role: $role"
        return 1
    fi

    log_info "🎭 Starting $role role initialization story..."

    # Execute the story using the variable manager
    if [[ -x "$VARIABLE_MANAGER" ]]; then
        "$VARIABLE_MANAGER" STORY EXECUTE "$story_file" "startup-$(date +%s)"
        adventure_log "STORY_COMPLETE" "$role startup story completed successfully"
        log_success "✨ $role startup story completed!"

        # Update adventure log with role-specific achievement
        adventure_log "ACHIEVEMENT" "Role $role successfully initialized with custom configuration"

        return 0
    else
        log_error "Variable manager not available"
        return 1
    fi
}

# Interactive adventure mode
start_interactive_adventure() {
    local current_role=$(get_current_role)

    adventure_log "ADVENTURE_START" "Interactive adventure mode activated for role $current_role"

    echo ""
    echo "🎲 uDOS Interactive Adventure Mode"
    echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
    echo ""
    echo "🎭 Current Role: $current_role"
    echo "📖 Adventure Log: $ADVENTURE_LOG"
    echo ""

    while true; do
        echo "🗡️  Adventure Commands:"
        echo "   1. startup   - Run role-specific startup story"
        echo "   2. quest     - Start a new quest"
        echo "   3. status    - View current adventure status"
        echo "   4. log       - Show recent adventure entries"
        echo "   5. variables - Manage adventure variables"
        echo "   6. role      - Change role (triggers new startup)"
        echo "   7. exit      - Leave adventure mode"
        echo ""

        read -p "🎯 Choose your adventure: " choice

        case "$choice" in
            1|startup)
                run_role_startup_story "$current_role"
                ;;
            2|quest)
                start_new_quest
                ;;
            3|status)
                show_adventure_status
                ;;
            4|log)
                show_adventure_log
                ;;
            5|variables)
                "$VARIABLE_MANAGER" LIST all
                ;;
            6|role)
                change_role_adventure
                ;;
            7|exit)
                adventure_log "ADVENTURE_END" "Adventure mode session ended"
                echo "🌟 Adventure continues... farewell!"
                break
                ;;
            *)
                echo "❓ Unknown command. Choose 1-7."
                ;;
        esac
        echo ""
    done
}

# Start a new quest
start_new_quest() {
    local current_role=$(get_current_role)

    echo "🗡️ Starting new quest for $current_role..."

    # Role-specific quest suggestions
    case "$current_role" in
        "GHOST")
            echo "👻 Ghost Quests:"
            echo "   • Complete the tutorial journey"
            echo "   • Explore demo features"
            echo "   • Master basic commands"
            ;;
        "TOMB")
            echo "🗿 Tomb Keeper Quests:"
            echo "   • Organize your first archive"
            echo "   • Set up backup systems"
            echo "   • Master information storage"
            ;;
        "CRYPT")
            echo "🔐 Crypt Guardian Quests:"
            echo "   • Secure sensitive data"
            echo "   • Configure protection protocols"
            echo "   • Master security features"
            ;;
        "DRONE")
            echo "🤖 Automation Drone Quests:"
            echo "   • Create your first automation"
            echo "   • Optimize workflow efficiency"
            echo "   • Master systematic operations"
            ;;
        "KNIGHT")
            echo "⚔️ Digital Knight Quests:"
            echo "   • Protect system integrity"
            echo "   • Assist fellow users"
            echo "   • Maintain honor code"
            ;;
        "IMP")
            echo "😈 Clever Imp Quests:"
            echo "   • Create innovative solutions"
            echo "   • Build custom tools"
            echo "   • Master creative development"
            ;;
        "SORCERER")
            echo "🧙‍♂️ Sorcerer Quests:"
            echo "   • Channel advanced system magic"
            echo "   • Mentor lower-level users"
            echo "   • Master arcane administration"
            ;;
        "WIZARD")
            echo "🌟 Supreme Wizard Quests:"
            echo "   • Shape the entire realm"
            echo "   • Create lasting legacy"
            echo "   • Master all aspects of uDOS"
            ;;
    esac

    adventure_log "QUEST_START" "New quest initiated for role $current_role"
}

# Show adventure status
show_adventure_status() {
    local current_role=$(get_current_role)
    local quest_count=$(grep -c "QUEST_START" "$ADVENTURE_LOG" 2>/dev/null || echo 0)
    local achievement_count=$(grep -c "ACHIEVEMENT" "$ADVENTURE_LOG" 2>/dev/null || echo 0)

    echo "📊 Adventure Status"
    echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
    echo "🎭 Current Role: $current_role"
    echo "🗡️ Quests Started: $quest_count"
    echo "🏆 Achievements: $achievement_count"
    echo "📅 Adventure Started: $(head -n1 "$ADVENTURE_LOG" 2>/dev/null | cut -d']' -f1 | tr -d '[' || echo 'New adventure')"
}

# Show recent adventure log entries
show_adventure_log() {
    if [[ -f "$ADVENTURE_LOG" ]]; then
        echo "📖 Recent Adventure Log (last 10 entries)"
        echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
        tail -n10 "$ADVENTURE_LOG"
    else
        echo "📖 No adventures recorded yet!"
    fi
}

# Change role with adventure tracking
change_role_adventure() {
    echo "🎭 Role Change Adventure"
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
            local old_role=$(get_current_role)

            # Update role file
            cat > "$UDOS_ROOT/sandbox/current-role.conf" << EOF
ROLE="$new_role"
PREVIOUS_ROLE="$old_role"
TIMESTAMP="$(date '+%Y-%m-%d %H:%M:%S %Z')"
TRANSITION_REASON="Adventure mode role change"
EOF

            adventure_log "ROLE_CHANGE" "Changed from $old_role to $new_role"
            log_success "🎭 Role changed to $new_role!"

            # Offer to run new role startup story
            read -p "🌟 Run $new_role startup story? (y/n): " run_startup
            if [[ "$run_startup" =~ ^[Yy] ]]; then
                run_role_startup_story "$new_role"
            fi
            ;;
        *)
            echo "❌ Invalid role choice"
            ;;
    esac
}

# Main command handler
main() {
    local command="${1:-help}"

    case "$command" in
        "create-stories")
            create_role_startup_stories
            ;;
        "startup")
            local role="${2:-$(get_current_role)}"
            run_role_startup_story "$role"
            ;;
        "adventure")
            start_interactive_adventure
            ;;
        "status")
            show_adventure_status
            ;;
        "log")
            show_adventure_log
            ;;
        "help"|*)
            echo "🎭 uDOS Startup Story Manager & Adventure System"
            echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
            echo ""
            echo "Commands:"
            echo "  create-stories    Create all role-specific startup stories"
            echo "  startup [ROLE]    Run startup story for specified role"
            echo "  adventure         Enter interactive adventure mode"
            echo "  status           Show current adventure status"
            echo "  log              Show recent adventure log"
            echo "  help             Show this help"
            echo ""
            echo "Examples:"
            echo "  $0 create-stories"
            echo "  $0 startup WIZARD"
            echo "  $0 adventure"
            ;;
    esac
}

# Execute main function with all arguments
main "$@"
