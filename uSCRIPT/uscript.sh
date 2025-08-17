#!/bin/bash
# uSCRIPT v1.3 - Production Script Library & Execution Engine
# Purpose: Execute and manage production-ready scripts across multiple languages
# Author: uDOS Team
# Version: 1.3.0

# Configuration
USCRIPT_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
CONFIG_DIR="$USCRIPT_ROOT/config"
LIBRARY_DIR="$USCRIPT_ROOT/library"
REGISTRY_DIR="$USCRIPT_ROOT/registry"
RUNTIME_DIR="$USCRIPT_ROOT/runtime"
LOGS_DIR="$RUNTIME_DIR/logs"
SANDBOX_DIR="$RUNTIME_DIR/sandbox"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
PURPLE='\033[0;35m'
CYAN='\033[0;36m'
NC='\033[0m' # No Color

# Logging function
log() {
    local level="$1"
    local message="$2"
    local timestamp=$(date '+%Y-%m-%d %H:%M:%S')
    echo "[$timestamp] [$level] $message" >> "$LOGS_DIR/uscript.log"
    
    case "$level" in
        "ERROR")   echo -e "${RED}[ERROR]${NC} $message" ;;
        "SUCCESS") echo -e "${GREEN}[SUCCESS]${NC} $message" ;;
        "WARNING") echo -e "${YELLOW}[WARNING]${NC} $message" ;;
        "INFO")    echo -e "${BLUE}[INFO]${NC} $message" ;;
        *)         echo "$message" ;;
    esac
}

# Initialize uSCRIPT system
init_system() {
    log "INFO" "Initializing uSCRIPT v1.3 system..."
    
    # Create directories if they don't exist
    mkdir -p "$CONFIG_DIR" "$LIBRARY_DIR" "$REGISTRY_DIR" "$RUNTIME_DIR" "$LOGS_DIR" "$SANDBOX_DIR"
    mkdir -p "$LIBRARY_DIR"/{python,shell,javascript,ucode,utilities,automation}
    mkdir -p "$RUNTIME_DIR/engines"
    
    # Check for required dependencies
    check_dependencies
    
    # Create default configurations if they don't exist
    create_default_configs
    
    log "SUCCESS" "uSCRIPT v1.3 system initialized successfully"
}

