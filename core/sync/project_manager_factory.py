"""Factory for creating project management providers (Phase 8.4)."""

from typing import Optional

from core.sync.jira_manager import JiraManager
from core.sync.linear_manager import LinearManager


class ProjectManagerFactory:
    """Factory for instantiating project management providers."""

    PROVIDERS = {
        "jira": JiraManager,
        "linear": LinearManager,
    }

    @classmethod
    def create_provider(cls, provider_type: str) -> Optional[object]:
        """Create a project manager provider instance.

        Args:
            provider_type: Provider type ('jira', 'linear')

        Returns:
            Provider instance or None if not found
        """
        provider_class = cls.PROVIDERS.get(provider_type)
        if provider_class:
            return provider_class()
        return None

    @classmethod
    def get_available_providers(cls) -> list:
        """Get list of available project manager providers."""
        return list(cls.PROVIDERS.keys())
