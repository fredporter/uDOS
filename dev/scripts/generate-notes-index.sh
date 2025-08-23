#!/bin/bash
# Development Notes Index Generator
# Automatically generates README.md index for dev/notes/

# Colors for output
GREEN='\033[0;32m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Script directory
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
NOTES_DIR="$(dirname "$SCRIPT_DIR")/notes"

echo -e "${BLUE}📋 Generating Development Notes Index${NC}"
echo "====================================="

cd "$NOTES_DIR" || exit 1

# Generate the README.md
cat > README.md << 'EOF'
# Development Notes Index

## 📋 **Overview**

This directory contains all development notes, completion reports, implementation summaries, and project documentation in a flat structure for easy access and maintenance.

---

## 🗂️ **Auto-Generated File Index**

EOF

echo "### 📊 **Implementation & Completion Reports**" >> README.md
echo "" >> README.md
find . -name "*Complete*.md" -o -name "*Implementation*.md" | sort | while read -r file; do
    basename_file=$(basename "$file")
    echo "- \`$basename_file\`" >> README.md
done

echo "" >> README.md
echo "### 🔄 **Migration & Legacy Reports**" >> README.md
echo "" >> README.md
find . -name "*Migration*.md" -o -name "*Legacy*.md" | sort | while read -r file; do
    basename_file=$(basename "$file")
    echo "- \`$basename_file\`" >> README.md
done

echo "" >> README.md
echo "### 📝 **Daily Development Logs (uDEV Series)**" >> README.md
echo "" >> README.md
find . -name "uDEV-*.md" | sort | while read -r file; do
    basename_file=$(basename "$file")
    echo "- \`$basename_file\`" >> README.md
done

echo "" >> README.md
echo "### 👨‍💻 **Developer Guides & Documentation**" >> README.md
echo "" >> README.md
find . -name "*Guide*.md" -o -name "*Developer*.md" -o -name "DEV-MODE*.md" | sort | while read -r file; do
    basename_file=$(basename "$file")
    echo "- \`$basename_file\`" >> README.md
done

echo "" >> README.md
echo "### 🛠️ **System & Framework Documentation**" >> README.md
echo "" >> README.md
find . -name "uCORE*.md" -o -name "uMEMORY*.md" -o -name "uDOS*.md" -o -name "*framework*.md" | sort | while read -r file; do
    basename_file=$(basename "$file")
    echo "- \`$basename_file\`" >> README.md
done

echo "" >> README.md
echo "### 🔧 **Testing & Configuration**" >> README.md
echo "" >> README.md
find . -name "*TEST*.md" -o -name "*Test*.md" -o -name "*.yml" -o -name "*config*.md" | sort | while read -r file; do
    basename_file=$(basename "$file")
    echo "- \`$basename_file\`" >> README.md
done

echo "" >> README.md
echo "### 📋 **Tasks & Utilities**" >> README.md
echo "" >> README.md
find . -name "uTASK*.md" -o -name "*Utility*.md" -o -name "*Task*.md" | sort | while read -r file; do
    basename_file=$(basename "$file")
    echo "- \`$basename_file\`" >> README.md
done

# Add footer
cat >> README.md << 'EOF'

---

## 🔍 **Quick Reference**

### **Find by Type**
```bash
# Implementation & Completion Reports
ls *Complete*.md *Implementation*.md

# Daily Development Logs
ls uDEV-*.md

# Migration Reports
ls *Migration*.md

# System Documentation
ls uCORE*.md uMEMORY*.md uDOS*.md

# Developer Guides
ls *Developer*.md *Guide*.md
```

### **Find by Date**
```bash
# 2025-08-21 Development Session
ls uDEV-20250821-*.md

# Recent v1.3.3 Work
ls *v1.3.3*.md

# v1.4.0 Updates
ls *v1.4.0*.md
```

### **Find by Component**
```bash
# uCORE related
ls *uCORE*.md *Core*.md

# uMEMORY related
ls *uMEMORY*.md *Memory*.md

# Font System
ls *Font*.md *font*.md

# Backup System
ls *Backup*.md *backup*.md
```

---

## 🧹 **Housekeeping**

Use the provided cleanup script to maintain organization:
```bash
./dev/scripts/notes-cleanup.sh
```

**Maintenance Tasks**:
- Remove duplicate files
- Archive old session logs
- Update this index when adding new notes
- Validate file naming conventions

---

**Last Updated**: $(date '+%B %d, %Y')
**Structure**: Flat directory for easy access
**Maintenance**: Auto-generated index, regular cleanup recommended
**Total Files**: $(find . -name "*.md" | wc -l | tr -d ' ') markdown files
EOF

echo -e "${GREEN}✅ README.md index generated successfully${NC}"
echo ""
echo "📊 Index Statistics:"
echo "   Implementation reports: $(find . -name "*Complete*.md" -o -name "*Implementation*.md" | wc -l | tr -d ' ')"
echo "   Development logs: $(find . -name "uDEV-*.md" | wc -l | tr -d ' ')"
echo "   Migration reports: $(find . -name "*Migration*.md" | wc -l | tr -d ' ')"
echo "   Total files indexed: $(find . -name "*.md" | wc -l | tr -d ' ')"
echo ""
echo "💡 Run './dev/scripts/notes-cleanup.sh' for full maintenance"
