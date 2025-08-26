#!/bin/bash
# JSON to uDATA Converter Script v1.0
# Converts regular JSON files to uDATA format (minified JSON, one record per line)

set -euo pipefail

# Configuration
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
UDOS_ROOT="${UDOS_ROOT:-$(cd "$SCRIPT_DIR/../../../" && pwd)}"
JSON_PROCESSOR="$UDOS_ROOT/uCORE/json"

# Colors
readonly RED='\033[0;31m'
readonly GREEN='\033[0;32m'
readonly YELLOW='\033[1;33m'
readonly BLUE='\033[0;34m'
readonly CYAN='\033[0;36m'
readonly NC='\033[0m'

# Helper functions
log_info() { echo -e "${BLUE}ℹ️  $1${NC}"; }
log_success() { echo -e "${GREEN}✅ $1${NC}"; }
log_warning() { echo -e "${YELLOW}⚠️  $1${NC}"; }
log_error() { echo -e "${RED}❌ $1${NC}"; }

# Show help
show_help() {
    echo -e "${CYAN}JSON to uDATA Converter v1.0${NC}"
    echo ""
    echo -e "${YELLOW}Usage:${NC}"
    echo "  $0 <input.json> [output.udata]"
    echo "  $0 --batch <directory>"
    echo "  $0 --validate <file.udata>"
    echo "  $0 --info <file.udata>"
    echo ""
    echo -e "${YELLOW}Examples:${NC}"
    echo "  $0 data.json data.udata              # Convert single file"
    echo "  $0 input.json                        # Auto-generate output name"
    echo "  $0 --batch /path/to/json/files/      # Convert all JSON in directory"
    echo "  $0 --validate config.udata           # Validate uDATA format"
    echo "  $0 --info system.udata               # Show uDATA file info"
    echo ""
    echo -e "${YELLOW}uDATA Format:${NC}"
    echo "  • Minified JSON records, one per line"
    echo "  • Preserves all original data structure"
    echo "  • Optimized for streaming and processing"
    echo "  • Human-readable with proper line breaks"
    echo ""
}

# Check if TypeScript system is available
check_typescript_system() {
    if [[ ! -d "$JSON_PROCESSOR" ]]; then
        log_error "uCORE JSON processor not found at $JSON_PROCESSOR"
        return 1
    fi

    if [[ ! -f "$JSON_PROCESSOR/package.json" ]]; then
        log_error "TypeScript system not initialized"
        return 1
    fi

    # Check if dependencies are installed
    if [[ ! -d "$JSON_PROCESSOR/node_modules" ]]; then
        log_info "Installing TypeScript dependencies..."
        cd "$JSON_PROCESSOR"
        npm install || {
            log_error "Failed to install dependencies"
            return 1
        }
        cd - > /dev/null
    fi

    # Build if needed
    if [[ ! -d "$JSON_PROCESSOR/dist" ]] || [[ "$JSON_PROCESSOR/src/udataParser.ts" -nt "$JSON_PROCESSOR/dist/udataParser.js" ]]; then
        log_info "Building TypeScript system..."
        cd "$JSON_PROCESSOR"
        npm run build || {
            log_error "Failed to build TypeScript system"
            return 1
        }
        cd - > /dev/null
    fi

    return 0
}

