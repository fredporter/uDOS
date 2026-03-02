from __future__ import annotations

from typing import Any, Dict, List
from ..contracts import ExecutionResult, PhaseSpec
from ..providers.base import ProviderBase


class PackagingAdapter:
    name = "packaging"

    def estimate_tokens(self, phase: PhaseSpec, compiled_prompt: str) -> int:
        return 0

    def validate(self, phase: PhaseSpec, artifact_text: str) -> List[str]:
        # Packaging isn't validated via text; the build step should raise errors.
        return []

    def execute(
        self,
        phase: PhaseSpec,
        compiled_prompt: str,
        provider: ProviderBase,
        context: Dict[str, Any],
    ) -> ExecutionResult:
        # Stub: packaging steps run locally; return a log.
        return ExecutionResult(
            ok=True,
            provider_id="local:packaging",
            tier="local",
            cost_usd=0.0,
            tokens=0,
            artifact_text=compiled_prompt.strip() or "Packaging stub executed.",
            meta={"packaging": "stub"},
        )
