from __future__ import annotations

from typing import Any, Dict, List
from ..contracts import ExecutionResult, PhaseSpec
from ..providers.base import ProviderBase


class ImageAdapter:
    name = "image"

    def estimate_tokens(self, phase: PhaseSpec, compiled_prompt: str) -> int:
        return max(128, len(compiled_prompt) // 5)

    def validate(self, phase: PhaseSpec, artifact_text: str) -> List[str]:
        # In v1, we store image prompts/metadata as markdown or JSON.
        errors: List[str] = []
        if not artifact_text.strip():
            errors.append("empty_output")
        return errors

    def execute(
        self,
        phase: PhaseSpec,
        compiled_prompt: str,
        provider: ProviderBase,
        context: Dict[str, Any],
    ) -> ExecutionResult:
        # Prefer image capability; fall back to text prompt engineering.
        if "image" in getattr(provider, "supports", set()):
            return provider.run_image(compiled_prompt)
        return provider.run_text(compiled_prompt, max_tokens=phase.budget.max_tokens)
