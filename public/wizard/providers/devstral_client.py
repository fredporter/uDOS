"""
Devstral Client - Mistral AI Coding Assistant
==============================================

Provider client for Mistral AI's Devstral coding-focused models.
Supports code generation, explanation, debugging, and refactoring.

Models:
  - devstral-small-2505: Fast coding model (32k context)
  - codestral-latest: General code model (32k context)
  - mistral-large-latest: Most capable (128k context)

Alpha v1.0.0.20
"""

import json
import time
from pathlib import Path
from typing import Dict, Any, Optional, List, AsyncGenerator
from dataclasses import dataclass

from .base_provider import (
    BaseProvider,
    ProviderConfig,
    ProviderStatus,
    ProviderError,
    AuthenticationError,
    RateLimitError,
    QuotaExceededError,
)

# Model cost per 1K tokens (USD) - 2025 pricing
# OPEN = free tier available, PREMIER = paid only
MODEL_COSTS = {
    # FREE TIER (OPEN) MODELS
    "open-mistral-nemo": {"input": 0.00015, "output": 0.00015, "free": True},
    "mistral-small-latest": {"input": 0.0001, "output": 0.0003, "free": True},
    "devstral-small-2505": {"input": 0.0001, "output": 0.0003, "free": True},
    # PAID MODELS
    "codestral-latest": {"input": 0.0003, "output": 0.0009, "free": False},
    "mistral-large-latest": {"input": 0.002, "output": 0.006, "free": False},
    "mistral-medium-latest": {"input": 0.00065, "output": 0.002, "free": False},
}

# Default model - use free tier
DEFAULT_MODEL = "open-mistral-nemo"


@dataclass
class DevstralConfig(ProviderConfig):
    """Devstral-specific configuration."""

    model: str = DEFAULT_MODEL
    max_tokens: int = 4096
    temperature: float = 0.7
    top_p: float = 0.95


