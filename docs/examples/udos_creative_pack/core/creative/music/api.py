from __future__ import annotations

from typing import Any, Dict, List
from ..contracts import ExecutionResult, PhaseSpec
from ..providers.base import ProviderBase


class MusicAdapterAdapter:
    name = "music"

    def estimate_tokens(self, phase: PhaseSpec, compiled_prompt: str) -> int:
        # crude heuristic: 1 token ~ 4 chars
        return max(256, len(compiled_prompt) // 4)

    def validate(self, phase: PhaseSpec, artifact_text: str) -> List[str]:
        errors: List[str] = []
        if not artifact_text.strip():
            errors.append("empty_output")
        # phase-specific checks can be added here
        return errors

    def execute(
        self,
        phase: PhaseSpec,
        compiled_prompt: str,
        provider: ProviderBase,
        context: Dict[str, Any],
    ) -> ExecutionResult:
        # Default: text execution
        max_tokens = phase.budget.max_tokens
        return provider.run_text(compiled_prompt, max_tokens=max_tokens)
