#!/usr/bin/env python3
"""
Clean roadmap to remove all v1.1.x historical sections.
Keep only v1.2.x content and Contributing section.
"""

from pathlib import Path

ROADMAP_PATH = Path("dev/roadmap/ROADMAP.MD")

def main():
    print("🧹 Cleaning roadmap - removing v1.1.x historical sections...")

    # Read file
    with open(ROADMAP_PATH, 'r', encoding='utf-8') as f:
        lines = f.readlines()

    # Find the first Contributing section (should be around line 2114)
    contributing_idx = None
    for i, line in enumerate(lines):
        if line.strip() == "## 🤝 Contributing":
            contributing_idx = i
            break

    if contributing_idx is None:
        print("❌ Error: Could not find Contributing section")
        return False

    print(f"✓ Found Contributing section at line {contributing_idx + 1}")

    # Find the end of this Contributing section (look for **License:** MIT)
    license_idx = None
    for i in range(contributing_idx, min(contributing_idx + 50, len(lines))):
        if "**License:** MIT" in lines[i]:
            license_idx = i
            break

    if license_idx is None:
        print("❌ Error: Could not find License line")
        return False

    print(f"✓ Found License line at {license_idx + 1}")

    # Keep everything up to and including the License line
    # Discard everything after that (all v1.1.x content)
    clean_lines = lines[:license_idx + 1]

    # Add final newline
    if not clean_lines[-1].endswith('\n'):
        clean_lines[-1] += '\n'

    # Write cleaned file
    with open(ROADMAP_PATH, 'w', encoding='utf-8') as f:
        f.writelines(clean_lines)

    old_count = len(lines)
    new_count = len(clean_lines)
    removed = old_count - new_count

    print(f"✅ Roadmap cleaned successfully!")
    print(f"📊 Stats:")
    print(f"   Old: {old_count} lines")
    print(f"   New: {new_count} lines")
    print(f"   Removed: {removed} lines (v1.1.x historical content)")

    return True

if __name__ == "__main__":
    import sys
    sys.exit(0 if main() else 1)
