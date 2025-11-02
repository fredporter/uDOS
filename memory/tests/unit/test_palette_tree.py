#!/usr/bin/env python3
"""
Test PALETTE and TREE commands
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
        self.width = 80
        self.height = 24

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
        self.actions = []


def test_palette():
    """Test PALETTE command."""
    print("=" * 60)
    print("TEST: PALETTE Command")
    print("=" * 60)

    handler = SystemCommandHandler(
        theme='dungeon',
        viewport=MockViewport(),
        connection=MockConnection(),
        user_manager=MockUserManager(),
        history=MockHistory()
    )

    result = handler.handle_palette(params=[], grid=None, parser=None)
    print(result)
    print()

    # Validate output
    assert "POLAROID COLOR PALETTE" in result
    assert "PRIMARY COLORS" in result
    assert "MONOCHROME" in result
    assert "GRAYSCALE" in result
    print("✅ PALETTE test passed")
    print()


def test_tree():
    """Test TREE command."""
    print("=" * 60)
    print("TEST: TREE Command (default)")
    print("=" * 60)

    handler = SystemCommandHandler(
        theme='dungeon',
        viewport=MockViewport(),
        connection=MockConnection(),
        user_manager=MockUserManager(),
        history=MockHistory()
    )

    result = handler.handle_tree(params=[], grid=None, parser=None)
    print(result)
    print()

    # Validate output
    assert "REPOSITORY STRUCTURE" in result
    assert "structure.txt" in result
    print("✅ TREE test passed")
    print()


def test_tree_with_folder():
    """Test TREE command with specific folder."""
    print("=" * 60)
    print("TEST: TREE Command (core folder)")
    print("=" * 60)

    handler = SystemCommandHandler(
        theme='dungeon',
        viewport=MockViewport(),
        connection=MockConnection(),
        user_manager=MockUserManager(),
        history=MockHistory()
    )

    result = handler.handle_tree(params=['core'], grid=None, parser=None)
    print(result)
    print()

    # Validate output
    assert "REPOSITORY STRUCTURE" in result
    assert "core/" in result.lower()
    print("✅ TREE with folder test passed")
    print()


def test_tree_with_depth():
    """Test TREE command with depth limit."""
    print("=" * 60)
    print("TEST: TREE Command (depth=2)")
    print("=" * 60)

    handler = SystemCommandHandler(
        theme='dungeon',
        viewport=MockViewport(),
        connection=MockConnection(),
        user_manager=MockUserManager(),
        history=MockHistory()
    )

    result = handler.handle_tree(params=['--depth=2'], grid=None, parser=None)
    print(result)
    print()

    # Validate output
    assert "REPOSITORY STRUCTURE" in result
    assert "Max Depth: 2" in result
    print("✅ TREE with depth test passed")
    print()


if __name__ == '__main__':
    print("\n" + "=" * 60)
    print("PALETTE & TREE COMMAND TESTS")
    print("=" * 60 + "\n")

    test_palette()
    test_tree()
    test_tree_with_folder()
    test_tree_with_depth()

    print("=" * 60)
    print("✅ ALL TESTS PASSED")
    print("=" * 60)
