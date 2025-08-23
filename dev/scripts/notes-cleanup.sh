#!/bin/bash
# Development Notes Cleanup Script
# Maintains organization and cleanliness of dev/notes/ directory

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Script directory
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
NOTES_DIR="$(dirname "$SCRIPT_DIR")/notes"
UDOS_ROOT="$(dirname "$(dirname "$SCRIPT_DIR")")"

echo -e "${BLUE}🧹 Development Notes Cleanup Utility${NC}"
echo "====================================="

# Function to log actions
log_info() { echo -e "${BLUE}ℹ️  $1${NC}"; }
log_success() { echo -e "${GREEN}✅ $1${NC}"; }
log_warning() { echo -e "${YELLOW}⚠️  $1${NC}"; }
log_error() { echo -e "${RED}❌ $1${NC}"; }

# Change to notes directory
cd "$NOTES_DIR" || { log_error "Cannot access notes directory: $NOTES_DIR"; exit 1; }

echo ""
log_info "Working in: $NOTES_DIR"
echo ""

# 1. Remove system files
log_info "Removing system files..."
find . -name ".DS_Store" -delete 2>/dev/null
find . -name "Thumbs.db" -delete 2>/dev/null
find . -name ".gitkeep" -delete 2>/dev/null
log_success "System files cleaned"

# 2. Find and report empty files
log_info "Checking for empty files..."
empty_files=$(find . -name "*.md" -size 0 2>/dev/null)
if [[ -n "$empty_files" ]]; then
    echo "$empty_files" | while read -r file; do
        log_warning "Empty file found: $file"
    done
    echo ""
    read -p "Remove empty files? (y/N): " -n 1 -r
    echo ""
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        find . -name "*.md" -size 0 -delete
        log_success "Empty files removed"
    fi
else
    log_success "No empty files found"
fi

# 3. Find potential duplicates (same basename)
log_info "Checking for potential duplicates..."
duplicates=$(find . -name "*.md" -exec basename {} \; | sort | uniq -d)
if [[ -n "$duplicates" ]]; then
    echo "$duplicates" | while read -r basename; do
        log_warning "Potential duplicate basename: $basename"
        find . -name "$basename" -exec ls -la {} \;
        echo ""
    done
    log_warning "Review potential duplicates manually"
else
    log_success "No obvious duplicates found"
fi

# 4. Check file naming conventions
log_info "Checking file naming conventions..."
non_conforming=$(find . -name "*.md" ! -name "README.md" ! -name "*-*" ! -name "uDEV-*" ! -name "uDOS-*" ! -name "uCORE-*" ! -name "uMEMORY-*" 2>/dev/null)
if [[ -n "$non_conforming" ]]; then
    echo "$non_conforming" | while read -r file; do
        log_warning "Non-conforming filename: $file"
    done
    log_warning "Consider renaming files to follow conventions"
else
    log_success "All files follow naming conventions"
fi

# 4.5. Auto-rename files to follow uDEV-YYYYMMDD-Description.md convention
log_info "Checking for files that can be auto-renamed to uDEV convention..."

# Function to extract date from filename or file modification time
get_date_for_file() {
    local file="$1"
    local basename_file=$(basename "$file")

    # Try to extract date from filename patterns
    if [[ "$basename_file" =~ ([0-9]{8}) ]]; then
        echo "${BASH_REMATCH[1]}"
    elif [[ "$basename_file" =~ (202[0-9]-[0-9]{2}-[0-9]{2}) ]]; then
        echo "${BASH_REMATCH[1]}" | tr -d '-'
    else
        # Use file modification date as fallback
        stat -f "%Sm" -t "%Y%m%d" "$file" 2>/dev/null || date "+%Y%m%d"
    fi
}

