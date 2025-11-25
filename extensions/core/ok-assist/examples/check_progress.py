#!/usr/bin/env python3
"""
Monitor batch generation progress by counting generated files
"""

from pathlib import Path

# Project root
project_root = Path("/Users/fredbook/Code/uDOS")
diagrams_dir = project_root / "knowledge" / "diagrams"

# Count files in each category
ascii_count = len(list((diagrams_dir / "ascii").glob("*.txt"))) if (diagrams_dir / "ascii").exists() else 0
teletext_count = len(list((diagrams_dir / "teletext").glob("*.html"))) if (diagrams_dir / "teletext").exists() else 0

# Count SVG by category
categories = ['shelter', 'food', 'fire', 'navigation', 'medical', 'water', 'tools', 'communication']
svg_counts = {}
total_svg = 0

for cat in categories:
    cat_dir = diagrams_dir / cat
    if cat_dir.exists():
        count = len(list(cat_dir.glob("*.svg")))
        svg_counts[cat] = count
        total_svg += count

print("=" * 60)
print("DIAGRAM LIBRARY STATUS")
print("=" * 60)
print()
print(f"ASCII diagrams: {ascii_count}")
print(f"Teletext diagrams: {teletext_count}")
print(f"SVG diagrams: {total_svg}")
print()
print("SVG by category:")
for cat, count in sorted(svg_counts.items()):
    if count > 0:
        print(f"  {cat}: {count}")
print()
print(f"Total diagrams: {ascii_count + teletext_count + total_svg}")
print("=" * 60)
