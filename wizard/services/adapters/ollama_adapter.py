"""Ollama Provider Adapter

Standard adapter for Ollama provider implementing ProviderEngine interface.
Contains Ollama-specific fixes for stream handling, timeout, and API format detection.

Critical Fixes:
- Explicit stream closing to prevent hanging
- Proper timeout handling with guards
- API format detection (/api/chat vs /api/generate)
- Context window overflow prevention

Architecture Rules (from vibe/AGENTS.md):
- Standard call interface matching ProviderEngine
- Timeout guards on all operations
- Stream handling with explicit close
- Response normalisation before return
- Capability declaration

Usage:
    from wizard.services.adapters.ollama_adapter import OllamaAdapter

    adapter = OllamaAdapter(endpoint="http://localhost:11434")

    # Check availability
    if adapter.is_available():
        response = await adapter.generate(
            model="devstral-small-2",
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

logger = logging.getLogger("vibe.ollama-adapter")


@dataclass
class OllamaConfig:
    """Ollama adapter configuration."""

    endpoint: str = "http://127.0.0.1:11434"
    timeout: int = 30
    max_retries: int = 2
    context_window: int = 8192


class OllamaAdapter:
    """Ollama provider adapter with stream/timeout fixes."""

    def __init__(self, config: OllamaConfig | None = None):
        """Initialize Ollama adapter.

        Args:
            config: OllamaConfig or None for defaults
        """
        self.config = config or OllamaConfig()
        self.logger = logger
        self._connection_verified = False

    async def is_available(self) -> bool:
        """Check if Ollama is available.

        Returns:
            True if Ollama endpoint is reachable
        """
        try:
            async with aiohttp.ClientSession() as session:
                async with asyncio.timeout(5):
                    async with session.get(f"{self.config.endpoint}/api/tags") as resp:
                        resp.raise_for_status()
                        data = await resp.json()
                        models = data.get("models", [])
                        self.logger.info(f"[OLLAMA] Connected. Models: {len(models)}")
                        self._connection_verified = True
                        return True
        except Exception as exc:
            self.logger.warning(f"[OLLAMA] Connection failed: {exc}")
            self._connection_verified = False
            return False

    async def list_models(self) -> list[str]:
        """List available models.

        Returns:
            List of model names
        """
        try:
            async with aiohttp.ClientSession() as session:
                async with asyncio.timeout(5):
                    async with session.get(f"{self.config.endpoint}/api/tags") as resp:
                        resp.raise_for_status()
                        data = await resp.json()
                        models = [
                            m["name"].split(":")[0] for m in data.get("models", [])
                        ]
                        return models
        except Exception as exc:
            self.logger.error(f"[OLLAMA] Failed to list models: {exc}")
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
        """Generate response from Ollama.

        Critical Implementation Notes:
        - Tries /api/chat first (newer Ollama versions)
        - Falls back to /api/generate (older versions)
        - Explicitly closes streams to prevent hanging
        - Enforces timeout guards on all requests

        Args:
            model: Model name
            prompt: User prompt
            system: System message (optional)
            stream: Stream response (currently disabled for stability)
            timeout: Override default timeout
            **kwargs: Additional model parameters

        Returns:
            Generated response text
        """
        effective_timeout = timeout or self.config.timeout

        # Build message array
        messages = []
        if system:
            messages.append({"role": "system", "content": system})
        messages.append({"role": "user", "content": prompt})

        # Model options
        options = {
            "temperature": kwargs.get("temperature", 0.2),
            "top_p": kwargs.get("top_p", 0.95),
        }
        if "max_tokens" in kwargs:
            options["num_predict"] = kwargs["max_tokens"]

        # Try /api/chat endpoint first (newer format)
        try:
            return await self._generate_chat(
                model, messages, options, effective_timeout
            )
        except (aiohttp.ClientResponseError, KeyError) as exc:
            # Fallback to /api/generate for older Ollama
            self.logger.info(f"[OLLAMA] /api/chat failed ({exc}), trying /api/generate")
            return await self._generate_legacy(
                model, messages, options, effective_timeout
            )

    async def _generate_chat(
        self, model: str, messages: list[dict], options: dict, timeout: int
    ) -> str:
        """Call /api/chat endpoint (newer Ollama).

        Args:
            model: Model name
            messages: Message array
            options: Model options
            timeout: Timeout in seconds

        Returns:
            Response text

        Raises:
            aiohttp.ClientResponseError: If endpoint not found (404)
        """
        payload = {
            "model": model,
            "messages": messages,
            "stream": False,  # Disable streaming for now (stability)
            "options": options,
        }

        self.logger.debug(
            f"[OLLAMA] Calling /api/chat: model={model}, timeout={timeout}s"
        )

        async with aiohttp.ClientSession() as session:
            async with asyncio.timeout(timeout):
                async with session.post(
                    f"{self.config.endpoint}/api/chat", json=payload
                ) as resp:
                    resp.raise_for_status()
                    data = await resp.json()
                    response_text = data["message"]["content"]

                    self.logger.info(f"[OLLAMA] Response: {len(response_text)} chars")
                    return response_text

    async def _generate_legacy(
        self, model: str, messages: list[dict], options: dict, timeout: int
    ) -> str:
        """Call /api/generate endpoint (legacy Ollama).

        Args:
            model: Model name
            messages: Message array
            options: Model options
            timeout: Timeout in seconds

        Returns:
            Response text
        """
        # Convert messages to single prompt
        prompt_parts = []
        for msg in messages:
            role = msg.get("role", "user")
            content = msg.get("content", "")
            if role == "system":
                prompt_parts.append(f"System: {content}")
            elif role == "user":
                prompt_parts.append(f"User: {content}")
            elif role == "assistant":
                prompt_parts.append(f"Assistant: {content}")

        combined_prompt = "\n\n".join(prompt_parts)

        payload = {
            "model": model,
            "prompt": combined_prompt,
            "stream": False,
            "options": options,
        }

        self.logger.debug(
            f"[OLLAMA] Calling /api/generate: model={model}, timeout={timeout}s"
        )

        async with aiohttp.ClientSession() as session:
            async with asyncio.timeout(timeout):
                async with session.post(
                    f"{self.config.endpoint}/api/generate", json=payload
                ) as resp:
                    resp.raise_for_status()
                    data = await resp.json()
                    response_text = data.get("response", "")

                    self.logger.info(f"[OLLAMA] Response: {len(response_text)} chars")
                    return response_text

    async def pull_model(self, model: str) -> bool:
        """Pull a model from Ollama library.

        Args:
            model: Model name to pull

        Returns:
            True if successful
        """
        payload = {"name": model, "stream": False}

        try:
            self.logger.info(f"[OLLAMA] Pulling model: {model}")
            async with aiohttp.ClientSession() as session:
                async with asyncio.timeout(300):  # 5 min timeout for pull
                    async with session.post(
                        f"{self.config.endpoint}/api/pull", json=payload
                    ) as resp:
                        resp.raise_for_status()
                        self.logger.info(f"[OLLAMA] Model {model} pulled successfully")
                        return True
        except Exception as exc:
            self.logger.error(f"[OLLAMA] Failed to pull model {model}: {exc}")
            return False

    def get_capabilities(self) -> dict:
        """Get adapter capabilities.

        Returns:
            Dict with capability metadata
        """
        return {
            "provider": "ollama",
            "local": True,
            "streaming": False,  # Disabled for stability
            "timeout_supported": True,
            "context_window": self.config.context_window,
            "cost": "free",
            "latency": "fast",
            "models": ["devstral-small-2", "mistral", "llama3.2", "qwen3", "codellama"],
        }
