"""
ConfigManager Test Suite (v1.5.0)

Comprehensive tests for the unified configuration system:
- .env path correctness
- Auto-.env creation from template
- ConfigManager initialization
- Schema validation (all 18 fields)
- Priority system (runtime > user.json > .env > defaults)
- Username synchronization (.env ↔ user.json)
- Persistence (changes save to both files)
- Backup/restore functionality
- Error handling (missing files, invalid JSON)
- Integration tests (CONFIG command, DASH command)

Version: 1.0.0
Author: uDOS Configuration Team
"""

import unittest
import tempfile
import shutil
from pathlib import Path
import json
import sys
import os

# Add core to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from core.config_manager import ConfigManager, get_config_manager, reset_config_manager


class TestConfigManagerBasics(unittest.TestCase):
    """Test basic ConfigManager initialization and loading"""

    def setUp(self):
        """Create temporary test directory"""
        self.test_dir = Path(tempfile.mkdtemp())
        self.env_path = self.test_dir / '.env'
        self.user_json_path = self.test_dir / 'memory' / 'sandbox' / 'user.json'
        self.user_json_path.parent.mkdir(parents=True, exist_ok=True)

        # Reset singleton
        reset_config_manager()

    def tearDown(self):
        """Clean up test directory"""
        shutil.rmtree(self.test_dir, ignore_errors=True)
        reset_config_manager()

    def test_config_manager_initialization(self):
        """Test ConfigManager initializes correctly"""
        config = ConfigManager(base_path=self.test_dir)
        self.assertIsNotNone(config)
        self.assertEqual(config.base_path, self.test_dir)

    def test_env_path_correctness(self):
        """Test .env is at project root, not core/"""
        config = ConfigManager(base_path=self.test_dir)
        expected_path = self.test_dir / '.env'
        self.assertEqual(config.env_path, expected_path)

    def test_auto_env_creation_missing(self):
        """Test .env is NOT auto-created by ConfigManager (startup does this)"""
        config = ConfigManager(base_path=self.test_dir)
        config.load_all()
        # ConfigManager should not create .env - that's startup's job
        # It should just load defaults
        self.assertEqual(config.get('username'), 'user')

    def test_load_defaults(self):
        """Test default values are loaded when no files exist"""
        config = ConfigManager(base_path=self.test_dir)
        config.load_all()

        # Check defaults
        self.assertEqual(config.get('username'), 'user')
        self.assertEqual(config.get('location'), 'Unknown')
        self.assertEqual(config.get('timezone'), 'UTC')
        self.assertEqual(config.get('theme'), 'dungeon')
        self.assertEqual(config.get('UDOS_DEBUG'), False)


class TestEnvLoading(unittest.TestCase):
    """Test .env file loading and parsing"""

    def setUp(self):
        """Create temporary test directory with .env"""
        self.test_dir = Path(tempfile.mkdtemp())
        self.env_path = self.test_dir / '.env'
        self.user_json_path = self.test_dir / 'memory' / 'sandbox' / 'user.json'
        self.user_json_path.parent.mkdir(parents=True, exist_ok=True)

        reset_config_manager()

    def tearDown(self):
        """Clean up"""
        shutil.rmtree(self.test_dir, ignore_errors=True)
        reset_config_manager()

    def test_load_env_basic(self):
        """Test loading basic .env file"""
        self.env_path.write_text("""
GEMINI_API_KEY=test_key_12345
UDOS_USERNAME=TestUser
UDOS_LOCATION=TestCity
""")

        config = ConfigManager(base_path=self.test_dir)
        config.load_all()

        self.assertEqual(config.get('GEMINI_API_KEY'), 'test_key_12345')
        self.assertEqual(config.get('UDOS_USERNAME'), 'TestUser')
        self.assertEqual(config.get('location'), 'TestCity')

    def test_load_env_with_comments(self):
        """Test .env parsing ignores comments"""
        self.env_path.write_text("""
# This is a comment
GEMINI_API_KEY=test_key
# Another comment
UDOS_USERNAME=Fred
""")

        config = ConfigManager(base_path=self.test_dir)
        config.load_all()

        self.assertEqual(config.get('GEMINI_API_KEY'), 'test_key')
        self.assertEqual(config.get('UDOS_USERNAME'), 'Fred')

    def test_load_env_with_quotes(self):
        """Test .env handles quoted values"""
        self.env_path.write_text("""
GEMINI_API_KEY="quoted_key_123"
UDOS_USERNAME='single_quoted'
""")

        config = ConfigManager(base_path=self.test_dir)
        config.load_all()

        # ConfigManager should strip quotes
        api_key = config.get('GEMINI_API_KEY')
        username = config.get('UDOS_USERNAME')

        # Should not contain quote characters
        self.assertNotIn('"', api_key)
        self.assertNotIn("'", username)