class DevstralClient(BaseProvider):
    """
    Mistral AI Devstral coding assistant client.

    Usage:
        config = DevstralConfig(
            name="devstral",
            api_key="your-api-key"
        )
        client = DevstralClient(config)
        await client.authenticate()

        response = await client.code_generate(
            language="python",
            prompt="Create a function that calculates fibonacci"
        )
    """

    API_BASE = "https://api.mistral.ai/v1"
    CONFIG_PATH = Path(__file__).parent.parent / "config"
    API_KEYS_FILE = CONFIG_PATH / "ai_keys.json"

    def __init__(self, config: DevstralConfig = None):
        """Initialize Devstral client."""
        if config is None:
            config = DevstralConfig(name="devstral")

        # Try to get API key from environment if not provided
        if not config.api_key:
            import os

            config.api_key = os.environ.get("MISTRAL_API_KEY")

        # Try config file if still not set
        if not config.api_key and self.API_KEYS_FILE.exists():
            try:
                import json

                keys = json.loads(self.API_KEYS_FILE.read_text())
                config.api_key = keys.get("MISTRAL_API_KEY")
            except Exception:
                pass

        super().__init__(config)
        self.config: DevstralConfig = config
        self.api_key = config.api_key  # For compatibility with test code
        self._total_tokens_used = 0
        self._total_cost = 0.0

    async def authenticate(self) -> bool:
        """
        Verify API key is valid.

        Returns:
            True if authentication successful
        """
        if not self.config.api_key:
            self.status = ProviderStatus.AUTH_REQUIRED
            raise AuthenticationError("MISTRAL_API_KEY not configured")

        try:
            # Test authentication with a minimal request
            response = await self._make_request(
                "GET",
                "/models",
            )

            if "data" in response:
                self.status = ProviderStatus.READY
                return True
            else:
                self.status = ProviderStatus.ERROR
                return False

        except Exception as e:
            self.status = ProviderStatus.ERROR
            raise AuthenticationError(f"Authentication failed: {str(e)}")

    async def execute(self, request: Dict[str, Any]) -> Dict[str, Any]:
        """
        Execute a generic request.

        Args:
            request: Request with 'action' and params

        Returns:
            Response dictionary
        """
        # Auto-authenticate if needed
        if not self.is_available() and self.api_key:
            await self.authenticate()

        action = request.get("action", "chat")

        # Handle simple prompt-based requests
        if "prompt" in request and action == "chat":
            messages = [{"role": "user", "content": request["prompt"]}]
            return await self.chat(
                messages=messages,
                model=request.get("model"),
                temperature=request.get("temperature"),
                max_tokens=request.get("max_tokens"),
            )

        if action == "chat":
            return await self.chat(
                messages=request.get("messages", []),
                model=request.get("model"),
                temperature=request.get("temperature"),
                max_tokens=request.get("max_tokens"),
            )
        elif action == "code_generate":
            return await self.code_generate(
                language=request.get("language", "python"),
                prompt=request.get("prompt", ""),
            )
        elif action == "code_explain":
            return await self.code_explain(code=request.get("code", ""))
        elif action == "code_debug":
            return await self.code_debug(
                code=request.get("code", ""),
                error=request.get("error"),
            )
        elif action == "code_refactor":
            return await self.code_refactor(code=request.get("code", ""))
        else:
            raise ProviderError(f"Unknown action: {action}")

    def get_status(self) -> Dict[str, Any]:
        """Get provider status."""
        return {
            "provider": "devstral",
            "status": self.status.value,
            "available": self.is_available(),
            "model": self.config.model,
            "configured": bool(self.config.api_key),
            "stats": {
                "total_tokens": self._total_tokens_used,
                "total_cost_usd": round(self._total_cost, 4),
                "request_count": self._request_count,
            },
        }

    async def chat(
        self,
        messages: List[Dict[str, str]],
        model: str = None,
        temperature: float = None,
        max_tokens: int = None,
        stream: bool = False,
    ) -> Dict[str, Any]:
        """
        Send a chat completion request.

        Args:
            messages: List of {"role": "user/assistant/system", "content": "..."}
            model: Model to use (default: config.model)
            temperature: Sampling temperature
            max_tokens: Maximum tokens to generate
            stream: Whether to stream response

        Returns:
            Response with generated content and usage stats
        """
        # Auto-authenticate if needed
        if not self.is_available() and self.api_key:
            await self.authenticate()

        if not self.is_available():
            raise ProviderError("Provider not ready. Call authenticate() first.")

        model = model or self.config.model
        temperature = (
            temperature if temperature is not None else self.config.temperature
        )
        max_tokens = max_tokens or self.config.max_tokens

        payload = {
            "model": model,
            "messages": messages,
            "temperature": temperature,
            "max_tokens": max_tokens,
        }

        if stream:
            payload["stream"] = True
            return await self._stream_request("/chat/completions", payload)

        response = await self._make_request("POST", "/chat/completions", payload)

        # Extract content and track usage
        content = ""
        if "choices" in response and len(response["choices"]) > 0:
            content = response["choices"][0]["message"]["content"]

        usage = response.get("usage", {})
        self._track_usage(model, usage)

        return {
            "content": content,
            "model": model,
            "usage": usage,
            "cost_usd": self._calculate_cost(model, usage),
        }

    async def code_generate(
        self,
        language: str,
        prompt: str,
        context: str = None,
    ) -> Dict[str, Any]:
        """
        Generate code based on a prompt.

        Args:
            language: Programming language
            prompt: Description of what to generate
            context: Optional existing code context

        Returns:
            Generated code with explanation
        """
        system_prompt = f"""You are Devstral, an expert coding assistant specialized in {language}.
Generate clean, well-documented, production-ready code.
Include docstrings/comments explaining the code.
Follow {language} best practices and conventions."""

        user_message = f"Generate {language} code for: {prompt}"
        if context:
            user_message += f"\n\nExisting code context:\n```{language}\n{context}\n```"

        messages = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_message},
        ]

        return await self.chat(messages)

    async def code_explain(self, code: str, language: str = None) -> Dict[str, Any]:
        """
        Explain what code does.

        Args:
            code: Code to explain
            language: Optional language hint

        Returns:
            Detailed explanation
        """
        lang_hint = f" ({language})" if language else ""

        messages = [
            {
                "role": "system",
                "content": "You are Devstral, an expert at explaining code clearly and thoroughly. Explain what the code does, how it works, and any important patterns or techniques used.",
            },
            {
                "role": "user",
                "content": f"Explain this code{lang_hint}:\n\n```\n{code}\n```",
            },
        ]

        return await self.chat(messages)

    async def code_debug(
        self,
        code: str,
        error: str = None,
        language: str = None,
    ) -> Dict[str, Any]:
        """
        Debug code and suggest fixes.

        Args:
            code: Code with issues
            error: Optional error message
            language: Optional language hint

        Returns:
            Debug analysis and fix suggestions
        """
        lang_hint = f" ({language})" if language else ""

        user_content = f"Debug this code{lang_hint}:\n\n```\n{code}\n```"
        if error:
            user_content += f"\n\nError message:\n{error}"

        messages = [
            {
                "role": "system",
                "content": """You are Devstral, an expert debugger. Analyze the code for:
1. Syntax errors
2. Logic errors
3. Runtime issues
4. Edge cases

Provide specific fixes with explanations.""",
            },
            {"role": "user", "content": user_content},
        ]

        return await self.chat(messages)

    async def code_refactor(
        self,
        code: str,
        goals: List[str] = None,
        language: str = None,
    ) -> Dict[str, Any]:
        """
        Suggest code refactoring improvements.

        Args:
            code: Code to refactor
            goals: Optional specific refactoring goals
            language: Optional language hint

        Returns:
            Refactored code with explanations
        """
        lang_hint = f" ({language})" if language else ""

        default_goals = [
            "Improve readability",
            "Reduce complexity",
            "Follow best practices",
            "Add proper error handling",
        ]
        goals = goals or default_goals

        goals_text = "\n".join(f"- {g}" for g in goals)

        messages = [
            {
                "role": "system",
                "content": f"""You are Devstral, an expert at code refactoring. Improve the code with these goals:
{goals_text}

Show the refactored code and explain each improvement.""",
            },
            {
                "role": "user",
                "content": f"Refactor this code{lang_hint}:\n\n```\n{code}\n```",
            },
        ]

        return await self.chat(messages)

    async def _make_request(
        self,
        method: str,
        endpoint: str,
        data: Dict[str, Any] = None,
    ) -> Dict[str, Any]:
        """Make HTTP request to Mistral API."""
        import aiohttp

        url = f"{self.API_BASE}{endpoint}"
        headers = {
            "Authorization": f"Bearer {self.config.api_key}",
            "Content-Type": "application/json",
        }

        # Rate limit check (skip for non-generation endpoints like /models)
        is_generation = endpoint != "/models"
        if is_generation and not self._check_rate_limit():
            raise RateLimitError("Rate limit exceeded. Please wait.")

        self._request_count += 1
        # Only update last request time for generation requests
        if is_generation:
            self._last_request_time = time.time()

        try:
            async with aiohttp.ClientSession() as session:
                if method == "GET":
                    async with session.get(
                        url,
                        headers=headers,
                        timeout=aiohttp.ClientTimeout(
                            total=self.config.timeout_seconds
                        ),
                    ) as response:
                        if response.status == 401:
                            raise AuthenticationError("Invalid API key")
                        elif response.status == 429:
                            raise RateLimitError("API rate limit exceeded")
                        elif response.status != 200:
                            text = await response.text()
                            raise ProviderError(f"API error {response.status}: {text}")

                        return await response.json()

                elif method == "POST":
                    async with session.post(
                        url,
                        headers=headers,
                        json=data,
                        timeout=aiohttp.ClientTimeout(
                            total=self.config.timeout_seconds
                        ),
                    ) as response:
                        if response.status == 401:
                            raise AuthenticationError("Invalid API key")
                        elif response.status == 429:
                            raise RateLimitError("API rate limit exceeded")
                        elif response.status != 200:
                            text = await response.text()
                            raise ProviderError(f"API error {response.status}: {text}")

                        return await response.json()

        except aiohttp.ClientError as e:
            raise ProviderError(f"Network error: {str(e)}")

    async def _stream_request(
        self,
        endpoint: str,
        data: Dict[str, Any],
    ) -> AsyncGenerator[str, None]:
        """Make streaming request to Mistral API."""
        import aiohttp

        url = f"{self.API_BASE}{endpoint}"
        headers = {
            "Authorization": f"Bearer {self.config.api_key}",
            "Content-Type": "application/json",
        }

        self._request_count += 1
        self._last_request_time = time.time()

        try:
            async with aiohttp.ClientSession() as session:
                async with session.post(
                    url,
                    headers=headers,
                    json=data,
                    timeout=aiohttp.ClientTimeout(total=120),
                ) as response:
                    if response.status != 200:
                        text = await response.text()
                        raise ProviderError(f"API error {response.status}: {text}")

                    full_content = []
                    async for line in response.content:
                        line = line.decode("utf-8").strip()
                        if line.startswith("data: "):
                            data_str = line[6:]
                            if data_str == "[DONE]":
                                break
                            try:
                                chunk = json.loads(data_str)
                                if "choices" in chunk:
                                    delta = chunk["choices"][0].get("delta", {})
                                    content = delta.get("content", "")
                                    if content:
                                        full_content.append(content)
                                        yield content
                            except json.JSONDecodeError:
                                continue

                    # Async generators cannot return values
                    # The full content is accumulated externally

        except aiohttp.ClientError as e:
            raise ProviderError(f"Network error: {str(e)}")

    def _track_usage(self, model: str, usage: Dict[str, int]):
        """Track token usage and costs."""
        prompt_tokens = usage.get("prompt_tokens", 0)
        completion_tokens = usage.get("completion_tokens", 0)
        total_tokens = prompt_tokens + completion_tokens

        self._total_tokens_used += total_tokens
        self._total_cost += self._calculate_cost(model, usage)

    def _calculate_cost(self, model: str, usage: Dict[str, int]) -> float:
        """Calculate cost for usage."""
        if model not in MODEL_COSTS:
            return 0.0

        costs = MODEL_COSTS[model]
        prompt_tokens = usage.get("prompt_tokens", 0)
        completion_tokens = usage.get("completion_tokens", 0)

        input_cost = (prompt_tokens / 1000) * costs["input"]
        output_cost = (completion_tokens / 1000) * costs["output"]

        return input_cost + output_cost


# Convenience function
def get_devstral_client(api_key: str = None) -> DevstralClient:
    """
    Get a configured Devstral client.

    Args:
        api_key: Optional API key (uses env var if not provided)

    Returns:
        DevstralClient instance
    """
    config = DevstralConfig(name="devstral", api_key=api_key)
    return DevstralClient(config)


__all__ = [
    "DevstralClient",
    "DevstralConfig",
    "get_devstral_client",
    "MODEL_COSTS",
    "DEFAULT_MODEL",
]
