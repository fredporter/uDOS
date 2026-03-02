"""WORKFLOW command handler - deterministic markdown workflow scheduling."""

from __future__ import annotations

from pathlib import Path
from typing import Dict, List

from core.commands.base import BaseCommandHandler
from core.services.error_contract import CommandError
from core.services.logging_api import get_logger, get_repo_root
from core.workflows.scheduler import WorkflowScheduler

logger = get_logger("workflow-handler")


class WorkflowHandler(BaseCommandHandler):
    def __init__(self) -> None:
        super().__init__()
        self.repo_root = Path(get_repo_root())
        self.scheduler = WorkflowScheduler(self.repo_root)

    def handle(self, command: str, params: List[str], grid=None, parser=None) -> Dict:
        if not params:
            return self._help()

        action = params[0].upper()
        args = params[1:]

        if action in {"HELP", "--HELP", "-H", "?"}:
            return self._help()
        if action == "LIST":
            return self._list(args)
        if action == "NEW":
            return self._new(args)
        if action == "RUN":
            return self._run(args)
        if action == "STATUS":
            return self._status(args)
        if action == "APPROVE":
            return self._approve(args)
        if action == "ESCALATE":
            return self._escalate(args)

        raise CommandError(
            code="ERR_COMMAND_NOT_FOUND",
            message=f"Unknown WORKFLOW action: {action}",
            recovery_hint="Use WORKFLOW HELP",
            level="INFO",
        )

    def _help(self) -> Dict:
        return {
            "status": "success",
            "output": "\n".join(
                [
                    "WORKFLOW",
                    "WORKFLOW LIST [TEMPLATES|RUNS]           List available workflow templates or workflow runs",
                    "WORKFLOW NEW <template> <workflow_id>    Create a workflow from a markdown template",
                    "WORKFLOW RUN <workflow_id>               Run the current workflow phase",
                    "WORKFLOW STATUS <workflow_id>            Show workflow state and next window",
                    "WORKFLOW APPROVE <workflow_id>           Approve a completed review checkpoint",
                    "WORKFLOW ESCALATE <workflow_id>          Escalate current phase to the next provider tier",
                    "",
                    "Variable syntax for WORKFLOW NEW:",
                    "  WORKFLOW NEW WRITING-article article-001 goal=\"Write release note\" audience=operators tone=plain word_limit=600",
                ]
            ),
        }

    def _list(self, args: List[str]) -> Dict:
        mode = args[0].upper() if args else "TEMPLATES"
        if mode in {"TEMPLATES", "TEMPLATE"}:
            templates = self.scheduler.list_templates()
            return {
                "status": "success",
                "templates": templates,
                "output": "\n".join(["Workflow templates:"] + [f"- {item}" for item in templates]),
            }
        workflows = self.scheduler.list_workflows()
        return {
            "status": "success",
            "workflows": workflows,
            "output": "\n".join(["Workflow runs:"] + [f"- {item}" for item in workflows]),
        }

    def _new(self, args: List[str]) -> Dict:
        if len(args) < 2:
            raise CommandError(
                code="ERR_COMMAND_INVALID_ARG",
                message="WORKFLOW NEW requires template name and workflow id",
                recovery_hint="Use WORKFLOW NEW <template> <workflow_id> [key=value ...]",
                level="INFO",
            )
        template_name = args[0]
        workflow_id = args[1]
        variables = self._parse_variables(args[2:])
        spec = self.scheduler.create_workflow(template_name, workflow_id, variables)
        return {
            "status": "success",
            "workflow_id": workflow_id,
            "template": template_name,
            "workflow": spec.workflow_id,
            "output": f"Created workflow {workflow_id} from template {template_name}",
        }

    def _run(self, args: List[str]) -> Dict:
        workflow_id = self._require_workflow_id(args, "WORKFLOW RUN <workflow_id>")
        state = self.scheduler.run_workflow(workflow_id)
        return {
            "status": "success",
            "workflow_id": workflow_id,
            "state": state.status,
            "output": self._format_state(workflow_id, state),
        }

    def _status(self, args: List[str]) -> Dict:
        workflow_id = self._require_workflow_id(args, "WORKFLOW STATUS <workflow_id>")
        payload = self.scheduler.status(workflow_id)
        state = payload["state"]
        return {
            "status": "success",
            "workflow_id": workflow_id,
            "workflow": payload,
            "output": self._format_state_dict(workflow_id, state),
        }

    def _approve(self, args: List[str]) -> Dict:
        workflow_id = self._require_workflow_id(args, "WORKFLOW APPROVE <workflow_id>")
        state = self.scheduler.approve_phase(workflow_id)
        return {
            "status": "success",
            "workflow_id": workflow_id,
            "state": state.status,
            "output": self._format_state(workflow_id, state),
        }

    def _escalate(self, args: List[str]) -> Dict:
        workflow_id = self._require_workflow_id(args, "WORKFLOW ESCALATE <workflow_id>")
        state = self.scheduler.escalate_phase(workflow_id)
        return {
            "status": "success",
            "workflow_id": workflow_id,
            "state": state.status,
            "output": self._format_state(workflow_id, state),
        }

    def _require_workflow_id(self, args: List[str], usage: str) -> str:
        if not args:
            raise CommandError(
                code="ERR_COMMAND_INVALID_ARG",
                message="Missing workflow id",
                recovery_hint=usage,
                level="INFO",
            )
        return args[0]

    def _parse_variables(self, args: List[str]) -> dict[str, str]:
        variables: dict[str, str] = {}
        buffer = ""
        quote_count = 0
        items: list[str] = []
        for raw in args:
            if buffer:
                buffer = f"{buffer} {raw}"
            else:
                buffer = raw
            quote_count += raw.count('"') + raw.count("'")
            if quote_count % 2 == 0:
                items.append(buffer)
                buffer = ""
                quote_count = 0
        if buffer:
            items.append(buffer)
        for raw in items:
            if "=" not in raw:
                continue
            key, value = raw.split("=", 1)
            variables[key.strip()] = value.strip().strip("\"'")
        return variables

    def _format_state(self, workflow_id: str, state) -> str:
        current = state.phases[state.current_phase_index] if state.phases else None
        lines = [
            f"Workflow: {workflow_id}",
            f"Status: {state.status}",
            f"Current phase: {current.name if current else 'n/a'}",
            f"Next window: {state.next_run_at or 'n/a'}",
            f"Budget spent: ${state.total_cost_usd:.2f}",
            f"Tokens used: {state.total_tokens}",
        ]
        if current:
            lines.append(f"Current tier: {current.tier}")
            lines.append(f"Current phase status: {current.status}")
            if current.last_error:
                lines.append(f"Last error: {current.last_error}")
        return "\n".join(lines)

    def _format_state_dict(self, workflow_id: str, state: dict) -> str:
        current_index = state.get("current_phase_index", 0)
        phases = state.get("phases", [])
        current = phases[current_index] if phases and current_index < len(phases) else {}
        lines = [
            f"Workflow: {workflow_id}",
            f"Status: {state.get('status', 'unknown')}",
            f"Current phase: {current.get('name', 'n/a')}",
            f"Next window: {state.get('next_run_at') or 'n/a'}",
            f"Budget spent: ${float(state.get('total_cost_usd', 0.0)):.2f}",
            f"Tokens used: {state.get('total_tokens', 0)}",
        ]
        if current:
            lines.append(f"Current tier: {current.get('tier', 'n/a')}")
            lines.append(f"Current phase status: {current.get('status', 'n/a')}")
            if current.get("last_error"):
                lines.append(f"Last error: {current['last_error']}")
        return "\n".join(lines)
