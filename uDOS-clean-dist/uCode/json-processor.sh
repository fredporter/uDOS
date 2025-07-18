#!/bin/bash

# uDOS JSON Dataset Processing Script
# Version: 1.7.1
# Description: Process and import JSON datasets into uDOS template system

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
TEMPLATE_DIR="$SCRIPT_DIR/../uTemplate"
DATASET_DIR="$TEMPLATE_DIR/datasets"
MEMORY_DIR="$SCRIPT_DIR/../uMemory"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Logging function
log() {
    echo -e "${BLUE}[$(date +'%Y-%m-%d %H:%M:%S')]${NC} $1"
}

error() {
    echo -e "${RED}[ERROR]${NC} $1" >&2
}

success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

# Function to validate JSON files
validate_json() {
    local file="$1"
    if ! jq . "$file" > /dev/null 2>&1; then
        error "Invalid JSON in file: $file"
        return 1
    fi
    return 0
}

# Function to list available datasets
list_datasets() {
    log "Available JSON datasets in $DATASET_DIR:"
    echo ""
    
    if [ -d "$DATASET_DIR" ]; then
        for file in "$DATASET_DIR"/*.json; do
            if [ -f "$file" ]; then
                local basename=$(basename "$file" .json)
                local size=$(ls -lh "$file" | awk '{print $5}')
                local count=$(jq length "$file" 2>/dev/null || echo "N/A")
                printf "  📄 %-25s %s records, %s\n" "$basename" "$count" "$size"
            fi
        done
    else
        warning "Dataset directory not found: $DATASET_DIR"
    fi
    echo ""
}

# Function to show dataset info
show_dataset_info() {
    local dataset="$1"
    local file="$DATASET_DIR/${dataset}.json"
    
    if [ ! -f "$file" ]; then
        error "Dataset not found: $dataset"
        return 1
    fi
    
    log "Dataset Information: $dataset"
    echo ""
    
    if validate_json "$file"; then
        local records=$(jq length "$file")
        local size=$(ls -lh "$file" | awk '{print $5}')
        
        echo "📊 Records: $records"
        echo "📦 Size: $size"
        echo "📍 Location: $file"
        echo ""
        
        # Show first record structure
        log "Sample Record Structure:"
        jq '.[0] // {}' "$file" | jq 'keys[]' -r | sed 's/^/  • /'
        echo ""
        
        # Show first few records
        log "Sample Data (first 3 records):"
        jq '.[:3]' "$file"
    fi
}

# Function to search datasets
search_datasets() {
    local query="$1"
    log "Searching for: '$query'"
    echo ""
    
    for file in "$DATASET_DIR"/*.json; do
        if [ -f "$file" ]; then
            local basename=$(basename "$file" .json)
            if jq -r '.[] | @json' "$file" | grep -i "$query" > /dev/null 2>&1; then
                local matches=$(jq -r '.[] | @json' "$file" | grep -i "$query" | wc -l)
                printf "  🔍 %-25s %d matches\n" "$basename" "$matches"
            fi
        fi
    done
    echo ""
}

# Function to export dataset to different formats
export_dataset() {
    local dataset="$1"
    local format="$2"
    local output_dir="$3"
    
    local source_file="$DATASET_DIR/${dataset}.json"
    
    if [ ! -f "$source_file" ]; then
        error "Dataset not found: $dataset"
        return 1
    fi
    
    [ -z "$output_dir" ] && output_dir="$MEMORY_DIR/exports"
    mkdir -p "$output_dir"
    
    case "$format" in
        "csv")
            local output_file="$output_dir/${dataset}.csv"
            log "Exporting $dataset to CSV format..."
            if jq -r '(.[0] | keys_unsorted) as $keys | $keys, (.[] | [.[$keys[]]]) | @csv' "$source_file" > "$output_file"; then
                success "Exported to: $output_file"
            else
                error "Failed to export to CSV"
                return 1
            fi
            ;;
        "tsv")
            local output_file="$output_dir/${dataset}.tsv"
            log "Exporting $dataset to TSV format..."
            if jq -r '(.[0] | keys_unsorted) as $keys | $keys, (.[] | [.[$keys[]]]) | @tsv' "$source_file" > "$output_file"; then
                success "Exported to: $output_file"
            else
                error "Failed to export to TSV"
                return 1
            fi
            ;;
        "yaml"|"yml")
            local output_file="$output_dir/${dataset}.yml"
            log "Exporting $dataset to YAML format..."
            if command -v yq > /dev/null 2>&1; then
                if yq eval -P '.' "$source_file" > "$output_file"; then
                    success "Exported to: $output_file"
                else
                    error "Failed to export to YAML"
                    return 1
                fi
            else
                error "yq command not found. Install yq to export YAML format."
                return 1
            fi
            ;;
        "txt")
            local output_file="$output_dir/${dataset}.txt"
            log "Exporting $dataset to text format..."
            if jq -r '.[] | @json' "$source_file" > "$output_file"; then
                success "Exported to: $output_file"
            else
                error "Failed to export to text"
                return 1
            fi
            ;;
        *)
            error "Unsupported format: $format"
            error "Supported formats: csv, tsv, yaml, yml, txt"
            return 1
            ;;
    esac
}

# Function to merge datasets
merge_datasets() {
    local output_name="$1"
    shift
    local datasets=("$@")
    
    if [ ${#datasets[@]} -lt 2 ]; then
        error "Need at least 2 datasets to merge"
        return 1
    fi
    
    local output_file="$DATASET_DIR/${output_name}.json"
    local temp_file=$(mktemp)
    
    log "Merging datasets: ${datasets[*]}"
    
    # Start with empty array
    echo "[]" > "$temp_file"
    
    for dataset in "${datasets[@]}"; do
        local source_file="$DATASET_DIR/${dataset}.json"
        if [ ! -f "$source_file" ]; then
            error "Dataset not found: $dataset"
            rm -f "$temp_file"
            return 1
        fi
        
        log "Adding $dataset..."
        jq -s '.[0] + .[1]' "$temp_file" "$source_file" > "${temp_file}.tmp"
        mv "${temp_file}.tmp" "$temp_file"
    done
    
    mv "$temp_file" "$output_file"
    success "Merged datasets saved to: $output_file"
    
    local total_records=$(jq length "$output_file")
    log "Total records in merged dataset: $total_records"
}

# Function to validate all datasets
validate_all() {
    log "Validating all JSON datasets..."
    echo ""
    
    local valid_count=0
    local total_count=0
    
    for file in "$DATASET_DIR"/*.json; do
        if [ -f "$file" ]; then
            local basename=$(basename "$file" .json)
            total_count=$((total_count + 1))
            
            if validate_json "$file"; then
                printf "  ✅ %-25s Valid\n" "$basename"
                valid_count=$((valid_count + 1))
            else
                printf "  ❌ %-25s Invalid JSON\n" "$basename"
            fi
        fi
    done
    
    echo ""
    log "Validation Summary: $valid_count/$total_count datasets are valid"
    
    if [ $valid_count -eq $total_count ]; then
        success "All datasets are valid! 🎉"
        return 0
    else
        error "Some datasets have validation errors"
        return 1
    fi
}

# Function to show statistics
show_stats() {
    log "Dataset Statistics Summary"
    echo ""
    
    local total_files=0
    local total_records=0
    local total_size=0
    
    for file in "$DATASET_DIR"/*.json; do
        if [ -f "$file" ]; then
            local basename=$(basename "$file" .json)
            local records=$(jq length "$file" 2>/dev/null || echo 0)
            local size_bytes=$(stat -f%z "$file" 2>/dev/null || stat -c%s "$file" 2>/dev/null || echo 0)
            
            total_files=$((total_files + 1))
            total_records=$((total_records + records))
            total_size=$((total_size + size_bytes))
            
            printf "  📊 %-25s %6d records\n" "$basename" "$records"
        fi
    done
    
    echo ""
    log "Summary:"
    echo "  📁 Total datasets: $total_files"
    echo "  📄 Total records: $total_records"
    
    # Convert bytes to human readable
    if command -v numfmt > /dev/null 2>&1; then
        local human_size=$(echo $total_size | numfmt --to=iec)
        echo "  💾 Total size: $human_size"
    else
        echo "  💾 Total size: $total_size bytes"
    fi
}

# Main function
main() {
    local command="$1"
    
    echo "🔧 uDOS JSON Dataset Processor v1.7.1"
    echo "========================================"
    echo ""
    
    case "$command" in
        "list"|"ls")
            list_datasets
            ;;
        "info")
            if [ -z "$2" ]; then
                error "Usage: $0 info <dataset_name>"
                exit 1
            fi
            show_dataset_info "$2"
            ;;
        "search")
            if [ -z "$2" ]; then
                error "Usage: $0 search <query>"
                exit 1
            fi
            search_datasets "$2"
            ;;
        "export")
            if [ -z "$2" ] || [ -z "$3" ]; then
                error "Usage: $0 export <dataset_name> <format> [output_dir]"
                error "Formats: csv, tsv, yaml, yml, txt"
                exit 1
            fi
            export_dataset "$2" "$3" "$4"
            ;;
        "merge")
            if [ $# -lt 3 ]; then
                error "Usage: $0 merge <output_name> <dataset1> <dataset2> [dataset3...]"
                exit 1
            fi
            shift
            merge_datasets "$@"
            ;;
        "validate")
            validate_all
            ;;
        "stats")
            show_stats
            ;;
        "help"|"--help"|"-h"|"")
            cat << EOF
uDOS JSON Dataset Processor v1.7.1

USAGE:
    $0 <command> [arguments]

COMMANDS:
    list, ls                    List all available datasets
    info <dataset>              Show detailed information about a dataset
    search <query>              Search for data across all datasets
    export <dataset> <format>   Export dataset to different format
    merge <output> <ds1> <ds2>  Merge multiple datasets into one
    validate                    Validate all JSON datasets
    stats                       Show dataset statistics summary
    help                        Show this help message

EXAMPLES:
    $0 list                     # List all datasets
    $0 info cityMap             # Show info about cityMap dataset
    $0 search "London"          # Search for "London" across datasets
    $0 export cityMap csv       # Export cityMap to CSV format
    $0 merge worldData cityMap countryMap  # Merge datasets
    $0 validate                 # Validate all datasets
    $0 stats                    # Show statistics summary

SUPPORTED EXPORT FORMATS:
    csv      Comma-separated values
    tsv      Tab-separated values
    yaml     YAML format (requires yq)
    txt      Plain text (JSON lines)

EOF
            ;;
        *)
            error "Unknown command: $command"
            error "Run '$0 help' for usage information"
            exit 1
            ;;
    esac
}

# Run main function with all arguments
main "$@"
