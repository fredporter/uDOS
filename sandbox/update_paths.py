#!/usr/bin/env python3
"""Bulk update paths from knowledge/system to core/data and memory/user to sandbox/user"""

import re
from pathlib import Path

# Files and their replacements
replacements = {
    "knowledge/system": "core/data",
    "memory/user": "sandbox/user",
    "memory/logs": "sandbox/logs",
}

# Files to update
files_to_update = [
    "core/commands/configuration_handler.py",
    "core/commands/shakedown_handler.py",
    "core/commands/diagram_handler.py",
    "core/services/gemini_generator.py",
    "core/utils/path_validator.py",
    "core/output/graphics.py",
    "core/services/setup_wizard.py",
]

def update_file(filepath):
    """Update all path references in a file"""
    path = Path(filepath)
    if not path.exists():
        print(f"⚠️  File not found: {filepath}")
        return

    content = path.read_text()
    original = content

    for old, new in replacements.items():
        content = content.replace(old, new)

    if content != original:
        path.write_text(content)
        print(f"✅ Updated: {filepath}")
    else:
        print(f"➖ No changes: {filepath}")

if __name__ == "__main__":
    print("🔧 Updating file paths...")
    for file in files_to_update:
        update_file(file)
    print("\n✨ Path update complete!")