# Convert JSON to uDATA using Python (fallback)
convert_json_python() {
    local input_file="$1"
    local output_file="$2"

    log_info "Converting $input_file to uDATA format..."

    python3 << EOF
import json
import sys
import time

def convert_json_to_udata(input_path, output_path):
    try:
        print("🔄 Loading JSON data...")
        with open(input_path, 'r') as f:
            data = json.load(f)

        records = []

        print("📊 Processing data structure...")
        if isinstance(data, list):
            records = data
        elif isinstance(data, dict):
            # Handle metadata separately
            if 'metadata' in data:
                records.append({'metadata': data['metadata']})
                print("📋 ✓ Metadata record processed")
                del data['metadata']

            # Convert object properties to records
            for key, value in data.items():
                if isinstance(value, dict):
                    record = {'name': key}
                    record.update(value)
                    records.append(record)
                elif isinstance(value, list):
                    for item in value:
                        if isinstance(item, dict):
                            record = {'category': key}
                            record.update(item)
                            records.append(record)
                        else:
                            records.append({'category': key, 'value': item})
                else:
                    records.append({'name': key, 'value': value})

        print(f"🎯 Writing {len(records)} records to uDATA format...")
        print("┌─────────────────────────────────────────┐")
        print("│          uDATA MINIFICATION             │")
        print("└─────────────────────────────────────────┘")

        # Write uDATA format (one JSON record per line) with progress
        with open(output_path, 'w') as f:
            for i, record in enumerate(records, 1):
                minified_json = json.dumps(record, separators=(',', ':'))
                f.write(minified_json + '\n')

                # Show progress for every record
                if i <= 5 or i % max(1, len(records) // 10) == 0 or i == len(records):
                    progress = (i / len(records)) * 100
                    bar_length = 20
                    filled_length = int(bar_length * i // len(records))
                    bar = '█' * filled_length + '░' * (bar_length - filled_length)
                    print(f"📝 [{bar}] {progress:5.1f}% | Record {i:3d}/{len(records)} | {len(minified_json):4d} chars")

        print("┌─────────────────────────────────────────┐")
        print("│            ✨ COMPLETE ✨               │")
        print("└─────────────────────────────────────────┘")
        print(f"✅ Converted {len(records)} records to {output_path}")
        return True

    except Exception as e:
        print("┌─────────────────────────────────────────┐")
        print("│              ❌ ERROR ❌                │")
        print("└─────────────────────────────────────────┘")
        print(f"❌ Error: {e}")
        return False

convert_json_to_udata("$input_file", "$output_file")
EOF
}

# Convert JSON to uDATA using TypeScript
convert_json_typescript() {
    local input_file="$1"
    local output_file="$2"

    log_info "Converting $input_file to uDATA format using TypeScript..."

    cd "$JSON_PROCESSOR"
    node -e "
        const { uDATAParser } = require('./dist/udataParser');
        const success = uDATAParser.convertJsonToUDATA('$input_file', '$output_file');
        process.exit(success ? 0 : 1);
    " || {
        log_warning "TypeScript conversion failed, falling back to Python"
        convert_json_python "$input_file" "$output_file"
    }
    cd - > /dev/null
}

# Validate uDATA file
validate_udata() {
    local file="$1"

    if [[ ! -f "$file" ]]; then
        log_error "File not found: $file"
        return 1
    fi

    log_info "Validating uDATA file: $file"

    local line_count=0
    local valid_records=0
    local errors=0

    while IFS= read -r line; do
        ((line_count++))

        if [[ -z "${line// }" ]]; then
            continue  # Skip empty lines
        fi

        if echo "$line" | python3 -c "import json,sys; json.load(sys.stdin)" 2>/dev/null; then
            ((valid_records++))
        else
            log_error "Invalid JSON on line $line_count: $line"
            ((errors++))
        fi
    done < "$file"

    if [[ $errors -eq 0 ]]; then
        log_success "Valid uDATA file: $valid_records records, 0 errors"
        return 0
    else
        log_error "Invalid uDATA file: $errors errors found"
        return 1
    fi
}

# Show uDATA file information
show_udata_info() {
    local file="$1"

    if [[ ! -f "$file" ]]; then
        log_error "File not found: $file"
        return 1
    fi

    log_info "uDATA File Information: $file"
    echo ""

    local total_lines=$(wc -l < "$file")
    local record_count=0
    local metadata_records=0
    local data_records=0
    local file_size=$(ls -lh "$file" | awk '{print $5}')

    # Count record types
    while IFS= read -r line; do
        if [[ -n "${line// }" ]]; then
            ((record_count++))
            if echo "$line" | grep -q '"metadata"'; then
                ((metadata_records++))
            else
                ((data_records++))
            fi
        fi
    done < "$file"

    echo -e "${CYAN}📊 Statistics:${NC}"
    echo "  Total Lines: $total_lines"
    echo "  Records: $record_count"
    echo "  Metadata Records: $metadata_records"
    echo "  Data Records: $data_records"
    echo "  File Size: $file_size"
    echo ""

    # Show first few records as sample
    echo -e "${CYAN}📋 Sample Records:${NC}"
    head -3 "$file" | while IFS= read -r line; do
        if [[ -n "${line// }" ]]; then
            echo "  $line"
        fi
    done
    echo ""

    # Check for metadata
    if [[ $metadata_records -gt 0 ]]; then
        echo -e "${CYAN}🏷️  Metadata:${NC}"
        grep '"metadata"' "$file" | head -1 | python3 -c "
import json, sys
line = sys.stdin.readline()
if line.strip():
    data = json.loads(line)
    if 'metadata' in data:
        for key, value in data['metadata'].items():
            print(f'  {key}: {value}')
" 2>/dev/null || echo "  (Could not parse metadata)"
    fi
}

# Batch convert directory
batch_convert() {
    local directory="$1"

    if [[ ! -d "$directory" ]]; then
        log_error "Directory not found: $directory"
        return 1
    fi

    log_info "Batch converting JSON files in: $directory"

    local converted=0
    local failed=0

    find "$directory" -name "*.json" -type f | while read -r json_file; do
        local basename=$(basename "$json_file" .json)
        local output_file="${json_file%/*}/${basename}.udata"

        if convert_json_typescript "$json_file" "$output_file"; then
            ((converted++))
        else
            ((failed++))
        fi
    done

    log_success "Batch conversion complete: $converted successful, $failed failed"
}

# Main function
main() {
    if [[ $# -eq 0 ]]; then
        show_help
        exit 0
    fi

    case "$1" in
        --help|-h)
            show_help
            exit 0
            ;;
        --validate)
            if [[ $# -lt 2 ]]; then
                log_error "Please specify uDATA file to validate"
                exit 1
            fi
            validate_udata "$2"
            ;;
        --info)
            if [[ $# -lt 2 ]]; then
                log_error "Please specify uDATA file to analyze"
                exit 1
            fi
            show_udata_info "$2"
            ;;
        --batch)
            if [[ $# -lt 2 ]]; then
                log_error "Please specify directory for batch conversion"
                exit 1
            fi
            check_typescript_system || exit 1
            batch_convert "$2"
            ;;
        *)
            # Regular conversion
            local input_file="$1"
            local output_file="${2:-${input_file%.*}.udata}"

            if [[ ! -f "$input_file" ]]; then
                log_error "Input file not found: $input_file"
                exit 1
            fi

            # Try TypeScript first, fallback to Python
            if check_typescript_system; then
                convert_json_typescript "$input_file" "$output_file"
            else
                log_warning "TypeScript system not available, using Python fallback"
                convert_json_python "$input_file" "$output_file"
            fi

            # Validate the result
            if validate_udata "$output_file"; then
                log_success "Conversion completed successfully!"
                show_udata_info "$output_file"
            else
                log_error "Conversion failed validation"
                exit 1
            fi
            ;;
    esac
}

# Execute main function
main "$@"
