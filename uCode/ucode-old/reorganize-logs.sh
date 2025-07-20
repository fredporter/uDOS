#!/bin/bash
# uDOS Log Reorganization Script
# Moves system logs and config from uMemory to uDev
# Keeps user data separate in uMemory

set -euo pipefail

UHOME="${UHOME:-$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)}"
UCODE="$UHOME/uCode"
UMEM="$UHOME/uMemory"
UDEV="$UHOME/uDev"

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

echo "🔄 uDOS Log System Reorganization"
echo "════════════════════════════════════"

# Update path references in scripts
update_script_paths() {
    echo "📝 Updating script path references..."
    
    # Update core.sh paths
    if [[ -f "$UCODE/core.sh" ]]; then
        echo "  • Updating core.sh..."
        sed -i '' 's|\$UMEM/logs/system|\$UDEV/logs/system|g' "$UCODE/core.sh"
        sed -i '' 's|\$UMEM/config|\$UDEV/config|g' "$UCODE/core.sh"
        sed -i '' 's|\$UMEM/state|\$UDEV/state|g' "$UCODE/core.sh"
    fi
    
    # Update setup scripts
    if [[ -f "$UCODE/setup-template-processor.sh" ]]; then
        echo "  • Updating setup-template-processor.sh..."
        sed -i '' 's|logs/system|logs/system|g' "$UCODE/setup-template-processor.sh"
        sed -i '' 's|\$UMEM/config|\$UDEV/config|g' "$UCODE/setup-template-processor.sh"
    fi
    
    # Update dash-enhanced.sh
    if [[ -f "$UCODE/dash-enhanced.sh" ]]; then
        echo "  • Updating dash-enhanced.sh..."
        sed -i '' 's|\$UMEM/state|\$UDEV/state|g' "$UCODE/dash-enhanced.sh"
    fi
    
    # Update template.sh
    if [[ -f "$UCODE/template.sh" ]]; then
        echo "  • Updating template.sh..."
        sed -i '' 's|\$UMEM/config|\$UDEV/config|g' "$UCODE/template.sh"
    fi
    
    # Update setup.sh
    if [[ -f "$UCODE/setup.sh" ]]; then
        echo "  • Updating setup.sh..."
        sed -i '' 's|\$UMEM/config|\$UDEV/config|g' "$UCODE/setup.sh"
    fi
}

# Create new directory structure in uDev
create_udev_structure() {
    echo "📁 Creating uDev directory structure..."
    
    mkdir -p "$UDEV"/{logs/{system,errors,sessions,devices},config,state}
    
    echo "  ✅ Created: $UDEV/logs/system"
    echo "  ✅ Created: $UDEV/logs/errors"  
    echo "  ✅ Created: $UDEV/logs/sessions"
    echo "  ✅ Created: $UDEV/logs/devices"
    echo "  ✅ Created: $UDEV/config"
    echo "  ✅ Created: $UDEV/state"
}

# Create logging configuration
create_log_config() {
    echo "⚙️ Creating logging configuration..."
    
    cat > "$UDEV/config/logging.conf" << 'EOF'
# uDOS Logging Configuration
# System logs, errors, sessions, and device logs in uDev
# User logs (moves, missions, milestones, legacy) remain in uMemory

[system_logs]
location = $UDEV/logs/system
retention = 30d
max_size = 10M

[error_logs] 
location = $UDEV/logs/errors
retention = 90d
max_size = 50M

[session_logs]
location = $UDEV/logs/sessions
retention = 7d
max_size = 5M

[device_logs]
location = $UDEV/logs/devices  
retention = 14d
max_size = 5M

[user_logs]
# User data remains in uMemory
location = $UMEM/logs
retention = 365d
categories = moves,missions,milestones,legacy
EOF

    echo "  ✅ Created logging configuration"
}

