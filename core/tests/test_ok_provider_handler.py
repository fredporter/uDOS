"""Tests for centralized OKProviderHandler."""

from __future__ import annotations

import pytest

from core.services.ok_provider_handler import (
    OKProviderHandler,
    ProviderStatus,
    ProviderType,
    get_ok_provider_handler,
)


@pytest.fixture
def handler():
    """Create a fresh OKProviderHandler for each test."""
    h = get_ok_provider_handler()
    return h


class TestProviderType:
    """Test ProviderType enum."""

    def test_provider_type_has_local_gpt4all(self):
        """ProviderType should have a local GPT4All lane."""
        assert hasattr(ProviderType, "LOCAL_GPT4ALL")

    def test_provider_type_has_mistral(self):
        """ProviderType should have Mistral."""
        assert hasattr(ProviderType, "MISTRAL_CLOUD")

    def test_provider_type_values(self):
        """ProviderType should have string values."""
        assert isinstance(ProviderType.LOCAL_GPT4ALL.value, str)
        assert isinstance(ProviderType.MISTRAL_CLOUD.value, str)


class TestProviderStatus:
    """Test ProviderStatus dataclass."""

    def test_provider_status_creation(self):
        """ProviderStatus should be creatable."""
        status = ProviderStatus(
            provider_id="gpt4all",
            is_configured=True,
            is_running=True,
            is_available=True,
            loaded_models=["mistral-7b-instruct-v0.2.Q4_0.gguf"],
            default_model="mistral-7b-instruct-v0.2.Q4_0.gguf",
            issue=None,
        )
        assert status.provider_id == "gpt4all"
        assert status.is_available is True
        assert status.default_model == "mistral-7b-instruct-v0.2.Q4_0.gguf"

    def test_provider_status_with_issue(self):
        """ProviderStatus should support error state."""
        status = ProviderStatus(
            provider_id="mistral",
            is_configured=False,
            is_running=False,
            is_available=False,
            loaded_models=[],
            default_model=None,
            issue="API key not configured",
        )
        assert status.is_available is False
        assert status.issue == "API key not configured"


class TestOKProviderHandlerBasics:
    """Test OKProviderHandler basic functionality."""

    def test_handler_is_singleton(self):
        """get_ok_provider_handler should return same instance."""
        h1 = get_ok_provider_handler()
        h2 = get_ok_provider_handler()
        assert h1 is h2

    def test_handler_has_logger(self, handler):
        """Handler should have logger."""
        assert hasattr(handler, "logger")
        assert handler.logger is not None

    def test_handler_has_cache(self, handler):
        """Handler should have internal cache."""
        assert hasattr(handler, "_cache")
        assert isinstance(handler._cache, dict)


class TestLocalProviderDetection:
    """Test local GPT4All provider detection."""

    def test_check_local_provider_returns_status(self, handler):
        """check_local_provider should return ProviderStatus."""
        status = handler.check_local_provider()
        assert isinstance(status, ProviderStatus)

    def test_local_provider_status_has_provider_id(self, handler):
        """Local provider status should have provider ID."""
        status = handler.check_local_provider()
        assert status.provider_id == ProviderType.LOCAL_GPT4ALL.value

    def test_local_provider_has_availability(self, handler):
        """Local provider should indicate availability."""
        status = handler.check_local_provider()
        assert isinstance(status.is_available, bool)

    def test_local_provider_has_configured_flag(self, handler):
        """Local provider status should have configured flag."""
        status = handler.check_local_provider()
        assert isinstance(status.is_configured, bool)

    def test_local_provider_has_running_flag(self, handler):
        """Local provider status should have running flag."""
        status = handler.check_local_provider()
        assert isinstance(status.is_running, bool)


class TestCloudProviderDetection:
    """Test cloud Mistral provider detection."""

    def test_check_cloud_provider_returns_status(self, handler):
        """check_cloud_provider should return ProviderStatus."""
        status = handler.check_cloud_provider()
        assert isinstance(status, ProviderStatus)

    def test_cloud_provider_status_has_provider_id(self, handler):
        """Cloud provider status should have provider ID."""
        status = handler.check_cloud_provider()
        assert status.provider_id == ProviderType.MISTRAL_CLOUD.value

    def test_cloud_provider_has_availability(self, handler):
        """Cloud provider should indicate availability."""
        status = handler.check_cloud_provider()
        assert isinstance(status.is_available, bool)

    def test_cloud_provider_has_configured_flag(self, handler):
        """Cloud provider status should have configured flag."""
        status = handler.check_cloud_provider()
        assert isinstance(status.is_configured, bool)

    def test_cloud_provider_has_running_flag(self, handler):
        """Cloud provider status should have running flag."""
        status = handler.check_cloud_provider()
        assert isinstance(status.is_running, bool)


