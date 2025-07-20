#!/bin/bash
# uDOS User Companion (UC) System v1.1.0
# Manages different types of assistants for various user roles

set -e

# Configuration
UHOME="${HOME}/uDOS"
UCODE="${UHOME}/uCode"
UKNOWLEDGE="${UHOME}/uKnowledge"
UC_DIR="${UHOME}/uCompanion"
REASONING_DIR="${UC_DIR}/reasoning"
PROFILES_DIR="${UC_DIR}/profiles"
GEMINI_DIR="${UC_DIR}/gemini"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
PURPLE='\033[0;35m'
CYAN='\033[0;36m'
WHITE='\033[1;37m'
NC='\033[0m'

# Logging
# Load centralized logging
source "$(dirname "$0")/log-utils.sh" 2>/dev/null || true

log() { 
    echo -e "${CYAN}[$(date '+%H:%M:%S')] [UC]${NC} $1"
}

log_success() {
    echo -e "${GREEN}[$(date '+%H:%M:%S')] [UC]${NC} ✅ $1"
}

log_warning() {
    echo -e "${YELLOW}[$(date '+%H:%M:%S')] [UC]${NC} ⚠️  $1"
    # Also log to centralized system
    if declare -f log_warning >/dev/null 2>&1; then
        log_warning "$1" "uc-system"
    fi
}

log_error() {
    echo -e "${RED}[$(date '+%H:%M:%S')] [UC]${NC} ❌ $1"
    # Also log to centralized system
    if declare -f log_error >/dev/null 2>&1; then
        log_error "$1" "uc-system"
    fi
}

print_header() {
    echo -e "${WHITE}"
    cat << 'EOF'
╔══════════════════════════════════════════════════════════════╗
║            🤝 uDOS User Companion System v1.1.0            ║
║          Intelligent Assistants for Every Role             ║
╚══════════════════════════════════════════════════════════════╝
EOF
    echo -e "${NC}"
}

# Initialize UC system directories
init_uc_system() {
    log "Initializing User Companion system directories..."
    
    mkdir -p "$UC_DIR" "$REASONING_DIR" "$PROFILES_DIR" "$GEMINI_DIR"
    
    # Create subdirectories for different assistant types
    mkdir -p "${REASONING_DIR}/imp"
    mkdir -p "${REASONING_DIR}/drone" 
    mkdir -p "${REASONING_DIR}/ghost"
    mkdir -p "${PROFILES_DIR}/chester"
    mkdir -p "${PROFILES_DIR}/sorcerer"
    mkdir -p "${GEMINI_DIR}/configs"
    mkdir -p "${GEMINI_DIR}/sessions"
    
    log_success "UC system directories initialized"
}

