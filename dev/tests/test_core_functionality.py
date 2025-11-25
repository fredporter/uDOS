#!/usr/bin/env python3
"""
uDOS Core Functionality Test
Tests basic uDOS components without terminal interface
"""

import sys
import os
from pathlib import Path

# Add uDOS core to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'core'))

def test_imports():
    """Test if core uDOS modules can be imported"""
    print("🧪 Testing uDOS imports...")

    try:
        from uDOS_parser import Parser
        print("✅ Parser import successful")
    except Exception as e:
        print(f"❌ Parser import failed: {e}")
        return False

    try:
        from uDOS_grid import Grid
        print("✅ Grid import successful")
    except Exception as e:
        print(f"❌ Grid import failed: {e}")
        return False

    try:
        from commands.system_handler import SystemCommandHandler
        print("✅ System handler import successful")
    except Exception as e:
        print(f"❌ System handler import failed: {e}")
        return False

    try:
        from commands.map_handler import MapCommandHandler
        print("✅ Map handler import successful")
    except Exception as e:
        print(f"❌ Map handler import failed: {e}")
        return False

    return True

def test_basic_parsing():
    """Test basic command parsing"""
    print("\n🧪 Testing command parsing...")

    try:
        from uDOS_parser import Parser
        parser = Parser()

        # Test basic commands
        test_commands = [
            "HELP",
            "STATUS",
            "MAP STATUS",
            "FILE LIST"
        ]

        for cmd in test_commands:
            result = parser.parse(cmd)
            print(f"✅ '{cmd}' -> {result}")

        return True
    except Exception as e:
        print(f"❌ Parsing test failed: {e}")
        return False

def test_grid_system():
    """Test grid system"""
    print("\n🧪 Testing grid system...")

    try:
        from uDOS_grid import Grid
        grid = Grid()

        print(f"✅ Grid initialized: {grid.width}x{grid.height}")
        return True
    except Exception as e:
        print(f"❌ Grid test failed: {e}")
        return False

def test_basic_commands():
    """Test basic command execution"""
    print("\n🧪 Testing basic command execution...")

    try:
        from uDOS_parser import Parser
        from uDOS_grid import Grid
        from commands.system_handler import SystemCommandHandler

        parser = Parser()
        grid = Grid()

        # Create minimal handler
        handler = SystemCommandHandler()

        # Test STATUS command
        ucode = parser.parse("STATUS")
        print(f"✅ STATUS parsed: {ucode}")

        return True
    except Exception as e:
        print(f"❌ Command execution test failed: {e}")
        return False

def main():
    """Run all tests"""
    print("🌀 uDOS Core Functionality Test Suite")
    print("=" * 40)

    tests = [
        test_imports,
        test_basic_parsing,
        test_grid_system,
        test_basic_commands
    ]

    passed = 0
    total = len(tests)

    for test in tests:
        try:
            if test():
                passed += 1
        except Exception as e:
            print(f"❌ Test {test.__name__} crashed: {e}")

    print("\n" + "=" * 40)
    print(f"🎯 Results: {passed}/{total} tests passed")

    if passed == total:
        print("🎉 All tests passed! uDOS core is functional.")
        return 0
    else:
        print("⚠️  Some tests failed. Check output above.")
        return 1

if __name__ == "__main__":
    sys.exit(main())
