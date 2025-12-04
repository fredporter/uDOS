#!/usr/bin/env python3
"""
Batch Guide Improvement Script
Adds frontmatter to guides missing it (main quality issue).

Part of v1.2.11 - Knowledge Quality & Automation
"""

import json
import re
from pathlib import Path
from datetime import datetime
from typing import Dict, List


def add_frontmatter_to_guide(guide_path: Path, category: str) -> bool:
    """Add frontmatter to a guide that's missing it."""
    try:
        content = guide_path.read_text()

        # Check if already has frontmatter
        if content.startswith('---'):
            return False  # Already has frontmatter

        # Extract title from first # heading
        title_match = re.search(r'^#\s+(.+)$', content, re.MULTILINE)
        title = title_match.group(1) if title_match else guide_path.stem.replace('-', ' ').replace('_', ' ').title()

        # Determine complexity based on content length
        word_count = len(content.split())
        if word_count < 500:
            complexity = "basic"
            tier = 1
        elif word_count < 1500:
            complexity = "intermediate"
            tier = 2
        else:
            complexity = "advanced"
            tier = 3

        # Generate frontmatter
        frontmatter = f"""---
tier: {tier}
category: {category}
title: "{title}"
complexity: {complexity}
last_updated: {datetime.now().strftime('%Y-%m-%d')}
author: uDOS
version: 1.1
---

"""

        # Add frontmatter to content
        new_content = frontmatter + content

        # Write back
        guide_path.write_text(new_content)
        return True

    except Exception as e:
        print(f"  ⚠️  Error processing {guide_path.name}: {e}")
        return False


def improve_guides():
    """Add frontmatter to all guides missing it."""
    knowledge_path = Path("knowledge")
    categories = ['water', 'fire', 'shelter', 'food', 'navigation', 'medical']

    print("🔧 Starting guide improvement process...")
    print("")

    total_improved = 0
    total_skipped = 0

    for category in categories:
        category_path = knowledge_path / category
        if not category_path.exists():
            continue

        guides = list(category_path.glob("*.md"))
        improved_count = 0

        print(f"📂 {category.title()} ({len(guides)} guides)")

        for guide_path in guides:
            if add_frontmatter_to_guide(guide_path, category):
                improved_count += 1
                print(f"  ✓ {guide_path.name}")
            else:
                total_skipped += 1

        total_improved += improved_count
        print(f"  Improved: {improved_count}/{len(guides)}")
        print("")

    print("=== Summary ===")
    print(f"✅ Improved: {total_improved} guides")
    print(f"⏭️  Skipped: {total_skipped} guides (already had frontmatter)")
    print("")
    print("Next steps:")
    print("  1. Run quality scan again: python core/services/knowledge_metrics.py --scan")
    print("  2. View improvement: Check memory/system/knowledge-quality-dashboard.html")
    print("")


if __name__ == "__main__":
    import sys

    if '--dry-run' in sys.argv:
        print("Dry run mode - would improve guides but not making changes")
        print("Run without --dry-run to apply improvements")
    else:
        improve_guides()
