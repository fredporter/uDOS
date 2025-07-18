#!/bin/bash
# ARCHIVED SCRIPT - Use consolidated version instead
# Original: packages/manager-simple.sh
# Archived: Sat Jul 19 00:59:47 AEST 2025
# Replacement: See README.md in this directory

echo "⚠️ This script has been archived and consolidated."
echo "Use the consolidated version instead:"
echo "  ./packages/consolidated-manager.sh [command]"
echo "Or use unified manager: ./unified-manager.sh [group] [command]"
echo "See progress/script-consolidation-archive/README.md for details"
exit 1

# Original script content below:
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# #!/bin/bash
# # uDOS Package Manager - Simple and Compatible
# 
# SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
# UDOS_ROOT="$(dirname "$SCRIPT_DIR")"
# 
# echo "🌀 uDOS Package Manager v1.0"
# echo
# 
# case "${1:-help}" in
#     list)
#         echo "📦 Available Packages:"
#         echo
#         echo "ripgrep      $(command -v rg >/dev/null 2>&1 && echo '✅ Installed' || echo '⏳ Available')  - Fast text search"
#         echo "bat          $(command -v bat >/dev/null 2>&1 && echo '✅ Installed' || echo '⏳ Available')  - Syntax-highlighted file viewer"
#         echo "fd           $(command -v fd >/dev/null 2>&1 && echo '✅ Installed' || echo '⏳ Available')  - Fast file finder"
#         echo "glow         $(command -v glow >/dev/null 2>&1 && echo '✅ Installed' || echo '⏳ Available')  - Terminal markdown renderer"
#         echo "jq           $(command -v jq >/dev/null 2>&1 && echo '✅ Installed' || echo '⏳ Available')  - JSON processor"
#         echo "fzf          $(command -v fzf >/dev/null 2>&1 && echo '✅ Installed' || echo '⏳ Available')  - Fuzzy finder"
#         echo "gemini       $(command -v gemini >/dev/null 2>&1 && echo '✅ Installed' || echo '⏳ Available')  - Google Gemini CLI companion"
#         echo
#         ;;
#     install)
#         if [[ $# -lt 2 ]]; then
#             echo "❌ Package name required"
#             echo "Usage: $0 install <package>"
#             exit 1
#         fi
#         
#         package="$2"
#         installer="${SCRIPT_DIR}/install-${package}.sh"
#         
#         if [[ ! -f "$installer" ]]; then
#             echo "❌ Installer not found: $installer"
#             exit 1
#         fi
#         
#         echo "ℹ️  Installing $package..."
#         bash "$installer"
#         ;;
#     install-all)
#         echo "🚀 Installing all packages..."
#         for pkg in ripgrep bat fd glow jq fzf; do
#             echo "────────────────────────────────"
#             echo "Installing $pkg..."
#             if bash "${SCRIPT_DIR}/install-${pkg}.sh"; then
#                 echo "✅ $pkg installed successfully"
#             else
#                 echo "❌ Failed to install $pkg"
#             fi
#         done
#         echo "────────────────────────────────"
#         echo "🎉 Installation complete!"
#         ;;
#     status)
#         if [[ $# -lt 2 ]]; then
#             echo "❌ Package name required"
#             exit 1
#         fi
#         
#         package="$2"
#         if command -v "$package" >/dev/null 2>&1; then
#             echo "✅ $package is installed"
#             echo "Path: $(command -v "$package")"
#             echo "Version: $(command "$package" --version 2>/dev/null | head -n1 || echo 'unknown')"
#         else
#             echo "⏳ $package is not installed"
#         fi
#         ;;
#     help|*)
#         echo "Commands:"
#         echo "  list         - List all available packages"
#         echo "  install-all  - Install all packages"
#         echo "  install <pkg> - Install specific package"
#         echo "  status <pkg> - Check package status"
#         echo "  help         - Show this help"
#         echo
#         echo "Available packages: ripgrep bat fd glow jq fzf"
#         ;;
# esac
