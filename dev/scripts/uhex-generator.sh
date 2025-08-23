#!/bin/bash
# uHEX Generator - Generate 8-character hexadecimal identifiers for uDOS files
# Used for consistent naming across development artifacts

set -euo pipefail

# Generate uHEX using multiple methods for maximum compatibility
# Falls back to YYYYMMDD format on any error (as per dev mode protocol)
generate_uhex() {
    local uhex=""
    
    # Method 1: OpenSSL (most common)
    if command -v openssl >/dev/null 2>&1; then
        uhex="$(openssl rand -hex 4 2>/dev/null || echo "")"
    fi
    
    # Method 2: /dev/urandom (Unix systems)
    if [[ -z "$uhex" && -r /dev/urandom ]]; then
        uhex="$(head -c 4 /dev/urandom 2>/dev/null | od -An -tx1 2>/dev/null | tr -d ' \n' || echo "")"
    fi
    
    # Method 3: Date + MD5 (fallback)
    if [[ -z "$uhex" ]] && command -v md5sum >/dev/null 2>&1; then
        uhex="$(date +"%Y%m%d%H%M%S%N" 2>/dev/null | md5sum 2>/dev/null | cut -c1-8 || echo "")"
    fi
    
    # Method 4: Date + shasum (macOS fallback)
    if [[ -z "$uhex" ]] && command -v shasum >/dev/null 2>&1; then
        uhex="$(date +"%Y%m%d%H%M%S" 2>/dev/null | shasum 2>/dev/null | cut -c1-8 || echo "")"
    fi
    
    # Method 5: Error fallback - YYYYMMDD format (dev mode protocol)
    if [[ -z "$uhex" ]]; then
        uhex="$(date +%Y%m%d 2>/dev/null || echo "$(date +%Y%m%d)")"
        log_warning "uHEX generation failed, using date format: $uhex" >&2
    fi
    
    # Ensure lowercase and proper length
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

# Generate dev mode filename (date-based, no uHEX)
generate_dev_filename() {
    local prefix="${1:-uDEV}"
    local description="${2:-}"
    local extension="${3:-md}"
    local date_part="$(date +%Y%m%d 2>/dev/null || echo "unknown")"
    
    if [[ -n "$description" ]]; then
        # Clean description for filename
        local clean_desc="$(echo "$description" | sed 's/[^a-zA-Z0-9-]/-/g' | sed 's/--*/-/g' | sed 's/^-\|-$//g')"
        echo "${prefix}-${date_part}-${clean_desc}.${extension}"
    else
        echo "${prefix}-${date_part}.${extension}"
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
  uhex-generator.sh filename PREFIX DESC [EXT] - Generate full filename (production mode)
  uhex-generator.sh devname PREFIX DESC [EXT]  - Generate dev mode filename (date-based)
  uhex-generator.sh validate UHEX              - Validate uHEX format
  uhex-generator.sh extract FILENAME           - Extract uHEX/date from filename
  uhex-generator.sh batch COUNT [PREFIX]       - Generate multiple uHEX
  uhex-generator.sh convert FILE [PREFIX]      - Convert file to uHEX naming
  uhex-generator.sh help                       - Show this help

Examples:
  uhex-generator.sh generate
  # Output: a1b2c3d4

  uhex-generator.sh filename uDEV "Session Notes"
  # Output (Production): uDEV-a1b2c3d4-20250821-Session-Notes.md

  uhex-generator.sh devname uDEV "Session Notes"  
  # Output (Dev Mode): uDEV-20250821-Session-Notes.md

  uhex-generator.sh validate a1b2c3d4
  # Exit code 0 if valid, 1 if invalid

  uhex-generator.sh extract "uDEV-20250821-Session.md"
  # Output: 20250821 (date format in dev mode)

Naming Conventions:
  Production Mode: PREFIX-UHEX-YYYYMMDD-Description.ext
  Dev Mode:       PREFIX-YYYYMMDD-Description.ext
  Error Fallback: Always defaults to YYYYMMDD format

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
        devname|dev)
            generate_dev_filename "${2:-uDEV}" "${3:-}" "${4:-md}"
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
