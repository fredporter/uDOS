#!/bin/bash
# uCORE User Setup Script
# Automatically runs user setup when sandbox/user.md is missing

set -euo pipefail

# Get script directory
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
UDOS_ROOT="$(cd "$SCRIPT_DIR/../../.." && pwd)"

# Logging functions
log_info() { echo -e "\033[0;36m[INFO]\033[0m $1"; }
log_success() { echo -e "\033[0;32m[SUCCESS]\033[0m $1"; }
log_warning() { echo -e "\033[0;33m[WARNING]\033[0m $1"; }
log_error() { echo -e "\033[0;31m[ERROR]\033[0m $1"; }

# Check if user setup is needed
check_user_setup() {
    local user_file="$UDOS_ROOT/sandbox/user.md"

    if [ ! -f "$user_file" ]; then
        log_warning "User profile not found: $user_file"
        return 1
    fi

    # Check if profile is complete
    if ! grep -q "^name:" "$user_file" 2>/dev/null; then
        log_warning "Incomplete user profile detected"
        return 1
    fi

    return 0
}

# Run interactive user setup
run_user_setup() {
    log_info "Starting user setup wizard..."
    echo ""
    echo "╔══════════════════════════════════════════════════════════════════╗"
    echo "║                    🎭 uDOS v1.0.4.1 Setup                      ║"
    echo "║              Welcome to your development environment             ║"
    echo "╚══════════════════════════════════════════════════════════════════╝"
    echo ""

    # Collect user information
    collect_user_info

    # Create user files
    create_user_files

    # Run post-setup actions
    run_post_setup

    log_success "User setup completed successfully!"
}

# Collect user information interactively
collect_user_info() {
    # Username
    read -p "Enter your username [$(whoami)]: " username
    username=${username:-$(whoami)}

    # Display name
    read -p "Your full name or display name [$username]: " display_name
    display_name=${display_name:-$username}

    # Email (optional)
    read -p "Email address (optional): " email

    # Location
    read -p "Your primary location: " location
    while [ -z "$location" ]; do
        read -p "Location is required. Please enter your city/region: " location
    done

    # Timezone (try to detect)
    local system_timezone=""
    if command -v timedatectl >/dev/null 2>&1; then
        system_timezone=$(timedatectl show --property=Timezone --value 2>/dev/null || echo "")
    fi
    if [ -z "$system_timezone" ]; then
        system_timezone=$(date +%Z 2>/dev/null || echo "UTC")
    fi

    read -p "Timezone [$system_timezone]: " timezone
    timezone=${timezone:-$system_timezone}

    # Role
    echo ""
    echo "Available roles:"
    echo "  Ghost     - Demo/read-only access"
    echo "  Tomb      - Basic storage and operations"
    echo "  Crypt     - Secure storage and standard operations"
    echo "  Drone     - Automation tasks and maintenance"
    echo "  Knight    - Security functions and operations"
    echo "  Imp       - Development tools and automation"
    echo "  Sorcerer  - Advanced administration"
    echo "  Wizard    - Full development access"
    echo ""
    read -p "Choose your default role [Wizard]: " role
    role=${role:-Wizard}

    # Theme
    echo ""
    echo "Available themes:"
    echo "  Polaroid, Retro-Unicorn, Nostalgia, Tropical-Sunrise"
    echo "  Pastel-Power, Arcade-Pastels, Grayscale, Solar-Punk"
    echo ""
    read -p "Choose theme [Polaroid]: " theme
    theme=${theme:-Polaroid}

    # Development mode
    read -p "Enable development features? [y/N]: " dev_mode
    dev_mode=${dev_mode:-n}
    if [[ "$dev_mode" =~ ^[Yy] ]]; then
        development_mode="true"
    else
        development_mode="false"
    fi

    # Auto backup
    read -p "Enable automatic backup? [Y/n]: " backup
    backup=${backup:-y}
    if [[ "$backup" =~ ^[Nn] ]]; then
        auto_backup="false"
    else
        auto_backup="true"
    fi

    # Installation lifespan
    echo ""
    echo "Installation Lifespan Planning:"
    echo "  This helps plan the lifecycle of your uDOS installation"
    echo "  Typical lifespans: 6 months (project), 12 months (personal), 24+ months (long-term)"
    echo ""
    read -p "Planned installation lifespan in months [12]: " lifespan_months
    lifespan_months=${lifespan_months:-12}

    # Store variables for file creation
    export SETUP_USERNAME="$username"
    export SETUP_DISPLAY_NAME="$display_name"
    export SETUP_EMAIL="$email"
    export SETUP_LOCATION="$location"
    export SETUP_TIMEZONE="$timezone"
    export SETUP_ROLE="$role"
    export SETUP_THEME="$theme"
    export SETUP_DEVELOPMENT_MODE="$development_mode"
    export SETUP_AUTO_BACKUP="$auto_backup"
    export SETUP_LIFESPAN_MONTHS="$lifespan_months"
}

