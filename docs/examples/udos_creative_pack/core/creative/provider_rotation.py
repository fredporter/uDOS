from __future__ import annotations

from dataclasses import dataclass
from typing import Dict, List, Optional, Tuple

from .contracts import ProviderHint
from .providers.base import ProviderBase, ProviderConfig, MockTextProvider


@dataclass(frozen=True)
class TierPolicy:
    """Defines the provider tiers and their selection order."""
    # Ordered tiers to try
    tier_order: Tuple[str, ...] = ("tier1_local", "tier2_cloud", "tier3_high")

    # Map tier -> list of provider configs
    providers: Dict[str, Tuple[ProviderConfig, ...]] = None  # type: ignore

    def __post_init__(self):
        if self.providers is None:
            object.__setattr__(self, "providers", {})


class ProviderRotation:
    """Deterministic provider selection + escalation."""

    def __init__(self, policy: TierPolicy):
        self.policy = policy

    def select_provider(self, tier: str, hint: ProviderHint) -> ProviderBase:
        configs = self.policy.providers.get(tier, ())
        if not configs:
            # Safe fallback: a mock provider for test/demo
            return MockTextProvider(ProviderConfig(provider_id=f"mock:{tier}", tier=tier))
        # Deterministic: pick first compatible provider in tier
        for cfg in configs:
            if self._is_compatible(cfg, hint):
                return self._instantiate(cfg)
        # If none compatible, pick first and let adapter handle capability mismatch
        return self._instantiate(configs[0])

    def next_tier(self, current_tier: str) -> Optional[str]:
        try:
            idx = self.policy.tier_order.index(current_tier)
        except ValueError:
            return self.policy.tier_order[0] if self.policy.tier_order else None
        if idx + 1 >= len(self.policy.tier_order):
            return None
        return self.policy.tier_order[idx + 1]

    def _is_compatible(self, cfg: ProviderConfig, hint: ProviderHint) -> bool:
        supports = set(cfg.supports)
        if hint.needs_image and "image" not in supports:
            return False
        if hint.needs_audio and "audio" not in supports:
            return False
        if hint.needs_video and "video" not in supports:
            return False
        # needs_web is not a capability here; it's a routing hint you can enforce later.
        return True

    def _instantiate(self, cfg: ProviderConfig) -> ProviderBase:
        # TODO: Replace with your real provider factory (OpenAI/Anthropic/Ollama/etc).
        # For now, return mock for text-only tiers.
        return MockTextProvider(cfg)


def default_policy() -> TierPolicy:
    """A starter policy; wire real configs later."""
    return TierPolicy(
        tier_order=("tier1_local", "tier2_cloud", "tier3_high"),
        providers={
            "tier1_local": (
                ProviderConfig(provider_id="ollama:local", tier="tier1_local", supports=["text"]),
            ),
            "tier2_cloud": (
                ProviderConfig(provider_id="cloud:standard", tier="tier2_cloud", supports=["text"]),
            ),
            "tier3_high": (
                ProviderConfig(provider_id="cloud:high", tier="tier3_high", supports=["text"]),
            ),
        },
    )
