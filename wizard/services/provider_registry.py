"""Provider Registry - Multi-Provider Routing and Management

Manages provider capabilities, routing, fallback chains, and performance telemetry
for Vibe-CLI OK Agent interactions.

This extends core/services/provider_registry.py with Vibe-specific multi-provider
routing logic (Mistral, OpenAI, Anthropic, Gemini).

Architecture Rules (from vibe/AGENTS.md):
- Capability-based routing across supported providers
- Capability-based selection (match task to provider strengths)
- Graceful fallback on provider failure
- Performance telemetry for routing decisions
- Provider preference respect (user overrides)

Usage:
    from wizard.services.provider_registry import VibeProviderRegistry

    registry = VibeProviderRegistry()
    # Get provider for task
    provider, model = registry.select_provider_for_task("code")

    # Multi-provider fallback
    chain = registry.get_fallback_chain(mode="code")

Version: 1.0.0
Release baseline: v1.5 contributor routing
"""

from __future__ import annotations

from dataclasses import dataclass
from enum import Enum
import logging
import time
from typing import Any

from vibe.core.provider_engine import ProviderStatus, ProviderType

logger = logging.getLogger("vibe.provider-registry")


class TaskMode(str, Enum):
    """Task modes for capability-based routing."""

    CODE = "code"  # Code generation, refactoring, analysis
    CONVERSATION = "conversation"  # General chat, Q&A
    CREATIVE = "creative"  # Creative writing, brainstorming
    ANALYSIS = "analysis"  # Data analysis, summarization
    COMMAND = "command"  # ucode command generation


@dataclass
class ProviderCapabilities:
    """Provider capability declaration."""

    provider_type: ProviderType
    models: list[str]
    strengths: list[TaskMode]
    cost: str  # "free", "low", "medium", "high"
    latency: str  # "fast", "medium", "slow"
    context_window: int = 8192
    supports_streaming: bool = True
    local: bool = False


@dataclass
class ProviderConfig:
    """Provider configuration."""

    provider_type: ProviderType
    enabled: bool = True
    endpoint: str | None = None
    api_key: str | None = None
    default_model: str | None = None
    capabilities: ProviderCapabilities | None = None
    priority: int = 0  # Lower = higher priority


@dataclass
class ProviderTelemetry:
    """Provider performance telemetry."""

    provider_type: ProviderType
    total_calls: int = 0
    successful_calls: int = 0
    failed_calls: int = 0
    timeout_calls: int = 0
    total_latency: float = 0.0
    last_call_time: float = 0.0
    last_status: ProviderStatus = ProviderStatus.UNAVAILABLE

    @property
    def success_rate(self) -> float:
        """Calculate success rate."""
        if self.total_calls == 0:
            return 0.0
        return self.successful_calls / self.total_calls

    @property
    def avg_latency(self) -> float:
        """Calculate average latency."""
        if self.successful_calls == 0:
            return 0.0
        return self.total_latency / self.successful_calls