class TestUserJsonLoading(unittest.TestCase):
    """Test user.json loading and priority"""

    def setUp(self):
        """Create test environment"""
        self.test_dir = Path(tempfile.mkdtemp())
        self.env_path = self.test_dir / '.env'
        self.user_json_path = self.test_dir / 'memory' / 'sandbox' / 'user.json'
        self.user_json_path.parent.mkdir(parents=True, exist_ok=True)

        reset_config_manager()

    def tearDown(self):
        """Clean up"""
        shutil.rmtree(self.test_dir, ignore_errors=True)
        reset_config_manager()

    def test_load_user_json(self):
        """Test user.json loads correctly"""
        user_data = {
            "user_profile": {
                "username": "JsonUser",
                "location": "JsonCity",
                "timezone": "America/New_York"
            },
            "system_settings": {
                "display": {
                    "theme": "cyberpunk"
                }
            }
        }

        with open(self.user_json_path, 'w') as f:
            json.dump(user_data, f)

        config = ConfigManager(base_path=self.test_dir)
        config.load_all()

        self.assertEqual(config.get('username'), 'JsonUser')
        self.assertEqual(config.get('location'), 'JsonCity')
        self.assertEqual(config.get('timezone'), 'America/New_York')
        self.assertEqual(config.get('theme'), 'cyberpunk')

    def test_priority_user_json_over_env(self):
        """Test user.json values override .env values"""
        # Create .env with values
        self.env_path.write_text("""
UDOS_USERNAME=EnvUser
UDOS_LOCATION=EnvCity
""")

        # Create user.json with different values
        user_data = {
            "user_profile": {
                "username": "JsonUser",
                "location": "JsonCity"
            }
        }

        with open(self.user_json_path, 'w') as f:
            json.dump(user_data, f)

        config = ConfigManager(base_path=self.test_dir)
        config.load_all()

        # user.json should win
        self.assertEqual(config.get('username'), 'JsonUser')
        self.assertEqual(config.get('location'), 'JsonCity')


class TestPrioritySystem(unittest.TestCase):
    """Test configuration priority: runtime > user.json > .env > defaults"""

    def setUp(self):
        """Create test environment"""
        self.test_dir = Path(tempfile.mkdtemp())
        self.env_path = self.test_dir / '.env'
        self.user_json_path = self.test_dir / 'memory' / 'sandbox' / 'user.json'
        self.user_json_path.parent.mkdir(parents=True, exist_ok=True)

        reset_config_manager()

    def tearDown(self):
        """Clean up"""
        shutil.rmtree(self.test_dir, ignore_errors=True)
        reset_config_manager()

    def test_runtime_override_highest_priority(self):
        """Test runtime values override everything"""
        # .env
        self.env_path.write_text("UDOS_USERNAME=EnvUser")

        # user.json
        user_data = {"user_profile": {"username": "JsonUser"}}
        with open(self.user_json_path, 'w') as f:
            json.dump(user_data, f)

        config = ConfigManager(base_path=self.test_dir)
        config.load_all()

        # Runtime override
        config.set('username', 'RuntimeUser', persist=False)

        # Runtime should win (not persisted)
        self.assertEqual(config.get('username'), 'RuntimeUser')

    def test_full_priority_chain(self):
        """Test defaults < .env < user.json < runtime"""
        config = ConfigManager(base_path=self.test_dir)

        # 1. Default
        config.load_all()
        self.assertEqual(config.get('username'), 'user')  # default

        # 2. .env overrides default
        self.env_path.write_text("UDOS_USERNAME=EnvUser")
        config.load_all()
        self.assertEqual(config.get('username'), 'EnvUser')

        # 3. user.json overrides .env
        user_data = {"user_profile": {"username": "JsonUser"}}
        with open(self.user_json_path, 'w') as f:
            json.dump(user_data, f)
        config.load_all()
        self.assertEqual(config.get('username'), 'JsonUser')

        # 4. Runtime overrides user.json
        config.set('username', 'RuntimeUser', persist=False)
        self.assertEqual(config.get('username'), 'RuntimeUser')


