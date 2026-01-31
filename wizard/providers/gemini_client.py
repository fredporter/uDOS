"""
Gemini Client - Google AI Models Implementation
================================================

Google Gemini API client for Gemini family models.

Setup Required:
  1. Get API key from ai.google.dev
  2. Set in config/ai_keys.json or environment

Dependencies:
  pip install google-generativeai

Models:
  - gemini-1.5-flash (fast, cheap)
  - gemini-1.5-pro (balanced)
  - gemini-pro (legacy)
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
    AuthenticationError,
    RateLimitError,
    ProviderError,
)
from core.services.logging_service import get_logger

logger = get_logger("gemini-client")

# Check for Google AI library
try:
    import google.generativeai as genai
    from google.generativeai.types import HarmCategory, HarmBlockThreshold

    GEMINI_AVAILABLE = True
except ImportError:
    GEMINI_AVAILABLE = False
    logger.warning("[GEMINI] google-generativeai package not installed")

# Config paths
CONFIG_PATH = Path(__file__).parent.parent / "config"
API_KEYS_FILE = CONFIG_PATH / "ai_keys.json"

# Cost per 1K tokens (USD) - as of 2025
MODEL_COSTS = {
    "gemini-2.0-flash": {"input": 0.0001, "output": 0.0004},
    "gemini-2.0-flash-lite": {"input": 0.000075, "output": 0.0003},
    "gemini-2.5-flash": {"input": 0.00015, "output": 0.0006},
    "gemini-2.5-pro": {"input": 0.00125, "output": 0.005},
    "gemini-flash-latest": {"input": 0.0001, "output": 0.0004},
    "gemini-pro-latest": {"input": 0.00125, "output": 0.005},
}


@dataclass
class GeminiRequest:
    """Request for Gemini completion."""

    prompt: str
    model: str = "gemini-2.0-flash"
    system_prompt: str = ""
    max_tokens: int = 1024
    temperature: float = 0.7
    stream: bool = False


@dataclass
class GeminiResponse:
    """Response from Gemini."""

    success: bool
    content: str = ""
    model: str = ""
    prompt_tokens: int = 0
    completion_tokens: int = 0
    total_tokens: int = 0
    cost_usd: float = 0.0
    latency_ms: int = 0
    finish_reason: str = ""
    error: Optional[str] = None


class GeminiClient(BaseProvider):
    """
    Google Gemini API client for uDOS Wizard Server.
    """

    DEFAULT_MODEL = "gemini-2.0-flash"

    def __init__(self, config: Optional[ProviderConfig] = None):
        """Initialize Gemini client."""
        if config is None:
            config = ProviderConfig(
                name="gemini",
                rate_limit_rpm=60,
            )
        super().__init__(config)

        self.api_key: Optional[str] = None
        self._models: Dict[str, Any] = {}

        self._load_api_key()

    def _load_api_key(self):
        """Load API key from config or environment."""
        import os

        # Try environment first
        self.api_key = os.environ.get("GEMINI_API_KEY") or os.environ.get(
            "GOOGLE_API_KEY"
        )

        # Try config file
        if not self.api_key and API_KEYS_FILE.exists():
            try:
                keys = json.loads(API_KEYS_FILE.read_text())
                self.api_key = keys.get("GEMINI_API_KEY") or keys.get("GOOGLE_API_KEY")
            except Exception:
                pass

        if self.api_key:
            self.status = ProviderStatus.READY
        else:
            self.status = ProviderStatus.NOT_CONFIGURED

    async def authenticate(self) -> bool:
        """Initialize Gemini client."""
        if not GEMINI_AVAILABLE:
            raise AuthenticationError(
                "google-generativeai package not installed. Run: pip install google-generativeai"
            )

        if not self.api_key:
            raise AuthenticationError("Gemini API key not configured")

        try:
            genai.configure(api_key=self.api_key)

            # Test by listing models
            models = genai.list_models()
            available = [
                m.name
                for m in models
                if "generateContent" in m.supported_generation_methods
            ]

            logger.info(f"[GEMINI] Found {len(available)} available models")
            self.status = ProviderStatus.READY
            return True

        except Exception as e:
            self.status = ProviderStatus.AUTH_REQUIRED
            raise AuthenticationError(f"Authentication failed: {e}")

    def _get_model(self, model_name: str):
        """Get or create model instance."""
        if model_name not in self._models:
            if not GEMINI_AVAILABLE:
                raise ProviderError("Gemini not available")

            genai.configure(api_key=self.api_key)

            # Safety settings - allow most content for knowledge work
            safety_settings = {
                HarmCategory.HARM_CATEGORY_HARASSMENT: HarmBlockThreshold.BLOCK_NONE,
                HarmCategory.HARM_CATEGORY_HATE_SPEECH: HarmBlockThreshold.BLOCK_ONLY_HIGH,
                HarmCategory.HARM_CATEGORY_SEXUALLY_EXPLICIT: HarmBlockThreshold.BLOCK_ONLY_HIGH,
                HarmCategory.HARM_CATEGORY_DANGEROUS_CONTENT: HarmBlockThreshold.BLOCK_ONLY_HIGH,
            }

            self._models[model_name] = genai.GenerativeModel(
                model_name=model_name,
                safety_settings=safety_settings,
            )

        return self._models[model_name]

    async def execute(self, request: Dict[str, Any]) -> Dict[str, Any]:
        """Execute Gemini request."""
        if not self.api_key:
            raise ProviderError("Gemini not configured")

        req = GeminiRequest(
            prompt=request.get("prompt", ""),
            model=request.get("model", self.DEFAULT_MODEL),
            system_prompt=request.get("system_prompt", ""),
            max_tokens=request.get("max_tokens", 1024),
            temperature=request.get("temperature", 0.7),
            stream=request.get("stream", False),
        )

        response = await self._complete(req)

        return {
            "success": response.success,
            "content": response.content,
            "model": response.model,
            "prompt_tokens": response.prompt_tokens,
            "completion_tokens": response.completion_tokens,
            "total_tokens": response.total_tokens,
            "cost_usd": response.cost_usd,
            "latency_ms": response.latency_ms,
            "finish_reason": response.finish_reason,
            "error": response.error,
        }

    async def _complete(self, request: GeminiRequest) -> GeminiResponse:
        """Execute completion request."""
        start_time = time.time()

        try:
            model = self._get_model(request.model)

            # Build prompt with system context
            full_prompt = request.prompt
            if request.system_prompt:
                full_prompt = f"{request.system_prompt}\n\n{request.prompt}"

            # Generation config
            gen_config = genai.types.GenerationConfig(
                max_output_tokens=request.max_tokens,
                temperature=request.temperature,
            )

            # Generate
            response = model.generate_content(
                full_prompt,
                generation_config=gen_config,
            )

            # Extract content
            content = ""
            if response.candidates:
                for part in response.candidates[0].content.parts:
                    content += part.text

            # Token counts (Gemini provides these)
            prompt_tokens = 0
            completion_tokens = 0

            if hasattr(response, "usage_metadata"):
                prompt_tokens = response.usage_metadata.prompt_token_count
                completion_tokens = response.usage_metadata.candidates_token_count

            # Calculate cost
            cost = self._calculate_cost(request.model, prompt_tokens, completion_tokens)

            latency = int((time.time() - start_time) * 1000)

            # Get finish reason
            finish_reason = ""
            if response.candidates:
                finish_reason = str(response.candidates[0].finish_reason)

            return GeminiResponse(
                success=True,
                content=content,
                model=request.model,
                prompt_tokens=prompt_tokens,
                completion_tokens=completion_tokens,
                total_tokens=prompt_tokens + completion_tokens,
                cost_usd=cost,
                latency_ms=latency,
                finish_reason=finish_reason,
            )

        except Exception as e:
            error_msg = str(e)

            # Check for specific error types
            if "quota" in error_msg.lower():
                return GeminiResponse(
                    success=False,
                    error=f"Quota exceeded: {e}",
                    latency_ms=int((time.time() - start_time) * 1000),
                )

            return GeminiResponse(
                success=False,
                error=error_msg,
                latency_ms=int((time.time() - start_time) * 1000),
            )

    async def stream_complete(
        self, request: GeminiRequest
    ) -> AsyncGenerator[str, None]:
        """Stream completion response."""
        if not self.api_key:
            raise ProviderError("Gemini not configured")

        model = self._get_model(request.model)

        full_prompt = request.prompt
        if request.system_prompt:
            full_prompt = f"{request.system_prompt}\n\n{request.prompt}"

        response = model.generate_content(
            full_prompt,
            generation_config=genai.types.GenerationConfig(
                max_output_tokens=request.max_tokens,
                temperature=request.temperature,
            ),
            stream=True,
        )

        for chunk in response:
            if chunk.text:
                yield chunk.text

    def _calculate_cost(
        self, model: str, input_tokens: int, output_tokens: int
    ) -> float:
        """Calculate request cost."""
        if model not in MODEL_COSTS:
            return 0.0

        costs = MODEL_COSTS[model]
        return (input_tokens * costs["input"] + output_tokens * costs["output"]) / 1000

    def get_status(self) -> Dict[str, Any]:
        """Get client status."""
        return {
            "provider": "gemini",
            "status": self.status.value,
            "available": self.is_available(),
            "api_key_set": bool(self.api_key),
            "models": list(MODEL_COSTS.keys()),
            "default_model": self.DEFAULT_MODEL,
        }

    def list_models(self) -> List[Dict[str, Any]]:
        """List available models with costs."""
        return [
            {
                "id": model,
                "input_cost_per_1k": costs["input"],
                "output_cost_per_1k": costs["output"],
            }
            for model, costs in MODEL_COSTS.items()
        ]


# Singleton
_client: Optional[GeminiClient] = None


def get_gemini_client() -> GeminiClient:
    """Get Gemini client singleton."""
    global _client
    if _client is None:
        _client = GeminiClient()
    return _client


if __name__ == "__main__":
    print("Gemini Client")
    print("=" * 40)
    print(f"google-generativeai available: {GEMINI_AVAILABLE}")
    print(f"Config path: {API_KEYS_FILE}")
    print()
    print("Setup:")
    print("1. Get API key from ai.google.dev")
    print("2. Add to config/ai_keys.json:")
    print('   {"GEMINI_API_KEY": "..."}')
    print("   OR set GEMINI_API_KEY environment variable")
