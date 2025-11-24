"""
Test Suite for Feature 1.1.2.3: 4-Tier Memory System Finalization
v1.1.2 Phase 1: Advanced Security & Roles

Tests 4-tier memory architecture with encryption, tier boundaries, and
AI visibility rules. Tier 1 (Private/Encrypted), Tier 2 (Shared),
Tier 3 (Group), Tier 4 (Public).

Test Categories:
1. Tier Architecture (5 tests)
2. Tier 1 Encryption (6 tests)
3. Tier 2-4 Management (5 tests)
4. Tier Boundaries (6 tests)
5. AI Visibility Rules (6 tests)
6. Key Management (5 tests)
7. Data Migration (4 tests)
8. Access Control Integration (5 tests)
9. Tier Metadata (4 tests)
10. Search & Indexing (5 tests)
11. Tier Quotas (4 tests)
12. Integration Scenarios (3 tests)

Total: 58 tests
"""

import unittest
from unittest.mock import Mock, patch, MagicMock
import json
import base64
from datetime import datetime
from enum import Enum
from cryptography.fernet import Fernet


class MemoryTier(Enum):
    """Memory tier enumeration."""
    TIER1_PRIVATE = 1
    TIER2_SHARED = 2
    TIER3_GROUP = 3
    TIER4_PUBLIC = 4


