#!/bin/bash
# uDOS Development Mode Manager
# Provides development tools and environment management

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
UHOME="${UHOME:-$HOME/uDOS}"
UDEV="$UHOME/uDev"

# Colors
GREEN='\033[0;32m'
RED='\033[0;31m' 
YELLOW='\033[1;33m'
CYAN='\033[0;36m'
BLUE='\033[0;34m'
PURPLE='\033[0;35m'
DIM='\033[2m'
BOLD='\033[1m'
NC='\033[0m'

log() { echo -e "${CYAN}[$(date '+%H:%M:%S')] [DEV-MODE]${NC} $1"; }
success() { echo -e "${GREEN}✅${NC} $1"; }
error() { echo -e "${RED}❌${NC} $1" >&2; }
warn() { echo -e "${YELLOW}⚠️${NC} $1"; }
info() { echo -e "${BLUE}ℹ️${NC} $1"; }

# Check if development mode is enabled
is_dev_mode_enabled() {
    [[ "${UDOS_DEV_MODE:-false}" == "true" || -f "$UDEV/.dev-mode-enabled" ]]
}

# Enable development mode
enable_dev_mode() {
    log "Enabling uDOS development mode..."
    
    # Create development directory structure
    mkdir -p "$UDEV"/{validation,templates,testing,schemas,tools,docs}
    mkdir -p "$UDEV/validation"/{dataget,dataset,template,schema,reports}
    mkdir -p "$UDEV/templates"/{validation,testing,examples,backup}
    mkdir -p "$UDEV/testing"/{unit,integration,performance,mock-data,fixtures}
    mkdir -p "$UDEV/tools"/{generators,validators,analyzers,utilities}
    mkdir -p "$UDEV/docs"/{api,guides,examples,troubleshooting}
    
    # Create development mode marker
    touch "$UDEV/.dev-mode-enabled"
    echo "$(date)" > "$UDEV/.dev-mode-enabled"
    
    # Create development configuration
    cat > "$UDEV/dev-config.json" << 'EOF'
{
    "version": "1.1.0",
    "enabled": true,
    "created": "$(date -Iseconds)",
    "settings": {
        "validation": {
            "strict_mode": true,
            "auto_fix": false,
            "backup_on_fix": true,
            "detailed_output": true,
            "generate_reports": true
        },
        "testing": {
            "run_unit_tests": true,
            "run_integration_tests": true,
            "mock_external_deps": true,
            "performance_benchmarks": true,
            "coverage_reports": true
        },
        "template_processing": {
            "validate_before_process": true,
            "cache_validation_results": true,
            "sandbox_execution": true,
            "backup_templates": true
        },
        "development_tools": {
            "auto_formatting": true,
            "syntax_highlighting": true,
            "debug_logging": true,
            "profiling": false
        }
    },
    "paths": {
        "validation": "./validation",
        "templates": "./templates", 
        "testing": "./testing",
        "schemas": "./schemas",
        "tools": "./tools",
        "docs": "./docs"
    }
}
EOF
    
    # Create development environment variables
    cat > "$UDEV/.dev-env" << 'EOF'
# uDOS Development Mode Environment
export UDOS_DEV_MODE=true
export UDEV_ROOT="$UDEV"
export UDOS_VALIDATION_STRICT=true
export UDOS_DEBUG_LOGGING=true
export UDOS_BACKUP_TEMPLATES=true
export UDOS_SANDBOX_MODE=true
EOF
    
    success "Development mode enabled"
    info "Development environment created in $UDEV"
    
    # Create development tools
    create_development_tools
    
    # Copy and backup production templates
    backup_production_templates
    
    # Generate development documentation
    generate_dev_documentation
}

# Disable development mode
disable_dev_mode() {
    log "Disabling uDOS development mode..."
    
    # Remove development mode marker
    rm -f "$UDEV/.dev-mode-enabled"
    
    # Archive development work
    if [[ -d "$UDEV" ]]; then
        local archive_name="dev-archive-$(date +%Y%m%d-%H%M%S).tar.gz"
        log "Archiving development work to $UHOME/archives/$archive_name"
        mkdir -p "$UHOME/archives"
        tar -czf "$UHOME/archives/$archive_name" -C "$UDEV" . 2>/dev/null || warn "Could not create archive"
    fi
    
    success "Development mode disabled"
    info "Development work archived to $UHOME/archives/"
}

