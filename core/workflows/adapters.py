from __future__ import annotations

from typing import Any

from .contracts import PhaseResult, PhaseSpec
from .providers import ProviderBase


class TextAdapter:
    def __init__(self, name: str):
        self.name = name

    def execute(
        self,
        phase: PhaseSpec,
        compiled_prompt: str,
        provider: ProviderBase,
        context: dict[str, Any],
    ) -> PhaseResult:
        return provider.run_text(compiled_prompt, max_tokens=phase.budget.max_tokens)

    def validate(self, phase: PhaseSpec, artifact_text: str) -> list[str]:
        return [] if artifact_text.strip() else ["empty_output"]


class ImageAdapter(TextAdapter):
    def execute(
        self,
        phase: PhaseSpec,
        compiled_prompt: str,
        provider: ProviderBase,
        context: dict[str, Any],
    ) -> PhaseResult:
        if "image" in provider.supports:
            return provider.run_image(compiled_prompt)
        return provider.run_text(compiled_prompt, max_tokens=phase.budget.max_tokens)


def default_registry() -> dict[str, object]:
    return {
        "writing": TextAdapter("writing"),
        "video": TextAdapter("video"),
        "music": TextAdapter("music"),
        "packaging": TextAdapter("packaging"),
        "image": ImageAdapter("image"),
    }