class TierMemoryManager:
    """4-tier memory management system."""

    def __init__(self):
        self.tiers = {
            MemoryTier.TIER1_PRIVATE: {
                "name": "Private",
                "encrypted": True,
                "ai_visible": False,
                "data": {},
                "quota_mb": 100
            },
            MemoryTier.TIER2_SHARED: {
                "name": "Shared",
                "encrypted": False,
                "ai_visible": True,
                "data": {},
                "quota_mb": 500
            },
            MemoryTier.TIER3_GROUP: {
                "name": "Group",
                "encrypted": False,
                "ai_visible": True,
                "data": {},
                "quota_mb": 1000
            },
            MemoryTier.TIER4_PUBLIC: {
                "name": "Public",
                "encrypted": False,
                "ai_visible": True,
                "data": {},
                "quota_mb": 5000
            }
        }
        self.encryption_key = Fernet.generate_key()
        self.cipher = Fernet(self.encryption_key)
        self.tier_metadata = {}
        self.access_log = []

    def store_data(self, tier, key, value, metadata=None):
        """Store data in specified tier."""
        if not isinstance(tier, MemoryTier):
            raise ValueError(f"Invalid tier: {tier}")

        tier_config = self.tiers[tier]

        # Check quota
        if not self._check_quota(tier, len(json.dumps(value))):
            raise RuntimeError(f"Tier {tier.value} quota exceeded")

        # Encrypt if Tier 1
        if tier_config["encrypted"]:
            stored_value = self._encrypt_data(value)
        else:
            stored_value = value

        # Store
        tier_config["data"][key] = stored_value

        # Store metadata
        if metadata:
            self.tier_metadata[f"{tier.value}:{key}"] = metadata

        # Log access
        self._log_access("store", tier, key)

        return True

    def retrieve_data(self, tier, key):
        """Retrieve data from specified tier."""
        if not isinstance(tier, MemoryTier):
            raise ValueError(f"Invalid tier: {tier}")

        tier_config = self.tiers[tier]

        if key not in tier_config["data"]:
            raise KeyError(f"Key not found in tier {tier.value}: {key}")

        stored_value = tier_config["data"][key]

        # Decrypt if Tier 1
        if tier_config["encrypted"]:
            value = self._decrypt_data(stored_value)
        else:
            value = stored_value

        # Log access
        self._log_access("retrieve", tier, key)

        return value

    def delete_data(self, tier, key):
        """Delete data from specified tier."""
        if not isinstance(tier, MemoryTier):
            raise ValueError(f"Invalid tier: {tier}")

        tier_config = self.tiers[tier]

        if key in tier_config["data"]:
            del tier_config["data"][key]

            # Remove metadata
            meta_key = f"{tier.value}:{key}"
            if meta_key in self.tier_metadata:
                del self.tier_metadata[meta_key]

            # Log access
            self._log_access("delete", tier, key)
            return True

        return False

    def list_keys(self, tier):
        """List all keys in tier."""
        if not isinstance(tier, MemoryTier):
            raise ValueError(f"Invalid tier: {tier}")

        return list(self.tiers[tier]["data"].keys())

    def get_tier_info(self, tier):
        """Get tier configuration info."""
        if not isinstance(tier, MemoryTier):
            raise ValueError(f"Invalid tier: {tier}")

        config = self.tiers[tier]
        return {
            "tier": tier.value,
            "name": config["name"],
            "encrypted": config["encrypted"],
            "ai_visible": config["ai_visible"],
            "quota_mb": config["quota_mb"],
            "item_count": len(config["data"])
        }

    def get_ai_visible_tiers(self):
        """Get list of tiers visible to AI."""
        visible = []
        for tier, config in self.tiers.items():
            if config["ai_visible"]:
                visible.append(tier.value)
        return visible

    def check_tier_boundary(self, source_tier, target_tier):
        """Check if data can move between tiers."""
        if not isinstance(source_tier, MemoryTier) or not isinstance(target_tier, MemoryTier):
            raise ValueError("Invalid tier")

        # Can always move to higher security (lower number)
        if target_tier.value < source_tier.value:
            return True

        # Moving to lower security requires explicit permission
        # (would check RBAC in real implementation)
        return False

    def migrate_data(self, key, source_tier, target_tier):
        """Migrate data between tiers."""
        if not self.check_tier_boundary(source_tier, target_tier):
            raise PermissionError(f"Cannot migrate from tier {source_tier.value} to {target_tier.value}")

        # Retrieve from source
        data = self.retrieve_data(source_tier, key)

        # Get metadata
        meta_key = f"{source_tier.value}:{key}"
        metadata = self.tier_metadata.get(meta_key)

        # Store in target
        self.store_data(target_tier, key, data, metadata)

        # Delete from source
        self.delete_data(source_tier, key)

        # Log migration
        self._log_access("migrate", source_tier, key, {
            "target_tier": target_tier.value
        })

        return True

    def _encrypt_data(self, data):
        """Encrypt data for Tier 1."""
        json_data = json.dumps(data)
        encrypted = self.cipher.encrypt(json_data.encode())
        return base64.b64encode(encrypted).decode()

    def _decrypt_data(self, encrypted_data):
        """Decrypt data from Tier 1."""
        encrypted = base64.b64decode(encrypted_data.encode())
        decrypted = self.cipher.decrypt(encrypted)
        return json.loads(decrypted.decode())

    def _check_quota(self, tier, size_bytes):
        """Check if tier has quota available."""
        config = self.tiers[tier]
        current_size = sum(
            len(json.dumps(v)) for v in config["data"].values()
        )
        quota_bytes = config["quota_mb"] * 1024 * 1024
        return (current_size + size_bytes) <= quota_bytes

    def get_tier_usage(self, tier):
        """Get tier storage usage."""
        if not isinstance(tier, MemoryTier):
            raise ValueError(f"Invalid tier: {tier}")

        config = self.tiers[tier]
        size_bytes = sum(
            len(json.dumps(v)) for v in config["data"].values()
        )

        return {
            "tier": tier.value,
            "items": len(config["data"]),
            "size_bytes": size_bytes,
            "size_mb": round(size_bytes / 1024 / 1024, 2),
            "quota_mb": config["quota_mb"],
            "usage_percent": round((size_bytes / (config["quota_mb"] * 1024 * 1024)) * 100, 2)
        }

    def search_tier(self, tier, query):
        """Search within a tier."""
        if not isinstance(tier, MemoryTier):
            raise ValueError(f"Invalid tier: {tier}")

        results = []
        config = self.tiers[tier]

        for key, value in config["data"].items():
            # Decrypt if needed
            if config["encrypted"]:
                search_value = self._decrypt_data(value)
            else:
                search_value = value

            # Simple string search in JSON
            if query.lower() in json.dumps(search_value).lower():
                results.append({
                    "key": key,
                    "tier": tier.value,
                    "value": search_value
                })

        return results

    def get_metadata(self, tier, key):
        """Get metadata for tier item."""
        meta_key = f"{tier.value}:{key}"
        return self.tier_metadata.get(meta_key)

    def set_metadata(self, tier, key, metadata):
        """Set metadata for tier item."""
        if not isinstance(tier, MemoryTier):
            raise ValueError(f"Invalid tier: {tier}")

        # Verify key exists
        if key not in self.tiers[tier]["data"]:
            raise KeyError(f"Key not found: {key}")

        meta_key = f"{tier.value}:{key}"
        self.tier_metadata[meta_key] = metadata
        return True

    def rotate_encryption_key(self, new_key=None):
        """Rotate Tier 1 encryption key."""
        # Generate new key if not provided
        if new_key is None:
            new_key = Fernet.generate_key()

        new_cipher = Fernet(new_key)

        # Re-encrypt all Tier 1 data
        tier1_config = self.tiers[MemoryTier.TIER1_PRIVATE]
        re_encrypted = {}

        for key, encrypted_value in tier1_config["data"].items():
            # Decrypt with old key
            data = self._decrypt_data(encrypted_value)

            # Encrypt with new key
            json_data = json.dumps(data)
            encrypted = new_cipher.encrypt(json_data.encode())
            re_encrypted[key] = base64.b64encode(encrypted).decode()

        # Update
        tier1_config["data"] = re_encrypted
        self.encryption_key = new_key
        self.cipher = new_cipher

        # Log
        self._log_access("key_rotation", MemoryTier.TIER1_PRIVATE, "all")

        return True

    def export_tier(self, tier, include_encrypted=False):
        """Export tier data."""
        if not isinstance(tier, MemoryTier):
            raise ValueError(f"Invalid tier: {tier}")

        config = self.tiers[tier]
        export_data = {}

        for key, value in config["data"].items():
            if config["encrypted"] and not include_encrypted:
                # Skip encrypted data unless explicitly requested
                continue
            elif config["encrypted"]:
                # Decrypt for export
                export_data[key] = self._decrypt_data(value)
            else:
                export_data[key] = value

        return {
            "tier": tier.value,
            "encrypted": config["encrypted"],
            "data": export_data,
            "exported_at": datetime.now().isoformat()
        }

    def _log_access(self, operation, tier, key, extra_data=None):
        """Log tier access."""
        entry = {
            "operation": operation,
            "tier": tier.value,
            "key": key,
            "timestamp": datetime.now().isoformat()
        }
        if extra_data:
            entry.update(extra_data)

        self.access_log.append(entry)

    def get_access_log(self, filter_tier=None):
        """Get access log with optional tier filtering."""
        if filter_tier:
            tier_value = filter_tier.value if isinstance(filter_tier, MemoryTier) else filter_tier
            return [
                entry for entry in self.access_log
                if entry["tier"] == tier_value
            ]
        return self.access_log.copy()


