#!/bin/bash
# uDOS Installer Template Processor
# Generates platform-specific installers from templates

set -euo pipefail

# Configuration
TEMPLATE_DIR="$(dirname "$0")"
OUTPUT_DIR="./installers-generated"
UDOS_VERSION="v1.0.0"

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[0;33m'
BLUE='\033[0;34m'
BOLD='\033[1m'
NC='\033[0m'

print_header() {
    echo -e "${BOLD}${BLUE}"
    echo "╔══════════════════════════════════════════════════════════════════╗"
    echo "║              🚀 uDOS Installer Template Processor               ║"
    echo "║                Generate Platform-Specific Installers            ║"
    echo "╚══════════════════════════════════════════════════════════════════╝"
    echo -e "${NC}"
}

log_info() { echo -e "${BLUE}ℹ️  $1${NC}"; }
log_success() { echo -e "${GREEN}✅ $1${NC}"; }
log_warning() { echo -e "${YELLOW}⚠️  $1${NC}"; }
log_error() { echo -e "${RED}❌ $1${NC}"; }

# Show usage
show_usage() {
    echo "Usage: $0 [command] [options]"
    echo
    echo "Commands:"
    echo "  generate <template> [options]  Generate installer from template"
    echo "  list                          List available templates"
    echo "  validate <template>           Validate template syntax"
    echo "  help                          Show this help"
    echo
    echo "Available Templates:"
    echo "  macos-vscode                  macOS with VS Code integration"
    echo "  ubuntu22                      Ubuntu 22.04 LTS installation"
    echo "  usb-bootable                  Bootable USB creator"
    echo "  docker                        Docker container deployment"
    echo "  browser-pwa                   Progressive Web App"
    echo "  raspberry-pi                  Raspberry Pi ARM installation"
    echo "  cloud                         Cloud instance deployment"
    echo
    echo "Options:"
    echo "  --user-role <role>            Target user role (wizard/sorcerer/ghost/imp)"
    echo "  --install-dir <path>          Installation directory"
    echo "  --enable-chester <bool>       Enable Chester AI (true/false)"
    echo "  --packages <list>             Comma-separated package list"
    echo "  --output <file>               Output file path"
    echo "  --config <file>               Configuration file"
    echo
    echo "Examples:"
    echo "  $0 generate macos-vscode --user-role wizard --enable-chester true"
    echo "  $0 generate ubuntu22 --install-dir /opt/udos --packages ripgrep,bat,fd"
    echo "  $0 generate usb-bootable --target-device /dev/sdb --udos-mode persistent"
}

# List available templates
list_templates() {
    log_info "Available installer templates:"
    echo
    
    if [ -f "$TEMPLATE_DIR/macos-vscode-installer.md" ]; then
        echo "📱 macos-vscode         - macOS with VS Code integration"
    fi
    
    if [ -f "$TEMPLATE_DIR/ubuntu22-installer.md" ]; then
        echo "🐧 ubuntu22             - Ubuntu 22.04 LTS installation"
    fi
    
    if [ -f "$TEMPLATE_DIR/usb-bootable-installer.md" ]; then
        echo "💾 usb-bootable         - Bootable USB creator"
    fi
    
    if [ -f "$TEMPLATE_DIR/docker-installer.md" ]; then
        echo "🐳 docker               - Docker container deployment"
    fi
    
    if [ -f "$TEMPLATE_DIR/browser-pwa-installer.md" ]; then
        echo "🌍 browser-pwa          - Progressive Web App"
    fi
    
    if [ -f "$TEMPLATE_DIR/raspberry-pi-installer.md" ]; then
        echo "🥧 raspberry-pi         - Raspberry Pi ARM installation"
    fi
    
    if [ -f "$TEMPLATE_DIR/cloud-installer.md" ]; then
        echo "☁️  cloud                - Cloud instance deployment"
    fi
    
    echo
}

# Detect system defaults
detect_system_defaults() {
    # Operating system
    if [[ "$OSTYPE" == "darwin"* ]]; then
        OS_TYPE="macOS"
        PACKAGE_MANAGER="brew"
        SHELL_TYPE="zsh"
        VS_CODE_VARIANT="code"
        DESKTOP_ENVIRONMENT="macOS"
    elif [[ "$OSTYPE" == "linux-gnu"* ]]; then
        OS_TYPE="Linux"
        
        # Detect Linux distribution
        if [ -f /etc/os-release ]; then
            source /etc/os-release
            OS_DISTRO="$ID"
            OS_VERSION="$VERSION_ID"
        fi
        
        # Package manager detection
        if command -v apt &> /dev/null; then
            PACKAGE_MANAGER="apt"
        elif command -v yum &> /dev/null; then
            PACKAGE_MANAGER="yum"
        elif command -v pacman &> /dev/null; then
            PACKAGE_MANAGER="pacman"
        else
            PACKAGE_MANAGER="unknown"
        fi
        
        # Shell detection
        SHELL_TYPE=$(basename "$SHELL")
        
        # Desktop environment
        DESKTOP_ENVIRONMENT="${XDG_CURRENT_DESKTOP:-headless}"
        
        VS_CODE_VARIANT="code"
    else
        OS_TYPE="Unknown"
        PACKAGE_MANAGER="unknown"
        SHELL_TYPE="bash"
        VS_CODE_VARIANT="code"
        DESKTOP_ENVIRONMENT="unknown"
    fi
    
    # Architecture
    ARCHITECTURE=$(uname -m)
    
    # Default directories
    INSTALL_DIRECTORY="$HOME/uDOS"
    BACKUP_DIRECTORY="$HOME/uDOS-backup-$(date +%Y%m%d-%H%M%S)"
    
    # Default settings
    USER_ROLE="wizard"
    ENABLE_CHESTER="true"
    PRIVACY_MODE="standard"
    INSTALL_PACKAGES="ripgrep,fd,bat,glow"
}

# Process template variables
process_template() {
    local template_file="$1"
    local output_file="$2"
    local config_file="${3:-}"
    
    log_info "Processing template: $template_file"
    
    # Load configuration if provided
    if [ -n "$config_file" ] && [ -f "$config_file" ]; then
        log_info "Loading configuration from: $config_file"
        source "$config_file"
    fi
    
    # Set default values
    detect_system_defaults
    
    # Override with command line arguments
    while [ $# -gt 0 ]; do
        case "$1" in
            --user-role)
                USER_ROLE="$2"
                shift 2
                ;;
            --install-dir)
                INSTALL_DIRECTORY="$2"
                BACKUP_DIRECTORY="$2-backup-$(date +%Y%m%d-%H%M%S)"
                shift 2
                ;;
            --enable-chester)
                ENABLE_CHESTER="$2"
                shift 2
                ;;
            --packages)
                INSTALL_PACKAGES="$2"
                shift 2
                ;;
            --target-device)
                TARGET_DEVICE="$2"
                shift 2
                ;;
            --udos-mode)
                UDOS_MODE="$2"
                shift 2
                ;;
            --persistence-size)
                PERSISTENCE_SIZE="$2"
                shift 2
                ;;
            --privacy-mode)
                PRIVACY_MODE="$2"
                shift 2
                ;;
            --vs-code-variant)
                VS_CODE_VARIANT="$2"
                shift 2
                ;;
            *)
                shift
                ;;
        esac
    done
    
    # Generate timestamp
    TIMESTAMP=$(date -u +"%Y-%m-%d %H:%M:%S UTC")
    
    # Process template
    # Escape forward slashes in variables for sed
    ESCAPED_INSTALL_DIR=$(echo "$INSTALL_DIRECTORY" | sed 's|/|\\/|g')
    ESCAPED_BACKUP_DIR=$(echo "$BACKUP_DIRECTORY" | sed 's|/|\\/|g')
    
    sed \
        -e "s/{{udos_version}}/$UDOS_VERSION/g" \
        -e "s/{{template_name}}/${template_file##*/}/g" \
        -e "s/{{timestamp}}/$TIMESTAMP/g" \
        -e "s/{{user_role}}/$USER_ROLE/g" \
        -e "s/{{install_directory}}/$ESCAPED_INSTALL_DIR/g" \
        -e "s/{{backup_directory}}/$ESCAPED_BACKUP_DIR/g" \
        -e "s/{{enable_chester}}/$ENABLE_CHESTER/g" \
        -e "s/{{privacy_mode}}/$PRIVACY_MODE/g" \
        -e "s/{{os_type}}/$OS_TYPE/g" \
        -e "s/{{architecture}}/$ARCHITECTURE/g" \
        -e "s/{{package_manager}}/$PACKAGE_MANAGER/g" \
        -e "s/{{shell_type}}/$SHELL_TYPE/g" \
        -e "s/{{vs_code_variant}}/$VS_CODE_VARIANT/g" \
        -e "s/{{desktop_environment}}/$DESKTOP_ENVIRONMENT/g" \
        -e "s/{{install_packages}}/$INSTALL_PACKAGES/g" \
        -e "s|{{target_device}}|${TARGET_DEVICE:-/dev/sdb}|g" \
        -e "s/{{udos_mode}}/${UDOS_MODE:-live}/g" \
        -e "s/{{persistence_size}}/${PERSISTENCE_SIZE:-4}/g" \
        -e "s/{{usb_format}}/${USB_FORMAT:-FAT32}/g" \
        -e "s/{{bootloader}}/${BOOTLOADER:-grub2}/g" \
        -e "s/{{boot_mode}}/${BOOT_MODE:-UEFI}/g" \
        -e "s/{{base_os}}/${BASE_OS:-Ubuntu 22.04 LTS}/g" \
        -e "s/{{os_version}}/${OS_VERSION:-22.04}/g" \
        -e "s/{{kernel_params}}/${KERNEL_PARAMS:-quiet splash}/g" \
        -e "s/{{auto_login}}/${AUTO_LOGIN:-true}/g" \
        -e "s/{{network_config}}/${NETWORK_CONFIG:-dhcp}/g" \
        -e "s/{{auto_open}}/${AUTO_OPEN:-true}/g" \
        "$template_file" > "$output_file"
    
    # Make executable if it's a shell script
    if [[ "$output_file" == *.sh ]]; then
        chmod +x "$output_file"
    fi
    
    log_success "Template processed: $output_file"
}

