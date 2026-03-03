from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any


@dataclass(frozen=True)
class BudgetCaps:
    max_cost_usd: float = 0.0
    max_tokens: int | None = None


@dataclass(frozen=True)
class ProviderHint:
    quality: str = "standard"
    needs_web: bool = False
    needs_image: bool = False
    needs_audio: bool = False
    needs_video: bool = False


@dataclass(frozen=True)
class PhaseSpec:
    name: str
    adapter: str
    prompt_name: str
    outputs: list[str]
    inputs: list[str] = field(default_factory=list)
    requires_user_approval: bool = True
    provider_hint: ProviderHint = field(default_factory=ProviderHint)
    budget: BudgetCaps = field(default_factory=BudgetCaps)


@dataclass(frozen=True)
class WorkflowSpec:
    workflow_id: str
    template_id: str
    project: str
    goal: str
    constraints: dict[str, Any]
    phases: list[PhaseSpec]
    outputs: list[str]
    created_at_iso: str
    purpose: str = ""
    inputs: dict[str, Any] = field(default_factory=dict)
    source_path: str | None = None


@dataclass
class PhaseRuntimeState:
    name: str
    status: str = "pending"
    tier: str = "tier1_local"
    retries_used: int = 0
    escalations_used: int = 0
    provider_id: str = ""
    last_error: str = ""
    last_run_at: str = ""
    approved_at: str = ""
    next_run_at: str = ""
    cost_usd: float = 0.0
    tokens: int = 0


@dataclass
class WorkflowRuntimeState:
    workflow_id: str
    status: str = "ready"
    current_phase_index: int = 0
    total_cost_usd: float = 0.0
    total_tokens: int = 0
    created_at: str = ""
    updated_at: str = ""
    next_run_at: str = ""
    phases: list[PhaseRuntimeState] = field(default_factory=list)


@dataclass(frozen=True)
class PhaseResult:
    ok: bool
    provider_id: str
    tier: str
    cost_usd: float
    tokens: int
    artifact_text: str
    errors: list[str] = field(default_factory=list)