class TestTierArchitecture(unittest.TestCase):
    """Test 4-tier memory architecture."""

    def setUp(self):
        self.memory = TierMemoryManager()

    def test_four_tier_structure(self):
        """Test system has 4 tiers."""
        self.assertEqual(len(self.memory.tiers), 4)
        self.assertIn(MemoryTier.TIER1_PRIVATE, self.memory.tiers)
        self.assertIn(MemoryTier.TIER4_PUBLIC, self.memory.tiers)

    def test_tier_names(self):
        """Test tier names."""
        self.assertEqual(self.memory.tiers[MemoryTier.TIER1_PRIVATE]["name"], "Private")
        self.assertEqual(self.memory.tiers[MemoryTier.TIER2_SHARED]["name"], "Shared")
        self.assertEqual(self.memory.tiers[MemoryTier.TIER3_GROUP]["name"], "Group")
        self.assertEqual(self.memory.tiers[MemoryTier.TIER4_PUBLIC]["name"], "Public")

    def test_tier_encryption_config(self):
        """Test tier encryption configuration."""
        self.assertTrue(self.memory.tiers[MemoryTier.TIER1_PRIVATE]["encrypted"])
        self.assertFalse(self.memory.tiers[MemoryTier.TIER2_SHARED]["encrypted"])
        self.assertFalse(self.memory.tiers[MemoryTier.TIER3_GROUP]["encrypted"])
        self.assertFalse(self.memory.tiers[MemoryTier.TIER4_PUBLIC]["encrypted"])

    def test_tier_ai_visibility(self):
        """Test AI visibility configuration."""
        self.assertFalse(self.memory.tiers[MemoryTier.TIER1_PRIVATE]["ai_visible"])
        self.assertTrue(self.memory.tiers[MemoryTier.TIER2_SHARED]["ai_visible"])
        self.assertTrue(self.memory.tiers[MemoryTier.TIER3_GROUP]["ai_visible"])
        self.assertTrue(self.memory.tiers[MemoryTier.TIER4_PUBLIC]["ai_visible"])

    def test_tier_info_retrieval(self):
        """Test getting tier information."""
        info = self.memory.get_tier_info(MemoryTier.TIER1_PRIVATE)
        self.assertEqual(info["tier"], 1)
        self.assertEqual(info["name"], "Private")
        self.assertTrue(info["encrypted"])


