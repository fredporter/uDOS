#!/usr/bin/env python3
"""
Generate Knowledge Catalog (_index.json) - Phase 7

Creates a comprehensive catalog of all knowledge files with:
- Full metadata extraction
- Search index by tags/categories
- Location linking
- Quick reference lookup
"""

import os
import re
import json
from pathlib import Path
from typing import Dict, List, Optional


def parse_frontmatter(content: str) -> Optional[dict]:
    """Extract YAML frontmatter from markdown."""
    if content.startswith('---\n'):
        parts = content.split('---\n', 2)
        if len(parts) >= 3:
            fm_text = parts[1]
            fm_dict = {}
            for line in fm_text.strip().split('\n'):
                if ':' in line:
                    key, value = line.split(':', 1)
                    key = key.strip()
                    value = value.strip().strip('"').strip("'")
                    
                    # Parse arrays
                    if value.startswith('[') and value.endswith(']'):
                        items = value[1:-1].split(',')
                        fm_dict[key] = [item.strip() for item in items if item.strip()]
                    else:
                        fm_dict[key] = value
            
            return fm_dict
    return None


def extract_summary(content: str, max_length: int = 200) -> str:
    """Extract first paragraph as summary."""
    # Remove frontmatter
    if content.startswith('---\n'):
        parts = content.split('---\n', 2)
        if len(parts) >= 3:
            content = parts[2]
    
    # Remove markdown headings
    lines = content.split('\n')
    paragraphs = []
    for line in lines:
        line = line.strip()
        if line and not line.startswith('#') and not line.startswith('**'):
            paragraphs.append(line)
            if len(' '.join(paragraphs)) > max_length:
                break
    
    summary = ' '.join(paragraphs)
    if len(summary) > max_length:
        summary = summary[:max_length].rsplit(' ', 1)[0] + '...'
    
    return summary


def process_file(filepath: Path, knowledge_root: Path) -> dict:
    """Process a single markdown file and extract metadata."""
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Extract frontmatter
        frontmatter = parse_frontmatter(content)
        if not frontmatter:
            frontmatter = {}
        
        # Calculate relative path
        rel_path = str(filepath.relative_to(knowledge_root))
        
        # Build entry
        entry = {
            'id': frontmatter.get('id', rel_path.replace('/', '-').replace('.md', '')),
            'title': frontmatter.get('title', filepath.stem.replace('_', ' ').title()),
            'path': rel_path,
            'type': frontmatter.get('type', 'reference'),
            'category': frontmatter.get('category', filepath.parent.name),
            'tags': frontmatter.get('tags', []),
            'difficulty': frontmatter.get('difficulty', 'intermediate'),
            'last_updated': frontmatter.get('last_updated', ''),
            'summary': extract_summary(content, 150),
        }
        
        # Optional fields
        if frontmatter.get('location_id'):
            entry['location_id'] = frontmatter['location_id']
        
        if frontmatter.get('coordinates'):
            entry['coordinates'] = frontmatter['coordinates']
        
        if frontmatter.get('region'):
            entry['region'] = frontmatter['region']
        
        return entry
        
    except Exception as e:
        print(f"❌ Error processing {filepath}: {e}")
        return None


def build_indexes(entries: List[dict]) -> dict:
    """Build search indexes."""
    indexes = {
        'by_category': {},
        'by_type': {},
        'by_tag': {},
        'by_difficulty': {},
        'by_region': {}
    }
    
    for entry in entries:
        entry_id = entry['id']
        
        # Index by category
        cat = entry['category']
        if cat not in indexes['by_category']:
            indexes['by_category'][cat] = []
        indexes['by_category'][cat].append(entry_id)
        
        # Index by type
        typ = entry['type']
        if typ not in indexes['by_type']:
            indexes['by_type'][typ] = []
        indexes['by_type'][typ].append(entry_id)
        
        # Index by tags
        for tag in entry.get('tags', []):
            if tag not in indexes['by_tag']:
                indexes['by_tag'][tag] = []
            indexes['by_tag'][tag].append(entry_id)
        
        # Index by difficulty
        diff = entry['difficulty']
        if diff not in indexes['by_difficulty']:
            indexes['by_difficulty'][diff] = []
        indexes['by_difficulty'][diff].append(entry_id)
        
        # Index by region (if present)
        if 'region' in entry:
            region = entry['region']
            if region not in indexes['by_region']:
                indexes['by_region'][region] = []
            indexes['by_region'][region].append(entry_id)
    
    return indexes


def main():
    """Generate knowledge catalog."""
    knowledge_dir = Path('/Users/fredbook/Code/uDOS/knowledge')
    
    if not knowledge_dir.exists():
        print(f"❌ Knowledge directory not found: {knowledge_dir}")
        return
    
    print(f"📚 Scanning {knowledge_dir}...")
    
    # Find all markdown files
    md_files = list(knowledge_dir.rglob('*.md'))
    
    print(f"📄 Found {len(md_files)} markdown files")
    print(f"🔄 Processing...\n")
    
    # Process all files
    entries = []
    for filepath in sorted(md_files):
        entry = process_file(filepath, knowledge_dir)
        if entry:
            entries.append(entry)
    
    print(f"✅ Processed {len(entries)} entries")
    
    # Build indexes
    print(f"🔍 Building search indexes...")
    indexes = build_indexes(entries)
    
    # Build catalog
    catalog = {
        'version': '1.0.0',
        'generated': '2026-01-29',
        'total_entries': len(entries),
        'categories': list(indexes['by_category'].keys()),
        'types': list(indexes['by_type'].keys()),
        'tags': list(indexes['by_tag'].keys()),
        'entries': {entry['id']: entry for entry in entries},
        'indexes': indexes,
        'stats': {
            'by_category': {k: len(v) for k, v in indexes['by_category'].items()},
            'by_type': {k: len(v) for k, v in indexes['by_type'].items()},
            'by_difficulty': {k: len(v) for k, v in indexes['by_difficulty'].items()},
            'total_tags': len(indexes['by_tag'])
        }
    }
    
    # Write catalog
    output_path = knowledge_dir / '_index.json'
    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(catalog, f, indent=2, ensure_ascii=False)
    
    print(f"\n✅ Catalog written to: {output_path}")
    print(f"\n📊 Statistics:")
    print(f"   Total entries: {catalog['total_entries']}")
    print(f"   Categories: {len(catalog['categories'])}")
    print(f"   Types: {len(catalog['types'])}")
    print(f"   Tags: {len(catalog['tags'])}")
    print(f"\n📂 Entries by category:")
    for cat, count in sorted(catalog['stats']['by_category'].items()):
        print(f"   {cat}: {count}")
    
    print(f"\n📝 Entries by type:")
    for typ, count in sorted(catalog['stats']['by_type'].items()):
        print(f"   {typ}: {count}")


if __name__ == '__main__':
    main()
