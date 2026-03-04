"""Provider Engine - Async Provider Interaction Layer

.. deprecated::
    This module's cloud provider adapters (_call_mistral, _call_openai,
    _call_anthropic, _call_gemini) are unimplemented stubs superseded by
    the production fallback chain in v1.4.7.

    **Canonical replacements (as of v1.4.7):**

    - Cloud multi-provider fallback:
      ``wizard.services.cloud_provider_executor.run_cloud_with_fallback()``
    - Multi-provider availability check:
      ``wizard.services.cloud_provider_executor.get_cloud_availability()``
    - Provider policy contracts (auth, request/response shape, failover):
      ``core.services.cloud_provider_policy``
Handles all interactions with OK Providers (Mistral, OpenAI, Anthropic, Gemini).
Enforces timeout guards, stream handling, response normalisation, and error recovery.

Architecture Rules (from vibe/AGENTS.md):
- NO direct execution of responses (normalisation only)
- Timeout guards on all calls
- Proper stream closing
- Provider capability respect
- Error recovery with fallback chain

Version: 1.0.0
Milestone: v1.4.6 Architecture Stabilisation
"""

from __future__ import annotations

import asyncio
from dataclasses import dataclass
from enum import Enum
import logging

from vibe.core.response_normaliser import NormalisedResponse, ResponseNormaliser

logger = logging.getLogger("vibe.provider-engine")


class ProviderType(str, Enum):
    """Supported provider types."""

    MISTRAL = "mistral"
    OPENAI = "openai"
    ANTHROPIC = "anthropic"
    GEMINI = "gemini"


class ProviderStatus(str, Enum):
    """Provider availability status."""

    AVAILABLE = "available"
    UNAVAILABLE = "unavailable"
    TIMEOUT = "timeout"
    ERROR = "error"


@dataclass
class ProviderResult:
    """Result from provider call."""

    success: bool
    raw_response: str = ""
    normalised: NormalisedResponse | None = None
    provider: str = ""
    model: str = ""
    error: str | None = None
    status: ProviderStatus = ProviderStatus.UNAVAILABLE
    execution_time: float = 0.0


