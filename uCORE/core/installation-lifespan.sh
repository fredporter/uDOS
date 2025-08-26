#!/bin/bash
# uCORE Installation Lifespan Management System
# Manages installation lifecycle and EOL planning

# Remove strict mode temporarily for initialization
set -euo pipefail

# Get script directory and uDOS root
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
UDOS_ROOT="$(cd "$SCRIPT_DIR/../.." && pwd)"

# Source logging
source "$SCRIPT_DIR/logging.sh" 2>/dev/null || {
    log_info() { echo -e "\033[0;36m[INFO]\033[0m $1"; }
    log_success() { echo -e "\033[0;32m[SUCCESS]\033[0m $1"; }
    log_warning() { echo -e "\033[0;33m[WARNING]\033[0m $1"; }
    log_error() { echo -e "\033[0;31m[ERROR]\033[0m $1"; }
}

# Configuration
INSTALLATION_FILE="$UDOS_ROOT/uMEMORY/installation.md"
LIFESPAN_CONFIG="$UDOS_ROOT/uMEMORY/system/installation-lifespan.json"
WORKFLOW_DIR="$UDOS_ROOT/sandbox/workflow"

# Lifespan phases (bash 3 compatible)
setup_phase_desc="Initial installation and configuration"
active_phase_desc="Primary usage and development phase"
maintenance_phase_desc="Ongoing maintenance and optimization"
legacy_prep_phase_desc="Preparation for legacy transition"
archival_phase_desc="Final archival and preservation"
eol_phase_desc="End of life - installation complete"

# Initialize lifespan management
init_lifespan() {
    log_info "🕐 Initializing installation lifespan management"

    # Create lifespan configuration
    cat > "$LIFESPAN_CONFIG" << EOF
{
    "installation_id": "$(get_installation_id)",
    "created": "$(date -u +%Y-%m-%dT%H:%M:%SZ)",
    "version": "v1.0.4.1",
    "lifespan": {
        "duration_months": $(get_lifespan_duration),
        "phase": "setup",
        "start_date": "$(date -u +%Y-%m-%dT%H:%M:%SZ)",
        "estimated_completion": "$(calculate_completion_date)",
        "eol_warning_months": 2,
        "legacy_preparation_months": 3
    },
    "phases": {
        "setup": {
            "start": "$(date -u +%Y-%m-%dT%H:%M:%SZ)",
            "completed": false,
            "duration_estimate": "1-2 weeks"
        },
        "active": {
            "start": null,
            "completed": false,
            "duration_estimate": "$(( $(get_lifespan_duration) - 4 )) months"
        },
        "maintenance": {
            "start": null,
            "completed": false,
            "duration_estimate": "2-3 months"
        },
        "legacy_prep": {
            "start": null,
            "completed": false,
            "duration_estimate": "1 month"
        },
        "archival": {
            "start": null,
            "completed": false,
            "duration_estimate": "1-2 weeks"
        },
        "eol": {
            "start": null,
            "completed": false,
            "duration_estimate": "final"
        }
    },
    "tracking": {
        "total_moves": 0,
        "total_milestones": 0,
        "total_missions": 0,
        "legacy_items": 0,
        "last_activity": "$(date -u +%Y-%m-%dT%H:%M:%SZ)"
    }
}
EOF

    log_success "✅ Lifespan management initialized"
}

# Get installation ID
get_installation_id() {
    if [[ -f "$INSTALLATION_FILE" ]]; then
        grep "^**Installation ID**:" "$INSTALLATION_FILE" | cut -d: -f2 | sed 's/^[[:space:]]*//' || echo "unknown"
    else
        echo "$(date +uDOS-%Y%m%d)-$(openssl rand -hex 4)"
    fi
}

# Get lifespan duration from user input or default
get_lifespan_duration() {
    local duration="${SETUP_LIFESPAN_MONTHS:-}"
    if [[ -n "$duration" && "$duration" =~ ^[0-9]+$ ]]; then
        echo "$duration"
    elif [[ -f "$LIFESPAN_CONFIG" ]]; then
        local existing_duration=$(jq -r '.lifespan.duration_months' "$LIFESPAN_CONFIG" 2>/dev/null)
        if [[ "$existing_duration" != "null" && "$existing_duration" =~ ^[0-9]+$ ]]; then
            echo "$existing_duration"
        else
            echo "12"
        fi
    else
        echo "12"  # Default 12 months
    fi
}

# Calculate completion date
calculate_completion_date() {
    local months=$(get_lifespan_duration)
    # Use macOS date with -v flag
    if date -v+1m >/dev/null 2>&1; then
        # macOS native date
        date -v+${months}m +%Y-%m-%d
    elif command -v gdate >/dev/null 2>&1; then
        # GNU date (if installed via homebrew)
        gdate -d "+${months} months" +%Y-%m-%d
    else
        # Fallback: approximate calculation
        local current_date=$(date +%Y-%m-%d)
        echo "$current_date (+ $months months)"
    fi
}

# Check lifespan status
check_lifespan_status() {
    if [[ ! -f "$LIFESPAN_CONFIG" ]]; then
        log_warning "⚠️  Lifespan configuration not found"
        return 1
    fi

    local config=$(cat "$LIFESPAN_CONFIG")
    local current_phase=$(echo "$config" | jq -r '.lifespan.phase')
    local start_date=$(echo "$config" | jq -r '.lifespan.start_date')
    local estimated_completion=$(echo "$config" | jq -r '.lifespan.estimated_completion')
    local duration_months=$(echo "$config" | jq -r '.lifespan.duration_months')

    log_info "📊 Installation Lifespan Status"
    echo "   Phase: $current_phase"
    echo "   Started: $start_date"
    echo "   Duration: $duration_months months"
    echo "   Est. Completion: $estimated_completion"

    # Check if approaching EOL
    check_eol_proximity "$estimated_completion"
}