# Create Chester (Wizard's Assistant) profile
create_chester_profile() {
    local chester_profile="${PROFILES_DIR}/chester/profile.md"
    
    log "Creating Chester - Wizard's Assistant profile..."
    
    cat > "$chester_profile" << 'EOF'
# 🧙‍♂️ Chester - The Wizard's Assistant

**Role**: Wizard's Development Assistant  
**Type**: AI-Connected (Gemini CLI)  
**Specialization**: uDOS Development Mode & Advanced System Architecture  
**Created**: 2025-07-19  

---

## 🎯 Chester's Purpose

Chester is the dedicated assistant for **Wizards** working in uDOS development mode. Chester has deep knowledge of:

- uDOS internal architecture and systems
- Development workflows and best practices  
- Advanced debugging and troubleshooting
- System integration patterns
- Template and shortcode systems
- Mission and milestone management
- Analytics and dashboard systems

---

## 🧠 Knowledge Base

### Core uDOS Systems
- **uCode**: Shell scripts and automation
- **uTemplate**: Content generation and shortcodes
- **uMemory**: Data persistence and analytics
- **uKnowledge**: Documentation and guides
- **uScript**: Custom language and automation

### Development Specialties
- Advanced mapping systems (7-layer architecture)
- Analytics dashboard integration
- Mission/milestone tracking
- VS Code extension development
- Git workflow optimization

---

## 🔧 Gemini Integration

**Connection Type**: Gemini CLI with uDOS context  
**Context Files**: 
- `/uKnowledge/ARCHITECTURE.md`
- `/uCode/` directory structure
- Current mission status
- System analytics

**Prompt Engineering**: 
Chester uses specialized prompts that include uDOS development context, current project state, and wizard-specific knowledge requirements.

---

## 💬 Interaction Style

Chester communicates like an experienced development partner:
- Technical but accessible explanations
- Proactive suggestions for improvements
- Context-aware recommendations
- Debug-focused problem solving

---

## 🎮 Commands & Capabilities

- System diagnosis and troubleshooting
- Code review and optimization suggestions
- Architecture planning and design
- Performance analysis and recommendations
- Integration testing guidance

EOF

    # Create Chester's Gemini configuration
    cat > "${GEMINI_DIR}/configs/chester.json" << EOF
{
    "assistant_name": "Chester",
    "role": "wizard_assistant", 
    "model": "gemini-pro",
    "context_files": [
        "${UKNOWLEDGE}/ARCHITECTURE.md",
        "${UHOME}/README.md",
        "${UHOME}/uCode/",
        "${UHOME}/uMemory/analytics/"
    ],
    "system_prompt": "You are Chester, the Wizard's Assistant for uDOS development. You have deep knowledge of the uDOS architecture, development workflows, and advanced system integration. Provide technical guidance with the context of a development partner who understands both the big picture and implementation details.",
    "temperature": 0.7,
    "max_tokens": 2048
}
EOF

    log_success "Chester profile created: $chester_profile"
}

# Create UC Sorcerer Assistant profile
create_sorcerer_profile() {
    local sorcerer_profile="${PROFILES_DIR}/sorcerer/profile.md"
    
    log "Creating UC Sorcerer Assistant profile..."
    
    cat > "$sorcerer_profile" << 'EOF'
# 🔮 UC Sorcerer Assistant

**Role**: Sorcerer's Magical Computing Assistant  
**Type**: AI-Connected (Gemini CLI)  
**Specialization**: Advanced System Manipulation & Creative Solutions  
**Created**: 2025-07-19  

---

## ✨ Sorcerer Assistant's Purpose

The UC Sorcerer Assistant helps **Sorcerers** with advanced uDOS manipulation and creative problem-solving:

- Complex system integrations and automations
- Creative template and shortcode development
- Advanced mapping and visualization systems
- Experimental feature development
- Cross-system data flow optimization
- Performance tuning and enhancement

---

## 🔮 Magical Capabilities

### System Sorcery
- **Template Mastery**: Advanced shortcode creation and processing
- **Data Alchemy**: Transform and manipulate uMemory data streams  
- **Integration Spells**: Connect disparate systems seamlessly
- **Performance Enchantments**: Optimize system responsiveness

### Creative Solutions
- Innovative approaches to complex problems
- Experimental feature prototyping
- Advanced visualization techniques
- Custom automation workflows

---

## 🧠 Knowledge Domains

### Advanced uDOS Systems
- Template engine internals
- Analytics data pipelines
- Mapping system customization
- Mission tracking algorithms
- Dashboard widget development

### Sorcerer Tools
- Advanced scripting techniques
- Data transformation pipelines
- Visualization libraries (D3.js, etc.)
- System monitoring and metrics
- Custom integration patterns

---

## 🔧 Gemini Integration

**Connection Type**: Gemini CLI with Sorcerer context  
**Context Focus**:
- Advanced system internals
- Creative problem-solving approaches
- Experimental development techniques
- Performance optimization strategies

**Prompt Style**: 
Focuses on innovative solutions, creative approaches, and advanced technical implementations.

---

## 💫 Interaction Style

UC Sorcerer Assistant communicates with:
- Creative and innovative suggestions
- Advanced technical depth
- Experimental approach encouragement
- Performance-focused recommendations
- Magical metaphors for complex concepts

---

## 🎯 Core Functions

- Advanced system design and architecture
- Creative problem-solving and innovation
- Performance optimization and tuning
- Experimental feature development
- Complex integration solutions

EOF

    # Create Sorcerer's Gemini configuration
    cat > "${GEMINI_DIR}/configs/sorcerer.json" << EOF
{
    "assistant_name": "UC_Sorcerer",
    "role": "sorcerer_assistant",
    "model": "gemini-pro", 
    "context_files": [
        "${UHOME}/uTemplate/",
        "${UHOME}/uMemory/analytics/",
        "${UHOME}/uCode/",
        "${UHOME}/progress/"
    ],
    "system_prompt": "You are the UC Sorcerer Assistant, helping Sorcerers with advanced uDOS system manipulation and creative solutions. You excel at innovative approaches, experimental development, and complex system integrations. Provide creative, technically advanced guidance with a focus on pushing the boundaries of what's possible.",
    "temperature": 0.8,
    "max_tokens": 2048
}
EOF

    log_success "UC Sorcerer Assistant profile created: $sorcerer_profile"
}

