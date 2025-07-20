#!/bin/bash
# enhanced-help-system.sh - Dataset-Driven Dynamic Help System for uDOS
# Version: 2.0.0
# Description: Links uCode commands to templated datasets and documentation

set -euo pipefail

# Script directory and project paths
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(dirname "$SCRIPT_DIR")"
DATASET_DIR="$PROJECT_ROOT/uTemplate/datasets"
DOCS_DIR="$PROJECT_ROOT/docs"
TEMPLATE_DIR="$PROJECT_ROOT/uTemplate"

# Colors for display
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
PURPLE='\033[0;35m'
CYAN='\033[0;36m'
BOLD='\033[1m'
NC='\033[0m' # No Color

# logging
log() { echo -e "${BLUE}[$(date +'%H:%M:%S')]${NC} $1"; }
error() { echo -e "${RED}[ERROR]${NC} $1" >&2; }
success() { echo -e "${GREEN}[SUCCESS]${NC} $1"; }
warning() { echo -e "${YELLOW}[WARNING]${NC} $1"; }

# Get command information from dataset
get_command_info() {
    local command="$1"
    local dataset_file="$DATASET_DIR/ucode-commands.json"
    
    if [[ ! -f "$dataset_file" ]]; then
        error "Command dataset not found: $dataset_file"
        return 1
    fi
    
    # Search for command (case insensitive)
    local cmd_info
    if command -v jq >/dev/null 2>&1; then
        cmd_info=$(jq -r ".[] | select(.command == \"$command\")" "$dataset_file" 2>/dev/null)
    else
        # Fallback without jq
        cmd_info=$(grep -A 10 -B 2 "\"command\": \"$command\"" "$dataset_file" || true)
    fi
    
    echo "$cmd_info"
}

# Show help for a specific command
show_command_help() {
    local command="$1"
    local cmd_info=$(get_command_info "$command")
    
    if [[ -z "$cmd_info" ]]; then
        error "Command '$command' not found in dataset"
        suggest_similar_commands "$command"
        return 1
    fi
    
    echo -e "${BOLD}${PURPLE}🔧 uDOS Command Help: $command${NC}"
    echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
    echo ""
    
    if command -v jq >/dev/null 2>&1; then
        local category=$(echo "$cmd_info" | jq -r '.category // "unknown"')
        local syntax=$(echo "$cmd_info" | jq -r '.syntax // "N/A"')
        local description=$(echo "$cmd_info" | jq -r '.description // "No description available"')
        local version=$(echo "$cmd_info" | jq -r '.version // "1.0.0"')
        
        echo -e "${CYAN}📂 Category:${NC} $category"
        echo -e "${CYAN}📋 Syntax:${NC} $syntax"
        echo -e "${CYAN}📄 Description:${NC} $description"
        echo -e "${CYAN}🏷️ Version:${NC} $version"
        echo ""
        
        # Show examples
        echo -e "${BLUE}💡 Examples:${NC}"
        echo "$cmd_info" | jq -r '.examples[]' | while read -r example; do
            echo -e "  • ${GREEN}$example${NC}"
        done
        echo ""
        
        # Link to documentation
        show_related_documentation "$command" "$category"
    else
        # Fallback display without jq
        echo -e "${CYAN}Command Information:${NC} $command"
        echo "$cmd_info"
    fi
}

