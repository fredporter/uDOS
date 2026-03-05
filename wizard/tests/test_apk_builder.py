"""
Tests for APK package builder.

Alpine APK packages are the standard package format for uDOS,
using the current Alpine core plugin contract.
"""

import pytest
from pathlib import Path
from unittest.mock import Mock, patch, MagicMock

# Add wizard to path
import sys

sys.path.insert(0, str(Path(__file__).parent.parent))

from wizard.services.plugin_factory import APKBuilder, BuildResult


class TestAPKBuilder:
    """Test APK builder class."""

    def test_apk_builder_initialization(self):
        """APKBuilder should initialize with paths."""
        builder = APKBuilder()
        assert builder.containers_path is not None
        assert builder.build_temp is not None
        assert builder.repo_path is not None

    def test_apk_builder_with_logger(self):
        """APKBuilder should accept optional logger."""
        mock_logger = Mock()
        builder = APKBuilder(logger=mock_logger)
        assert builder.logger is mock_logger

    def test_build_apk_missing_container(self):
        """build_apk should return error for missing container."""
        builder = APKBuilder()
        result = builder.build_apk(
            "nonexistent-plugin", container_path=Path("/nonexistent/path")
        )

        assert not result.success
        assert "not found" in result.error.lower()
        assert result.plugin_id == "nonexistent-plugin"

    def test_build_apk_placeholder_implementation(self):
        """build_apk should return not-implemented error (placeholder)."""
        builder = APKBuilder()

        # Create temporary container path
        with patch("pathlib.Path.exists", return_value=True):
            result = builder.build_apk("test-plugin")

            assert not result.success
            assert "not yet implemented" in result.error.lower()
            assert result.build_time_seconds > 0

    def test_build_apk_architecture_support(self):
        """build_apk should accept Alpine architectures."""
        builder = APKBuilder()
        arches = ["x86_64", "aarch64", "armv7", "ppc64le", "s390x"]

        for arch in arches:
            # Just verify it doesn't crash on arch parameter
            with patch("pathlib.Path.exists", return_value=True):
                result = builder.build_apk("test-plugin", arch=arch)
                # Expected to fail with placeholder, but should handle arch
                assert result.plugin_id == "test-plugin"

    def test_verify_apk_not_implemented(self):
        """verify_apk should return not-implemented."""
        builder = APKBuilder()
        valid, msg = builder.verify_apk(Path("/test/package.apk"))

        assert not valid
        assert "not yet implemented" in msg.lower()

    def test_generate_apkindex_not_implemented(self):
        """generate_apkindex should return not-implemented."""
        builder = APKBuilder()
        success, msg = builder.generate_apkindex()

        assert not success
        assert "not yet implemented" in msg.lower()

    def test_generate_apkindex_custom_path(self):
        """generate_apkindex should accept custom repo path."""
        builder = APKBuilder()
        custom_path = Path("/custom/repo")

        success, msg = builder.generate_apkindex(repo_path=custom_path)
        # Should still return not-implemented, but should accept the path
        assert not success


class TestBuildResult:
    """Test BuildResult data class."""

    def test_build_result_success(self):
        """BuildResult should represent successful builds."""
        from pathlib import Path

        result = BuildResult(
            success=True,
            plugin_id="test-plugin",
            package_path=Path("/tmp/test-plugin-1.0.apk"),
            manifest=Mock(),
            build_time_seconds=5.5,
        )

        assert result.success
        assert result.plugin_id == "test-plugin"
        assert result.build_time_seconds == 5.5

    def test_build_result_failure(self):
        """BuildResult should represent failed builds."""
        result = BuildResult(
            success=False,
            plugin_id="test-plugin",
            error="Build failed",
            build_time_seconds=2.0,
        )

        assert not result.success
        assert result.error == "Build failed"
        assert result.package_path is None
        assert result.manifest is None


class TestAPKBuilderIntegration:
    """Integration tests for APK builder with PluginFactory."""

    def test_apk_builder_available_in_factory(self):
        """APKBuilder should be importable from plugin_factory."""
        from wizard.services.plugin_factory import APKBuilder as FactoryAPKBuilder

        builder = FactoryAPKBuilder()
        assert builder is not None


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
