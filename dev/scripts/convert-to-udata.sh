#!/bin/bash
# Simple JSON to uDATA converter for uDOS v1.3.3
# Converts existing JSON files to the new minified uDATA format

set -euo pipefail

# Minify JSON - remove unnecessary whitespace and newlines
minify_json() {
    local json_data="$1"

    # Remove comments (// and /* */)
    json_data=$(echo "$json_data" | sed 's|//.*$||g' | sed 's|/\*.*\*/||g')

    # Remove leading/trailing whitespace from each line
    json_data=$(echo "$json_data" | sed 's/^[[:space:]]*//' | sed 's/[[:space:]]*$//')

    # Remove empty lines
    json_data=$(echo "$json_data" | grep -v '^$')

    # Minify: remove spaces around operators and separators
    json_data=$(echo "$json_data" | tr -d '\n\r' | \
        sed 's/[[:space:]]*:[[:space:]]*/:/g' | \
        sed 's/[[:space:]]*,[[:space:]]*/,/g' | \
        sed 's/[[:space:]]*{[[:space:]]*/\{/g' | \
        sed 's/[[:space:]]*}[[:space:]]*/\}/g' | \
        sed 's/[[:space:]]*\[[[:space:]]*/\[/g' | \
        sed 's/[[:space:]]*\][[:space:]]*/\]/g')

    echo "$json_data"
}

# Format JSON for one-record-per-line output
format_one_record_per_line() {
    local json_data="$1"

    # Use Python to properly handle both arrays and objects
    echo "$json_data" | python3 -c "
import json
import sys
try:
    data = json.loads(sys.stdin.read())
    if isinstance(data, list):
        # Array: output each element on a separate line (compact but readable)
        for item in data:
            print(json.dumps(item, separators=(', ', ': '), ensure_ascii=False))
    else:
        # Single object: output as is (compact but readable)
        print(json.dumps(data, separators=(', ', ': '), ensure_ascii=False))
except Exception as e:
    # Fallback: output original content
    sys.stderr.write(f'JSON parsing error: {e}\n')
    sys.exit(1)
"
}

# Generate uDATA filename
generate_udata_filename() {
    local original_name="$1"
    local date="$(date +%Y%m%d)"

    # Extract base name without .json
    local base_name=$(basename "$original_name" .json)

    # Convert to kebab-case and sanitize
    local clean_name=$(echo "$base_name" | tr '_' '-' | tr -cd '[:alnum:]-')

    echo "uDATA-${date}-${clean_name}.json"
}

# Convert single JSON file
convert_json_file() {
    local input_file="$1"
    local output_dir="$2"

    echo "Converting: $input_file"

    if [[ ! -f "$input_file" ]]; then
        echo "ERROR: File not found: $input_file"
        return 1
    fi

    # Generate output filename
    local output_filename=$(generate_udata_filename "$(basename "$input_file")")
    local output_path="$output_dir/$output_filename"

    # Read and process JSON
    local json_content=$(cat "$input_file")
    local processed_json=$(format_one_record_per_line "$json_content")

    # Write to output file
    echo "$processed_json" > "$output_path"

    echo "  → Created: $output_path"
    echo "  → Records: $(echo "$processed_json" | wc -l | tr -d ' ') lines"

    # Show compression stats
    local original_size=$(wc -c < "$input_file")
    local processed_size=$(wc -c < "$output_path")
    if [[ $original_size -gt 0 ]]; then
        local compression_ratio=$(( (original_size - processed_size) * 100 / original_size ))
        echo "  → Compression: ${compression_ratio}% (${original_size} → ${processed_size} bytes)"
    else
        echo "  → Compression: N/A (empty file: ${original_size} → ${processed_size} bytes)"
    fi
    echo
}

