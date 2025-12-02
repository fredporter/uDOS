#!/usr/bin/env python3
"""
Migrate old .upy files to new COMMAND(args) syntax.

Usage:
    python bin/migrate_upy.py sandbox/ucode/old_file.upy
    python bin/migrate_upy.py sandbox/ucode/*.upy  # Batch mode
"""

import sys
import os
import re
from pathlib import Path

# Add core to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from core.runtime.upy_parser import UPYParser


def migrate_file(input_path: str, output_path: str = None) -> bool:
    """
    Migrate a .upy file from old to new format.

    Args:
        input_path: Path to old format .upy file
        output_path: Optional output path (default: same path with .new.upy)

    Returns:
        True if successful
    """
    if not os.path.exists(input_path):
        print(f"❌ File not found: {input_path}")
        return False

    if output_path is None:
        base = input_path.replace('.upy', '')
        output_path = f"{base}.new.upy"

    parser = UPYParser()

    print(f"📄 Migrating: {input_path}")
    print(f"   Output: {output_path}")

    try:
        with open(input_path, 'r') as f:
            content = f.read()

        # Line-by-line migration
        lines = content.split('\n')
        migrated_lines = []

        for line in lines:
            original = line
            stripped = line.strip()

            # Keep comments and empty lines
            if not stripped or stripped.startswith('#'):
                migrated_lines.append(original)
                continue

            # Try to detect old format patterns
            try:
                # Pattern 1: SET VAR value → SPRITE-SET('VAR'|value)
                if stripped.startswith('SET '):
                    parts = stripped[4:].split(None, 1)
                    if len(parts) == 2:
                        var_name = parts[0]
                        value = parts[1]

                        # Handle numbers
                        if value.isdigit() or (value.startswith('-') and value[1:].isdigit()):
                            migrated = f"SPRITE-SET('{var_name}'|{value})"
                        # Handle quoted strings
                        elif value.startswith("'") or value.startswith('"'):
                            migrated = f"SPRITE-SET('{var_name}'|{value})"
                        else:
                            migrated = f"SPRITE-SET('{var_name}'|'{value}')"

                        # Preserve indentation
                        indent = len(original) - len(original.lstrip())
                        migrated_lines.append(' ' * indent + migrated)
                        print(f"  • {stripped[:40]} → {migrated[:40]}")
                        continue

                # Pattern 2: PRINT [text] or PRINT (text) → PRINT('text')
                if stripped.startswith('PRINT '):
                    content = stripped[6:].strip()

                    # Remove brackets if present
                    if content.startswith('[') and content.endswith(']'):
                        content = content[1:-1]
                    # Remove parens if present
                    elif content.startswith('(') and content.endswith(')'):
                        content = content[1:-1]

                    # Check for variable interpolation {VAR}
                    if '{' in content:
                        # Convert {VAR} to $VAR
                        content = re.sub(r'\{([A-Z-]+)\}', r'$\1', content)

                    # Don't double-quote already quoted strings
                    if not (content.startswith("'") and content.endswith("'")):
                        migrated = f"PRINT('{content}')"
                    else:
                        migrated = f"PRINT({content})"

                    indent = len(original) - len(original.lstrip())
                    migrated_lines.append(' ' * indent + migrated)
                    print(f"  • {stripped[:40]} → {migrated[:40]}")
                    continue

                # Pattern 2b: PRINT(text) with emoji - keep as-is
                if re.match(r'PRINT\([\'"]', stripped):
                    migrated_lines.append(original)
                    continue

                # Pattern 3: IF condition THEN → {IF condition:
                if stripped.startswith('IF ') and ' THEN' in stripped:
                    condition = stripped[3:stripped.find(' THEN')].strip()
                    # Convert {$VAR} to $VAR
                    condition = re.sub(r'\{\$([A-Z-]+)\}', r'$\1', condition)
                    migrated = f"{{IF {condition}:"
                    indent = len(original) - len(original.lstrip())
                    migrated_lines.append(' ' * indent + migrated)
                    print(f"  • {stripped[:40]} → {migrated[:40]}")
                    continue

                # Pattern 4: ELSE → }
                if stripped == 'ELSE':
                    indent = len(original) - len(original.lstrip())
                    migrated_lines.append(' ' * indent + "} ELSE: {")
                    print(f"  • ELSE → }} ELSE: {{")
                    continue

                # Pattern 5: END → }
                if stripped == 'END':
                    indent = len(original) - len(original.lstrip())
                    migrated_lines.append(' ' * indent + "}")
                    print(f"  • END → }}")
                    continue

                # Pattern 6: ROLL dice → GAME-ROLL('dice')
                roll_match = re.match(r'ROLL\s+(\d+d\d+)', stripped)
                if roll_match:
                    dice = roll_match.group(1)
                    migrated = f"GAME-ROLL('{dice}')"
                    indent = len(original) - len(original.lstrip())
                    migrated_lines.append(' ' * indent + migrated)
                    print(f"  • {stripped} → {migrated}")
                    continue

                # Pattern 7: Function-style IF {condition | action}
                func_if = re.match(r'IF\s+\{(.+?)\s*\|\s*(.+?)\}', stripped)
                if func_if:
                    condition = func_if.group(1)
                    action = func_if.group(2)
                    # Recursively migrate the action
                    migrated = f"{{IF {condition}: {action}}}"
                    indent = len(original) - len(original.lstrip())
                    migrated_lines.append(' ' * indent + migrated)
                    print(f"  • {stripped[:40]} → {migrated[:40]}")
                    continue                # Pattern 3: $VAR = value → SPRITE-SET('VAR'|value)
                var_assign = re.match(r'\$([A-Z-]+)\s*=\s*(.+)', stripped)
                if var_assign:
                    var_name = var_assign.group(1)
                    value = var_assign.group(2).strip()

                    # Handle numbers
                    if value.isdigit() or re.match(r'-?\d+(\.\d+)?', value):
                        migrated = f"SPRITE-SET('{var_name}'|{value})"
                    # Handle quoted strings
                    elif value.startswith("'") or value.startswith('"'):
                        migrated = f"SPRITE-SET('{var_name}'|{value})"
                    else:
                        migrated = f"SPRITE-SET('{var_name}'|'{value}')"

                    indent = len(original) - len(original.lstrip())
                    migrated_lines.append(' ' * indent + migrated)
                    print(f"  • {stripped[:40]} → {migrated[:40]}")
                    continue

                # Pattern 4: Already new format - keep as-is
                if re.match(r'^[A-Z-]+\(', stripped):
                    migrated_lines.append(original)
                    continue

                # Pattern 5: Old uCODE [MODULE|COMMAND*ARGS]
                if stripped.startswith('[') and stripped.endswith(']'):
                    migrated = parser.migrate_ucode_to_upy(stripped)
                    indent = len(original) - len(original.lstrip())
                    migrated_lines.append(' ' * indent + migrated)
                    print(f"  • {stripped[:40]} → {migrated[:40]}")
                    continue

                # Unknown pattern - keep original with warning
                migrated_lines.append(original)
                if stripped and not stripped.startswith('#'):
                    print(f"  ⚠️  Kept as-is: {stripped[:50]}")

            except Exception as e:
                print(f"  ⚠️  Error migrating line: {stripped[:50]}")
                print(f"     {e}")
                migrated_lines.append(original)

        # Write output
        with open(output_path, 'w') as f:
            f.write('\n'.join(migrated_lines))

        print(f"✅ Migration complete: {output_path}")
        return True

    except Exception as e:
        print(f"❌ Migration failed: {e}")
        return False


def main():
    """Main entry point"""
    if len(sys.argv) < 2:
        print("Usage: python bin/migrate_upy.py <file.upy> [output.upy]")
        sys.exit(1)

    input_path = sys.argv[1]
    output_path = sys.argv[2] if len(sys.argv) > 2 else None

    # Handle wildcards
    if '*' in input_path:
        from glob import glob
        files = glob(input_path)
        print(f"📦 Batch migration: {len(files)} files")

        success = 0
        for f in files:
            if migrate_file(f):
                success += 1

        print(f"\n✅ {success}/{len(files)} files migrated")
    else:
        success = migrate_file(input_path, output_path)
        sys.exit(0 if success else 1)


if __name__ == '__main__':
    main()
