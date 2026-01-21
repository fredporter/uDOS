"""
Base Provider - Abstract Interface
===================================

Common interface for all API providers.
"""

from abc import ABC, abstractmethod
from typing import Dict, Any, Optional
from dataclasses import dataclass
from enum import Enum


class ProviderError(Exception):
    """Base exception for provider errors."""

    pass


class AuthenticationError(ProviderError):
    """Authentication failed."""

    pass


class RateLimitError(ProviderError):
    """Rate limit exceeded."""

    pass


class QuotaExceededError(ProviderError):
    """Usage quota exceeded."""

    pass


class ProviderStatus(Enum):
    """Provider status."""

    NOT_CONFIGURED = "not_configured"
    READY = "ready"
    AUTH_REQUIRED = "auth_required"
    RATE_LIMITED = "rate_limited"
    ERROR = "error"


@dataclass
class ProviderConfig:
    """Provider configuration."""

    name: str
    api_key: Optional[str] = None
    api_base: Optional[str] = None
    timeout_seconds: int = 30
    max_retries: int = 3
    rate_limit_rpm: int = 60


class BaseProvider(ABC):
    """
    Abstract base class for API providers.

    All providers must implement:
      - authenticate()
      - execute()
      - get_status()
    """

    def __init__(self, config: ProviderConfig):
        """Initialize provider with config."""
        self.config = config
        self.status = ProviderStatus.NOT_CONFIGURED
        self._request_count = 0
        self._last_request_time = None

    @abstractmethod
    async def authenticate(self) -> bool:
        """
        Authenticate with the provider.

        Returns:
            True if authentication successful

        Raises:
            AuthenticationError if authentication fails
        """
        pass

    @abstractmethod
    async def execute(self, request: Dict[str, Any]) -> Dict[str, Any]:
        """
        Execute a request.

        Args:
            request: Provider-specific request data

        Returns:
            Provider-specific response data

        Raises:
            ProviderError on failure
        """
        pass

    @abstractmethod
    def get_status(self) -> Dict[str, Any]:
        """
        Get provider status.

        Returns:
            Status dictionary with availability info
        """
        pass

    def is_available(self) -> bool:
        """Check if provider is ready for requests."""
        return self.status == ProviderStatus.READY

    def _check_rate_limit(self) -> bool:
        """Check if we're within rate limits."""
        import time

        if self._last_request_time is None:
            return True

        elapsed = time.time() - self._last_request_time
        min_interval = 60.0 / self.config.rate_limit_rpm

        return elapsed >= min_interval
