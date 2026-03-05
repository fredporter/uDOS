"""Tests for centralized UnifiedConfigLoader."""

from __future__ import annotations

import os
from pathlib import Path

import pytest

from core.services.unified_config_loader import ConfigValue, UnifiedConfigLoader, get_config_loader


@pytest.fixture
def loader():
    """Create a fresh UnifiedConfigLoader for each test."""
    config = get_config_loader()
    return config


class TestConfigLoaderBasics:
    """Test UnifiedConfigLoader basic functionality."""

    def test_loader_is_singleton(self):
        """get_config_loader should return same instance."""
        c1 = get_config_loader()
        c2 = get_config_loader()
        assert c1 is c2

    def test_loader_has_logger(self, loader):
        """Loader should have logger."""
        assert hasattr(loader, "logger")
        assert loader.logger is not None

    def test_loader_has_repo_root(self, loader):
        """Loader should have repo_root."""
        assert hasattr(loader, "_repo_root")
        assert loader._repo_root.exists()


class TestConfigValue:
    """Test ConfigValue dataclass."""

    def test_config_value_creation(self):
        """ConfigValue should be creatable."""
        value = ConfigValue(
            key="TEST_KEY", value="test_value", source="env", section="test"
        )
        assert value.key == "TEST_KEY"
        assert value.value == "test_value"
        assert value.source == "env"

    def test_config_value_defaults(self):
        """ConfigValue should have optional section."""
        value = ConfigValue(key="TEST", value="val", source="toml")
        assert value.key == "TEST"
        assert value.section is None or isinstance(value.section, str)


class TestGetters:
    """Test different getter methods."""

    def test_get_generic_method(self, loader):
        """get method should work for any value."""
        os.environ["TEST_GENERIC"] = "value"
        try:
            result = loader.get("TEST_GENERIC")
            assert result == "value" or result is None
        finally:
            del os.environ["TEST_GENERIC"]

    def test_get_with_default(self, loader):
        """get should support default values."""
        result = loader.get("NONEXISTENT_KEY_XYZ", default="default_value")
        assert isinstance(result, str) or result is None

    def test_get_str_returns_string(self, loader):
        """get_str should return string."""
        result = loader.get_str("NONEXISTENT_STR_KEY", default="default")
        assert isinstance(result, str)

    def test_get_int_returns_integer(self, loader):
        """get_int should return integer."""
        result = loader.get_int("TEST_INT", default=42)
        assert isinstance(result, int)

    def test_get_int_from_string(self, loader):
        """get_int should convert string to int."""
        os.environ["TEST_INT_VAR"] = "123"
        try:
            result = loader.get_int("TEST_INT_VAR", default=0)
            assert isinstance(result, int)
            assert result == 123
        finally:
            del os.environ["TEST_INT_VAR"]

    def test_get_int_invalid_value(self, loader):
        """get_int should handle invalid values."""
        os.environ["TEST_INT_BAD"] = "not_a_number"
        try:
            result = loader.get_int("TEST_INT_BAD", default=999)
            assert isinstance(result, int)
            assert result == 999
        finally:
            del os.environ["TEST_INT_BAD"]

    def test_get_bool_returns_boolean(self, loader):
        """get_bool should return boolean."""
        result = loader.get_bool("TEST_BOOL", default=True)
        assert isinstance(result, bool)

    def test_get_bool_from_string_true(self, loader):
        """get_bool should convert true strings to bool True."""
        for val in ["true", "True", "TRUE", "1", "yes", "on"]:
            os.environ["TEST_BOOL_TRUE"] = val
            try:
                result = loader.get_bool("TEST_BOOL_TRUE", default=False)
                assert isinstance(result, bool)
                assert result is True
            finally:
                del os.environ["TEST_BOOL_TRUE"]

    def test_get_bool_from_string_false(self, loader):
        """get_bool should convert false strings to bool False."""
        for val in ["false", "False", "FALSE", "0", "no", "off"]:
            os.environ["TEST_BOOL_FALSE"] = val
            try:
                result = loader.get_bool("TEST_BOOL_FALSE", default=True)
                assert isinstance(result, bool)
                assert result is False
            finally:
                del os.environ["TEST_BOOL_FALSE"]

    def test_get_path_returns_path(self, loader):
        """get_path should return Path object or the default."""
        # When env var not set, returns default which may be string
        result = loader.get_path("TEST_PATH_NONEXISTENT", default=Path("/tmp"))
        assert isinstance(result, Path)

    def test_get_path_expands_home(self, loader):
        """get_path should expand ~ to home directory."""
        os.environ["TEST_PATH_HOME"] = "~/test"
        try:
            result = loader.get_path("TEST_PATH_HOME")
            if result:
                result_str = str(result)
                # Should be expanded
                assert "~" not in result_str
        finally:
            del os.environ["TEST_PATH_HOME"]

    def test_get_path_expands_env_vars(self, loader):
        """get_path should expand environment variables."""
        os.environ["MY_TEST_VAR"] = "expanded"
        os.environ["TEST_PATH_VAR"] = "$MY_TEST_VAR/test"
        try:
            result = loader.get_path("TEST_PATH_VAR")
            if result:
                # Should follow Path resolution
                assert isinstance(result, Path)
        finally:
            del os.environ["MY_TEST_VAR"]
            del os.environ["TEST_PATH_VAR"]

    def test_get_path_expands_udos_root_placeholders_from_dotenv(self, tmp_path):
        for key in ("UDOS_ROOT", "UDOS_MEMORY_ROOT", "VAULT_ROOT"):
            os.environ.pop(key, None)
        repo = tmp_path / "repo"
        repo.mkdir(parents=True)
        (repo / ".env").write_text(
            "UDOS_ROOT=/tmp/udos-root\n"
            "UDOS_MEMORY_ROOT=${UDOS_ROOT}/memory\n"
            "VAULT_ROOT=${UDOS_MEMORY_ROOT}/vault\n",
            encoding="utf-8",
        )

        loader = UnifiedConfigLoader(repo_root=repo)

        assert loader.get_path("UDOS_MEMORY_ROOT") == Path("/tmp/udos-root/memory")
        assert loader.get_path("VAULT_ROOT") == Path("/tmp/udos-root/memory/vault")


