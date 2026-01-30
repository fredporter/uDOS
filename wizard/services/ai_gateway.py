"""
AI Gateway - LLM Access for User Devices
=========================================

Provides AI/LLM capabilities for user devices through the Wizard Server.
Handles API key management, rate limiting, and cost tracking.

Supported Providers:
  - Google Gemini (default)
  - OpenAI GPT
  - Anthropic Claude
  - Local models (Ollama)

Features:
  - Multi-provider routing
  - Cost tracking per device
  - Request caching
  - Prompt templates
  - Response filtering

Security:
  - API keys stored in encrypted KeyStore (v1.0.0.23+)
  - Keys encrypted with OS keychain or machine-derived key
  - User devices never see credentials
  - Rate limiting per device/day
  - Content safety filtering

Note: This is WIZARD-ONLY functionality.
User devices request AI operations via private transport.
"""

import json
import asyncio
import hashlib
import time
import uuid
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, Any, Optional, List, AsyncGenerator
from dataclasses import dataclass, asdict, field
from enum import Enum

from wizard.services.logging_manager import get_logger
from wizard.security.key_store import get_wizard_key
from .model_router import ModelRouter, Backend
from .policy_enforcer import PolicyEnforcer
from .vibe_service import VibeService
from .task_classifier import TaskClassifier

logger = get_logger("ai-gateway")

# Configuration paths
CONFIG_PATH = Path(__file__).parent / "config"
CACHE_PATH = Path(__file__).parent.parent.parent / "memory" / "wizard" / "ai_cache"


class AIProvider(Enum):
    """Supported AI providers."""

    GEMINI = "gemini"
    OPENAI = "openai"
    ANTHROPIC = "anthropic"
    OLLAMA = "ollama"


class AIModel(Enum):
    """Supported models."""

    # Gemini
    GEMINI_PRO = "gemini-pro"
    GEMINI_FLASH = "gemini-1.5-flash"
    GEMINI_ULTRA = "gemini-ultra"

    # OpenAI
    GPT4 = "gpt-4"
    GPT4_TURBO = "gpt-4-turbo"
    GPT35_TURBO = "gpt-3.5-turbo"

    # Anthropic
    CLAUDE_3_OPUS = "claude-3-opus"
    CLAUDE_3_SONNET = "claude-3-sonnet"
    CLAUDE_3_HAIKU = "claude-3-haiku"

    # Local
    OLLAMA_LLAMA = "llama2"
    OLLAMA_MISTRAL = "mistral"


@dataclass
class AIRequest:
    """AI request structure."""

    prompt: str
    model: str = ""
    system_prompt: str = ""
    max_tokens: int = 1024
    temperature: float = 0.7
    stream: bool = False

    # Routing metadata
    task_id: Optional[str] = None
    workspace: str = "core"
    privacy: str = "internal"
    urgency: str = "normal"
    tags: List[str] = field(default_factory=list)
    actor: Optional[str] = None

    # Context
    conversation_id: Optional[str] = None
    context: List[Dict[str, str]] = None

    def __post_init__(self):
        if self.context is None:
            self.context = []


@dataclass
class AIResponse:
    """AI response structure."""

    success: bool
    content: str = ""
    model: str = ""
    provider: str = ""

    # Usage
    prompt_tokens: int = 0
    completion_tokens: int = 0
    total_tokens: int = 0

    # Cost (USD)
    cost: float = 0.0

    # Routing meta
    backend: str = ""
    route: Dict[str, Any] = field(default_factory=dict)
    classification: Dict[str, Any] = field(default_factory=dict)

    # Meta
    cached: bool = False
    latency_ms: int = 0
    error: Optional[str] = None
    timestamp: str = ""

    def __post_init__(self):
        if not self.timestamp:
            self.timestamp = datetime.now().isoformat()

    def to_dict(self) -> Dict[str, Any]:
        """Return response as serializable dict."""
        return asdict(self)


