#!/bin/bash
# uDOS ASCII Generator Integration

show_ascii_help() {
    echo ""
    echo "🎨 ASCII Generator - uDOS Integration"
    echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
    echo ""
    echo "📝 COMMANDS:"
    echo "  ascii-gen text 'Hello World'           - Generate ASCII text"
    echo "  ascii-gen image path/to/image.jpg      - Convert image to ASCII"
    echo "  ascii-gen banner 'uDOS' --font big     - Create ASCII banner"
    echo ""
    echo "🎛️ OPTIONS:"
    echo "  --width N        - Set output width (default: 80)"
    echo "  --height N       - Set output height"
    echo "  --font NAME      - Text font (small, big, block, etc.)"
    echo "  --invert         - Invert ASCII art"
    echo "  --save FILE      - Save output to file"
    echo ""
    echo "📁 INTEGRATION:"
    echo "  ascii-gen logo 'uDOS' > docs/ASCII-Art-Gallery.md"
    echo "  ascii-gen banner 'Welcome' >> uMemory/banner.md"
    echo ""
    echo "🔍 Available fonts: small, big, block, shadow, script"
    echo ""
}

# uDOS-specific ASCII generation functions
generate_udos_logo() {
    local text="${1:-uDOS}"
    local font="${2:-big}"
    
    echo "🎨 Generating uDOS logo..."
    ascii-gen text "$text" --font "$font" --width 60
}

generate_system_banner() {
    local title="${1:-System}"
    local subtitle="${2:-}"
    
    echo "🏷️ Generating system banner..."
    ascii-gen text "$title" --font big --width 80
    if [[ -n "$subtitle" ]]; then
        echo ""
        ascii-gen text "$subtitle" --font small --width 80
    fi
}

# Check if called directly
if [[ "${BASH_SOURCE[0]}" == "${0}" ]]; then
    case "${1:-help}" in
        help|--help|-h)
            show_ascii_help
            ;;
        logo)
            generate_udos_logo "$2" "$3"
            ;;
        banner)
            generate_system_banner "$2" "$3"
            ;;
        *)
            ascii-gen "$@"
            ;;
    esac
fi