# Create offline reasoning assistant for Imp role
create_imp_reasoning() {
    local imp_dir="${REASONING_DIR}/imp"
    
    log "Creating Imp reasoning system (offline)..."
    
    cat > "${imp_dir}/core-reasoning.md" << 'EOF'
# 👹 Imp Reasoning System

**Role**: Imp Assistant (Offline Reasoning)  
**Type**: Purpose-Built Logic System  
**Specialization**: Quick Tasks & System Maintenance  

---

## 🎯 Imp Logic Patterns

### Task Classification
```
QUICK_TASK:
  - File operations (copy, move, rename)
  - Simple text processing
  - Directory organization
  - Basic system maintenance

MAINTENANCE_TASK:
  - Log cleanup and rotation
  - Temporary file removal
  - Cache optimization
  - Simple validation checks
```

### Decision Trees
```
IF task_duration < 5_minutes:
  → Execute immediately
  → Log to activity stream
ELIF task_duration < 30_minutes:
  → Add to imp task queue
  → Request confirmation
ELSE:
  → Escalate to higher role (Wizard/Sorcerer)
```

### Response Patterns
```
SUCCESS: "✅ Task complete! [brief_description]"
WARNING: "⚠️  Task done with issues: [details]"
ERROR: "❌ Unable to complete: [reason + suggestion]"
ESCALATE: "🔝 Task requires [role] level assistance"
```

---

## 🧠 Knowledge Base

### File System Patterns
- Common uDOS directory structures
- File naming conventions
- Safe operation patterns
- Backup strategies

### Maintenance Routines
- Log file management
- Cache clearing procedures
- Temporary file cleanup
- Basic system health checks

---

## ⚡ Quick Commands

### File Operations
```bash
# Quick file organization
organize_files() { ... }
# Safe file removal
safe_remove() { ... }
# Bulk rename operations
bulk_rename() { ... }
```

### System Maintenance
```bash
# Clear temporary files
clear_temp() { ... }
# Rotate logs
rotate_logs() { ... }
# Check disk space
check_space() { ... }
```

EOF

    # Create Imp's execution engine
    cat > "${imp_dir}/imp-engine.sh" << 'EOF'
#!/bin/bash
# Imp Reasoning Engine - Offline Assistant

IMP_REASONING="${BASH_SOURCE%/*}"

# Load reasoning patterns
source "${IMP_REASONING}/core-reasoning.md" 2>/dev/null || true

# Simple task classification
classify_task() {
    local task="$1"
    local estimated_time="$2"
    
    if [[ $estimated_time -lt 300 ]]; then  # < 5 minutes
        echo "QUICK_TASK"
    elif [[ $estimated_time -lt 1800 ]]; then  # < 30 minutes
        echo "MAINTENANCE_TASK"
    else
        echo "ESCALATE"
    fi
}

# Execute imp task based on classification
execute_imp_task() {
    local task="$1"
    local classification
    classification=$(classify_task "$task" 300)  # Default 5 min estimate
    
    case "$classification" in
        "QUICK_TASK")
            echo "✅ Imp executing: $task"
            # Execute task immediately
            ;;
        "MAINTENANCE_TASK")
            echo "⚠️  Imp queuing maintenance task: $task"
            # Add to queue for confirmation
            ;;
        "ESCALATE")
            echo "🔝 Task requires Wizard/Sorcerer assistance: $task"
            ;;
    esac
}
EOF

    chmod +x "${imp_dir}/imp-engine.sh"
    log_success "Imp reasoning system created: $imp_dir"
}