class ProviderEngine:
    """Async provider interaction engine with timeout guards and response normalisation."""

    def __init__(
        self, normaliser: ResponseNormaliser, timeout: int = 30, max_retries: int = 2
    ):
        """Initialize provider engine.

        Args:
            normaliser: ResponseNormaliser instance for sanitizing responses
            timeout: Default timeout in seconds for provider calls
            max_retries: Maximum retry attempts on transient failures
        """
        self.normaliser = normaliser
        self.timeout = timeout
        self.max_retries = max_retries
        self.logger = logger

    async def call_provider(
        self,
        provider_type: str,
        model: str,
        prompt: str,
        system: str | None = None,
        stream: bool = False,
        timeout: int | None = None,
        **kwargs,
    ) -> ProviderResult:
        """Call provider with timeout guards and response normalisation.

        Args:
            provider_type: Provider to use (mistral, openai, anthropic, gemini)
            model: Model identifier
            prompt: User prompt
            system: System message (optional)
            stream: Whether to stream response
            timeout: Override default timeout
            **kwargs: Additional provider-specific parameters

        Returns:
            ProviderResult with normalised response or error
        """
        import time

        start_time = time.time()
        effective_timeout = timeout or self.timeout

        try:
            self.logger.info(
                f"Calling {provider_type} provider: model={model}, timeout={effective_timeout}s"
            )

            # Route to provider-specific handler
            if provider_type == ProviderType.MISTRAL.value:
                raw_response = await self._call_mistral(
                    model, prompt, system, stream, effective_timeout, **kwargs
                )
            elif provider_type == ProviderType.OPENAI.value:
                raw_response = await self._call_openai(
                    model, prompt, system, stream, effective_timeout, **kwargs
                )
            elif provider_type == ProviderType.ANTHROPIC.value:
                raw_response = await self._call_anthropic(
                    model, prompt, system, stream, effective_timeout, **kwargs
                )
            elif provider_type == ProviderType.GEMINI.value:
                raw_response = await self._call_gemini(
                    model, prompt, system, stream, effective_timeout, **kwargs
                )
            else:
                return ProviderResult(
                    success=False,
                    error=f"Unsupported provider: {provider_type}",
                    provider=provider_type,
                    model=model,
                    status=ProviderStatus.ERROR,
                )

            # Normalise response
            normalised = self.normaliser.normalise(raw_response)

            execution_time = time.time() - start_time
            self.logger.info(
                f"Provider call succeeded: {len(raw_response)} chars in {execution_time:.2f}s"
            )

            return ProviderResult(
                success=True,
                raw_response=raw_response,
                normalised=normalised,
                provider=provider_type,
                model=model,
                status=ProviderStatus.AVAILABLE,
                execution_time=execution_time,
            )

        except TimeoutError:
            execution_time = time.time() - start_time
            error_msg = f"Provider timeout after {execution_time:.1f}s"
            self.logger.error(error_msg)
            return ProviderResult(
                success=False,
                error=error_msg,
                provider=provider_type,
                model=model,
                status=ProviderStatus.TIMEOUT,
                execution_time=execution_time,
            )

        except Exception as exc:
            execution_time = time.time() - start_time
            error_msg = f"Provider error: {exc}"
            self.logger.error(error_msg, exc_info=True)
            return ProviderResult(
                success=False,
                error=error_msg,
                provider=provider_type,
                model=model,
                status=ProviderStatus.ERROR,
                execution_time=execution_time,
            )

    async def _call_mistral(
        self,
        model: str,
        prompt: str,
        system: str | None,
        stream: bool,
        timeout: int,
        **kwargs,
    ) -> str:
        """Call Mistral API provider.

        .. deprecated::
            Use ``wizard.services.cloud_provider_executor.run_cloud_with_fallback()``
            which supports Mistral, OpenRouter, OpenAI, Anthropic, and Gemini with
            automatic failover. This stub will not be implemented here.
        """
        raise NotImplementedError(
            "Mistral adapter not implemented here. "
            "Use wizard.services.cloud_provider_executor.run_cloud_with_fallback() instead."
        )

    async def _call_openai(
        self,
        model: str,
        prompt: str,
        system: str | None,
        stream: bool,
        timeout: int,
        **kwargs,
    ) -> str:
        """Call OpenAI API provider.

        .. deprecated::
            Use ``wizard.services.cloud_provider_executor.run_cloud_with_fallback()``.
        """
        raise NotImplementedError(
            "OpenAI adapter not implemented here. "
            "Use wizard.services.cloud_provider_executor.run_cloud_with_fallback() instead."
        )

    async def _call_anthropic(
        self,
        model: str,
        prompt: str,
        system: str | None,
        stream: bool,
        timeout: int,
        **kwargs,
    ) -> str:
        """Call Anthropic API provider.

        .. deprecated::
            Use ``wizard.services.cloud_provider_executor.run_cloud_with_fallback()``.
        """
        raise NotImplementedError(
            "Anthropic adapter not implemented here. "
            "Use wizard.services.cloud_provider_executor.run_cloud_with_fallback() instead."
        )

    async def _call_gemini(
        self,
        model: str,
        prompt: str,
        system: str | None,
        stream: bool,
        timeout: int,
        **kwargs,
    ) -> str:
        """Call Google Gemini API provider.

        .. deprecated::
            Use ``wizard.services.cloud_provider_executor.run_cloud_with_fallback()``.
        """
        raise NotImplementedError(
            "Gemini adapter not implemented here. "
            "Use wizard.services.cloud_provider_executor.run_cloud_with_fallback() instead."
        )

    async def call_with_fallback(
        self,
        provider_chain: list[tuple[str, str]],
        prompt: str,
        system: str | None = None,
        **kwargs,
    ) -> ProviderResult:
        """Call providers in fallback chain until success.

        Args:
            provider_chain: List of (provider_type, model) tuples
            prompt: User prompt
            system: System message
            **kwargs: Additional parameters

        Returns:
            ProviderResult from first successful provider
        """
        last_error = None

        for provider_type, model in provider_chain:
            self.logger.info(f"Trying provider: {provider_type} / {model}")
            result = await self.call_provider(
                provider_type, model, prompt, system, **kwargs
            )

            if result.success:
                self.logger.info(f"Provider {provider_type} succeeded")
                return result

            last_error = result.error
            self.logger.warning(
                f"Provider {provider_type} failed: {result.error}, trying next..."
            )

        # All providers failed
        return ProviderResult(
            success=False,
            error=f"All providers failed. Last: {last_error}",
            status=ProviderStatus.ERROR,
        )

    def check_provider_availability(self, provider_type: str) -> ProviderStatus:
        """Check if provider is available.

        Args:
            provider_type: Provider to check

        Returns:
            ProviderStatus enum
        """
        # Synchronous availability check
        # TODO: Implement actual checks per provider
        # For now, assume all providers are potentially available
        return ProviderStatus.AVAILABLE
