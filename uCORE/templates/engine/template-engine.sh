#!/bin/bash
# uCORE Template Engine v1.0.0
# Advanced template processing with variable substitution and logic

set -euo pipefail

# Configuration
TEMPLATE_ROOT="${UDOS_ROOT:-$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)}/uCORE/templates"
TEMPLATE_CACHE="$TEMPLATE_ROOT/.cache"
TEMPLATE_VARS="$TEMPLATE_ROOT/.variables"

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
PURPLE='\033[0;35m'
CYAN='\033[0;36m'
WHITE='\033[1;37m'
NC='\033[0m'

# Initialize template engine
init_template_engine() {
    mkdir -p "$TEMPLATE_CACHE"
    touch "$TEMPLATE_VARS"
    
    # Default variables
    cat > "$TEMPLATE_VARS" << EOF
# uCORE Template Variables
TIMESTAMP=$(date '+%Y-%m-%d %H:%M:%S')
DATE=$(date '+%Y-%m-%d')
TIME=$(date '+%H:%M:%S')
USER=$(whoami)
UDOS_VERSION=1.0.5.7
SYSTEM_STATUS=Online
TEMPLATE_ENGINE_VERSION=1.0.0
EOF
    
    echo -e "${GREEN}✅ Template engine initialized${NC}"
}

# Load variables
load_variables() {
    if [[ -f "$TEMPLATE_VARS" ]]; then
        source "$TEMPLATE_VARS"
    fi
}

# Set variable
set_variable() {
    local var_name="$1"
    local var_value="$2"
    
    # Validate variable name
    if [[ ! "$var_name" =~ ^[A-Z_][A-Z0-9_]*$ ]]; then
        echo -e "${RED}❌ Invalid variable name: $var_name${NC}"
        echo -e "${BLUE}💡 Use uppercase letters, numbers, and underscores only${NC}"
        return 1
    fi
    
    # Update variables file
    if grep -q "^$var_name=" "$TEMPLATE_VARS" 2>/dev/null; then
        sed -i.bak "s/^$var_name=.*/$var_name=$var_value/" "$TEMPLATE_VARS"
    else
        echo "$var_name=$var_value" >> "$TEMPLATE_VARS"
    fi
    
    echo -e "${GREEN}✅ Set $var_name=$var_value${NC}"
}

# Get variable
get_variable() {
    local var_name="$1"
    
    load_variables
    
    if [[ -n "${!var_name:-}" ]]; then
        echo "${!var_name}"
    else
        echo -e "${YELLOW}⚠️  Variable '$var_name' not set${NC}"
        return 1
    fi
}

# List all variables
list_variables() {
    echo -e "${CYAN}📋 Template Variables:${NC}"
    echo "========================"
    
    load_variables
    
    while IFS='=' read -r key value; do
        [[ "$key" =~ ^[A-Z_] ]] && echo -e "${BLUE}  $key${NC} = ${GREEN}$value${NC}"
    done < "$TEMPLATE_VARS"
}

# Process template with variable substitution
process_template() {
    local template_file="$1"
    local output_file="${2:-}"
    
    if [[ ! -f "$template_file" ]]; then
        echo -e "${RED}❌ Template not found: $template_file${NC}"
        return 1
    fi
    
    load_variables
    
    local processed_content
    processed_content=$(cat "$template_file")
    
    # Replace variables in format {VARIABLE_NAME}
    while IFS='=' read -r key value; do
        if [[ "$key" =~ ^[A-Z_] ]]; then
            processed_content="${processed_content//\{$key\}/$value}"
        fi
    done < "$TEMPLATE_VARS"
    
    # Handle conditional blocks {?VARIABLE}...{/VARIABLE}
    processed_content=$(echo "$processed_content" | sed -E 's/\{[\?!][^}]+\}[^{]*\{\/[^}]+\}//g')
    
    if [[ -n "$output_file" ]]; then
        echo "$processed_content" > "$output_file"
        echo -e "${GREEN}✅ Template processed to: $output_file${NC}"
    else
        echo "$processed_content"
    fi
}

# Create new template
create_template() {
    local template_name="$1"
    local template_type="${2:-basic}"
    
    local template_dir="$TEMPLATE_ROOT/collections/$template_type"
    mkdir -p "$template_dir"
    
    local template_file="$template_dir/$template_name.md"
    
    cat > "$template_file" << EOF
# {TEMPLATE_NAME} Template

**Generated**: {TIMESTAMP}  
**Author**: {USER}  
**Version**: {UDOS_VERSION}

## Description
Template for $template_name

## Variables
- TEMPLATE_NAME: $template_name
- USER: Current user
- TIMESTAMP: Generation time

## Content
This is a template for $template_name.

Generated on {DATE} at {TIME} by {USER}.

## Status
- System: {SYSTEM_STATUS}
- Version: {UDOS_VERSION}
EOF
    
    echo -e "${GREEN}✅ Created template: $template_file${NC}"
}

