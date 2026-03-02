from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional
from ..contracts import ExecutionResult


@dataclass
class ProviderConfig:
    provider_id: str
    tier: str
    supports: List[str] = field(default_factory=lambda: ["text"])  # text|image|audio|video


class ProviderError(RuntimeError):
    pass


class ProviderBase:
    def __init__(self, config: ProviderConfig):
        self.provider_id = config.provider_id
        self.tier = config.tier
        self.supports = set(config.supports)

    def run_text(self, prompt: str, max_tokens: Optional[int] = None) -> ExecutionResult:
        raise NotImplementedError

    def run_image(self, prompt: str, **kwargs) -> ExecutionResult:
        raise NotImplementedError

    def run_audio(self, prompt: str, **kwargs) -> ExecutionResult:
        raise NotImplementedError

    def run_video(self, prompt: str, **kwargs) -> ExecutionResult:
        raise NotImplementedError


class MockTextProvider(ProviderBase):
    """A deterministic mock provider for local testing."""
    def run_text(self, prompt: str, max_tokens: Optional[int] = None) -> ExecutionResult:
        # This mock just echoes a shortened prompt section as output.
        out = prompt.strip()
        if len(out) > 2500:
            out = out[:2500] + "\n\n[TRUNCATED BY MOCK PROVIDER]"
        tokens = min(len(out) // 4, max_tokens or 10_000)
        return ExecutionResult(
            ok=True,
            provider_id=self.provider_id,
            tier=self.tier,
            cost_usd=0.0,
            tokens=tokens,
            artifact_text=out,
            meta={"mock": True},
        )
