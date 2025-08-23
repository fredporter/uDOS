#!/bin/bash
# Enhanced Briefings Cleanup and Maintenance Script
# Part of uDOS Dev Mode Workflow Integration

set -e

BRIEFINGS_DIR="/Users/agentdigital/uDOS/dev/briefings"
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
TODAY=$(date "+%Y%m%d")

# Color codes for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

echo -e "${BLUE}🧠 Briefings Cleanup and Maintenance${NC}"
echo "========================================"

cd "$BRIEFINGS_DIR"

# Function to standardize briefing filenames
standardize_briefing_names() {
    echo -e "${YELLOW}📝 Standardizing briefing filenames...${NC}"

    local renamed_count=0

    for file in *.md; do
        # Skip if file doesn't exist or is already in correct format
        [[ ! -f "$file" ]] && continue
        [[ "$file" =~ ^uBRIEF- ]] && continue
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

        # Clean up description
        description=$(echo "$description" | sed 's/claude-briefing/Claude-Briefing/g' | \
            sed 's/dev-mode/Dev-Mode/g' | \
            sed 's/-/ /g' | \
            sed 's/\b\w/\u&/g' | \
            sed 's/ /-/g')

        local new_name="uBRIEF-${date_from_name}-${description}.md"

        # Avoid conflicts
        local counter=1
        local base_new_name="$new_name"
        while [[ -f "$new_name" && "$new_name" != "$file" ]]; do
            new_name="uBRIEF-${date_from_name}-${description}-${counter}.md"
            ((counter++))
        done

        if [[ "$file" != "$new_name" ]]; then
            echo "  📄 $file → $new_name"
            mv "$file" "$new_name"
            ((renamed_count++))
        fi
    done

    echo -e "${GREEN}✅ Renamed $renamed_count briefing files${NC}"
}

# Function to remove empty files
remove_empty_files() {
    echo -e "${YELLOW}🗑️ Removing empty briefing files...${NC}"

    local removed_count=0
    for file in *.md; do
        [[ ! -f "$file" ]] && continue
        if [[ ! -s "$file" ]]; then
            echo "  🗑️ Removing empty file: $file"
            rm "$file"
            ((removed_count++))
        fi
    done

    echo -e "${GREEN}✅ Removed $removed_count empty files${NC}"
}

# Function to generate briefings index
generate_briefings_index() {
    echo -e "${YELLOW}📋 Generating briefings index...${NC}"

    cat > README.md << 'EOF'
# uDOS Development Briefings

This directory contains AI assistant briefings and session documentation for uDOS development workflows.

## 🧠 Integration with Dev Mode

These briefings are automatically integrated with the uDOS workflow system:

```bash
# Access briefings through workflow system
./dev/workflow.sh briefings list          # List all briefings
./dev/workflow.sh briefings current       # Show current session briefing
./dev/workflow.sh briefings update        # Update briefing with current context
```

## 📁 Briefing Categories

EOF

    # Categorize briefings
    local claude_briefings=()
    local session_briefings=()
    local dev_briefings=()
    local other_briefings=()

    for file in uBRIEF-*.md; do
        [[ ! -f "$file" ]] && continue

        if [[ "$file" =~ [Cc]laude ]]; then
            claude_briefings+=("$file")
        elif [[ "$file" =~ [Ss]ession ]]; then
            session_briefings+=("$file")
        elif [[ "$file" =~ [Dd]ev ]]; then
            dev_briefings+=("$file")
        else
            other_briefings+=("$file")
        fi
    done

    # Add categorized listings
    if [[ ${#claude_briefings[@]} -gt 0 ]]; then
        echo "### 🤖 Claude AI Briefings" >> README.md
        for file in "${claude_briefings[@]}"; do
            echo "- \`$file\`" >> README.md
        done
        echo "" >> README.md
    fi

    if [[ ${#dev_briefings[@]} -gt 0 ]]; then
        echo "### 🛠️ Development Mode Briefings" >> README.md
        for file in "${dev_briefings[@]}"; do
            echo "- \`$file\`" >> README.md
        done
        echo "" >> README.md
    fi

    if [[ ${#session_briefings[@]} -gt 0 ]]; then
        echo "### 📝 Session Briefings" >> README.md
        for file in "${session_briefings[@]}"; do
            echo "- \`$file\`" >> README.md
        done
        echo "" >> README.md
    fi

    if [[ ${#other_briefings[@]} -gt 0 ]]; then
        echo "### 📋 Other Briefings" >> README.md
        for file in "${other_briefings[@]}"; do
            echo "- \`$file\`" >> README.md
        done
        echo "" >> README.md
    fi

    # Add statistics and maintenance info
    cat >> README.md << EOF
## 📊 Briefing Statistics

- **Total briefings**: $(ls -1 uBRIEF-*.md 2>/dev/null | wc -l | tr -d ' ')
- **Last updated**: $(date)
- **Naming convention**: \`uBRIEF-YYYYMMDD-Description.md\`

## 🔧 Maintenance

Run the cleanup script to maintain this directory:

\`\`\`bash
./dev/scripts/briefings-cleanup.sh
\`\`\`

## 🔗 Workflow Integration

This directory is integrated with:
- uDOS Assist Mode (OK/END commands)
- Dev Mode Workflow Scheduler
- Automated session management
- Context-aware AI briefing updates

For more information, see the workflow documentation in \`dev/notes/\`.
EOF

    echo -e "${GREEN}✅ Briefings index generated${NC}"
}

# Main execution
main() {
    # Ensure we're in the briefings directory
    if [[ ! -d "$BRIEFINGS_DIR" ]]; then
        echo -e "${RED}❌ Briefings directory not found: $BRIEFINGS_DIR${NC}"
        exit 1
    fi

    cd "$BRIEFINGS_DIR"

    # Run maintenance functions
    remove_empty_files
    standardize_briefing_names
    generate_briefings_index

    echo ""
    echo -e "${GREEN}🎯 Briefings maintenance complete!${NC}"
    echo -e "${BLUE}📊 Statistics:${NC}"
    echo "   Total briefings: $(ls -1 uBRIEF-*.md 2>/dev/null | wc -l | tr -d ' ')"
    echo "   Directory size: $(du -sh . | cut -f1)"
    echo ""
    echo -e "${YELLOW}💡 Run './dev/workflow.sh briefings list' to see integrated briefings${NC}"
}

# Run if called directly
if [[ "${BASH_SOURCE[0]}" == "${0}" ]]; then
    main "$@"
fi
