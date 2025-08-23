#!/bin/bash
# Enhanced Roadmaps Cleanup and Maintenance Script
# Part of uDOS Dev Mode Workflow Integration

set -e

ROADMAPS_DIR="/Users/agentdigital/uDOS/dev/roadmaps"
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
TODAY=$(date "+%Y%m%d")

# Color codes for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

echo -e "${BLUE}🗺️ Roadmaps Cleanup and Maintenance${NC}"
echo "========================================"

cd "$ROADMAPS_DIR"

# Function to standardize roadmap filenames
standardize_roadmap_names() {
    echo -e "${YELLOW}📝 Standardizing roadmap filenames...${NC}"

    local renamed_count=0

    for file in *.md; do
        # Skip if file doesn't exist or is already in correct format
        [[ ! -f "$file" ]] && continue
        [[ "$file" =~ ^uROAD- ]] && continue
        [[ "$file" == "README.md" ]] && continue

        # Extract date from filename or use file modification date
        local date_from_name=""
        if [[ "$file" =~ ([0-9]{8}) ]]; then
            date_from_name="${BASH_REMATCH[1]}"
        elif [[ "$file" =~ ([0-9]{4}-[0-9]{2}-[0-9]{2}) ]]; then
            date_from_name=$(echo "${BASH_REMATCH[1]}" | tr -d '-')
        else
            # Use file modification date
            date_from_name=$(date -r "$file" "+%Y%m%d" 2>/dev/null || echo "$TODAY")
        fi

        # Generate description from filename
        local description=$(echo "$file" | sed 's/\.[^.]*$//' | \
            sed 's/[0-9-]*//g' | \
            sed 's/^[^A-Za-z]*//' | \
            sed 's/[^A-Za-z0-9]/-/g' | \
            sed 's/--*/-/g' | \
            sed 's/^-\|-$//g' | \
            tr '[:upper:]' '[:lower:]')

        # Clean up description for roadmaps
        description=$(echo "$description" | \
            sed 's/utask/uTASK/g' | \
            sed 's/roadmap/Roadmap/g' | \
            sed 's/framework/Framework/g' | \
            sed 's/enhancement/Enhancement/g' | \
            sed 's/-/ /g' | \
            sed 's/\b\w/\u&/g' | \
            sed 's/ /-/g')

        local new_name="uROAD-${date_from_name}-${description}.md"

        # Avoid conflicts
        local counter=1
        local base_new_name="$new_name"
        while [[ -f "$new_name" && "$new_name" != "$file" ]]; do
            new_name="uROAD-${date_from_name}-${description}-${counter}.md"
            ((counter++))
        done

        if [[ "$file" != "$new_name" ]]; then
            echo "  📄 $file → $new_name"
            mv "$file" "$new_name"
            ((renamed_count++))
        fi
    done

    echo -e "${GREEN}✅ Renamed $renamed_count roadmap files${NC}"
}

# Function to remove empty files
remove_empty_files() {
    echo -e "${YELLOW}🗑️ Removing empty roadmap files...${NC}"

    local removed_count=0
    for file in *.md; do
        [[ ! -f "$file" ]] && continue
        [[ "$file" == "README.md" ]] && continue
        if [[ ! -s "$file" ]]; then
            echo "  🗑️ Removing empty file: $file"
            rm "$file"
            ((removed_count++))
        fi
    done

    echo -e "${GREEN}✅ Removed $removed_count empty files${NC}"
}

# Function to categorize roadmaps by timeline
categorize_roadmaps() {
    echo -e "${YELLOW}📊 Categorizing roadmaps by timeline...${NC}"

    # Arrays for different categories
    local daily_roadmaps=()
    local sprint_roadmaps=()
    local quarterly_roadmaps=()
    local longterm_roadmaps=()
    local version_roadmaps=()
    local other_roadmaps=()

    for file in uROAD-*.md; do
        [[ ! -f "$file" ]] && continue

        # Categorize based on content and naming patterns
        if [[ "$file" =~ [Dd]aily|$(date "+%Y%m%d")|$(date -v-1d "+%Y%m%d")|$(date -v+1d "+%Y%m%d") ]]; then
            daily_roadmaps+=("$file")
        elif [[ "$file" =~ [Ss]print|[Ww]eek|[Tt]ask ]]; then
            sprint_roadmaps+=("$file")
        elif [[ "$file" =~ [Qq]uarter|[Mm]onth|[Qq][0-9] ]]; then
            quarterly_roadmaps+=("$file")
        elif [[ "$file" =~ [Ll]ong|[Yy]ear|[Ee]nterprise|[Aa]rchitecture ]]; then
            longterm_roadmaps+=("$file")
        elif [[ "$file" =~ [Vv][0-9]|v[0-9] ]]; then
            version_roadmaps+=("$file")
        else
            other_roadmaps+=("$file")
        fi
    done

    # Export categories for index generation
    export daily_roadmaps sprint_roadmaps quarterly_roadmaps longterm_roadmaps version_roadmaps other_roadmaps
}