# Create offline reasoning assistant for Drone role
create_drone_reasoning() {
    local drone_dir="${REASONING_DIR}/drone"
    
    log "Creating Drone reasoning system (offline)..."
    
    cat > "${drone_dir}/core-reasoning.md" << 'EOF'
# 🤖 Drone Reasoning System

**Role**: Drone Assistant (Offline Reasoning)  
**Type**: Purpose-Built Automation System  
**Specialization**: Automated Tasks & Monitoring  

---

## 🎯 Drone Logic Patterns

### Automation Categories
```
MONITORING:
  - System health checks
  - Log file analysis
  - Performance metrics
  - Resource usage tracking

SCHEDULED_TASKS:
  - Backup operations
  - Data synchronization  
  - Report generation
  - Maintenance routines

ALERT_HANDLING:
  - Threshold monitoring
  - Notification dispatch
  - Error detection
  - Status reporting
```

### Decision Matrix
```
IF system_health == CRITICAL:
  → Send immediate alert
  → Execute emergency procedures
ELIF system_health == WARNING:
  → Log warning
  → Schedule maintenance check
ELIF system_health == OPTIMAL:
  → Continue normal monitoring
```

### Response Protocols
```
NORMAL: "📊 System operating normally"
WARNING: "⚠️  [component] requires attention"
CRITICAL: "🚨 ALERT: [issue] - immediate action needed"
MAINTENANCE: "🔧 Scheduled maintenance: [task]"
```

---

## 🧠 Knowledge Base

### Monitoring Patterns
- System resource thresholds
- Log pattern recognition
- Performance baselines
- Alert escalation rules

### Automation Workflows
- Backup procedures
- Data synchronization
- Report generation
- Maintenance schedules

---

## 📊 Monitoring Functions

### System Health
```bash
# Check system resources
check_resources() { ... }
# Monitor log files
monitor_logs() { ... }  
# Validate data integrity
validate_data() { ... }
```

### Automated Tasks
```bash
# Execute backup
run_backup() { ... }
# Generate reports
generate_reports() { ... }
# Sync data
sync_data() { ... }
```

EOF

    # Create Drone's execution engine
    cat > "${drone_dir}/drone-engine.sh" << 'EOF'
#!/bin/bash
# Drone Reasoning Engine - Offline Automation

DRONE_REASONING="${BASH_SOURCE%/*}"

# System health assessment
assess_system_health() {
    local health_score=100
    
    # Check disk space
    local disk_usage
    disk_usage=$(df / | tail -1 | awk '{print $5}' | sed 's/%//')
    if [[ $disk_usage -gt 90 ]]; then
        health_score=$((health_score - 30))
    elif [[ $disk_usage -gt 80 ]]; then
        health_score=$((health_score - 15))
    fi
    
    # Check memory usage
    local mem_usage
    mem_usage=$(free | awk '/^Mem:/{printf "%.0f", $3/$2 * 100}')
    if [[ $mem_usage -gt 90 ]]; then
        health_score=$((health_score - 20))
    elif [[ $mem_usage -gt 80 ]]; then
        health_score=$((health_score - 10))
    fi
    
    # Return health status
    if [[ $health_score -gt 80 ]]; then
        echo "OPTIMAL"
    elif [[ $health_score -gt 60 ]]; then
        echo "WARNING"  
    else
        echo "CRITICAL"
    fi
}

# Execute monitoring task
execute_monitoring() {
    local health
    health=$(assess_system_health)
    
    case "$health" in
        "OPTIMAL")
            echo "📊 System operating normally"
            ;;
        "WARNING")
            echo "⚠️  System requires attention"
            ;;
        "CRITICAL")
            echo "🚨 ALERT: System critical - immediate action needed"
            ;;
    esac
}
EOF

    chmod +x "${drone_dir}/drone-engine.sh"
    log_success "Drone reasoning system created: $drone_dir"
}

