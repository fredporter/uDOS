"""
Test PRIVATE Command Functionality - v1.0.20
Demonstrates encrypted storage workflow

Author: uDOS Development Team
"""

import os
import sys
from pathlib import Path

# Add uDOS to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from core.commands.private_commands import PrivateCommandHandler


def test_private_commands():
    """Test PRIVATE command workflow"""

    print("\n" + "=" * 70)
    print("🔒 PRIVATE Command Test Suite - v1.0.20")
    print("=" * 70)

    handler = PrivateCommandHandler()

    # Test 1: Show help
    print("\n📖 TEST 1: PRIVATE HELP")
    print("-" * 70)
    result = handler.handle("HELP", [])
    print(result[:500] + "..." if len(result) > 500 else result)

    # Test 2: Check status (locked)
    print("\n\n🔐 TEST 2: PRIVATE STATUS (locked)")
    print("-" * 70)
    result = handler.handle("STATUS", [])
    print(result)

    # Test 3: Try to list without unlocking
    print("\n\n🚫 TEST 3: PRIVATE LIST (should fail - locked)")
    print("-" * 70)
    result = handler.handle("LIST", [])
    print(result)

    # Test 4: Programmatically unlock (simulating user input)
    print("\n\n🔓 TEST 4: PRIVATE UNLOCK (programmatic)")
    print("-" * 70)
    test_password = "test_password_123"
    handler.encryption_service.set_master_key(test_password)
    handler.password = test_password
    handler.unlocked = True
    print("✅ Private tier unlocked programmatically (for testing)")

    # Test 5: Check status (unlocked)
    print("\n\n✅ TEST 5: PRIVATE STATUS (unlocked)")
    print("-" * 70)
    result = handler.handle("STATUS", [])
    print(result)

    # Test 6: Create a test file and save it
    print("\n\n💾 TEST 6: PRIVATE SAVE (encrypt test file)")
    print("-" * 70)

    # Create test file
    test_file = Path("/tmp/test_private.txt")
    test_content = """
This is a test of the PRIVATE tier encryption system.

Personal Notes:
- This data is encrypted with AES-256-GCM
- Only the device owner can decrypt it
- Perfect for sensitive information

Test completed successfully! 🔒
"""

    with open(test_file, 'w') as f:
        f.write(test_content)

    print(f"Created test file: {test_file}")
    print(f"Content length: {len(test_content)} bytes")

    result = handler.handle("SAVE", [str(test_file)])
    print(result)

    # Test 7: List files
    print("\n\n📋 TEST 7: PRIVATE LIST")
    print("-" * 70)
    result = handler.handle("LIST", [])
    print(result)

    # Test 8: Read the encrypted file
    print("\n\n🔓 TEST 8: PRIVATE READ (decrypt file)")
    print("-" * 70)
    result = handler.handle("READ", ["test_private.txt"])
    print(result)

    # Test 9: Lock tier
    print("\n\n🔒 TEST 9: PRIVATE LOCK")
    print("-" * 70)
    result = handler.handle("LOCK", [])
    print(result)

    # Test 10: Verify locked
    print("\n\n🔐 TEST 10: PRIVATE STATUS (locked again)")
    print("-" * 70)
    result = handler.handle("STATUS", [])
    print(result)

    # Cleanup
    test_file.unlink()

    print("\n" + "=" * 70)
    print("✅ All PRIVATE command tests completed successfully!")
    print("=" * 70)


if __name__ == "__main__":
    test_private_commands()
