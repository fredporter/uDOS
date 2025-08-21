#!/bin/bash
# uHEX Generator - Generate 8-character hexadecimal identifiers for uDOS files
# Used for consistent naming across development artifacts

set -euo pipefail

# Generate uHEX using multiple methods for maximum compatibility
generate_uhex() {
    local uhex=""
    
    # Method 1: OpenSSL (most common)
    if command -v openssl >/dev/null 2>&1; then
        uhex="$(openssl rand -hex 4)"
    # Method 2: /dev/urandom (Unix systems)
    elif [[ -r /dev/urandom ]]; then
        uhex="$(head -c 4 /dev/urandom | od -An -tx1 | tr -d ' \n')"
    # Method 3: Date + MD5 (fallback)
    elif command -v md5sum >/dev/null 2>&1; then
        uhex="$(date +"%Y%m%d%H%M%S%N" | md5sum | cut -c1-8)"
    # Method 4: Date + shasum (macOS fallback)
    elif command -v shasum >/dev/null 2>&1; then
        uhex="$(date +"%Y%m%d%H%M%S" | shasum | cut -c1-8)"
    # Method 5: Simple date-based (last resort)
    else
        uhex="$(date +"%H%M%S%N" | tail -c 9 | head -c 8)"
    fi
    
    # Ensure lowercase and 8 characters
    echo "$uhex" | tr '[:upper:]' '[:lower:]' | head -c 8
}

# Generate filename with uHEX prefix
generate_filename() {
    local prefix="${1:-uDEV}"
    local description="${2:-}"
    local extension="${3:-md}"
    local uhex="$(generate_uhex)"
    local date_part="$(date +%Y%m%d)"
    
    if [[ -n "$description" ]]; then
        # Clean description for filename
        local clean_desc="$(echo "$description" | sed 's/[^a-zA-Z0-9-]/-/g' | sed 's/--*/-/g' | sed 's/^-\|-$//g')"
        echo "${prefix}-${uhex}-${date_part}-${clean_desc}.${extension}"
    else
        echo "${prefix}-${uhex}-${date_part}.${extension}"
    fi
}

# Validate uHEX format
validate_uhex() {
    local uhex="$1"
    
    if [[ ${#uhex} -eq 8 && "$uhex" =~ ^[0-9a-f]+$ ]]; then
        return 0
    else
        return 1
    fi
}

# Extract uHEX from filename
extract_uhex() {
    local filename="$1"
    local uhex=""
    
    # Extract pattern: PREFIX-XXXXXXXX-...
    if [[ "$filename" =~ [a-zA-Z]+-([0-9a-f]{8})- ]]; then
        uhex="${BASH_REMATCH[1]}"
        if validate_uhex "$uhex"; then
            echo "$uhex"
            return 0
        fi
    fi
    
    return 1
}

# Batch generate multiple uHEX values
batch_generate() {
    local count="${1:-1}"
    local prefix="${2:-}"
    
    for ((i=1; i<=count; i++)); do
        local uhex="$(generate_uhex)"
        if [[ -n "$prefix" ]]; then
            echo "${prefix}${uhex}"
        else
            echo "$uhex"
        fi
    done
}

# Convert existing file to uHEX naming
convert_to_uhex() {
    local file_path="$1"
    local prefix="${2:-uDEV}"
    
    if [[ ! -f "$file_path" ]]; then
        echo "Error: File not found: $file_path" >&2
        return 1
    fi
    
    local dir="$(dirname "$file_path")"
    local basename="$(basename "$file_path")"
    local extension="${basename##*.}"
    local name="${basename%.*}"
    
    # Check if already has uHEX format
    if extract_uhex "$basename" >/dev/null 2>&1; then
        echo "File already has uHEX format: $basename"
        return 0
    fi
    
    # Generate new filename
    local new_filename="$(generate_filename "$prefix" "$name" "$extension")"
    local new_path="$dir/$new_filename"
    
    # Move file
    mv "$file_path" "$new_path"
    echo "Converted: $basename -> $new_filename"
    echo "New path: $new_path"
}

# Help function
show_help() {
    cat << 'EOF'
uHEX Generator - Generate 8-character hex identifiers for uDOS files

Usage:
  uhex-generator.sh generate                    - Generate single uHEX
  uhex-generator.sh filename PREFIX DESC [EXT] - Generate full filename
  uhex-generator.sh validate UHEX              - Validate uHEX format
  uhex-generator.sh extract FILENAME           - Extract uHEX from filename
  uhex-generator.sh batch COUNT [PREFIX]       - Generate multiple uHEX
  uhex-generator.sh convert FILE [PREFIX]      - Convert file to uHEX naming
  uhex-generator.sh help                       - Show this help

Examples:
  uhex-generator.sh generate
  # Output: a1b2c3d4

  uhex-generator.sh filename uDEV "Session Notes"
  # Output: uDEV-a1b2c3d4-20250821-Session-Notes.md

  uhex-generator.sh validate a1b2c3d4
  # Exit code 0 if valid, 1 if invalid

  uhex-generator.sh extract "uDEV-a1b2c3d4-Session.md"
  # Output: a1b2c3d4

  uhex-generator.sh batch 5
  # Output: 5 uHEX values, one per line

  uhex-generator.sh convert "old-file.md" uDOC
  # Renames file to uDOC-XXXXXXXX-YYYYMMDD-old-file.md

Prefix Types:
  uDEV - Development session files
  uLOG - Implementation logs
  uDOC - Documentation files
  uTASK - Task tracking files
  uROAD - Roadmap files
  uNOTE - General notes
  uTEST - Test files
  uDATA - Data files
EOF
}

# Main command processing
main() {
    case "${1:-generate}" in
        generate|gen)
            generate_uhex
            ;;
        filename|file)
            generate_filename "${2:-uDEV}" "${3:-}" "${4:-md}"
            ;;
        validate|val)
            if [[ -z "${2:-}" ]]; then
                echo "Error: uHEX value required" >&2
                exit 1
            fi
            if validate_uhex "$2"; then
                echo "Valid uHEX: $2"
                exit 0
            else
                echo "Invalid uHEX: $2" >&2
                exit 1
            fi
            ;;
        extract|ext)
            if [[ -z "${2:-}" ]]; then
                echo "Error: Filename required" >&2
                exit 1
            fi
            extract_uhex "$2"
            ;;
        batch)
            batch_generate "${2:-1}" "${3:-}"
            ;;
        convert|conv)
            if [[ -z "${2:-}" ]]; then
                echo "Error: File path required" >&2
                exit 1
            fi
            convert_to_uhex "$2" "${3:-uDEV}"
            ;;
        help|--help|-h)
            show_help
            ;;
        *)
            echo "Error: Unknown command: $1" >&2
            echo "Use 'uhex-generator.sh help' for usage information" >&2
            exit 1
            ;;
    esac
}

# Execute if run directly
if [[ "${BASH_SOURCE[0]}" == "${0}" ]]; then
    main "$@"
fi
