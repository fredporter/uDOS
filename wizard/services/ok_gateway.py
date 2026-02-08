"""
OK Gateway - LLM Access for User Devices
=========================================

Provides OK/LLM capabilities for user devices through the Wizard Server.
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

from wizard.services.logging_api import get_logger
from wizard.services.quota_tracker import (
    APIProvider as QuotaAPIProvider,
    get_quota_tracker,
    record_usage,
)
from wizard.security.key_store import get_wizard_key
from .model_router import ModelRouter, Backend
from .policy_enforcer import PolicyEnforcer
from .vibe_service import VibeService
from .task_classifier import TaskClassifier

logger = get_logger("wizard", category="ok-gateway", name="ok-gateway")

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
class OKRequest:
    """AI request structure."""

    prompt: str
    model: str = ""
    system_prompt: str = ""
    max_tokens: int = 1024
    temperature: Optional[float] = None
    stream: bool = False
    mode: Optional[str] = None
    force_cloud: bool = False
    cloud_sanity: bool = False
    allow_cloud: bool = True
    offline_required: bool = False
    ghost_mode: bool = False
    task_hint: Optional[str] = None

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
    sanity_check: Optional[Dict[str, Any]] = None

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

# Wizard AI mode presets (applied when mode is set and no explicit overrides)
MODE_PRESETS: Dict[str, Dict[str, Any]] = {
    "conversation": {
        "temperature": 0.7,
        "system_prompt": (
            "You are a helpful conversational assistant for uDOS. "
            "Be concise, friendly, and practical. Ask clarifying questions "
            "when requirements are ambiguous."
        ),
    },
    "creative": {
        "temperature": 1.0,
        "system_prompt": (
            "You are a creative assistant for uDOS. Generate multiple options "
            "and bold ideas while staying grounded in project context."
        ),
    },
    "code": {
        "temperature": 0.2,
        "system_prompt": (
            "You are a precise coding assistant for uDOS. Prefer deterministic, "
            "actionable responses and avoid speculation."
        ),
    },
}


class OKGateway:
    """
    OK gateway service for uDOS.

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
        """Initialize OK gateway."""
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
        self.quota_tracker = get_quota_tracker()

        # Routing + policy stack
        self.classifier = TaskClassifier()
        self.router = ModelRouter()
        self.policy = PolicyEnforcer()
        self.vibe = VibeService()
        self.cloud_sanity_enabled = self._load_cloud_sanity_flag()

    def _load_cloud_sanity_flag(self) -> bool:
        """Read cloud sanity toggle from wizard config."""
        try:
            config_path = Path(__file__).parent.parent / "config" / "wizard.json"
            if config_path.exists():
                data = json.loads(config_path.read_text())
                return bool(data.get("ok_cloud_sanity_enabled", True))
        except Exception:
            pass
        return True

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
            except Exception:
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

    def _default_model_for_mode(self, mode: Optional[str]) -> str:
        """Return a default local model for a given mode."""
        mode_key = (mode or "").strip().lower()
        if mode_key in {"conversation", "creative"}:
            return "mistral-small2"
        if mode_key == "code":
            return "devstral-small-2"
        return self._default_model()

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

    def _get_cache_key(self, request: OKRequest) -> str:
        """Generate cache key for request."""
        data = f"{request.model}:{request.prompt}:{request.system_prompt}"
        return hashlib.md5(data.encode()).hexdigest()

    def _check_cache(self, request: OKRequest) -> Optional[AIResponse]:
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
            except Exception:
                pass

        return None

    def _save_cache(self, request: OKRequest, response: AIResponse):
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

    def _apply_mode_preset(self, request: OKRequest) -> None:
        """Apply Wizard mode presets to an AI request (conversation/creative/etc)."""
        if not request.mode:
            return
        mode_key = str(request.mode).strip().lower()
        preset = MODE_PRESETS.get(mode_key)
        if not preset:
            return
        if not request.system_prompt:
            request.system_prompt = preset.get("system_prompt", "")
        if request.temperature is None:
            request.temperature = preset.get("temperature", None)

    def _evaluate_vibe_router_contract(
        self,
        request: OKRequest,
        classification,
    ) -> Dict[str, Any]:
        """Enforce VIBE-ROUTER-CONTRACT rules and return contract decision."""
        tags = set(request.tags or [])
        ghost_mode = bool(request.ghost_mode) or "ghost_mode" in tags or "ghost" in tags
        offline_required = bool(request.offline_required) or "offline_required" in tags or "offline" in tags
        privacy = (request.privacy or "internal").lower()

        intent_raw = getattr(classification, "intent", None)
        intent_value = intent_raw.value if intent_raw else "code"
        if intent_value in {"design"}:
            contract_intent = "design"
        elif intent_value in {"docs"}:
            contract_intent = "chat"
        else:
            contract_intent = "code"

        model_map = {
            "chat": "mistral-small",
            "design": "mistral-large",
            "code": "devstral-small-2",
        }
        model = model_map.get(contract_intent, self._default_model_for_mode(request.mode))

        online_allowed = True
        reason = "policy_allows_online"
        provider = "wizard"
        if ghost_mode:
            online_allowed = False
            provider = "ollama"
            reason = "ghost_mode"
        elif privacy == "private" or offline_required:
            online_allowed = False
            provider = "ollama"
            reason = "offline_required_or_private"

        return {
            "intent": contract_intent,
            "mode": (request.mode or "conversation"),
            "privacy": privacy,
            "provider": provider,
            "model": model,
            "online_allowed": online_allowed,
            "ghost_mode": ghost_mode,
            "offline_required": offline_required,
            "reason": reason,
        }

    async def complete(self, request: OKRequest, device_id: str) -> AIResponse:
        """Complete an AI request via local-first routing."""
        start_time = time.time()

        # Normalize request
        task_id = request.task_id or self._generate_task_id(device_id)
        request.task_id = task_id
        if not request.model:
            request.model = self._default_model_for_mode(request.mode)
        self._apply_mode_preset(request)
        if request.temperature is None:
            request.temperature = 0.7

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
        allow_cloud = bool(request.allow_cloud)
        if request.workspace == "dev" and not request.force_cloud:
            allow_cloud = False
            request.cloud_sanity = False
        # Force local-first unless explicitly forced cloud
        if not request.force_cloud:
            route = self.router.force_local_route(classification)

        contract = self._evaluate_vibe_router_contract(request, classification)
        if not contract.get("online_allowed", True):
            allow_cloud = False
            request.cloud_sanity = False
            if request.force_cloud:
                latency = int((time.time() - start_time) * 1000)
                return AIResponse(
                    success=False,
                    error="Vibe router contract blocked cloud routing",
                    model=contract.get("model") or route.model,
                    provider=contract.get("provider") or route.backend.value,
                    backend=Backend.LOCAL.value,
                    route=route.to_dict(),
                    classification=self._classification_to_dict(classification),
                    latency_ms=latency,
                )
            route = self.router.force_local_route(classification)

        contract_model = contract.get("model")
        if contract_model:
            route.model = contract_model
            if not request.model:
                request.model = contract_model

        estimated_cost = route.estimated_cost if allow_cloud and (request.force_cloud or route.backend == Backend.CLOUD) else 0.0
        try:
            logger.event(
                "info",
                "ok.gateway.route",
                "Vibe router contract decision",
                ctx={
                    "intent": contract.get("intent"),
                    "mode": contract.get("mode"),
                    "privacy": contract.get("privacy"),
                    "provider": contract.get("provider"),
                    "model": contract.get("model"),
                    "online_allowed": contract.get("online_allowed"),
                    "ghost_mode": contract.get("ghost_mode"),
                    "offline_required": contract.get("offline_required"),
                    "force_cloud": bool(request.force_cloud),
                    "allow_cloud": bool(allow_cloud),
                    "estimated_cost": estimated_cost,
                    "reason": contract.get("reason"),
                },
            )
        except Exception:
            pass

        # Guardrail: prevent oversized prompts from being sent to cloud backends
        # Providers like OpenRouter may return "user_request_timeout" when the
        # request body is too large or slow to read. Provide a clear local error
        # and guidance rather than attempting a failing cloud call.
        if request.force_cloud and allow_cloud:
            if classification.estimated_tokens > self.MAX_SAFE_CLOUD_TOKENS:
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
                    backend=Backend.CLOUD.value,
                    route=route.to_dict(),
                    classification=self._classification_to_dict(classification),
                    latency_ms=latency,
                )

        # Policy enforcement
        is_valid, reason = self.policy.validate_route(
            task_id=task_id,
            privacy=classification.privacy.value,
            backend=route.backend.value if not request.force_cloud else Backend.CLOUD.value,
            estimated_cost=route.estimated_cost,
            prompt=request.prompt,
        )

        if not is_valid:
            if request.force_cloud:
                latency = int((time.time() - start_time) * 1000)
                return AIResponse(
                    success=False,
                    error=reason or "Policy validation failed",
                    model=route.model,
                    provider=Backend.CLOUD.value,
                    backend=Backend.CLOUD.value,
                    route=route.to_dict(),
                    classification=self._classification_to_dict(classification),
                    latency_ms=latency,
                )
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

        # Determine provider for quota tracking
        provider_name = (
            "vibe"
            if route.backend == Backend.LOCAL
            else self._select_provider(request.model) or route.backend.value
        )
        quota_provider = self._map_to_quota_provider(provider_name)
        if quota_provider and not self.quota_tracker.can_request(
            quota_provider, classification.estimated_tokens
        ):
            latency = int((time.time() - start_time) * 1000)
            return AIResponse(
                success=False,
                error=f"Quota limits hit for {provider_name}; request refused",
                model=route.model,
                provider=provider_name,
                backend=route.backend.value,
                route=route.to_dict(),
                classification=self._classification_to_dict(classification),
                latency_ms=latency,
            )

        # Execute route
        model_used = route.model
        backend_value = route.backend.value
        try:
            if request.force_cloud and allow_cloud:
                cloud_response = self._run_cloud_mistral(request.prompt)
                if not cloud_response.success:
                    raise RuntimeError(cloud_response.error or "Cloud request failed")
                content = cloud_response.content
                model_used = cloud_response.model or model_used
                provider = cloud_response.provider or provider_name
                backend_value = Backend.CLOUD.value
            else:
                content = self.vibe.generate(
                    prompt=request.prompt,
                    system=request.system_prompt or None,
                    format="text",
                    stream=request.stream,
                    temperature=request.temperature,
                    max_tokens=request.max_tokens,
                )
                provider = "vibe"
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

        if quota_provider:
            record_usage(
                provider_name,
                input_tokens=classification.estimated_tokens,
                output_tokens=completion_tokens,
                cost=route.estimated_cost or 0.0,
            )

        response = AIResponse(
            success=True,
            content=content,
            model=model_used,
            provider=provider,
            backend=backend_value,
            prompt_tokens=classification.estimated_tokens,
            completion_tokens=completion_tokens,
            total_tokens=classification.estimated_tokens + completion_tokens,
            cost=route.estimated_cost,
            route=route.to_dict(),
            classification=self._classification_to_dict(classification),
            latency_ms=latency,
        )

        if not request.force_cloud and allow_cloud and self.cloud_sanity_enabled:
            if request.cloud_sanity or self._should_sanity_check(response.content):
                is_valid, reason = self.policy.validate_route(
                    task_id=task_id,
                    privacy=classification.privacy.value,
                    backend=Backend.CLOUD.value,
                    estimated_cost=route.estimated_cost or 0.0,
                    prompt=request.prompt,
                )
                if is_valid:
                    sanity = self._run_cloud_mistral(request.prompt)
                    if sanity.success:
                        response.sanity_check = {
                            "model": sanity.model,
                            "provider": sanity.provider,
                            "content": sanity.content,
                        }
                else:
                    logger.info(
                        f"[LOCAL] Cloud sanity check skipped ({reason}) for {task_id}"
                    )

        return response

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

    def _cloud_model(self) -> str:
        """Return default cloud model for sanity checks."""
        try:
            config_path = Path(__file__).parent.parent.parent / "core" / "config" / "ok_modes.json"
            if config_path.exists():
                data = json.loads(config_path.read_text())
                mode = (data.get("modes") or {}).get("onvibe", {})
                model = mode.get("default_model")
                if model:
                    return model
        except Exception:
            pass
        return "mistral-small-latest"

    def _should_sanity_check(self, response: str) -> bool:
        """Heuristic: request cloud sanity check when local confidence is low."""
        text = (response or "").strip()
        if len(text) < 160:
            return True
        lowered = text.lower()
        uncertain_phrases = [
            "i'm not sure",
            "i am not sure",
            "not sure",
            "unsure",
            "i think",
            "maybe",
            "might be",
            "cannot",
            "can't",
            "unable",
            "no access",
            "need more information",
            "not enough context",
            "as an ai",
        ]
        return any(phrase in lowered for phrase in uncertain_phrases)

    def _run_cloud_mistral(self, prompt: str) -> AIResponse:
        """Run cloud sanity check via Mistral API."""
        from wizard.services.mistral_api import MistralAPI

        model = self._cloud_model()
        client = MistralAPI()
        if not client.available():
            return AIResponse(success=False, error="Mistral API key missing", backend=Backend.CLOUD.value)

        content = client.chat(prompt, model=model)
        completion_tokens = len(content) // 4 if isinstance(content, str) else 0
        return AIResponse(
            success=True,
            content=content,
            model=model,
            provider="mistral",
            backend=Backend.CLOUD.value,
            completion_tokens=completion_tokens,
        )

    def _map_to_quota_provider(self, provider_name: str) -> Optional[QuotaAPIProvider]:
        """Map gateway provider name to quota tracker enum."""
        if not provider_name:
            return None
        try:
            return QuotaAPIProvider(provider_name)
        except ValueError:
            fallback = {
                "vibe": QuotaAPIProvider.OFFLINE,
                "local": QuotaAPIProvider.OFFLINE,
                "cloud": QuotaAPIProvider.OPENAI,
                "openrouter": QuotaAPIProvider.OPENAI,
                "ollama": QuotaAPIProvider.OLLAMA,
            }
            return fallback.get(provider_name.lower())

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
_gateway: Optional[OKGateway] = None


def get_ok_gateway() -> OKGateway:
    """Get OK gateway singleton."""
    global _gateway
    if _gateway is None:
        _gateway = OKGateway()
    return _gateway
