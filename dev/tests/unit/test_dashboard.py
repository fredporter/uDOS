#!/usr/bin/env python3
"""
Test DASHBOARD command
"""

import sys
import os

# Add project root to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))

from core.commands.system_handler import SystemCommandHandler


# Mock classes
class MockViewport:
    """Mock viewport for testing."""
    def __init__(self):
        self.width = 120
        self.height = 40
        self.device_type = "LAPTOP"
        self.grid_width = 40
        self.grid_height = 20

    def draw_viewport_map(self):
        return "Mock viewport output"


class MockConnection:
    """Mock connection for testing."""
    def __init__(self):
        self.active = True


class MockUserManager:
    """Mock user manager for testing."""
    def __init__(self):
        self.current_user = "test_user"


class MockHistory:
    """Mock history for testing."""
    def __init__(self):
        self.actions = [1, 2, 3, 4, 5]  # 5 items in undo history


def test_dashboard_cli():
    """Test DASHBOARD command in CLI mode."""
    print("=" * 80)
    print("TEST: DASHBOARD Command (CLI mode)")
    print("=" * 80)

    handler = SystemCommandHandler(
        theme='dungeon',
        viewport=MockViewport(),
        connection=MockConnection(),
        user_manager=MockUserManager(),
        history=MockHistory()
    )

    result = handler.handle_dashboard(params=[], grid=None, parser=None)
    print(result)
    print()

    # Validate output sections
    assert "uDOS DASHBOARD" in result
    assert "USER PROFILE" in result
    assert "INSTALLATION INFO" in result
    assert "SYSTEM STATS" in result
    assert "WEB SERVERS" in result
    assert "SANDBOX" in result
    assert "MEMORY" in result
    assert "QUICK COMMANDS" in result

    # Validate specific content
    assert "Python:" in result
    assert "uDOS: v1.0.0" in result
    assert "Connection:" in result
    assert "Terminal: 120×40" in result
    assert "Device: LAPTOP" in result
    assert "Grid: 40×20" in result
    assert "History: Undo(5)" in result

    print("✅ DASHBOARD CLI test passed")
    print()


def test_dashboard_web():
    """Test DASHBOARD command in WEB mode."""
    print("=" * 80)
    print("TEST: DASHBOARD Command (WEB mode)")
    print("=" * 80)

    handler = SystemCommandHandler(
        theme='dungeon',
        viewport=MockViewport(),
        connection=MockConnection(),
        user_manager=MockUserManager(),
        history=MockHistory()
    )

    result = handler.handle_dashboard(params=['WEB'], grid=None, parser=None)
    print(result)
    print()

    # Validate output (should mention dashboard or installation)
    assert "dashboard" in result.lower() or "Dashboard" in result

    print("✅ DASHBOARD WEB test passed")
    print()


if __name__ == '__main__':
    print("\n" + "=" * 80)
    print("DASHBOARD COMMAND TESTS")
    print("=" * 80 + "\n")

    test_dashboard_cli()
    test_dashboard_web()

    print("=" * 80)
    print("✅ ALL TESTS PASSED")
    print("=" * 80)