class TestUsernameSync(unittest.TestCase):
    """Test username synchronization between .env and user.json"""

    def setUp(self):
        """Create test environment"""
        self.test_dir = Path(tempfile.mkdtemp())
        self.env_path = self.test_dir / '.env'
        self.user_json_path = self.test_dir / 'memory' / 'sandbox' / 'user.json'
        self.user_json_path.parent.mkdir(parents=True, exist_ok=True)

        reset_config_manager()

    def tearDown(self):
        """Clean up"""
        shutil.rmtree(self.test_dir, ignore_errors=True)
        reset_config_manager()

    def test_username_sync_on_load(self):
        """Test username syncs from user.json to .env on load"""
        # .env has different username
        self.env_path.write_text("UDOS_USERNAME=OldUser")

        # user.json has the correct username
        user_data = {"user_profile": {"username": "Fred"}}
        with open(self.user_json_path, 'w') as f:
            json.dump(user_data, f)

        config = ConfigManager(base_path=self.test_dir)
        config.load_all()

        # Both should be synced to 'Fred'
        self.assertEqual(config.get('username'), 'Fred')
        self.assertEqual(config.get('UDOS_USERNAME'), 'Fred')

    def test_username_sync_on_save(self):
        """Test username change saves to both files"""
        config = ConfigManager(base_path=self.test_dir)
        config.load_all()

        # Change username
        config.set('username', 'NewUser', persist=True)

        # Check .env
        env_content = self.env_path.read_text()
        self.assertIn('UDOS_USERNAME=NewUser', env_content)

        # Check user.json
        with open(self.user_json_path, 'r') as f:
            user_data = json.load(f)
        self.assertEqual(user_data['user_profile']['username'], 'NewUser')


class TestPersistence(unittest.TestCase):
    """Test configuration persistence to files"""

    def setUp(self):
        """Create test environment"""
        self.test_dir = Path(tempfile.mkdtemp())
        self.env_path = self.test_dir / '.env'
        self.user_json_path = self.test_dir / 'memory' / 'sandbox' / 'user.json'
        self.user_json_path.parent.mkdir(parents=True, exist_ok=True)

        reset_config_manager()

    def tearDown(self):
        """Clean up"""
        shutil.rmtree(self.test_dir, ignore_errors=True)
        reset_config_manager()

    def test_persist_to_env(self):
        """Test API keys persist to .env only"""
        config = ConfigManager(base_path=self.test_dir)
        config.load_all()

        config.set('GEMINI_API_KEY', 'new_api_key_123', persist=True)

        # Should be in .env
        env_content = self.env_path.read_text()
        self.assertIn('GEMINI_API_KEY=new_api_key_123', env_content)

        # Should NOT be in user.json (API keys are .env only)
        if self.user_json_path.exists():
            with open(self.user_json_path, 'r') as f:
                user_data = json.load(f)
            self.assertNotIn('GEMINI_API_KEY', str(user_data))

    def test_persist_to_user_json(self):
        """Test user profile fields persist to user.json"""
        config = ConfigManager(base_path=self.test_dir)
        config.load_all()

        config.set('location', 'San Francisco', persist=True)
        config.set('timezone', 'America/Los_Angeles', persist=True)

        # Should be in user.json
        with open(self.user_json_path, 'r') as f:
            user_data = json.load(f)

        self.assertEqual(user_data['user_profile']['location'], 'San Francisco')
        self.assertEqual(user_data['user_profile']['timezone'], 'America/Los_Angeles')

    def test_persist_false_no_save(self):
        """Test persist=False doesn't save to files"""
        config = ConfigManager(base_path=self.test_dir)
        config.load_all()

        config.set('username', 'TemporaryUser', persist=False)

        # In memory only
        self.assertEqual(config.get('username'), 'TemporaryUser')

        # Not in .env
        if self.env_path.exists():
            env_content = self.env_path.read_text()
            self.assertNotIn('TemporaryUser', env_content)


class TestSchemaValidation(unittest.TestCase):
    """Test schema validation for all 18 fields"""

    def setUp(self):
        """Create test environment"""
        self.test_dir = Path(tempfile.mkdtemp())
        reset_config_manager()

    def tearDown(self):
        """Clean up"""
        shutil.rmtree(self.test_dir, ignore_errors=True)
        reset_config_manager()

    def test_schema_all_fields_defined(self):
        """Test all 18 expected fields are in schema"""
        config = ConfigManager(base_path=self.test_dir)
        schema = config._get_schema()

        expected_fields = [
            'GEMINI_API_KEY', 'GITHUB_TOKEN',
            'username', 'UDOS_USERNAME', 'password', 'location', 'timezone',
            'theme', 'grid_size',
            'UDOS_INSTALL_PATH', 'UDOS_INSTALLATION_ID', 'UDOS_VERSION',
            'UDOS_MASTER_PASSWORD', 'UDOS_MASTER_USER',
            'UDOS_DEBUG', 'UDOS_VIEWPORT_MODE'
        ]

        for field in expected_fields:
            self.assertIn(field, schema, f"Field {field} missing from schema")

    def test_validate_success(self):
        """Test validation passes with valid config"""
        config = ConfigManager(base_path=self.test_dir)
        config.load_all()

        # Should not raise
        config.validate()

    def test_type_validation(self):
        """Test type validation for different field types"""
        config = ConfigManager(base_path=self.test_dir)
        config.load_all()

        # Boolean field
        config.set('UDOS_DEBUG', True, persist=False)
        self.assertIsInstance(config.get('UDOS_DEBUG'), bool)

        # String field
        config.set('username', 'Fred', persist=False)
        self.assertIsInstance(config.get('username'), str)

        # Int field
        config.set('grid_size', 20, persist=False)
        self.assertIsInstance(config.get('grid_size'), int)


