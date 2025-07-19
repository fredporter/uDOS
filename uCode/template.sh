#!/bin/bash
# template.sh - uDOS Unified Template System v2.0
# Consolidated: template-generator.sh + display-template-processor.sh + vscode-template-processor.sh
# Handles all template processing, generation, and display configuration

set -euo pipefail

# Environment Setup
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
UHOME="${HOME}/uDOS"
UMEM="${UHOME}/uMemory"
TEMPLATE_DIR="${UHOME}/uTemplate"
DISPLAY_VARS="${UMEM}/config/display-vars.sh"

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
PURPLE='\033[0;35m'
CYAN='\033[0;36m'
WHITE='\033[1;37m'
NC='\033[0m'

# Logging
log() { echo -e "${CYAN}[$(date '+%H:%M:%S')] [TEMPLATE]${NC} $1"; }
success() { echo -e "${GREEN}✅${NC} $1"; }
error() { echo -e "${RED}❌${NC} $1" >&2; }
warn() { echo -e "${YELLOW}⚠️${NC} $1"; }
info() { echo -e "${BLUE}ℹ️${NC} $1"; }

# ═══════════════════════════════════════════════════════════════════════
# 🎨 DISPLAY TEMPLATE PROCESSING
# ═══════════════════════════════════════════════════════════════════════

# Initialize display configuration
init_display_config() {
    log "Initializing display configuration..."
    
    # Detect terminal capabilities
    local term_cols=${COLUMNS:-$(tput cols 2>/dev/null || echo 80)}
    local term_rows=${LINES:-$(tput lines 2>/dev/null || echo 24)}
    local term_program=${TERM_PROGRAM:-unknown}
    local colorterm=${COLORTERM:-unknown}
    
    # Determine optimal settings
    local display_mode="auto"
    local grid_cols=26
    local grid_rows=99
    local block_width=40
    local block_height=6
    local border_style="single"
    
    # Adjust for different terminals
    case "$term_program" in
        "vscode")
            display_mode="compact"
            block_width=35
            ;;
        "iTerm.app"|"kitty"|"WezTerm")
            display_mode="enhanced"
            block_width=45
            grid_cols=30
            ;;
    esac
    
    # Adjust for screen size
    if [[ $term_cols -gt 120 ]]; then
        display_mode="wide"
        grid_cols=32
        block_width=50
    elif [[ $term_cols -lt 80 ]]; then
        display_mode="narrow"
        grid_cols=20
        block_width=30
    fi
    
    # Create display variables file
    mkdir -p "$(dirname "$DISPLAY_VARS")"
    cat > "$DISPLAY_VARS" << EOF
#!/bin/bash
# uDOS Display Configuration Variables
# Generated: $(date '+%Y-%m-%d %H:%M:%S')

# Terminal Information
export UDOS_TERMINAL_PROGRAM="$term_program"
export UDOS_TERMINAL_COLORTERM="$colorterm"
export UDOS_TERMINAL_COLS=$term_cols
export UDOS_TERMINAL_ROWS=$term_rows

# Display Mode Configuration
export UDOS_DISPLAY_MODE="$display_mode"
export UDOS_GRID_COLS_MAX=$grid_cols
export UDOS_GRID_ROWS_MAX=$grid_rows
export UDOS_BLOCK_WIDTH=$block_width
export UDOS_BLOCK_HEIGHT=$block_height
export UDOS_BORDER_STYLE="$border_style"

# Color Configuration
export UDOS_COLORS_ENABLED=true
export UDOS_TRUECOLOR_SUPPORT=$(if [[ "$colorterm" == "truecolor" ]] || [[ "$colorterm" == "24bit" ]]; then echo "true"; else echo "false"; fi)

# ASCII Art Configuration
export UDOS_ASCII_ENABLED=true
export UDOS_ASCII_WIDTH=$((block_width - 4))
export UDOS_ASCII_HEIGHT=$((block_height - 2))

# Animation Settings
export UDOS_ANIMATION_ENABLED=true
export UDOS_ANIMATION_SPEED=100