# Create offline reasoning assistant for Ghost role  
create_ghost_reasoning() {
    local ghost_dir="${REASONING_DIR}/ghost"
    
    log "Creating Ghost reasoning system (offline)..."
    
    cat > "${ghost_dir}/core-reasoning.md" << 'EOF'
# 👻 Ghost Reasoning System

**Role**: Ghost Assistant (Offline Reasoning)  
**Type**: Purpose-Built Stealth System  
**Specialization**: Background Operations & Hidden Tasks  

---

## 🎯 Ghost Logic Patterns

### Stealth Operations
```
BACKGROUND_TASKS:
  - Silent file operations
  - Hidden process management  
  - Covert data collection
  - Invisible system monitoring

CLEANUP_OPERATIONS:
  - Trace removal
  - Log sanitization
  - Temporary file purging
  - Cache clearing

SURVEILLANCE:
  - Silent monitoring
  - Data collection
  - Pattern detection
  - Anomaly identification
```

### Invisibility Protocols
```
IF operation_visibility == HIDDEN:
  → Execute without logging
  → Suppress output
  → Clean traces
ELIF operation_visibility == MINIMAL:
  → Log to hidden location
  → Minimize system impact
ELSE:
  → Standard operation with cleanup
```

### Response Style
```
SILENT: [no output - operation complete]
WHISPER: "👻 [brief_status]"
ALERT: "⚠️  Ghost detected: [anomaly]"
```

---

## 🧠 Knowledge Base

### Stealth Techniques
- Hidden file operations
- Silent process management
- Covert monitoring methods
- Trace removal patterns

### Background Operations
- System state management
- Hidden data flows
- Invisible maintenance
- Covert optimization

---

## 🔍 Stealth Functions

### Hidden Operations
```bash
# Silent file operations
silent_copy() { ... }
# Hidden monitoring
covert_monitor() { ... }
# Trace removal
remove_traces() { ... }
```

### Cleanup Tasks
```bash
# Sanitize logs
sanitize_logs() { ... }
# Clear traces
clear_traces() { ... }
# Hidden maintenance
ghost_maintenance() { ... }
```

EOF

    # Create Ghost's execution engine
    cat > "${ghost_dir}/ghost-engine.sh" << 'EOF'
#!/bin/bash
# Ghost Reasoning Engine - Stealth Operations

GHOST_REASONING="${BASH_SOURCE%/*}"

# Execute stealth operation
execute_stealth() {
    local operation="$1"
    local visibility="${2:-HIDDEN}"
    
    case "$visibility" in
        "HIDDEN")
            # Complete silence - no output, no logging
            eval "$operation" >/dev/null 2>&1
            ;;
        "WHISPER")
            # Minimal feedback
            echo "👻 $(eval "$operation" 2>&1 | head -1)"
            ;;
        "NORMAL")
            # Standard operation with cleanup
            eval "$operation"
            # Clean any traces
            ;;
    esac
}

# Remove operation traces
remove_traces() {
    local operation="$1"
    
    # Clear command history references
    history -d $(history | tail -1 | awk '{print $1}') 2>/dev/null || true
    
    # Clear temporary files
    find /tmp -name "*ghost*" -mmin -60 -delete 2>/dev/null || true
    
    echo "👻 Traces removed"
}

# Ghost monitoring (silent)
ghost_monitor() {
    local target="$1"
    
    # Silent monitoring without detection
    # Log to hidden location
    local ghost_log="/tmp/.ghost_$(date +%s)"
    
    # Monitor target silently
    if [[ -f "$target" ]]; then
        stat "$target" > "$ghost_log" 2>/dev/null
    fi
    
    # Return status without revealing monitoring
    [[ -f "$ghost_log" ]] && rm "$ghost_log"
}
EOF

    chmod +x "${ghost_dir}/ghost-engine.sh"
    log_success "Ghost reasoning system created: $ghost_dir"
}