class VibeProviderRegistry:
    """Multi-provider registry with capability-based routing."""

    def __init__(self):
        """Initialize provider registry."""
        self.providers: dict[ProviderType, ProviderConfig] = {}
        self.telemetry: dict[ProviderType, ProviderTelemetry] = {}
        self.logger = logger

        # Initialize telemetry for all provider types
        for ptype in ProviderType:
            self.telemetry[ptype] = ProviderTelemetry(provider_type=ptype)

    def register_provider(
        self,
        provider_type: ProviderType,
        endpoint: str | None = None,
        api_key: str | None = None,
        default_model: str | None = None,
        priority: int = 0,
    ) -> None:
        """Register a provider.

        Args:
            provider_type: Provider type enum
            endpoint: Provider endpoint URL (for local/custom)
            api_key: API key (for cloud providers)
            default_model: Default model name
            priority: Priority (lower = higher, 0 = highest)
        """
        capabilities = self._get_default_capabilities(provider_type)

        config = ProviderConfig(
            provider_type=provider_type,
            enabled=True,
            endpoint=endpoint,
            api_key=api_key,
            default_model=default_model or capabilities.models[0],
            capabilities=capabilities,
            priority=priority,
        )

        self.providers[provider_type] = config
        self.logger.info(
            f"Registered provider: {provider_type.value} (priority={priority})"
        )

    def _get_default_capabilities(
        self, provider_type: ProviderType
    ) -> ProviderCapabilities:
        """Get default capabilities for provider type.

        Args:
            provider_type: Provider type

        Returns:
            ProviderCapabilities with sensible defaults
        """
        if provider_type == ProviderType.MISTRAL:
            return ProviderCapabilities(
                provider_type=provider_type,
                models=["mistral-small-latest", "mistral-large-latest"],
                strengths=[TaskMode.CODE, TaskMode.CONVERSATION, TaskMode.CREATIVE],
                cost="medium",
                latency="fast",
                context_window=32000,
                supports_streaming=True,
                local=False,
            )
        elif provider_type == ProviderType.OPENAI:
            return ProviderCapabilities(
                provider_type=provider_type,
                models=["gpt-4", "gpt-3.5-turbo"],
                strengths=[TaskMode.CONVERSATION, TaskMode.CREATIVE, TaskMode.ANALYSIS],
                cost="medium",
                latency="medium",
                context_window=8192,
                supports_streaming=True,
                local=False,
            )
        elif provider_type == ProviderType.ANTHROPIC:
            return ProviderCapabilities(
                provider_type=provider_type,
                models=["claude-3-5-sonnet-latest", "claude-3-opus-latest"],
                strengths=[TaskMode.CODE, TaskMode.ANALYSIS, TaskMode.CREATIVE],
                cost="high",
                latency="medium",
                context_window=200000,
                supports_streaming=True,
                local=False,
            )
        elif provider_type == ProviderType.GEMINI:
            return ProviderCapabilities(
                provider_type=provider_type,
                models=["gemini-1.5-pro", "gemini-1.5-flash"],
                strengths=[TaskMode.CONVERSATION, TaskMode.ANALYSIS],
                cost="low",
                latency="fast",
                context_window=128000,
                supports_streaming=True,
                local=False,
            )
        else:
            # Generic fallback
            return ProviderCapabilities(
                provider_type=provider_type,
                models=["default"],
                strengths=[],
                cost="unknown",
                latency="unknown",
                context_window=4096,
                supports_streaming=False,
                local=False,
            )

    def select_provider_for_task(
        self, mode: str, prefer_local: bool = True, user_override: str | None = None
    ) -> tuple[ProviderType, str]:
        """Select best provider for task mode.

        Args:
            mode: Task mode (code, conversation, etc.)
            prefer_local: Prefer local providers when available
            user_override: User-specified provider override

        Returns:
            Tuple of (provider_type, model_name)

        Raises:
            RuntimeError: If no suitable provider available
        """
        task_mode = TaskMode(mode.lower()) if mode else TaskMode.CONVERSATION

        # User override takes precedence
        if user_override:
            try:
                override_type = ProviderType(user_override.lower())
                if override_type in self.providers:
                    config = self.providers[override_type]
                    return (override_type, config.default_model)
            except ValueError:
                self.logger.warning(f"Invalid provider override: {user_override}")

        # Local-first routing
        if prefer_local:
            local_providers = [
                (ptype, config)
                for ptype, config in self.providers.items()
                if config.enabled and config.capabilities and config.capabilities.local
            ]
            if local_providers:
                # Prefer local provider with task capability
                for ptype, config in local_providers:
                    if (
                        config.capabilities
                        and task_mode in config.capabilities.strengths
                    ):
                        return (ptype, config.default_model)

                # Fallback to any local provider
                ptype, config = local_providers[0]
                return (ptype, config.default_model)

        # Capability-based selection
        candidates = []
        for ptype, config in self.providers.items():
            if not config.enabled or not config.capabilities:
                continue

            if task_mode in config.capabilities.strengths:
                # Score based on success rate and latency
                telemetry = self.telemetry.get(ptype)
                score = 0.0

                if telemetry:
                    # Favor high success rate
                    score += telemetry.success_rate * 100

                    # Penalize high latency
                    if telemetry.avg_latency > 0:
                        score -= telemetry.avg_latency

                # Priority adjustment (lower priority = higher score)
                score += (10 - config.priority) * 10

                candidates.append((score, ptype, config))

        if not candidates:
            raise RuntimeError(
                f"No suitable provider for task mode: {mode}. "
                f"Available: {list(self.providers.keys())}"
            )

        # Select highest scoring provider
        candidates.sort(key=lambda x: x[0], reverse=True)
        _, best_provider, best_config = candidates[0]

        return (best_provider, best_config.default_model)

    def get_fallback_chain(
        self, mode: str, exclude: list[ProviderType] | None = None
    ) -> list[tuple[ProviderType, str]]:
        """Get fallback chain for task mode.

        Args:
            mode: Task mode
            exclude: Provider types to exclude from chain

        Returns:
            Ordered list of (provider_type, model) tuples
        """
        exclude = exclude or []
        task_mode = TaskMode(mode.lower()) if mode else TaskMode.CONVERSATION

        chain = []

        # Sort by priority (lower = higher)
        sorted_providers = sorted(
            [
                (config.priority, ptype, config)
                for ptype, config in self.providers.items()
                if config.enabled and ptype not in exclude
            ],
            key=lambda x: x[0],
        )

        for _, ptype, config in sorted_providers:
            chain.append((ptype, config.default_model))

        return chain

    def record_call(
        self,
        provider_type: ProviderType,
        success: bool,
        latency: float,
        status: ProviderStatus,
    ) -> None:
        """Record provider call for telemetry.

        Args:
            provider_type: Provider type
            success: Whether call succeeded
            latency: Call latency in seconds
            status: Provider status result
        """
        telemetry = self.telemetry.get(provider_type)
        if not telemetry:
            return

        telemetry.total_calls += 1
        telemetry.last_call_time = time.time()
        telemetry.last_status = status

        if success:
            telemetry.successful_calls += 1
            telemetry.total_latency += latency
        elif status == ProviderStatus.TIMEOUT:
            telemetry.timeout_calls += 1
        else:
            telemetry.failed_calls += 1

        self.logger.debug(
            f"Recorded call: {provider_type.value} success={success} latency={latency:.2f}s"
        )

    def get_telemetry(self, provider_type: ProviderType) -> ProviderTelemetry:
        """Get telemetry for provider.

        Args:
            provider_type: Provider type

        Returns:
            ProviderTelemetry object
        """
        return self.telemetry.get(provider_type, ProviderTelemetry(provider_type))

    def get_status(self) -> dict[str, Any]:
        """Get registry status.

        Returns:
            Dict with provider status and telemetry
        """
        return {
            "total_providers": len(self.providers),
            "enabled_providers": sum(
                1 for config in self.providers.values() if config.enabled
            ),
            "providers": {
                ptype.value: {
                    "enabled": config.enabled,
                    "model": config.default_model,
                    "priority": config.priority,
                    "local": config.capabilities.local
                    if config.capabilities
                    else False,
                    "telemetry": {
                        "total_calls": self.telemetry[ptype].total_calls,
                        "success_rate": f"{self.telemetry[ptype].success_rate:.2%}",
                        "avg_latency": f"{self.telemetry[ptype].avg_latency:.2f}s",
                    },
                }
                for ptype, config in self.providers.items()
            },
        }


# Global registry instance
_registry: VibeProviderRegistry | None = None


def get_provider_registry() -> VibeProviderRegistry:
    """Get or create global provider registry."""
    global _registry
    if _registry is None:
        _registry = VibeProviderRegistry()
    return _registry
