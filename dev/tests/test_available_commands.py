#!/usr/bin/env python3
"""
uDOS Available Commands Test
Tests what commands are actually available in v1.0.10
"""

import sys
import os

# Add uDOS core to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../../core'))

def test_available_commands():
    """Test various commands to see what's available"""
    print("🧪 Testing available commands...")

    from uDOS_parser import Parser
    parser = Parser()

    # Test various command categories
    test_commands = [
        # System commands
        "HELP",
        "STATUS",
        "REPAIR",
        "CONFIG",

        # Map commands
        "MAP STATUS",
        "MAP VIEW",
        "MAP METRO",

        # File commands
        "FILE PICK",
        "FILE RECENT",

        # Bank commands
        "BANK FIND test",
        "BANK LIST",

        # POKE commands
        "POKE LIST",
        "POKE STATUS",

        # Assist commands
        "OK test question",
        "READ test",
    ]

    valid_commands = []
    invalid_commands = []

    for cmd in test_commands:
        result = parser.parse(cmd)
        if "ERROR" in result:
            invalid_commands.append((cmd, result))
        else:
            valid_commands.append((cmd, result))

    print(f"\n✅ Valid commands ({len(valid_commands)}):")
    for cmd, result in valid_commands:
        print(f"  {cmd} -> {result}")

    print(f"\n❌ Invalid commands ({len(invalid_commands)}):")
    for cmd, result in invalid_commands:
        print(f"  {cmd} -> {result}")

    return len(valid_commands), len(invalid_commands)

def test_command_handlers():
    """Test what command handlers are available"""
    print("\n🧪 Testing command handlers...")

    try:
        from commands.system_handler import SystemCommandHandler
        print("✅ SystemCommandHandler available")
    except:
        print("❌ SystemCommandHandler not available")

    try:
        from commands.map_handler import MapCommandHandler
        print("✅ MapCommandHandler available")
    except:
        print("❌ MapCommandHandler not available")

    try:
        from commands.file_handler import FileCommandHandler
        print("✅ FileCommandHandler available")
    except:
        print("❌ FileCommandHandler not available")

    try:
        from commands.assistant_handler import AssistantCommandHandler
        print("✅ AssistantCommandHandler available")
    except:
        print("❌ AssistantCommandHandler not available")

    try:
        from commands.bank_handler import BankCommandHandler
        print("✅ BankCommandHandler available")
    except ImportError as e:
        print("❌ BankCommandHandler not available")

def main():
    """Run command availability tests"""
    print("🌀 uDOS Command Availability Test")
    print("=" * 40)

    test_command_handlers()
    valid_count, invalid_count = test_available_commands()

    print("\n" + "=" * 40)
    print(f"🎯 Summary: {valid_count} valid, {invalid_count} invalid commands")

    if valid_count > invalid_count:
        print("🎉 Most commands are working!")
    else:
        print("⚠️  Many commands may be unavailable")

if __name__ == "__main__":
    main()
