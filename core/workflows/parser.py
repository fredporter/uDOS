from __future__ import annotations

from datetime import datetime, timezone
from pathlib import Path
import re

from .contracts import BudgetCaps, PhaseSpec, ProviderHint, WorkflowSpec

_PHASE_RE = re.compile(r"^\d+\.\s+(?P<label>.+?)\s+\((?P<adapter>[^/]+)/(?P<prompt>[^ ]+)\s+->\s+(?P<output>[^)]+)\)$")
_CONSTRAINT_RE = re.compile(r"^- (?P<key>[^:]+): (?P<value>.+)$")


class WorkflowTemplateParser:
    def parse(self, workflow_id: str, markdown: str, source_path: Path | None = None) -> WorkflowSpec:
        title = self._section_text(markdown, "WORKFLOW:", title_mode=True)
        purpose = self._section_text(markdown, "Purpose")
        inputs = self._field_map(markdown, "Inputs")
        project = self._section_text(markdown, "Project")
        goal = self._section_text(markdown, "Goal")
        constraints = self._constraint_map(markdown)
        phases = self._phases(markdown)
        outputs = self._outputs(markdown)
        return WorkflowSpec(
            workflow_id=workflow_id,
            template_id=title,
            project=(project.strip() or inputs.get("project") or constraints.get("project") or workflow_id),
            goal=(goal.strip() or purpose.strip()),
            purpose=purpose.strip(),
            inputs=inputs,
            constraints=constraints,
            phases=phases,
            outputs=outputs,
            created_at_iso=datetime.now(timezone.utc).isoformat(),
            source_path=str(source_path) if source_path else None,
        )

    def _section_text(self, markdown: str, heading: str, title_mode: bool = False) -> str:
        lines = markdown.splitlines()
        if title_mode:
            for line in lines:
                if line.startswith("# "):
                    return line.split(":", 1)[-1].strip()
            return ""
        capture = False
        collected: list[str] = []
        for line in lines:
            if line.strip().lower() == f"## {heading}".lower():
                capture = True
                continue
            if capture and line.startswith("## "):
                break
            if capture:
                collected.append(line)
        return "\n".join(collected).strip()

    def _constraint_map(self, markdown: str) -> dict[str, str]:
        return self._field_map(markdown, "Constraints")

    def _field_map(self, markdown: str, heading: str) -> dict[str, str]:
        section = self._section_text(markdown, heading)
        constraints: dict[str, str] = {}
        for line in section.splitlines():
            match = _CONSTRAINT_RE.match(line.strip())
            if not match:
                continue
            key = match.group("key").strip().lower().replace(" ", "_")
            constraints[key] = match.group("value").strip()
        return constraints

    def _phases(self, markdown: str) -> list[PhaseSpec]:
        section = self._section_text(markdown, "Phases")
        phases: list[PhaseSpec] = []
        for index, line in enumerate(section.splitlines()):
            match = _PHASE_RE.match(line.strip())
            if not match:
                continue
            label = match.group("label").strip()
            phase_name = re.sub(r"[^a-z0-9]+", "_", label.lower()).strip("_") or f"phase_{index + 1}"
            phases.append(
                PhaseSpec(
                    name=phase_name,
                    adapter=match.group("adapter").strip(),
                    prompt_name=match.group("prompt").strip(),
                    outputs=[match.group("output").strip()],
                    requires_user_approval=True,
                    provider_hint=ProviderHint(),
                    budget=BudgetCaps(),
                )
            )
        return phases

    def _outputs(self, markdown: str) -> list[str]:
        section = self._section_text(markdown, "Outputs")
        outputs: list[str] = []
        for line in section.splitlines():
            line = line.strip()
            if line.startswith("- "):
                outputs.append(line[2:].strip())
        return outputs