# Show related documentation links
show_related_documentation() {
    local command="$1"
    local category="$2"
    
    echo -e "${PURPLE}📚 Related Documentation:${NC}"
    
    # Check for command-specific documentation
    local doc_files=(
        "$DOCS_DIR/command-reference.md"
        "$DOCS_DIR/user-manual.md"
        "$DOCS_DIR/feature-guide.md"
    )
    
    for doc_file in "${doc_files[@]}"; do
        if [[ -f "$doc_file" ]]; then
            local doc_name=$(basename "$doc_file" .md)
            local matches=$(grep -c -i "$command\|$category" "$doc_file" 2>/dev/null || echo "0")
            if [[ "$matches" -gt 0 ]]; then
                echo -e "  • ${GREEN}$doc_name${NC} ($matches references)"
            fi
        fi
    done
    
    # Check template system
    if [[ -f "$TEMPLATE_DIR/datasets/template-definitions.json" ]]; then
        echo -e "  • ${GREEN}Template System${NC} - Advanced usage patterns"
    fi
    
    # Category-specific links
    case "$category" in
        "system")
            echo -e "  • ${GREEN}System Commands${NC} - Core system operations"
            ;;
        "variables")
            echo -e "  • ${GREEN}Variable System${NC} - Data management and storage"
            ;;
        "control")
            echo -e "  • ${GREEN}Control Flow${NC} - Logic and execution patterns"
            ;;
        "file")
            echo -e "  • ${GREEN}File Operations${NC} - Data persistence and I/O"
            ;;
        "timing")
            echo -e "  • ${GREEN}Time Management${NC} - Scheduling and temporal operations"
            ;;
    esac
    
    echo ""
}

# Suggest similar commands
suggest_similar_commands() {
    local query="$1"
    local dataset_file="$DATASET_DIR/ucode-commands.json"
    
    if [[ ! -f "$dataset_file" ]] || ! command -v jq >/dev/null 2>&1; then
        return 0
    fi
    
    echo -e "${YELLOW}💡 Did you mean one of these?${NC}"
    
    # Find commands with similar names or categories
    local suggestions=$(jq -r ".[] | select(.command | contains(\"$(echo "$query" | tr '[:lower:]' '[:upper:]')\") or .description | contains(\"$query\")) | .command" "$dataset_file" 2>/dev/null | head -5)
    
    if [[ -n "$suggestions" ]]; then
        echo "$suggestions" | while read -r suggestion; do
            echo -e "  • ${GREEN}$suggestion${NC}"
        done
    else
        # Fallback to category-based suggestions
        echo -e "  • ${GREEN}HELP${NC} - Show all available commands"
        echo -e "  • ${GREEN}LIST${NC} - List system resources"
        echo -e "  • ${GREEN}CHECK${NC} - System validation commands"
    fi
    echo ""
}

# Show commands by category
show_commands_by_category() {
    local category="${1:-all}"
    local dataset_file="$DATASET_DIR/ucode-commands.json"
    
    if [[ ! -f "$dataset_file" ]]; then
        error "Command dataset not found"
        return 1
    fi
    
    echo -e "${BOLD}${PURPLE}🗂️ uDOS Commands by Category${NC}"
    echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
    echo ""
    
    if command -v jq >/dev/null 2>&1; then
        if [[ "$category" == "all" ]]; then
            # Get all unique categories
            local categories=$(jq -r '.[].category' "$dataset_file" | sort -u)
            
            echo "$categories" | while read -r cat; do
                show_category_commands "$cat"
            done
        else
            show_category_commands "$category"
        fi
    else
        warning "jq not available - showing basic format"
        cat "$dataset_file"
    fi
}

# Show commands for a specific category
show_category_commands() {
    local category="$1"
    local dataset_file="$DATASET_DIR/ucode-commands.json"
    
    # Category emoji mapping
    local emoji=""
    case "$category" in
        "system") emoji="🖥️" ;;
        "variables") emoji="📊" ;;
        "control") emoji="🔄" ;;
        "file") emoji="📁" ;;
        "timing") emoji="⏰" ;;
        "output") emoji="📤" ;;
        "input") emoji="📥" ;;
        "math") emoji="🔢" ;;
        "string") emoji="📝" ;;
        "network") emoji="🌐" ;;
        *) emoji="🔧" ;;
    esac
    
    local category_title=$(echo "${category:0:1}" | tr '[:lower:]' '[:upper:]')$(echo "${category:1}" | tr '[:upper:]' '[:lower:]')
    echo -e "${BLUE}$emoji ${category_title} Commands${NC}"
    echo "────────────────────────────────────────"
    
    # Get commands for this category
    local commands=$(jq -r ".[] | select(.category == \"$category\") | \"  • \\(.command) - \\(.description)\"" "$dataset_file" 2>/dev/null)
    
    if [[ -n "$commands" ]]; then
        echo "$commands" | while read -r line; do
            echo -e "${GREEN}$line${NC}"
        done
    else
        echo -e "  ${YELLOW}No commands found in category: $category${NC}"
    fi
    echo ""
}