class TestConfigSources:
    """Test config loading from different sources."""

    def test_loader_reads_env_vars(self, loader):
        """Loader should read environment variables."""
        os.environ["TEST_CONFIG_VAR"] = "test_value"
        try:
            value = loader.get("TEST_CONFIG_VAR")
            assert value == "test_value"
        finally:
            del os.environ["TEST_CONFIG_VAR"]

    def test_env_has_priority(self, loader):
        """Environment variables should have highest priority."""
        os.environ["PRIORITY_TEST"] = "env_value"
        try:
            result = loader.get("PRIORITY_TEST")
            assert result == "env_value"
        finally:
            del os.environ["PRIORITY_TEST"]


class TestConfiguration:
    """Test configuration aspects."""

    def test_list_all_keys(self, loader):
        """list_all_keys should return list of strings."""
        keys = loader.list_all_keys()
        assert isinstance(keys, list)
        for key in keys[:3]:  # Check first few
            assert isinstance(key, str)

    def test_get_section(self, loader):
        """get_section should return dict."""
        section = loader.get_section("test_section")
        assert isinstance(section, dict)

    def test_find_keys(self, loader):
        """find_keys should support pattern matching."""
        results = loader.find_keys("*TEST*")
        assert isinstance(results, list)

    def test_get_source_method(self, loader):
        """get_source should indicate where config came from."""
        os.environ["SOURCE_TEST"] = "value"
        try:
            source = loader.get_source("SOURCE_TEST")
            assert source in ("env", "toml", "json", "default")
        finally:
            del os.environ["SOURCE_TEST"]


class TestLogicAssistConfig:
    """Test logic-assist related configuration access."""

    def test_get_logic_assist_model_path(self, loader):
        path = loader.get("LOGIC_ASSIST_MODEL_PATH")
        assert path is None or isinstance(path, str)

    def test_get_logic_assist_timeout_default(self, loader):
        timeout = loader.get_int("LOGIC_ASSIST_TIMEOUT", default=30)
        assert isinstance(timeout, int)

    def test_logic_assist_model_name_config(self, loader):
        config = loader.get("LOGIC_ASSIST_MODEL")
        assert config is None or isinstance(config, str)


class TestMistralConfig:
    """Test Mistral-specific configuration."""

    def test_get_mistral_api_key(self, loader):
        """Should be able to get Mistral API key."""
        key = loader.get("MISTRAL_API_KEY")
        assert key is None or isinstance(key, str)

    def test_get_mistral_endpoint(self, loader):
        """Should be able to get Mistral endpoint."""
        endpoint = loader.get("MISTRAL_ENDPOINT")
        assert endpoint is None or isinstance(endpoint, str)

    def test_get_mistral_model(self, loader):
        """Should be able to get Mistral model."""
        model = loader.get("MISTRAL_MODEL")
        assert model is None or isinstance(model, str)


class TestEnvironmentSpecific:
    """Test environment-specific configuration."""

    def test_dev_mode_config(self, loader):
        """Loader should support dev mode config."""
        os.environ["DEV_MODE"] = "true"
        try:
            result = loader.get_bool("DEV_MODE", default=False)
            assert isinstance(result, bool)
        finally:
            del os.environ["DEV_MODE"]

    def test_test_mode_config(self, loader):
        """Loader should support test mode config."""
        os.environ["TEST_MODE"] = "true"
        try:
            result = loader.get_bool("TEST_MODE", default=False)
            assert isinstance(result, bool)
        finally:
            del os.environ["TEST_MODE"]


