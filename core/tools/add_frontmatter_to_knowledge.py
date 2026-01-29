#!/usr/bin/env python3
"""
Add Frontmatter to Knowledge Files (Phase 6)

Adds YAML frontmatter to all .md files in /knowledge/ that don't have it yet.
Extracts metadata from file path and existing content.
"""

import os
import re
import json
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Optional


def parse_existing_frontmatter(content: str) -> tuple[Optional[dict], str]:
    """Extract existing frontmatter if present."""
    if content.startswith("---\n"):
        parts = content.split("---\n", 2)
        if len(parts) >= 3:
            # Has frontmatter
            fm_text = parts[1]
            body = parts[2]
            # Parse YAML-like frontmatter
            fm_dict = {}
            for line in fm_text.strip().split("\n"):
                if ":" in line:
                    key, value = line.split(":", 1)
                    fm_dict[key.strip()] = value.strip().strip('"').strip("'")
            return fm_dict, body
    return None, content


def extract_metadata_from_content(content: str, filepath: Path) -> dict:
    """Extract metadata hints from markdown content."""
    meta = {
        "category": filepath.parent.name,
        "title": "",
        "difficulty": "intermediate",
        "tags": [],
    }

    # Extract title from first # heading
    title_match = re.search(r"^#\s+(.+)$", content, re.MULTILINE)
    if title_match:
        meta["title"] = title_match.group(1).strip()
    else:
        # Use filename as title
        meta["title"] = filepath.stem.replace("_", " ").replace("-", " ").title()

    # Extract Category/Difficulty if present in content
    cat_match = re.search(r"\*\*Category:\*\*\s+(\w+)", content)
    if cat_match:
        meta["category"] = cat_match.group(1).lower()

    diff_match = re.search(r"\*\*Difficulty:\*\*\s+(\w+)", content)
    if diff_match:
        meta["difficulty"] = diff_match.group(1).lower()

    # Generate tags from category and title
    meta["tags"] = [
        meta["category"],
        filepath.parent.name,
    ]

    return meta


def generate_frontmatter(meta: dict) -> str:
    """Generate YAML frontmatter block."""
    lines = ["---"]
    lines.append(f'title: "{meta.get("title", "Untitled")}"')
    lines.append(f'id: {meta.get("id", "auto-generated")}')
    lines.append(f'type: {meta.get("type", "guide")}')
    lines.append(f'category: {meta.get("category", "general")}')

    if meta.get("region"):
        lines.append(f'region: {meta["region"]}')

    tags = meta.get("tags", [])
    if tags:
        lines.append(f'tags: [{", ".join(tags)}]')

    if meta.get("location_id"):
        lines.append(f'location_id: {meta["location_id"]}')

    if meta.get("coordinates"):
        lines.append(f'coordinates: {meta["coordinates"]}')

    lines.append(f'difficulty: {meta.get("difficulty", "intermediate")}')
    lines.append(f'last_updated: {datetime.now().strftime("%Y-%m-%d")}')
    lines.append("---")

    return "\n".join(lines) + "\n\n"


def process_file(filepath: Path, dry_run: bool = False) -> tuple[bool, str]:
    """Process a single markdown file."""
    try:
        with open(filepath, "r", encoding="utf-8") as f:
            content = f.read()

        # Check if already has frontmatter
        existing_fm, body = parse_existing_frontmatter(content)

        if existing_fm:
            return False, f"⏭️  Already has frontmatter"

        # Extract metadata
        meta = extract_metadata_from_content(content, filepath)

        # Generate ID from filepath
        rel_path = filepath.relative_to(Path("/Users/fredbook/Code/uDOS/knowledge"))
        meta["id"] = str(rel_path).replace("/", "-").replace(".md", "")

        # Determine type from category
        if meta["category"] in ["places", "cities", "planets"]:
            meta["type"] = "place"
        elif meta["category"] in ["skills", "tools", "making"]:
            meta["type"] = "skill"
        elif meta["category"] in ["medical", "survival", "fire", "water", "shelter"]:
            meta["type"] = "emergency"
        else:
            meta["type"] = "reference"

        # Generate new frontmatter
        frontmatter = generate_frontmatter(meta)
        new_content = frontmatter + body

        if not dry_run:
            with open(filepath, "w", encoding="utf-8") as f:
                f.write(new_content)

        return True, f"✅ Added frontmatter"

    except Exception as e:
        return False, f"❌ Error: {str(e)}"


def main():
    """Process all markdown files in knowledge directory."""
    knowledge_dir = Path("/Users/fredbook/Code/uDOS/knowledge")

    if not knowledge_dir.exists():
        print(f"❌ Knowledge directory not found: {knowledge_dir}")
        return

    # Find all .md files
    md_files = list(knowledge_dir.rglob("*.md"))

    print(f"📚 Found {len(md_files)} markdown files in {knowledge_dir}")
    print(f"🔄 Processing...\n")

    updated = 0
    skipped = 0
    errors = 0

    for filepath in sorted(md_files):
        rel_path = filepath.relative_to(knowledge_dir)
        success, message = process_file(filepath, dry_run=False)

        if success:
            updated += 1
            print(f"  {message}: {rel_path}")
        elif "already" in message.lower():
            skipped += 1
        else:
            errors += 1
            print(f"  {message}: {rel_path}")

    print(f"\n📊 Summary:")
    print(f"  ✅ Updated: {updated}")
    print(f"  ⏭️  Skipped: {skipped}")
    print(f"  ❌ Errors: {errors}")
    print(f"  📁 Total: {len(md_files)}")


if __name__ == "__main__":
    main()