# Function to generate new filename
generate_udev_filename() {
    local file="$1"
    local basename_file=$(basename "$file")
    local date_part=$(get_date_for_file "$file")

    # Remove existing prefixes and clean up description
    local description=$(echo "$basename_file" | \
        sed 's/^uDEV-[0-9]*-//' | \
        sed 's/^uDOS-//' | \
        sed 's/^uCORE-//' | \
        sed 's/^uMEMORY-//' | \
        sed 's/\.md$//' | \
        sed 's/^[A-Z]*-//' | \
        sed 's/--/-/g' | \
        sed 's/^-//' | \
        sed 's/-$//')

    # If description is empty or too short, use generic description
    if [[ ${#description} -lt 5 ]]; then
        description="Development-Notes"
    fi

    echo "uDEV-${date_part}-${description}.md"
}

# Find files that could be renamed to uDEV convention
renameable_files=$(find . -name "*.md" ! -name "README.md" ! -name "uDEV-*" \
    -name "*-*" \( \
        -name "uDOS-*" -o \
        -name "uCORE-*" -o \
        -name "uMEMORY-*" -o \
        -name "*Complete*.md" -o \
        -name "*Implementation*.md" -o \
        -name "*Migration*.md" \
    \) 2>/dev/null)

if [[ -n "$renameable_files" ]]; then
    echo ""
    log_warning "Found files that can be renamed to uDEV convention:"

    # Create temporary file to store rename pairs
    rename_list="/tmp/udos_rename_list_$$"
    > "$rename_list"

    # Show proposed renames and store them
    while IFS= read -r file; do
        if [[ -n "$file" ]]; then
            new_name=$(generate_udev_filename "$file")
            basename_file=$(basename "$file")
            echo "   $basename_file → $new_name"
            echo "$file|$new_name" >> "$rename_list"
        fi
    done <<< "$renameable_files"

    echo ""
    read -p "Rename these files to follow uDEV-YYYYMMDD-Description.md convention? (y/N): " -n 1 -r
    echo ""
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        renamed_count=0
        while IFS='|' read -r old_file new_name; do
            if [[ -n "$old_file" && -n "$new_name" ]]; then
                basename_file=$(basename "$old_file")

                # Check if target filename already exists
                if [[ -f "$new_name" ]]; then
                    log_warning "Target exists, skipping: $basename_file → $new_name"
                    continue
                fi

                # Perform the rename
                if mv "$old_file" "$new_name" 2>/dev/null; then
                    log_success "Renamed: $basename_file → $new_name"
                    ((renamed_count++))
                else
                    log_error "Failed to rename: $basename_file"
                fi
            fi
        done < "$rename_list"

        # Cleanup temporary file
        rm -f "$rename_list"

        if [[ $renamed_count -gt 0 ]]; then
            log_success "Successfully renamed $renamed_count files"
            log_info "Consider regenerating the README index with: ./dev/scripts/generate-notes-index.sh"
        fi
    else
        log_info "Skipped file renaming"
        rm -f "$rename_list"
    fi
else
    log_success "No files found that need renaming to uDEV convention"
fi

# 5. Generate file statistics
log_info "Generating statistics..."
total_files=$(find . -name "*.md" | wc -l | tr -d ' ')
udev_files=$(find . -name "uDEV-*.md" | wc -l | tr -d ' ')
complete_files=$(find . -name "*Complete*.md" | wc -l | tr -d ' ')
implementation_files=$(find . -name "*Implementation*.md" | wc -l | tr -d ' ')
migration_files=$(find . -name "*Migration*.md" | wc -l | tr -d ' ')

echo ""
echo "📊 Statistics:"
echo "   Total markdown files: $total_files"
echo "   uDEV session logs: $udev_files"
echo "   Completion reports: $complete_files"
echo "   Implementation docs: $implementation_files"
echo "   Migration reports: $migration_files"

# 6. Archive old session logs (optional)
old_sessions=$(find . -name "uDEV-202508*" -mtime +30 2>/dev/null)
if [[ -n "$old_sessions" ]]; then
    echo ""
    log_warning "Found old session logs (30+ days):"
    echo "$old_sessions"
    echo ""
    read -p "Archive old session logs to archive/ subdirectory? (y/N): " -n 1 -r
    echo ""
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        mkdir -p archive
        echo "$old_sessions" | while read -r file; do
            mv "$file" archive/
        done
        log_success "Old session logs archived"
    fi
fi

# 7. Update README index if needed
log_info "Checking README.md index..."
if [[ -f "README.md" ]]; then
    # Count actual files vs README mentions
    actual_complete=$(find . -name "*Complete*.md" ! -name "README.md" | wc -l | tr -d ' ')
    readme_complete=$(grep -c "Complete\.md" README.md 2>/dev/null || echo 0)

    if [[ $actual_complete -ne $readme_complete ]]; then
        log_warning "README.md index may be outdated"
        log_warning "Actual completion files: $actual_complete, README mentions: $readme_complete"
        echo ""
        read -p "Would you like to regenerate the README index? (y/N): " -n 1 -r
        echo ""
        if [[ $REPLY =~ ^[Yy]$ ]]; then
            log_info "Backing up current README..."
            cp README.md README.md.backup
            log_info "Please manually update README.md or run the index generator"
        fi
    else
        log_success "README.md index appears current"
    fi
else
    log_warning "README.md not found - consider creating an index"
fi

# 8. Final summary
echo ""
echo "🏁 Cleanup Summary:"
echo "=================="
log_success "✅ System files cleaned"
log_success "✅ Empty files checked"
log_success "✅ Duplicates checked"
log_success "✅ Naming conventions validated"
log_success "✅ File renaming offered (uDEV convention)"
log_success "✅ Statistics generated"
log_success "✅ Archive maintenance completed"

echo ""
echo "💡 Maintenance Tips:"
echo "  • Run this script monthly for best results"
echo "  • Update README.md when adding significant new notes"
echo "  • Consider archiving session logs older than 60 days"
echo "  • Use consistent naming: uDEV-YYYYMMDD-Description.md"

echo ""
log_success "Cleanup completed successfully!"