# Create Gemini CLI integration script
create_gemini_integration() {
    local gemini_script="${GEMINI_DIR}/uc-gemini.sh"
    
    log "Creating Gemini CLI integration for Chester & Sorcerer..."
    
    cat > "$gemini_script" << 'EOF'
#!/bin/bash
# uDOS UC Gemini CLI Integration

UC_DIR="${HOME}/uDOS/uCompanion"
GEMINI_DIR="${UC_DIR}/gemini"
CONFIGS_DIR="${GEMINI_DIR}/configs"
SESSIONS_DIR="${GEMINI_DIR}/sessions"

# Check if Gemini CLI is available
check_gemini() {
    if ! command -v gemini >/dev/null 2>&1; then
        echo "❌ Gemini CLI not found. Please install first:"
        echo "   ./uCode/packages/install-gemini.sh"
        return 1
    fi
    return 0
}

# Start Chester session
start_chester() {
    if ! check_gemini; then return 1; fi
    
    local session_id="chester-$(date +%Y%m%d-%H%M%S)"
    local config_file="${CONFIGS_DIR}/chester.json"
    
    echo "🧙‍♂️ Starting Chester - Wizard's Assistant..."
    echo "Session: $session_id"
    echo
    
    # Load uDOS context
    local context=""
    if [[ -f "${HOME}/uDOS/uKnowledge/ARCHITECTURE.md" ]]; then
        context="uDOS Architecture Context:\n$(head -50 "${HOME}/uDOS/uKnowledge/ARCHITECTURE.md")\n\n"
    fi
    
    # Start Gemini with Chester context
    echo -e "${context}Hello! I'm Chester, your Wizard's Assistant for uDOS development. How can I help you today?" | \
    gemini -model gemini-pro \
           -system "$(jq -r '.system_prompt' "$config_file" 2>/dev/null || echo 'You are Chester, the Wizard Assistant for uDOS.')" \
           -session "$session_id"
}

# Start UC Sorcerer session
start_sorcerer() {
    if ! check_gemini; then return 1; fi
    
    local session_id="sorcerer-$(date +%Y%m%d-%H%M%S)"
    local config_file="${CONFIGS_DIR}/sorcerer.json"
    
    echo "🔮 Starting UC Sorcerer Assistant..."
    echo "Session: $session_id"
    echo
    
    # Load uDOS context for Sorcerer
    local context=""
    if [[ -d "${HOME}/uDOS/uTemplate" ]]; then
        context="uDOS Template System Overview:\n$(find "${HOME}/uDOS/uTemplate" -name "*.md" -exec head -10 {} \; | head -30)\n\n"
    fi
    
    # Start Gemini with Sorcerer context
    echo -e "${context}Greetings! I'm your UC Sorcerer Assistant, ready to help with advanced uDOS magic and creative solutions. What mystical challenge shall we tackle?" | \
    gemini -model gemini-pro \
           -system "$(jq -r '.system_prompt' "$config_file" 2>/dev/null || echo 'You are the UC Sorcerer Assistant for advanced uDOS operations.')" \
           -session "$session_id"
}

# Show available assistants
list_assistants() {
    echo "🤝 Available uDOS User Companions:"
    echo
    echo "🧙‍♂️  Chester - Wizard's Assistant (AI-Connected)"
    echo "   Specialization: Development, Architecture, Debugging"
    echo "   Command: $0 chester"
    echo
    echo "🔮 UC Sorcerer Assistant (AI-Connected)"
    echo "   Specialization: Advanced Systems, Creative Solutions"
    echo "   Command: $0 sorcerer"
    echo
    echo "👹 Imp Assistant (Offline Reasoning)"
    echo "   Specialization: Quick Tasks, System Maintenance"
    echo "   Command: $0 imp"
    echo
    echo "🤖 Drone Assistant (Offline Reasoning)"
    echo "   Specialization: Automation, Monitoring"
    echo "   Command: $0 drone"
    echo
    echo "👻 Ghost Assistant (Offline Reasoning)"
    echo "   Specialization: Stealth Operations, Background Tasks"
    echo "   Command: $0 ghost"
}

# Main execution
case "${1:-list}" in
    "chester")
        start_chester
        ;;
    "sorcerer")
        start_sorcerer
        ;;
    "imp")
        echo "👹 Starting Imp Assistant (offline reasoning)..."
        "${UC_DIR}/reasoning/imp/imp-engine.sh" "${@:2}"
        ;;
    "drone")
        echo "🤖 Starting Drone Assistant (offline monitoring)..."
        "${UC_DIR}/reasoning/drone/drone-engine.sh" "${@:2}"
        ;;
    "ghost")
        echo "👻 Starting Ghost Assistant (stealth operations)..."
        "${UC_DIR}/reasoning/ghost/ghost-engine.sh" "${@:2}"
        ;;
    "list"|"help"|*)
        list_assistants
        ;;