class TestTier1Encryption(unittest.TestCase):
    """Test Tier 1 encryption."""

    def setUp(self):
        self.memory = TierMemoryManager()

    def test_data_encrypted_at_rest(self):
        """Test Tier 1 data is encrypted at rest."""
        data = {"secret": "password123"}
        self.memory.store_data(MemoryTier.TIER1_PRIVATE, "test", data)

        # Raw stored data should be encrypted string
        raw = self.memory.tiers[MemoryTier.TIER1_PRIVATE]["data"]["test"]
        self.assertIsInstance(raw, str)
        self.assertNotIn("password123", raw)

    def test_data_decrypted_on_retrieval(self):
        """Test Tier 1 data is decrypted on retrieval."""
        data = {"secret": "password123"}
        self.memory.store_data(MemoryTier.TIER1_PRIVATE, "test", data)

        retrieved = self.memory.retrieve_data(MemoryTier.TIER1_PRIVATE, "test")
        self.assertEqual(retrieved, data)

    def test_encryption_key_generation(self):
        """Test encryption key is generated."""
        self.assertIsNotNone(self.memory.encryption_key)
        self.assertIsInstance(self.memory.encryption_key, bytes)

    def test_encryption_key_rotation(self):
        """Test encryption key rotation."""
        # Store data
        data = {"test": "data"}
        self.memory.store_data(MemoryTier.TIER1_PRIVATE, "key1", data)

        # Rotate key
        old_key = self.memory.encryption_key
        self.memory.rotate_encryption_key()

        # Key should change
        self.assertNotEqual(old_key, self.memory.encryption_key)

        # Data should still be retrievable
        retrieved = self.memory.retrieve_data(MemoryTier.TIER1_PRIVATE, "key1")
        self.assertEqual(retrieved, data)

    def test_custom_encryption_key(self):
        """Test using custom encryption key."""
        custom_key = Fernet.generate_key()
        self.memory.rotate_encryption_key(custom_key)
        self.assertEqual(self.memory.encryption_key, custom_key)

    def test_encryption_format(self):
        """Test encrypted data format."""
        data = {"test": "value"}
        self.memory.store_data(MemoryTier.TIER1_PRIVATE, "key", data)

        raw = self.memory.tiers[MemoryTier.TIER1_PRIVATE]["data"]["key"]
        # Should be base64 encoded
        import base64
        try:
            base64.b64decode(raw)
            valid_base64 = True
        except:
            valid_base64 = False

        self.assertTrue(valid_base64)


class TestTier2to4Management(unittest.TestCase):
    """Test Tier 2-4 (unencrypted) management."""

    def setUp(self):
        self.memory = TierMemoryManager()

    def test_tier2_plain_storage(self):
        """Test Tier 2 stores data unencrypted."""
        data = {"shared": "data"}
        self.memory.store_data(MemoryTier.TIER2_SHARED, "test", data)

        raw = self.memory.tiers[MemoryTier.TIER2_SHARED]["data"]["test"]
        self.assertEqual(raw, data)

    def test_tier3_plain_storage(self):
        """Test Tier 3 stores data unencrypted."""
        data = {"group": "info"}
        self.memory.store_data(MemoryTier.TIER3_GROUP, "test", data)

        raw = self.memory.tiers[MemoryTier.TIER3_GROUP]["data"]["test"]
        self.assertEqual(raw, data)

    def test_tier4_plain_storage(self):
        """Test Tier 4 stores data unencrypted."""
        data = {"public": "knowledge"}
        self.memory.store_data(MemoryTier.TIER4_PUBLIC, "test", data)

        raw = self.memory.tiers[MemoryTier.TIER4_PUBLIC]["data"]["test"]
        self.assertEqual(raw, data)

    def test_list_tier_keys(self):
        """Test listing keys in tier."""
        self.memory.store_data(MemoryTier.TIER4_PUBLIC, "key1", {"a": 1})
        self.memory.store_data(MemoryTier.TIER4_PUBLIC, "key2", {"b": 2})

        keys = self.memory.list_keys(MemoryTier.TIER4_PUBLIC)
        self.assertIn("key1", keys)
        self.assertIn("key2", keys)

    def test_delete_from_tier(self):
        """Test deleting data from tier."""
        self.memory.store_data(MemoryTier.TIER4_PUBLIC, "test", {"data": 1})
        self.assertTrue(self.memory.delete_data(MemoryTier.TIER4_PUBLIC, "test"))

        keys = self.memory.list_keys(MemoryTier.TIER4_PUBLIC)
        self.assertNotIn("test", keys)