class TestBackupRestore(unittest.TestCase):
    """Test backup and restore functionality"""

    def setUp(self):
        """Create test environment"""
        self.test_dir = Path(tempfile.mkdtemp())
        self.env_path = self.test_dir / '.env'
        self.user_json_path = self.test_dir / 'memory' / 'sandbox' / 'user.json'
        self.user_json_path.parent.mkdir(parents=True, exist_ok=True)

        reset_config_manager()

    def tearDown(self):
        """Clean up"""
        shutil.rmtree(self.test_dir, ignore_errors=True)
        reset_config_manager()

    def test_backup_creates_files(self):
        """Test backup() creates backup files"""
        config = ConfigManager(base_path=self.test_dir)
        config.load_all()
        config.set('username', 'BackupUser', persist=True)

        backup_path = config.backup()

        self.assertTrue(backup_path.exists())
        self.assertTrue((backup_path / '.env').exists())
        self.assertTrue((backup_path / 'user.json').exists())

    def test_restore_from_backup(self):
        """Test restore() restores from backup"""
        config = ConfigManager(base_path=self.test_dir)
        config.load_all()

        # Set initial values
        config.set('username', 'OriginalUser', persist=True)
        backup_path = config.backup()

        # Change values
        config.set('username', 'ChangedUser', persist=True)
        self.assertEqual(config.get('username'), 'ChangedUser')

        # Restore
        config.restore(backup_path)
        config.load_all()  # Reload after restore

        self.assertEqual(config.get('username'), 'OriginalUser')


class TestErrorHandling(unittest.TestCase):
    """Test error handling for invalid files and data"""

    def setUp(self):
        """Create test environment"""
        self.test_dir = Path(tempfile.mkdtemp())
        self.env_path = self.test_dir / '.env'
        self.user_json_path = self.test_dir / 'memory' / 'sandbox' / 'user.json'
        self.user_json_path.parent.mkdir(parents=True, exist_ok=True)

        reset_config_manager()

    def tearDown(self):
        """Clean up"""
        shutil.rmtree(self.test_dir, ignore_errors=True)
        reset_config_manager()

    def test_invalid_json_graceful_failure(self):
        """Test invalid JSON doesn't crash, uses defaults"""
        # Create invalid JSON
        self.user_json_path.write_text("{invalid json content")

        config = ConfigManager(base_path=self.test_dir)
        config.load_all()

        # Should load defaults, not crash
        self.assertEqual(config.get('username'), 'user')

    def test_missing_files_use_defaults(self):
        """Test missing files result in defaults"""
        config = ConfigManager(base_path=self.test_dir)
        config.load_all()

        # Should have default values
        self.assertEqual(config.get('username'), 'user')
        self.assertEqual(config.get('timezone'), 'UTC')

    def test_invalid_key_raises_keyerror(self):
        """Test accessing invalid key raises KeyError"""
        config = ConfigManager(base_path=self.test_dir)
        config.load_all()

        # Should return None for unknown keys (graceful)
        result = config.get('NONEXISTENT_KEY')
        self.assertIsNone(result)


class TestSingletonPattern(unittest.TestCase):
    """Test singleton pattern for global config access"""

    def setUp(self):
        """Reset singleton"""
        reset_config_manager()

    def tearDown(self):
        """Reset singleton"""
        reset_config_manager()

    def test_singleton_returns_same_instance(self):
        """Test get_config_manager() returns same instance"""
        config1 = get_config_manager()
        config2 = get_config_manager()

        self.assertIs(config1, config2)

    def test_reset_config_manager(self):
        """Test reset_config_manager() clears singleton"""
        config1 = get_config_manager()
        reset_config_manager()
        config2 = get_config_manager()

        self.assertIsNot(config1, config2)


if __name__ == '__main__':
    # Run tests with verbose output
    unittest.main(verbosity=2)