# Function to generate roadmaps index
generate_roadmaps_index() {
    echo -e "${YELLOW}📋 Generating roadmaps index...${NC}"

    categorize_roadmaps

    cat > README.md << 'EOF'
# uDOS Development Roadmaps

This directory contains all development roadmaps organized in a flat structure for easy access and maintenance.

## 🔗 Integration with Dev Mode

These roadmaps are automatically integrated with the uDOS workflow system:

```bash
# Access roadmaps through workflow system
./dev/workflow.sh roadmaps list           # List all roadmaps
./dev/workflow.sh roadmaps timeline       # Show timeline view
./dev/workflow.sh roadmaps active         # Show active roadmaps
./dev/workflow.sh roadmaps create         # Create new roadmap
```

## 📅 Roadmap Categories

EOF

    # Add categorized listings with arrays
    if [[ ${#daily_roadmaps[@]} -gt 0 ]]; then
        echo "### 📅 Daily Roadmaps" >> README.md
        for file in "${daily_roadmaps[@]}"; do
            echo "- \`$file\`" >> README.md
        done
        echo "" >> README.md
    fi

    if [[ ${#sprint_roadmaps[@]} -gt 0 ]]; then
        echo "### 🏃 Sprint Roadmaps" >> README.md
        for file in "${sprint_roadmaps[@]}"; do
            echo "- \`$file\`" >> README.md
        done
        echo "" >> README.md
    fi

    if [[ ${#quarterly_roadmaps[@]} -gt 0 ]]; then
        echo "### 📊 Quarterly Roadmaps" >> README.md
        for file in "${quarterly_roadmaps[@]}"; do
            echo "- \`$file\`" >> README.md
        done
        echo "" >> README.md
    fi

    if [[ ${#longterm_roadmaps[@]} -gt 0 ]]; then
        echo "### 🔮 Long-term Roadmaps" >> README.md
        for file in "${longterm_roadmaps[@]}"; do
            echo "- \`$file\`" >> README.md
        done
        echo "" >> README.md
    fi

    if [[ ${#version_roadmaps[@]} -gt 0 ]]; then
        echo "### 🔢 Version Roadmaps" >> README.md
        for file in "${version_roadmaps[@]}"; do
            echo "- \`$file\`" >> README.md
        done
        echo "" >> README.md
    fi

    if [[ ${#other_roadmaps[@]} -gt 0 ]]; then
        echo "### 📋 Other Roadmaps" >> README.md
        for file in "${other_roadmaps[@]}"; do
            echo "- \`$file\`" >> README.md
        done
        echo "" >> README.md
    fi

    # Add statistics and maintenance info
    cat >> README.md << EOF
## 📊 Roadmap Statistics

- **Total roadmaps**: $(ls -1 uROAD-*.md 2>/dev/null | wc -l | tr -d ' ')
- **Last updated**: $(date)
- **Naming convention**: \`uROAD-YYYYMMDD-Description.md\`

## 🔧 Maintenance

Run the cleanup script to maintain this directory:

\`\`\`bash
./dev/scripts/roadmaps-cleanup.sh
\`\`\`

## 🔗 Workflow Integration

This directory is integrated with:
- uDOS Assist Mode (OK/END commands)
- Dev Mode Workflow Scheduler
- Automated roadmap tracking
- Timeline-based organization

For more information, see the workflow documentation in \`dev/notes/\`.
EOF

    echo -e "${GREEN}✅ Roadmaps index generated${NC}"
}

# Main execution
main() {
    # Ensure we're in the roadmaps directory
    if [[ ! -d "$ROADMAPS_DIR" ]]; then
        echo -e "${RED}❌ Roadmaps directory not found: $ROADMAPS_DIR${NC}"
        exit 1
    fi

    cd "$ROADMAPS_DIR"

    # Run maintenance functions
    remove_empty_files
    standardize_roadmap_names
    generate_roadmaps_index

    echo ""
    echo -e "${GREEN}🎯 Roadmaps maintenance complete!${NC}"
    echo -e "${BLUE}📊 Statistics:${NC}"
    echo "   Total roadmaps: $(ls -1 uROAD-*.md 2>/dev/null | wc -l | tr -d ' ')"
    echo "   Directory size: $(du -sh . | cut -f1)"
    echo ""
    echo -e "${YELLOW}💡 Run './dev/workflow.sh roadmaps list' to see integrated roadmaps${NC}"
}

# Run if called directly
if [[ "${BASH_SOURCE[0]}" == "${0}" ]]; then
    main "$@"
fi
