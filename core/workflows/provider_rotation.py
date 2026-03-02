from __future__ import annotations

from dataclasses import dataclass

from .contracts import ProviderHint
from .providers import MockTextProvider, ProviderBase, ProviderConfig


@dataclass(frozen=True)
class TierPolicy:
    tier_order: tuple[str, ...] = ("tier1_local", "tier2_cloud", "tier3_high")
    providers: dict[str, tuple[ProviderConfig, ...]] | None = None

    def __post_init__(self) -> None:
        if self.providers is None:
            object.__setattr__(self, "providers", {})


class ProviderRotation:
    def __init__(self, policy: TierPolicy):
        self.policy = policy

    def select_provider(self, tier: str, hint: ProviderHint) -> ProviderBase:
        configs = (self.policy.providers or {}).get(tier, ())
        if not configs:
            return MockTextProvider(ProviderConfig(provider_id=f"mock:{tier}", tier=tier))
        for config in configs:
            if self._compatible(config, hint):
                return MockTextProvider(config)
        return MockTextProvider(configs[0])

    def next_tier(self, current_tier: str) -> str | None:
        try:
            idx = self.policy.tier_order.index(current_tier)
        except ValueError:
            return self.policy.tier_order[0] if self.policy.tier_order else None
        if idx + 1 >= len(self.policy.tier_order):
            return None
        return self.policy.tier_order[idx + 1]

    def _compatible(self, config: ProviderConfig, hint: ProviderHint) -> bool:
        supports = set(config.supports)
        if hint.needs_image and "image" not in supports:
            return False
        if hint.needs_audio and "audio" not in supports:
            return False
        if hint.needs_video and "video" not in supports:
            return False
        return True


def default_policy() -> TierPolicy:
    return TierPolicy(
        providers={
            "tier1_local": (
                ProviderConfig(provider_id="ollama:local", tier="tier1_local", supports=["text"]),
            ),
            "tier2_cloud": (
                ProviderConfig(provider_id="ok-provider:standard", tier="tier2_cloud", supports=["text"]),
            ),
            "tier3_high": (
                ProviderConfig(provider_id="ok-provider:high", tier="tier3_high", supports=["text"]),
            ),
        }
    )
