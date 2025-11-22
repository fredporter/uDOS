#!/usr/bin/env python3
"""
uDOS System Test Script
Tests startup, commands, and shutdown in CLI mode
"""

import sys
import subprocess
import time
from pathlib import Path

# Change to uDOS root directory (3 levels up from knowledge/system/tests/)
UDOS_ROOT = Path(__file__).parent.parent.parent.parent
import os
os.chdir(UDOS_ROOT)
sys.path.insert(0, str(UDOS_ROOT))

print("=" * 70)
print("uDOS SYSTEM TEST")
print("=" * 70)
print()

# Test 1: Startup
print("TEST 1: System Startup")
print("-" * 70)
try:
    from core.uDOS_main import initialize_system
    components = initialize_system(is_script_mode=True)
    assert 'viewport' in components, "Viewport not initialized"
    assert 'connection' in components, "Connection not initialized"
    assert 'user_manager' in components, "User manager not initialized"
    print("✅ System initialization successful")
    print(f"   Components: {', '.join(components.keys())}")
except Exception as e:
    print(f"❌ Startup failed: {e}")
    sys.exit(1)
print()

# Test 2: Parser
print("TEST 2: Command Parser")
print("-" * 70)
try:
    from core.uDOS_parser import Parser
    p = Parser()

    # Test valid command
    ucode = p.parse("help")
    assert ucode == "[SYSTEM|HELP*ALL]", f"Unexpected parse: {ucode}"
    print("✅ Valid command parsing works")

    # Test empty command
    ucode = p.parse("")
    assert "ERROR" in ucode, f"Empty should error: {ucode}"
    print("✅ Empty command handling works")

    # Test complex command
    ucode = p.parse("new story myfile")
    assert "[FILE|NEW" in ucode, f"Complex parse failed: {ucode}"
    print("✅ Complex command parsing works")
except Exception as e:
    print(f"❌ Parser test failed: {e}")
    sys.exit(1)
print()

# Test 3: Directory Structure
print("TEST 3: Directory Structure & Permissions")
print("-" * 70)
try:
    knowledge_path = Path("knowledge")
    memory_path = Path("memory")

    assert knowledge_path.exists(), "knowledge/ directory missing"
    assert knowledge_path.is_dir(), "knowledge/ is not a directory"
    print(f"✅ knowledge/ exists (bundled content)")

    assert memory_path.exists(), "memory/ directory missing"
    assert memory_path.is_dir(), "memory/ is not a directory"
    print(f"✅ memory/ exists (user workspace)")

    # Check key subdirectories
    assert (memory_path / "sandbox").exists(), "memory/sandbox missing"
    assert (memory_path / "workflow").exists(), "memory/workflow missing"
    assert (knowledge_path / "system").exists(), "knowledge/system missing"
    assert (knowledge_path / "README.md").exists(), "knowledge/README.md missing"
    print("✅ Required subdirectories present")

except Exception as e:
    print(f"❌ Directory structure test failed: {e}")
    sys.exit(1)
print()

# Test 4: Command Handler
print("TEST 4: Command Handler")
print("-" * 70)
try:
    from core.uDOS_commands import CommandHandler
    from core.uDOS_grid import Grid
    from core.uDOS_logger import Logger
    from core.services.history_manager import ActionHistory
    from core.services.connection_manager import ConnectionMonitor
    from core.utils.viewport import ViewportDetector
    from core.services.user_manager import UserManager
    from core.services.history import CommandHistory

    # Initialize components
    parser = Parser()
    grid = Grid()
    logger = Logger()
    history = ActionHistory(logger=logger)
    connection = ConnectionMonitor()
    viewport = ViewportDetector()
    user_manager = UserManager()
    command_history = CommandHistory()

    handler = CommandHandler(
        history=history,
        connection=connection,
        viewport=viewport,
        user_manager=user_manager,
        command_history=command_history,
        logger=logger
    )

    # Test HELP command
    ucode = parser.parse("help")
    result = handler.handle_command(ucode, grid, parser)
    assert result and len(result) > 100, "HELP command failed"
    assert "COMMAND REFERENCE" in result, "HELP output invalid"
    print("✅ HELP command works")

    # Test STATUS command
    ucode = parser.parse("status")
    result = handler.handle_command(ucode, grid, parser)
    assert result is not None, "STATUS command returned None"
    print("✅ STATUS command executes (returns output)")

    # Test blank command handler
    ucode = parser.parse("blank")
    result = handler.handle_command(ucode, grid, parser)
    assert result is not None, "BLANK command failed"
    print("✅ BLANK command works")    # Test empty command handling
    ucode = parser.parse("")
    result = handler.handle_command(ucode, grid, parser)
    assert "ERROR" in result, "Empty command should error"
    print("✅ Empty command error handling works")

except Exception as e:
    print(f"❌ Command handler test failed: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)
print()

# Test 5: Reboot Flag
print("TEST 5: REBOOT Command Flag")
print("-" * 70)
try:
    # Test that reboot command sets the flag
    ucode = parser.parse("reboot")
    result = handler.handle_command(ucode, grid, parser)
    assert handler.reboot_requested == True, "Reboot flag not set"
    print("✅ REBOOT command sets reboot_requested flag")
except Exception as e:
    print(f"❌ Reboot test failed: {e}")
    sys.exit(1)
print()

# Test 6: User Manager
print("TEST 6: User Manager")
print("-" * 70)
try:
    from core.services.user_manager import UserManager
    um = UserManager()

    # Test that get_user_data method exists
    assert hasattr(um, 'get_user_data'), "get_user_data method missing"

    # Try calling it
    data = um.get_user_data()
    # It might be None if no user.json exists yet, that's ok
    print(f"✅ UserManager.get_user_data() works (data: {'present' if data else 'none'})")

except Exception as e:
    print(f"❌ User manager test failed: {e}")
    sys.exit(1)
print()

print("=" * 70)
print("✅ ALL TESTS PASSED")
print("=" * 70)
print()
print("System is ready for interactive use!")
print("Run: ./start_udos.sh")
print()
