"""
Comprehensive Test Suite for v1.0.20 - 4-Tier Knowledge Bank & Memory System

Tests all 4 tiers:
- Tier 1: PRIVATE (encrypted storage)
- Tier 2: SHARED (permission-based sharing)
- Tier 3: GROUPS (community knowledge)
- Tier 4: PUBLIC (global knowledge bank)

Plus:
- Cross-tier operations
- Performance benchmarks
- Security validation
- Integration tests

Author: uDOS Development Team
Version: 1.0.20
"""

import unittest
import tempfile
import shutil
from pathlib import Path
import json
import time
from datetime import datetime, timedelta

from core.services.memory_manager import MemoryManager, MemoryTier
from core.services.encryption_service import EncryptionService
from core.services.sharing_service import SharingService, SharePermission
from core.services.community_service import CommunityService, GroupRole
from core.commands.memory_commands import MemoryCommandHandler
from core.commands.private_commands import PrivateCommandHandler
from core.commands.shared_commands import SharedCommandHandler
from core.commands.community_commands import CommunityCommandHandler
from core.commands.knowledge_commands import KnowledgeCommandHandler


class TestMemoryManager(unittest.TestCase):
    """Test MemoryManager service"""

    def setUp(self):
        """Set up test environment"""
        self.test_dir = Path(tempfile.mkdtemp())
        self.manager = MemoryManager(str(self.test_dir))

    def tearDown(self):
        """Clean up test environment"""
        shutil.rmtree(self.test_dir, ignore_errors=True)

    def test_tier_paths_exist(self):
        """Test that all tier directories are created"""
        for tier in MemoryTier:
            path = self.manager.get_tier_path(tier)
            self.assertTrue(path.exists())
            self.assertTrue(path.is_dir())

    def test_tier_stats(self):
        """Test tier statistics collection"""
        # Create test file
        private_path = self.manager.get_tier_path(MemoryTier.PRIVATE)
        test_file = private_path / "test.txt"
        test_file.write_text("test content")

        stats = self.manager.get_tier_stats(MemoryTier.PRIVATE)
        self.assertEqual(stats['file_count'], 1)
        self.assertGreater(stats['total_size'], 0)

    def test_search_all_tiers(self):
        """Test cross-tier searching"""
        # Create files in multiple tiers
        for tier in [MemoryTier.PRIVATE, MemoryTier.SHARED]:
            path = self.manager.get_tier_path(tier)
            (path / "searchable.txt").write_text("findme content")

        results = self.manager.search_all_tiers("findme")
        self.assertEqual(len(results), 2)


class TestEncryptionService(unittest.TestCase):
    """Test EncryptionService (Tier 1)"""

    def setUp(self):
        """Set up test environment"""
        self.test_dir = Path(tempfile.mkdtemp())
        # Create memory structure
        (self.test_dir / '.metadata').mkdir(exist_ok=True)
        self.key_file = self.test_dir / '.metadata' / 'encryption.key'
        self.service = EncryptionService(str(self.key_file))

    def tearDown(self):
        """Clean up test environment"""
        shutil.rmtree(self.test_dir, ignore_errors=True)

    def test_unlock_with_password(self):
        """Test unlocking with password"""
        success = self.service.unlock("test_password_123")
        self.assertTrue(success)
        self.assertTrue(self.service.is_unlocked())

    def test_encrypt_decrypt_cycle(self):
        """Test encryption and decryption"""
        self.service.unlock("test_password_123")

        plaintext = "Sensitive information"
        ciphertext = self.service.encrypt(plaintext.encode())

        self.assertNotEqual(plaintext.encode(), ciphertext)
        self.assertGreater(len(ciphertext), len(plaintext))

        decrypted = self.service.decrypt(ciphertext)
        self.assertEqual(plaintext, decrypted.decode())

    def test_save_and_read_encrypted(self):
        """Test saving and reading encrypted files"""
        self.service.unlock("test_password_123")

        content = "Top secret data"
        self.service.save_encrypted("secret.txt", content)

        # File should exist (EncryptionService creates memory/private/)
        memory_dir = self.key_file.parent.parent  # Go up from .metadata
        encrypted_path = memory_dir / "private" / "secret.txt.enc"
        self.assertTrue(encrypted_path.exists())

        # Read back
        decrypted = self.service.read_encrypted("secret.txt")
        self.assertEqual(content, decrypted)

    def test_wrong_password_fails(self):
        """Test that wrong password fails"""
        self.service.unlock("correct_password")
        self.service.save_encrypted("data.txt", "secret")

        # Try with wrong password
        service2 = EncryptionService(str(self.key_file))
        service2.unlock("wrong_password")

        with self.assertRaises(Exception):
            service2.read_encrypted("data.txt")

    def test_session_persistence(self):
        """Test that unlock persists in session"""
        self.service.unlock("test_password")

        self.service.save_encrypted("file1.txt", "data1")
        self.service.save_encrypted("file2.txt", "data2")

        # Should work without unlocking again
        content1 = self.service.read_encrypted("file1.txt")
        content2 = self.service.read_encrypted("file2.txt")

        self.assertEqual(content1, "data1")
        self.assertEqual(content2, "data2")