# Check if approaching end of life
check_eol_proximity() {
    local completion_date="$1"
    local current_date=$(date +%Y-%m-%d)

    # Calculate days until completion (simplified)
    if [[ "$completion_date" < "$current_date" ]]; then
        log_warning "⚠️  Installation has exceeded planned lifespan!"
        log_info "💡 Consider running legacy preparation process"
    else
        log_info "✅ Installation within planned lifespan"
    fi
}

# Advance to next phase
advance_phase() {
    local target_phase="$1"

    if [[ ! -f "$LIFESPAN_CONFIG" ]]; then
        log_error "❌ Lifespan configuration not found"
        return 1
    fi

    local temp_file=$(mktemp)
    jq --arg phase "$target_phase" --arg timestamp "$(date -u +%Y-%m-%dT%H:%M:%SZ)" \
        '.lifespan.phase = $phase | .phases[$phase].start = $timestamp' \
        "$LIFESPAN_CONFIG" > "$temp_file" && mv "$temp_file" "$LIFESPAN_CONFIG"

    log_success "✅ Advanced to phase: $target_phase"

    # Log milestone for significant phase changes
    case "$target_phase" in
        "active")
            log_milestone "operational_ready" "Installation reached operational status"
            ;;
        "maintenance")
            log_milestone "maintenance_phase" "Installation entered maintenance phase"
            ;;
        "legacy_prep")
            log_milestone "legacy_preparation" "Installation preparing for legacy transition"
            ;;
        "archival")
            log_milestone "archived" "Installation moved to archival status"
            ;;
        "eol")
            log_milestone "end_of_life" "Installation reached end of life"
            ;;
    esac
}

# Log milestone in workflow system
log_milestone() {
    local milestone_type="$1"
    local description="$2"

    if [[ -d "$WORKFLOW_DIR" && -f "$UDOS_ROOT/uCORE/core/workflow-manager.sh" ]]; then
        "$UDOS_ROOT/uCORE/core/workflow-manager.sh" milestone "$milestone_type" "$description"
    fi
}

# Update activity tracking
update_activity() {
    local activity_type="$1"  # moves, milestones, missions, legacy
    local increment="${2:-1}"

    if [[ ! -f "$LIFESPAN_CONFIG" ]]; then
        return 1
    fi

    local temp_file=$(mktemp)
    jq --arg type "$activity_type" --arg inc "$increment" --arg timestamp "$(date -u +%Y-%m-%dT%H:%M:%SZ)" \
        '.tracking.["total_" + $type] += ($inc | tonumber) | .tracking.last_activity = $timestamp' \
        "$LIFESPAN_CONFIG" > "$temp_file" && mv "$temp_file" "$LIFESPAN_CONFIG"
}

# Generate EOL script
generate_eol_script() {
    local eol_script="$UDOS_ROOT/uCORE/core/installation-eol.sh"

    cat > "$eol_script" << 'EOF'
#!/bin/bash
# Installation End of Life (EOL) Script
# Automatically generated by lifespan management

set -euo pipefail

UDOS_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"

log_info() { echo -e "\033[0;36m[INFO]\033[0m $1"; }
log_success() { echo -e "\033[0;32m[SUCCESS]\033[0m $1"; }
log_warning() { echo -e "\033[0;33m[WARNING]\033[0m $1"; }

log_info "🏁 Starting installation End of Life process"

# Archive active work to legacy
log_info "📚 Archiving active work to legacy..."
mkdir -p "$UDOS_ROOT/uMEMORY/legacy/$(date +%Y%m%d)"
if [[ -d "$UDOS_ROOT/sandbox" ]]; then
    cp -r "$UDOS_ROOT/sandbox" "$UDOS_ROOT/uMEMORY/legacy/$(date +%Y%m%d)/sandbox-final"
fi

# Create installation summary
log_info "📊 Creating installation summary..."
cat > "$UDOS_ROOT/uMEMORY/legacy/$(date +%Y%m%d)/installation-summary.md" << SUMMARY
# Installation Summary - $(date +%Y-%m-%d)

This installation has reached its planned end of life.

## Installation Details
- **ID**: $(grep "Installation ID" "$UDOS_ROOT/uMEMORY/installation.md" | cut -d: -f2)
- **Duration**: $(( ($(date +%s) - $(stat -f %B "$UDOS_ROOT/uMEMORY/installation.md" 2>/dev/null || echo 0)) / 86400 )) days
- **Version**: v1.0.4.1

## Legacy Preserved
- Sandbox final state
- User configurations
- Workflow data
- Mission and milestone records

*Generated by uDOS v1.0.4.1 EOL process*
SUMMARY

log_success "✅ EOL process completed"
log_info "💡 Legacy data preserved in: uMEMORY/legacy/$(date +%Y%m%d)/"
EOF

    chmod +x "$eol_script"
    log_success "✅ EOL script generated: $eol_script"
}

# Main function
main() {
    case "${1:-status}" in
        "init")
            init_lifespan
            generate_eol_script
            ;;
        "status")
            check_lifespan_status
            ;;
        "advance")
            advance_phase "$2"
            ;;
        "activity")
            update_activity "$2" "${3:-1}"
            ;;
        "eol")
            "$UDOS_ROOT/uCORE/core/installation-eol.sh"
            ;;
        *)
            echo "Usage: $0 {init|status|advance|activity|eol}"
            echo "  init                     - Initialize lifespan management"
            echo "  status                   - Check current lifespan status"
            echo "  advance <phase>          - Advance to next phase"
            echo "  activity <type> [count]  - Update activity tracking"
            echo "  eol                      - Run end of life process"
            ;;
    esac
}

main "$@"
