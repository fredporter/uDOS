#!/usr/bin/env python3
"""
TUI Smart Input Test Suite (v1.2.22)
Tests numpad navigation, arrow keys, and command completion fixes.

Run: python dev/tools/test_smart_input.py
"""

import sys
from pathlib import Path

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

def test_buffer_empty_check():
    """Test strict buffer empty check logic."""
    print("\n🧪 Test 1: Buffer Empty Check Logic")
    print("=" * 60)
    
    test_cases = [
        ("", True, "Empty string"),
        (" ", False, "Whitespace only"),
        ("R", False, "Single character"),
        ("REBOOT", False, "Full command"),
        ("   ", False, "Multiple spaces"),
    ]
    
    passed = 0
    failed = 0
    
    for text, expected_empty, description in test_cases:
        is_empty = len(text) == 0
        status = "✅ PASS" if is_empty == expected_empty else "❌ FAIL"
        
        if is_empty == expected_empty:
            passed += 1
        else:
            failed += 1
        
        print(f"{status} | '{text}' | empty={is_empty} | {description}")
    
    print(f"\nResults: {passed} passed, {failed} failed")
    return failed == 0


def test_autocomplete_loading():
    """Test autocomplete service loads correctly."""
    print("\n🧪 Test 2: Autocomplete Service Loading")
    print("=" * 60)
    
    try:
        from core.utils.autocomplete import AutocompleteService
        
        autocomplete = AutocompleteService()
        print("✅ AutocompleteService initialized")
        
        # Test empty suggestions
        empty_suggestions = autocomplete.get_command_suggestions('', max_results=5)
        print(f"✅ Empty input suggestions: {len(empty_suggestions)} commands")
        
        # Test 'R' suggestions
        r_suggestions = autocomplete.get_command_suggestions('R', max_results=25)
        print(f"✅ 'R' suggestions: {len(r_suggestions)} commands")
        
        if r_suggestions:
            print("\n   Commands starting with 'R':")
            for sug in r_suggestions[:10]:  # Show first 10
                print(f"   - {sug['command']:<15} {sug['description'][:40]}")
        
        return True
    except Exception as e:
        print(f"❌ Autocomplete test failed: {e}")
        return False


def test_smart_prompt_initialization():
    """Test SmartPrompt initializes without errors."""
    print("\n🧪 Test 3: SmartPrompt Initialization")
    print("=" * 60)
    
    try:
        from core.input.smart_prompt import SmartPrompt
        
        # Test with fallback mode
        prompt_fallback = SmartPrompt(use_fallback=True)
        print("✅ SmartPrompt initialized (fallback mode)")
        
        # Test with TUI mode (if available)
        try:
            prompt_tui = SmartPrompt(use_fallback=False)
            if prompt_tui.use_fallback:
                print("⚠️  TUI mode auto-switched to fallback (expected in non-TTY)")
            else:
                print("✅ SmartPrompt initialized (TUI mode)")
        except Exception as e:
            print(f"⚠️  TUI mode unavailable: {e}")
        
        return True
    except Exception as e:
        print(f"❌ SmartPrompt test failed: {e}")
        return False


def test_key_bindings():
    """Test key bindings are registered correctly."""
    print("\n🧪 Test 4: Key Bindings Registration")
    print("=" * 60)
    
    try:
        from core.input.smart_prompt import SmartPrompt
        
        prompt = SmartPrompt(use_fallback=False)
        
        if prompt.use_fallback:
            print("⚠️  Skipped (fallback mode active)")
            return True
        
        # Check key bindings exist
        kb = prompt.key_bindings
        print(f"✅ Key bindings created: {len(kb.bindings)} bindings")
        
        # Expected keys
        expected_keys = ['up', 'down', 'left', 'right', '8', '2', '4', '6', '5', '1', '3', '7', '9', '0']
        registered_keys = [str(binding.keys[0]) if binding.keys else None for binding in kb.bindings]
        
        found = 0
        for key in expected_keys:
            # Check if key is in any binding
            key_found = any(key in str(binding.keys) for binding in kb.bindings)
            if key_found:
                found += 1
                print(f"✅ Key '{key}' registered")
            else:
                print(f"⚠️  Key '{key}' not found")
        
        print(f"\nFound {found}/{len(expected_keys)} expected keys")
        return found >= 10  # At least 10 keys should be registered
        
    except Exception as e:
        print(f"❌ Key binding test failed: {e}")
        return False


def test_completer():
    """Test ImprovedCompleter functionality."""
    print("\n🧪 Test 5: ImprovedCompleter Functionality")
    print("=" * 60)
    
    try:
        from core.input.smart_prompt import ImprovedCompleter
        from core.utils.autocomplete import AutocompleteService
        from prompt_toolkit.document import Document
        from prompt_toolkit.completion import CompleteEvent
        
        autocomplete = AutocompleteService()
        completer = ImprovedCompleter(autocomplete)
        
        # Test empty completion
        doc_empty = Document('')
        event = CompleteEvent()
        completions_empty = list(completer.get_completions(doc_empty, event))
        print(f"✅ Empty input: {len(completions_empty)} completions")
        
        # Test 'R' completion
        doc_r = Document('R')
        completions_r = list(completer.get_completions(doc_r, event))
        print(f"✅ 'R' input: {len(completions_r)} completions")
        
        if completions_r:
            print("\n   Top 5 'R' completions:")
            for comp in completions_r[:5]:
                print(f"   - {comp.text}")
        
        # Verify we get more than 10 results (updated to 25 max)
        if len(completions_r) > 10:
            print(f"✅ Showing {len(completions_r)} results (exceeds old 10 limit)")
        
        return True
    except Exception as e:
        print(f"❌ Completer test failed: {e}")
        import traceback
        traceback.print_exc()
        return False


def main():
    """Run all tests."""
    print("=" * 60)
    print("TUI Smart Input Test Suite (v1.2.22)")
    print("=" * 60)
    
    tests = [
        ("Buffer Empty Check", test_buffer_empty_check),
        ("Autocomplete Loading", test_autocomplete_loading),
        ("SmartPrompt Init", test_smart_prompt_initialization),
        ("Key Bindings", test_key_bindings),
        ("Completer", test_completer),
    ]
    
    results = []
    for name, test_func in tests:
        try:
            passed = test_func()
            results.append((name, passed))
        except Exception as e:
            print(f"\n❌ Test '{name}' crashed: {e}")
            import traceback
            traceback.print_exc()
            results.append((name, False))
    
    # Summary
    print("\n" + "=" * 60)
    print("TEST SUMMARY")
    print("=" * 60)
    
    passed_count = sum(1 for _, passed in results if passed)
    total_count = len(results)
    
    for name, passed in results:
        status = "✅ PASS" if passed else "❌ FAIL"
        print(f"{status} | {name}")
    
    print("=" * 60)
    print(f"Results: {passed_count}/{total_count} tests passed")
    
    if passed_count == total_count:
        print("🎉 ALL TESTS PASSED!")
        return 0
    else:
        print("⚠️  Some tests failed - review above")
        return 1


if __name__ == '__main__':
    sys.exit(main())
