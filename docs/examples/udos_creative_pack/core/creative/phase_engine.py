from __future__ import annotations

from dataclasses import asdict
from typing import Any, Dict, List, Tuple
from pathlib import Path

from .contracts import WorkflowSpec, PhaseSpec
from .artifacts import ArtifactStore
from .prompting import PromptCompiler
from .registry import default_registry
from .provider_rotation import ProviderRotation, default_policy
from .escalation import EscalationRule, EscalationState, summarize_errors


class PhaseEngine:
    def __init__(self, vault_root: Path, prompt_root: Path):
        self.store = ArtifactStore(vault_root=vault_root)
        self.compiler = PromptCompiler(prompt_root=prompt_root)
        self.registry = default_registry()
        self.rotation = ProviderRotation(default_policy())

    def run_phase(self, wf: WorkflowSpec, phase: PhaseSpec, tier: str) -> Tuple[bool, str]:
        adapter = self.registry.get(phase.adapter)
        if adapter is None:
            raise KeyError(f"Unknown adapter: {phase.adapter}")

        # Load inputs
        inputs: Dict[str, Any] = {}
        for ip in phase.inputs:
            inputs[ip] = self.store.read_text(wf.workflow_id, ip)

        # Compile prompt
        template = self.compiler.load(phase.adapter, phase.prompt_name)
        vars = {
            "goal": wf.goal,
            "constraints": wf.constraints,
            "phase": phase.name,
            "inputs": inputs,
            **wf.constraints,
        }
        compiled = self.compiler.compile(template, vars)

        provider = self.rotation.select_provider(tier=tier, hint=phase.provider_hint)

        # Execute
        result = adapter.execute(phase, compiled, provider, context=vars)

        # Validate (text artifact only for now)
        errors = adapter.validate(phase, result.artifact_text)
        ok = (len(errors) == 0) and result.ok

        # Write outputs: if multiple outputs, write identical artifact_text for now
        for op in phase.outputs:
            self.store.write_text(wf.workflow_id, op, result.artifact_text)

        # Write metadata
        self.store.write_json(
            wf.workflow_id,
            f"meta/{phase.name}.json",
            {
                "phase": asdict(phase),
                "provider_id": result.provider_id,
                "tier": result.tier,
                "cost_usd": result.cost_usd,
                "tokens": result.tokens,
                "ok": ok,
                "errors": errors,
            },
        )
        status = "OK" if ok else f"FAIL: {summarize_errors(errors)}"
        return ok, status

    def run_with_escalation(self, wf: WorkflowSpec, phase: PhaseSpec, start_tier: str) -> str:
        rule = EscalationRule(max_escalations=2, retry_same_tier=1)
        state = EscalationState()
        tier = start_tier

        while True:
            ok, status = self.run_phase(wf, phase, tier=tier)
            if ok:
                return f"{phase.name}: {status} (tier={tier})"

            if state.should_retry_same_tier(rule):
                state.on_retry()
                continue

            if state.should_escalate(rule):
                nt = self.rotation.next_tier(tier)
                if nt is None:
                    return f"{phase.name}: {status} (no higher tier)"
                tier = nt
                state.on_escalate()
                continue

            return f"{phase.name}: {status} (exhausted retries/escalations)"