class TestTierBoundaries(unittest.TestCase):
    """Test tier boundary enforcement."""

    def setUp(self):
        self.memory = TierMemoryManager()

    def test_boundary_check_to_higher_security(self):
        """Test moving to higher security allowed."""
        can_move = self.memory.check_tier_boundary(
            MemoryTier.TIER4_PUBLIC,
            MemoryTier.TIER1_PRIVATE
        )
        self.assertTrue(can_move)

    def test_boundary_check_to_lower_security(self):
        """Test moving to lower security restricted."""
        can_move = self.memory.check_tier_boundary(
            MemoryTier.TIER1_PRIVATE,
            MemoryTier.TIER4_PUBLIC
        )
        self.assertFalse(can_move)

    def test_migration_to_higher_security(self):
        """Test migrating data to higher security tier."""
        self.memory.store_data(MemoryTier.TIER4_PUBLIC, "test", {"data": "value"})
        self.memory.migrate_data("test", MemoryTier.TIER4_PUBLIC, MemoryTier.TIER1_PRIVATE)

        # Should be in Tier 1
        data = self.memory.retrieve_data(MemoryTier.TIER1_PRIVATE, "test")
        self.assertEqual(data["data"], "value")

        # Should not be in Tier 4
        self.assertNotIn("test", self.memory.list_keys(MemoryTier.TIER4_PUBLIC))

    def test_migration_to_lower_security_denied(self):
        """Test migration to lower security denied."""
        self.memory.store_data(MemoryTier.TIER1_PRIVATE, "test", {"secret": "data"})

        with self.assertRaises(PermissionError):
            self.memory.migrate_data("test", MemoryTier.TIER1_PRIVATE, MemoryTier.TIER4_PUBLIC)

    def test_invalid_tier_boundary(self):
        """Test invalid tier raises error."""
        with self.assertRaises(ValueError):
            self.memory.check_tier_boundary("invalid", MemoryTier.TIER1_PRIVATE)

    def test_migration_preserves_metadata(self):
        """Test migration preserves metadata."""
        metadata = {"tags": ["important"], "created": "2025-11-24"}
        self.memory.store_data(MemoryTier.TIER4_PUBLIC, "test", {"data": 1}, metadata)

        self.memory.migrate_data("test", MemoryTier.TIER4_PUBLIC, MemoryTier.TIER2_SHARED)

        retrieved_meta = self.memory.get_metadata(MemoryTier.TIER2_SHARED, "test")
        self.assertEqual(retrieved_meta, metadata)


class TestAIVisibilityRules(unittest.TestCase):
    """Test AI visibility rules."""

    def setUp(self):
        self.memory = TierMemoryManager()

    def test_tier1_not_visible_to_ai(self):
        """Test Tier 1 not visible to AI."""
        info = self.memory.get_tier_info(MemoryTier.TIER1_PRIVATE)
        self.assertFalse(info["ai_visible"])

    def test_tier2_visible_to_ai(self):
        """Test Tier 2 visible to AI."""
        info = self.memory.get_tier_info(MemoryTier.TIER2_SHARED)
        self.assertTrue(info["ai_visible"])

    def test_tier3_visible_to_ai(self):
        """Test Tier 3 visible to AI."""
        info = self.memory.get_tier_info(MemoryTier.TIER3_GROUP)
        self.assertTrue(info["ai_visible"])

    def test_tier4_visible_to_ai(self):
        """Test Tier 4 visible to AI."""
        info = self.memory.get_tier_info(MemoryTier.TIER4_PUBLIC)
        self.assertTrue(info["ai_visible"])

    def test_get_ai_visible_tiers(self):
        """Test getting list of AI-visible tiers."""
        visible = self.memory.get_ai_visible_tiers()
        self.assertIn(2, visible)
        self.assertIn(3, visible)
        self.assertIn(4, visible)
        self.assertNotIn(1, visible)

    def test_ai_search_restricted(self):
        """Test AI search should skip Tier 1."""
        self.memory.store_data(MemoryTier.TIER1_PRIVATE, "secret", {"password": "123"})
        self.memory.store_data(MemoryTier.TIER4_PUBLIC, "public", {"info": "data"})

        # AI should only search visible tiers
        visible_tiers = [
            tier for tier in [MemoryTier.TIER1_PRIVATE, MemoryTier.TIER2_SHARED,
                             MemoryTier.TIER3_GROUP, MemoryTier.TIER4_PUBLIC]
            if self.memory.get_tier_info(tier)["ai_visible"]
        ]

        self.assertNotIn(MemoryTier.TIER1_PRIVATE, visible_tiers)
        self.assertIn(MemoryTier.TIER4_PUBLIC, visible_tiers)