# Check for required system dependencies
check_dependencies() {
    local missing_deps=()
    
    # Check for jq (JSON processing)
    if ! command -v jq &> /dev/null; then
        missing_deps+=("jq")
    fi
    
    # Check for python3
    if ! command -v python3 &> /dev/null; then
        missing_deps+=("python3")
    fi
    
    # Check for node (for JavaScript)
    if ! command -v node &> /dev/null; then
        missing_deps+=("node")
    fi
    
    if [ ${#missing_deps[@]} -gt 0 ]; then
        log "WARNING" "Missing dependencies: ${missing_deps[*]}"
        log "INFO" "Some script types may not be available without these dependencies"
    else
        log "SUCCESS" "All dependencies are available"
    fi
}

# Create default configuration files
create_default_configs() {
    # Create catalog.json if it doesn't exist
    if [ ! -f "$REGISTRY_DIR/catalog.json" ]; then
        cat > "$REGISTRY_DIR/catalog.json" << 'EOF'
{
  "version": "1.3.0",
  "scripts": {
    "data-processor": {
      "name": "data-processor",
      "type": "python",
      "path": "library/python/data-processor.py",
      "description": "Process and analyze data files with statistical summaries",
      "version": "1.0.0",
      "author": "uDOS Team",
      "security_level": "safe",
      "dependencies": ["pandas", "numpy"],
      "parameters": {
        "input_file": "string",
        "output_format": "json|csv|txt"
      },
      "created": "2024-12-28",
      "last_modified": "2024-12-28"
    },
    "system-backup": {
      "name": "system-backup",
      "type": "shell",
      "path": "library/shell/system-backup.sh",
      "description": "Create system backups with compression and verification",
      "version": "1.0.0",
      "author": "uDOS Team",
      "security_level": "elevated",
      "dependencies": ["tar", "gzip"],
      "parameters": {
        "source_dir": "string",
        "backup_name": "string",
        "compression": "gzip|bzip2|none"
      },
      "created": "2024-12-28",
      "last_modified": "2024-12-28"
    },
    "report-generator": {
      "name": "report-generator",
      "type": "ucode",
      "path": "library/ucode/report-generator.ucode.md",
      "description": "Generate formatted reports using uCODE template system",
      "version": "1.0.0",
      "author": "uDOS Team",
      "security_level": "safe",
      "dependencies": ["ucode-engine"],
      "parameters": {
        "template": "string",
        "data_source": "string",
        "output_format": "html|pdf|md"
      },
      "created": "2024-12-28",
      "last_modified": "2024-12-28"
    }
  }
}
EOF
        log "INFO" "Created default catalog.json"
    fi
    
    # Create security.json if it doesn't exist
    if [ ! -f "$CONFIG_DIR/security.json" ]; then
        cat > "$CONFIG_DIR/security.json" << 'EOF'
{
  "security_levels": {
    "safe": {
      "description": "Scripts that only read data and perform calculations",
      "restrictions": ["no_file_write", "no_network", "no_system_calls"],
      "sandbox": true,
      "timeout": 300
    },
    "elevated": {
      "description": "Scripts that can modify files but not system settings",
      "restrictions": ["no_system_config", "no_user_management"],
      "sandbox": true,
      "timeout": 600,
      "require_confirmation": true
    },
    "admin": {
      "description": "Scripts with full system access",
      "restrictions": [],
      "sandbox": false,
      "timeout": 1800,
      "require_confirmation": true,
      "require_admin": true
    }
  },
  "default_level": "safe",
  "sandbox_config": {
    "max_memory": "512MB",
    "max_cpu": "50%",
    "network_access": false,
    "file_system_access": "read_only"
  }
}
EOF
        log "INFO" "Created default security.json"
    fi
    
    # Create engines.json if it doesn't exist
    if [ ! -f "$CONFIG_DIR/engines.json" ]; then
        cat > "$CONFIG_DIR/engines.json" << 'EOF'
{
  "engines": {
    "python": {
      "command": "python3",
      "file_extension": ".py",
      "timeout": 300,
      "sandbox_supported": true,
      "version_check": "python3 --version"
    },
    "shell": {
      "command": "bash",
      "file_extension": ".sh",
      "timeout": 600,
      "sandbox_supported": false,
      "version_check": "bash --version"
    },
    "javascript": {
      "command": "node",
      "file_extension": ".js",
      "timeout": 300,
      "sandbox_supported": true,
      "version_check": "node --version"
    },
    "ucode": {
      "command": "ucode-engine",
      "file_extension": ".ucode.md",
      "timeout": 300,
      "sandbox_supported": true,
      "version_check": "echo 'uCODE v2.1'"
    }
  }
}
EOF
        log "INFO" "Created default engines.json"
    fi
    
    # Create defaults.json if it doesn't exist
    if [ ! -f "$CONFIG_DIR/defaults.json" ]; then
        cat > "$CONFIG_DIR/defaults.json" << 'EOF'
{
  "execution": {
    "default_timeout": 300,
    "max_concurrent": 3,
    "log_level": "INFO",
    "auto_cleanup": true
  },
  "output": {
    "format": "json",
    "include_metadata": true,
    "color_output": true,
    "timestamp": true
  },
  "security": {
    "default_level": "safe",
    "require_confirmation_above": "safe",
    "sandbox_by_default": true
  }
}
EOF
        log "INFO" "Created default defaults.json"
    fi
}

# List all available scripts
list_scripts() {
    log "INFO" "Listing available scripts..."
    
    if [ ! -f "$REGISTRY_DIR/catalog.json" ]; then
        log "ERROR" "Script catalog not found. Run 'uscript init' first."
        return 1
    fi
    
    echo -e "\n${CYAN}📚 uSCRIPT v1.3 Script Library${NC}"
    echo -e "${CYAN}================================${NC}\n"
    
    # Use jq to parse and display scripts
    jq -r '.scripts | to_entries[] | 
        "\(.key):\n  Type: \(.value.type)\n  Description: \(.value.description)\n  Security: \(.value.security_level)\n  Version: \(.value.version)\n"' \
        "$REGISTRY_DIR/catalog.json"
    
    local script_count=$(jq '.scripts | length' "$REGISTRY_DIR/catalog.json")
    echo -e "${GREEN}Total scripts available: $script_count${NC}\n"
}

# Show detailed information about a specific script
show_script_info() {
    local script_name="$1"
    
    if [ -z "$script_name" ]; then
        log "ERROR" "Script name required. Usage: uscript info <script-name>"
        return 1
    fi
    
    if [ ! -f "$REGISTRY_DIR/catalog.json" ]; then
        log "ERROR" "Script catalog not found. Run 'uscript init' first."
        return 1
    fi
    
    # Check if script exists
    local script_exists=$(jq --arg name "$script_name" '.scripts | has($name)' "$REGISTRY_DIR/catalog.json")
    
    if [ "$script_exists" = "false" ]; then
        log "ERROR" "Script '$script_name' not found in catalog"
        return 1
    fi
    
    echo -e "\n${CYAN}📋 Script Information: $script_name${NC}"
    echo -e "${CYAN}=====================================${NC}\n"
    
    # Extract and display script information
    jq --arg name "$script_name" -r '
        .scripts[$name] | 
        "Name: \(.name)\n" +
        "Type: \(.type)\n" +
        "Description: \(.description)\n" +
        "Version: \(.version)\n" +
        "Author: \(.author)\n" +
        "Security Level: \(.security_level)\n" +
        "Path: \(.path)\n" +
        "Dependencies: \(.dependencies | join(", "))\n" +
        "Created: \(.created)\n" +
        "Last Modified: \(.last_modified)\n"
    ' "$REGISTRY_DIR/catalog.json"
    
    # Show parameters if available
    local has_params=$(jq --arg name "$script_name" '.scripts[$name] | has("parameters")' "$REGISTRY_DIR/catalog.json")
    if [ "$has_params" = "true" ]; then
        echo -e "${YELLOW}Parameters:${NC}"
        jq --arg name "$script_name" -r '.scripts[$name].parameters | to_entries[] | "  \(.key): \(.value)"' "$REGISTRY_DIR/catalog.json"
        echo ""
    fi
}

# Execute a script
execute_script() {
    local script_name="$1"
    shift
    local script_args=("$@")
    
    if [ -z "$script_name" ]; then
        log "ERROR" "Script name required. Usage: uscript run <script-name> [args...]"
        return 1
    fi
    
    if [ ! -f "$REGISTRY_DIR/catalog.json" ]; then
        log "ERROR" "Script catalog not found. Run 'uscript init' first."
        return 1
    fi
    
    # Check if script exists
    local script_exists=$(jq --arg name "$script_name" '.scripts | has($name)' "$REGISTRY_DIR/catalog.json")
    
    if [ "$script_exists" = "false" ]; then
        log "ERROR" "Script '$script_name' not found in catalog"
        return 1
    fi
    
    # Get script information
    local script_type=$(jq --arg name "$script_name" -r '.scripts[$name].type' "$REGISTRY_DIR/catalog.json")
    local script_path=$(jq --arg name "$script_name" -r '.scripts[$name].path' "$REGISTRY_DIR/catalog.json")
    local security_level=$(jq --arg name "$script_name" -r '.scripts[$name].security_level' "$REGISTRY_DIR/catalog.json")
    
    local full_script_path="$USCRIPT_ROOT/$script_path"
    
    if [ ! -f "$full_script_path" ]; then
        log "ERROR" "Script file not found: $full_script_path"
        return 1
    fi
    
    log "INFO" "Executing script: $script_name (type: $script_type, security: $security_level)"
    
    # Security check
    if [ "$security_level" = "elevated" ] || [ "$security_level" = "admin" ]; then
        echo -e "${YELLOW}⚠️  This script requires '$security_level' permissions.${NC}"
        echo -e "${YELLOW}Script: $script_name${NC}"
        echo -e "${YELLOW}Path: $script_path${NC}"
        read -p "Continue? (y/N): " -n 1 -r
        echo
        if [[ ! $REPLY =~ ^[Yy]$ ]]; then
            log "INFO" "Script execution cancelled by user"
            return 0
        fi
    fi
    
    # Get engine configuration
    local engine_cmd=$(jq --arg type "$script_type" -r '.engines[$type].command' "$CONFIG_DIR/engines.json")
    local engine_timeout=$(jq --arg type "$script_type" -r '.engines[$type].timeout' "$CONFIG_DIR/engines.json")
    
    if [ "$engine_cmd" = "null" ]; then
        log "ERROR" "No engine configured for script type: $script_type"
        return 1
    fi
    
    # Execute the script
    local start_time=$(date '+%Y-%m-%d %H:%M:%S')
    local execution_id="exec_$(date +%s)_$script_name"
    
    log "INFO" "Starting execution (ID: $execution_id)"
    
    # Create execution log
    mkdir -p "$LOGS_DIR/executions"
    local exec_log="$LOGS_DIR/executions/${execution_id}.log"
    
    {
        echo "Execution ID: $execution_id"
        echo "Script: $script_name"
        echo "Type: $script_type"
        echo "Start Time: $start_time"
        echo "Command: $engine_cmd $full_script_path ${script_args[*]}"
        echo "Security Level: $security_level"
        echo "=====================================\n"
    } > "$exec_log"
    
    # Execute based on script type
    case "$script_type" in
        "python")
            timeout "$engine_timeout" python3 "$full_script_path" "${script_args[@]}" 2>&1 | tee -a "$exec_log"
            ;;
        "shell")
            timeout "$engine_timeout" bash "$full_script_path" "${script_args[@]}" 2>&1 | tee -a "$exec_log"
            ;;
        "javascript")
            timeout "$engine_timeout" node "$full_script_path" "${script_args[@]}" 2>&1 | tee -a "$exec_log"
            ;;
        "ucode")
            log "WARNING" "uCODE execution not yet implemented"
            return 1
            ;;
        *)
            log "ERROR" "Unknown script type: $script_type"
            return 1
            ;;
    esac
    
    local exit_code=$?
    local end_time=$(date '+%Y-%m-%d %H:%M:%S')
    
    {
        echo "\n====================================="
        echo "End Time: $end_time"
        echo "Exit Code: $exit_code"
    } >> "$exec_log"
    
    if [ $exit_code -eq 0 ]; then
        log "SUCCESS" "Script execution completed successfully (ID: $execution_id)"
    else
        log "ERROR" "Script execution failed with exit code $exit_code (ID: $execution_id)"
    fi
    
    return $exit_code
}

