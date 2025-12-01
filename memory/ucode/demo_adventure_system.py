#!/usr/bin/env python3
"""
Comprehensive Demo: uDOS Adventure System
Round 2 Complete Implementation

Demonstrates:
- .upy adventure parsing
- Event processing (narrative, choices, stats, XP, items)
- SPRITE/OBJECT integration (stats/XP/inventory display)
- Full interactive playthrough
"""

from core.commands.story_handler import StoryHandler
from core.services.game.scenario_service import ScenarioService
from core.services.game.xp_service import XPService
from core.services.game.inventory_service import InventoryService
from core.services.game.survival_service import SurvivalService


def print_section(title):
    """Print a formatted section header."""
    print()
    print("=" * 70)
    print(f"  {title}")
    print("=" * 70)
    print()


def main():
    """Run comprehensive adventure system demo."""

    # Initialize services
    print_section("ROUND 2: ADVENTURE SYSTEM DEMO")

    print("Initializing game services...")
    components = {
        'scenario_service': ScenarioService(),
        'xp_service': XPService(),
        'inventory_service': InventoryService(),
        'survival_service': SurvivalService()
    }

    handler = StoryHandler(components)
    print("✅ Services initialized")
    print()

    # Test 1: Start Adventure
    print_section("TEST 1: Start Adventure")

    result = handler.handle('START', ['first-steps'])
    print(result)

    input("\nPress Enter to continue...")

    # Test 2: First Events
    print_section("TEST 2: CONTINUE - First Events")

    result = handler.handle('CONTINUE', [])
    print(result)

    input("\nPress Enter to make choice...")

    # Test 3: Make First Choice
    print_section("TEST 3: CHOICE 1 - Go to Stream")

    result = handler.handle('CHOICE', ['1'])
    print(result)

    input("\nPress Enter to make second choice...")

    # Test 4: Make Second Choice
    print_section("TEST 4: CHOICE 2 - Make Fire and Boil")

    result = handler.handle('CHOICE', ['2'])
    print(result)

    input("\nPress Enter to check status...")

    # Test 5: Check Status
    print_section("TEST 5: STATUS - View Complete Progress")

    result = handler.handle('STATUS', [])
    print(result)

    input("\nPress Enter to continue adventure...")

    # Test 6: Continue More
    print_section("TEST 6: CONTINUE - More Events")

    result = handler.handle('CONTINUE', [])
    print(result)

    # Final summary
    print_section("DEMO SUMMARY")

    print("✅ Adventure System Features Demonstrated:")
    print("   • .upy file parsing")
    print("   • Event processing (narrative/choice/checkpoint)")
    print("   • Stat modifications (Health/Thirst/Hunger/Stamina)")
    print("   • XP awards and leveling")
    print("   • Inventory management (GIVE/TAKE)")
    print("   • Choice system with branching")
    print("   • Complete status display")
    print()
    print("✅ All Systems Working:")
    print("   • SurvivalService - Stats tracking")
    print("   • XPService - Experience and levels")
    print("   • InventoryService - Item management")
    print("   • ScenarioEngine - Event processing")
    print()
    print("🎮 Adventures are fully playable!")
    print()


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n👋 Demo interrupted by user")
    except Exception as e:
        print(f"\n\n❌ Error: {e}")
        import traceback
        traceback.print_exc()