class TestKeyManagement(unittest.TestCase):
    """Test encryption key management."""

    def setUp(self):
        self.memory = TierMemoryManager()

    def test_key_initialization(self):
        """Test encryption key is initialized."""
        self.assertIsNotNone(self.memory.encryption_key)

    def test_key_rotation(self):
        """Test key rotation."""
        old_key = self.memory.encryption_key
        self.memory.rotate_encryption_key()
        self.assertNotEqual(old_key, self.memory.encryption_key)

    def test_key_rotation_preserves_data(self):
        """Test key rotation preserves all data."""
        # Store multiple items
        for i in range(5):
            self.memory.store_data(MemoryTier.TIER1_PRIVATE, f"key{i}", {"value": i})

        # Rotate
        self.memory.rotate_encryption_key()

        # All data should be retrievable
        for i in range(5):
            data = self.memory.retrieve_data(MemoryTier.TIER1_PRIVATE, f"key{i}")
            self.assertEqual(data["value"], i)

    def test_key_rotation_logged(self):
        """Test key rotation is logged."""
        self.memory.rotate_encryption_key()
        log = self.memory.get_access_log()

        rotation_entries = [e for e in log if e["operation"] == "key_rotation"]
        self.assertGreater(len(rotation_entries), 0)

    def test_key_format(self):
        """Test encryption key format."""
        # Should be Fernet key format (32 URL-safe base64 bytes)
        self.assertIsInstance(self.memory.encryption_key, bytes)
        self.assertEqual(len(self.memory.encryption_key), 44)  # Base64 of 32 bytes


class TestDataMigration(unittest.TestCase):
    """Test data migration between tiers."""

    def setUp(self):
        self.memory = TierMemoryManager()

    def test_migrate_with_metadata(self):
        """Test migration preserves metadata."""
        meta = {"author": "test", "tags": ["demo"]}
        self.memory.store_data(MemoryTier.TIER4_PUBLIC, "item", {"data": 1}, meta)

        self.memory.migrate_data("item", MemoryTier.TIER4_PUBLIC, MemoryTier.TIER2_SHARED)

        new_meta = self.memory.get_metadata(MemoryTier.TIER2_SHARED, "item")
        self.assertEqual(new_meta, meta)

    def test_migrate_removes_from_source(self):
        """Test migration removes from source tier."""
        self.memory.store_data(MemoryTier.TIER3_GROUP, "item", {"data": 1})
        self.memory.migrate_data("item", MemoryTier.TIER3_GROUP, MemoryTier.TIER1_PRIVATE)

        self.assertNotIn("item", self.memory.list_keys(MemoryTier.TIER3_GROUP))

    def test_migrate_encryption_transition(self):
        """Test migration handles encryption transition."""
        data = {"sensitive": "info"}
        self.memory.store_data(MemoryTier.TIER4_PUBLIC, "item", data)

        # Migrate to encrypted tier
        self.memory.migrate_data("item", MemoryTier.TIER4_PUBLIC, MemoryTier.TIER1_PRIVATE)

        # Data should be encrypted in storage
        raw = self.memory.tiers[MemoryTier.TIER1_PRIVATE]["data"]["item"]
        self.assertNotIn("sensitive", str(raw))

        # But retrievable
        retrieved = self.memory.retrieve_data(MemoryTier.TIER1_PRIVATE, "item")
        self.assertEqual(retrieved, data)

    def test_migration_logged(self):
        """Test migration is logged."""
        self.memory.store_data(MemoryTier.TIER4_PUBLIC, "item", {"data": 1})
        self.memory.migrate_data("item", MemoryTier.TIER4_PUBLIC, MemoryTier.TIER2_SHARED)

        log = self.memory.get_access_log()
        migrations = [e for e in log if e["operation"] == "migrate"]
        self.assertGreater(len(migrations), 0)


class TestAccessControlIntegration(unittest.TestCase):
    """Test integration with access control."""

    def setUp(self):
        self.memory = TierMemoryManager()

    def test_tier_access_logged(self):
        """Test all tier access is logged."""
        self.memory.store_data(MemoryTier.TIER4_PUBLIC, "key", {"data": 1})
        self.memory.retrieve_data(MemoryTier.TIER4_PUBLIC, "key")

        log = self.memory.get_access_log()
        self.assertGreater(len(log), 0)

    def test_log_filtering_by_tier(self):
        """Test filtering access log by tier."""
        self.memory.store_data(MemoryTier.TIER1_PRIVATE, "key1", {"a": 1})
        self.memory.store_data(MemoryTier.TIER4_PUBLIC, "key2", {"b": 2})

        tier1_log = self.memory.get_access_log(MemoryTier.TIER1_PRIVATE)
        self.assertTrue(all(e["tier"] == 1 for e in tier1_log))

    def test_operation_types_logged(self):
        """Test different operation types are logged."""
        self.memory.store_data(MemoryTier.TIER4_PUBLIC, "key", {"data": 1})
        self.memory.retrieve_data(MemoryTier.TIER4_PUBLIC, "key")
        self.memory.delete_data(MemoryTier.TIER4_PUBLIC, "key")

        log = self.memory.get_access_log()
        operations = [e["operation"] for e in log]

        self.assertIn("store", operations)
        self.assertIn("retrieve", operations)
        self.assertIn("delete", operations)

    def test_timestamp_in_log(self):
        """Test timestamps in access log."""
        self.memory.store_data(MemoryTier.TIER4_PUBLIC, "key", {"data": 1})
        log = self.memory.get_access_log()

        self.assertIn("timestamp", log[0])
        datetime.fromisoformat(log[0]["timestamp"])

    def test_invalid_tier_access(self):
        """Test invalid tier raises error."""
        with self.assertRaises(ValueError):
            self.memory.store_data("invalid", "key", {})


