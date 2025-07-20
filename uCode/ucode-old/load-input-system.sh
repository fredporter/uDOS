#!/bin/bash
# uDOS Input System Integration
# Source this file from ucode.sh to enable input features

# Check if already loaded
[[ "${UDOS_INPUT_SYSTEM_LOADED:-}" == "true" ]] && return 0

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
UHOME="${UHOME:-$HOME/uDOS}"

# Load core input system
if [[ -f "$SCRIPT_DIR/input-system.sh" ]]; then
    source "$SCRIPT_DIR/input-system.sh"
fi

# Load input handler
if [[ -f "$SCRIPT_DIR/input-handler.sh" ]]; then
    source "$SCRIPT_DIR/input-handler.sh"
fi

# Colors for status messages
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
CYAN='\033[0;36m'
NC='\033[0m'

# input processing function for uCode integration
process_enhanced_input() {
    local input="$1"
    
    # Handle shortcode triggers
    if [[ "$input" == "[" ]] || [[ "$input" =~ ^\[.*$ ]]; then
        if command -v process_shortcode_input >/dev/null 2>&1; then
            process_shortcode_input "$input"
            return $?
        fi
    fi
    
    # Handle form-commands  
    if command -v process_command_with_forms >/dev/null 2>&1; then
        if process_command_with_forms "$input"; then
            return 0
        fi
    fi
    
    # Not handled by input system
    return 2
}

# Function to show input system status
show_input_system_status() {
    echo -e "${CYAN}🎯 Input System Status:${NC}"
    
    # Check core components
    local components_ok=true
    
    if command -v interactive_shortcode_selector >/dev/null 2>&1; then
        echo -e "  ${GREEN}✅ Shortcode selector available${NC}"
    else
        echo -e "  ${RED}❌ Shortcode selector missing${NC}"
        components_ok=false
    fi
    
    if command -v interactive_form >/dev/null 2>&1; then
        echo -e "  ${GREEN}✅ Interactive forms available${NC}"
    else
        echo -e "  ${RED}❌ Interactive forms missing${NC}"
        components_ok=false
    fi
    
    # Check datasets
    if [[ -f "$UHOME/uTemplate/datasets/shortcodes.json" ]]; then
        local shortcode_count
        if command -v jq >/dev/null 2>&1; then
            shortcode_count=$(jq '.shortcodes | length' "$UHOME/uTemplate/datasets/shortcodes.json" 2>/dev/null || echo "unknown")
        else
            shortcode_count="unknown (jq not available)"
        fi
        echo -e "  ${GREEN}✅ Shortcode database ($shortcode_count entries)${NC}"
    else
        echo -e "  ${YELLOW}⚠️ Shortcode database not initialized${NC}"
        echo -e "     ${CYAN}Run: ./uCode/input-system.sh init${NC}"
    fi
    
    # Check forms
    local dataget_count
    dataget_count=$(find "$UHOME/uTemplate/datagets" -name "*.json" 2>/dev/null | wc -l || echo "0")
    if [[ $dataget_count -gt 0 ]]; then
        echo -e "  ${GREEN}✅ Datagets available ($dataget_count configurations)${NC}"
    else
        echo -e "  ${RED}❌ No dataget configurations found${NC}"
    fi
    
    echo
    if [[ "$components_ok" == true ]]; then
        echo -e "${GREEN}🚀 Input system ready! Try typing '[' to launch shortcode selector${NC}"
    else
        echo -e "${YELLOW}🔧 Some components missing. Run validation: ./uCode/validate-input-system.sh test${NC}"
    fi
}

# Function to initialize input system on demand
init_input_system() {
    echo -e "${CYAN}🔧 Initializing input system...${NC}"
    
    # Initialize datasets
    if command -v init_shortcode_datasets >/dev/null 2>&1; then
        if init_shortcode_datasets; then
            echo -e "  ${GREEN}✅ Datasets initialized${NC}"
        else
            echo -e "  ${RED}❌ Dataset initialization failed${NC}"
            return 1
        fi
    fi
    
    # Initialize required directories
    mkdir -p "$UHOME/uMemory/datagets"
    mkdir -p "$UHOME/uMemory"
    
    echo -e "${GREEN}✅ Input system initialization complete${NC}"
    return 0
}

# command wrapper for uCode
enhanced_command_wrapper() {
    local cmd="$1"
    shift
    local args="$*"
    local full_input="$cmd $args"
    
    # Try input processing first
    if process_enhanced_input "$full_input"; then
        return $?
    fi
    
    # Fall back to normal processing
    return 2
}

# Export functions for uCode integration
export -f process_enhanced_input
export -f show_input_system_status
export -f init_input_system
export -f enhanced_command_wrapper

# Mark as loaded
export UDOS_INPUT_SYSTEM_LOADED=true

# Show status when sourced (but not during silent loads)
if [[ "${UDOS_SILENT_LOAD:-}" != "true" ]]; then
    echo -e "${GREEN}🎯 Input System loaded${NC}"
    
    # Initialize if needed
    if [[ ! -f "$UHOME/uTemplate/datasets/shortcodes.json" ]]; then
        echo -e "${YELLOW}⚡ First-time setup detected, initializing...${NC}"
        init_input_system
    fi
fi

# Provide usage hints
if [[ "${UDOS_SHOW_INPUT_HINTS:-}" == "true" ]]; then
    cat << 'EOF'

🎯 Input System Ready!

Quick Start:
  • Type [ to launch shortcode selector
  • Use: ucode DATAGET user-setup for interactive setup
  • Try: ucode INPUT DEMO for demonstration

EOF
fi
