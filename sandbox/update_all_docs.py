#!/usr/bin/env python3
"""
Comprehensive path update script for all markdown files
Replaces knowledge/system → core/data, memory/user → sandbox/user, memory/logs → sandbox/logs
Excludes memory/user/workflow references
"""
import os
import re

# Path replacements
REPLACEMENTS = [
    ("knowledge/system", "core/data"),
    ("memory/logs", "sandbox/logs"),
]

# Special case: memory/user → sandbox/user (but NOT memory/user/workflow)
def replace_memory_user(content):
    """Replace memory/user with sandbox/user, except memory/user/workflow"""
    # Replace memory/user but not memory/user/workflow
    pattern = r'memory/user(?!/workflow)'
    return re.sub(pattern, 'sandbox/user', content)

# Files to update
FILES = [
    # Core docs
    "core/docs/README-FONT-SYSTEM.md",
    "core/docs/BLANK-ENHANCED.md",
    "core/README.md",

    # Extensions docs
    "extensions/core/teletext/README.md",
    "extensions/SERVER-MANAGEMENT.md",
    "extensions/QUICK-REFERENCE.md",

    # Root docs
    "QUICK-START.md",
    "CHANGELOG.md",

    # Wiki docs
    "wiki/Development-History.md",
    "wiki/Philosophy.md",
    "wiki/Configuration.md",
    "wiki/Developers-Guide.md",
    "wiki/Home.md",
    "wiki/Command-Reference.md",
    "wiki/FAQ.md",
    "wiki/Content-Generation.md",
    "wiki/uCODE-Language.md",
    "wiki/Troubleshooting-Complete.md",
    "wiki/Workflows.md",
    "wiki/Architecture.md",

    # Knowledge system
    "knowledge/survival/bush-navigation.md",

    # Core data diagrams
    "core/data/diagrams/systems/memory-tiers-medium.md",
]

def update_file(filepath):
    """Update a single file with path replacements"""
    if not os.path.exists(filepath):
        print(f"⚠️  File not found: {filepath}")
        return False

    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            content = f.read()

        original_content = content
        changes = []

        # Apply standard replacements
        for old, new in REPLACEMENTS:
            count = content.count(old)
            if count > 0:
                content = content.replace(old, new)
                changes.append(f"{old} → {new} ({count}x)")

        # Apply memory/user replacement (excluding workflow)
        memory_user_count = len(re.findall(r'memory/user(?!/workflow)', content))
        if memory_user_count > 0:
            content = replace_memory_user(content)
            changes.append(f"memory/user → sandbox/user ({memory_user_count}x)")

        if content != original_content:
            with open(filepath, 'w', encoding='utf-8') as f:
                f.write(content)
            print(f"✅ Updated: {filepath}")
            for change in changes:
                print(f"   - {change}")
            return True
        else:
            print(f"➖ No changes: {filepath}")
            return False

    except Exception as e:
        print(f"❌ Error updating {filepath}: {e}")
        return False

def main():
    print("=" * 70)
    print("uDOS Path Update Script - All Documentation")
    print("=" * 70)
    print()

    base_dir = "/Users/fredbook/Code/uDOS"
    os.chdir(base_dir)

    updated = 0
    skipped = 0
    errors = 0

    for file in FILES:
        result = update_file(file)
        if result is True:
            updated += 1
        elif result is False:
            skipped += 1
        else:
            errors += 1

    print()
    print("=" * 70)
    print(f"Summary: {updated} updated, {skipped} unchanged, {errors} errors")
    print("=" * 70)

if __name__ == "__main__":
    main()