class TestAllProvidersCheck:
    """Test checking all providers at once."""

    def test_check_all_providers_returns_dict(self, handler):
        """check_all_providers should return dict."""
        results = handler.check_all_providers()
        assert isinstance(results, dict)

    def test_check_all_providers_has_both_providers(self, handler):
        """check_all_providers should include local and cloud providers."""
        results = handler.check_all_providers()
        provider_ids = list(results.keys())
        assert len(provider_ids) >= 2

    def test_check_all_providers_values_are_status(self, handler):
        """All values in check_all_providers should be ProviderStatus."""
        results = handler.check_all_providers()
        for status in results.values():
            assert isinstance(status, ProviderStatus)


class TestProviderAvailability:
    """Test checking provider availability."""

    def test_provider_models_list(self, handler):
        """Provider status should have loaded models list."""
        status = handler.check_local_provider()
        assert hasattr(status, "loaded_models")
        assert isinstance(status.loaded_models, list)

    def test_provider_default_model(self, handler):
        """Provider status should have default model info."""
        status = handler.check_local_provider()
        assert hasattr(status, "default_model")
        assert status.default_model is None or isinstance(status.default_model, str)


class TestProviderCaching:
    """Test provider status caching."""

    def test_cache_results_match(self, handler):
        """Cached results should match."""
        status1 = handler.check_local_provider()
        status2 = handler.check_local_provider()

        assert status1.provider_id == status2.provider_id
        assert status1.is_available == status2.is_available


class TestStatusIntegration:
    """Test integration with TUI and Wizard."""

    def test_handler_works_for_tui_status(self, handler):
        """Handler should support TUI status checks."""
        local = handler.check_local_provider()
        mistral = handler.check_cloud_provider()

        assert isinstance(local, ProviderStatus)
        assert isinstance(mistral, ProviderStatus)

    def test_handler_supports_wizard_api_calls(self, handler):
        """Handler should support Wizard API route calls."""
        results = handler.check_all_providers()
        assert isinstance(results, dict)
        for status in results.values():
            assert isinstance(status, ProviderStatus)


class TestErrorHandling:
    """Test error handling in provider detection."""

    def test_failed_provider_returns_status(self, handler):
        """Failed provider detection should return status with issue."""
        status = handler.check_local_provider()
        if not status.is_available:
            assert status.issue is not None or not status.is_configured

    def test_all_providers_returns_results_even_if_failed(self, handler):
        """If all providers fail, should still return status dict."""
        results = handler.check_all_providers()
        assert isinstance(results, dict)
        assert len(results) > 0


class TestProviderConfiguration:
    """Test provider configuration checking."""

    def test_configured_flag_is_boolean(self, handler):
        """is_configured should be boolean."""
        status = handler.check_local_provider()
        assert isinstance(status.is_configured, bool)

    def test_running_flag_is_boolean(self, handler):
        """is_running should be boolean."""
        status = handler.check_local_provider()
        assert isinstance(status.is_running, bool)

    def test_available_flag_is_boolean(self, handler):
        """is_available should be boolean."""
        status = handler.check_local_provider()
        assert isinstance(status.is_available, bool)

    def test_available_requires_configured_and_running(self, handler):
        """is_available should require both configured and running."""
        status = handler.check_local_provider()
        if status.is_available:
            assert status.is_configured is True
            assert status.is_running is True


class TestProviderIssueMessages:
    """Test provider issue message reporting."""

    def test_issue_is_string_or_none(self, handler):
        """issue field should be string or None."""
        status = handler.check_local_provider()
        assert isinstance(status.issue, (str, type(None)))

    def test_issue_populated_when_unavailable(self, handler):
        """If unavailable, should have issue message."""
        status = handler.check_local_provider()
        if not status.is_available:
            # Should have an issue message
            assert status.issue is not None or (not status.is_configured)