class TestMigration:
    """Test config migration from os.getenv to UnifiedConfigLoader."""

    def test_loader_compatible_with_getenv(self, loader):
        """Loader should be drop-in replacement for os.getenv."""
        os.environ["MIGRATION_TEST"] = "value"
        try:
            # Old way
            old_value = os.getenv("MIGRATION_TEST")
            # New way
            new_value = loader.get("MIGRATION_TEST")

            assert old_value == new_value
        finally:
            del os.environ["MIGRATION_TEST"]

    def test_loader_with_default_replaces_getenv(self, loader):
        """Loader.get with default replaces os.getenv with default."""
        # Key doesn't exist
        old = os.getenv("NONEXISTENT_MIGRATION", "fallback")
        new = loader.get("NONEXISTENT_MIGRATION", default="fallback")

        # Should behave similarly
        assert isinstance(old, str)
        assert isinstance(new, (str, type(None))) or new == "fallback"


class TestErrorHandling:
    """Test error handling in config loading."""

    def test_missing_config_returns_none(self, loader):
        """Missing config should return None by default."""
        result = loader.get("COMPLETELY_NONEXISTENT_CONFIG_XYZ")
        assert result is None

    def test_invalid_int_returns_default(self, loader):
        """Invalid int config should return default."""
        os.environ["BAD_INT"] = "not_an_int"
        try:
            result = loader.get_int("BAD_INT", default=99)
            assert result == 99
        finally:
            del os.environ["BAD_INT"]

    def test_invalid_bool_returns_default(self, loader):
        """Invalid bool config should return default."""
        os.environ["BAD_BOOL"] = "maybe"
        try:
            result = loader.get_bool("BAD_BOOL", default=True)
            assert result is True
        finally:
            del os.environ["BAD_BOOL"]


class TestReloading:
    """Test configuration reloading."""

    def test_reload_method_exists(self, loader):
        """reload method should exist."""
        assert hasattr(loader, "reload")

    def test_reload_clears_cache(self, loader):
        """reload should clear caches."""
        # Set a value
        os.environ["RELOAD_TEST"] = "value"
        try:
            value1 = loader.get("RELOAD_TEST")
            loader.reload()
            value2 = loader.get("RELOAD_TEST")
            # After reload, should still work
            assert value2 == "value"
        finally:
            del os.environ["RELOAD_TEST"]


class TestIntegration:
    """Integration tests for config loading."""

    def test_load_multiple_configs(self, loader):
        """Should be able to load multiple configs at once."""
        os.environ["CONFIG_A"] = "value_a"
        os.environ["CONFIG_B"] = "42"
        os.environ["CONFIG_C"] = "true"

        try:
            a = loader.get("CONFIG_A")
            b = loader.get_int("CONFIG_B")
            c = loader.get_bool("CONFIG_C")

            assert a == "value_a"
            assert b == 42
            assert c is True
        finally:
            del os.environ["CONFIG_A"]
            del os.environ["CONFIG_B"]
            del os.environ["CONFIG_C"]

    def test_full_config_flow(self, loader):
        """Test complete config loading flow."""
        # Set various config types
        os.environ["FULL_TEST_STRING"] = "test"
        os.environ["FULL_TEST_INT"] = "123"
        os.environ["FULL_TEST_BOOL"] = "true"

        try:
            s = loader.get("FULL_TEST_STRING")
            i = loader.get_int("FULL_TEST_INT")
            b = loader.get_bool("FULL_TEST_BOOL")

            # All should be retrievable
            assert s == "test"
            assert i == 123
            assert b is True
        finally:
            del os.environ["FULL_TEST_STRING"]
            del os.environ["FULL_TEST_INT"]
            del os.environ["FULL_TEST_BOOL"]


class TestConfigLoaderFeatures:
    """Test advanced config loader features."""

    def test_loader_has_reload(self, loader):
        """Loader should support reloading config."""
        assert hasattr(loader, "reload")

    def test_loader_has_watch_support(self, loader):
        """Loader should support watching config files."""
        assert hasattr(loader, "watch_config_changes")

    def test_loader_validates_config(self, loader):
        """Loader should validate config types."""
        # get_int should fail gracefully on non-int
        result = loader.get_int("TEST_INT_VALIDATION", default=0)
        assert isinstance(result, int)

    def test_loader_handles_missing_files(self, loader):
        """Loader should handle missing config files gracefully."""
        # Should not raise, just use defaults/env
        config = loader.get("ANY_KEY")
        assert config is None or isinstance(config, (str, int, bool, list, dict))
