#!/bin/bash
#
# GitHub SSH Setup Script
# ========================
# Generates SSH keys for GitHub authentication (local machine only)
# Stores keys in ~/.ssh/ following system standards
# Never commits keys to git repository
#
# Usage:
#   ./setup_github_ssh.sh              # Interactive mode (recommended)
#   ./setup_github_ssh.sh --auto       # Auto-detect defaults
#   ./setup_github_ssh.sh --help       # Show help
#

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Configuration
SSH_DIR="$HOME/.ssh"
DEFAULT_KEY_NAME="id_ed25519_github"
DEFAULT_COMMENT="github@$(hostname)"

# Functions
print_header() {
    echo -e "\n${BLUE}═══════════════════════════════════════════════════════════${NC}"
    echo -e "${BLUE}$1${NC}"
    echo -e "${BLUE}═══════════════════════════════════════════════════════════${NC}\n"
}

print_success() {
    echo -e "${GREEN}✓ $1${NC}"
}

print_info() {
    echo -e "${BLUE}ℹ $1${NC}"
}

print_warning() {
    echo -e "${YELLOW}⚠ $1${NC}"
}

print_error() {
    echo -e "${RED}✗ $1${NC}"
}

show_help() {
    cat << 'EOF'
GitHub SSH Setup Script
=======================

Generate and manage SSH keys for GitHub authentication.
Keys are stored locally in ~/.ssh/ (never committed to git).

USAGE:
  ./setup_github_ssh.sh              # Interactive setup (recommended)
  ./setup_github_ssh.sh --auto       # Auto-detect with defaults
  ./setup_github_ssh.sh --help       # Show this help
  ./setup_github_ssh.sh --status     # Check current SSH setup
  ./setup_github_ssh.sh --regenerate # Generate new key pair

OPTIONS:
  -h, --help        Show this help message
  -a, --auto        Use default values (non-interactive)
  -s, --status      Check SSH key status
  -r, --regenerate  Generate new key (will backup old one)
  -t, --type        Key type (ed25519 or rsa, default: ed25519)
  -n, --name        Key filename (default: id_ed25519_github)
  -e, --email       GitHub email (used in key comment)

EXAMPLES:
  # Interactive setup
  $ ./setup_github_ssh.sh

  # Auto setup with defaults
  $ ./setup_github_ssh.sh --auto

  # Check status
  $ ./setup_github_ssh.sh --status

  # Generate RSA key instead
  $ ./setup_github_ssh.sh --type rsa

KEY LOCATIONS:
  Private key: ~/.ssh/id_ed25519_github
  Public key:  ~/.ssh/id_ed25519_github.pub

NEXT STEPS AFTER SETUP:
  1. View your public key
  2. Add it to GitHub (Settings > SSH and GPG keys > New SSH key)
  3. Test connection: ssh -T git@github.com
  4. Configure git to use the key

EOF
}

check_status() {
    print_header "SSH Key Status"

    if [[ ! -d "$SSH_DIR" ]]; then
        print_error "SSH directory not found: $SSH_DIR"
        return 1
    fi

    if [[ -f "$SSH_DIR/$DEFAULT_KEY_NAME" ]]; then
        print_success "GitHub SSH key exists: $SSH_DIR/$DEFAULT_KEY_NAME"

        # Show key type
        key_type=$(ssh-keygen -l -f "$SSH_DIR/$DEFAULT_KEY_NAME" 2>/dev/null | awk '{print $4}')
        print_info "Key type: $key_type"

        # Show fingerprint
        fingerprint=$(ssh-keygen -l -f "$SSH_DIR/$DEFAULT_KEY_NAME" 2>/dev/null | awk '{print $2}')
        print_info "Fingerprint: $fingerprint"

        # Show public key path
        print_info "Public key: $SSH_DIR/$DEFAULT_KEY_NAME.pub"

        echo ""
        print_info "To view your public key:"
        echo "  cat $SSH_DIR/$DEFAULT_KEY_NAME.pub"
        echo ""

        print_info "To test GitHub connection:"
        echo "  ssh -T git@github.com"

        return 0
    else
        print_warning "No GitHub SSH key found"
        print_info "Run without --status flag to generate one"
        return 1
    fi
}

generate_key() {
    local key_type=$1
    local key_name=$2
    local key_comment=$3

    print_header "Generating SSH Key"

    # Validate key name
    local key_path="$SSH_DIR/$key_name"
    if [[ -f "$key_path" ]]; then
        print_warning "Key already exists: $key_path"
        echo -n "Overwrite? (y/N) "
        read -r response
        if [[ "$response" != "y" && "$response" != "Y" ]]; then
            print_info "Cancelled"
            return 1
        fi

        # Backup existing key
        local backup_path="${key_path}.backup-$(date +%Y%m%d-%H%M%S)"
        cp "$key_path" "$backup_path"
        print_info "Backed up existing key to: $backup_path"
    fi

    # Create SSH directory if needed
    mkdir -p "$SSH_DIR"
    chmod 700 "$SSH_DIR"

    # Generate key
    print_info "Generating $key_type key..."
    echo ""

    if [[ "$key_type" == "ed25519" ]]; then
        ssh-keygen -t ed25519 -f "$key_path" -C "$key_comment" -N ""
    elif [[ "$key_type" == "rsa" ]]; then
        ssh-keygen -t rsa -b 4096 -f "$key_path" -C "$key_comment" -N ""
    else
        print_error "Invalid key type: $key_type"
        return 1
    fi

    # Set proper permissions
    chmod 600 "$key_path"
    chmod 644 "${key_path}.pub"

    print_success "SSH key generated successfully!"
    echo ""
    print_info "Key location: $key_path"
    print_info "Public key: ${key_path}.pub"

    return 0
}