# Responsive Design Settings
export UDOS_RESPONSIVE_MODE=true
export UDOS_BREAKPOINT_NARROW=80
export UDOS_BREAKPOINT_WIDE=120

# Template Processing Settings
export UDOS_TEMPLATE_CACHE_ENABLED=true
export UDOS_TEMPLATE_CACHE_DIR="$UMEM/cache/templates"
EOF

    source "$DISPLAY_VARS"
    success "Display configuration initialized ($display_mode mode: ${term_cols}x${term_rows})"
}

# Process display template
process_display_template() {
    local template_file="$1"
    local output_file="$2"
    
    if [[ ! -f "$template_file" ]]; then
        error "Template file not found: $template_file"
        return 1
    fi
    
    log "Processing display template: $(basename "$template_file")"
    
    # Load display variables
    [[ -f "$DISPLAY_VARS" ]] && source "$DISPLAY_VARS"
    
    # Create output directory
    mkdir -p "$(dirname "$output_file")"
    
    # Process template with variable substitution
    local temp_file=$(mktemp)
    cp "$template_file" "$temp_file"
    
    # Replace common template variables
    sed -i.bak \
        -e "s/{{TERMINAL_COLS}}/${UDOS_TERMINAL_COLS:-80}/g" \
        -e "s/{{TERMINAL_ROWS}}/${UDOS_TERMINAL_ROWS:-24}/g" \
        -e "s/{{BLOCK_WIDTH}}/${UDOS_BLOCK_WIDTH:-40}/g" \
        -e "s/{{BLOCK_HEIGHT}}/${UDOS_BLOCK_HEIGHT:-6}/g" \
        -e "s/{{DISPLAY_MODE}}/${UDOS_DISPLAY_MODE:-auto}/g" \
        -e "s/{{DATE}}/$(date '+%Y-%m-%d')/g" \
        -e "s/{{TIME}}/$(date '+%H:%M:%S')/g" \
        -e "s/{{USERNAME}}/$(whoami)/g" \
        -e "s/{{HOSTNAME}}/$(hostname)/g" \
        "$temp_file"
    
    mv "$temp_file" "$output_file"
    rm -f "$temp_file.bak" 2>/dev/null || true
    
    success "Template processed: $output_file"
}

# ═══════════════════════════════════════════════════════════════════════
# 📄 VS CODE TEMPLATE PROCESSING  
# ═══════════════════════════════════════════════════════════════════════

# Generate VS Code configuration
generate_vscode_config() {
    local workspace_dir="$UHOME"
    local vscode_dir="$workspace_dir/.vscode"
    
    log "Generating VS Code configuration..."
    mkdir -p "$vscode_dir"
    
    # Generate settings.json
    cat > "$vscode_dir/settings.json" << EOF
{
    "workbench.colorTheme": "Dark+ (default dark)",
    "editor.fontSize": 14,
    "editor.tabSize": 4,
    "editor.insertSpaces": true,
    "editor.wordWrap": "on",
    "files.trimTrailingWhitespace": true,
    "files.insertFinalNewline": true,
    "terminal.integrated.fontSize": 13,
    "terminal.integrated.shell.osx": "$SHELL",
    "markdown.preview.fontSize": 14,
    "explorer.confirmDelete": false,
    "git.confirmSync": false,
    "extensions.ignoreRecommendations": false,
    "workbench.startupEditor": "welcomePage"
}
EOF

    # Generate launch.json
    cat > "$vscode_dir/launch.json" << EOF
{
    "version": "0.2.0",
    "configurations": [
        {
            "name": "uDOS Shell Debug",
            "type": "bashdb",
            "request": "launch",
            "program": "\${workspaceFolder}/uCode/ucode.sh",
            "cwd": "\${workspaceFolder}",
            "args": [],
            "stopOnEntry": false
        }
    ]
}
EOF

    # Generate extensions.json (recommendations)
    cat > "$vscode_dir/extensions.json" << EOF
{
    "recommendations": [
        "ms-vscode.vscode-json",
        "ms-vscode.bash-debug",
        "yzhang.markdown-all-in-one",
        "davidanson.vscode-markdownlint",
        "ms-vscode.vscode-typescript-next",
        "ms-python.python",
        "rogalmic.bash-debug"
    ]
}
EOF

    success "VS Code configuration generated in $vscode_dir"
}