# Show help information
show_help() {
    echo -e "\n${CYAN}uSCRIPT v3.0 - Production Script Library & Execution Engine${NC}"
    echo -e "${CYAN}==========================================================${NC}\n"
    
    echo -e "${YELLOW}USAGE:${NC}"
    echo -e "  uscript <command> [options]\n"
    
    echo -e "${YELLOW}COMMANDS:${NC}"
    echo -e "  ${GREEN}init${NC}                    Initialize uSCRIPT system and create default configs"
    echo -e "  ${GREEN}list${NC}                    List all available scripts in the library"
    echo -e "  ${GREEN}info${NC} <script-name>      Show detailed information about a specific script"
    echo -e "  ${GREEN}run${NC} <script-name> [args] Execute a script with optional arguments"
    echo -e "  ${GREEN}help${NC}                    Show this help message"
    echo -e "  ${GREEN}version${NC}                 Show version information\n"
    
    echo -e "${YELLOW}EXAMPLES:${NC}"
    echo -e "  uscript init"
    echo -e "  uscript list"
    echo -e "  uscript info data-processor"
    echo -e "  uscript run system-backup /home/user backup-$(date +%Y%m%d)"
    echo -e "  uscript run data-processor --input data.csv --format json\n"
    
    echo -e "${YELLOW}SCRIPT TYPES:${NC}"
    echo -e "  ${PURPLE}python${NC}     - Python 3 scripts (.py)"
    echo -e "  ${PURPLE}shell${NC}      - Bash shell scripts (.sh)"
    echo -e "  ${PURPLE}javascript${NC} - Node.js scripts (.js)"
    echo -e "  ${PURPLE}ucode${NC}      - uDOS native scripts (.ucode.md)\n"
    
    echo -e "${YELLOW}SECURITY LEVELS:${NC}"
    echo -e "  ${GREEN}safe${NC}       - Read-only scripts, sandboxed execution"
    echo -e "  ${YELLOW}elevated${NC}   - File modification allowed, requires confirmation"
    echo -e "  ${RED}admin${NC}      - Full system access, requires admin confirmation\n"
}

# Show version information
show_version() {
    echo -e "${CYAN}uSCRIPT v3.0.0${NC}"
    echo -e "Production Script Library & Execution Engine"
    echo -e "Part of uDOS v1.3"
    echo -e "https://github.com/udos-project/udos\n"
}

# Main command dispatcher
main() {
    local command="$1"
    shift
    
    case "$command" in
        "init")
            init_system
            ;;
        "list")
            list_scripts
            ;;
        "info")
            show_script_info "$@"
            ;;
        "run")
            execute_script "$@"
            ;;
        "help"|"--help"|"-h")
            show_help
            ;;
        "version"|"--version"|"-v")
            show_version
            ;;
        "")
            log "ERROR" "No command specified. Use 'uscript help' for usage information."
            exit 1
            ;;
        *)
            log "ERROR" "Unknown command: $command. Use 'uscript help' for usage information."
            exit 1
            ;;
    esac
}

# Run main function with all arguments
main "$@"
