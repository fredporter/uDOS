#!/bin/bash
# uDOS Command System Migration v1.3.3
# Consolidates multiple command files into unified system

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
SYSTEM_DIR="$SCRIPT_DIR"
BACKUP_DIR="$SYSTEM_DIR/temp/migration-backup-$(date +%Y%m%d-%H%M%S)"

# Color output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

log() {
    echo -e "${BLUE}[$(date +'%H:%M:%S')]${NC} $1"
}

success() {
    echo -e "${GREEN}✅ $1${NC}"
}

warn() {
    echo -e "${YELLOW}⚠️ $1${NC}"
}

error() {
    echo -e "${RED}❌ $1${NC}"
}

# Create backup directory
mkdir -p "$BACKUP_DIR"

log "Starting uDOS Command System Migration v1.3.3"
log "Backup directory: $BACKUP_DIR"

# Backup existing files
backup_files() {
    log "Backing up existing command files..."

    local files=(
        "commands.json"
        "shortcodes.json"
        "dynamic-commands.json"
        "ucode-commands.json"
        "vb-commands.json"
    )

    for file in "${files[@]}"; do
        if [[ -f "$SYSTEM_DIR/$file" ]]; then
            cp "$SYSTEM_DIR/$file" "$BACKUP_DIR/"
            success "Backed up $file"
        else
            warn "File not found: $file"
        fi
    done
}