# Process VS Code template
process_vscode_template() {
    local template_type="$1"
    local output_dir="${2:-$UHOME/.vscode}"
    
    case "$template_type" in
        "workspace")
            generate_vscode_config
            ;;
        "extension")
            generate_extension_template "$output_dir"
            ;;
        "settings")
            generate_settings_template "$output_dir"
            ;;
        *)
            error "Unknown VS Code template type: $template_type"
            return 1
            ;;
    esac
}

# ═══════════════════════════════════════════════════════════════════════
# 📋 TEMPLATE GENERATION SYSTEM
# ═══════════════════════════════════════════════════════════════════════

# List available templates
list_templates() {
    log "Available templates in $TEMPLATE_DIR:"
    
    if [[ -d "$TEMPLATE_DIR" ]]; then
        find "$TEMPLATE_DIR" -name "*.md" -o -name "*.json" -o -name "*.sh" | while read -r template; do
            local rel_path=$(realpath --relative-to="$TEMPLATE_DIR" "$template" 2>/dev/null || echo "$template")
            local size=$(du -h "$template" | cut -f1)
            echo "  📄 $rel_path ($size)"
        done
    else
        warn "Template directory not found: $TEMPLATE_DIR"
    fi
}

# Generate template from type
generate_template() {
    local template_type="$1"
    local output_file="${2:-}"
    local template_vars="${3:-}"
    
    case "$template_type" in
        "mission")
            generate_mission_template "$output_file" "$template_vars"
            ;;
        "user")
            generate_user_template "$output_file" "$template_vars"
            ;;
        "config")
            generate_config_template "$output_file" "$template_vars"
            ;;
        "script")
            generate_script_template "$output_file" "$template_vars"
            ;;
        "display")
            generate_display_template "$output_file" "$template_vars"
            ;;
        *)
            error "Unknown template type: $template_type"
            show_template_help
            return 1
            ;;
    esac
}

# Generate mission template
generate_mission_template() {
    local output_file="$1"
    local mission_name="${2:-New Mission}"
    
    [[ -z "$output_file" ]] && output_file="$UMEM/missions/$(date +%Y%m%d_%H%M%S)_mission.md"
    
    mkdir -p "$(dirname "$output_file")"
    
    cat > "$output_file" << EOF
# 🎯 $mission_name

**Mission ID**: $(basename "$output_file" .md)
**Created**: $(date '+%Y-%m-%d %H:%M:%S')
**Status**: Active
**Priority**: Medium

## Objective

Define the main objective of this mission here.

## Tasks

- [ ] Task 1: Description
- [ ] Task 2: Description  
- [ ] Task 3: Description

## Resources

- Resource 1
- Resource 2

## Notes

Add any additional notes or context here.

---
*Generated by uDOS Template System v2.0*
EOF

    success "Mission template created: $output_file"
}

# Generate user identity template
generate_user_template() {
    local output_file="$1"
    local username="${2:-$(whoami)}"
    
    [[ -z "$output_file" ]] && output_file="$UMEM/user/$(date +%Y%m%d_%H%M%S)_user_identity.md"
    
    mkdir -p "$(dirname "$output_file")"
    
    cat > "$output_file" << EOF
# uDOS User Identity

**Username**: $username
**Location**: Earth
**Timezone**: UTC
**Created**: $(date '+%Y-%m-%d %H:%M:%S')
**Version**: uDOS v1.0

## Configuration

- **Theme**: dark
- **Shell**: $SHELL
- **Platform**: $(uname -s)

## Preferences

- **Debug Mode**: false
- **Auto Backup**: true
- **Logging Level**: info

---
*Generated by uDOS Template System v2.0*
EOF

    success "User template created: $output_file"
}