# Create user files
create_user_files() {
    log_info "Creating user files..."

    # Create directories
    mkdir -p "$UDOS_ROOT/sandbox"
    mkdir -p "$UDOS_ROOT/uMEMORY/user"
    mkdir -p "$UDOS_ROOT/uMEMORY/system"

    # Create sandbox user file
    local user_file="$UDOS_ROOT/sandbox/user.md"
    cat > "$user_file" << EOF
# User Profile

name: $SETUP_DISPLAY_NAME
username: $SETUP_USERNAME
email: $SETUP_EMAIL
role: $SETUP_ROLE
location: $SETUP_LOCATION
timezone: $SETUP_TIMEZONE
theme: $SETUP_THEME
created: $(date '+%Y-%m-%d')
last_login: $(date '+%Y-%m-%d %H:%M:%S')
user_id: $(echo "$SETUP_USERNAME" | tr '[:upper:]' '[:lower:]' | sed 's/[^a-z0-9]//g')
development_mode: $SETUP_DEVELOPMENT_MODE
auto_backup: $SETUP_AUTO_BACKUP
logging_level: INFO
EOF

    log_success "Created user profile: $user_file"

    # Create user profile in uMEMORY
    local user_id=$(echo "$SETUP_USERNAME" | tr '[:upper:]' '[:lower:]' | sed 's/[^a-z0-9]//g')
    local profile_file="$UDOS_ROOT/uMEMORY/user/profile-$user_id.md"
    cat > "$profile_file" << EOF
# uDOS User Profile

**Name**: $SETUP_DISPLAY_NAME
**Username**: $SETUP_USERNAME
**User ID**: $user_id
**Created**: $(date '+%Y-%m-%d %H:%M:%S')
**Version**: v1.0.4.1

## Identity & Contact
- **Display Name**: $SETUP_DISPLAY_NAME
- **Email**: $SETUP_EMAIL
- **Location**: $SETUP_LOCATION
- **Timezone**: $SETUP_TIMEZONE

## System Configuration
- **Default Role**: $SETUP_ROLE
- **Theme**: $SETUP_THEME
- **Development Mode**: $SETUP_DEVELOPMENT_MODE
- **Auto Backup**: $SETUP_AUTO_BACKUP
- **Logging Level**: INFO

## File Organization
- **User ID**: $user_id
- **Created**: $(date '+%Y-%m-%d %H:%M:%S')

---

*Profile generated by uDOS v1.0.4.1 setup system*
EOF

    log_success "Created user profile: $profile_file"

    # Create environment file
    local env_file="$UDOS_ROOT/uMEMORY/system/environment-$user_id.sh"
    cat > "$env_file" << 'EOF'
#!/bin/bash
# uDOS System Environment Variables
# Generated by setup script

# User Identity
export UDOS_USERNAME="$SETUP_USERNAME"
export UDOS_USER_ID="$user_id"
export UDOS_DISPLAY_NAME="$SETUP_DISPLAY_NAME"
export UDOS_EMAIL="$SETUP_EMAIL"

# Location & Time
export UDOS_LOCATION="$SETUP_LOCATION"
export UDOS_TIMEZONE="$SETUP_TIMEZONE"

# System Configuration
export UDOS_ROLE="$SETUP_ROLE"
export UDOS_THEME="$SETUP_THEME"
export UDOS_DEVELOPMENT_MODE="$SETUP_DEVELOPMENT_MODE"
export UDOS_AUTO_BACKUP="$SETUP_AUTO_BACKUP"
export UDOS_LOGGING_LEVEL="INFO"

# System Metadata
export UDOS_VERSION="v1.0.4.1"
export UDOS_CREATED="$(date '+%Y-%m-%d %H:%M:%S')"

# Path Configuration
export UDOS_HOME="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
export UDOS_MEMORY="$UDOS_HOME/uMEMORY"
export UDOS_SANDBOX="$UDOS_HOME/sandbox"
export UDOS_CORE="$UDOS_HOME/uCORE"
EOF

    log_success "Created environment file: $env_file"
}