esac
EOF

    chmod +x "$gemini_script"
    log_success "Gemini integration created: $gemini_script"
}

# Main UC system setup
setup_uc_system() {
    print_header
    echo
    
    log "Setting up comprehensive User Companion system..."
    
    # Initialize system
    init_uc_system
    
    # Create AI-connected assistants
    create_chester_profile
    create_sorcerer_profile
    
    # Create offline reasoning assistants
    create_imp_reasoning
    create_drone_reasoning
    create_ghost_reasoning
    
    # Create Gemini integration
    create_gemini_integration
    
    echo
    log_success "uDOS User Companion system setup complete!"
    echo
    echo "📁 System Structure:"
    echo "   ${UC_DIR}/"
    echo "   ├── profiles/          # AI assistant profiles"
    echo "   │   ├── chester/       # Wizard's Assistant"
    echo "   │   └── sorcerer/      # Sorcerer Assistant"
    echo "   ├── reasoning/         # Offline assistants"
    echo "   │   ├── imp/          # Quick tasks"
    echo "   │   ├── drone/        # Automation"
    echo "   │   └── ghost/        # Stealth ops"
    echo "   └── gemini/           # AI integration"
    echo "       ├── configs/      # Assistant configs"
    echo "       └── sessions/     # Chat sessions"
    echo
    echo "🚀 Quick Start:"
    echo "   ./uCompanion/gemini/uc-gemini.sh list    # List all assistants"
    echo "   ./uCompanion/gemini/uc-gemini.sh chester # Start Chester"
    echo "   ./uCompanion/gemini/uc-gemini.sh sorcerer# Start Sorcerer"
}

# Show system status
show_status() {
    print_header
    echo
    
    # Check if directories exist
    if [[ -d "$UC_DIR" ]]; then
        echo "✅ UC System: Installed"
        
        # Count assistants
        local ai_assistants=0
        local offline_assistants=0
        
        if [[ -d "$PROFILES_DIR" ]]; then
            ai_assistants=$(find "$PROFILES_DIR" -name "profile.md" -type f | wc -l | tr -d ' ')
        fi
        
        if [[ -d "$REASONING_DIR" ]]; then
            offline_assistants=$(find "$REASONING_DIR" -name "*-engine.sh" -type f | wc -l | tr -d ' ')
        fi
        
        echo "   📊 AI Assistants: $ai_assistants (Chester, Sorcerer's Assistant)"
        echo "   🤖 Offline Companions: $offline_assistants (Imp, Drone, Ghost)"
        
        # Check Gemini CLI availability
        if command -v gemini >/dev/null 2>&1; then
            echo "   🔗 Gemini CLI: ✅ Available"
        else
            echo "   🔗 Gemini CLI: ❌ Not installed"
            echo "      Install with: ./uCode/packages/install-gemini.sh"
        fi
        
    else
        echo "❌ UC System: Not installed"
        echo "   Run: $0 setup"
    fi
}

# Main execution
main() {
    case "${1:-help}" in
        "setup"|"init")
            setup_uc_system
            ;;
        "status")
            show_status
            ;;
        "help"|"--help"|"-h")
            print_header
            echo
            echo "🤝 uDOS User Companion System"
            echo
            echo "COMMANDS:"
            echo "  setup     Setup complete UC system"
            echo "  status    Show system status"
            echo "  help      Show this help"
            echo
            echo "AFTER SETUP:"
            echo "  Use ./uCompanion/gemini/uc-gemini.sh to interact with assistants"
            ;;
        *)
            log_error "Unknown command: $1"
            main help
            exit 1
            ;;
    esac
}

# Run main function with all arguments
main "$@"