# Generate configuration template
generate_config_template() {
    local output_file="$1"
    local config_type="${2:-system}"
    
    [[ -z "$output_file" ]] && output_file="$UMEM/config/$(date +%Y%m%d_%H%M%S)_${config_type}.conf"
    
    mkdir -p "$(dirname "$output_file")"
    
    cat > "$output_file" << EOF
# uDOS Configuration File
# Type: $config_type
# Generated: $(date '+%Y-%m-%d %H:%M:%S')

# System Settings
UDOS_VERSION=1.0
UDOS_DEBUG=false
UDOS_LOGGING=info

# User Settings
UDOS_USER=$(whoami)
UDOS_HOSTNAME=$(hostname)
UDOS_SHELL=$SHELL

# Feature Settings
UDOS_FEATURES_ENABLED=dashboard,missions,sandbox
UDOS_TEMPLATE_SYSTEM=enabled
UDOS_DISPLAY_MODE=auto

# Path Settings  
UDOS_HOME=$UHOME
UDOS_MEMORY=$UMEM
UDOS_TEMPLATES=$TEMPLATE_DIR
EOF

    success "Configuration template created: $output_file"
}

# ═══════════════════════════════════════════════════════════════════════
# 📊 TEMPLATE STATISTICS AND INFO
# ═══════════════════════════════════════════════════════════════════════

# Show template statistics
show_template_stats() {
    log "Template system statistics:"
    
    local total_templates=0
    local template_types=()
    
    if [[ -d "$TEMPLATE_DIR" ]]; then
        total_templates=$(find "$TEMPLATE_DIR" -type f | wc -l | tr -d ' ')
        
        # Count by type
        local md_count=$(find "$TEMPLATE_DIR" -name "*.md" | wc -l | tr -d ' ')
        local json_count=$(find "$TEMPLATE_DIR" -name "*.json" | wc -l | tr -d ' ')
        local sh_count=$(find "$TEMPLATE_DIR" -name "*.sh" | wc -l | tr -d ' ')
        local other_count=$((total_templates - md_count - json_count - sh_count))
        
        echo "  📊 Total templates: $total_templates"
        echo "  📄 Markdown templates: $md_count"
        echo "  🔧 JSON templates: $json_count"
        echo "  📜 Shell templates: $sh_count"
        [[ $other_count -gt 0 ]] && echo "  📁 Other templates: $other_count"
    else
        warn "Template directory not found"
    fi
    
    # Check generated files
    local user_files=$(find "$UMEM/user" -name "*.md" 2>/dev/null | wc -l | tr -d ' ')
    local config_files=$(find "$UMEM/config" -name "*.sh" -o -name "*.conf" 2>/dev/null | wc -l | tr -d ' ')
    local mission_files=$(find "$UMEM/missions" -name "*.md" 2>/dev/null | wc -l | tr -d ' ')
    
    echo
    echo "  📈 Generated files:"
    echo "    👤 User files: $user_files"
    echo "    ⚙️  Config files: $config_files"
    echo "    🎯 Mission files: $mission_files"
}

# Validate template system
validate_templates() {
    log "Validating template system..."
    
    local issues=0
    
    # Check template directory
    if [[ ! -d "$TEMPLATE_DIR" ]]; then
        error "Template directory missing: $TEMPLATE_DIR"
        ((issues++))
    else
        success "Template directory exists"
    fi
    
    # Check core templates
    local core_templates=("uc-template.md" "user-setup-template.md")
    for template in "${core_templates[@]}"; do
        if [[ -f "$TEMPLATE_DIR/$template" ]]; then
            success "Core template exists: $template"
        else
            warn "Core template missing: $template"
            ((issues++))
        fi
    done
    
    # Check display configuration
    if [[ -f "$DISPLAY_VARS" ]]; then
        success "Display configuration exists"
    else
        warn "Display configuration missing - run: template display init"
        ((issues++))
    fi
    
    return $issues
}

# ═══════════════════════════════════════════════════════════════════════
# 🎯 MAIN COMMAND INTERFACE
# ═══════════════════════════════════════════════════════════════════════