class TestSharingService(unittest.TestCase):
    """Test SharingService (Tier 2)"""

    def setUp(self):
        """Set up test environment"""
        self.test_dir = Path(tempfile.mkdtemp())
        # Create memory directory
        memory_dir = self.test_dir / 'memory'
        memory_dir.mkdir()
        self.service = SharingService(str(memory_dir))
        self.owner = "owner@localhost"
        self.user = "user@example.com"

    def tearDown(self):
        """Clean up test environment"""
        shutil.rmtree(self.test_dir, ignore_errors=True)

    def test_grant_access(self):
        """Test granting access"""
        success = self.service.grant_access(
            "doc.txt", self.owner, self.user, SharePermission.READ
        )
        self.assertTrue(success)

        has_access = self.service.check_access("doc.txt", self.user, SharePermission.READ)
        self.assertTrue(has_access)

    def test_permission_levels(self):
        """Test different permission levels"""
        self.service.grant_access("doc.txt", self.owner, self.user, SharePermission.READ)

        # READ granted
        self.assertTrue(self.service.check_access("doc.txt", self.user, SharePermission.READ))

        # EDIT not granted
        self.assertFalse(self.service.check_access("doc.txt", self.user, SharePermission.EDIT))

    def test_revoke_access(self):
        """Test revoking access"""
        self.service.grant_access("doc.txt", self.owner, self.user, SharePermission.READ)

        success = self.service.revoke_access("doc.txt", self.owner, self.user)
        self.assertTrue(success)

        has_access = self.service.check_access("doc.txt", self.user, SharePermission.READ)
        self.assertFalse(has_access)

    def test_time_limited_access(self):
        """Test time-limited sharing"""
        # Grant access for 1 second
        expiry = datetime.now() + timedelta(seconds=1)
        self.service.grant_access(
            "doc.txt", self.owner, self.user, SharePermission.READ, expiry
        )

        # Should have access now
        self.assertTrue(self.service.check_access("doc.txt", self.user, SharePermission.READ))

        # Wait for expiry
        time.sleep(1.1)

        # Should not have access after expiry
        self.assertFalse(self.service.check_access("doc.txt", self.user, SharePermission.READ))

    def test_access_logging(self):
        """Test access log recording"""
        self.service.grant_access("doc.txt", self.owner, self.user, SharePermission.READ)
        self.service.check_access("doc.txt", self.user, SharePermission.READ)

        logs = self.service.get_access_logs("doc.txt")
        self.assertGreater(len(logs), 0)
        self.assertEqual(logs[0]['user'], self.user)
class TestCommunityService(unittest.TestCase):
    """Test CommunityService (Tier 3)"""

    def setUp(self):
        """Set up test environment"""
        self.test_dir = Path(tempfile.mkdtemp())
        # Create memory directory
        memory_dir = self.test_dir / 'memory'
        memory_dir.mkdir()
        self.service = CommunityService(str(memory_dir))
        self.founder = "founder@localhost"
        self.member = "member@example.com"

    def tearDown(self):
        """Clean up test environment"""
        shutil.rmtree(self.test_dir, ignore_errors=True)

    def test_create_group(self):
        """Test group creation"""
        success = self.service.create_group(
            "test-group", self.founder, "Test group"
        )
        self.assertTrue(success)

        info = self.service.get_group_info("test-group")
        self.assertEqual(info['founder'], self.founder)

    def test_join_group(self):
        """Test joining a group"""
        self.service.create_group("test-group", self.founder, "")

        success = self.service.join_group("test-group", self.member)
        self.assertTrue(success)

        info = self.service.get_group_info("test-group")
        self.assertIn(self.member, info['members'])

    def test_add_contribution(self):
        """Test adding contributions"""
        self.service.create_group("test-group", self.founder, "")

        success = self.service.add_contribution(
            "test-group", self.founder, "Test Knowledge",
            "Content here", "knowledge"
        )
        self.assertTrue(success)

        items = self.service.browse_group_knowledge("test-group", "knowledge")
        self.assertEqual(len(items), 1)

    def test_reputation_system(self):
        """Test reputation tracking"""
        self.service.create_group("test-group", self.founder, "")
        self.service.join_group("test-group", self.member)

        # Add contribution (earns 10 points)
        self.service.add_contribution(
            "test-group", self.member, "Contribution",
            "Content", "knowledge"
        )

        rep = self.service.get_user_reputation(self.member)
        self.assertEqual(rep['total_points'], 10)
        self.assertEqual(rep['contributions'], 1)

    def test_role_permissions(self):
        """Test role-based permissions"""
        self.service.create_group("test-group", self.founder, "")
        self.service.join_group("test-group", self.member)

        # Founder can moderate
        can_moderate = self.service.check_permission(
            "test-group", self.founder, GroupRole.MODERATOR
        )
        self.assertTrue(can_moderate)

        # Regular member cannot moderate
        can_moderate = self.service.check_permission(
            "test-group", self.member, GroupRole.MODERATOR
        )
        self.assertFalse(can_moderate)


