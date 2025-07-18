#!/bin/bash
# ARCHIVED SCRIPT - Use consolidated version instead
# Original: packages/manager-enhanced.sh
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
# # uDOS Enhanced Package Manager v2.0.0
# # Description: Shortcode-integrated package management with uTemplate support
# 
# set -euo pipefail
# 
# # Check bash version
# if [[ ${BASH_VERSION%%.*} -lt 4 ]]; then
#     echo "❌ This script requires Bash 4.0 or higher"
#     echo "Current version: $BASH_VERSION"
#     echo "Please upgrade bash or use the simple package manager instead"
#     exit 1
# fi
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
# # Package database - Enhanced with metadata
# declare -A PACKAGES
# PACKAGES["ripgrep"]="rg|Fast text search|https://github.com/BurntSushi/ripgrep|search,utility"
# PACKAGES["bat"]="bat|Syntax-highlighted file viewer|https://github.com/sharkdp/bat|viewer,utility"
# PACKAGES["fd"]="fd|Fast file finder|https://github.com/sharkdp/fd|finder,utility"
# PACKAGES["glow"]="glow|Terminal markdown renderer|https://github.com/charmbracelet/glow|markdown,viewer"
# PACKAGES["jq"]="jq|JSON processor|https://github.com/jqlang/jq|json,processor"
# PACKAGES["fzf"]="fzf|Fuzzy finder|https://github.com/junegunn/fzf|finder,interactive"
# PACKAGES["gemini"]="gemini|Google Gemini CLI|https://github.com/google/generative-ai|ai,assistant"
# PACKAGES["eza"]="eza|Modern ls replacement|https://github.com/eza-community/eza|listing,utility"
# PACKAGES["zoxide"]="zoxide|Smart cd command|https://github.com/ajeetdsouza/zoxide|navigation,utility"
# PACKAGES["delta"]="delta|Better diff viewer|https://github.com/dandavison/delta|diff,utility"
# 
# # Package categories
# declare -A CATEGORIES
# CATEGORIES["search"]="🔍 Search & Find Tools"
# CATEGORIES["viewer"]="👀 File Viewers & Displays"
# CATEGORIES["utility"]="🛠️ System Utilities"
# CATEGORIES["ai"]="🤖 AI & Intelligence Tools"
# CATEGORIES["development"]="💻 Development Tools"
# CATEGORIES["navigation"]="🧭 Navigation & Movement"
# CATEGORIES["interactive"]="🎮 Interactive Tools"
# CATEGORIES["markdown"]="📝 Markdown Tools"
# CATEGORIES["json"]="📋 JSON Processing"
# CATEGORIES["finder"]="🔍 File Finding"
# CATEGORIES["listing"]="📂 Directory Listing"
# CATEGORIES["diff"]="🔄 Diff & Comparison"
# 
# # Initialize package manager
# initialize_package_manager() {
#     info_log "Initializing uDOS Package Manager v2.0.0"
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
# # Create package registry with metadata
# create_package_registry() {
#     local registry_file="$MEMORY_DIR/packages/registry.json"
#     
#     echo "{" > "$registry_file"
#     echo "  \"version\": \"2.0.0\"," >> "$registry_file"
#     echo "  \"updated\": \"$(date -Iseconds)\"," >> "$registry_file"
#     echo "  \"packages\": {" >> "$registry_file"
#     
#     local first=true
#     for package in "${!PACKAGES[@]}"; do
#         [[ "$first" == "false" ]] && echo "," >> "$registry_file"
#         first=false
#         
#         IFS='|' read -r cmd desc url tags <<< "${PACKAGES[$package]}"
#         
#         cat >> "$registry_file" << EOF
#     "$package": {
#       "command": "$cmd",
#       "description": "$desc",
#       "homepage": "$url",
#       "tags": ["$(echo "$tags" | sed 's/,/", "/g')"],
#       "installer": "install-$package.sh",
#       "status": "$(get_package_status "$package")",
#       "version": "$(get_package_version "$cmd" 2>/dev/null || echo 'unknown')"
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
# # Get package status
# get_package_status() {
#     local package="$1"
#     IFS='|' read -r cmd _ _ _ <<< "${PACKAGES[$package]}"
#     
#     if command -v "$cmd" >/dev/null 2>&1; then
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
#         "rg") rg --version | head -n1 | awk '{print $2}' ;;
#         "bat") bat --version | head -n1 | awk '{print $2}' ;;
#         "fd") fd --version | head -n1 | awk '{print $2}' ;;
#         "glow") glow --version | head -n1 | awk '{print $3}' ;;
#         "jq") jq --version | sed 's/jq-//' ;;
#         "fzf") fzf --version | awk '{print $1}' ;;
#         *) echo "unknown" ;;
#     esac
# }
# 
# # List packages with enhanced display
# list_packages() {
#     local category_filter="${1:-all}"
#     local status_filter="${2:-all}"
#     
#     echo -e "${PURPLE}📦 uDOS Package Manager v2.0.0${NC}"
#     echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
#     echo ""
#     
#     if [[ "$category_filter" != "all" ]]; then
#         echo -e "${CYAN}📋 Category: ${CATEGORIES[$category_filter]:-$category_filter}${NC}"
#         echo ""
#     fi
#     
#     # Group packages by category
#     declare -A category_packages
#     
#     for package in "${!PACKAGES[@]}"; do
#         IFS='|' read -r cmd desc url tags <<< "${PACKAGES[$package]}"
#         local status=$(get_package_status "$package")
#         
#         # Apply status filter
#         if [[ "$status_filter" != "all" && "$status" != "$status_filter" ]]; then
#             continue
#         fi
#         
#         # Apply category filter
#         if [[ "$category_filter" != "all" ]]; then
#             if [[ ! "$tags" =~ $category_filter ]]; then
#                 continue
#             fi
#         fi
#         
#         # Get primary category
#         local primary_category=$(echo "$tags" | cut -d',' -f1)
#         category_packages["$primary_category"]+="$package|$cmd|$desc|$status "
#     done
#     
#     # Display packages by category
#     for category in "${!category_packages[@]}"; do
#         echo -e "${BLUE}${CATEGORIES[$category]:-📦 $category}${NC}"
#         echo ""
#         
#         for entry in ${category_packages["$category"]}; do
#             IFS='|' read -r pkg cmd desc status <<< "$entry"
#             [[ -z "$pkg" ]] && continue
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
#     done
#     
#     # Show statistics
#     local total=$(echo "${!PACKAGES[@]}" | wc -w)
#     local installed=0
#     for package in "${!PACKAGES[@]}"; do
#         [[ "$(get_package_status "$package")" == "installed" ]] && ((installed++))
#     done
#     
#     echo -e "${CYAN}📊 Statistics:${NC}"
#     echo "  Total packages: $total"
#     echo "  Installed: $installed"
#     echo "  Available: $((total - installed))"
# }
# 
# # Install package with enhanced error handling
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
#     if [[ ! "${PACKAGES[$package]+exists}" ]]; then
#         error_log "Unknown package: $package"
#         suggest_similar_packages "$package"
#         return 1
#     fi
#     
#     IFS='|' read -r cmd desc url tags <<< "${PACKAGES[$package]}"
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
#         # Update package registry
#         update_package_status "$package" "installed"
#         
#         # Create configuration from template if available
#         create_package_config "$package"
#         
#         return 0
#     else
#         error_log "Failed to install $package"
#         echo "📋 Installation log: $install_log"
#         return 1
#     fi
# }
# 
# # Suggest similar packages
# suggest_similar_packages() {
#     local query="$1"
#     echo -e "${YELLOW}💡 Did you mean one of these?${NC}"
#     
#     for package in "${!PACKAGES[@]}"; do
#         if [[ "$package" =~ $query ]] || [[ "${PACKAGES[$package]}" =~ $query ]]; then
#             IFS='|' read -r cmd desc _ _ <<< "${PACKAGES[$package]}"
#             echo "  • $package - $desc"
#         fi
#     done
# }
# 
# # Update package status in registry
# update_package_status() {
#     local package="$1"
#     local status="$2"
#     
#     local status_file="$MEMORY_DIR/packages/installed/$package.json"
#     cat > "$status_file" << EOF
# {
#   "package": "$package",
#   "status": "$status",
#   "installed_at": "$(date -Iseconds)",
#   "version": "$(get_package_version "${PACKAGES[$package]%%|*}")",
#   "installer_version": "2.0.0"
# }
# EOF
# }
# 
# # Create package configuration from template
# create_package_config() {
#     local package="$1"
#     local config_template="$TEMPLATE_DIR/package-config-$package.md"
#     local config_file="$MEMORY_DIR/packages/configs/$package.md"
#     
#     if [[ -f "$config_template" ]]; then
#         info_log "Creating configuration from template"
#         cp "$config_template" "$config_file"
#         
#         # Process template variables
#         if [[ -f "$UHOME/uCode/vb-template-processor.sh" ]]; then
#             bash "$UHOME/uCode/vb-template-processor.sh" process "$config_file"
#         fi
#     fi
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
#     if [[ ! "${PACKAGES[$package]+exists}" ]]; then
#         error_log "Unknown package: $package"
#         return 1
#     fi
#     
#     IFS='|' read -r cmd desc url tags <<< "${PACKAGES[$package]}"
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
#         
#         # Show installation details if available
#         local status_file="$MEMORY_DIR/packages/installed/$package.json"
#         if [[ -f "$status_file" ]] && command -v jq >/dev/null 2>&1; then
#             local installed_at=$(jq -r '.installed_at' "$status_file")
#             echo "  Installed: $installed_at"
#         fi
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
#         echo "  [package:config $package] - Show configuration"
#     else
#         echo "  [package:install $package] - Install package"
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
#         "update")
#             update_package "$1"
#             ;;
#         "remove")
#             remove_package "$1"
#             ;;
#         "search")
#             search_packages "$1"
#             ;;
#         "categories")
#             list_categories
#             ;;
#         "registry")
#             show_registry
#             ;;
#         *)
#             error_log "Unknown package action: $action"
#             show_package_help
#             return 1
#             ;;
#     esac
# }
# 
# # Install all packages
# install_all_packages() {
#     echo -e "${PURPLE}🚀 Installing All uDOS Packages${NC}"
#     echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
#     echo ""
#     
#     local total=${#PACKAGES[@]}
#     local installed=0
#     local failed=0
#     
#     for package in "${!PACKAGES[@]}"; do
#         echo "────────────────────────────────────────"
#         if install_package "$package"; then
#             ((installed++))
#         else
#             ((failed++))
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
#     for package in "${!PACKAGES[@]}"; do
#         IFS='|' read -r cmd desc url tags <<< "${PACKAGES[$package]}"
#         
#         if [[ "$package" =~ $query ]] || [[ "$desc" =~ $query ]] || [[ "$tags" =~ $query ]]; then
#             local status=$(get_package_status "$package")
#             local status_icon="⏳"
#             [[ "$status" == "installed" ]] && status_icon="✅"
#             
#             echo -e "${BLUE}$package${NC} $status_icon"
#             echo "  $desc"
#             echo "  Tags: $tags"
#             echo ""
#             ((found++))
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
# # List categories
# list_categories() {
#     echo -e "${PURPLE}📂 Package Categories${NC}"
#     echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
#     echo ""
#     
#     for category in "${!CATEGORIES[@]}"; do
#         echo -e "${BLUE}${CATEGORIES[$category]}${NC}"
#         echo "  Shortcode: [package:list $category]"
#         
#         # Count packages in category
#         local count=0
#         for package in "${!PACKAGES[@]}"; do
#             IFS='|' read -r _ _ _ tags <<< "${PACKAGES[$package]}"
#             [[ "$tags" =~ $category ]] && ((count++))
#         done
#         echo "  Packages: $count"
#         echo ""
#     done
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
#     echo -e "${PURPLE}📦 uDOS Package Manager v2.0.0${NC}"
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
#     echo "  [package:categories] - List all categories"
#     echo ""
#     echo -e "${GREEN}System Management:${NC}"
#     echo "  [package:registry] - Show package registry"
#     echo "  [package:update <package>] - Update package"
#     echo "  [package:remove <package>] - Remove package"
#     echo ""
#     echo -e "${BLUE}📂 Categories:${NC}"
#     for category in "${!CATEGORIES[@]}"; do
#         echo "  $category - ${CATEGORIES[$category]}"
#     done
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
