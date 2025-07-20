#!/bin/bash
# uDOS Template-Integrated Validation System
# Combines template processing with comprehensive validation

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
UHOME="${UHOME:-$HOME/uDOS}"
UDEV="$UHOME/uDev"
TEMPLATE_DIR="$UHOME/uTemplate"

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

# Development mode flag
DEV_MODE="${UDOS_DEV_MODE:-false}"

# Validation counters
VALIDATION_PASSED=0
VALIDATION_FAILED=0
VALIDATION_TOTAL=0

# ═══════════════════════════════════════════════════════════════════════════════════════
# 🏗️ DEVELOPMENT MODE SETUP
# ═══════════════════════════════════════════════════════════════════════════════════════

setup_dev_mode() {
    log "Setting up development mode environment..."
    
    # Create development directories
    mkdir -p "$UDEV"/{validation,templates,testing,schemas,mocks}
    mkdir -p "$UDEV/validation"/{dataget,dataset,template,schema}
    mkdir -p "$UDEV/templates"/{validation,testing,examples}
    mkdir -p "$UDEV/testing"/{unit,integration,performance,mock-data}
    
    # Copy templates to dev environment for safe testing
    if [[ -d "$TEMPLATE_DIR" ]]; then
        log "Copying templates to development environment..."
        cp -r "$TEMPLATE_DIR"/* "$UDEV/templates/" 2>/dev/null || true
    fi
    
    # Create dev configuration
    cat > "$UDEV/dev-config.json" << 'EOF'
{
    "version": "1.0.0",
    "dev_mode": true,
    "validation": {
        "strict_mode": true,
        "auto_fix": false,
        "backup_on_fix": true,
        "detailed_output": true
    },
    "testing": {
        "run_unit_tests": true,
        "run_integration_tests": true,
        "mock_external_deps": true,
        "performance_benchmarks": true
    },
    "template_processing": {
        "validate_before_process": true,
        "cache_validation_results": true,
        "sandbox_execution": true
    }
}
EOF
    
    success "Development mode environment ready"
}

# ═══════════════════════════════════════════════════════════════════════════════════════
# 📋 TEMPLATE VALIDATION SYSTEM
# ═══════════════════════════════════════════════════════════════════════════════════════

log() { echo -e "${CYAN}[$(date '+%H:%M:%S')] [TEMPLATE-VALIDATE]${NC} $1"; }
success() { echo -e "${GREEN}✅${NC} $1"; }
error() { echo -e "${RED}❌${NC} $1" >&2; }
warn() { echo -e "${YELLOW}⚠️${NC} $1"; }
info() { echo -e "${BLUE}ℹ️${NC} $1"; }

validate_pass() {
    ((VALIDATION_PASSED++))
    ((VALIDATION_TOTAL++))
    echo -e "${GREEN}✅ PASS${NC} $1"
}

validate_fail() {
    ((VALIDATION_FAILED++))
    ((VALIDATION_TOTAL++))
    echo -e "${RED}❌ FAIL${NC} $1"
}

# Validate dataget schema compliance
validate_dataget_schema() {
    local dataget_file="$1"
    local schema_errors=0
    
    log "Validating dataget schema: $(basename "$dataget_file")"
    
    if [[ ! -f "$dataget_file" ]]; then
        validate_fail "Dataget file not found: $dataget_file"
        return 1
    fi
    
    # Check JSON validity
    if ! jq '.' "$dataget_file" >/dev/null 2>&1; then
        validate_fail "Invalid JSON syntax in $dataget_file"
        return 1
    fi
    
    # Check required top-level keys
    local required_keys=("title" "description" "fields")
    for key in "${required_keys[@]}"; do
        if ! jq -e ".$key" "$dataget_file" >/dev/null 2>&1; then
            validate_fail "Missing required key: $key"
            ((schema_errors++))
        fi
    done
    
    # Validate field structure
    local field_count=$(jq '.fields | length' "$dataget_file")
    if [[ "$field_count" -eq 0 ]]; then
        validate_fail "Dataget has no fields defined"
        ((schema_errors++))
    else
        log "Found $field_count fields to validate"
        
        # Check each field
        for ((i=0; i<field_count; i++)); do
            local field_name=$(jq -r ".fields[$i].name" "$dataget_file")
            local field_type=$(jq -r ".fields[$i].type" "$dataget_file")
            local noblank=$(jq -r ".fields[$i].noblank // true" "$dataget_file")
            local has_default=$(jq -e ".fields[$i] | has(\"default\")" "$dataget_file" >/dev/null 2>&1 && echo "true" || echo "false")
            
            # Handle special case where noblank is explicitly set to false
            if jq -e ".fields[$i] | has(\"noblank\")" "$dataget_file" >/dev/null 2>&1; then
                noblank=$(jq -r ".fields[$i].noblank" "$dataget_file")
            else
                noblank="true"  # Default value
            fi
            
            # Validate field structure
            if [[ "$field_name" == "null" || -z "$field_name" ]]; then
                validate_fail "Field $i: Missing or null name"
                ((schema_errors++))
            fi
            
            if [[ "$field_type" == "null" || -z "$field_type" ]]; then
                validate_fail "Field $field_name: Missing or null type"
                ((schema_errors++))
            fi
            
            # Validate noblank and default value logic
            if [[ "$field_type" == "password" ]]; then
                if [[ "$noblank" == "true" ]]; then
                    validate_fail "Field $field_name: Password fields should have noblank=false"
                    ((schema_errors++))
                fi
            else
                if [[ "$noblank" == "true" && "$has_default" == "false" ]]; then
                    validate_fail "Field $field_name: Fields with noblank=true must have meaningful default"
                    ((schema_errors++))
                # Special check for boolean fields - false is a valid default
                elif [[ "$noblank" == "true" && "$field_type" == "boolean" ]]; then
                    local default_value=$(jq -r ".fields[$i].default" "$dataget_file")
                    if [[ "$default_value" == "null" ]]; then
                        validate_fail "Field $field_name: Boolean fields with noblank=true must have true/false default"
                        ((schema_errors++))
                    fi
                fi
            fi
            
            # Check for validation patterns on text fields
            if [[ "$field_type" == "text" || "$field_type" == "email" ]]; then
                if ! jq -e ".fields[$i].validation" "$dataget_file" >/dev/null 2>&1; then
                    warn "Field $field_name: Text field missing validation pattern (recommended)"
                fi
            fi
        done
    fi
    
    if [[ $schema_errors -eq 0 ]]; then
        validate_pass "Dataget schema validation for $(basename "$dataget_file")"
        return 0
    else
        validate_fail "Dataget schema validation failed with $schema_errors errors"
        return 1
    fi
}

# Validate dataset structure
validate_dataset_schema() {
    local dataset_file="$1"
    local schema_errors=0
    
    log "Validating dataset: $(basename "$dataset_file")"
    
    if [[ ! -f "$dataset_file" ]]; then
        validate_fail "Dataset file not found: $dataset_file"
        return 1
    fi
    
    # Check JSON validity
    if ! jq '.' "$dataset_file" >/dev/null 2>&1; then
        validate_fail "Invalid JSON syntax in $dataset_file"
        return 1
    fi
    
    # Check dataset structure based on type
    local dataset_name=$(basename "$dataset_file" .json)
    case "$dataset_name" in
        "shortcodes")
            # Validate shortcode dataset
            if jq -e '.shortcodes' "$dataset_file" >/dev/null 2>&1; then
                local shortcode_count=$(jq '.shortcodes | length' "$dataset_file")
                log "Found $shortcode_count shortcodes"
                
                # Validate each shortcode
                for ((i=0; i<shortcode_count; i++)); do
                    local command=$(jq -r ".shortcodes[$i].command" "$dataset_file")
                    local category=$(jq -r ".shortcodes[$i].category" "$dataset_file")
                    local description=$(jq -r ".shortcodes[$i].description" "$dataset_file")
                    
                    if [[ "$command" == "null" || -z "$command" ]]; then
                        validate_fail "Shortcode $i: Missing command"
                        ((schema_errors++))
                    fi
                    
                    if [[ "$category" == "null" || -z "$category" ]]; then
                        validate_fail "Shortcode $command: Missing category"
                        ((schema_errors++))
                    fi
                    
                    if [[ "$description" == "null" || -z "$description" ]]; then
                        validate_fail "Shortcode $command: Missing description"
                        ((schema_errors++))
                    fi
                done
            else
                validate_fail "Shortcode dataset missing 'shortcodes' array"
                ((schema_errors++))
            fi
            ;;
        *)
            # Generic dataset validation
            local keys=$(jq -r 'keys[]' "$dataset_file" 2>/dev/null || echo "")
            if [[ -z "$keys" ]]; then
                validate_fail "Dataset appears to be empty or malformed"
                ((schema_errors++))
            fi
            ;;
    esac
    
    if [[ $schema_errors -eq 0 ]]; then
        validate_pass "Dataset validation for $(basename "$dataset_file")"
        return 0
    else
        validate_fail "Dataset validation failed with $schema_errors errors"
        return 1
    fi
}

# Validate template files
validate_template_files() {
    local template_dir="$1"
    local template_errors=0
    
    log "Validating template files in $template_dir"
    
    if [[ ! -d "$template_dir" ]]; then
        validate_fail "Template directory not found: $template_dir"
        return 1
    fi
    
    # Find all template files
    local template_files=$(find "$template_dir" -name "*.md" -o -name "*.json" -o -name "*.yaml" -o -name "*.yml" 2>/dev/null || true)
    
    if [[ -z "$template_files" ]]; then
        warn "No template files found in $template_dir"
        return 0
    fi
    
    while IFS= read -r template_file; do
        if [[ -f "$template_file" ]]; then
            local extension="${template_file##*.}"
            case "$extension" in
                "json")
                    if jq '.' "$template_file" >/dev/null 2>&1; then
                        validate_pass "JSON template: $(basename "$template_file")"
                    else
                        validate_fail "Invalid JSON template: $(basename "$template_file")"
                        ((template_errors++))
                    fi
                    ;;
                "yaml"|"yml")
                    if command -v yq >/dev/null 2>&1; then
                        if yq '.' "$template_file" >/dev/null 2>&1; then
                            validate_pass "YAML template: $(basename "$template_file")"
                        else
                            validate_fail "Invalid YAML template: $(basename "$template_file")"
                            ((template_errors++))
                        fi
                    else
                        warn "yq not available - skipping YAML validation for $(basename "$template_file")"
                    fi
                    ;;
                "md")
                    # Basic markdown validation
                    if [[ -r "$template_file" && -s "$template_file" ]]; then
                        validate_pass "Markdown template: $(basename "$template_file")"
                    else
                        validate_fail "Markdown template empty or unreadable: $(basename "$template_file")"
                        ((template_errors++))
                    fi
                    ;;
            esac
        fi
    done <<< "$template_files"
    
    if [[ $template_errors -eq 0 ]]; then
        validate_pass "Template file validation completed"
        return 0
    else
        validate_fail "Template validation failed with $template_errors errors"
        return 1
    fi
}

# Generate validation schemas
generate_validation_schemas() {
    log "Generating validation schemas for development..."
    
    mkdir -p "$UDEV/schemas"
    
    # Dataget schema
    cat > "$UDEV/schemas/dataget-schema.json" << 'EOF'
{
    "$schema": "http://json-schema.org/draft-07/schema#",
    "type": "object",
    "title": "uDOS Dataget Schema",
    "required": ["title", "description", "fields"],
    "properties": {
        "title": {
            "type": "string",
            "minLength": 1,
            "description": "Human-readable title for the dataget"
        },
        "description": {
            "type": "string", 
            "minLength": 1,
            "description": "Brief description of dataget purpose"
        },
        "category": {
            "type": "string",
            "enum": ["setup", "configuration", "data-entry", "survey", "mission"]
        },
        "version": {
            "type": "string",
            "pattern": "^[0-9]+\\.[0-9]+\\.[0-9]+$"
        },
        "fields": {
            "type": "array",
            "minItems": 1,
            "items": {
                "type": "object",
                "required": ["name", "label", "type"],
                "properties": {
                    "name": {
                        "type": "string",
                        "pattern": "^[a-z][a-z0-9_]*$"
                    },
                    "label": {
                        "type": "string",
                        "minLength": 1
                    },
                    "type": {
                        "type": "string",
                        "enum": ["text", "choice", "boolean", "email", "password", "number", "date", "textarea", "multi_select", "dataset_select"]
                    },
                    "required": {
                        "type": "boolean"
                    },
                    "noblank": {
                        "type": "boolean",
                        "description": "Defaults to true except for password fields"
                    },
                    "default": {
                        "description": "Default value - required if noblank is true and type is not password"
                    },
                    "validation": {
                        "type": "string",
                        "description": "Regular expression for validation"
                    },
                    "help": {
                        "type": "string",
                        "description": "Help text for the field"
                    },
                    "options": {
                        "type": "array",
                        "items": {"type": "string"}
                    }
                }
            }
        }
    }
}
EOF

    # Dataset schema
    cat > "$UDEV/schemas/dataset-schema.json" << 'EOF'
{
    "$schema": "http://json-schema.org/draft-07/schema#",
    "type": "object",
    "title": "uDOS Dataset Schema",
    "properties": {
        "metadata": {
            "type": "object",
            "properties": {
                "name": {"type": "string"},
                "version": {"type": "string"},
                "description": {"type": "string"},
                "created": {"type": "string", "format": "date-time"},
                "updated": {"type": "string", "format": "date-time"}
            }
        }
    },
    "additionalProperties": true
}
EOF

    success "Validation schemas generated in $UDEV/schemas/"
}

# ═══════════════════════════════════════════════════════════════════════════════════════
# 🧪 INTEGRATED TESTING SYSTEM
# ═══════════════════════════════════════════════════════════════════════════════════════

run_comprehensive_validation() {
    log "Starting comprehensive template-integrated validation..."
    
    echo -e "${BOLD}🧪 uDOS Template-Integrated Validation System${NC}"
    echo "═══════════════════════════════════════════════════════════════"
    
    # Setup development mode if requested
    if [[ "$DEV_MODE" == "true" ]]; then
        setup_dev_mode
    fi
    
    # Generate schemas
    generate_validation_schemas
    
    # Validate datagets
    log "Validating dataget configurations..."
    local dataget_dir="$TEMPLATE_DIR/datagets"
    if [[ -d "$dataget_dir" ]]; then
        find "$dataget_dir" -name "*.json" | while IFS= read -r dataget_file; do
            validate_dataget_schema "$dataget_file"
        done
    else
        # Fallback to forms directory for backward compatibility
        local forms_dir="$TEMPLATE_DIR/forms"
        if [[ -d "$forms_dir" ]]; then
            find "$forms_dir" -name "*.json" | while IFS= read -r form_file; do
                validate_dataget_schema "$form_file"
            done
        fi
    fi
    
    # Validate datasets
    log "Validating dataset configurations..."
    local datasets_dir="$TEMPLATE_DIR/datasets"
    if [[ -d "$datasets_dir" ]]; then
        find "$datasets_dir" -name "*.json" | while IFS= read -r dataset_file; do
            validate_dataset_schema "$dataset_file"
        done
    fi
    
    # Validate template files
    validate_template_files "$TEMPLATE_DIR"
    
    # Template processing validation
    log "Validating template processing capabilities..."
    if [[ -f "$SCRIPT_DIR/template.sh" ]]; then
        if bash -n "$SCRIPT_DIR/template.sh"; then
            validate_pass "Template processor syntax check"
        else
            validate_fail "Template processor syntax error"
        fi
    fi
    
    # Input system integration validation
    log "Validating input system integration..."
    if [[ -f "$SCRIPT_DIR/input-system.sh" ]]; then
        if bash -n "$SCRIPT_DIR/input-system.sh"; then
            validate_pass "Input system syntax check"
        else
            validate_fail "Input system syntax error"
        fi
    fi
    
    # Print validation summary
    echo
    echo "═══════════════════════════════════════════════════════════════"
    echo -e "${BOLD}Validation Summary:${NC}"
    echo -e "  Total Validations: $VALIDATION_TOTAL"
    echo -e "  ${GREEN}Passed: $VALIDATION_PASSED${NC}"
    echo -e "  ${RED}Failed: $VALIDATION_FAILED${NC}"
    
    if [[ $VALIDATION_FAILED -eq 0 ]]; then
        echo
        success "🎉 All template validations passed! System is ready for production."
        
        if [[ "$DEV_MODE" == "true" ]]; then
            info "Development mode active - additional tools available in $UDEV/"
        fi
        
        return 0
    else
        echo
        error "❌ Validation failures detected. Please review and fix issues before proceeding."
        
        if [[ "$DEV_MODE" == "true" ]]; then
            info "Check $UDEV/validation/ for detailed error logs and fixing tools"
        fi
        
        return 1
    fi
}

# ═══════════════════════════════════════════════════════════════════════════════════════
# 🛠️ DEVELOPMENT MODE TOOLS
# ═══════════════════════════════════════════════════════════════════════════════════════

create_dev_tools() {
    if [[ "$DEV_MODE" != "true" ]]; then
        return 0
    fi
    
    log "Creating development mode tools..."
    
    # Template validator tool
    cat > "$UDEV/validate-template.sh" << 'EOF'
#!/bin/bash
# Development Template Validator
UDEV="$(dirname "$0")"
source "$UDEV/../uCode/template-validation.sh"

if [[ $# -eq 0 ]]; then
    echo "Usage: $0 <template-file>"
    exit 1
fi

validate_template_files "$(dirname "$1")"
EOF
    
    # Schema validator
    cat > "$UDEV/validate-schema.sh" << 'EOF'
#!/bin/bash
# JSON Schema Validator for Development
if command -v ajv >/dev/null 2>&1; then
    ajv validate -s "$1" -d "$2"
else
    echo "⚠️ ajv-cli not installed. Install with: npm install -g ajv-cli"
    exit 1
fi
EOF
    
    # Mock data generator
    cat > "$UDEV/generate-mock-data.sh" << 'EOF'
#!/bin/bash
# Mock Data Generator for Testing
UDEV="$(dirname "$0")"
mkdir -p "$UDEV/testing/mock-data"

echo "Generating mock dataget data..."
cat > "$UDEV/testing/mock-data/test-user-setup.json" << 'MOCK'
{
    "username": "testuser123",
    "full_name": "Test User",
    "email": "test@example.com",
    "location": "Test City, Test Country (TX01)",
    "timezone": "UTC",
    "primary_role": "developer",
    "password": "",
    "auto_backup": true,
    "debug_mode": false,
    "preferred_companion": "chester",
    "notification_level": "standard",
    "experimental_features": false
}
MOCK

echo "✅ Mock data generated in $UDEV/testing/mock-data/"
EOF
    
    chmod +x "$UDEV"/*.sh
    
    success "Development tools created in $UDEV/"
}

# ═══════════════════════════════════════════════════════════════════════════════════════
# 🚀 MAIN EXECUTION
# ═══════════════════════════════════════════════════════════════════════════════════════

main() {
    case "${1:-validate}" in
        "validate"|"test")
            run_comprehensive_validation
            ;;
        "dev"|"development")
            export UDOS_DEV_MODE=true
            setup_dev_mode
            create_dev_tools
            run_comprehensive_validation
            ;;
        "schemas")
            generate_validation_schemas
            ;;
        "help"|"-h"|"--help")
            echo "uDOS Template-Integrated Validation System"
            echo
            echo "Usage: $0 [command]"
            echo
            echo "Commands:"
            echo "  validate    Run comprehensive validation (default)"
            echo "  dev         Enable development mode with additional tools"
            echo "  schemas     Generate validation schemas only"
            echo "  help        Show this help message"
            echo
            echo "Environment Variables:"
            echo "  UDOS_DEV_MODE=true    Enable development mode"
            echo "  UHOME=path           Set uDOS home directory"
            ;;
        *)
            error "Unknown command: $1"
            echo "Run '$0 help' for usage information"
            exit 1
            ;;
    esac
}

# Run main function with all arguments
main "$@"
