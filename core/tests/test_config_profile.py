#!/usr/bin/env python3
"""
Test script for CONFIG command user profile updates.
Verifies that CONFIG properly saves username, password, timezone, and location.
"""

import json
import sys
import os
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from core.services.story_manager import StoryManager
from core.utils.system_info import get_system_timezone

def test_config_profile_update():
    """Test that CONFIG command updates work through story_manager."""

    print("=" * 70)
    print("CONFIG COMMAND - USER PROFILE UPDATE TEST")
    print("=" * 70)
    print()

    # 1. Test timezone detection
    print("1. Testing timezone detection...")
    tz, city = get_system_timezone()
    print(f"   ✓ Detected timezone: {tz}")
    print(f"   ✓ Detected city: {city}")
    print()

    # 2. Initialize StoryManager
    print("2. Initializing StoryManager...")
    story_manager = StoryManager(story_path="memory/sandbox/user.json")
    print(f"   ✓ Story manager initialized")
    print()

    # 3. Check current profile
    print("3. Current user profile:")
    user_name = story_manager.get_field('STORY.USER_NAME', 'Not set')
    password = story_manager.get_field('STORY.PASSWORD', 'Not set')
    location = story_manager.get_field('STORY.LOCATION', 'Not set')
    timezone = story_manager.get_field('STORY.TIMEZONE', 'Not set')

    print(f"   Username: {user_name}")
    print(f"   Password: {'●●●●●●' if password and password != 'Not set' else 'Not set'}")
    print(f"   Location: {location}")
    print(f"   Timezone: {timezone}")
    print()

    # 4. Test updating fields
    print("4. Testing field updates...")
    test_username = "test_user"
    test_password = "test_pass_123"
    test_timezone = "America/New_York"
    test_location = "New York"

    story_manager.set_field('STORY.USER_NAME', test_username, auto_save=False)
    print(f"   ✓ Set username: {test_username}")

    story_manager.set_field('STORY.PASSWORD', test_password, auto_save=False)
    print(f"   ✓ Set password: ●●●●●●")

    story_manager.set_field('STORY.TIMEZONE', test_timezone, auto_save=False)
    print(f"   ✓ Set timezone: {test_timezone}")

    story_manager.set_field('STORY.LOCATION', test_location, auto_save=True)
    print(f"   ✓ Set location: {test_location}")
    print()

    # 5. Verify save worked
    print("5. Verifying save to user.json...")
    if Path("memory/sandbox/user.json").exists():
        with open("memory/sandbox/user.json", 'r') as f:
            saved_data = json.load(f)

        story_section = saved_data.get('STORY', {})
        saved_username = story_section.get('USER_NAME', 'NOT FOUND')
        saved_password = story_section.get('PASSWORD', 'NOT FOUND')
        saved_timezone = story_section.get('TIMEZONE', 'NOT FOUND')
        saved_location = story_section.get('LOCATION', 'NOT FOUND')

        print(f"   Username in file: {saved_username}")
        print(f"   Password in file: {'●●●●●●' if saved_password != 'NOT FOUND' else 'NOT FOUND'}")
        print(f"   Timezone in file: {saved_timezone}")
        print(f"   Location in file: {saved_location}")
        print()

        # 6. Validate
        print("6. Validation:")
        all_match = True

        if saved_username != test_username:
            print(f"   ❌ Username mismatch: expected '{test_username}', got '{saved_username}'")
            all_match = False
        else:
            print(f"   ✓ Username matches")

        if saved_password != test_password:
            print(f"   ❌ Password mismatch")
            all_match = False
        else:
            print(f"   ✓ Password matches")

        if saved_timezone != test_timezone:
            print(f"   ❌ Timezone mismatch: expected '{test_timezone}', got '{saved_timezone}'")
            all_match = False
        else:
            print(f"   ✓ Timezone matches")

        if saved_location != test_location:
            print(f"   ❌ Location mismatch: expected '{test_location}', got '{saved_location}'")
            all_match = False
        else:
            print(f"   ✓ Location matches")

        print()

        if all_match:
            print("=" * 70)
            print("✅ ALL TESTS PASSED - CONFIG command should work correctly!")
            print("=" * 70)
            return 0
        else:
            print("=" * 70)
            print("❌ SOME TESTS FAILED - Review errors above")
            print("=" * 70)
            return 1
    else:
        print("   ❌ user.json file not found!")
        return 1

if __name__ == '__main__':
    sys.exit(test_config_profile_update())