# List available templates
list_templates() {
    local template_type="${1:-all}"
    
    echo -e "${CYAN}📋 Available Templates:${NC}"
    echo "======================="
    
    if [[ "$template_type" == "all" ]]; then
        for category in "$TEMPLATE_ROOT/collections"/*; do
            if [[ -d "$category" ]]; then
                local category_name=$(basename "$category")
                echo -e "${BLUE}📁 $category_name:${NC}"
                
                for template in "$category"/*.md; do
                    if [[ -f "$template" ]]; then
                        local template_name=$(basename "$template" .md)
                        echo -e "  ${GREEN}• $template_name${NC}"
                    fi
                done
                echo
            fi
        done
    else
        local category_dir="$TEMPLATE_ROOT/collections/$template_type"
        if [[ -d "$category_dir" ]]; then
            echo -e "${BLUE}📁 $template_type:${NC}"
            for template in "$category_dir"/*.md; do
                if [[ -f "$template" ]]; then
                    local template_name=$(basename "$template" .md)
                    echo -e "  ${GREEN}• $template_name${NC}"
                fi
            done
        else
            echo -e "${YELLOW}⚠️  Template category not found: $template_type${NC}"
        fi
    fi
}

# Render template by name
render_template() {
    local template_name="$1"
    local template_type="${2:-basic}"
    local output_file="${3:-}"
    
    local template_file="$TEMPLATE_ROOT/collections/$template_type/$template_name.md"
    
    if [[ ! -f "$template_file" ]]; then
        echo -e "${RED}❌ Template not found: $template_type/$template_name${NC}"
        return 1
    fi
    
    set_variable "TEMPLATE_NAME" "$template_name"
    process_template "$template_file" "$output_file"
}

# Show help
show_help() {
    echo -e "${CYAN}🎨 uCORE Template Engine${NC}"
    echo "========================"
    echo ""
    echo -e "${WHITE}Commands:${NC}"
    echo "  init                          - Initialize template engine"
    echo "  set <var> <value>            - Set template variable"
    echo "  get <var>                    - Get variable value"
    echo "  list                         - List all variables"
    echo "  create <name> [type]         - Create new template"
    echo "  templates [type]             - List available templates"
    echo "  render <name> [type] [output] - Render template"
    echo "  process <file> [output]      - Process template file"
    echo ""
    echo -e "${WHITE}Examples:${NC}"
    echo "  $0 init"
    echo "  $0 set PROJECT_NAME myproject"
    echo "  $0 create api-endpoint api"
    echo "  $0 render api-endpoint api ./output.md"
    echo ""
}

# Main function
main() {
    local command="${1:-help}"
    shift || true
    
    case "$command" in
        "init")
            init_template_engine
            ;;
        "set")
            if [[ $# -lt 2 ]]; then
                echo -e "${RED}❌ Usage: $0 set <variable> <value>${NC}"
                exit 1
            fi
            set_variable "$1" "$2"
            ;;
        "get")
            if [[ $# -lt 1 ]]; then
                echo -e "${RED}❌ Usage: $0 get <variable>${NC}"
                exit 1
            fi
            get_variable "$1"
            ;;
        "list")
            list_variables
            ;;
        "create")
            if [[ $# -lt 1 ]]; then
                echo -e "${RED}❌ Usage: $0 create <name> [type]${NC}"
                exit 1
            fi
            create_template "$1" "${2:-basic}"
            ;;
        "templates")
            list_templates "${1:-all}"
            ;;
        "render")
            if [[ $# -lt 1 ]]; then
                echo -e "${RED}❌ Usage: $0 render <name> [type] [output]${NC}"
                exit 1
            fi
            render_template "$1" "${2:-basic}" "${3:-}"
            ;;
        "process")
            if [[ $# -lt 1 ]]; then
                echo -e "${RED}❌ Usage: $0 process <file> [output]${NC}"
                exit 1
            fi
            process_template "$1" "${2:-}"
            ;;
        "help"|"--help"|"-h")
            show_help
            ;;
        *)
            echo -e "${RED}❌ Unknown command: $command${NC}"
            show_help
            exit 1
            ;;
    esac
}

# Execute main function
main "$@"
