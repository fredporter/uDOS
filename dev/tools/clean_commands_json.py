#!/usr/bin/env python3
"""
Clean commands.json for v1.3 - Remove bloat, modernize syntax.
"""

import json
import sys
from pathlib import Path

def clean_commands_json(input_path, output_path):
    """Remove DEFERRED commands and clean up structure."""
    
    with open(input_path, 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    original_count = len(data['COMMANDS'])
    
    # Filter out DEFERRED commands
    cleaned_commands = []
    removed_count = 0
    
    for cmd in data['COMMANDS']:
        # Skip DEFERRED commands
        if cmd.get('DEFERRED') and cmd['DEFERRED'] != "":
            removed_count += 1
            print(f"  ❌ Removing DEFERRED: {cmd['NAME']}")
            continue
        
        # Remove DEFERRED field from active commands
        if 'DEFERRED' in cmd:
            del cmd['DEFERRED']
        
        # Clean up NOTES - remove DEFERRED warnings
        if 'NOTES' in cmd:
            cmd['NOTES'] = [note for note in cmd['NOTES'] if '⚠️ DEFERRED' not in note]
            if not cmd['NOTES']:
                del cmd['NOTES']
        
        cleaned_commands.append(cmd)
    
    data['COMMANDS'] = cleaned_commands
    
    # Write cleaned version
    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=2, ensure_ascii=False)
    
    final_count = len(cleaned_commands)
    
    print(f"\n✅ Cleanup Complete:")
    print(f"   Original commands: {original_count}")
    print(f"   Removed DEFERRED: {removed_count}")
    print(f"   Final commands: {final_count}")
    print(f"   Reduction: {removed_count / original_count * 100:.1f}%")
    
    # Count lines
    with open(input_path, 'r') as f:
        original_lines = len(f.readlines())
    with open(output_path, 'r') as f:
        final_lines = len(f.readlines())
    
    print(f"\n📊 File Size:")
    print(f"   Original: {original_lines} lines")
    print(f"   Final: {final_lines} lines")
    print(f"   Saved: {original_lines - final_lines} lines ({(original_lines - final_lines) / original_lines * 100:.1f}%)")

if __name__ == '__main__':
    input_file = Path('core/data/commands.json')
    output_file = Path('core/data/commands.json')
    
    print("🧹 Cleaning commands.json for v1.3...")
    print(f"📂 Input: {input_file}")
    print(f"📝 Output: {output_file}")
    print()
    
    clean_commands_json(input_file, output_file)
    print("\n✨ Done!")