# Main conversion function
main() {
    echo "uDOS JSON to uDATA Converter v1.3.3"
    echo "==================================="
    echo

    # Create output directory structure
    local base_output_dir="/Users/agentdigital/uDOS"
    local system_output_dir="$base_output_dir/uMEMORY/system/udata-converted"
    local config_output_dir="$base_output_dir/uCORE/config/udata-converted"
    local templates_output_dir="$base_output_dir/uMEMORY/system/templates/udata-converted"
    local permissions_output_dir="$base_output_dir/permissions/udata-converted"

    mkdir -p "$system_output_dir"
    mkdir -p "$config_output_dir"
    mkdir -p "$templates_output_dir"
    mkdir -p "$permissions_output_dir"

    # System JSON files to convert
    local system_files=(
        "/Users/agentdigital/uDOS/uMEMORY/system/commands.json:$system_output_dir"
        "/Users/agentdigital/uDOS/uMEMORY/system/dynamic-commands.json:$system_output_dir"
        "/Users/agentdigital/uDOS/uMEMORY/system/user-roles.json:$system_output_dir"
        "/Users/agentdigital/uDOS/uMEMORY/system/emoji-support.json:$system_output_dir"
        "/Users/agentdigital/uDOS/uMEMORY/system/shortcodes.json:$system_output_dir"
        "/Users/agentdigital/uDOS/uMEMORY/system/ucode-commands.json:$system_output_dir"
        "/Users/agentdigital/uDOS/uMEMORY/system/variable-system.json:$system_output_dir"
        "/Users/agentdigital/uDOS/uMEMORY/system/vb-commands.json:$system_output_dir"
        "/Users/agentdigital/uDOS/uMEMORY/system/installation-lifespan.json:$system_output_dir"
        "/Users/agentdigital/uDOS/uMEMORY/system/colors/color-palettes.json:$system_output_dir"
        "/Users/agentdigital/uDOS/uMEMORY/system/colors/color-palettes-final.json:$system_output_dir"
        "/Users/agentdigital/uDOS/uMEMORY/system/fonts/font-registry.json:$system_output_dir"
    )

    # uCORE config files
    local config_files=(
        "/Users/agentdigital/uDOS/uCORE/config/dataset-metadata.json:$config_output_dir"
        "/Users/agentdigital/uDOS/uCORE/config/shortcode-integration-v2.1.json:$config_output_dir"
        "/Users/agentdigital/uDOS/uCORE/config/template-definitions.json:$config_output_dir"
        "/Users/agentdigital/uDOS/uCORE/config/template-system-config.json:$config_output_dir"
        "/Users/agentdigital/uDOS/uCORE/config/vb-integration-config.json:$config_output_dir"
        "/Users/agentdigital/uDOS/uCORE/config/vb-template-categories.json:$config_output_dir"
        "/Users/agentdigital/uDOS/uCORE/config/vscode-teletext-settings.json:$config_output_dir"
    )

    # Template system files
    local template_files=(
        "/Users/agentdigital/uDOS/uMEMORY/system/get/mission-create.json:$templates_output_dir"
        "/Users/agentdigital/uDOS/uMEMORY/system/get/system-config.json:$templates_output_dir"
        "/Users/agentdigital/uDOS/uMEMORY/system/get/user-setup.json:$templates_output_dir"
        "/Users/agentdigital/uDOS/uMEMORY/system/templates/system/error-config.json:$templates_output_dir"
        "/Users/agentdigital/uDOS/uMEMORY/system/templates/system/shortcodes.json:$templates_output_dir"
        "/Users/agentdigital/uDOS/uMEMORY/system/templates/variables/env.json:$templates_output_dir"
        "/Users/agentdigital/uDOS/uMEMORY/system/templates/variables/session.json:$templates_output_dir"
        "/Users/agentdigital/uDOS/uMEMORY/system/templates/variables/user-vars.json:$templates_output_dir"
    )

    # Permission files
    local permission_files=(
        "/Users/agentdigital/uDOS/wizard/permissions.json:$permissions_output_dir"
        "/Users/agentdigital/uDOS/sorcerer/permissions.json:$permissions_output_dir"
        "/Users/agentdigital/uDOS/imp/permissions.json:$permissions_output_dir"
        "/Users/agentdigital/uDOS/drone/permissions.json:$permissions_output_dir"
        "/Users/agentdigital/uDOS/ghost/permissions.json:$permissions_output_dir"
        "/Users/agentdigital/uDOS/tomb/permissions.json:$permissions_output_dir"
    )

    # Combine all file arrays
    local all_files=("${system_files[@]}" "${config_files[@]}" "${template_files[@]}" "${permission_files[@]}")

    local converted_count=0
    local failed_count=0
    local skipped_count=0

    echo "Converting ALL system JSON files to uDATA format..."
    echo "📁 System files → $system_output_dir"
    echo "⚙️  Config files → $config_output_dir"
    echo "📝 Template files → $templates_output_dir"
    echo "🔐 Permission files → $permissions_output_dir"
    echo

    for file_spec in "${all_files[@]}"; do
        local json_file="${file_spec%:*}"
        local output_dir="${file_spec#*:}"

        if [[ -f "$json_file" ]]; then
            if convert_json_file "$json_file" "$output_dir"; then
                ((converted_count++))
            else
                ((failed_count++))
                echo "FAILED: $json_file"
                echo
            fi
        else
            echo "SKIPPED: $json_file (not found)"
            ((skipped_count++))
            echo
        fi
    done

    echo "=========================================="
    echo "🎉 COMPREHENSIVE uDATA CONVERSION COMPLETE"
    echo "=========================================="
    echo "  ✅ Converted: $converted_count files"
    echo "  ❌ Failed: $failed_count files"
    echo "  ⏭️  Skipped: $skipped_count files"
    echo
    echo "📊 Output Locations:"
    echo "  🗂️  System: $system_output_dir"
    echo "  ⚙️  Config: $config_output_dir"
    echo "  📝 Templates: $templates_output_dir"
    echo "  🔐 Permissions: $permissions_output_dir"
    echo

    # Show summary of created files
    echo "📋 Created uDATA files by category:"
    echo
    if [[ -d "$system_output_dir" ]]; then
        echo "🗂️  SYSTEM FILES:"
        ls -la "$system_output_dir/" 2>/dev/null | grep -v "^total" | grep -v "^d" || echo "   (none created)"
        echo
    fi

    if [[ -d "$config_output_dir" ]]; then
        echo "⚙️  CONFIG FILES:"
        ls -la "$config_output_dir/" 2>/dev/null | grep -v "^total" | grep -v "^d" || echo "   (none created)"
        echo
    fi

    if [[ -d "$templates_output_dir" ]]; then
        echo "📝 TEMPLATE FILES:"
        ls -la "$templates_output_dir/" 2>/dev/null | grep -v "^total" | grep -v "^d" || echo "   (none created)"
        echo
    fi

    if [[ -d "$permissions_output_dir" ]]; then
        echo "🔐 PERMISSION FILES:"
        ls -la "$permissions_output_dir/" 2>/dev/null | grep -v "^total" | grep -v "^d" || echo "   (none created)"
        echo
    fi
}

# Run the converter
main "$@"