class TestCommandHandlers(unittest.TestCase):
    """Test command handlers"""

    def test_memory_command_help(self):
        """Test MEMORY command help"""
        handler = MemoryCommandHandler()
        result = handler.handle("HELP", [])
        self.assertIn("MEMORY", result)
        self.assertIn("STATUS", result)

    def test_private_command_help(self):
        """Test PRIVATE command help"""
        handler = PrivateCommandHandler()
        result = handler.handle("HELP", [])
        self.assertIn("PRIVATE", result)
        self.assertIn("UNLOCK", result)

    def test_shared_command_help(self):
        """Test SHARED command help"""
        handler = SharedCommandHandler()
        result = handler.handle("HELP", [])
        self.assertIn("SHARED", result)
        self.assertIn("GRANT", result)

    def test_community_command_help(self):
        """Test COMMUNITY command help"""
        handler = CommunityCommandHandler()
        result = handler.handle("HELP", [])
        self.assertIn("COMMUNITY", result)
        self.assertIn("CREATE", result)

    def test_knowledge_command_help(self):
        """Test KNOWLEDGE command help"""
        handler = KnowledgeCommandHandler()
        result = handler.handle("HELP", [])
        self.assertIn("KNOWLEDGE", result)
        self.assertIn("CONTRIBUTE", result)


class TestPerformance(unittest.TestCase):
    """Test performance benchmarks"""

    def setUp(self):
        """Set up test environment"""
        self.test_dir = Path(tempfile.mkdtemp())
        self.manager = MemoryManager(str(self.test_dir))

    def tearDown(self):
        """Clean up test environment"""
        shutil.rmtree(self.test_dir, ignore_errors=True)

    def test_search_performance(self):
        """Test that search completes in <100ms"""
        # Create 100 test files
        for i in range(100):
            path = self.manager.get_tier_path(MemoryTier.PUBLIC) / f"test{i}.txt"
            path.write_text(f"test content {i}")

        # Measure search time
        start = time.time()
        results = self.manager.search_all_tiers("test")
        elapsed = (time.time() - start) * 1000  # Convert to ms

        self.assertLess(elapsed, 100, f"Search took {elapsed:.2f}ms (should be <100ms)")
        self.assertGreater(len(results), 0)

    def test_encryption_performance(self):
        """Test encryption speed"""
        memory_dir = self.manager.get_tier_path(MemoryTier.PRIVATE).parent
        (memory_dir / '.metadata').mkdir(exist_ok=True)

        service = EncryptionService(str(memory_dir / '.metadata' / 'encryption.key'))
        service.unlock("test_password")

        # Test with 10KB of data
        data = "x" * 10240

        start = time.time()
        encrypted = service.encrypt(data.encode())
        encrypt_time = (time.time() - start) * 1000

        self.assertLess(encrypt_time, 50, f"Encryption took {encrypt_time:.2f}ms")

        start = time.time()
        decrypted = service.decrypt(encrypted)
        decrypt_time = (time.time() - start) * 1000

        self.assertLess(decrypt_time, 50, f"Decryption took {decrypt_time:.2f}ms")