# Analyze current command overlap
analyze_overlap() {
    log "Analyzing command overlap and conflicts..."

    # Extract command names from each file
    local temp_dir="$SYSTEM_DIR/temp"
    mkdir -p "$temp_dir"

    # Commands.json - simple list
    if [[ -f "$SYSTEM_DIR/commands.json" ]]; then
        jq -r '.commands[].command' "$SYSTEM_DIR/commands.json" 2>/dev/null > "$temp_dir/commands-list.txt" || true
    fi

    # Shortcodes.json
    if [[ -f "$SYSTEM_DIR/shortcodes.json" ]]; then
        jq -r '.shortcodes[].command' "$SYSTEM_DIR/shortcodes.json" 2>/dev/null > "$temp_dir/shortcodes-list.txt" || true
    fi

    # Dynamic commands
    if [[ -f "$SYSTEM_DIR/dynamic-commands.json" ]]; then
        jq -r '.commands[].command' "$SYSTEM_DIR/dynamic-commands.json" 2>/dev/null > "$temp_dir/dynamic-list.txt" || true
    fi

    # uCode commands
    if [[ -f "$SYSTEM_DIR/ucode-commands.json" ]]; then
        jq -r '.[].command' "$SYSTEM_DIR/ucode-commands.json" 2>/dev/null > "$temp_dir/ucode-list.txt" || true
    fi

    # Find overlaps
    log "Command counts by file:"
    for list_file in "$temp_dir"/*-list.txt; do
        if [[ -f "$list_file" ]]; then
            local count=$(wc -l < "$list_file" 2>/dev/null || echo "0")
            local basename=$(basename "$list_file" -list.txt)
            echo "  $basename: $count commands"
        fi
    done

    # Find common commands
    log "Finding command overlaps..."
    if [[ -f "$temp_dir/commands-list.txt" && -f "$temp_dir/shortcodes-list.txt" ]]; then
        local overlaps=$(comm -12 <(sort "$temp_dir/commands-list.txt") <(sort "$temp_dir/shortcodes-list.txt") | wc -l)
        echo "  commands.json ↔ shortcodes.json: $overlaps overlapping commands"
    fi
}

# Create consolidated command dataset
create_unified_dataset() {
    log "Creating unified command dataset..."

    local unified_file="$SYSTEM_DIR/unified-command-system-complete.json"

    # Start building the unified structure
    cat > "$unified_file" << 'EOF'
{
    "metadata": {
        "version": "1.3.3",
        "description": "Unified uDOS Command System - Complete Dataset",
        "created": "2025-08-23",
        "migration_source": "Consolidated from 5 separate command files",
        "total_commands": 0,
        "data_sources": [
            "commands.json",
            "shortcodes.json",
            "dynamic-commands.json",
            "ucode-commands.json",
            "vb-commands.json"
        ]
    },
    "command_categories": [
        {
            "category": "system",
            "description": "Core system operations",
            "icon": "⚙️",
            "color": "#2196F3",
            "role_access": ["DRONE", "KNIGHT", "IMP", "SORCERER", "WIZARD"]
        },
        {
            "category": "ugrid",
            "description": "uGRID display and widget management",
            "icon": "🎮",
            "color": "#4CAF50",
            "role_access": ["IMP", "SORCERER", "WIZARD"]
        },
        {
            "category": "data",
            "description": "Data processing and manipulation",
            "icon": "📊",
            "color": "#FF9800",
            "role_access": ["DRONE", "KNIGHT", "IMP", "SORCERER", "WIZARD"]
        },
        {
            "category": "workflow",
            "description": "Workflow and automation",
            "icon": "🔄",
            "color": "#9C27B0",
            "role_access": ["KNIGHT", "IMP", "SORCERER", "WIZARD"]
        },
        {
            "category": "git",
            "description": "Version control operations",
            "icon": "🔀",
            "color": "#F44336",
            "role_access": ["SORCERER", "WIZARD"]
        },
        {
            "category": "programming",
            "description": "Programming language commands",
            "icon": "💻",
            "color": "#607D8B",
            "role_access": ["IMP", "SORCERER", "WIZARD"]
        }
    ],
    "unified_commands": []
}
EOF

    # Process each source file and merge commands
    merge_commands_json "$unified_file"
    merge_shortcodes_json "$unified_file"
    merge_dynamic_commands_json "$unified_file"
    merge_ucode_commands_json "$unified_file"
    merge_vb_commands_json "$unified_file"

    # Update total command count
    local total_commands=$(jq '.unified_commands | length' "$unified_file")
    jq --arg count "$total_commands" '.metadata.total_commands = ($count | tonumber)' "$unified_file" > "$unified_file.tmp" && mv "$unified_file.tmp" "$unified_file"

    success "Created unified dataset with $total_commands commands: $unified_file"
}

# Merge commands.json
merge_commands_json() {
    local unified_file="$1"
    local source_file="$SYSTEM_DIR/commands.json"

    if [[ ! -f "$source_file" ]]; then
        warn "Source file not found: $source_file"
        return
    fi

    log "Merging commands.json..."

    # Convert commands.json format to unified format
    jq --slurpfile existing "$unified_file" '
    .commands[] as $cmd |
    {
        "command": $cmd.command,
        "languages": ["System"],
        "category": "system",
        "priority": 3,
        "role_access": ["DRONE", "KNIGHT", "IMP", "SORCERER", "WIZARD"],
        "syntax": {
            "system": ($cmd.command + " " + ($cmd.args | join(" | ")))
        },
        "description": ("Core " + ($cmd.command | ascii_downcase) + " command"),
        "source": "commands.json",
        "parameters": ($cmd.args | map({"name": ., "type": "string", "required": false}))
    } as $unified_cmd |
    $existing[0].unified_commands += [$unified_cmd] |
    $existing[0]
    ' "$source_file" > "$unified_file.tmp" && mv "$unified_file.tmp" "$unified_file"

    success "Merged commands.json"
}

# Merge shortcodes.json
merge_shortcodes_json() {
    local unified_file="$1"
    local source_file="$SYSTEM_DIR/shortcodes.json"

    if [[ ! -f "$source_file" ]]; then
        warn "Source file not found: $source_file"
        return
    fi

    log "Merging shortcodes.json..."

    # Convert shortcodes format
    jq --slurpfile existing "$unified_file" '
    .shortcodes[] as $sc |
    {
        "command": $sc.command,
        "languages": ["Shortcode"],
        "category": $sc.category,
        "priority": 5,
        "role_access": ["DRONE", "KNIGHT", "IMP", "SORCERER", "WIZARD"],
        "syntax": {
            "shortcode": ("[" + $sc.command + "|" + ($sc.args[0] // "ACTION") + "]")
        },
        "description": $sc.description,
        "examples": {
            "basic": $sc.examples
        },
        "help_text": $sc.help,
        "source": "shortcodes.json",
        "operations": ($sc.args | map({"name": ., "description": ("Execute " + . + " operation")}))
    } as $unified_cmd |
    $existing[0].unified_commands += [$unified_cmd] |
    $existing[0]
    ' "$source_file" > "$unified_file.tmp" && mv "$unified_file.tmp" "$unified_file"

    success "Merged shortcodes.json"
}

# Merge dynamic-commands.json
merge_dynamic_commands_json() {
    local unified_file="$1"
    local source_file="$SYSTEM_DIR/dynamic-commands.json"

    if [[ ! -f "$source_file" ]]; then
        warn "Source file not found: $source_file"
        return
    fi

    log "Merging dynamic-commands.json..."

    jq --slurpfile existing "$unified_file" '
    .commands[] as $dc |
    {
        "command": $dc.command,
        "languages": ["System", "Dynamic"],
        "category": $dc.category,
        "priority": 4,
        "role_access": ["KNIGHT", "IMP", "SORCERER", "WIZARD"],
        "syntax": {
            "system": $dc.syntax,
            "dynamic": $dc.syntax
        },
        "description": $dc.description,
        "examples": {
            "basic": $dc.examples
        },
        "help_text": $dc.help_text,
        "source": "dynamic-commands.json",
        "script_integration": $dc.script,
        "validation": $dc.validation
    } as $unified_cmd |
    $existing[0].unified_commands += [$unified_cmd] |
    $existing[0]
    ' "$source_file" > "$unified_file.tmp" && mv "$unified_file.tmp" "$unified_file"

    success "Merged dynamic-commands.json"
}

# Merge ucode-commands.json
merge_ucode_commands_json() {
    local unified_file="$1"
    local source_file="$SYSTEM_DIR/ucode-commands.json"

    if [[ ! -f "$source_file" ]]; then
        warn "Source file not found: $source_file"
        return
    fi

    log "Merging ucode-commands.json..."

    jq --slurpfile existing "$unified_file" '
    .[] as $uc |
    {
        "command": $uc.command,
        "languages": ["uCODE"],
        "category": $uc.category,
        "priority": 2,
        "role_access": ["IMP", "SORCERER", "WIZARD"],
        "syntax": {
            "ucode": $uc.syntax
        },
        "description": $uc.description,
        "examples": {
            "basic": $uc.examples
        },
        "source": "ucode-commands.json",
        "version": $uc.version
    } as $unified_cmd |
    $existing[0].unified_commands += [$unified_cmd] |
    $existing[0]
    ' "$source_file" > "$unified_file.tmp" && mv "$unified_file.tmp" "$unified_file"

    success "Merged ucode-commands.json"
}

# Merge vb-commands.json
merge_vb_commands_json() {
    local unified_file="$1"
    local source_file="$SYSTEM_DIR/vb-commands.json"

    if [[ ! -f "$source_file" ]]; then
        warn "Source file not found: $source_file"
        return
    fi

    log "Merging vb-commands.json..."

    jq --slurpfile existing "$unified_file" '
    .commands[] as $vb |
    {
        "command": $vb.command,
        "languages": ["VB-Style"],
        "category": $vb.category,
        "priority": 6,
        "role_access": ["SORCERER", "WIZARD"],
        "syntax": {
            "vb": $vb.syntax
        },
        "description": $vb.description,
        "examples": {
            "basic": $vb.examples
        },
        "source": "vb-commands.json",
        "parameters": ($vb.parameters // [])
    } as $unified_cmd |
    $existing[0].unified_commands += [$unified_cmd] |
    $existing[0]
    ' "$source_file" > "$unified_file.tmp" && mv "$unified_file.tmp" "$unified_file"

    success "Merged vb-commands.json"
}

# Remove duplicate commands
deduplicate_commands() {
    local unified_file="$SYSTEM_DIR/unified-command-system-complete.json"

    log "Removing duplicate commands..."

    # Group by command name and merge information
    jq '
    .unified_commands |
    group_by(.command) |
    map({
        "command": .[0].command,
        "languages": (map(.languages[]) | unique),
        "category": .[0].category,
        "priority": (map(.priority) | min),
        "role_access": (map(.role_access[]) | unique),
        "syntax": (map(.syntax) | add),
        "description": .[0].description,
        "examples": (map(.examples // {}) | add),
        "help_text": (map(.help_text // "") | map(select(. != "")) | .[0] // ""),
        "source": (map(.source) | unique | join(", ")),
        "operations": (map(.operations // []) | add),
        "parameters": (map(.parameters // []) | add),
        "script_integration": (map(.script_integration // "") | map(select(. != "")) | .[0] // ""),
        "validation": (map(.validation // {}) | add),
        "version": (map(.version // "") | map(select(. != "")) | .[0] // "")
    }) as $deduplicated |
    . + {"unified_commands": $deduplicated}
    ' "$unified_file" > "$unified_file.tmp" && mv "$unified_file.tmp" "$unified_file"

    local final_count=$(jq '.unified_commands | length' "$unified_file")
    jq --arg count "$final_count" '.metadata.total_commands = ($count | tonumber)' "$unified_file" > "$unified_file.tmp" && mv "$unified_file.tmp" "$unified_file"

    success "Deduplicated to $final_count unique commands"
}

# Clean up duplicate uDATA files
cleanup_duplicates() {
    log "Cleaning up duplicate uDATA files..."

    local udata_dir="$SYSTEM_DIR/udata-converted"
    if [[ -d "$udata_dir" ]]; then
        # Move to backup
        mv "$udata_dir" "$BACKUP_DIR/udata-converted-backup"
        success "Moved udata-converted to backup"

        # Create new minimal udata-converted with only the unified file
        mkdir -p "$udata_dir"

        if [[ -f "$SYSTEM_DIR/unified-command-system-complete.json" ]]; then
            # Convert unified file to uDATA format
            jq '{
                "METADATA": .metadata,
                "COMMAND-CATEGORIES": .command_categories,
                "UNIFIED-COMMANDS": .unified_commands
            }' "$SYSTEM_DIR/unified-command-system-complete.json" > "$udata_dir/uDATA-$(date +%Y%m%d)-unified-command-system.json"

            success "Created uDATA format unified command file"
        fi
    fi
}

# Create migration report
create_migration_report() {
    local report_file="$BACKUP_DIR/migration-report.md"

    cat > "$report_file" << EOF
# uDOS Command System Migration Report

**Date**: $(date '+%Y-%m-%d %H:%M:%S')
**Migration Version**: v1.3.3

## Summary

This migration consolidated 5 separate command files into a unified command system:

### Source Files Processed:
- \`commands.json\` - Basic command definitions
- \`shortcodes.json\` - Modern shortcode system
- \`dynamic-commands.json\` - Extended system commands
- \`ucode-commands.json\` - uCODE programming language
- \`vb-commands.json\` - Visual Basic-style commands

### Output Files:
- \`unified-command-system-complete.json\` - Complete unified dataset
- \`help-engine-v1.3.3.sh\` - Dynamic help system

### Changes Made:
1. **Consolidated** all command definitions into single dataset
2. **Deduplicated** overlapping commands
3. **Standardized** schema format across all commands
4. **Added** role-based access filtering
5. **Enhanced** with dynamic help system integration
6. **Cleaned up** duplicate uDATA files

### Files Backed Up:
All original files have been preserved in: \`$BACKUP_DIR\`

### Integration Points:
- Dynamic help system: \`uCORE/core/help-engine-v1.3.3.sh\`
- Unified dataset: \`uMEMORY/system/unified-command-system-complete.json\`
- Role-based filtering integrated with 8-role system
- Interactive command exploration available

## Next Steps:
1. Test the new help system: \`./uCORE/core/help-engine-v1.3.3.sh --interactive\`
2. Update any scripts that reference old command files
3. Integrate with dashboard and CLI systems
4. Consider removing original files after validation

## Rollback Instructions:
If needed, original files can be restored from: \`$BACKUP_DIR\`
EOF

    success "Migration report created: $report_file"
}

# Main execution
main() {
    echo -e "${BLUE}╭─ uDOS Command System Migration v1.3.3 ─────────────╮${NC}"
    echo -e "${BLUE}│ Consolidating command datasets into unified system │${NC}"
    echo -e "${BLUE}╰────────────────────────────────────────────────────╯${NC}"
    echo

    backup_files
    echo

    analyze_overlap
    echo

    create_unified_dataset
    echo

    deduplicate_commands
    echo

    cleanup_duplicates
    echo

    create_migration_report
    echo

    success "Migration completed successfully!"
    log "Backup directory: $BACKUP_DIR"
    log "New unified file: $SYSTEM_DIR/unified-command-system-complete.json"
    log "Help engine: $SCRIPT_DIR/../uCORE/core/help-engine-v1.3.3.sh"

    echo
    echo -e "${GREEN}Test the new system:${NC}"
    echo -e "  ${YELLOW}$SCRIPT_DIR/../uCORE/core/help-engine-v1.3.3.sh --interactive${NC}"
}

# Run migration
main "$@"
