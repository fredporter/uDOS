"""
AI & API Provider Implementations
=================================

Actual API client implementations for Wizard Server services.

Providers:
  - gmail_client.py - Google Gmail API (OAuth 2.0)
  - openai_client.py - OpenAI GPT models
  - anthropic_client.py - Anthropic Claude models
  - gemini_client.py - Google Gemini models
  - devstral_client.py - Mistral AI Devstral coding assistant
  - nounproject_client.py - Noun Project icon library

Each provider implements a consistent interface for:
  - Authentication/initialization
  - Request execution
  - Error handling
  - Rate limiting
  - Cost tracking
"""

from .base_provider import (
    BaseProvider,
    ProviderConfig,
    ProviderStatus,
    ProviderError,
    AuthenticationError,
    RateLimitError,
    QuotaExceededError,
)

# Lazy imports to avoid import errors when dependencies missing
__all__ = [
    "BaseProvider",
    "ProviderConfig",
    "ProviderStatus",
    "ProviderError",
    "AuthenticationError",
    "RateLimitError",
    "QuotaExceededError",
    # Clients (import individually when needed)
    "get_gmail_client",
    "get_openai_client",
    "get_anthropic_client",
    "get_gemini_client",
    "get_devstral_client",
    "get_nounproject_client",
]


def get_gmail_client(*args, **kwargs):
    """Get Gmail client (lazy import)."""
    from .gmail_client import GmailClient

    return GmailClient(*args, **kwargs)


def get_openai_client(*args, **kwargs):
    """Get OpenAI client (lazy import)."""
    from .openai_client import OpenAIClient

    return OpenAIClient(*args, **kwargs)


def get_anthropic_client(*args, **kwargs):
    """Get Anthropic client (lazy import)."""
    from .anthropic_client import AnthropicClient

    return AnthropicClient(*args, **kwargs)


def get_gemini_client(*args, **kwargs):
    """Get Gemini client (lazy import)."""
    from .gemini_client import GeminiClient

    return GeminiClient(*args, **kwargs)


def get_devstral_client(*args, **kwargs):
    """Get Devstral client (lazy import)."""
    from .devstral_client import DevstralClient, DevstralConfig

    config = DevstralConfig(name="devstral", **kwargs) if kwargs else None
    return DevstralClient(config)


def get_nounproject_client(*args, **kwargs):
    """Get Noun Project client (lazy import)."""
    from .nounproject_client import NounProjectClient, NounProjectConfig

    config = NounProjectConfig(name="nounproject", **kwargs) if kwargs else None
    return NounProjectClient(config)
