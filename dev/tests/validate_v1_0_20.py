"""
Quick Validation Test for v1.0.20 - 4-Tier Knowledge Bank

Validates that all services and command handlers exist and are importable.

Author: uDOS Development Team
Version: 1.0.20
"""

import sys
from pathlib import Path

print("\n" + "=" * 70)
print(" uDOS v1.0.20 - 4-Tier Knowledge Bank Validation")
print("=" * 70 + "\n")

tests_passed = 0
tests_failed = 0

def test(name, func):
    """Run a test and report result"""
    global tests_passed, tests_failed
    try:
        func()
        print(f"✅ {name}")
        tests_passed += 1
    except Exception as e:
        print(f"❌ {name}: {e}")
        tests_failed += 1

# Test 1: Services exist and importable
def test_services():
    from core.services.memory_manager import MemoryManager, MemoryTier
    from core.services.encryption_service import EncryptionService
    from core.services.sharing_service import SharingService, SharePermission
    from core.services.community_service import CommunityService, GroupRole
    assert MemoryManager is not None
    assert EncryptionService is not None
    assert SharingService is not None
    assert CommunityService is not None

test("All 4 services importable", test_services)

# Test 2: Command handlers exist
def test_handlers():
    from core.commands.memory_commands import MemoryCommandHandler
    from core.commands.private_commands import PrivateCommandHandler
    from core.commands.shared_commands import SharedCommandHandler
    from core.commands.community_commands import CommunityCommandHandler
    from core.commands.knowledge_commands import KnowledgeCommandHandler
    assert MemoryCommandHandler is not None
    assert PrivateCommandHandler is not None
    assert SharedCommandHandler is not None
    assert CommunityCommandHandler is not None
    assert KnowledgeCommandHandler is not None

test("All 5 command handlers importable", test_handlers)

# Test 3: MemoryManager initializes
def test_memory_manager():
    from core.services.memory_manager import MemoryManager, MemoryTier
    manager = MemoryManager()
    # Should create all tier paths
    for tier in MemoryTier:
        path = manager.get_tier_path(tier)
        assert path.exists(), f"Tier {tier} path not created"

test("MemoryManager creates tier structure", test_memory_manager)

# Test 4: Encryption Service initializes
def test_encryption():
    from core.services.encryption_service import EncryptionService
    service = EncryptionService()
    assert service is not None
    assert hasattr(service, 'set_master_key')
    assert hasattr(service, 'encrypt')
    assert hasattr(service, 'decrypt')

test("EncryptionService has required methods", test_encryption)

# Test 5: Sharing Service initializes
def test_sharing():
    from core.services.sharing_service import SharingService
    service = SharingService()
    assert service is not None
    assert hasattr(service, 'grant_access')
    assert hasattr(service, 'revoke_access')
    assert hasattr(service, 'check_access')

test("SharingService has required methods", test_sharing)

# Test 6: Community Service initializes
def test_community():
    from core.services.community_service import CommunityService
    service = CommunityService()
    assert service is not None
    assert hasattr(service, 'create_group')
    assert hasattr(service, 'join_group')
    assert hasattr(service, 'add_contribution')

test("CommunityService has required methods", test_community)

# Test 7: Memory Command Handler works
def test_memory_cmd():
    from core.commands.memory_commands import MemoryCommandHandler
    handler = MemoryCommandHandler()
    result = handler.handle("HELP", [])
    assert "MEMORY" in result
    assert "STATUS" in result

test("MEMORY command handler responds", test_memory_cmd)

# Test 8: Private Command Handler works
def test_private_cmd():
    from core.commands.private_commands import PrivateCommandHandler
    handler = PrivateCommandHandler()
    result = handler.handle("HELP", [])
    assert "PRIVATE" in result
    assert "SAVE" in result or "save" in result

test("PRIVATE command handler responds", test_private_cmd)

# Test 9: Shared Command Handler works
def test_shared_cmd():
    from core.commands.shared_commands import SharedCommandHandler
    handler = SharedCommandHandler()
    result = handler.handle("HELP", [])
    assert "SHARED" in result
    assert "GRANT" in result or "grant" in result

test("SHARED command handler responds", test_shared_cmd)

# Test 10: Community Command Handler works
def test_community_cmd():
    from core.commands.community_commands import CommunityCommandHandler
    handler = CommunityCommandHandler()
    result = handler.handle("HELP", [])
    assert "COMMUNITY" in result
    assert "CREATE" in result or "create" in result

test("COMMUNITY command handler responds", test_community_cmd)

# Test 11: Knowledge Command Handler works
def test_knowledge_cmd():
    from core.commands.knowledge_commands import KnowledgeCommandHandler
    handler = KnowledgeCommandHandler()
    result = handler.handle("HELP", [])
    assert "KNOWLEDGE" in result
    assert "CONTRIBUTE" in result or "contribute" in result

test("KNOWLEDGE command handler responds", test_knowledge_cmd)

# Test 12: Tier paths exist
def test_tier_paths():
    memory_path = Path(__file__).parent.parent
    assert (memory_path / "private").exists()
    assert (memory_path / "shared").exists()
    assert (memory_path / "groups").exists()
    assert (memory_path / "public").exists()

test("All 4 tier directories exist", test_tier_paths)

# Test 13: READMEs exist
def test_readmes():
    memory_path = Path(__file__).parent.parent
    assert (memory_path / "private" / "README.md").exists()
    assert (memory_path / "shared" / "README.md").exists()
    assert (memory_path / "groups" / "README.md").exists()
    assert (memory_path / "public" / "README.md").exists()

test("All tier READMEs exist", test_readmes)

# Test 14: .gitignore exists
def test_gitignore():
    memory_path = Path(__file__).parent.parent
    assert (memory_path / ".gitignore").exists()
    content = (memory_path / ".gitignore").read_text()
    assert "*.enc" in content
    assert "*.json" in content

test(".gitignore properly configured", test_gitignore)

# Test 15: MemoryManager stats work
def test_stats():
    from core.services.memory_manager import MemoryManager, MemoryTier
    manager = MemoryManager()
    stats = manager.get_tier_stats(MemoryTier.PRIVATE)
    assert 'file_count' in stats
    assert 'total_size' in stats
    assert 'total_size_mb' in stats

test("MemoryManager statistics working", test_stats)

# Summary
print("\n" + "=" * 70)
print(" Test Summary")
print("=" * 70)
print(f"Tests run: {tests_passed + tests_failed}")
print(f"✅ Passed: {tests_passed}")
print(f"❌ Failed: {tests_failed}")
print("=" * 70 + "\n")

if tests_failed == 0:
    print("🎉 All tests passed! v1.0.20 implementation validated.\n")
    sys.exit(0)
else:
    print(f"⚠️  {tests_failed} test(s) failed. Review errors above.\n")
    sys.exit(1)