# Show help
show_help() {
    echo -e "${PURPLE}╔══════════════════════════════════════════════════════════════╗${NC}"
    echo -e "${PURPLE}║                  🎨 uDOS TEMPLATE SYSTEM                    ║${NC}"
    echo -e "${PURPLE}║            Generation · Processing · Display v2.0           ║${NC}"
    echo -e "${PURPLE}╚══════════════════════════════════════════════════════════════╝${NC}"
    echo
    
    echo -e "${WHITE}Template System Commands:${NC}"
    echo -e "${YELLOW}═══════════════════════════════════════════════════════════════${NC}"
    echo
    echo -e "${CYAN}🎨 Template Generation:${NC}"
    echo -e "${WHITE}  template generate mission [file] [name]  Generate mission template${NC}"
    echo -e "${WHITE}  template generate user [file] [name]     Generate user template${NC}"
    echo -e "${WHITE}  template generate config [file] [type]   Generate config template${NC}"
    echo -e "${WHITE}  template generate script [file] [name]   Generate script template${NC}"
    echo
    echo -e "${CYAN}🖥️  Display Processing:${NC}"
    echo -e "${WHITE}  template display init                    Initialize display config${NC}"
    echo -e "${WHITE}  template display process <file> <out>    Process display template${NC}"
    echo -e "${WHITE}  template display vars                    Show display variables${NC}"
    echo
    echo -e "${CYAN}📄 VS Code Integration:${NC}"
    echo -e "${WHITE}  template vscode workspace                Generate VS Code config${NC}"
    echo -e "${WHITE}  template vscode extension                Generate extension config${NC}"
    echo -e "${WHITE}  template vscode settings                 Generate settings only${NC}"
    echo
    echo -e "${CYAN}📊 Information & Management:${NC}"
    echo -e "${WHITE}  template list                           List available templates${NC}"
    echo -e "${WHITE}  template stats                          Show template statistics${NC}"
    echo -e "${WHITE}  template validate                       Validate template system${NC}"
    echo -e "${WHITE}  template help                           Show this help${NC}"
    echo
}

# Show template help for generation
show_template_help() {
    echo -e "${CYAN}Available template types:${NC}"
    echo "  mission  - Mission/task template"
    echo "  user     - User identity template"  
    echo "  config   - Configuration file template"
    echo "  script   - Shell script template"
    echo "  display  - Display configuration template"
}

# Main command router
main() {
    local command="${1:-help}"
    
    case "$command" in
        "generate"|"gen")
            local template_type="${2:-}"
            local output_file="${3:-}"
            local template_vars="${4:-}"
            
            if [[ -z "$template_type" ]]; then
                error "Template type required"
                show_template_help
                return 1
            fi
            
            generate_template "$template_type" "$output_file" "$template_vars"
            ;;
        "display")
            local subcommand="${2:-help}"
            case "$subcommand" in
                "init"|"initialize")
                    init_display_config
                    ;;
                "process")
                    local input_file="${3:-}"
                    local output_file="${4:-}"
                    if [[ -z "$input_file" || -z "$output_file" ]]; then
                        error "Usage: template display process <input_file> <output_file>"
                        return 1
                    fi
                    process_display_template "$input_file" "$output_file"
                    ;;
                "vars"|"variables")
                    if [[ -f "$DISPLAY_VARS" ]]; then
                        source "$DISPLAY_VARS"
                        echo "Display Variables:"
                        env | grep UDOS_ | sort
                    else
                        warn "Display variables not initialized. Run: template display init"
                    fi
                    ;;
                *)
                    error "Unknown display command: $subcommand"
                    echo "Available: init, process, vars"
                    ;;
            esac
            ;;
        "vscode"|"vs")
            local subcommand="${2:-workspace}"
            local output_dir="${3:-}"
            process_vscode_template "$subcommand" "$output_dir"
            ;;
        "list"|"ls")
            list_templates
            ;;
        "stats"|"statistics")
            show_template_stats
            ;;
        "validate"|"check")
            validate_templates
            ;;
        "help"|"-h"|"--help"|*)
            show_help
            ;;
    esac
}

# Execute main function if script is called directly
if [[ "${BASH_SOURCE[0]}" == "${0}" ]]; then
    main "$@"
fi