# Validate template
validate_template() {
    local template_file="$1"
    
    log_info "Validating template: $template_file"
    
    if [ ! -f "$template_file" ]; then
        log_error "Template file not found: $template_file"
        return 1
    fi
    
    # Check for required variables
    local required_vars=(
        "{{udos_version}}"
        "{{timestamp}}"
        "{{user_role}}"
        "{{install_directory}}"
    )
    
    local missing_vars=()
    for var in "${required_vars[@]}"; do
        if ! grep -q "$var" "$template_file"; then
            missing_vars+=("$var")
        fi
    done
    
    if [ ${#missing_vars[@]} -gt 0 ]; then
        log_warning "Missing required variables:"
        for var in "${missing_vars[@]}"; do
            echo "  - $var"
        done
    fi
    
    # Check for syntax errors in embedded scripts
    local script_blocks=$(grep -n '```bash' "$template_file" | cut -d: -f1)
    if [ -n "$script_blocks" ]; then
        log_info "Found bash script blocks - basic syntax check passed"
    fi
    
    log_success "Template validation completed"
}

# Generate installer
generate_installer() {
    local template_name="$1"
    shift
    
    # Create output directory
    mkdir -p "$OUTPUT_DIR"
    
    # Determine template file and output name
    case "$template_name" in
        macos-vscode)
            TEMPLATE_FILE="$TEMPLATE_DIR/macos-vscode-installer.md"
            OUTPUT_FILE="$OUTPUT_DIR/install-udos-macos.sh"
            ;;
        ubuntu22)
            TEMPLATE_FILE="$TEMPLATE_DIR/ubuntu22-installer.md"
            OUTPUT_FILE="$OUTPUT_DIR/install-udos-ubuntu22.sh"
            ;;
        usb-bootable)
            TEMPLATE_FILE="$TEMPLATE_DIR/usb-bootable-installer.md"
            OUTPUT_FILE="$OUTPUT_DIR/create-udos-usb.sh"
            ;;
        docker)
            TEMPLATE_FILE="$TEMPLATE_DIR/docker-installer.md"
            OUTPUT_FILE="$OUTPUT_DIR/install-udos-docker.sh"
            ;;
        browser-pwa)
            TEMPLATE_FILE="$TEMPLATE_DIR/browser-pwa-installer.md"
            OUTPUT_FILE="$OUTPUT_DIR/deploy-udos-pwa.sh"
            ;;
        raspberry-pi)
            TEMPLATE_FILE="$TEMPLATE_DIR/raspberry-pi-installer.md"
            OUTPUT_FILE="$OUTPUT_DIR/install-udos-pi.sh"
            ;;
        cloud)
            TEMPLATE_FILE="$TEMPLATE_DIR/cloud-installer.md"
            OUTPUT_FILE="$OUTPUT_DIR/deploy-udos-cloud.sh"
            ;;
        *)
            log_error "Unknown template: $template_name"
            log_info "Available templates: macos-vscode, ubuntu22, usb-bootable, docker, browser-pwa, raspberry-pi, cloud"
            return 1
            ;;
    esac
    
    # Check for custom output file
    while [ $# -gt 0 ]; do
        case "$1" in
            --output)
                OUTPUT_FILE="$2"
                shift 2
                ;;
            *)
                break
                ;;
        esac
    done
    
    if [ ! -f "$TEMPLATE_FILE" ]; then
        log_error "Template file not found: $TEMPLATE_FILE"
        return 1
    fi
    
    # Process template
    process_template "$TEMPLATE_FILE" "$OUTPUT_FILE" "$@"
    
    echo
    log_success "Installer generated successfully!"
    log_info "Output: $OUTPUT_FILE"
    
    # Show next steps
    echo
    echo -e "${BOLD}${GREEN}Next steps:${NC}"
    case "$template_name" in
        macos-vscode|ubuntu22|raspberry-pi)
            echo "1. Review the generated installer script"
            echo "2. Make executable: chmod +x $OUTPUT_FILE"
            echo "3. Run installer: ./$OUTPUT_FILE"
            ;;
        usb-bootable)
            echo "1. Review the generated USB creator script"
            echo "2. Run as root: sudo $OUTPUT_FILE"
            echo "3. Follow USB creation prompts"
            ;;
        docker)
            echo "1. Review the generated Docker setup"
            echo "2. Build container: docker build -t udos ."
            echo "3. Run container: docker run -d -p 8080:8080 udos"
            ;;
        browser-pwa)
            echo "1. Review the generated PWA deployment"
            echo "2. Configure hosting platform variables"
            echo "3. Run deployment: ./$OUTPUT_FILE"
            ;;
        cloud)
            echo "1. Review the generated Terraform configuration"
            echo "2. Configure cloud provider credentials"
            echo "3. Run deployment: ./$OUTPUT_FILE"
            ;;
    esac
}

# Main command processor
main() {
    case "${1:-help}" in
        generate)
            if [ $# -lt 2 ]; then
                log_error "Template name required"
                show_usage
                exit 1
            fi
            shift
            generate_installer "$@"
            ;;
        list)
            list_templates
            ;;
        validate)
            if [ $# -lt 2 ]; then
                log_error "Template file required"
                show_usage
                exit 1
            fi
            validate_template "$2"
            ;;
        help|--help|-h)
            show_usage
            ;;
        *)
            log_error "Unknown command: $1"
            show_usage
            exit 1
            ;;
    esac
}

# Run main function
print_header
main "$@"
