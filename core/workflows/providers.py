from __future__ import annotations

from dataclasses import dataclass, field

from .contracts import PhaseResult


@dataclass(frozen=True)
class ProviderConfig:
    provider_id: str
    tier: str
    supports: list[str] = field(default_factory=lambda: ["text"])


class ProviderBase:
    def __init__(self, config: ProviderConfig):
        self.provider_id = config.provider_id
        self.tier = config.tier
        self.supports = set(config.supports)

    def run_text(self, prompt: str, max_tokens: int | None = None) -> PhaseResult:
        raise NotImplementedError

    def run_image(self, prompt: str) -> PhaseResult:
        raise NotImplementedError

    def run_audio(self, prompt: str) -> PhaseResult:
        raise NotImplementedError

    def run_video(self, prompt: str) -> PhaseResult:
        raise NotImplementedError


class MockTextProvider(ProviderBase):
    def run_text(self, prompt: str, max_tokens: int | None = None) -> PhaseResult:
        text = prompt.strip()
        if len(text) > 2500:
            text = text[:2500] + "\n\n[TRUNCATED BY MOCK PROVIDER]"
        tokens = min(max(1, len(text) // 4), max_tokens or 10000)
        return PhaseResult(
            ok=True,
            provider_id=self.provider_id,
            tier=self.tier,
            cost_usd=0.0,
            tokens=tokens,
            artifact_text=text,
            errors=[],
        )