class TestSecurity(unittest.TestCase):
    """Test security features"""

    def setUp(self):
        """Set up test environment"""
        self.test_dir = Path(tempfile.mkdtemp())

    def tearDown(self):
        """Clean up test environment"""
        shutil.rmtree(self.test_dir, ignore_errors=True)

    def test_private_file_permissions(self):
        """Test that private files have correct permissions (600)"""
        memory_dir = self.test_dir / 'memory'
        memory_dir.mkdir()
        (memory_dir / '.metadata').mkdir()

        service = EncryptionService(str(memory_dir / '.metadata' / 'encryption.key'))
        service.unlock("password")
        service.save_encrypted("secret.txt", "data")

        encrypted_path = memory_dir / "private" / "secret.txt.enc"
        mode = encrypted_path.stat().st_mode & 0o777

        # Should be 600 (owner read/write only)
        self.assertEqual(mode, 0o600)

    def test_unauthorized_access_blocked(self):
        """Test that unauthorized access is blocked"""
        memory_dir = self.test_dir / 'memory'
        memory_dir.mkdir()
        sharing = SharingService(str(memory_dir))

        # User without permission should not have access
        has_access = sharing.check_access(
            "doc.txt", "unauthorized@example.com", SharePermission.READ
        )
        self.assertFalse(has_access)

    def test_encryption_uniqueness(self):
        """Test that same plaintext encrypts differently each time"""
        memory_dir = self.test_dir / 'memory'
        memory_dir.mkdir()
        (memory_dir / '.metadata').mkdir()

        service = EncryptionService(str(memory_dir / '.metadata' / 'encryption.key'))
        service.unlock("password")

        plaintext = "same content"
        encrypted1 = service.encrypt(plaintext.encode())
        encrypted2 = service.encrypt(plaintext.encode())

        # Should be different due to unique nonces
        self.assertNotEqual(encrypted1, encrypted2)


class TestIntegration(unittest.TestCase):
    """Test cross-tier integration"""

    def setUp(self):
        """Set up test environment"""
        self.test_dir = Path(tempfile.mkdtemp())
        # Create memory directory
        memory_dir = self.test_dir / 'memory'
        memory_dir.mkdir()
        (memory_dir / '.metadata').mkdir()

        self.manager = MemoryManager(str(memory_dir))
        self.encryption = EncryptionService(str(memory_dir / '.metadata' / 'encryption.key'))
        self.sharing = SharingService(str(memory_dir))
        self.community = CommunityService(str(memory_dir))

    def tearDown(self):
        """Clean up test environment"""
        shutil.rmtree(self.test_dir, ignore_errors=True)

    def test_private_to_shared_workflow(self):
        """Test moving from private to shared tier"""
        # Create private content
        self.encryption.unlock("password")
        self.encryption.save_encrypted("document.txt", "Private content")

        # Share with another user
        self.sharing.grant_access(
            "document.txt", "owner@localhost",
            "friend@example.com", SharePermission.READ
        )

        # Verify access
        has_access = self.sharing.check_access(
            "document.txt", "friend@example.com", SharePermission.READ
        )
        self.assertTrue(has_access)

    def test_community_to_knowledge_workflow(self):
        """Test contributing from community to global knowledge"""
        # Create community group
        self.community.create_group("test-group", "founder@localhost", "")

        # Add contribution
        self.community.add_contribution(
            "test-group", "founder@localhost",
            "Test Knowledge", "Content", "knowledge"
        )

        # Verify contribution exists
        items = self.community.browse_group_knowledge("test-group", "knowledge")
        self.assertEqual(len(items), 1)


def run_tests():
    """Run all tests with detailed output"""
    print("\n" + "=" * 70)
    print(" uDOS v1.0.20 - 4-Tier Knowledge Bank Test Suite")
    print("=" * 70 + "\n")

    # Create test suite
    loader = unittest.TestLoader()
    suite = unittest.TestSuite()

    # Add all test classes
    test_classes = [
        TestMemoryManager,
        TestEncryptionService,
        TestSharingService,
        TestCommunityService,
        TestCommandHandlers,
        TestPerformance,
        TestSecurity,
        TestIntegration
    ]

    for test_class in test_classes:
        tests = loader.loadTestsFromTestCase(test_class)
        suite.addTests(tests)

    # Run tests
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)

    # Summary
    print("\n" + "=" * 70)
    print(" Test Summary")
    print("=" * 70)
    print(f"Tests run: {result.testsRun}")
    print(f"Successes: {result.testsRun - len(result.failures) - len(result.errors)}")
    print(f"Failures: {len(result.failures)}")
    print(f"Errors: {len(result.errors)}")
    print("=" * 70 + "\n")

    return result.wasSuccessful()


if __name__ == "__main__":
    success = run_tests()
    exit(0 if success else 1)
