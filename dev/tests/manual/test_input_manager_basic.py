#!/usr/bin/env python3
"""
Quick test of InputManager functionality
"""

import sys
sys.path.insert(0, '/Users/fredbook/Code/uDOS')

from core.services.input_manager import create_input_manager

def test_input_manager():
    """Test basic InputManager functionality"""

    print("="*60)
    print("Testing InputManager")
    print("="*60)

    # Create manager
    input_mgr = create_input_manager(theme='dungeon')
    print("✓ InputManager created")

    # Test get_field/set_field
    data = {
        'STORY': {
            'USER_NAME': 'Fred',
            'THEME': 'dungeon'
        },
        'OPTIONS': {
            'AUTO_SAVE': True
        }
    }

    # Test get_field
    name = input_mgr.get_field(data, 'STORY.USER_NAME', 'unknown')
    assert name == 'Fred', f"Expected 'Fred', got '{name}'"
    print(f"✓ get_field: STORY.USER_NAME = {name}")

    theme = input_mgr.get_field(data, 'STORY.THEME', 'default')
    assert theme == 'dungeon', f"Expected 'dungeon', got '{theme}'"
    print(f"✓ get_field: STORY.THEME = {theme}")

    missing = input_mgr.get_field(data, 'STORY.MISSING', 'default')
    assert missing == 'default', f"Expected 'default', got '{missing}'"
    print(f"✓ get_field: STORY.MISSING = {missing} (default)")

    # Test set_field
    input_mgr.set_field(data, 'STORY.LOCATION', 'Brisbane')
    location = input_mgr.get_field(data, 'STORY.LOCATION')
    assert location == 'Brisbane', f"Expected 'Brisbane', got '{location}'"
    print(f"✓ set_field: STORY.LOCATION = {location}")

    # Test nested creation
    input_mgr.set_field(data, 'NEW_SECTION.NESTED.VALUE', 42)
    value = input_mgr.get_field(data, 'NEW_SECTION.NESTED.VALUE')
    assert value == 42, f"Expected 42, got {value}"
    print(f"✓ set_field: NEW_SECTION.NESTED.VALUE = {value}")

    print("\n✅ All InputManager tests passed!")
    print("="*60)

if __name__ == '__main__':
    test_input_manager()