# Generate comprehensive help documentation
generate_help_docs() {
    local output_file="$UHOME/uMemory/generated/comprehensive-help.md"
    mkdir -p "$(dirname "$output_file")"
    
    log "Generating comprehensive help documentation"
    
    cat > "$output_file" << EOF
# 🔧 uDOS Comprehensive Command Reference
*Generated on $(date) by Help System v2.0*

## 📚 Overview
This comprehensive reference links all uDOS commands to their dataset definitions, providing:
- **Detailed syntax** and usage patterns
- **Category-based organization** for easy navigation
- **Cross-references** to documentation and templates
- **Real-world examples** and use cases
- **Version tracking** and change history

## 📊 Dataset Integration
Commands are dynamically loaded from:
- \`ucode-commands.json\` - Core command definitions
- \`template-definitions.json\` - Template system integration
- \`docs/\` - Comprehensive documentation library

---

EOF

    # Generate category-based sections
    if command -v jq >/dev/null 2>&1 && [[ -f "$DATASET_DIR/ucode-commands.json" ]]; then
        local categories=$(jq -r '.[].category' "$DATASET_DIR/ucode-commands.json" | sort -u)
        
        echo "$categories" | while read -r category; do
            local category_title=$(echo "${category:0:1}" | tr '[:lower:]' '[:upper:]')$(echo "${category:1}" | tr '[:upper:]' '[:lower:]')
            echo "## ${category_title} Commands" >> "$output_file"
            echo "" >> "$output_file"
            
            # Get command names for this category first
            local commands_in_category=$(jq -r ".[] | select(.category == \"$category\") | .command" "$DATASET_DIR/ucode-commands.json")
            
            echo "$commands_in_category" | while read -r cmd_name; do
                local cmd_info=$(jq -r ".[] | select(.command == \"$cmd_name\")" "$DATASET_DIR/ucode-commands.json")
                local cmd_desc=$(echo "$cmd_info" | jq -r '.description')
                local cmd_syntax=$(echo "$cmd_info" | jq -r '.syntax')
                
                cat >> "$output_file" << EOF
### \`$cmd_name\`
**Description**: $cmd_desc
**Syntax**: \`$cmd_syntax\`

**Examples**:
EOF
                echo "$cmd_info" | jq -r '.examples[]' | while read -r example; do
                    echo "- \`$example\`" >> "$output_file"
                done
                echo "" >> "$output_file"
            done
        done
    fi
    
    success "Documentation generated: $output_file"
    echo -e "${CYAN}📄 Generated: $(wc -l < "$output_file") lines${NC}"
}

# Interactive help explorer
interactive_help() {
    echo -e "${PURPLE}🎮 Interactive Help Explorer${NC}"
    echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
    echo "Enter command names for detailed help, or:"
    echo "• 'categories' - Browse by category"
    echo "• 'all' - Show all commands"
    echo "• 'generate' - Generate documentation"
    echo "• 'quit' - Exit"
    echo ""
    
    while true; do
        echo -ne "${CYAN}help> ${NC}"
        read -r input
        
        case "$input" in
            "quit"|"exit"|"bye")
                echo -e "${GREEN}👋 Goodbye!${NC}"
                break
                ;;
            "categories")
                show_commands_by_category
                ;;
            "all")
                show_commands_by_category "all"
                ;;
            "generate")
                generate_help_docs
                ;;
            "")
                continue
                ;;
            *)
                show_command_help "$(echo "$input" | tr '[:lower:]' '[:upper:]')"
                ;;
        esac
        echo ""
    done
}

# Main function
main() {
    case "${1:-help}" in
        "command"|"cmd")
            if [[ -n "${2:-}" ]]; then
                show_command_help "$(echo "${2}" | tr '[:lower:]' '[:upper:]')"
            else
                error "Usage: $0 command <command_name>"
                exit 1
            fi
            ;;
        "category"|"cat")
            show_commands_by_category "${2:-all}"
            ;;
        "generate"|"docs")
            generate_help_docs
            ;;
        "interactive"|"repl")
            interactive_help
            ;;
        "search")
            if [[ -n "${2:-}" ]]; then
                local query="$2"
                echo -e "${PURPLE}🔍 Searching for: $query${NC}"
                if command -v jq >/dev/null 2>&1; then
                    local query_upper=$(echo "$query" | tr '[:lower:]' '[:upper:]')
                    jq -r --arg query "$query" --arg query_upper "$query_upper" '.[] | select((.command | contains($query_upper)) or (.description | contains($query)) or (.category | contains($query))) | "🔧 \(.command) (\(.category)) - \(.description)"' "$DATASET_DIR/ucode-commands.json" 2>/dev/null || echo "No matches found"
                else
                    grep -i "$query" "$DATASET_DIR/ucode-commands.json" || echo "No matches found"
                fi
            else
                error "Usage: $0 search <query>"
            fi
            ;;
        "stats")
            if [[ -f "$DATASET_DIR/ucode-commands.json" ]] && command -v jq >/dev/null 2>&1; then
                echo -e "${PURPLE}📊 Command Dataset Statistics${NC}"
                echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
                echo -e "Total commands: $(jq length "$DATASET_DIR/ucode-commands.json")"
                echo -e "Categories: $(jq -r '.[].category' "$DATASET_DIR/ucode-commands.json" | sort -u | wc -l)"
                echo ""
                echo "Commands by category:"
                jq -r '.[].category' "$DATASET_DIR/ucode-commands.json" | sort | uniq -c | while read -r count cat; do
                    echo -e "  $cat: ${GREEN}$count${NC}"
                done
            else
                error "Dataset not available or jq not installed"
            fi
            ;;
        "validate")
            log "Validating command dataset and help system"
            local errors=0
            
            # Check dataset file
            if [[ ! -f "$DATASET_DIR/ucode-commands.json" ]]; then
                error "Command dataset not found"
                ((errors++))
            fi
            
            # Check jq availability
            if ! command -v jq >/dev/null 2>&1; then
                warning "jq not available - limited functionality"
            fi
            
            # Validate JSON structure
            if command -v jq >/dev/null 2>&1 && [[ -f "$DATASET_DIR/ucode-commands.json" ]]; then
                if ! jq empty "$DATASET_DIR/ucode-commands.json" 2>/dev/null; then
                    error "Invalid JSON in command dataset"
                    ((errors++))
                fi
            fi
            
            if [[ $errors -eq 0 ]]; then
                success "Help system validation passed"
            else
                error "Help system validation failed with $errors errors"
                exit 1
            fi
            ;;
        "help"|*)
            echo -e "${PURPLE}🔧 Help System v2.0${NC}"
            echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
            echo ""
            echo "Dataset-driven dynamic help system for uDOS commands"
            echo ""
            echo "Usage: $0 <command> [options]"
            echo ""
            echo "Commands:"
            echo "  command <name>     - Show detailed help for specific command"
            echo "  category [name]    - Show commands by category (all if no name)"
            echo "  search <query>     - Search commands and descriptions"
            echo "  generate          - Generate comprehensive documentation"
            echo "  interactive       - Start interactive help explorer"
            echo "  stats            - Show dataset statistics"
            echo "  validate         - Validate help system"
            echo ""
            echo "Examples:"
            echo "  $0 command PRINT      # Show help for PRINT command"
            echo "  $0 category system    # Show all system commands"
            echo "  $0 search file        # Search for file-related commands"
            echo "  $0 generate           # Generate comprehensive docs"
            ;;
    esac
}

# Initialize if called directly
if [[ "${BASH_SOURCE[0]}" == "${0}" ]]; then
    main "$@"
fi