show_public_key() {
    local key_path="$SSH_DIR/$DEFAULT_KEY_NAME.pub"

    if [[ ! -f "$key_path" ]]; then
        print_error "Public key not found: $key_path"
        return 1
    fi

    print_header "Your GitHub SSH Public Key"
    print_info "Copy this and add it to https://github.com/settings/keys"
    echo ""
    cat "$key_path"
    echo ""
    print_info "To copy to clipboard (macOS):"
    echo "  cat $key_path | pbcopy"
    print_info "To copy to clipboard (Linux with xclip):"
    echo "  cat $key_path | xclip -selection clipboard"
}

configure_git() {
    print_header "Configuring Git to Use SSH Key"

    local key_path="$SSH_DIR/$DEFAULT_KEY_NAME"

    # Check if git is available
    if ! command -v git &> /dev/null; then
        print_error "Git not found. Please install git first."
        return 1
    fi

    # Configure git to use the SSH key
    print_info "Setting git core.sshCommand..."
    git config --global core.sshCommand "ssh -i $key_path"
    print_success "Git configured to use: $key_path"

    # Test connection
    echo ""
    print_info "Testing GitHub SSH connection..."
    if ssh -i "$key_path" -T git@github.com 2>&1 | grep -q "successfully authenticated"; then
        print_success "SSH connection to GitHub successful!"
    else
        print_warning "SSH connection test inconclusive"
        print_info "Try: ssh -T git@github.com"
    fi
}

test_connection() {
    print_header "Testing SSH Connection"

    local key_path="$SSH_DIR/$DEFAULT_KEY_NAME"

    if [[ ! -f "$key_path" ]]; then
        print_error "SSH key not found: $key_path"
        return 1
    fi

    print_info "Testing SSH connection to GitHub..."
    echo ""

    if ssh -i "$key_path" -T git@github.com 2>&1; then
        echo ""
        print_success "SSH connection working!"
    else
        echo ""
        print_warning "SSH connection failed"
        print_info "Make sure your public key is added to GitHub"
        print_info "https://github.com/settings/keys"
    fi
}

main() {
    # Parse arguments
    while [[ $# -gt 0 ]]; do
        case "$1" in
            -h|--help)
                show_help
                exit 0
                ;;
            -s|--status)
                check_status
                exit $?
                ;;
            -a|--auto)
                AUTO_MODE=true
                shift
                ;;
            -r|--regenerate)
                REGENERATE=true
                shift
                ;;
            -t|--type)
                KEY_TYPE="$2"
                shift 2
                ;;
            -n|--name)
                KEY_NAME="$2"
                shift 2
                ;;
            -e|--email)
                EMAIL="$2"
                shift 2
                ;;
            *)
                print_error "Unknown option: $1"
                show_help
                exit 1
                ;;
        esac
    done

    # Set defaults
    KEY_TYPE="${KEY_TYPE:-ed25519}"
    KEY_NAME="${KEY_NAME:-$DEFAULT_KEY_NAME}"
    EMAIL="${EMAIL:-$DEFAULT_COMMENT}"

    print_header "GitHub SSH Setup"

    # Check if key already exists
    if [[ -f "$SSH_DIR/$KEY_NAME" ]] && [[ "$REGENERATE" != "true" ]]; then
        print_success "SSH key already exists: $SSH_DIR/$KEY_NAME"
        echo ""

        # Show options
        echo "Choose an action:"
        echo "  1) View public key"
        echo "  2) Check status"
        echo "  3) Test connection"
        echo "  4) Regenerate key (backup existing)"
        echo "  5) Configure git"
        echo "  6) Exit"
        echo ""

        if [[ "$AUTO_MODE" == "true" ]]; then
            print_info "Auto mode: exiting (key already exists)"
            exit 0
        fi

        echo -n "Select (1-6): "
        read -r choice

        case "$choice" in
            1) show_public_key ;;
            2) check_status ;;
            3) test_connection ;;
            4) generate_key "$KEY_TYPE" "$KEY_NAME" "$EMAIL" ;;
            5) configure_git ;;
            6) echo "Cancelled"; exit 0 ;;
            *) print_error "Invalid choice"; exit 1 ;;
        esac
    else
        # Interactive mode
        if [[ "$AUTO_MODE" != "true" ]]; then
            echo "This script will:"
            echo "  1. Generate an SSH key pair ($KEY_TYPE)"
            echo "  2. Store it in: $SSH_DIR/$KEY_NAME"
            echo "  3. Provide instructions for adding to GitHub"
            echo ""

            echo -n "Email for SSH key comment [$EMAIL]: "
            read -r input
            [[ -n "$input" ]] && EMAIL="$input"

            echo ""
            echo "Key type options: ed25519 (faster, recommended) or rsa (wider compatibility)"
            echo -n "Key type [$KEY_TYPE]: "
            read -r input
            [[ -n "$input" ]] && KEY_TYPE="$input"
        fi

        # Generate the key
        if generate_key "$KEY_TYPE" "$KEY_NAME" "$EMAIL"; then
            echo ""
            show_public_key
            echo ""

            # Ask if user wants to configure git
            if [[ "$AUTO_MODE" != "true" ]]; then
                echo -n "Configure git to use this key? (Y/n) "
                read -r response
                if [[ "$response" != "n" && "$response" != "N" ]]; then
                    configure_git
                fi
            else
                configure_git
            fi

            print_success "Setup complete!"
            echo ""
            print_info "Next steps:"
            echo "  1. Copy your public key (shown above)"
            echo "  2. Add it to GitHub: https://github.com/settings/keys"
            echo "  3. Test: ssh -T git@github.com"
        else
            print_error "Failed to generate SSH key"
            exit 1
        fi
    fi
}

# Run main function
main "$@"