# Create helper functions for logging
create_log_helpers() {
    echo "🛠️ Creating logging helper functions..."
    
    cat > "$UCODE/log-utils.sh" << 'EOF'
#!/bin/bash
# uDOS Logging Utilities
# Provides consistent logging functions for system vs user logs

# System logging (goes to uDev)
log_system() {
    local level="$1"
    local message="$2"
    local log_file="$UDEV/logs/system/$(date +%Y%m%d).log"
    
    mkdir -p "$(dirname "$log_file")"
    echo "[$(date '+%Y-%m-%d %H:%M:%S')] [$level] $message" >> "$log_file"
}

log_error() {
    local message="$1"
    local log_file="$UDEV/logs/errors/$(date +%Y%m%d).log"
    
    mkdir -p "$(dirname "$log_file")"
    echo "[$(date '+%Y-%m-%d %H:%M:%S')] [ERROR] $message" >> "$log_file"
    echo -e "\033[0;31m❌ ERROR: $message\033[0m" >&2
}

log_session() {
    local session_id="$1"
    local event="$2"
    local log_file="$UDEV/logs/sessions/${session_id}.log"
    
    mkdir -p "$(dirname "$log_file")"
    echo "[$(date '+%Y-%m-%d %H:%M:%S')] $event" >> "$log_file"
}

log_device() {
    local device="$1"
    local event="$2"
    local log_file="$UDEV/logs/devices/$(date +%Y%m%d)-${device}.log"
    
    mkdir -p "$(dirname "$log_file")"
    echo "[$(date '+%Y-%m-%d %H:%M:%S')] $event" >> "$log_file"
}

# User logging (stays in uMemory)  
log_move() {
    local message="$1"
    local log_file="$UMEM/logs/moves/$(date +%Y%m%d).md"
    
    mkdir -p "$(dirname "$log_file")"
    echo "- $(date '+%H:%M:%S'): $message" >> "$log_file"
}

log_mission() {
    local mission_id="$1"
    local event="$2"
    local log_file="$UMEM/logs/missions/${mission_id}.log"
    
    mkdir -p "$(dirname "$log_file")"
    echo "[$(date '+%Y-%m-%d %H:%M:%S')] $event" >> "$log_file"
}

log_milestone() {
    local milestone="$1"
    local description="$2"
    local log_file="$UMEM/logs/milestones/$(date +%Y%m).md"
    
    mkdir -p "$(dirname "$log_file")"
    echo "## $(date '+%Y-%m-%d') - $milestone" >> "$log_file"
    echo "$description" >> "$log_file"
    echo "" >> "$log_file"
}
EOF

    chmod +x "$UCODE/log-utils.sh"
    echo "  ✅ Created logging utilities"
}

# Update uMemory structure documentation
update_memory_structure() {
    echo "📚 Updating uMemory structure documentation..."
    
    cat > "$UMEM/README.md" << 'EOF'
# uMemory - User Data Storage

This directory contains **user-specific data only**:

## 📁 Directory Structure

```
uMemory/
├── logs/                      # User activity logs only
│   ├── moves/                 # User movement logs  
│   ├── missions/              # Mission progress logs
│   ├── milestones/            # Achievement logs
│   └── legacy/                # Historical user data
├── sandbox/                   # User workspace/scratch area
├── users/                     # User profiles and data
├── missions/                  # Active user missions
├── milestones/                # User achievements
└── forms/                     # Completed user forms
```

## 🚫 What's NOT Here

System logs, configuration, and development data have been moved to `uDev/`:
- System logs → `uDev/logs/system/`
- Error logs → `uDev/logs/errors/`
- Session logs → `uDev/logs/sessions/`
- Device logs → `uDev/logs/devices/`
- System config → `uDev/config/`

This separation keeps user data isolated from system operations.
EOF

    echo "  ✅ Updated uMemory documentation"
}

# Main execution
main() {
    echo "Starting log system reorganization..."
    
    create_udev_structure
    update_script_paths
    create_log_config
    create_log_helpers
    update_memory_structure
    
    echo ""
    echo "✅ Log system reorganization complete!"
    echo ""
    echo "📊 Summary:"
    echo "  • User logs remain in uMemory/logs/"
    echo "  • System logs moved to uDev/logs/"  
    echo "  • Configuration moved to uDev/config/"
    echo "  • Added logging utilities in uCode/log-utils.sh"
    echo ""
    echo "💡 Use: source uCode/log-utils.sh to access logging functions"
}

# Run if executed directly
if [[ "${BASH_SOURCE[0]}" == "${0}" ]]; then
    main "$@"
fi
