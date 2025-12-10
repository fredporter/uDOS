#!/usr/bin/env python3
"""
Quick test to verify completion menu shows multiple items.
Run: python dev/tools/test_completion_menu.py
"""

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from core.utils.autocomplete import AutocompleteService

def test_completions():
    """Test that we get multiple completions for 'R'."""
    print("\n" + "=" * 60)
    print("COMPLETION MENU TEST")
    print("=" * 60)
    
    autocomplete = AutocompleteService()
    
    # Test 'R' completions
    results = autocomplete.get_command_suggestions('R', max_results=25)
    
    print(f"\nSearching for commands starting with 'R'...")
    print(f"Found {len(results)} matches:\n")
    
    for i, result in enumerate(results[:15], 1):  # Show first 15
        cmd = result['command']
        desc = result['description'][:50]
        print(f"{i:2}. {cmd:<15} - {desc}")
    
    if len(results) > 15:
        print(f"\n... and {len(results) - 15} more")
    
    print("\n" + "=" * 60)
    print(f"✅ Total: {len(results)} commands starting with 'R'")
    print("=" * 60)
    
    # Expected commands
    expected = ['READ', 'REBOOT', 'REPAIR', 'RUN', 'REPORT', 'ROLE']
    found = [r['command'] for r in results]
    
    print("\nChecking expected commands:")
    for cmd in expected:
        if cmd in found:
            print(f"  ✅ {cmd} - Found")
        else:
            print(f"  ❌ {cmd} - Missing")
    
    print("\n")

if __name__ == '__main__':
    test_completions()