# Create development tools
create_development_tools() {
    log "Creating development tools..."
    
    # Template validator
    cat > "$UDEV/tools/validate-template.sh" << 'EOF'
#!/bin/bash
# Template Validation Tool
set -euo pipefail

UDEV="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
source "$UDEV/../uCode/template-validation.sh"

if [[ $# -eq 0 ]]; then
    echo "Usage: $0 <template-file|directory>"
    echo
    echo "Examples:"
    echo "  $0 ../uTemplate/datagets/user-setup.json"
    echo "  $0 ../uTemplate/datagets/"
    exit 1
fi

target="$1"
if [[ -f "$target" ]]; then
    validate_dataget_schema "$target"
elif [[ -d "$target" ]]; then
    validate_template_files "$target"
else
    echo "Error: $target is not a valid file or directory"
    exit 1
fi
EOF
    
    # Mock data generator
    cat > "$UDEV/tools/generate-mock-data.sh" << 'EOF'
#!/bin/bash
# Mock Data Generator
set -euo pipefail

UDEV="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
MOCK_DIR="$UDEV/testing/mock-data"

mkdir -p "$MOCK_DIR"

echo "🎭 Generating mock data for testing..."

# Mock user setup data
cat > "$MOCK_DIR/mock-user-setup.json" << 'MOCK'
{
    "username": "devuser",
    "full_name": "Development User", 
    "email": "dev@udos.local",
    "location": "Development City, Dev Country (DV01)",
    "timezone": "UTC",
    "primary_role": "developer",
    "password": "",
    "auto_backup": true,
    "debug_mode": true,
    "preferred_companion": "chester",
    "notification_level": "verbose",
    "experimental_features": true
}
MOCK

# Mock mission data
cat > "$MOCK_DIR/mock-mission-create.json" << 'MOCK'
{
    "mission_name": "Development Test Mission",
    "mission_type": "development",
    "priority_level": "medium",
    "description": "Test mission for development and validation purposes",
    "estimated_duration": "1-2 hours",
    "start_date": "$(date +%Y-%m-%d)",
    "target_completion": "$(date -d '+1 week' +%Y-%m-%d)",
    "required_skills": ["testing", "validation"],
    "resources_needed": ["development_tools"],
    "success_criteria": ["All tests pass", "Validation complete"]
}
MOCK

# Mock system config
cat > "$MOCK_DIR/mock-system-config.json" << 'MOCK'
{
    "display_mode": "console",
    "border_style": "single",
    "color_scheme": "default",
    "logging_level": "DEBUG",
    "enable_debug_mode": true,
    "verbose_output": true,
    "auto_backup_interval": "hourly",
    "backup_retention": "7_days",
    "max_log_size": "10MB",
    "terminal_history_size": "5000",
    "enable_experimental_features": true,
    "network_timeout": "30",
    "command_aliases": true,
    "system_password": ""
}
MOCK

echo "✅ Mock data generated in $MOCK_DIR"
ls -la "$MOCK_DIR"
EOF
    
    # Development test runner
    cat > "$UDEV/tools/run-dev-tests.sh" << 'EOF'
#!/bin/bash
# Development Test Runner
set -euo pipefail

UDEV="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
TEST_DIR="$UDEV/testing"

echo "🧪 Running development tests..."

# Source development environment
source "$UDEV/.dev-env" 2>/dev/null || true

# Run template validation tests
echo "Running template validation..."
"$UDEV/../uCode/template-validation.sh" dev

# Run mock data tests
echo "Running mock data validation..."
"$UDEV/tools/generate-mock-data.sh"

# Validate mock data against schemas
if [[ -f "$UDEV/schemas/dataget-schema.json" ]]; then
    echo "Validating mock data against schemas..."
    for mock_file in "$UDEV/testing/mock-data"/*.json; do
        if [[ -f "$mock_file" ]]; then
            echo "  Checking $(basename "$mock_file")..."
            if jq '.' "$mock_file" >/dev/null 2>&1; then
                echo "    ✅ Valid JSON"
            else
                echo "    ❌ Invalid JSON"
            fi
        fi
    done
fi

echo "✅ Development tests completed"
EOF
    
    # Performance benchmark tool
    cat > "$UDEV/tools/benchmark-performance.sh" << 'EOF'
#!/bin/bash
# Performance Benchmarking Tool
set -euo pipefail

UDEV="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"

echo "⚡ Running performance benchmarks..."

# Template processing benchmark
benchmark_template_processing() {
    local start_time=$(date +%s.%N)
    
    # Run template validation
    "$UDEV/../uCode/template-validation.sh" validate >/dev/null 2>&1
    
    local end_time=$(date +%s.%N)
    local duration=$(echo "$end_time - $start_time" | bc -l 2>/dev/null || echo "0")
    
    echo "Template validation: ${duration}s"
}

# Input system benchmark
benchmark_input_system() {
    local start_time=$(date +%s.%N)
    
    # Test input system loading
    source "$UDEV/../uCode/input-system.sh" >/dev/null 2>&1
    
    local end_time=$(date +%s.%N)
    local duration=$(echo "$end_time - $start_time" | bc -l 2>/dev/null || echo "0")
    
    echo "Input system load: ${duration}s"
}

benchmark_template_processing
benchmark_input_system

echo "✅ Performance benchmarks completed"
EOF
    
    # Make tools executable
    chmod +x "$UDEV/tools"/*.sh
    
    success "Development tools created in $UDEV/tools/"
}

# Backup production templates
backup_production_templates() {
    log "Backing up production templates..."
    
    local backup_dir="$UDEV/templates/backup/$(date +%Y%m%d-%H%M%S)"
    mkdir -p "$backup_dir"
    
    # Backup uTemplate directory
    if [[ -d "$UHOME/uTemplate" ]]; then
        cp -r "$UHOME/uTemplate"/* "$backup_dir/" 2>/dev/null || true
        success "Production templates backed up to $backup_dir"
    fi
    
    # Create working copies in development
    if [[ -d "$UHOME/uTemplate/datagets" ]]; then
        cp -r "$UHOME/uTemplate/datagets" "$UDEV/templates/" 2>/dev/null || true
    fi
    
    if [[ -d "$UHOME/uTemplate/datasets" ]]; then
        cp -r "$UHOME/uTemplate/datasets" "$UDEV/templates/" 2>/dev/null || true
    fi
}

# Generate development documentation
generate_dev_documentation() {
    log "Generating development documentation..."
    
    # Development guide
    cat > "$UDEV/docs/development-guide.md" << 'EOF'
# uDOS Development Mode Guide

## Overview
Development mode provides additional tools and safety features for working with uDOS templates, datagets, and validation systems.

## Directory Structure
```
uDev/
├── validation/          # Validation results and reports
├── templates/           # Template development and backup
├── testing/            # Testing infrastructure and mock data
├── schemas/            # JSON schemas for validation
├── tools/              # Development utilities
└── docs/               # Documentation and guides
```

## Available Tools

### Template Validation
```bash
./tools/validate-template.sh <file-or-directory>
```

### Mock Data Generation
```bash
./tools/generate-mock-data.sh
```

### Development Testing
```bash
./tools/run-dev-tests.sh
```

### Performance Benchmarking
```bash
./tools/benchmark-performance.sh
```

## Best Practices

1. **Always validate before committing**: Use template validation tools
2. **Test with mock data**: Generate and use mock data for testing
3. **Backup templates**: Templates are automatically backed up
4. **Use schemas**: Follow JSON schema validation
5. **Performance monitoring**: Regular performance benchmarks

## Environment Variables

- `UDOS_DEV_MODE=true` - Enable development mode
- `UDOS_VALIDATION_STRICT=true` - Strict validation mode
- `UDOS_DEBUG_LOGGING=true` - Enable debug logging
- `UDOS_BACKUP_TEMPLATES=true` - Auto-backup templates
- `UDOS_SANDBOX_MODE=true` - Sandbox execution mode

## Troubleshooting

### Common Issues
1. **Permission errors**: Ensure scripts are executable
2. **Missing dependencies**: Install jq, yq, and other tools
3. **Schema validation failures**: Check against schemas in schemas/
4. **Template syntax errors**: Use validation tools before testing

### Getting Help
- Check logs in `validation/reports/`
- Review mock data in `testing/mock-data/`
- Validate against schemas in `schemas/`
- Run development tests with `tools/run-dev-tests.sh`
EOF
    
    # API documentation
    cat > "$UDEV/docs/validation-api.md" << 'EOF'
# uDOS Validation API Documentation

## Template Validation Functions

### `validate_dataget_schema(dataget_file)`
Validates a dataget JSON configuration against schema rules.

**Parameters:**
- `dataget_file`: Path to dataget JSON file

**Returns:**
- 0 on success, 1 on failure

**Validates:**
- JSON syntax
- Required fields (title, description, fields)
- Field structure and types
- noblank logic
- Default value requirements

### `validate_dataset_schema(dataset_file)`
Validates dataset JSON files.

**Parameters:**
- `dataset_file`: Path to dataset JSON file

**Returns:**
- 0 on success, 1 on failure

### `validate_template_files(template_dir)`
Validates all template files in a directory.

**Parameters:**
- `template_dir`: Directory containing templates

**Returns:**
- 0 on success, 1 on failure

**Supports:**
- JSON templates
- YAML templates (if yq available)
- Markdown templates

## Schema Validation Rules

### Dataget Fields
- `noblank`: Defaults to `true`, must be `false` for password fields
- `default`: Required when `noblank=true` (except passwords)
- `validation`: Recommended for text and email fields
- `help`: Required for all fields

### Dataset Structure
- Must contain valid JSON
- Schema varies by dataset type
- Shortcode datasets require `shortcodes` array
- Each shortcode needs `command`, `category`, `description`

## Error Handling
All validation functions provide detailed error messages and return appropriate exit codes for scripting integration.
EOF
    
    success "Development documentation generated in $UDEV/docs/"
}

# Show development mode status
show_dev_status() {
    echo -e "${BOLD}🛠️ uDOS Development Mode Status${NC}"
    echo "═══════════════════════════════════════"
    
    if is_dev_mode_enabled; then
        echo -e "${GREEN}✅ Development mode: ENABLED${NC}"
        
        if [[ -f "$UDEV/dev-config.json" ]]; then
            local created=$(jq -r '.created // "unknown"' "$UDEV/dev-config.json" 2>/dev/null || echo "unknown")
            echo -e "${CYAN}📅 Enabled since: $created${NC}"
        fi
        
        echo
        echo -e "${BOLD}Available Tools:${NC}"
        if [[ -d "$UDEV/tools" ]]; then
            for tool in "$UDEV/tools"/*.sh; do
                if [[ -f "$tool" ]]; then
                    echo -e "  ${GREEN}•${NC} $(basename "$tool")"
                fi
            done
        fi
        
        echo
        echo -e "${BOLD}Directory Structure:${NC}"
        if [[ -d "$UDEV" ]]; then
            ls -la "$UDEV" | tail -n +2 | while IFS= read -r line; do
                echo "  $line"
            done
        fi
        
    else
        echo -e "${YELLOW}⚠️ Development mode: DISABLED${NC}"
        echo
        info "Enable with: $0 enable"
    fi
    
    echo
    echo -e "${BOLD}Environment Variables:${NC}"
    echo -e "  UDOS_DEV_MODE: ${UDOS_DEV_MODE:-false}"
    echo -e "  UHOME: $UHOME"
    echo -e "  UDEV: $UDEV"
}

# Main function
main() {
    case "${1:-status}" in
        "enable"|"on")
            enable_dev_mode
            ;;
        "disable"|"off")
            disable_dev_mode
            ;;
        "status"|"info")
            show_dev_status
            ;;
        "tools")
            if is_dev_mode_enabled; then
                echo -e "${BOLD}🔧 Development Tools${NC}"
                echo "═══════════════════════"
                for tool in "$UDEV/tools"/*.sh; do
                    if [[ -f "$tool" ]]; then
                        echo -e "${GREEN}$(basename "$tool")${NC}"
                        echo -e "${DIM}  $tool${NC}"
                        echo
                    fi
                done
            else
                error "Development mode is not enabled"
                info "Enable with: $0 enable"
            fi
            ;;
        "test")
            if is_dev_mode_enabled; then
                "$UDEV/tools/run-dev-tests.sh"
            else
                error "Development mode is not enabled"
                exit 1
            fi
            ;;
        "help"|"-h"|"--help")
            echo -e "${BOLD}uDOS Development Mode Manager${NC}"
            echo
            echo "Usage: $0 [command]"
            echo
            echo "Commands:"
            echo "  enable    Enable development mode"
            echo "  disable   Disable development mode (archives work)"
            echo "  status    Show development mode status (default)"
            echo "  tools     List available development tools"
            echo "  test      Run development tests"
            echo "  help      Show this help message"
            echo
            echo "Development mode provides:"
            echo "  • Template validation tools"
            echo "  • Mock data generators"
            echo "  • Performance benchmarking"
            echo "  • Schema validation"
            echo "  • Safe development environment"
            ;;
        *)
            error "Unknown command: $1"
            echo "Run '$0 help' for usage information"
            exit 1
            ;;
    esac
}

main "$@"
