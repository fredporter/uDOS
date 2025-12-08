#!/usr/bin/env python3
"""
Restructure ROADMAP.MD for v1.2.3 Knowledge & Map Layer Expansion.

This script:
1. Keeps header and v1.2.2 archive reference
2. Replaces v1.2.3 with Knowledge & Map Layer Expansion content
3. Moves old v1.2.3 (Hot Reload) to become v1.2.4
4. Renumbers current v1.2.4 (MeshCore) to v1.2.5
5. Preserves all content after v1.2.4/v1.2.5
"""

import re
from pathlib import Path

# File paths
ROADMAP_PATH = Path("dev/roadmap/ROADMAP.MD")
V123_PLAN_PATH = Path("dev/sessions/2025-12-04-v1.2.3-knowledge-mapping-plan.md")
BACKUP_PATH = Path("dev/roadmap/.archive/ROADMAP-before-v1.2.3-knowledge-expansion.md")

def read_file(path):
    """Read file content."""
    with open(path, 'r', encoding='utf-8') as f:
        return f.read()

def write_file(path, content):
    """Write content to file."""
    with open(path, 'w', encoding='utf-8') as f:
        f.write(content)

def extract_section(content, start_marker, end_marker):
    """Extract content between two markers."""
    start_idx = content.find(start_marker)
    if start_idx == -1:
        return None, None

    end_idx = content.find(end_marker, start_idx + len(start_marker))
    if end_idx == -1:
        # If no end marker, take to end of file
        return content[start_idx:], len(content)

    return content[start_idx:end_idx], end_idx

def main():
    print("📋 Restructuring ROADMAP.MD for v1.2.3 Knowledge & Map Layer Expansion...")

    # Read files
    print("📖 Reading files...")
    roadmap = read_file(ROADMAP_PATH)
    v123_plan = read_file(V123_PLAN_PATH)

    # Create backup
    print(f"💾 Creating backup: {BACKUP_PATH}")
    write_file(BACKUP_PATH, roadmap)

    # Extract sections
    print("✂️  Extracting sections...")

    # Find header (everything before "## 📍 Next Release: v1.2.3")
    header_end_marker = "## 📍 Next Release: v1.2.3"
    header_idx = roadmap.find(header_end_marker)
    if header_idx == -1:
        print("❌ Error: Could not find v1.2.3 section marker")
        return False

    header = roadmap[:header_idx]

    # Find old v1.2.3 section (from "## 📍 Next Release" to "## 📍 Future Release: v1.2.4")
    old_v123_marker = header_end_marker
    old_v124_marker = "## 📍 Future Release: v1.2.4"

    old_v123_start = roadmap.find(old_v123_marker)
    old_v124_start = roadmap.find(old_v124_marker)

    if old_v123_start == -1 or old_v124_start == -1:
        print("❌ Error: Could not find section boundaries")
        return False

    old_v123_content = roadmap[old_v123_start:old_v124_start]
    old_v124_and_rest = roadmap[old_v124_start:]

    # Build new v1.2.3 section from plan
    # Remove the header from v123_plan (we just want the content, not the title)
    v123_lines = v123_plan.split('\n')
    # Skip the first few lines (title, metadata) and start from "## Mission:"
    v123_content_start = None
    for i, line in enumerate(v123_lines):
        if line.startswith('## Mission:'):
            v123_content_start = i
            break

    if v123_content_start is None:
        print("❌ Error: Could not find mission section in v1.2.3 plan")
        return False

    new_v123_body = '\n'.join(v123_lines[v123_content_start:])

    # Build new v1.2.3 section
    new_v123 = f"""## 📍 Next Release: v1.2.3 (December 2025)

**Status:** 📋 **PLANNED** - Knowledge & Map Layer Expansion
**Target:** December 2025
**Complexity:** High (knowledge generation + map layers + GeoJSON + planet/galaxy data)
**Dependencies:** v1.2.2 complete (DEV MODE), knowledge-expansion.upy workflow ready

{new_v123_body}

---

"""

    # Convert old v1.2.3 to v1.2.4
    new_v124 = old_v123_content.replace(
        "## 📍 Next Release: v1.2.3 (December 2025)",
        "## 📍 Future Release: v1.2.4 (January 2026)"
    ).replace(
        "**Status:** 📋 **PLANNED** - Developer Experience & Hot Reload",
        "**Status:** 📋 **PLANNED** - Developer Experience & Hot Reload"
    ).replace(
        "**Target:** December 2025",
        "**Target:** January 2026"
    ).replace(
        "**Dependencies:** v1.2.2 complete (DEV MODE debugging system)",
        "**Dependencies:** v1.2.3 complete (Knowledge & Map Layer Expansion)"
    )

    # Convert old v1.2.4 to v1.2.5
    new_v125_and_rest = old_v124_and_rest.replace(
        "## 📍 Future Release: v1.2.4 (January 2026)",
        "## 📍 Future Release: v1.2.5 (February 2026)"
    ).replace(
        "**Status:** 📋 **PLANNED** - MeshCore Off-Grid Networking Integration",
        "**Status:** 📋 **PLANNED** - MeshCore Off-Grid Networking Integration"
    ).replace(
        "**Target:** January 2026",
        "**Target:** February 2026"
    ).replace(
        "**Dependencies:** v1.2.3 complete (hot reload, GitHub integration)",
        "**Dependencies:** v1.2.4 complete (Developer Experience & Hot Reload)"
    )

    # Assemble new roadmap
    new_roadmap = header + new_v123 + new_v124 + new_v125_and_rest

    # Write new roadmap
    print("💾 Writing restructured roadmap...")
    write_file(ROADMAP_PATH, new_roadmap)

    print("✅ Roadmap restructured successfully!")
    print(f"📦 Backup saved: {BACKUP_PATH}")
    print(f"📄 New structure:")
    print(f"   - Header + v1.2.2 archive reference")
    print(f"   - v1.2.3: Knowledge & Map Layer Expansion (NEW)")
    print(f"   - v1.2.4: Developer Experience & Hot Reload (moved from v1.2.3)")
    print(f"   - v1.2.5: MeshCore Integration (renumbered from v1.2.4)")

    return True

if __name__ == "__main__":
    import sys
    sys.exit(0 if main() else 1)
