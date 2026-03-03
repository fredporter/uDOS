from __future__ import annotations

from datetime import datetime, timedelta, timezone
from pathlib import Path
from dataclasses import asdict, replace

from .artifacts import WorkflowArtifactStore
from .contracts import PhaseRuntimeState, WorkflowRuntimeState, WorkflowSpec
from .parser import WorkflowTemplateParser
from .phase_engine import PhaseEngine


def _now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


class WorkflowScheduler:
    def __init__(self, repo_root: Path):
        self.repo_root = repo_root
        self.workflow_root = repo_root / "memory" / "vault"
        self.template_root = repo_root / "core" / "framework" / "seed" / "bank" / "templates" / "workflows"
        self.prompt_root = repo_root / "docs" / "examples" / "udos_creative_pack" / "core" / "creative"
        self.parser = WorkflowTemplateParser()
        self.store = WorkflowArtifactStore(self.workflow_root)
        self.engine = PhaseEngine(vault_root=self.workflow_root, prompt_root=self.prompt_root)

    def list_templates(self) -> list[str]:
        if not self.template_root.exists():
            return []
        return sorted(path.stem for path in self.template_root.glob("*.md"))

    def list_workflows(self) -> list[str]:
        return self.store.list_workflows()

    def create_workflow(
        self,
        template_name: str,
        workflow_id: str,
        variables: dict[str, str],
        *,
        project: str | None = None,
    ) -> WorkflowSpec:
        template_path = self.template_root / f"{template_name}.md"
        template = template_path.read_text(encoding="utf-8")
        rendered = template
        for key, value in variables.items():
            rendered = rendered.replace(f"{{{{{key}}}}}", value)
        spec = self.parser.parse(workflow_id=workflow_id, markdown=rendered, source_path=template_path)
        if project:
            spec = replace(spec, project=project)
        self.store.ensure_workflow_dir(workflow_id)
        self.store.write_spec(spec, rendered)
        self.store.write_state(self._initial_state(spec))
        return spec

    def create_workflow_from_markdown(
        self,
        workflow_id: str,
        markdown: str,
        *,
        source_path: Path | None = None,
        project: str | None = None,
    ) -> WorkflowSpec:
        spec = self.parser.parse(workflow_id=workflow_id, markdown=markdown, source_path=source_path)
        if project:
            spec = replace(spec, project=project)
        self.store.ensure_workflow_dir(workflow_id)
        self.store.write_spec(spec, markdown)
        self.store.write_state(self._initial_state(spec))
        return spec

    def load_spec(self, workflow_id: str) -> WorkflowSpec:
        payload = self.store.read_json(workflow_id, "workflow.json")
        phases = []
        for item in payload["phases"]:
            from .contracts import BudgetCaps, PhaseSpec, ProviderHint

            phases.append(
                PhaseSpec(
                    name=item["name"],
                    adapter=item["adapter"],
                    prompt_name=item["prompt_name"],
                    outputs=list(item.get("outputs", [])),
                    inputs=list(item.get("inputs", [])),
                    requires_user_approval=item.get("requires_user_approval", True),
                    provider_hint=ProviderHint(**item.get("provider_hint", {})),
                    budget=BudgetCaps(**item.get("budget", {})),
                )
            )
        from .contracts import WorkflowSpec

        return WorkflowSpec(
            workflow_id=payload["workflow_id"],
            template_id=payload.get("template_id", ""),
            project=payload.get("project", payload["workflow_id"]),
            goal=payload.get("goal", ""),
            purpose=payload.get("purpose", ""),
            inputs=dict(payload.get("inputs", {})),
            constraints=dict(payload.get("constraints", {})),
            phases=phases,
            outputs=list(payload.get("outputs", [])),
            created_at_iso=payload.get("created_at_iso", ""),
            source_path=payload.get("source_path"),
        )

    def load_state(self, workflow_id: str) -> WorkflowRuntimeState:
        payload = self.store.read_json(workflow_id, "state.json")
        phases = [PhaseRuntimeState(**item) for item in payload.get("phases", [])]
        return WorkflowRuntimeState(
            workflow_id=payload["workflow_id"],
            status=payload.get("status", "ready"),
            current_phase_index=payload.get("current_phase_index", 0),
            total_cost_usd=payload.get("total_cost_usd", 0.0),
            total_tokens=payload.get("total_tokens", 0),
            created_at=payload.get("created_at", ""),
            updated_at=payload.get("updated_at", ""),
            next_run_at=payload.get("next_run_at", ""),
            phases=phases,
        )

    def run_workflow(self, workflow_id: str) -> WorkflowRuntimeState:
        spec = self.load_spec(workflow_id)
        state = self.load_state(workflow_id)
        if state.status == "completed":
            return state
        current = state.phases[state.current_phase_index]
        if current.status == "pending_approval":
            return state

        phase = spec.phases[state.current_phase_index]
        result = self.engine.run_phase(spec, phase, tier=current.tier)
        current.provider_id = result.provider_id
        current.last_run_at = _now_iso()
        current.cost_usd += result.cost_usd
        current.tokens += result.tokens
        state.total_cost_usd += result.cost_usd
        state.total_tokens += result.tokens
        state.updated_at = _now_iso()
        meta = {
            "phase": phase.name,
            "provider_id": result.provider_id,
            "tier": result.tier,
            "ok": result.ok,
            "errors": result.errors,
            "cost_usd": result.cost_usd,
            "tokens": result.tokens,
        }
        self.store.write_json(workflow_id, f"meta/{phase.name}.json", meta)

        if not result.ok:
            current.status = "failed"
            current.last_error = "; ".join(result.errors)
            current.next_run_at = self._next_window(hours=12)
            state.next_run_at = current.next_run_at
            state.status = "waiting"
            self.store.write_state(state)
            return state

        for output in phase.outputs:
            self.store.write_text(workflow_id, output, result.artifact_text)

        if phase.requires_user_approval:
            current.status = "pending_approval"
            current.next_run_at = ""
            state.status = "awaiting_approval"
            state.next_run_at = ""
        else:
            current.status = "completed"
            self._advance_state(spec, state)
        self.store.write_state(state)
        return state

    def approve_phase(self, workflow_id: str) -> WorkflowRuntimeState:
        spec = self.load_spec(workflow_id)
        state = self.load_state(workflow_id)
        current = state.phases[state.current_phase_index]
        if current.status != "pending_approval":
            return state
        current.status = "completed"
        current.approved_at = _now_iso()
        self._advance_state(spec, state)
        self.store.write_state(state)
        return state

    def escalate_phase(self, workflow_id: str) -> WorkflowRuntimeState:
        state = self.load_state(workflow_id)
        current = state.phases[state.current_phase_index]
        tier_order = ("tier1_local", "tier2_cloud", "tier3_high")
        try:
            idx = tier_order.index(current.tier)
        except ValueError:
            idx = 0
        if idx + 1 < len(tier_order):
            current.tier = tier_order[idx + 1]
            current.escalations_used += 1
            current.status = "ready"
            current.next_run_at = self._next_window(hours=1)
            state.status = "ready"
            state.next_run_at = current.next_run_at
            state.updated_at = _now_iso()
            self.store.write_state(state)
        return state

    def status(self, workflow_id: str) -> dict[str, object]:
        spec = self.load_spec(workflow_id)
        state = self.load_state(workflow_id)
        return {"spec": asdict(spec), "state": asdict(state)}

    def _initial_state(self, spec: WorkflowSpec) -> WorkflowRuntimeState:
        now = _now_iso()
        phases = [
            PhaseRuntimeState(
                name=phase.name,
                status="ready" if index == 0 else "pending",
                next_run_at=self._next_window(hours=0) if index == 0 else "",
            )
            for index, phase in enumerate(spec.phases)
        ]
        return WorkflowRuntimeState(
            workflow_id=spec.workflow_id,
            status="ready",
            current_phase_index=0,
            total_cost_usd=0.0,
            total_tokens=0,
            created_at=now,
            updated_at=now,
            next_run_at=phases[0].next_run_at if phases else "",
            phases=phases,
        )

    def _advance_state(self, spec: WorkflowSpec, state: WorkflowRuntimeState) -> None:
        state.phases[state.current_phase_index].next_run_at = ""
        if state.current_phase_index + 1 >= len(spec.phases):
            state.status = "completed"
            state.next_run_at = ""
            state.updated_at = _now_iso()
            return
        state.current_phase_index += 1
        next_phase = state.phases[state.current_phase_index]
        next_phase.status = "ready"
        next_phase.next_run_at = self._next_window(hours=12)
        state.status = "ready"
        state.next_run_at = next_phase.next_run_at
        state.updated_at = _now_iso()

    def _next_window(self, hours: int) -> str:
        return (datetime.now(timezone.utc) + timedelta(hours=hours)).isoformat()
