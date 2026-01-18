#!/usr/bin/env python3
"""
uPY Syntax Migration Tool (v1.2.24)

Upgrades existing .upy files from legacy syntax to Python-first format.

Changes:
- Commas → Pipes in COMMAND[...] syntax
- Double-dash tags → Asterisk tags (COMMAND--tag → COMMAND*TAG)
- Validates forbidden characters in variables/filenames
- Preserves emoji codes (already in new format)
- Reports Python compatibility issues

Usage:
    python dev/tools/upgrade_upy_syntax.py [path]
    
Examples:
    python dev/tools/upgrade_upy_syntax.py memory/ucode/scripts/
    python dev/tools/upgrade_upy_syntax.py memory/ucode/scripts/water.upy
    python dev/tools/upgrade_upy_syntax.py --dry-run memory/ucode/
"""

import os
import re
import sys
from pathlib import Path
from typing import List, Tuple, Dict

# Forbidden characters in variables/filenames (only output text)
FORBIDDEN_CHARS = '`~@#$%^&*[]{}\'\"<>\\|_'

class SyntaxUpgrader:
    """Upgrades .upy files to Python-first syntax."""
    
    def __init__(self, dry_run: bool = False):
        self.dry_run = dry_run
        self.stats = {
            'files_scanned': 0,
            'files_modified': 0,
            'commas_converted': 0,
            'tags_converted': 0,
            'warnings': []
        }
    
    def scan_file(self, filepath: Path) -> Tuple[str, bool, List[str]]:
        """Scan a .upy file and return upgraded content with warnings.
        
        Returns:
            (upgraded_content, needs_upgrade, warnings)
        """
        with open(filepath, 'r', encoding='utf-8') as f:
            content = f.read()
        
        original = content
        warnings = []
        
        # 1. Convert commas to pipes in COMMAND[...] syntax
        # Pattern: COMMAND[arg1, arg2, arg3] → COMMAND[arg1|arg2|arg3]
        def replace_commas(match):
            cmd = match.group(1)
            args = match.group(2)
            
            # Only replace commas NOT inside quotes
            # Simple heuristic: split by comma, check quote balance
            result_args = []
            current = ""
            in_quotes = False
            quote_char = None
            
            for char in args:
                if char in ('"', "'") and (not in_quotes or char == quote_char):
                    in_quotes = not in_quotes
                    quote_char = char if in_quotes else None
                    current += char
                elif char == ',' and not in_quotes:
                    result_args.append(current.strip())
                    current = ""
                    self.stats['commas_converted'] += 1
                else:
                    current += char
            
            if current.strip():
                result_args.append(current.strip())
            
            return f"{cmd}[{'|'.join(result_args)}]"
        
        # Match WORD[...] where WORD is uppercase command
        command_pattern = r'([A-Z_]+)\[([^\]]+)\]'
        content = re.sub(command_pattern, replace_commas, content)
        
        # 2. Convert double-dash tags to asterisk tags
        # COMMAND--tag → COMMAND*TAG (uppercase the tag)
        def replace_tags(match):
            cmd = match.group(1)
            tag = match.group(2).upper()  # Uppercase the tag
            self.stats['tags_converted'] += 1
            return f"{cmd}*{tag}"
        
        tag_pattern = r'([A-Z_]+)--([a-zA-Z0-9-]+)'
        content = re.sub(tag_pattern, replace_tags, content)
        
        # 3. Check for forbidden characters in variable names
        # Pattern: {$variable_name} or variable_name = ...
        var_pattern = r'\{\$([a-zA-Z0-9_-]+)\}'
        variables = re.findall(var_pattern, content)
        
        for var in variables:
            if any(char in FORBIDDEN_CHARS for char in var):
                warnings.append(
                    f"Variable '{{${var}}}' contains forbidden characters: "
                    f"{[c for c in var if c in FORBIDDEN_CHARS]}"
                )
            
            # Check for underscores specifically
            if '_' in var:
                warnings.append(
                    f"Variable '{{${var}}}' uses underscores - "
                    f"uCODE uses dashes: {{${var.replace('_', '-')}}}"
                )
        
        # 4. Check for Python syntax issues
        # Warn about common issues
        if 'def ' in content and not content.strip().startswith('#'):
            # Python function definitions should use underscores
            func_pattern = r'def\s+([a-zA-Z0-9_-]+)\s*\('
            functions = re.findall(func_pattern, content)
            for func in functions:
                if '-' in func:
                    warnings.append(
                        f"Python function '{func}' uses dashes - "
                        f"should be: {func.replace('-', '_')}"
                    )
        
        needs_upgrade = (content != original)
        
        return content, needs_upgrade, warnings
    
    def upgrade_file(self, filepath: Path) -> bool:
        """Upgrade a single .upy file.
        
        Returns:
            True if file was modified
        """
        self.stats['files_scanned'] += 1
        
        try:
            upgraded_content, needs_upgrade, warnings = self.scan_file(filepath)
            
            if warnings:
                self.stats['warnings'].extend([
                    f"{filepath}: {w}" for w in warnings
                ])
            
            if needs_upgrade:
                if not self.dry_run:
                    # Backup original
                    backup_path = filepath.with_suffix('.upy.bak')
                    filepath.rename(backup_path)
                    
                    # Write upgraded version
                    with open(filepath, 'w', encoding='utf-8') as f:
                        f.write(upgraded_content)
                    
                    print(f"✅ Upgraded: {filepath}")
                    print(f"   Backup: {backup_path}")
                else:
                    print(f"🔍 Would upgrade: {filepath}")
                
                self.stats['files_modified'] += 1
                return True
            else:
                print(f"✓ Already up-to-date: {filepath}")
                return False
        
        except Exception as e:
            print(f"❌ Error processing {filepath}: {e}")
            return False
    
    def upgrade_directory(self, dirpath: Path, recursive: bool = True):
        """Upgrade all .upy files in a directory."""
        pattern = '**/*.upy' if recursive else '*.upy'
        
        for filepath in dirpath.glob(pattern):
            if filepath.is_file():
                self.upgrade_file(filepath)
    
    def print_stats(self):
        """Print upgrade statistics."""
        print("\n" + "="*60)
        print("UPGRADE STATISTICS")
        print("="*60)
        print(f"Files scanned:      {self.stats['files_scanned']}")
        print(f"Files modified:     {self.stats['files_modified']}")
        print(f"Commas converted:   {self.stats['commas_converted']}")
        print(f"Tags converted:     {self.stats['tags_converted']}")
        print(f"Warnings:           {len(self.stats['warnings'])}")
        
        if self.stats['warnings']:
            print("\n" + "="*60)
            print("WARNINGS")
            print("="*60)
            for warning in self.stats['warnings']:
                print(f"⚠️  {warning}")
        
        print("\n" + "="*60)
        if self.dry_run:
            print("DRY RUN - No files were modified")
            print("Run without --dry-run to apply changes")
        else:
            print(f"✅ Upgrade complete!")
            print("Original files backed up with .bak extension")
        print("="*60)


