from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional, Protocol


@dataclass(frozen=True)
class BudgetCaps:
    """Budget caps for a single phase."""
    max_cost_usd: float = 0.0
    max_tokens: Optional[int] = None


@dataclass(frozen=True)
class ProviderHint:
    """Hints that help provider selection."""
    needs_web: bool = False
    needs_image: bool = False
    needs_audio: bool = False
    needs_video: bool = False
    quality: str = "standard"  # "draft" | "standard" | "high"


@dataclass
class PhaseSpec:
    name: str
    adapter: str  # writing|image|video|music|packaging
    prompt_name: str  # filename without extension in adapter prompts/
    inputs: List[str] = field(default_factory=list)  # artifact relpaths
    outputs: List[str] = field(default_factory=list)  # artifact relpaths
    requires_user_approval: bool = True
    provider_hint: ProviderHint = field(default_factory=ProviderHint)
    budget: BudgetCaps = field(default_factory=BudgetCaps)


@dataclass
class WorkflowSpec:
    workflow_id: str
    goal: str
    constraints: Dict[str, Any] = field(default_factory=dict)
    phases: List[PhaseSpec] = field(default_factory=list)
    created_at_iso: str = ""


@dataclass
class ExecutionResult:
    ok: bool
    provider_id: str
    tier: str
    cost_usd: float
    tokens: int
    artifact_text: str
    errors: List[str] = field(default_factory=list)
    meta: Dict[str, Any] = field(default_factory=dict)


class CreativeAdapter(Protocol):
    name: str

    def execute(
        self,
        phase: PhaseSpec,
        compiled_prompt: str,
        provider: "Provider",
        context: Dict[str, Any],
    ) -> ExecutionResult:
        ...

    def validate(self, phase: PhaseSpec, artifact_text: str) -> List[str]:
        """Return list of validation errors (empty => valid)."""
        ...

    def estimate_tokens(self, phase: PhaseSpec, compiled_prompt: str) -> int:
        ...


class Provider(Protocol):
    provider_id: str
    tier: str

    def run_text(self, prompt: str, max_tokens: Optional[int] = None) -> ExecutionResult:
        ...

    # These are optional; some tiers won't implement them
    def run_image(self, prompt: str, **kwargs) -> ExecutionResult:
        ...

    def run_audio(self, prompt: str, **kwargs) -> ExecutionResult:
        ...

    def run_video(self, prompt: str, **kwargs) -> ExecutionResult:
        ...
