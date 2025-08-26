#!/bin/bash
# uCORE POST Utility - Simple Data Storage
# Handles data creation and storage operations for uCORE compatibility

set -euo pipefail

# Get script directory
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
UDOS_ROOT="$(cd "$SCRIPT_DIR/../../.." && pwd)"

# Logging functions
log_info() { echo -e "\033[0;36m[INFO]\033[0m $1"; }
log_success() { echo -e "\033[0;32m[SUCCESS]\033[0m $1"; }
log_warning() { echo -e "\033[0;33m[WARNING]\033[0m $1"; }
log_error() { echo -e "\033[0;31m[ERROR]\033[0m $1"; }

# Post data to various destinations
post_data() {
    local target="$1"
    local key="$2"
    local value="$3"

    case "$target" in
        user)
            post_user_data "$key" "$value"
            ;;
        system)
            post_system_data "$key" "$value"
            ;;
        log)
            post_log_data "$key" "$value"
            ;;
        session)
            post_session_data "$key" "$value"
            ;;
        backup)
            post_backup_data "$key" "$value"
            ;;
        *)
            log_error "Unknown target: $target"
            return 1
            ;;
    esac
}

# Post user data to sandbox
post_user_data() {
    local key="$1"
    local value="$2"
    local user_file="$UDOS_ROOT/sandbox/user.md"

    # Create user file if it doesn't exist
    if [ ! -f "$user_file" ]; then
        cat > "$user_file" << EOF
# User Profile

name:
email:
role: Tomb
location:
timezone:
created: $(date '+%Y-%m-%d')
last_login: $(date '+%Y-%m-%d %H:%M:%S')
EOF
    fi

    # Update or add the key-value pair
    if grep -q "^$key:" "$user_file"; then
        # Update existing key
        sed -i.bak "s/^$key:.*/$key: $value/" "$user_file" && rm -f "$user_file.bak"
    else
        # Add new key
        echo "$key: $value" >> "$user_file"
    fi

    log_success "Updated user data: $key = $value"
}

# Post system data
post_system_data() {
    local key="$1"
    local value="$2"
    local system_file="$UDOS_ROOT/uMEMORY/system/system.json"

    # Create system file if it doesn't exist
    if [ ! -f "$system_file" ]; then
        mkdir -p "$(dirname "$system_file")"
        echo '{}' > "$system_file"
    fi

    # Update JSON using jq if available, otherwise simple append
    if command -v jq >/dev/null 2>&1; then
        local temp_file=$(mktemp)
        jq ".$key = \"$value\"" "$system_file" > "$temp_file" && mv "$temp_file" "$system_file"
    else
        log_warning "jq not available, using simple storage"
        echo "$key=$value" >> "$system_file.txt"
    fi

    log_success "Updated system data: $key = $value"
}

# Post log data
post_log_data() {
    local level="$1"
    local message="$2"
    local log_file="$UDOS_ROOT/sandbox/logs/uCORE-$(date '+%Y%m%d').log"

    mkdir -p "$(dirname "$log_file")"

    local timestamp=$(date '+%Y-%m-%d %H:%M:%S')
    echo "[$timestamp] [$level] $message" >> "$log_file"

    log_info "Logged: [$level] $message"
}

# Post session data
post_session_data() {
    local key="$1"
    local value="$2"
    local session_file="$UDOS_ROOT/sandbox/sessions/current-session.json"

    mkdir -p "$(dirname "$session_file")"

    # Create session file if it doesn't exist
    if [ ! -f "$session_file" ]; then
        echo '{"created": "'$(date -Iseconds)'"}' > "$session_file"
    fi

    # Update session data
    if command -v jq >/dev/null 2>&1; then
        local temp_file=$(mktemp)
        jq ".$key = \"$value\" | .last_updated = \"$(date -Iseconds)\"" "$session_file" > "$temp_file" && mv "$temp_file" "$session_file"
    else
        echo "$key=$value" >> "$session_file.txt"
    fi

    log_success "Updated session data: $key = $value"
}

# Post backup data
post_backup_data() {
    local backup_name="$1"
    local source_path="$2"
    local backup_dir="$UDOS_ROOT/backup"

    mkdir -p "$backup_dir"

    local timestamp=$(date '+%Y%m%d_%H%M%S')
    local backup_file="$backup_dir/${backup_name}-${timestamp}.tar.gz"

    if [ -d "$source_path" || -f "$source_path" ]; then
        tar -czf "$backup_file" -C "$(dirname "$source_path")" "$(basename "$source_path")"
        log_success "Backup created: $backup_file"
    else
        log_error "Source path not found: $source_path"
        return 1
    fi
}

# Create file with content
create_file() {
    local file_path="$1"
    local content="$2"

    mkdir -p "$(dirname "$file_path")"
    echo "$content" > "$file_path"

    log_success "Created file: $file_path"
}

# Show usage
show_usage() {
    echo "Usage: post <target> <key> <value>"
    echo "       post create <file_path> <content>"
    echo ""
    echo "Targets:"
    echo "  user        User data in sandbox"
    echo "  system      System configuration"
    echo "  log         Log entry"
    echo "  session     Session data"
    echo "  backup      Create backup"
    echo ""
    echo "Examples:"
    echo "  post user name 'John Doe'"
    echo "  post system version '1.0.4.1'"
    echo "  post log INFO 'System started'"
    echo "  post session last_action 'login'"
    echo "  post backup sandbox_backup ./sandbox"
    echo "  post create ./sandbox/test.txt 'Hello World'"
}

# Main execution
main() {
    if [ $# -eq 0 ]; then
        show_usage
        return 1
    fi

    case "$1" in
        help|--help|-h)
            show_usage
            ;;
        create)
            if [ $# -lt 3 ]; then
                log_error "create requires file_path and content"
                return 1
            fi
            create_file "$2" "$3"
            ;;
        *)
            if [ $# -lt 3 ]; then
                log_error "post requires target, key, and value"
                return 1
            fi
            post_data "$@"
            ;;
    esac
}

# Run if executed directly
if [ "${BASH_SOURCE[0]}" == "${0}" ]; then
    main "$@"
fi