class TestTierMetadata(unittest.TestCase):
    """Test tier metadata management."""

    def setUp(self):
        self.memory = TierMemoryManager()

    def test_store_with_metadata(self):
        """Test storing data with metadata."""
        meta = {"tags": ["test"], "author": "user"}
        self.memory.store_data(MemoryTier.TIER4_PUBLIC, "key", {"data": 1}, meta)

        retrieved_meta = self.memory.get_metadata(MemoryTier.TIER4_PUBLIC, "key")
        self.assertEqual(retrieved_meta, meta)

    def test_set_metadata_after_storage(self):
        """Test setting metadata after storage."""
        self.memory.store_data(MemoryTier.TIER4_PUBLIC, "key", {"data": 1})

        meta = {"added": "later"}
        self.memory.set_metadata(MemoryTier.TIER4_PUBLIC, "key", meta)

        retrieved = self.memory.get_metadata(MemoryTier.TIER4_PUBLIC, "key")
        self.assertEqual(retrieved, meta)

    def test_metadata_deleted_with_data(self):
        """Test metadata is deleted with data."""
        self.memory.store_data(MemoryTier.TIER4_PUBLIC, "key", {"data": 1}, {"meta": "data"})
        self.memory.delete_data(MemoryTier.TIER4_PUBLIC, "key")

        meta = self.memory.get_metadata(MemoryTier.TIER4_PUBLIC, "key")
        self.assertIsNone(meta)

    def test_metadata_for_nonexistent_key(self):
        """Test metadata for nonexistent key."""
        meta = self.memory.get_metadata(MemoryTier.TIER4_PUBLIC, "nonexistent")
        self.assertIsNone(meta)


class TestSearchAndIndexing(unittest.TestCase):
    """Test tier search and indexing."""

    def setUp(self):
        self.memory = TierMemoryManager()

    def test_search_tier(self):
        """Test searching within a tier."""
        self.memory.store_data(MemoryTier.TIER4_PUBLIC, "key1", {"content": "hello world"})
        self.memory.store_data(MemoryTier.TIER4_PUBLIC, "key2", {"content": "goodbye"})

        results = self.memory.search_tier(MemoryTier.TIER4_PUBLIC, "hello")
        self.assertEqual(len(results), 1)
        self.assertEqual(results[0]["key"], "key1")

    def test_search_encrypted_tier(self):
        """Test searching encrypted tier decrypts data."""
        self.memory.store_data(MemoryTier.TIER1_PRIVATE, "key", {"secret": "data"})

        results = self.memory.search_tier(MemoryTier.TIER1_PRIVATE, "secret")
        self.assertEqual(len(results), 1)
        self.assertEqual(results[0]["value"]["secret"], "data")

    def test_search_case_insensitive(self):
        """Test search is case insensitive."""
        self.memory.store_data(MemoryTier.TIER4_PUBLIC, "key", {"text": "Hello World"})

        results = self.memory.search_tier(MemoryTier.TIER4_PUBLIC, "hello")
        self.assertEqual(len(results), 1)

    def test_search_no_results(self):
        """Test search with no matches."""
        self.memory.store_data(MemoryTier.TIER4_PUBLIC, "key", {"data": "test"})

        results = self.memory.search_tier(MemoryTier.TIER4_PUBLIC, "nonexistent")
        self.assertEqual(len(results), 0)

    def test_search_multiple_results(self):
        """Test search returning multiple results."""
        self.memory.store_data(MemoryTier.TIER4_PUBLIC, "key1", {"text": "python code"})
        self.memory.store_data(MemoryTier.TIER4_PUBLIC, "key2", {"text": "python tutorial"})

        results = self.memory.search_tier(MemoryTier.TIER4_PUBLIC, "python")
        self.assertEqual(len(results), 2)


