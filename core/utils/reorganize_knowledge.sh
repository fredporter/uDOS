#!/bin/bash
# Knowledge Reorganization Script for uDOS v1.0.21
# Flattens structure and consolidates folders

set -e  # Exit on error

echo "🔄 Reorganizing uDOS Knowledge Library..."
echo ""

# Create new flat structure
echo "📁 Creating new folder structure..."

cd /Users/fredbook/Code/uDOS

# New simplified structure (8 main categories)
mkdir -p knowledge_new/{system,reference,survival,medical,food,water,making,tech}

# ====================
# 1. SYSTEM (from commands, concepts, faq, system, datasets, user)
# ====================
echo "Moving SYSTEM files..."
if [ -d "knowledge/commands" ]; then
  cp -r knowledge/commands/* knowledge_new/system/ 2>/dev/null || true
fi
if [ -d "knowledge/concepts" ]; then
  cp -r knowledge/concepts/* knowledge_new/system/ 2>/dev/null || true
fi
if [ -d "knowledge/faq" ]; then
  cp -r knowledge/faq/* knowledge_new/system/ 2>/dev/null || true
fi
if [ -d "knowledge/system" ]; then
  cp -r knowledge/system/* knowledge_new/system/ 2>/dev/null || true
fi
if [ -d "knowledge/datasets" ]; then
  cp -r knowledge/datasets/* knowledge_new/system/ 2>/dev/null || true
fi

# Merge data/ folder into knowledge/system (DEPRECATED - data/ removed in v1.0.24)
echo "Checking for legacy data/ folder..."
if [ -d "data/system" ]; then
  echo "⚠️  Found legacy data/system - migrating to knowledge/system..."
  cp -r data/system/* knowledge_new/system/ 2>/dev/null || true
fi
if [ -d "data/templates" ]; then
  echo "⚠️  Found legacy data/templates - migrating to knowledge/system/templates..."
  cp -r data/templates knowledge_new/system/ 2>/dev/null || true
fi
if [ -d "data/themes" ]; then
  echo "⚠️  Found legacy data/themes - migrating to knowledge/system/themes..."
  cp -r data/themes knowledge_new/system/ 2>/dev/null || true
fi

# ====================
# 2. REFERENCE (from maps, resources, tools - general reference)
# ====================
echo "Moving REFERENCE files..."
if [ -d "knowledge/maps" ]; then
  cp -r knowledge/maps/* knowledge_new/reference/ 2>/dev/null || true
fi
if [ -d "knowledge/resources" ]; then
  cp -r knowledge/resources/* knowledge_new/reference/ 2>/dev/null || true
fi
if [ -d "knowledge/tools" ]; then
  cp -r knowledge/tools/* knowledge_new/reference/ 2>/dev/null || true
fi

# ====================
# 3. SURVIVAL (flatten survival subfold ers)
# ====================
echo "Moving SURVIVAL files (flattened)..."
if [ -d "knowledge/survival" ]; then
  # Copy all markdown files from all subfolders into flat structure
  find knowledge/survival -name "*.md" -type f -exec cp {} knowledge_new/survival/ \; 2>/dev/null || true
fi

# ====================
# 4. MEDICAL (from survival/medical, survival/first-aid, medical/)
# ====================
echo "Moving MEDICAL files (flattened)..."
if [ -d "knowledge/survival/medical" ]; then
  find knowledge/survival/medical -name "*.md" -type f -exec cp {} knowledge_new/medical/ \; 2>/dev/null || true
fi
if [ -d "knowledge/survival/first-aid" ]; then
  find knowledge/survival/first-aid -name "*.md" -type f -exec cp {} knowledge_new/medical/ \; 2>/dev/null || true
fi
if [ -d "knowledge/medical" ]; then
  find knowledge/medical -name "*.md" -type f -exec cp {} knowledge_new/medical/ \; 2>/dev/null || true
fi

# ====================
# 5. FOOD (from survival/food, food/)
# ====================
echo "Moving FOOD files (flattened)..."
if [ -d "knowledge/survival/food" ]; then
  find knowledge/survival/food -name "*.md" -type f -exec cp {} knowledge_new/food/ \; 2>/dev/null || true
fi
if [ -d "knowledge/food" ]; then
  find knowledge/food -name "*.md" -type f -exec cp {} knowledge_new/food/ \; 2>/dev/null || true
fi

# ====================
# 6. WATER (from survival/water, water/)
# ====================
echo "Moving WATER files (flattened)..."
if [ -d "knowledge/survival/water" ]; then
  find knowledge/survival/water -name "*.md" -type f -exec cp {} knowledge_new/water/ \; 2>/dev/null || true
fi
if [ -d "knowledge/water" ]; then
  find knowledge/water -name "*.md" -type f -exec cp {} knowledge_new/water/ \; 2>/dev/null || true
fi

# ====================
# 7. MAKING (from building, energy, environment - practical making/doing)
# ====================
echo "Moving MAKING files (flattened)..."
if [ -d "knowledge/building" ]; then
  find knowledge/building -name "*.md" -type f -exec cp {} knowledge_new/making/ \; 2>/dev/null || true
fi
if [ -d "knowledge/energy" ]; then
  find knowledge/energy -name "*.md" -type f -exec cp {} knowledge_new/making/ \; 2>/dev/null || true
fi
if [ -d "knowledge/survival/energy" ]; then
  find knowledge/survival/energy -name "*.md" -type f -exec cp {} knowledge_new/making/ \; 2>/dev/null || true
fi
if [ -d "knowledge/environment" ]; then
  find knowledge/environment -name "*.md" -type f -exec cp {} knowledge_new/making/ \; 2>/dev/null || true
fi

# ====================
# 8. TECH (from skills/programming, productivity, communication)
# ====================
echo "Moving TECH files (flattened)..."
if [ -d "knowledge/skills/programming" ]; then
  find knowledge/skills/programming -name "*.md" -type f -exec cp {} knowledge_new/tech/ \; 2>/dev/null || true
fi
if [ -d "knowledge/productivity" ]; then
  find knowledge/productivity -name "*.md" -type f -exec cp {} knowledge_new/tech/ \; 2>/dev/null || true
fi
if [ -d "knowledge/communication" ]; then
  find knowledge/communication -name "*.md" -type f -exec cp {} knowledge_new/tech/ \; 2>/dev/null || true
fi

# ====================
# Keep personal and well-being separate (user-specific)
# ====================
echo "Preserving user folders..."
if [ -d "knowledge/personal" ]; then
  cp -r knowledge/personal knowledge_new/ 2>/dev/null || true
fi
if [ -d "knowledge/well-being" ]; then
  cp -r knowledge/well-being knowledge_new/ 2>/dev/null || true
fi
if [ -d "knowledge/community" ]; then
  cp -r knowledge/community knowledge_new/ 2>/dev/null || true
fi
if [ -d "knowledge/skills" ]; then
  # Keep non-programming skills
  mkdir -p knowledge_new/skills
  if [ -d "knowledge/skills/art" ]; then
    cp -r knowledge/skills/art knowledge_new/skills/ 2>/dev/null || true
  fi
  if [ -d "knowledge/skills/writing" ]; then
    cp -r knowledge/skills/writing knowledge_new/skills/ 2>/dev/null || true
  fi
  if [ -d "knowledge/skills/music" ]; then
    cp -r knowledge/skills/music knowledge_new/skills/ 2>/dev/null || true
  fi
fi

# Copy root level files
echo "Copying root documentation..."
cp knowledge/README.md knowledge_new/ 2>/dev/null || true
cp knowledge/KNOWLEDGE-SYSTEM.md knowledge_new/ 2>/dev/null || true

echo ""
echo "✅ Reorganization complete!"
echo ""
echo "New structure:"
tree -L 1 knowledge_new 2>/dev/null || ls -la knowledge_new/
echo ""
echo "📊 File counts:"
echo "  system:    $(find knowledge_new/system -name "*.md" 2>/dev/null | wc -l | tr -d ' ') files"
echo "  reference: $(find knowledge_new/reference -name "*.md" 2>/dev/null | wc -l | tr -d ' ') files"
echo "  survival:  $(find knowledge_new/survival -name "*.md" 2>/dev/null | wc -l | tr -d ' ') files"
echo "  medical:   $(find knowledge_new/medical -name "*.md" 2>/dev/null | wc -l | tr -d ' ') files"
echo "  food:      $(find knowledge_new/food -name "*.md" 2>/dev/null | wc -l | tr -d ' ') files"
echo "  water:     $(find knowledge_new/water -name "*.md" 2>/dev/null | wc -l | tr -d ' ') files"
echo "  making:    $(find knowledge_new/making -name "*.md" 2>/dev/null | wc -l | tr -d ' ') files"
echo "  tech:      $(find knowledge_new/tech -name "*.md" 2>/dev/null | wc -l | tr -d ' ') files"
echo ""
echo "⚠️  REVIEW THE NEW STRUCTURE BEFORE PROCEEDING!"
echo "When ready, run:"
echo "  mv knowledge knowledge_old_backup"
echo "  mv knowledge_new knowledge"