@dataclass
class CostTracker:
    """Track AI API costs."""

    daily_budget: float = 10.0
    monthly_budget: float = 100.0

    spent_today: float = 0.0
    spent_this_month: float = 0.0

    last_daily_reset: str = ""
    last_monthly_reset: str = ""

    requests_today: int = 0
    total_requests: int = 0


# Cost per 1K tokens (approximate USD)
MODEL_COSTS = {
    # Gemini (input/output)
    "gemini-pro": (0.0005, 0.0015),
    "gemini-1.5-flash": (0.00035, 0.00105),
    "gemini-ultra": (0.01, 0.03),
    # OpenAI
    "gpt-4": (0.03, 0.06),
    "gpt-4-turbo": (0.01, 0.03),
    "gpt-3.5-turbo": (0.0005, 0.0015),
    # Anthropic
    "claude-3-opus": (0.015, 0.075),
    "claude-3-sonnet": (0.003, 0.015),
    "claude-3-haiku": (0.00025, 0.00125),
    # Local (free)
    "llama2": (0.0, 0.0),
    "mistral": (0.0, 0.0),
}


class AIGateway:
    """
    AI gateway service for uDOS.

    Routes AI requests to appropriate providers,
    manages costs, and caches responses.
    """

    # Rate limits
    MAX_REQUESTS_PER_DAY = 100
    MAX_TOKENS_PER_REQUEST = 4096
    # Conservative cloud safety threshold to avoid provider body read timeouts
    # (e.g., OpenRouter "user_request_timeout" when request body is too large)
    MAX_SAFE_CLOUD_TOKENS = 6000

    def __init__(self):
        """Initialize AI gateway."""
        self.config_path = CONFIG_PATH
        self.cache_path = CACHE_PATH
        self.cache_path.mkdir(parents=True, exist_ok=True)

        # Load API keys from secure KeyStore
        self.api_keys = self._load_api_keys()

        # Cost tracking
        self.costs = CostTracker()
        self._load_costs()

        # Available providers
        self.providers = self._detect_providers()

        # Routing + policy stack
        self.classifier = TaskClassifier()
        self.router = ModelRouter()
        self.policy = PolicyEnforcer()
        self.vibe = VibeService()

        logger.info(
            f"[AI] Gateway initialized with providers: {list(self.providers.keys())}"
        )

    def _load_api_keys(self) -> Dict[str, str]:
        """
        Load API keys from secure KeyStore.

        Falls back to legacy ai_keys.json for migration.
        """
        keys = {}

        # Primary: Load from encrypted KeyStore
        key_names = [
            "GEMINI_API_KEY",
            "OPENAI_API_KEY",
            "ANTHROPIC_API_KEY",
            "OLLAMA_HOST",
        ]

        for key_name in key_names:
            value = get_wizard_key(key_name)
            if value:
                keys[key_name] = value
                logger.debug(f"[AI] Loaded {key_name} from secure KeyStore")

        # Fallback: Legacy ai_keys.json (for migration)
        if not keys:
            keys_file = self.config_path / "ai_keys.json"
            if keys_file.exists():
                try:
                    legacy_keys = json.loads(keys_file.read_text())
                    # Filter out empty values and comments
                    for k, v in legacy_keys.items():
                        if v and not k.startswith("_"):
                            keys[k] = v

                    if keys:
                        logger.warning(
                            "[AI] Using legacy ai_keys.json - migrate to KeyStore with: "
                            "python -m core.security.key_store store GEMINI_API_KEY --realm wizard"
                        )
                except Exception as e:
                    logger.error(f"[AI] Failed to load legacy keys: {e}")

        return keys

    def _load_costs(self):
        """Load cost tracking data."""
        costs_file = self.config_path / "ai_costs.json"
        if costs_file.exists():
            try:
                data = json.loads(costs_file.read_text())
                self.costs = CostTracker(**data)
            except:
                pass

        # Reset daily/monthly if needed
        self._check_resets()

    def _save_costs(self):
        """Save cost tracking data."""
        self.config_path.mkdir(parents=True, exist_ok=True)
        costs_file = self.config_path / "ai_costs.json"
        costs_file.write_text(json.dumps(asdict(self.costs), indent=2))

    def _check_resets(self):
        """Reset daily/monthly counters if needed."""
        today = datetime.now().strftime("%Y-%m-%d")
        month = datetime.now().strftime("%Y-%m")

        if self.costs.last_daily_reset != today:
            self.costs.spent_today = 0.0
            self.costs.requests_today = 0
            self.costs.last_daily_reset = today

        if self.costs.last_monthly_reset != month:
            self.costs.spent_this_month = 0.0
            self.costs.last_monthly_reset = month

        self._save_costs()

    def _detect_providers(self) -> Dict[str, bool]:
        """Detect available AI providers."""
        providers = {}

        # Check API keys
        if "GEMINI_API_KEY" in self.api_keys:
            providers["gemini"] = True
        if "OPENAI_API_KEY" in self.api_keys:
            providers["openai"] = True
        if "ANTHROPIC_API_KEY" in self.api_keys:
            providers["anthropic"] = True

        # Check for local Ollama
        try:
            import requests
            resp = requests.get("http://127.0.0.1:11434/api/tags", timeout=2)
            providers["ollama"] = resp.status_code == 200
            if providers["ollama"]:
                logger.info("[LOCAL] Ollama endpoint detected and available")
        except Exception as e:
            providers["ollama"] = False
            logger.debug(f"[LOCAL] Ollama not available: {e}")

        return providers

    def _generate_task_id(self, device_id: str) -> str:
        """Generate a stable-ish task id for routing/logging."""
        return f"task-{device_id}-{uuid.uuid4().hex[:8]}"

    def _default_model(self) -> str:
        """Return default model (local-first)."""
        return self.vibe.config.model or "devstral-small-2"

    def is_available(self) -> bool:
        """Check if local Vibe or any cloud provider is available."""
        return self.vibe._verify_connection() or any(self.providers.values())

    def get_status(self) -> Dict[str, Any]:
        """Get gateway status."""
        return {
            "available": self.is_available(),
            "providers": self.providers,
            "costs": {
                "spent_today": round(self.costs.spent_today, 4),
                "daily_budget": self.costs.daily_budget,
                "spent_this_month": round(self.costs.spent_this_month, 4),
                "monthly_budget": self.costs.monthly_budget,
                "requests_today": self.costs.requests_today,
            },
            "routing": self.router.get_routing_stats(),
            "policy": self.policy.get_policy_status(),
            "vibe": self.vibe.get_status(),
        }

    def _get_cache_key(self, request: AIRequest) -> str:
        """Generate cache key for request."""
        data = f"{request.model}:{request.prompt}:{request.system_prompt}"
        return hashlib.md5(data.encode()).hexdigest()

    def _check_cache(self, request: AIRequest) -> Optional[AIResponse]:
        """Check if response is cached."""
        cache_key = self._get_cache_key(request)
        cache_file = self.cache_path / f"{cache_key}.json"

        if cache_file.exists():
            try:
                data = json.loads(cache_file.read_text())
                # Check expiry (24 hours)
                cached_time = datetime.fromisoformat(data["timestamp"])
                if datetime.now() - cached_time < timedelta(hours=24):
                    response = AIResponse(**data)
                    response.cached = True
                    return response
            except:
                pass

        return None

    def _save_cache(self, request: AIRequest, response: AIResponse):
        """Save response to cache."""
        if not response.success:
            return

        cache_key = self._get_cache_key(request)
        cache_file = self.cache_path / f"{cache_key}.json"
        cache_file.write_text(json.dumps(asdict(response), indent=2))

    def _calculate_cost(
        self, model: str, prompt_tokens: int, completion_tokens: int
    ) -> float:
        """Calculate request cost."""
        if model not in MODEL_COSTS:
            return 0.0

        input_cost, output_cost = MODEL_COSTS[model]
        return (prompt_tokens * input_cost + completion_tokens * output_cost) / 1000

    def _classification_to_dict(self, classification) -> Dict[str, Any]:
        """Serialize TaskClassification with enum values."""
        return {
            "task_id": classification.task_id,
            "workspace": classification.workspace.value,
            "intent": classification.intent.value,
            "privacy": classification.privacy.value,
            "urgency": classification.urgency,
            "size_estimate": classification.size_estimate,
            "tags": classification.tags,
            "estimated_tokens": classification.estimated_tokens,
            "timestamp": classification.timestamp,
        }

    async def complete(self, request: AIRequest, device_id: str) -> AIResponse:
        """Complete an AI request via local-first routing."""
        start_time = time.time()

        # Normalize request
        task_id = request.task_id or self._generate_task_id(device_id)
        request.task_id = task_id
        request.model = request.model or self._default_model()

        # Budget + rate guardrails
        self._check_resets()
        if self.costs.spent_today >= self.costs.daily_budget:
            return AIResponse(
                success=False,
                error=f"Daily AI budget exceeded (${self.costs.daily_budget})",
                backend=Backend.LOCAL.value,
            )

        if self.costs.requests_today >= self.MAX_REQUESTS_PER_DAY:
            return AIResponse(
                success=False,
                error=f"Daily request limit reached ({self.MAX_REQUESTS_PER_DAY})",
                backend=Backend.LOCAL.value,
            )

        # Classify + route
        try:
            profile = self.classifier.classify(
                task_id=task_id,
                prompt=request.prompt,
                workspace=request.workspace,
                urgency=request.urgency,
                explicit_privacy=request.privacy,
            )
        except Exception as exc:
            logger.warning(
                f"[LOCAL] Classification fallback for {task_id}: {exc}; defaulting to internal"
            )
            profile = self.classifier.classify(
                task_id=task_id,
                prompt=request.prompt,
                workspace=request.workspace,
                urgency=request.urgency,
                explicit_privacy="internal",
            )

        classification = self.router.classify_task(
            task_id=task_id,
            workspace=profile.workspace,
            intent=profile.intent.value,
            privacy=profile.privacy.value,
            urgency=profile.urgency,
            prompt=request.prompt,
            tags=list(set(profile.tags + (request.tags or []))),
        )

        route = self.router.route(classification)

        # Guardrail: prevent oversized prompts from being sent to cloud backends
        # Providers like OpenRouter may return "user_request_timeout" when the
        # request body is too large or slow to read. Provide a clear local error
        # and guidance rather than attempting a failing cloud call.
        if (
            route.backend == Backend.CLOUD
            and classification.estimated_tokens > self.MAX_SAFE_CLOUD_TOKENS
        ):
            latency = int((time.time() - start_time) * 1000)
            return AIResponse(
                success=False,
                error=(
                    "Request too large for cloud routing (~"
                    f"{classification.estimated_tokens} tokens). "
                    "Reduce input size or split into smaller chunks to avoid "
                    "provider timeouts (e.g., 'user_request_timeout')."
                ),
                model=route.model,
                provider=route.backend.value,
                backend=route.backend.value,
                route=route.to_dict(),
                classification=self._classification_to_dict(classification),
                latency_ms=latency,
            )

        # Policy enforcement
        is_valid, reason = self.policy.validate_route(
            task_id=task_id,
            privacy=classification.privacy.value,
            backend=route.backend.value,
            estimated_cost=route.estimated_cost,
            prompt=request.prompt,
        )

        if not is_valid:
            # Fallback to local when cloud path is blocked
            if route.backend == Backend.CLOUD:
                logger.info(
                    f"[LOCAL] Cloud route blocked ({reason}); falling back to local for {task_id}"
                )
                route = self.router.force_local_route(classification)
                is_valid, reason = self.policy.validate_route(
                    task_id=task_id,
                    privacy=classification.privacy.value,
                    backend=route.backend.value,
                    estimated_cost=route.estimated_cost,
                    prompt=request.prompt,
                )

            if not is_valid:
                latency = int((time.time() - start_time) * 1000)
                return AIResponse(
                    success=False,
                    error=reason or "Policy validation failed",
                    model=route.model,
                    provider=route.backend.value,
                    backend=route.backend.value,
                    route=route.to_dict(),
                    classification=self._classification_to_dict(classification),
                    latency_ms=latency,
                )

        # Execute route
        try:
            if route.backend == Backend.LOCAL:
                content = self.vibe.generate(
                    prompt=request.prompt,
                    system=request.system_prompt or None,
                    format="text",
                    stream=request.stream,
                    temperature=request.temperature,
                    max_tokens=request.max_tokens,
                )
                provider = "vibe"
            else:
                provider = self._select_provider(request.model) or "cloud"
                content = "Cloud routing not yet implemented; provider routing pending."
                if route.estimated_cost:
                    self.policy.record_cloud_cost(route.estimated_cost)
        except Exception as e:
            latency = int((time.time() - start_time) * 1000)
            logger.error(f"[LOCAL] AI generation failed for {task_id}: {e}")
            return AIResponse(
                success=False,
                error=str(e),
                model=route.model,
                provider=provider if "provider" in locals() else route.backend.value,
                backend=route.backend.value,
                route=route.to_dict(),
                classification=self._classification_to_dict(classification),
                latency_ms=latency,
            )

        # Update counters + logs
        latency = int((time.time() - start_time) * 1000)
        completion_tokens = len(content) // 4 if isinstance(content, str) else 0
        self.costs.requests_today += 1
        self.costs.total_requests += 1
        self._save_costs()
        self.router.record_route(route)

        return AIResponse(
            success=True,
            content=content,
            model=route.model,
            provider=provider,
            backend=route.backend.value,
            prompt_tokens=classification.estimated_tokens,
            completion_tokens=completion_tokens,
            total_tokens=classification.estimated_tokens + completion_tokens,
            cost=route.estimated_cost,
            route=route.to_dict(),
            classification=self._classification_to_dict(classification),
            latency_ms=latency,
        )

    def _select_provider(self, model: str) -> Optional[str]:
        """Select provider for model."""
        model_lower = model.lower()

        if "gemini" in model_lower and self.providers.get("gemini"):
            return "gemini"
        if "gpt" in model_lower and self.providers.get("openai"):
            return "openai"
        if "claude" in model_lower and self.providers.get("anthropic"):
            return "anthropic"
        if model_lower in ["llama2", "mistral"] and self.providers.get("ollama"):
            return "ollama"

        # Default to first available
        for provider, available in self.providers.items():
            if available:
                return provider

        return None

    def list_models(self) -> List[Dict[str, Any]]:
        """List available models."""
        models = []

        if self.providers.get("gemini"):
            models.extend(
                [
                    {"id": "gemini-1.5-flash", "provider": "gemini", "cost": "low"},
                    {"id": "gemini-pro", "provider": "gemini", "cost": "medium"},
                ]
            )

        if self.providers.get("openai"):
            models.extend(
                [
                    {"id": "gpt-3.5-turbo", "provider": "openai", "cost": "low"},
                    {"id": "gpt-4-turbo", "provider": "openai", "cost": "high"},
                ]
            )

        if self.providers.get("anthropic"):
            models.extend(
                [
                    {"id": "claude-3-haiku", "provider": "anthropic", "cost": "low"},
                    {
                        "id": "claude-3-sonnet",
                        "provider": "anthropic",
                        "cost": "medium",
                    },
                ]
            )

        if self.providers.get("ollama"):
            models.extend(
                [
                    {"id": "llama2", "provider": "ollama", "cost": "free"},
                    {"id": "mistral", "provider": "ollama", "cost": "free"},
                ]
            )

        # Always advertise local Devstral via Vibe
        models.insert(
            0,
            {
                "id": self._default_model(),
                "provider": "vibe",
                "cost": "free",
            },
        )

        return models


# Singleton instance
_gateway: Optional[AIGateway] = None


def get_ai_gateway() -> AIGateway:
    """Get AI gateway singleton."""
    global _gateway
    if _gateway is None:
        _gateway = AIGateway()
    return _gateway