# Run post-setup actions
run_post_setup() {
    log_info "Running post-setup actions..."

    # Initialize installation lifespan management
    log_info "📅 Setting up installation lifespan management..."
    if [ -x "$UDOS_ROOT/uCORE/core/installation-lifespan.sh" ]; then
        "$UDOS_ROOT/uCORE/core/installation-lifespan.sh" init
    fi

    # Initialize workflow system
    log_info "🗺️ Initializing workflow management..."
    if [ -x "$UDOS_ROOT/uCORE/core/workflow-manager.sh" ]; then
        "$UDOS_ROOT/uCORE/core/workflow-manager.sh" init
    fi

    # Create initial log entry
    if [ -x "$UDOS_ROOT/uCORE/core/utilities/log.sh" ]; then
        "$UDOS_ROOT/uCORE/core/utilities/log.sh" write INFO "User setup completed for $SETUP_USERNAME" setup
    fi

    # Setup first mission using GET form
    log_info "🎯 Setting up your first mission..."
    setup_first_mission

    # Create welcome mission
    local user_id=$(echo "$SETUP_USERNAME" | tr '[:upper:]' '[:lower:]' | sed 's/[^a-z0-9]//g')
    mkdir -p "$UDOS_ROOT/uMEMORY/user/missions"
    local mission_file="$UDOS_ROOT/uMEMORY/user/missions/welcome-$user_id.md"
    cat > "$mission_file" << EOF
# 🎯 Welcome to uDOS v1.0.4.1

**Mission**: Get started with uDOS
**User**: $SETUP_DISPLAY_NAME ($SETUP_USERNAME)
**Role**: $SETUP_ROLE
**Created**: $(date '+%Y-%m-%d %H:%M:%S')
**Location**: $SETUP_LOCATION

## Mission Objectives
Complete your uDOS setup and learn the essential commands.

## Getting Started Tasks
- [ ] **Test System**: Run \`ucode check all\` to validate installation
- [ ] **Explore Commands**: Try \`ucode help\` to see available commands
- [ ] **View Profile**: Run \`ucode get user name\` to test data retrieval
- [ ] **Create Log Entry**: Use \`ucode log write INFO "First login"\`
- [ ] **List Templates**: Run \`ucode template list\` to see available templates
- [ ] **Check Geographic Data**: Try \`ucode map stats\` to see geographic system

## Your Configuration
- **Role**: $SETUP_ROLE
- **Theme**: $SETUP_THEME color palette
- **Development Mode**: $SETUP_DEVELOPMENT_MODE
- **Location**: $SETUP_LOCATION ($SETUP_TIMEZONE)

## Resources
- **Documentation**: \`/docs/\` folder
- **Templates**: \`ucode template list\`
- **Help System**: \`ucode help <command>\`
- **System Status**: \`ucode check all\`

Welcome to the uDOS ecosystem! Your foundational development environment is ready.

---

*Mission generated by uDOS v1.0.4.1 setup system*
EOF

    log_success "Created welcome mission: $mission_file"

    # Display setup summary
    echo ""
    echo "╔══════════════════════════════════════════════════════════════════╗"
    echo "║                    🎉 Setup Complete!                           ║"
    echo "╚══════════════════════════════════════════════════════════════════╝"
    echo ""
    echo "User: $SETUP_DISPLAY_NAME ($SETUP_USERNAME)"
    echo "Role: $SETUP_ROLE"
    echo "Location: $SETUP_LOCATION ($SETUP_TIMEZONE)"
    echo "Theme: $SETUP_THEME"
    echo ""
    echo "Next steps:"
    echo "  1. Run: ucode help"
    echo "  2. Try: ucode get user name"
    echo "  3. View: ucode template list"
    echo ""
}

# Setup first mission interactively
setup_first_mission() {
    echo ""
    echo "╔══════════════════════════════════════════════════════════════════╗"
    echo "║                🎯 Create Your First Mission                     ║"
    echo "║  Every uDOS journey begins with a mission. Let's create yours!  ║"
    echo "╚══════════════════════════════════════════════════════════════════╝"
    echo ""

    # Collect mission details
    read -p "Mission title [Learn uDOS Fundamentals]: " mission_title
    mission_title=${mission_title:-"Learn uDOS Fundamentals"}

    echo ""
    echo "Mission types:"
    echo "  learning    - Skill development and education"
    echo "  development - Building and creating"
    echo "  research    - Investigation and analysis"
    echo "  enhancement - Improving existing systems"
    echo ""
    read -p "Mission type [learning]: " mission_type
    mission_type=${mission_type:-"learning"}

    read -p "Mission duration [1 week]: " mission_duration
    mission_duration=${mission_duration:-"1 week"}

    echo ""
    read -p "Primary objective: " mission_objective
    while [ -z "$mission_objective" ]; do
        read -p "Please enter your primary objective: " mission_objective
    done

    read -p "Save as legacy when completed? [y/N]: " save_legacy
    save_legacy=${save_legacy:-n}
    if [[ "$save_legacy" =~ ^[Yy] ]]; then
        save_as_legacy="true"
        echo ""
        echo "Legacy categories:"
        echo "  achievement - Personal accomplishment"
        echo "  knowledge   - Learning and understanding"
        echo "  innovation  - New techniques or approaches"
        echo ""
        read -p "Legacy category [achievement]: " legacy_category
        legacy_category=${legacy_category:-"achievement"}
    else
        save_as_legacy="false"
        legacy_category=""
    fi

    # Create mission using workflow system
    local mission_id=$(echo "$mission_title" | tr '[:upper:]' '[:lower:]' | sed 's/[^a-z0-9]/_/g' | sed 's/__*/_/g')

    # Create mission in workflow system
    mkdir -p "$UDOS_ROOT/sandbox/workflow/missions"
    cat > "$UDOS_ROOT/sandbox/workflow/missions/${mission_id}.json" << EOF
{
  "mission_id": "$mission_id",
  "title": "$mission_title",
  "type": "$mission_type",
  "priority": "medium",
  "complexity": "low",
  "status": "planning",
  "created": "$(date -u +%Y-%m-%dT%H:%M:%SZ)",
  "timeline": "$mission_duration",
  "start_date": "$(date +%Y-%m-%d)",
  "objective": "$mission_objective",
  "context": "First mission created during uDOS setup",
  "success_criteria": [
    "Complete uDOS system exploration",
    "Test core functionality",
    "Understand workflow system"
  ],
  "team_size": 1,
  "tracking_enabled": true,
  "milestone_frequency": "weekly",
  "save_as_legacy": $save_as_legacy,
  "legacy_category": "$legacy_category",
  "progress_percentage": 0,
  "required_milestones": [],
  "completed_milestones": [],
  "assist_recommendations": [],
  "legacy_impact": "$legacy_category"
}
EOF

    # Create mission brief document
    mkdir -p "$UDOS_ROOT/uMEMORY/missions"
    local mission_file="$UDOS_ROOT/uMEMORY/missions/$(date +%Y%m%d)-${mission_id}-mission.md"
    cat > "$mission_file" << EOF
# Mission: $mission_title

**Template Version:** v1.0.4.1
**Generated:** $(date -u +%Y-%m-%dT%H:%M:%SZ)
**Instance:** First Mission Setup
**Priority:** medium
**Status:** planning
**Legacy Save:** $save_as_legacy

> **Mission Type:** $mission_type
> **Complexity:** low
> **Estimated Duration:** $mission_duration
> **Start Date:** $(date +%Y-%m-%d)

---

## 📋 Mission Overview

### 🎯 Primary Objective
$mission_objective

### 🔍 Mission Context
First mission created during uDOS setup process. This mission will help you learn the core functionality and workflow system of uDOS.

## 🎯 Success Criteria & KPIs

### ✅ Success Criteria
- [ ] Complete uDOS system exploration
- [ ] Test core functionality
- [ ] Understand workflow system

## 📊 Progress Tracking

### Mission Phase Status
- [x] 🚀 Mission initiated
- [ ] 📋 Requirements gathered
- [ ] 👥 Team assembled
- [ ] 🛠️ Resources allocated
- [ ] ⚡ Execution begun
- [ ] 🎯 Milestones achieved
- [ ] 🔍 Quality assurance
- [ ] ✅ Mission completed
- [ ] 📝 Post-mission review

## 🏆 Mission Completion & Legacy

### ✅ Mission Completion Status
*To be updated when mission is completed*

$(if [[ "$save_as_legacy" == "true" ]]; then
cat << LEGACY

### 📚 Legacy Preservation
This mission will be saved as legacy content for future reference.

- **Legacy Category:** $legacy_category
- **Legacy Value:** *To be documented on completion*
- **Future Applications:** *To be identified during mission*
- **Archive Location:** uMEMORY/legacy/missions/${mission_id}/
LEGACY
fi)

---

## 🔗 Mission Integration

**uDOS Context Integration:**
- **Mission ID:** $mission_id
- **uCode Integration:** ✅ Enabled
- **Dashboard Tracking:** ✅ Active
- **Memory System:** ✅ Connected

---

**Generated:** $(date)
**Template Version:** v1.0.4.1
**uDOS Version:** v1.0.4.1
**Last Updated:** $(date)
EOF

    # Create initial milestone
    mkdir -p "$UDOS_ROOT/sandbox/workflow/milestones"
    cat > "$UDOS_ROOT/sandbox/workflow/milestones/${mission_id}-kickoff.json" << EOF
{
  "milestone_id": "${mission_id}-kickoff",
  "title": "Mission Kickoff: $mission_title",
  "description": "Initial mission setup and planning phase completed",
  "achieved": "$(date -u +%Y-%m-%dT%H:%M:%SZ)",
  "mission_id": "$mission_id",
  "significance": "foundational",
  "next_suggested_milestone": "System Exploration Complete",
  "contributes_to_mission": "$mission_id"
}
EOF

    log_success "✅ First mission created: $mission_title"
    log_info "📁 Mission files:"
    echo "   - Brief: $mission_file"
    echo "   - Workflow: sandbox/workflow/missions/${mission_id}.json"
    echo ""
    log_info "💡 Use 'ucode workflow status' to check your mission progress"

    # Advance lifespan to active phase
    if [ -x "$UDOS_ROOT/uCORE/core/installation-lifespan.sh" ]; then
        "$UDOS_ROOT/uCORE/core/installation-lifespan.sh" advance active
    fi
}

# Main execution
main() {
    if check_user_setup; then
        log_info "User setup already complete"
        return 0
    fi

    log_info "User setup required"
    run_user_setup
}

# Run if executed directly
if [ "${BASH_SOURCE[0]}" = "${0}" ]; then
    main "$@"
fi