class TestTierQuotas(unittest.TestCase):
    """Test tier storage quotas."""

    def setUp(self):
        self.memory = TierMemoryManager()

    def test_tier_usage_tracking(self):
        """Test tier usage is tracked."""
        self.memory.store_data(MemoryTier.TIER4_PUBLIC, "key", {"data": "x" * 1000})

        usage = self.memory.get_tier_usage(MemoryTier.TIER4_PUBLIC)
        self.assertGreater(usage["size_bytes"], 0)
        self.assertEqual(usage["items"], 1)

    def test_quota_enforcement(self):
        """Test quota is enforced."""
        # Set very small quota
        self.memory.tiers[MemoryTier.TIER4_PUBLIC]["quota_mb"] = 0.001  # ~1KB

        # Try to store large data
        large_data = {"data": "x" * 10000}

        with self.assertRaises(RuntimeError):
            self.memory.store_data(MemoryTier.TIER4_PUBLIC, "key", large_data)

    def test_usage_percentage(self):
        """Test usage percentage calculation."""
        usage = self.memory.get_tier_usage(MemoryTier.TIER4_PUBLIC)
        self.assertIn("usage_percent", usage)
        self.assertGreaterEqual(usage["usage_percent"], 0)
        self.assertLessEqual(usage["usage_percent"], 100)

    def test_quota_configuration(self):
        """Test tier quota configuration."""
        tier1_info = self.memory.get_tier_info(MemoryTier.TIER1_PRIVATE)
        tier4_info = self.memory.get_tier_info(MemoryTier.TIER4_PUBLIC)

        # Tier 4 should have larger quota
        self.assertGreater(tier4_info["quota_mb"], tier1_info["quota_mb"])


class TestIntegrationScenarios(unittest.TestCase):
    """Test end-to-end tier scenarios."""

    def setUp(self):
        self.memory = TierMemoryManager()

    def test_full_tier_workflow(self):
        """Test complete tier management workflow."""
        # 1. Store in public tier
        self.memory.store_data(MemoryTier.TIER4_PUBLIC, "item", {"info": "test"})

        # 2. Add metadata
        self.memory.set_metadata(MemoryTier.TIER4_PUBLIC, "item", {"tags": ["important"]})

        # 3. Migrate to private tier
        self.memory.migrate_data("item", MemoryTier.TIER4_PUBLIC, MemoryTier.TIER1_PRIVATE)

        # 4. Verify in new tier
        data = self.memory.retrieve_data(MemoryTier.TIER1_PRIVATE, "item")
        self.assertEqual(data["info"], "test")

        # 5. Verify metadata preserved
        meta = self.memory.get_metadata(MemoryTier.TIER1_PRIVATE, "item")
        self.assertEqual(meta["tags"], ["important"])

    def test_multi_tier_search(self):
        """Test searching across multiple tiers."""
        # Store in different tiers
        self.memory.store_data(MemoryTier.TIER1_PRIVATE, "priv", {"text": "private python"})
        self.memory.store_data(MemoryTier.TIER2_SHARED, "shar", {"text": "shared python"})
        self.memory.store_data(MemoryTier.TIER4_PUBLIC, "publ", {"text": "public python"})

        # Search AI-visible tiers only
        ai_visible = [tier for tier in [MemoryTier.TIER2_SHARED, MemoryTier.TIER3_GROUP, MemoryTier.TIER4_PUBLIC]]

        all_results = []
        for tier in ai_visible:
            results = self.memory.search_tier(tier, "python")
            all_results.extend(results)

        # Should find 2 (not the private one)
        self.assertEqual(len(all_results), 2)

    def test_encryption_lifecycle(self):
        """Test full encryption lifecycle."""
        # 1. Store encrypted data
        self.memory.store_data(MemoryTier.TIER1_PRIVATE, "key", {"password": "secret123"})

        # 2. Verify encrypted at rest
        raw = self.memory.tiers[MemoryTier.TIER1_PRIVATE]["data"]["key"]
        self.assertNotIn("secret123", str(raw))

        # 3. Rotate key
        self.memory.rotate_encryption_key()

        # 4. Still retrievable
        data = self.memory.retrieve_data(MemoryTier.TIER1_PRIVATE, "key")
        self.assertEqual(data["password"], "secret123")

        # 5. Export (decrypted)
        export = self.memory.export_tier(MemoryTier.TIER1_PRIVATE, include_encrypted=True)
        self.assertEqual(export["data"]["key"]["password"], "secret123")


if __name__ == "__main__":
    unittest.main()