def main():
    """Main entry point."""
    import argparse
    
    parser = argparse.ArgumentParser(
        description='Upgrade .upy files to Python-first syntax (v1.2.24)',
        epilog='Examples:\n'
               '  %(prog)s memory/ucode/scripts/\n'
               '  %(prog)s memory/ucode/scripts/water.upy\n'
               '  %(prog)s --dry-run memory/ucode/',
        formatter_class=argparse.RawDescriptionHelpFormatter
    )
    
    parser.add_argument(
        'path',
        type=str,
        nargs='?',
        default='memory/ucode/',
        help='File or directory to upgrade (default: memory/ucode/)'
    )
    
    parser.add_argument(
        '--dry-run',
        action='store_true',
        help='Preview changes without modifying files'
    )
    
    parser.add_argument(
        '--no-recursive',
        action='store_true',
        help='Don\'t scan subdirectories'
    )
    
    args = parser.parse_args()
    
    # Resolve path relative to project root
    project_root = Path(__file__).parent.parent.parent
    target_path = project_root / args.path
    
    if not target_path.exists():
        print(f"❌ Path not found: {target_path}")
        sys.exit(1)
    
    print("="*60)
    print("uPY SYNTAX MIGRATION TOOL (v1.2.24)")
    print("="*60)
    print(f"Target: {target_path}")
    print(f"Mode: {'DRY RUN' if args.dry_run else 'UPGRADE'}")
    print("="*60)
    print()
    
    upgrader = SyntaxUpgrader(dry_run=args.dry_run)
    
    if target_path.is_file():
        if target_path.suffix != '.upy':
            print(f"❌ Not a .upy file: {target_path}")
            sys.exit(1)
        upgrader.upgrade_file(target_path)
    else:
        upgrader.upgrade_directory(target_path, recursive=not args.no_recursive)
    
    upgrader.print_stats()


if __name__ == '__main__':
    main()
