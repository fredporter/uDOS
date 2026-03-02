from __future__ import annotations

from pathlib import Path

from .adapters import default_registry
from .artifacts import WorkflowArtifactStore
from .contracts import PhaseResult, PhaseSpec, WorkflowSpec
from .prompting import PromptCompiler
from .provider_rotation import ProviderRotation, default_policy


class PhaseEngine:
    def __init__(self, vault_root: Path, prompt_root: Path):
        self.store = WorkflowArtifactStore(vault_root=vault_root)
        self.compiler = PromptCompiler(prompt_root=prompt_root)
        self.registry = default_registry()
        self.rotation = ProviderRotation(default_policy())

    def run_phase(self, workflow: WorkflowSpec, phase: PhaseSpec, tier: str) -> PhaseResult:
        adapter = self.registry[phase.adapter]
        inputs: dict[str, str] = {}
        for input_path in phase.inputs:
            inputs[input_path] = self.store.read_text(workflow.workflow_id, input_path)
        template = self.compiler.load(phase.adapter, phase.prompt_name)
        variables: dict[str, object] = {
            "goal": workflow.goal,
            "constraints": workflow.constraints,
            "phase": phase.name,
            "inputs": inputs,
            **workflow.constraints,
        }
        compiled = self.compiler.compile(template, variables)
        provider = self.rotation.select_provider(tier=tier, hint=phase.provider_hint)
        result = adapter.execute(phase, compiled, provider, variables)
        errors = adapter.validate(phase, result.artifact_text)
        if errors:
            return PhaseResult(
                ok=False,
                provider_id=result.provider_id,
                tier=result.tier,
                cost_usd=result.cost_usd,
                tokens=result.tokens,
                artifact_text=result.artifact_text,
                errors=errors,
            )
        return result
