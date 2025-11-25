"""
uDOS v1.0.19 - Autocomplete Service Tests
Test smart command, option, and argument suggestions
"""

import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from core.utils.autocomplete import AutocompleteService


def test_command_suggestions():
    """Test command autocomplete."""
    print("\n" + "="*70)
    print("TEST: Command Suggestions")
    print("="*70)

    autocomplete = AutocompleteService()

    # Test 1: Empty input (should return common commands)
    print("\n1. Empty input:")
    suggestions = autocomplete.get_command_suggestions('')
    for i, sug in enumerate(suggestions[:5], 1):
        print(f"   {i}. {sug['command']:<15} - {sug['description']}")

    # Test 2: Partial match "HE"
    print("\n2. Partial 'HE':")
    suggestions = autocomplete.get_command_suggestions('HE')
    for i, sug in enumerate(suggestions, 1):
        score_bar = '█' * int(sug['score'] * 10)
        print(f"   {i}. {sug['command']:<15} {score_bar:<10} {sug['description']}")

    # Test 3: Fuzzy match "FILS" (should match FILE)
    print("\n3. Fuzzy 'FILS' (typo for FILE):")
    suggestions = autocomplete.get_command_suggestions('FILS')
    for i, sug in enumerate(suggestions[:3], 1):
        score_bar = '█' * int(sug['score'] * 10)
        print(f"   {i}. {sug['command']:<15} {score_bar:<10} {sug['description']}")

    # Test 4: Exact match "MAP"
    print("\n4. Exact 'MAP':")
    suggestions = autocomplete.get_command_suggestions('MAP')
    for i, sug in enumerate(suggestions[:3], 1):
        score_bar = '█' * int(sug['score'] * 10)
        print(f"   {i}. {sug['command']:<15} {score_bar:<10} {sug['description']}")

    print("\n✅ Command suggestions test complete")


def test_option_suggestions():
    """Test option/subcommand autocomplete."""
    print("\n" + "="*70)
    print("TEST: Option Suggestions")
    print("="*70)

    autocomplete = AutocompleteService()

    # Test 1: THEME options
    print("\n1. THEME options (no partial):")
    suggestions = autocomplete.get_option_suggestions('THEME', '')
    for i, sug in enumerate(suggestions, 1):
        print(f"   {i}. THEME {sug['option']}")

    # Test 2: THEME with partial "SE"
    print("\n2. THEME 'SE' (should match SET):")
    suggestions = autocomplete.get_option_suggestions('THEME', 'SE')
    for i, sug in enumerate(suggestions, 1):
        print(f"   {i}. THEME {sug['option']}")

    # Test 3: HELP options
    print("\n3. HELP options:")
    suggestions = autocomplete.get_option_suggestions('HELP', '')
    for i, sug in enumerate(suggestions[:5], 1):
        print(f"   {i}. HELP {sug['option']}")

    # Test 4: FILE options
    print("\n4. FILE options with 'P' (PICK, PREVIEW):")
    suggestions = autocomplete.get_option_suggestions('FILE', 'P')
    for i, sug in enumerate(suggestions, 1):
        print(f"   {i}. FILE {sug['option']}")

    print("\n✅ Option suggestions test complete")


def test_argument_suggestions():
    """Test argument autocomplete."""
    print("\n" + "="*70)
    print("TEST: Argument Suggestions")
    print("="*70)

    autocomplete = AutocompleteService()

    # Test 1: Theme SET argument
    print("\n1. THEME SET (should suggest theme names):")
    suggestions = autocomplete.get_argument_suggestions('THEME', 'SET', '')
    for i, sug in enumerate(suggestions, 1):
        print(f"   {i}. {sug['argument']:<15} (type: {sug.get('type', 'unknown')})")

    # Test 2: MAP GOTO (should suggest cell refs)
    print("\n2. MAP GOTO (should suggest cell references):")
    suggestions = autocomplete.get_argument_suggestions('MAP', 'GOTO', '')
    for i, sug in enumerate(suggestions, 1):
        desc = sug.get('description', '')
        print(f"   {i}. {sug['argument']:<10} - {desc}")

    # Test 3: File path suggestions (empty)
    print("\n3. EDIT <empty> (should suggest directories):")
    suggestions = autocomplete.get_argument_suggestions('EDIT', '', '')
    for i, sug in enumerate(suggestions, 1):
        print(f"   {i}. {sug['argument']:<20} (type: {sug.get('type', 'unknown')})")

    print("\n✅ Argument suggestions test complete")


def test_performance():
    """Test autocomplete performance (<50ms target)."""
    print("\n" + "="*70)
    print("TEST: Performance Benchmarks")
    print("="*70)

    import time

    autocomplete = AutocompleteService()

    # Test 100 command suggestion calls
    start = time.perf_counter()
    for i in range(100):
        autocomplete.get_command_suggestions('HE')
    elapsed = (time.perf_counter() - start) * 1000  # Convert to ms
    avg = elapsed / 100

    print(f"\n1. Command suggestions: {avg:.2f}ms average (target: <50ms)")
    print(f"   {'✅ PASS' if avg < 50 else '❌ FAIL - Too slow!'}")

    # Test 100 option suggestion calls
    start = time.perf_counter()
    for i in range(100):
        autocomplete.get_option_suggestions('THEME', 'SE')
    elapsed = (time.perf_counter() - start) * 1000
    avg = elapsed / 100

    print(f"\n2. Option suggestions: {avg:.2f}ms average (target: <50ms)")
    print(f"   {'✅ PASS' if avg < 50 else '❌ FAIL - Too slow!'}")

    # Test 100 argument suggestion calls
    start = time.perf_counter()
    for i in range(100):
        autocomplete.get_argument_suggestions('THEME', 'SET', '')
    elapsed = (time.perf_counter() - start) * 1000
    avg = elapsed / 100

    print(f"\n3. Argument suggestions: {avg:.2f}ms average (target: <50ms)")
    print(f"   {'✅ PASS' if avg < 50 else '❌ FAIL - Too slow!'}")


def test_format_suggestions():
    """Test suggestion formatting for CLI display."""
    print("\n" + "="*70)
    print("TEST: Suggestion Formatting")
    print("="*70)

    autocomplete = AutocompleteService()

    # Get some suggestions
    cmd_suggestions = autocomplete.get_command_suggestions('HE')

    print("\n1. Formatted command suggestions (selected=False):")
    for i, sug in enumerate(cmd_suggestions[:3], 1):
        formatted = autocomplete.format_suggestion(sug, i, is_selected=False)
        print(f"   {formatted}")

    print("\n2. Formatted command suggestions (selected=True):")
    if cmd_suggestions:
        formatted = autocomplete.format_suggestion(cmd_suggestions[0], 1, is_selected=True)
        print(f"   {formatted}")

    print("\n✅ Formatting test complete")


if __name__ == '__main__':
    print("\n" + "🚀 uDOS v1.0.19 - Autocomplete Service Tests")
    print("=" * 70)

    test_command_suggestions()
    test_option_suggestions()
    test_argument_suggestions()
    test_performance()
    test_format_suggestions()

    print("\n" + "="*70)
    print("✅ ALL TESTS COMPLETE")
    print("="*70)
    print("\nNext Steps:")
    print("  1. Integrate with prompt_toolkit for CLI")
    print("  2. Add keyboard navigation (Tab, arrows)")
    print("  3. Add command history integration")
    print("  4. Test in real uDOS session")
    print("")
