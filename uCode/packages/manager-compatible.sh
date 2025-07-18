#!/bin/bash
# ARCHIVED SCRIPT - Use consolidated version instead
# Original: packages/manager-compatible.sh
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
# # uDOS Package Manager v2.0.0 - Compatible Edition
# # Description: Shortcode-integrated package management (Bash 3.2+ compatible)
# 
# set -euo pipefail
# 
# # Environment Setup
# SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
# UDOS_ROOT="$(dirname "$SCRIPT_DIR")"
# UHOME="${UHOME:-$HOME/uDOS}"
# PACKAGE_DIR="$SCRIPT_DIR"
# TEMPLATE_DIR="$UHOME/uTemplate"
# MEMORY_DIR="$UHOME/uMemory"
# 
# # Colors for output
# RED='\033[0;31m'
# GREEN='\033[0;32m'
# YELLOW='\033[1;33m'
# BLUE='\033[0;34m'
# PURPLE='\033[0;35m'
# CYAN='\033[0;36m'
# NC='\033[0m' # No Color
# 
# # Error handling
# error_log() {
#     echo -e "${RED}❌ ERROR: $1${NC}" >&2
#     [[ -d "$MEMORY_DIR/logs" ]] && echo "[$(date)] ERROR: $1" >> "$MEMORY_DIR/logs/package-manager.log"
# }
# 
# info_log() {
#     echo -e "${BLUE}ℹ️  $1${NC}"
#     [[ -d "$MEMORY_DIR/logs" ]] && echo "[$(date)] INFO: $1" >> "$MEMORY_DIR/logs/package-manager.log"
# }
# 
# success_log() {
#     echo -e "${GREEN}✅ $1${NC}"
#     [[ -d "$MEMORY_DIR/logs" ]] && echo "[$(date)] SUCCESS: $1" >> "$MEMORY_DIR/logs/package-manager.log"
# }
# 
# warning_log() {
#     echo -e "${YELLOW}⚠️  $1${NC}"
#     [[ -d "$MEMORY_DIR/logs" ]] && echo "[$(date)] WARNING: $1" >> "$MEMORY_DIR/logs/package-manager.log"
# }
# 
# # Package database (compatible format)
# # Format: package_name|command|description|homepage|tags
# PACKAGE_DB="
# ripgrep|rg|Fast text search|https://github.com/BurntSushi/ripgrep|search,utility
# bat|bat|Syntax-highlighted file viewer|https://github.com/sharkdp/bat|viewer,utility
# fd|fd|Fast file finder|https://github.com/sharkdp/fd|finder,utility
# glow|glow|Terminal markdown renderer|https://github.com/charmbracelet/glow|markdown,viewer
# jq|jq|JSON processor|https://github.com/jqlang/jq|json,processor
# fzf|fzf|Fuzzy finder|https://github.com/junegunn/fzf|finder,interactive
# gemini|gemini|Google Gemini CLI|https://github.com/google/generative-ai|ai,assistant
# eza|eza|Modern ls replacement|https://github.com/eza-community/eza|listing,utility
# zoxide|zoxide|Smart cd command|https://github.com/ajeetdsouza/zoxide|navigation,utility
# delta|delta|Better diff viewer|https://github.com/dandavison/delta|diff,utility
# "
# 
# # Get package info by name
# get_package_info() {
#     local package="$1"
#     echo "$PACKAGE_DB" | grep "^$package|" | head -1
# }
# 
# # Get package field
# get_package_field() {
#     local package="$1"
#     local field="$2"
#     local info=$(get_package_info "$package")
#     [[ -z "$info" ]] && return 1
#     
#     case "$field" in
#         "command") echo "$info" | cut -d'|' -f2 ;;
#         "description") echo "$info" | cut -d'|' -f3 ;;
#         "homepage") echo "$info" | cut -d'|' -f4 ;;
#         "tags") echo "$info" | cut -d'|' -f5 ;;
#         *) return 1 ;;
#     esac
# }
# 
# # List all packages
# list_all_packages() {
#     echo "$PACKAGE_DB" | grep -v "^$" | awk -F'|' '{print $1}'
# }
# 
# # Get package status
# get_package_status() {
#     local package="$1"
#     local cmd=$(get_package_field "$package" "command")
#     
#     if [[ -n "$cmd" ]] && command -v "$cmd" >/dev/null 2>&1; then
#         echo "installed"
#     else
#         echo "available"
#     fi
# }
# 
# # Get package version
# get_package_version() {
#     local cmd="$1"
#     
#     case "$cmd" in
#         "rg") rg --version 2>/dev/null | head -n1 | awk '{print $2}' ;;
#         "bat") bat --version 2>/dev/null | head -n1 | awk '{print $2}' ;;
#         "fd") fd --version 2>/dev/null | head -n1 | awk '{print $2}' ;;
#         "glow") glow --version 2>/dev/null | head -n1 | awk '{print $3}' ;;
#         "jq") jq --version 2>/dev/null | sed 's/jq-//' ;;
#         "fzf") fzf --version 2>/dev/null | awk '{print $1}' ;;
#         *) echo "unknown" ;;
#     esac
# }
# 
# # Initialize package manager
# initialize_package_manager() {
#     info_log "Initializing uDOS Package Manager v2.0.0 (Compatible)"
#     
#     # Create necessary directories
#     mkdir -p "$MEMORY_DIR/packages/installed"
#     mkdir -p "$MEMORY_DIR/packages/configs"
#     mkdir -p "$MEMORY_DIR/packages/cache"
#     mkdir -p "$MEMORY_DIR/logs"
#     
#     # Create package registry
#     create_package_registry
# }
# 
# # Create package registry
# create_package_registry() {
#     local registry_file="$MEMORY_DIR/packages/registry.json"
#     
#     echo "{" > "$registry_file"
#     echo "  \"version\": \"2.0.0\"," >> "$registry_file"
#     echo "  \"updated\": \"$(date)\"," >> "$registry_file"
#     echo "  \"packages\": {" >> "$registry_file"
#     
#     local first=true
#     for package in $(list_all_packages); do
#         [[ "$first" == "false" ]] && echo "," >> "$registry_file"
#         first=false
#         
#         local cmd=$(get_package_field "$package" "command")
#         local desc=$(get_package_field "$package" "description")
#         local url=$(get_package_field "$package" "homepage")
#         local tags=$(get_package_field "$package" "tags")
#         local status=$(get_package_status "$package")
#         local version=$(get_package_version "$cmd")
#         
#         cat >> "$registry_file" << EOF
#     "$package": {
#       "command": "$cmd",
#       "description": "$desc",
#       "homepage": "$url",
#       "tags": "$tags",
#       "installer": "install-$package.sh",
#       "status": "$status",
#       "version": "$version"
#     }
# EOF
#     done
#     
#     echo "" >> "$registry_file"
#     echo "  }" >> "$registry_file"
#     echo "}" >> "$registry_file"
#     
#     info_log "Package registry created: $registry_file"
# }
# 
# # List packages with enhanced display
# list_packages() {
#     local category_filter="${1:-all}"
#     local status_filter="${2:-all}"
#     
#     echo -e "${PURPLE}📦 uDOS Package Manager v2.0.0 (Compatible)${NC}"
#     echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
#     echo ""
#     
#     # Categories for grouping
#     local search_packages="ripgrep fd fzf"
#     local viewer_packages="bat glow"
#     local utility_packages="jq eza zoxide delta"
#     local ai_packages="gemini"
#     
#     # Function to display category
#     display_category() {
#         local cat_name="$1"
#         local cat_icon="$2"
#         local cat_packages="$3"
#         
#         echo -e "${BLUE}$cat_icon $cat_name${NC}"
#         echo ""
#         
#         for pkg in $cat_packages; do
#             local cmd=$(get_package_field "$pkg" "command")
#             local desc=$(get_package_field "$pkg" "description")
#             local status=$(get_package_status "$pkg")
#             
#             # Apply filters
#             if [[ "$status_filter" != "all" && "$status" != "$status_filter" ]]; then
#                 continue
#             fi
#             
#             local status_icon="⏳"
#             local status_color="$YELLOW"
#             if [[ "$status" == "installed" ]]; then
#                 status_icon="✅"
#                 status_color="$GREEN"
#             fi
#             
#             local version=$(get_package_version "$cmd")
#             printf "  %-12s %s%-10s%s %s\n" "$pkg" "$status_color" "$status_icon $status" "$NC" "$desc"
#             if [[ "$status" == "installed" && "$version" != "unknown" ]]; then
#                 printf "               ${CYAN}v%s${NC} - %s\n" "$version" "$cmd"
#             fi
#         done
#         echo ""
#     }
#     
#     # Display categories
#     case "$category_filter" in
#         "all")
#             display_category "Search & Find Tools" "🔍" "$search_packages"
#             display_category "File Viewers & Displays" "👀" "$viewer_packages"
#             display_category "System Utilities" "🛠️" "$utility_packages"
#             display_category "AI & Intelligence Tools" "🤖" "$ai_packages"
#             ;;
#         "search")
#             display_category "Search & Find Tools" "🔍" "$search_packages"
#             ;;
#         "viewer")
#             display_category "File Viewers & Displays" "👀" "$viewer_packages"
#             ;;
#         "utility")
#             display_category "System Utilities" "🛠️" "$utility_packages"
#             ;;
#         "ai")
#             display_category "AI & Intelligence Tools" "🤖" "$ai_packages"
#             ;;
#         *)
#             display_category "All Packages" "📦" "$(list_all_packages)"
#             ;;
#     esac
#     
#     # Show statistics
#     local total=$(list_all_packages | wc -l)
#     local installed=0
#     for package in $(list_all_packages); do
#         [[ "$(get_package_status "$package")" == "installed" ]] && installed=$((installed + 1))
#     done
#     
#     echo -e "${CYAN}📊 Statistics:${NC}"
#     echo "  Total packages: $total"
#     echo "  Installed: $installed"
#     echo "  Available: $((total - installed))"
# }
# 
# # Install package
# install_package() {
#     local package="$1"
#     local force="${2:-false}"
#     
#     if [[ -z "$package" ]]; then
#         error_log "Package name required"
#         echo "💡 Usage: [package:install <package-name>]"
#         return 1
#     fi
#     
#     local package_info=$(get_package_info "$package")
#     if [[ -z "$package_info" ]]; then
#         error_log "Unknown package: $package"
#         suggest_similar_packages "$package"
#         return 1
#     fi
#     
#     local cmd=$(get_package_field "$package" "command")
#     local desc=$(get_package_field "$package" "description")
#     local url=$(get_package_field "$package" "homepage")
#     
#     # Check if already installed
#     if [[ "$force" != "true" ]] && command -v "$cmd" >/dev/null 2>&1; then
#         warning_log "$package is already installed: $(get_package_version "$cmd")"
#         echo "💡 Use [package:reinstall $package] to force reinstall"
#         return 0
#     fi
#     
#     info_log "Installing $package ($desc)"
#     echo -e "${CYAN}📦 Package: $package${NC}"
#     echo -e "${CYAN}🔗 Homepage: $url${NC}"
#     echo ""
#     
#     # Run installer
#     local installer="$PACKAGE_DIR/install-$package.sh"
#     if [[ ! -f "$installer" ]]; then
#         error_log "Installer not found: $installer"
#         return 1
#     fi
#     
#     # Create installation log
#     local install_log="$MEMORY_DIR/logs/install-$package-$(date +%Y%m%d-%H%M%S).log"
#     
#     echo "Starting installation at $(date)" > "$install_log"
#     if bash "$installer" 2>&1 | tee -a "$install_log"; then
#         success_log "$package installed successfully"
#         
#         # Update package status
#         update_package_status "$package" "installed"
#         
#         return 0
#     else
#         error_log "Failed to install $package"
#         echo "📋 Installation log: $install_log"
#         return 1
#     fi
# }
# 
# # Update package status
# update_package_status() {
#     local package="$1"
#     local status="$2"
#     local cmd=$(get_package_field "$package" "command")
#     
#     local status_file="$MEMORY_DIR/packages/installed/$package.json"
#     cat > "$status_file" << EOF
# {
#   "package": "$package",
#   "status": "$status",
#   "installed_at": "$(date)",
#   "version": "$(get_package_version "$cmd")",
#   "installer_version": "2.0.0"
# }
# EOF
# }
# 
# # Suggest similar packages
# suggest_similar_packages() {
#     local query="$1"
#     echo -e "${YELLOW}💡 Did you mean one of these?${NC}"
#     
#     for package in $(list_all_packages); do
#         local desc=$(get_package_field "$package" "description")
#         local tags=$(get_package_field "$package" "tags")
#         
#         if echo "$package $desc $tags" | grep -qi "$query"; then
#             echo "  • $package - $desc"
#         fi
#     done
# }
# 
# # Show package information
# show_package_info() {
#     local package="$1"
#     
#     if [[ -z "$package" ]]; then
#         error_log "Package name required"
#         return 1
#     fi
#     
#     local package_info=$(get_package_info "$package")
#     if [[ -z "$package_info" ]]; then
#         error_log "Unknown package: $package"
#         return 1
#     fi
#     
#     local cmd=$(get_package_field "$package" "command")
#     local desc=$(get_package_field "$package" "description")
#     local url=$(get_package_field "$package" "homepage")
#     local tags=$(get_package_field "$package" "tags")
#     local status=$(get_package_status "$package")
#     local version=$(get_package_version "$cmd")
#     
#     echo -e "${PURPLE}📦 Package Information: $package${NC}"
#     echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
#     echo ""
#     echo -e "${BLUE}📋 Basic Information${NC}"
#     echo "  Name: $package"
#     echo "  Command: $cmd"
#     echo "  Description: $desc"
#     echo "  Homepage: $url"
#     echo "  Tags: $tags"
#     echo ""
#     echo -e "${BLUE}📊 Status Information${NC}"
#     echo "  Status: $status"
#     if [[ "$status" == "installed" ]]; then
#         echo "  Version: $version"
#         echo "  Command Path: $(command -v "$cmd")"
#     fi
#     echo ""
#     
#     # Show available shortcodes
#     echo -e "${BLUE}🔧 Available Shortcodes${NC}"
#     echo "  [package:status $package] - Check package status"
#     echo "  [package:info $package] - Show this information"
#     if [[ "$status" == "installed" ]]; then
#         echo "  [package:update $package] - Update package"
#         echo "  [package:remove $package] - Remove package"
#     else
#         echo "  [package:install $package] - Install package"
#     fi
# }
# 
# # Install all packages
# install_all_packages() {
#     echo -e "${PURPLE}🚀 Installing All uDOS Packages${NC}"
#     echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
#     echo ""
#     
#     local total=$(list_all_packages | wc -l)
#     local installed=0
#     local failed=0
#     
#     for package in $(list_all_packages); do
#         echo "────────────────────────────────────────"
#         if install_package "$package"; then
#             installed=$((installed + 1))
#         else
#             failed=$((failed + 1))
#         fi
#     done
#     
#     echo "────────────────────────────────────────"
#     echo -e "${GREEN}🎉 Installation Summary${NC}"
#     echo "  Total packages: $total"
#     echo "  Successfully installed: $installed"
#     echo "  Failed: $failed"
#     
#     if [[ $failed -gt 0 ]]; then
#         echo -e "${YELLOW}⚠️  Some packages failed to install${NC}"
#         echo "Check logs in $MEMORY_DIR/logs/ for details"
#     fi
# }
# 
# # Search packages
# search_packages() {
#     local query="$1"
#     
#     if [[ -z "$query" ]]; then
#         error_log "Search query required"
#         return 1
#     fi
#     
#     echo -e "${CYAN}🔍 Searching packages for: $query${NC}"
#     echo ""
#     
#     local found=0
#     for package in $(list_all_packages); do
#         local cmd=$(get_package_field "$package" "command")
#         local desc=$(get_package_field "$package" "description")
#         local tags=$(get_package_field "$package" "tags")
#         
#         if echo "$package $desc $tags" | grep -qi "$query"; then
#             local status=$(get_package_status "$package")
#             local status_icon="⏳"
#             [[ "$status" == "installed" ]] && status_icon="✅"
#             
#             echo -e "${BLUE}$package${NC} $status_icon"
#             echo "  $desc"
#             echo "  Tags: $tags"
#             echo ""
#             found=$((found + 1))
#         fi
#     done
#     
#     if [[ $found -eq 0 ]]; then
#         warning_log "No packages found matching: $query"
#     else
#         echo -e "${GREEN}Found $found package(s)${NC}"
#     fi
# }
# 
# # Process shortcode commands
# process_package_shortcode() {
#     local action="$1"
#     shift
#     
#     case "$action" in
#         "list")
#             list_packages "$@"
#             ;;
#         "install")
#             install_package "$@"
#             ;;
#         "reinstall")
#             install_package "$1" "true"
#             ;;
#         "status")
#             if [[ $# -eq 0 ]]; then
#                 list_packages
#             else
#                 show_package_info "$1"
#             fi
#             ;;
#         "info")
#             show_package_info "$1"
#             ;;
#         "install-all")
#             install_all_packages
#             ;;
#         "search")
#             search_packages "$1"
#             ;;
#         "registry")
#             show_registry
#             ;;
#         "help")
#             show_package_help
#             ;;
#         *)
#             error_log "Unknown package action: $action"
#             show_package_help
#             return 1
#             ;;
#     esac
# }
# 
# # Show registry
# show_registry() {
#     local registry_file="$MEMORY_DIR/packages/registry.json"
#     
#     if [[ -f "$registry_file" ]]; then
#         echo -e "${CYAN}📋 Package Registry${NC}"
#         echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
#         
#         if command -v jq >/dev/null 2>&1; then
#             jq '.' "$registry_file"
#         else
#             cat "$registry_file"
#         fi
#     else
#         warning_log "Package registry not found. Run: [package:list] to create it"
#     fi
# }
# 
# # Show package help
# show_package_help() {
#     echo -e "${PURPLE}📦 uDOS Package Manager v2.0.0 (Compatible)${NC}"
#     echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
#     echo ""
#     echo -e "${BLUE}📋 Available Shortcodes${NC}"
#     echo ""
#     echo -e "${GREEN}Package Management:${NC}"
#     echo "  [package:list] - List all packages"
#     echo "  [package:list <category>] - List packages by category"
#     echo "  [package:install <package>] - Install specific package"
#     echo "  [package:install-all] - Install all packages"
#     echo "  [package:reinstall <package>] - Force reinstall package"
#     echo ""
#     echo -e "${GREEN}Package Information:${NC}"
#     echo "  [package:status <package>] - Check package status"
#     echo "  [package:info <package>] - Show detailed package info"
#     echo "  [package:search <query>] - Search packages"
#     echo ""
#     echo -e "${GREEN}System Management:${NC}"
#     echo "  [package:registry] - Show package registry"
#     echo "  [package:help] - Show this help"
#     echo ""
#     echo -e "${BLUE}📂 Categories:${NC}"
#     echo "  search - Search & Find Tools"
#     echo "  viewer - File Viewers & Displays"
#     echo "  utility - System Utilities"
#     echo "  ai - AI & Intelligence Tools"
#     echo ""
#     echo -e "${BLUE}📋 Examples:${NC}"
#     echo "  [package:list search] - List search tools"
#     echo "  [package:install ripgrep] - Install ripgrep"
#     echo "  [package:info bat] - Show bat information"
#     echo "  [package:search markdown] - Find markdown tools"
# }
# 
# # Main command interface
# main() {
#     # Initialize if needed
#     [[ ! -f "$MEMORY_DIR/packages/registry.json" ]] && initialize_package_manager
#     
#     case "${1:-help}" in
#         "shortcode")
#             # For integration with shortcode processor
#             process_package_shortcode "${@:2}"
#             ;;
#         *)
#             process_package_shortcode "$@"
#             ;;
#     esac
# }
# 
# # Initialize if called directly
# if [[ "${BASH_SOURCE[0]}" == "${0}" ]]; then
#     main "$@"
# fi
