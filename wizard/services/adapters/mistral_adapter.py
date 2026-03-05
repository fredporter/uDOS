"""Mistral Provider Adapter

Standard adapter for Mistral API implementing ProviderEngine interface.

Architecture Rules (from Dev Mode compatibility governance):
- Standard call interface matching ProviderEngine
- Timeout guards on all operations
- Response normalisation before return
- Capability declaration
- API key management

Usage:
    from wizard.services.adapters.mistral_adapter import MistralAdapter

    adapter = MistralAdapter(api_key="your-api-key")

    # Check availability
    if adapter.is_available():
        response = await adapter.generate(
            model="mistral-small-latest",
            prompt="Write a hello world function",
            system="You are a coding assistant."
        )

Version: 1.0.0
Release baseline: v1.5 contributor routing
"""

from __future__ import annotations

import asyncio
from dataclasses import dataclass
import logging

import aiohttp

from core.services.unified_config_loader import get_config

logger = logging.getLogger("dev-mode-tool.mistral-adapter")


@dataclass
class MistralConfig:
    """Mistral adapter configuration."""

    api_key: str
    endpoint: str = "https://api.mistral.ai/v1"
    timeout: int = 30
    max_retries: int = 2


class MistralAdapter:
    """Mistral API provider adapter."""

    def __init__(self, api_key: str | None = None, config: MistralConfig | None = None):
        """Initialize Mistral adapter.

        Args:
            api_key: Mistral API key (or uses MISTRAL_API_KEY env var)
            config: MistralConfig or None for defaults
        """
        effective_api_key = api_key or get_config("MISTRAL_API_KEY", "")
        if not effective_api_key:
            raise ValueError(
                "Mistral API key required. Set MISTRAL_API_KEY env var or pass api_key parameter."
            )

        if config:
            self.config = config
        else:
            self.config = MistralConfig(api_key=effective_api_key)

        self.logger = logger
        self._connection_verified = False

    async def is_available(self) -> bool:
        """Check if Mistral API is available.

        Returns:
            True if API is reachable with valid key
        """
        try:
            headers = {"Authorization": f"Bearer {self.config.api_key}"}
            async with aiohttp.ClientSession() as session:
                async with asyncio.timeout(5):
                    async with session.get(
                        f"{self.config.endpoint}/models", headers=headers
                    ) as resp:
                        resp.raise_for_status()
                        self.logger.info("[MISTRAL] Connected successfully")
                        self._connection_verified = True
                        return True
        except Exception as exc:
            self.logger.warning(f"[MISTRAL] Connection failed: {exc}")
            self._connection_verified = False
            return False

    async def list_models(self) -> list[str]:
        """List available Mistral models.

        Returns:
            List of model IDs
        """
        try:
            headers = {"Authorization": f"Bearer {self.config.api_key}"}
            async with aiohttp.ClientSession() as session:
                async with asyncio.timeout(5):
                    async with session.get(
                        f"{self.config.endpoint}/models", headers=headers
                    ) as resp:
                        resp.raise_for_status()
                        data = await resp.json()
                        models = [m["id"] for m in data.get("data", [])]
                        return models
        except Exception as exc:
            self.logger.error(f"[MISTRAL] Failed to list models: {exc}")
            return []

    async def generate(
        self,
        model: str,
        prompt: str,
        system: str | None = None,
        stream: bool = False,
        timeout: int | None = None,
        **kwargs,
    ) -> str:
        """Generate response from Mistral API.

        Args:
            model: Model ID (e.g., "mistral-small-latest")
            prompt: User prompt
            system: System message (optional)
            stream: Stream response (not implemented yet)
            timeout: Override default timeout
            **kwargs: Additional model parameters

        Returns:
            Generated response text
        """
        effective_timeout = timeout or self.config.timeout

        # Build messages
        messages = []
        if system:
            messages.append({"role": "system", "content": system})
        messages.append({"role": "user", "content": prompt})

        # API payload
        payload = {
            "model": model,
            "messages": messages,
            "temperature": kwargs.get("temperature", 0.2),
            "top_p": kwargs.get("top_p", 0.95),
        }
        if "max_tokens" in kwargs:
            payload["max_tokens"] = kwargs["max_tokens"]

        headers = {
            "Authorization": f"Bearer {self.config.api_key}",
            "Content-Type": "application/json",
        }

        self.logger.debug(
            f"[MISTRAL] Calling API: model={model}, timeout={effective_timeout}s"
        )

        async with aiohttp.ClientSession() as session:
            async with asyncio.timeout(effective_timeout):
                async with session.post(
                    f"{self.config.endpoint}/chat/completions",
                    json=payload,
                    headers=headers,
                ) as resp:
                    resp.raise_for_status()
                    data = await resp.json()
                    response_text = data["choices"][0]["message"]["content"]

                    self.logger.info(f"[MISTRAL] Response: {len(response_text)} chars")
                    return response_text

    def get_capabilities(self) -> dict:
        """Get adapter capabilities.

        Returns:
            Dict with capability metadata
        """
        return {
            "provider": "mistral",
            "local": False,
            "streaming": False,  # TODO: Implement streaming
            "timeout_supported": True,
            "context_window": 32000,
            "cost": "medium",
            "latency": "fast",
            "models": [
                "mistral-small-latest",
                "mistral-medium-latest",
                "mistral-large-latest",
                "codestral-latest",
            ],
        }
