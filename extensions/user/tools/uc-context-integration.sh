#!/bin/bash
# UC Context Integration - Connect User Companions to Mission System
# Provides dynamic context to Chester and Sorcerer's Assistant

UHOME="${HOME}/uDOS"
UMEM="${UHOME}/uMemory"
UC_DIR="${UHOME}/uCompanion"
CONTEXT_DIR="${UC_DIR}/context"

mkdir -p "$CONTEXT_DIR"

# Generate current mission context for AI assistants
generate_mission_context() {
    local context_file="${CONTEXT_DIR}/current-missions.txt"
    
    echo "=== uDOS Current Mission Context ===" > "$context_file"
    echo "Generated: $(date)" >> "$context_file"
    echo "" >> "$context_file"
    
    # Add active missions
    if [[ -d "${UMEM}/missions" ]] && [[ -n "$(ls -A "${UMEM}/missions" 2>/dev/null)" ]]; then
        echo "🎯 ACTIVE MISSIONS:" >> "$context_file"
        echo "" >> "$context_file"
        
        for mission_file in "${UMEM}/missions"/*.md; do
            if [[ -f "$mission_file" ]]; then
                local mission_id=$(basename "$mission_file" .md)
                local mission_name=$(grep "^# 🎯 Mission:" "$mission_file" | sed 's/^# 🎯 Mission: //')
                local status=$(grep "**Status**:" "$mission_file" | head -1 | sed 's/.*Status\*\*: //' | tr -d '\n\r')
                local created_date=$(grep "**Created**:" "$mission_file" | sed 's/.*Created\*\*: //' | awk '{print $1}')
                
                echo "Mission: $mission_name" >> "$context_file"
                echo "ID: $mission_id" >> "$context_file"
                echo "Status: $status" >> "$context_file"
                echo "Created: $created_date" >> "$context_file"
                
                # Add milestones
                local milestone_count=0
                if [[ -d "${UMEM}/milestones" ]]; then
                    for milestone_file in "${UMEM}/milestones"/${mission_id}-*.md; do
                        if [[ -f "$milestone_file" ]]; then
                            milestone_count=$((milestone_count + 1))
                            local milestone_name=$(grep "^# ⭐ Milestone:" "$milestone_file" | sed 's/^# ⭐ Milestone: //')
                            echo "  → Milestone: $milestone_name" >> "$context_file"
                        fi
                    done
                fi
                echo "Total Milestones: $milestone_count" >> "$context_file"
                echo "" >> "$context_file"
            fi
        done
    else
        echo "No active missions found." >> "$context_file"
    fi
    
    # Add system status
    echo "" >> "$context_file"
    echo "🔧 SYSTEM STATUS:" >> "$context_file"
    echo "uDOS Version: v1.1.0" >> "$context_file"
    echo "Mission System: ✅ Active" >> "$context_file"
    echo "Analytics Dashboard: ✅ Running" >> "$context_file"
    echo "Mapping System: ✅ Integrated" >> "$context_file"
    echo "User Companions: ✅ Available" >> "$context_file"
    
    echo "✅ Mission context generated: $context_file"
}

# Update Gemini configurations with current context
update_assistant_context() {
    generate_mission_context
    
    local mission_context="${CONTEXT_DIR}/current-missions.txt"
    
    # Update Chester's configuration
    local chester_config="${UC_DIR}/gemini/configs/chester.json"
    if [[ -f "$chester_config" ]]; then
        # Add context file to Chester's context_files array
        jq --arg context_file "$mission_context" '.context_files += [$context_file]' "$chester_config" > "${chester_config}.tmp" && mv "${chester_config}.tmp" "$chester_config"
        echo "✅ Chester context updated"
    fi
    
    # Update Sorcerer's Assistant configuration
    local sorcerer_config="${UC_DIR}/gemini/configs/sorcerer.json"
    if [[ -f "$sorcerer_config" ]]; then
        # Add context file to Sorcerer's context_files array
        jq --arg context_file "$mission_context" '.context_files += [$context_file]' "$sorcerer_config" > "${sorcerer_config}.tmp" && mv "${sorcerer_config}.tmp" "$sorcerer_config"
        echo "✅ Sorcerer's Assistant context updated"
    fi
}

# Auto-update context when missions change
setup_auto_context() {
    # Create a simple watcher script
    cat > "${CONTEXT_DIR}/auto-update.sh" << 'EOF'
#!/bin/bash
# Auto-update UC context when missions change

UC_CONTEXT_DIR="${HOME}/uDOS/uCompanion/context"
MISSIONS_DIR="${HOME}/uDOS/uMemory/missions"
MILESTONES_DIR="${HOME}/uDOS/uMemory/milestones"

# Check if mission files have been modified in the last 5 minutes
recent_changes() {
    if [[ -d "$MISSIONS_DIR" ]]; then
        find "$MISSIONS_DIR" -name "*.md" -mmin -5 -type f | head -1
    fi
    if [[ -d "$MILESTONES_DIR" ]]; then
        find "$MILESTONES_DIR" -name "*.md" -mmin -5 -type f | head -1
    fi
}

# Update context if changes detected
if [[ -n "$(recent_changes)" ]]; then
    "${UC_CONTEXT_DIR}/../context/uc-context-integration.sh" update
fi
EOF
    
    chmod +x "${CONTEXT_DIR}/auto-update.sh"
    echo "✅ Auto-context updater created"
}

# Main execution
case "${1:-update}" in
    "generate")
        generate_mission_context
        ;;
    "update")
        update_assistant_context
        ;;
    "auto")
        setup_auto_context
        ;;
    "all")
        update_assistant_context
        setup_auto_context
        ;;
    *)
        echo "Usage: $0 [generate|update|auto|all]"
        echo "  generate - Generate mission context only"
        echo "  update   - Update assistant configurations with current context"
        echo "  auto     - Setup automatic context updates"
        echo "  all      - Update context and setup auto-updates"
        ;;
esac
